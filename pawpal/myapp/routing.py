# work/dsi202/pawpal/myapp/routing.py

from django.urls import re_path
from . import consumers # <--- เราจะสร้าง consumers.py ในขั้นตอนถัดไป

websocket_urlpatterns = [
    # เส้นทางสำหรับ WebSocket chat (ตรงกับที่ระบุใน chat.html)
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
    # คุณสามารถเพิ่มเส้นทางอื่นๆ สำหรับ WebSocket ได้ที่นี่
    # เช่น re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()), # สำหรับห้องแชทแบบมีชื่อห้อง
]