# work/dsi202/pawpal/myapp/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from .models import User # หรือ from django.contrib.auth import get_user_model
from .models import AdoptionApplication, Notification

# (pre_save handler - store_original_adoption_application_values - ควรยังคงอยู่เหมือนเดิม)
@receiver(pre_save, sender=AdoptionApplication)
def store_original_adoption_application_values(sender, instance, **kwargs):
    if instance.pk:
        try:
            original_instance = sender.objects.get(pk=instance.pk)
            instance._original_status = original_instance.status
            instance._original_interview_datetime = original_instance.interview_datetime
        except sender.DoesNotExist:
            instance._original_status = None
            instance._original_interview_datetime = None
    else:
        instance._original_status = None
        instance._original_interview_datetime = None

@receiver(post_save, sender=AdoptionApplication)
def create_adoption_status_notification(sender, instance, created, **kwargs):
    user_to_notify = None
    if instance.email:
        user_to_notify = User.objects.filter(email=instance.email).first()

    if not user_to_notify: # ถ้าไม่พบผู้รับการแจ้งเตือน ก็ไม่ต้องทำอะไรต่อ
        return

    link = reverse('my_adoption_applications') # ลิงก์ทั่วไปสำหรับการแจ้งเตือนเหล่านี้

    if created:
        pet_names = ", ".join([pet.name for pet in instance.pets.all()])
        message = f"คำขอรับเลี้ยงหมายเลข APP-{instance.id:05d} ของคุณสำหรับ {pet_names} ได้รับการส่งเรียบร้อยแล้ว และกำลังรอการตรวจสอบ"
        notification_type = "adoption_submitted"
        Notification.objects.create(
            recipient=user_to_notify,
            message=message,
            link=link,
            notification_type=notification_type
        )
    else: # กรณีเป็นการอัปเดตข้อมูล (created is False)
        old_status = getattr(instance, '_original_status', None)
        old_interview_datetime = getattr(instance, '_original_interview_datetime', None)

        status_changed = (old_status != instance.status)
        interview_datetime_changed = (old_interview_datetime != instance.interview_datetime)

        # ตรวจสอบการเปลี่ยนแปลงสถานะ และสร้าง Notification หากมีการเปลี่ยนแปลง
        if status_changed:
            pet_names = ", ".join([pet.name for pet in instance.pets.all()])
            message_status = f"สถานะคำขอรับเลี้ยงหมายเลข APP-{instance.id:05d} สำหรับ {pet_names} ได้เปลี่ยนเป็น '{instance.get_status_display()}'"
            type_status = f"adoption_status_{instance.status}"
            Notification.objects.create(
                recipient=user_to_notify,
                message=message_status,
                link=link,
                notification_type=type_status
            )

        # ตรวจสอบการเปลี่ยนแปลงวันสัมภาษณ์ และสร้าง Notification หากมีการเปลี่ยนแปลง (แยก if)
        if interview_datetime_changed:
            message_interview = ""
            type_interview = ""
            if instance.interview_datetime: # มีการตั้งค่าหรือเปลี่ยนแปลงวันนัดหมายใหม่
                message_interview = f"มีการนัดหมายสัมภาษณ์สำหรับคำขอ APP-{instance.id:05d} ในวันที่ {instance.interview_datetime.strftime('%d %b %Y, %H:%M')}"
                type_interview = "appointment_scheduled"
            elif old_interview_datetime and not instance.interview_datetime: # วันนัดหมายถูกยกเลิก (จากเดิมมีค่า กลายเป็นไม่มีค่า)
                message_interview = f"นัดหมายสัมภาษณ์สำหรับคำขอ APP-{instance.id:05d} (เดิมวันที่ {old_interview_datetime.strftime('%d %b %Y, %H:%M')}) ได้ถูกยกเลิก"
                type_interview = "appointment_cancelled"
            
            if message_interview and type_interview: # ตรวจสอบว่ามีข้อความและประเภทจริง ๆ ก่อนสร้าง
                Notification.objects.create(
                    recipient=user_to_notify,
                    message=message_interview,
                    link=link,
                    notification_type=type_interview
                )