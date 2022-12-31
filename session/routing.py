from django.urls import re_path

from session.consumers import SessionConsumer

websocket_urlpatterns = [
    re_path(r"ws/session/(?P<session_id>\w+)/$", SessionConsumer.as_asgi()),
]