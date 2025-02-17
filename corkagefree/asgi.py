
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from rp.routing import  websocket_urlpatterns
from channels.auth import AuthMiddlewareStack
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'corkagefree.settings')

#asgi 어플리케이션 초기화
application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # HTTP 요청 처리
    "websocket": AuthMiddlewareStack(  # WebSocket 요청 처리
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
