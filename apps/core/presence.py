import json
from datetime import datetime, timezone

import redis
from django.conf import settings

# Shared "who is online" presence, so it works across multiple worker
# processes (unlike a plain in-memory dict). A visitor counts as online
# only while its heartbeat is fresher than PRESENCE_TTL - if a worker
# crashes without running disconnect(), the entry expires on its own
# instead of leaving a phantom "online" visitor forever.
PRESENCE_KEY = 'max_log:online_visitors'
PRESENCE_TTL = 90
HEARTBEAT_INTERVAL = 30

_client = None


def get_redis_client():
    global _client
    if _client is None:
        host = settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0]
        _client = redis.Redis(host=host['host'], port=host['port'], decode_responses=True)
    return _client


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _seconds_since(iso_value):
    return (datetime.now(timezone.utc) - datetime.fromisoformat(iso_value)).total_seconds()


def mark_online(visitor_id):
    """Record a fresh connection. Keeps connected_at stable across reconnects/heartbeats."""
    client = get_redis_client()
    now = _now_iso()
    connected_at = now
    raw = client.hget(PRESENCE_KEY, visitor_id)
    if raw:
        try:
            connected_at = json.loads(raw).get('connected_at', now)
        except ValueError:
            pass
    client.hset(PRESENCE_KEY, visitor_id, json.dumps({'connected_at': connected_at, 'heartbeat': now}))
    return connected_at


def heartbeat(visitor_id):
    """Refresh the TTL clock for a visitor that's still connected."""
    client = get_redis_client()
    raw = client.hget(PRESENCE_KEY, visitor_id)
    if not raw:
        return
    try:
        data = json.loads(raw)
    except ValueError:
        return
    data['heartbeat'] = _now_iso()
    client.hset(PRESENCE_KEY, visitor_id, json.dumps(data))


def mark_offline(visitor_id):
    get_redis_client().hdel(PRESENCE_KEY, visitor_id)


def get_presence(visitor_id):
    """{'connected_at': ...} if the visitor is currently online, else None. Evicts a stale entry."""
    raw = get_redis_client().hget(PRESENCE_KEY, visitor_id)
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except ValueError:
        mark_offline(visitor_id)
        return None
    if _seconds_since(data.get('heartbeat', data['connected_at'])) > PRESENCE_TTL:
        mark_offline(visitor_id)
        return None
    return data


def online_visitor_ids():
    """All currently-online visitor ids. Evicts any stale (crashed-worker) entries along the way."""
    client = get_redis_client()
    raw = client.hgetall(PRESENCE_KEY)
    online, stale = [], []
    for visitor_id, value in raw.items():
        try:
            data = json.loads(value)
        except ValueError:
            stale.append(visitor_id)
            continue
        if _seconds_since(data.get('heartbeat', data['connected_at'])) > PRESENCE_TTL:
            stale.append(visitor_id)
        else:
            online.append(visitor_id)
    if stale:
        client.hdel(PRESENCE_KEY, *stale)
    return online
