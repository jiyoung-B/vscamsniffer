
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import rp.routing
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'corkagefree.settings')

#asgi 어플리케이션 초기화
application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # HTTP 요청 처리
    "websocket": AuthMiddlewareStack(  # WebSocket 요청 처리
        URLRouter(
            rp.routing.websocket_urlpatterns
        )
    ),
})
