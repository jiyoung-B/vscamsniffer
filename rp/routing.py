from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from rp.consumers import RPConsumer  # WebSocket Consumer 추가
from solution.consumers import SolutionConsumer

websocket_urlpatterns = [
    re_path(r"ws/rp/$", RPConsumer.as_asgi()),
    re_path(r"ws/solution/$", SolutionConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "websocket": URLRouter(websocket_urlpatterns),
})