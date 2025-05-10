# work/dsi202/pawpal/pawpal/settings.py


from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-1*k4!o(+480)7hj(nqpfh$v1h6rw7#%d^y!otxdl+vo@bc6z4e' # ควรเปลี่ยนใน Production

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',
    # 'channels', # ถ้าคุณใช้ Django Channels สำหรับ chat (จากไฟล์ asgi.py และ settings.py ที่มี CHANNEL_LAYERS)
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pawpal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # ถ้าคุณมี_DIR `templates` ที่ root ของโปรเจกต์
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'myapp.context_processors.favorite_count', # context processor ของคุณ
            ],
        },
    },
]

WSGI_APPLICATION = 'pawpal.wsgi.application'
ASGI_APPLICATION = 'pawpal.asgi.application' # ถ้าใช้ Channels

# CHANNEL_LAYERS = { ... } # ถ้าใช้ Channels

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    # ... (validators เดิม) ...
]

LANGUAGE_CODE = 'en-us' # หรือ 'th' ถ้าต้องการภาษาไทยเป็นหลัก
TIME_ZONE = 'Asia/Bangkok' # ตั้งค่า Time Zone
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static", # ถ้าคุณมี_DIR `static` ที่ root ของโปรเจกต์
]
# STATIC_ROOT = BASE_DIR / "staticfiles" # สำหรับ production ตอน collectstatic

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- เพิ่ม/ตรวจสอบ ส่วนนี้ ---
LOGIN_URL = 'login'
# หรือถ้าคุณต้องการให้ชัดเจนยิ่งขึ้นเมื่อใช้ namespace 'accounts' จาก django.contrib.auth.urls:
# LOGIN_URL = 'accounts:login' 
# โดยปกติ Django จะหา 'login' จาก global namespace ได้ แต่ถ้ามีปัญหา ลองใช้ 'accounts:login'

LOGIN_REDIRECT_URL = 'home'  # ชื่อ URL pattern ของหน้าที่จะไปหลัง login สำเร็จ
LOGOUT_REDIRECT_URL = 'home' # ชื่อ URL pattern ของหน้าที่จะไปหลัง logout
#test