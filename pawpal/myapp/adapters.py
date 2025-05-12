# work/dsi202/pawpal/myapp/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url
from django.conf import settings


User = get_user_model()

class MyCustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        # ... (โค้ดเดิมของคุณใน pre_social_login) ...
        if sociallogin.is_existing:
            return

        try:
            email_address = sociallogin.account.extra_data.get('email')
            if email_address:
                users = User.objects.filter(email=email_address)
                if users.exists():
                     pass # ปล่อยให้ allauth จัดการตาม settings

        except User.DoesNotExist:
            pass

    def populate_user(self, request, sociallogin, data):
        """
        Override เพื่อ populate first_name และ last_name ด้วย
        """
        user = super().populate_user(request, sociallogin, data)

        # ดึง first_name และ last_name จาก extra_data ของ social account
        # key อาจต่างกันไปในแต่ละ provider (สำหรับ Google คือ 'given_name', 'family_name')
        first_name = sociallogin.account.extra_data.get('given_name', '')
        last_name = sociallogin.account.extra_data.get('family_name', '')
        full_name = sociallogin.account.extra_data.get('name', '') # Fallback

        # เติมค่าถ้าฟิลด์ใน user model ยังว่างอยู่
        if not user.first_name and first_name:
            user.first_name = first_name
        elif not user.first_name and full_name and not last_name:
             # ลองแยกจาก full name ถ้าไม่มี first/last แยกมา
             parts = full_name.split(' ', 1)
             user.first_name = parts[0]
             if len(parts) > 1:
                 user.last_name = parts[1] # เติมนามสกุลถ้าแยกได้

        if not user.last_name and last_name:
            user.last_name = last_name

        # email และ username มักจะถูกจัดการโดย default หรือ signup form อยู่แล้ว

        return user

    def save_user(self, request, sociallogin, form=None):
        """
        ตรวจสอบให้แน่ใจว่า first_name และ last_name จาก social provider ถูกบันทึก
        """
        user = super().save_user(request, sociallogin, form=form)
        # อาจจะต้อง populate อีกครั้งเผื่อ user object ถูกสร้างใหม่
        first_name = sociallogin.account.extra_data.get('given_name', '')
        last_name = sociallogin.account.extra_data.get('family_name', '')
        full_name = sociallogin.account.extra_data.get('name', '')

        needs_save = False
        if not user.first_name and first_name:
            user.first_name = first_name
            needs_save = True
        elif not user.first_name and full_name and not last_name:
             parts = full_name.split(' ', 1)
             user.first_name = parts[0]
             if len(parts) > 1 and not user.last_name:
                 user.last_name = parts[1]
             needs_save = True

        if not user.last_name and last_name:
            user.last_name = last_name
            needs_save = True

        if needs_save:
             user.save(update_fields=['first_name', 'last_name']) # ระบุ field ที่ต้องการ update

        return user


class MyCustomAccountAdapter(DefaultAccountAdapter):
    # ... (โค้ดเดิมของคุณใน MyCustomAccountAdapter) ...
     def get_login_redirect_url(self, request):
         return resolve_url(settings.LOGIN_REDIRECT_URL)

     def get_signup_redirect_url(self, request):
         return resolve_url(settings.LOGIN_REDIRECT_URL)