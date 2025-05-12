# # work/dsi202/pawpal/myapp/context_processors.py
from .models import UserFavorite, Notification # ตรวจสอบว่า import Notification ถูกต้อง
from django.contrib.auth.models import User # หาก Notification model ใช้ User โดยตรง

def common_context(request):
    context = {}
    if request.user.is_authenticated:
        try:
            fav_count = UserFavorite.objects.filter(user=request.user).count()
            # ตรวจสอบว่า Notification model import ถูกต้อง และ recipient field อ้างถึง User model อย่างไร
            # หาก Notification.recipient อ้างถึง User โดยตรง:
            unread_notif_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        except Exception as e: # เพิ่มการจัดการ exception เพื่อ debug
            print(f"Error in common_context: {e}")
            fav_count = 0
            unread_notif_count = 0

        context['favorite_count'] = fav_count
        context['has_favorites'] = fav_count > 0
        context['unread_notifications_count'] = unread_notif_count
    else:
        context['favorite_count'] = 0
        context['has_favorites'] = False
        context['unread_notifications_count'] = 0
    return context