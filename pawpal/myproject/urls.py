# work/dsi202/pawpal/pawpal/urls.py

"""
URL configuration for pawpal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include # ตรวจสอบว่า include ถูก import
from django.conf import settings
from django.conf.urls.static import static
# ไม่จำเป็นต้อง import auth_views ถ้าใช้ include('django.contrib.auth.urls')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')), # URL ของแอป myapp

    # เพิ่ม/ตรวจสอบ บรรทัดนี้:
    # การ include นี้จะสร้าง URL patterns ต่างๆ ที่จำเป็นสำหรับระบบ authentication
    # รวมถึง URL ที่ชื่อ 'login' ซึ่งจะ map ไปที่ /accounts/login/
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # เพิ่มบรรทัดนี้ถ้ายังไม่มี และจำเป็นสำหรับการ serve static files ใน development