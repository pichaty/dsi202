# work/dsi202/pawpal/pawpal/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import myapp.routing # <--- เราจะสร้างไฟล์นี้ในขั้นตอนถัดไป

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pawpal.settings')

# เรียก get_asgi_application() ก่อนเพื่อโหลด settings และ apps
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app, # การเชื่อมต่อ HTTP ปกติจะยังใช้ Django จัดการ
    "websocket": AuthMiddlewareStack( # AuthMiddlewareStack สำหรับการยืนยันตัวตนใน WebSocket
        URLRouter(
            myapp.routing.websocket_urlpatterns # <--- เส้นทางสำหรับ WebSocket
        )
    ),
})