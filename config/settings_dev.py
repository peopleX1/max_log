import os

# Password validation
AUTH_PASSWORD_VALIDATORS = []

# Sessions and security
# SESSION_COOKIE_AGE = 1209600
# SESSION_SAVE_EVERY_REQUEST = False
# SESSION_EXPIRE_AT_BROWSER_CLOSE = False
X_FRAME_OPTIONS = 'SAMEORIGIN'

#CHANNELS
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [{
                "host": os.environ.get('CHANNELS_REDIS_HOST', '127.0.0.1'),
                "port": int(os.environ.get('CHANNELS_REDIS_PORT', 6379)),
                "socket_timeout": None,
            }],
        },
    },
}


