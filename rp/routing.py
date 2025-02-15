from django.urls import re_path
from rp.consumers import RPConsumer  # WebSocket Consumer 추가

websocket_urlpatterns = [
    # re_path(r"ws/rp/$", RPConsumer.as_asgi()),
    re_path(r"ws/rp/$", RPConsumer.as_asgi()),
]