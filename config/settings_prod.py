# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
                    'min_length': 6,
                }
    },
]

# Sessions and security
CSRF_TRUSTED_ORIGINS = ['http://45.15.157.172', 'https://24cbr.com']

#SESSION_COOKIE_SECURE = False
#CSRF_COOKIE_SECURE = False
#X_FRAME_OPTIONS = 'SAMEORIGIN'
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = CSRF_TRUSTED_ORIGINS

# SESSION_COOKIE_AGE = 1800
# SESSION_SAVE_EVERY_REQUEST = True
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_BROWSER_XSS_FILTER = True

SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000

X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_REFERRER_POLICY = 'same-origin'
DJANGO_REDIS_IGNORE_EXCEPTIONS = True
SECURE_CONTENT_TYPE_NOSNIFF = True

USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = True

#CHANNELS
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}
