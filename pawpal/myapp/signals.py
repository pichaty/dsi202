# work/dsi202/pawpal/myapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from .models import AdoptionApplication, Notification, User # หรือ from django.contrib.auth.models import User

@receiver(post_save, sender=AdoptionApplication)
def create_adoption_status_notification(sender, instance, created, **kwargs):
    """
    สร้าง Notification เมื่อสถานะ AdoptionApplication เปลี่ยนแปลง หรือมีการสร้างใหม่
    หรือเมื่อมีการกำหนด/เปลี่ยนแปลง interview_datetime
    """
    user_to_notify = None
    try:
        # หากใบคำขอผูกกับ User โดยตรง (ถ้ามีการปรับ Model)
        # user_to_notify = instance.user
        # หรือ หากใช้ email ในการหา User
        if instance.email:
            user_to_notify = User.objects.filter(email=instance.email).first()
    except User.DoesNotExist:
        user_to_notify = None

    if user_to_notify:
        message = ""
        link = reverse('my_adoption_applications') # ลิงก์ไปยังหน้ารายการสถานะการรับเลี้ยง

        if created:
            message = f"คำขอรับเลี้ยงหมายเลข APP-{instance.id:05d} ของคุณสำหรับ {', '.join([pet.name for pet in instance.pets.all()])} ได้รับการส่งเรียบร้อยแล้ว และกำลังรอการตรวจสอบ"
            notification_type = "adoption_submitted"
        else:
            # ตรวจสอบการเปลี่ยนแปลงสถานะ
            try:
                old_instance = AdoptionApplication.objects.get(pk=instance.pk)
                if old_instance.status != instance.status:
                    message = f"สถานะคำขอรับเลี้ยงหมายเลข APP-{instance.id:05d} สำหรับ {', '.join([pet.name for pet in instance.pets.all()])} ได้เปลี่ยนเป็น '{instance.get_status_display()}'"
                    notification_type = f"adoption_status_{instance.status}"
                elif old_instance.interview_datetime != instance.interview_datetime and instance.interview_datetime:
                    message = f"มีการนัดหมายสัมภาษณ์สำหรับคำขอ APP-{instance.id:05d} ในวันที่ {instance.interview_datetime.strftime('%d %b %Y, %H:%M')}"
                    notification_type = "appointment_scheduled"
                elif not old_instance.interview_datetime and instance.interview_datetime: # กรณีเพิ่มวันนัดหมายใหม่
                    message = f"มีการนัดหมายสัมภาษณ์สำหรับคำขอ APP-{instance.id:05d} ในวันที่ {instance.interview_datetime.strftime('%d %b %Y, %H:%M')}"
                    notification_type = "appointment_scheduled"

            except AdoptionApplication.DoesNotExist: # เกิดขึ้นได้ยากถ้า instance ถูก save แล้ว
                pass


        if message: # สร้าง Notification ถ้ามีข้อความ
            Notification.objects.create(
                recipient=user_to_notify,
                message=message,
                link=link,
                notification_type=notification_type
            )

# (เพิ่ม) Signal สำหรับการยืนยัน/เปลี่ยนแปลงนัดหมายจาก Admin โดยตรง (ถ้ามี Action แยกต่างหากใน Admin)
# ตัวอย่าง: ถ้า Admin มี Action 'confirm_interview' ใน AdoptionApplicationAdmin
# def create_admin_appointment_confirmation_notification(user, application_instance):
#     message = f"แอดมินยืนยันนัดหมายสัมภาษณ์สำหรับคำขอ APP-{application_instance.id:05d} ในวันที่ {application_instance.interview_datetime.strftime('%d %b %Y, %H:%M')}"
#     link = reverse('my_adoption_applications')
#     Notification.objects.create(
#         recipient=user,
#         message=message,
#         link=link,
#         notification_type="appointment_confirmed_admin"
#     )