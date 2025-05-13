# work/dsi202/pawpal/myapp/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.db.models import F
from django.utils import timezone

class Pet(models.Model):
    is_adopted = models.BooleanField(default=False)
    PET_TYPE_CHOICES = [
        ('dog', 'Dog'),
        ('cat', 'Cat'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
    
        ('female', 'Female'),
    ]
    SIZE_CHOICES = [
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('unknown', 'Unknown'), # เพิ่ม unknown หรือค่า default อื่นๆ ตามต้องการ
    ]
    size = models.CharField(max_length=10,choices=SIZE_CHOICES,default='unknown', blank=True ,null=True )         # อนุญาตให้เป็นค่า null ในฐานข้อมูล (ถ้า blank=True ก็มักจะใส่ null=True ด้วยสำหรับ CharField)
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    age = models.CharField(max_length=100, default='Unknown')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    personality = models.CharField(max_length=200, blank=True)
    story = models.TextField(blank=True)
    vaccinated = models.BooleanField(default=False)
    disability = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='pets/', blank=True, null=True)
    pet_type = models.CharField(max_length=10, choices=PET_TYPE_CHOICES)
    detail = models.CharField(max_length=500, blank=True)
    favorited_by = models.ManyToManyField(User, related_name='favorite_pets', blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_pet_type_display()})"

class PetImage(models.Model):
    pet = models.ForeignKey(Pet, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='pets/additional/')
    caption = models.CharField(max_length=255, blank=True, null=True, help_text="Optional caption for the image.")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.pet.name} ({self.id})"

    class Meta:
        ordering = ['uploaded_at']


class DonationCase(models.Model):
    case_id = models.CharField(max_length=10, unique=True)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='donation_cases')
    title = models.CharField(max_length=255)
    description = models.TextField()
    hospital = models.CharField(max_length=100, blank=True)
    amount_needed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_raised = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='donations/', blank=True, null=True)

    def __str__(self):
        return f"{self.case_id} - {self.title}"


class DonationSettings(models.Model):
    promptpay_qr_code = models.ImageField(
        upload_to='site_settings/qr_codes/',
        blank=True,
        null=True,
        verbose_name="PromptPay QR Code Image"
    )

    class Meta:
        verbose_name = "Donation Settings"
        verbose_name_plural = "Donation Settings"

    def clean(self):
        if not self.pk and DonationSettings.objects.exists():
            raise ValidationError("Can only have one Donation Settings instance.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return "Donation Settings"


class Product(models.Model): # This model seems unused based on current context
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.name

class AboutContent(models.Model):
    what_we_do_title = models.CharField(max_length=100, default="What we do?")
    what_we_do_content = models.TextField(default="At PawPal, we rescue, care for and rehome stray dogs and cats.")
    what_we_do_content2 = models.TextField(default="We work with kind-hearted volunteers and loving adopters to give every furry friend a second chance at life.")
    tagline = models.TextField(default="From street to sofa — we're here for every paw. 🐾")
    why_we_do_title = models.CharField(max_length=100, default="Why we do it?")
    why_we_do_content = models.TextField(default="We believe every dog and cat deserves love, safety, and a place to call home. No paw should be left behind.")
    why_we_do_content2 = models.TextField(default="We do this because they can't ask for help — but we can help them. ❤️")

    class Meta:
        verbose_name = "About Us Content"
        verbose_name_plural = "About Us Content"

    def __str__(self):
        return "About Us Page Content"


class PetStatistics(models.Model):
    stats_title = models.CharField(max_length=100, default="Hope in Numbers")
    treated_count = models.IntegerField(default=200)
    treated_label = models.CharField(max_length=100, default="Sick and injured animals treated")
    adopted_count = models.IntegerField(default=99)
    adopted_label = models.CharField(max_length=100, default="Animals adopted to new homes")
    neutered_count = models.IntegerField(default=112)
    neutered_label = models.CharField(max_length=100, default="Animals neutered and vaccinated")

    class Meta:
        verbose_name = "Pet Statistics"
        verbose_name_plural = "Pet Statistics"

    def __str__(self):
        return "Pet Statistics"


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    is_new = models.BooleanField(default=False)
    url = models.URLField(max_length=5000, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            queryset = BlogPost.objects.all().exclude(pk=self.pk)
            counter = 1
            while queryset.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ContactInfo(models.Model):
    phone = models.CharField(max_length=20, default="1212312121")
    opening_hours = models.TextField(default="mon - fri (9:00 - 18:00)")
    closing_days = models.CharField(max_length=100, default="close every 2nd sun")
    description = models.TextField(default="เราเป็นองค์กรที่ช่วยเหลือสุนัขและแมวจรจัดให้ได้รับความรักและการดูแลอย่างดีที่สุด")

    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"

    def __str__(self):
        return "Contact Information"

class YourModel(models.Model): # This model seems unused or a placeholder
    your_url = models.URLField(max_length=5000)

    def __str__(self):
        return self.your_url

class UserFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'pet')

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.pet.name}"


class AdoptionApplication(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_UNDER_REVIEW = 'under_review'
    STATUS_CANCELED = 'canceled'

    APPLICATION_STATUS_CHOICES = [
        (STATUS_PENDING, 'รอดำเนินการ (Pending)'),
        (STATUS_APPROVED, 'อนุมัติแล้ว (Approved)'),
        (STATUS_REJECTED, 'ถูกปฏิเสธ (Rejected)'),
        (STATUS_UNDER_REVIEW, 'กำลังตรวจสอบ (Under Review)'),
        (STATUS_CANCELED, 'ยกเลิกแล้ว (Canceled)'),
    ]

    first_name = models.CharField(max_length=100, verbose_name="ชื่อจริง")
    last_name = models.CharField(max_length=100, verbose_name="นามสกุล")
    address = models.CharField(max_length=255, verbose_name="ที่อยู่")
    subdistrict = models.CharField(max_length=100, blank=True, null=True, verbose_name="ตำบล/แขวง")
    district = models.CharField(max_length=100, blank=True, null=True, verbose_name="อำเภอ/เขต")
    province = models.CharField(max_length=100, blank=True, null=True, verbose_name="จังหวัด")
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="รหัสไปรษณีย์")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="เบอร์โทรศัพท์")
    email = models.EmailField(blank=True, null=True, verbose_name="อีเมล")
    household = models.TextField(blank=True, null=True, verbose_name="บุคคลในครัวเรือน")
    other_pets = models.TextField(blank=True, null=True, verbose_name="สัตว์เลี้ยงอื่นๆ (ถ้ามี)")
    property_description = models.TextField(blank=True, null=True, verbose_name="รายละเอียดที่พักอาศัย")
    job_working_hours = models.CharField(max_length=255, blank=True, null=True, verbose_name="อาชีพและเวลาทำงาน")
    motivation = models.TextField(blank=True, null=True, verbose_name="เหตุผลที่ต้องการรับเลี้ยง")
    apply_date = models.DateTimeField(auto_now_add=True, verbose_name="วันที่ยื่นคำขอ")
    status = models.CharField(
        max_length=20,
        choices=APPLICATION_STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='สถานะคำขอ'
    )
    pets = models.ManyToManyField(Pet, related_name='applications', verbose_name="สัตว์เลี้ยงที่ขอรับเลี้ยง")

    # --- START: เพิ่ม Field สำหรับนัดหมายสัมภาษณ์ ---
    interview_datetime = models.DateTimeField(
        verbose_name="วันและเวลานัดหมายสัมภาษณ์ (Video Call)",
        null=True,
        blank=True, # ทำให้ field นี้ไม่บังคับกรอกในเบื้องต้น
        help_text="ผู้ใช้เลือกวันเวลาสำหรับ Video Call กับผู้ประสานงาน"
    )
    # --- END: เพิ่ม Field สำหรับนัดหมายสัมภาษณ์ ---

    def __str__(self):
        pet_names = ", ".join([pet.name for pet in self.pets.all()])
        return f"คำขอจาก {self.first_name} {self.last_name} สำหรับ {pet_names} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        is_new_application = self._state.adding
        old_status = None
        if not is_new_application:
            try:
                old_instance = AdoptionApplication.objects.get(pk=self.pk)
                old_status = old_instance.status
            except AdoptionApplication.DoesNotExist:
                old_status = self.STATUS_PENDING
        super().save(*args, **kwargs)
        if old_status != self.STATUS_APPROVED and self.status == self.STATUS_APPROVED:
            pets_marked_adopted_count = 0
            for pet in self.pets.all():
                if not pet.is_adopted:
                    pet.is_adopted = True
                    pet.save()
                    pets_marked_adopted_count += 1
            if pets_marked_adopted_count > 0:
                stats, created = PetStatistics.objects.get_or_create(pk=1)
                stats.adopted_count = F('adopted_count') + pets_marked_adopted_count
                stats.save()
        elif old_status == self.STATUS_APPROVED and self.status != self.STATUS_APPROVED:
            pets_reverted_count = 0
            for pet in self.pets.all():
                other_approved_apps_for_pet = AdoptionApplication.objects.filter(
                    pets=pet, status=self.STATUS_APPROVED
                ).exclude(pk=self.pk).exists()
                if pet.is_adopted and not other_approved_apps_for_pet:
                    pet.is_adopted = False
                    pet.save()
                    pets_reverted_count += 1
            if pets_reverted_count > 0:
                stats, created = PetStatistics.objects.get_or_create(pk=1)
                stats.adopted_count = F('adopted_count') - pets_reverted_count
                stats.save()

    class Meta:
        verbose_name = "คำขอรับเลี้ยง"
        verbose_name_plural = "คำขอรับเลี้ยงทั้งหมด"
        ordering = ['-apply_date']


class DonationRecord(models.Model):
    donation_case = models.ForeignKey(
        DonationCase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='records',
        verbose_name="เคสบริจาค (ถ้ามี)"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="ผู้บริจาค (ถ้าล็อกอิน)"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="จำนวนเงิน")
    payment_method = models.CharField(max_length=50, verbose_name="ช่องทางการชำระเงิน")
    slip_image = models.ImageField(upload_to='donation_slips/', blank=True, null=True, verbose_name="รูปสลิป")
    donated_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่บริจาค")

    def __str__(self):
        if self.donation_case:
            return f"บริจาค {self.amount} บาท ให้เคส {self.donation_case.case_id} โดย {self.user.username if self.user else 'ผู้ไม่ประสงค์ออกนาม'}"
        else:
            return f"บริจาคทั่วไป {self.amount} บาท โดย {self.user.username if self.user else 'ผู้ไม่ประสงค์ออกนาม'}"

    class Meta:
        verbose_name = "รายการบริจาค"
        verbose_name_plural = "รายการบริจาคทั้งหมด"
        ordering = ['-donated_at']

class Conversation(models.Model):
    user = models.ForeignKey(User, related_name='chat_conversations_with_admin', on_delete=models.CASCADE)
    admin = models.ForeignKey(User, related_name='chat_conversations_with_user', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'is_staff': True})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        admin_username = self.admin.username if self.admin else "Admin"
        return f"Conversation between {self.user.username} and {admin_username}"

    class Meta:
        unique_together = ('user', 'admin')
        ordering = ['-updated_at']

class ChatMessage(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE, null=True, blank=True)
    sender = models.ForeignKey(User, related_name='sent_chat_messages', on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    is_admin_message = models.BooleanField(default=False)

    def __str__(self):
        sender_name = self.sender.username if self.sender else "System"
        return f"From {sender_name}: {self.content[:50]}"

    class Meta:
        ordering = ['timestamp']

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="ผู้รับการแจ้งเตือน")
    message = models.TextField(verbose_name="ข้อความแจ้งเตือน")
    link = models.URLField(max_length=200, blank=True, null=True, verbose_name="ลิงก์ที่เกี่ยวข้อง") # สำหรับคลิกไปยังหน้ารายละเอียด
    is_read = models.BooleanField(default=False, verbose_name="อ่านแล้ว")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="เวลาที่สร้าง")
    notification_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="ประเภทการแจ้งเตือน") # เช่น 'adoption_status', 'appointment_confirm'

    class Meta:
        ordering = ['-created_at'] # แสดงอันล่าสุดก่อน
        verbose_name = "การแจ้งเตือน"
        verbose_name_plural = "การแจ้งเตือนทั้งหมด"

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message[:30]}"

