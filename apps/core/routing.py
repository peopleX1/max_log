from django.urls import re_path

from apps.core.consumers import ManagerConsumer, VisitorTrackerConsumer

websocket_urlpatterns = [
    re_path(r'^ws/track/$', VisitorTrackerConsumer.as_asgi()),
    re_path(r'^ws/manager/$', ManagerConsumer.as_asgi()),
]
