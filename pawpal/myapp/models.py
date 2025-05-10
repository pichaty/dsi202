# ใน work/dsi202/pawpal/myapp/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.exceptions import ValidationError # นำเข้า ValidationError

class Pet(models.Model):
    is_adopted = models.BooleanField(default=False) # ฟิลด์นี้ถูกต้องแล้ว
    PET_TYPE_CHOICES = [
        ('dog', 'Dog'),
        ('cat', 'Cat'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    # ปรับ default ของ age ให้เหมาะสม ถ้าเป็น CharField
    age = models.CharField(max_length=100, default='Unknown') # เปลี่ยน default จาก False
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    personality = models.CharField(max_length=200)
    story = models.TextField(blank=True)
    vaccinated = models.BooleanField(default=False)
    disability = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='pets/', blank=True, null=True)
    pet_type = models.CharField(max_length=10, choices=PET_TYPE_CHOICES)
    detail = models.CharField(max_length=200, blank=True)
    favorited_by = models.ManyToManyField(User, related_name='favorite_pets', blank=True)

    def __str__(self):
        return self.name


class DonationCase(models.Model):
    case_id = models.CharField(max_length=10, unique=True)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='donation_cases')
    title = models.CharField(max_length=255)
    description = models.TextField()
    hospital = models.CharField(max_length=100, blank=True)
    amount_needed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_raised = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='donations/', blank=True, null=True)
    # ลบฟิลด์ qr_code_image ออกจาก DonationCase
    # qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True) # ลบบรรทัดนี้

    def __str__(self):
        return f"{self.case_id} - {self.title}"

# เพิ่ม Model ใหม่สำหรับเก็บ QR Code ส่วนกลาง
class DonationSettings(models.Model):
    promptpay_qr_code = models.ImageField(
        upload_to='site_settings/qr_codes/', # เปลี่ยน path การเก็บไฟล์
        blank=True,
        null=True,
        verbose_name="PromptPay QR Code Image"
    )

    class Meta:
        verbose_name = "Donation Settings"
        verbose_name_plural = "Donation Settings"

    # จำกัดให้มีได้เพียง 1 instance
    def clean(self):
        if not self.pk and DonationSettings.objects.exists():
            raise ValidationError("Can only have one Donation Settings instance.")

    def save(self, *args, **kwargs):
        self.clean() # เรียก clean ก่อน save เพื่อตรวจสอบข้อจำกัด
        super().save(*args, **kwargs)

    def __str__(self):
        return "Donation Settings"


class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/')

class AboutContent(models.Model):
    """โมเดลสำหรับเนื้อหาหลักในหน้า About Us"""
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

class PetStatistics(models.Model):
    """โมเดลสำหรับสถิติข้อมูลสัตว์เลี้ยง"""
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
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ContactInfo(models.Model):
    """โมเดลสำหรับข้อมูลการติดต่อ"""
    phone = models.CharField(max_length=20, default="1212312121")
    opening_hours = models.TextField(default="mon - fri (9:00 - 18:00)")
    closing_days = models.CharField(max_length=100, default="close every 2nd sun")
    description = models.TextField(default="เราเป็นองค์กรที่ช่วยเหลือสุนัขและแมวจรจัดให้ได้รับความรักและการดูแลอย่างดีที่สุด")

    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"

class YourModel(models.Model):
    your_url = models.URLField(max_length=5000)

class UserFavorite(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'pet')


# work/dsi202/pawpal/myapp/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.db.models import F # เพิ่ม F object สำหรับ atomic updates

# ... (Pet, DonationCase, DonationSettings, etc.) ...
# ตรวจสอบว่า PetStatistics ถูก import แล้ว
# from .models import PetStatistics # ถ้า PetStatistics อยู่ในไฟล์เดียวกัน ไม่ต้อง import ซ้ำ

class AdoptionApplication(models.Model):
    # ... (fields ของ AdoptionApplication เหมือนเดิม) ...
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    subdistrict = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    household = models.TextField(blank=True, null=True)
    other_pets = models.TextField(blank=True, null=True)
    property_description = models.TextField(blank=True, null=True)
    job_working_hours = models.CharField(max_length=255, blank=True, null=True)
    motivation = models.TextField(blank=True, null=True)
    apply_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    pets = models.ManyToManyField(Pet, related_name='applications')

    def save(self, *args, **kwargs):
        print(f"\n--- AdoptionApplication save START (ID: {self.pk}) ---")
        
        old_is_approved = None
        is_new_application = self.pk is None # ตรวจสอบว่าเป็น object ใหม่หรือไม่

        if not is_new_application: # ถ้าเป็น object ที่มีอยู่แล้ว
            try:
                old_instance = AdoptionApplication.objects.get(pk=self.pk)
                old_is_approved = old_instance.is_approved
                print(f"  Old approval status for App ID {self.pk}: {old_is_approved}")
            except AdoptionApplication.DoesNotExist:
                print(f"  Warning: App ID {self.pk} provided, but old instance not found during save.")
                # ถ้าหา object เก่าไม่เจอ แต่มี pk อาจจะถือว่าเป็นการเปลี่ยนแปลงสถานะจาก default (False)
                old_is_approved = False # สมมติว่าสถานะเก่าคือ False
        else: # ถ้าเป็น object ใหม่
            old_is_approved = False # สถานะเริ่มต้นของ object ใหม่ (ก่อน save ครั้งแรก) คือยังไม่ approved
            print(f"  New application is being processed.")

        # เรียก super().save() ก่อน เพื่อให้ self.pk มีค่าแน่นอน และ self.pets.all() ทำงานได้ถูกต้อง
        super().save(*args, **kwargs)
        print(f"  AdoptionApplication (ID: {self.pk}) saved. Current is_approved: {self.is_approved}")

        # ตรวจสอบการเปลี่ยนแปลงสถานะ is_approved
        approval_newly_granted = old_is_approved is False and self.is_approved is True
        approval_newly_revoked = old_is_approved is True and self.is_approved is False

        pets_in_application = self.pets.all() # ดึงสัตว์เลี้ยงที่เกี่ยวข้องหลังจาก save แล้ว

        if approval_newly_granted:
            print(f"  Approval GRANTED for Application ID: {self.pk}. Processing pets...")
            pets_marked_adopted_count = 0
            for pet in pets_in_application:
                if not pet.is_adopted:
                    pet.is_adopted = True
                    pet.save()
                    pets_marked_adopted_count += 1
                    print(f"    Pet ID: {pet.id} (Name: {pet.name}) marked as adopted.")
                else:
                    print(f"    Pet ID: {pet.id} (Name: {pet.name}) was ALREADY adopted. Skipping.")
            
            if pets_marked_adopted_count > 0:
                stats, created = PetStatistics.objects.get_or_create(pk=1) # หรือเงื่อนไขอื่นในการ get stats
                stats.adopted_count = F('adopted_count') + pets_marked_adopted_count
                stats.save()
                stats.refresh_from_db()
                print(f"    PetStatistics.adopted_count INCREASED by {pets_marked_adopted_count}. New count: {stats.adopted_count}")

        elif approval_newly_revoked:
            print(f"  Approval REVOKED for Application ID: {self.pk}. Reverting pet status...")
            pets_reverted_count = 0
            for pet in pets_in_application:
                # เมื่อยกเลิก approve, เราจะตั้ง is_adopted เป็น False
                # ไม่ว่าสัตว์เลี้ยงตัวนี้จะถูก adopt โดย application อื่นหรือไม่ก็ตาม
                # ซึ่งอาจจะต้องพิจารณา logic นี้เพิ่มเติมถ้ามีหลาย application ต่อ 1 สัตว์เลี้ยง
                # แต่ตาม flow ปัจจุบัน 1 สัตว์เลี้ยงควรจะถูก adopt โดย 1 application ที่ approved เท่านั้น
                if pet.is_adopted: # เฉพาะตัวที่เคยถูก adopted (อาจจะโดย application นี้)
                    pet.is_adopted = False
                    pet.save()
                    pets_reverted_count += 1
                    print(f"    Pet ID: {pet.id} (Name: {pet.name}) reverted to NOT adopted.")
                else:
                    print(f"    Pet ID: {pet.id} (Name: {pet.name}) was ALREADY NOT adopted. Skipping.")

            if pets_reverted_count > 0:
                stats, created = PetStatistics.objects.get_or_create(pk=1)
                # ตรวจสอบว่า adopted_count ไม่ติดลบ
                current_adopted_count = stats.adopted_count
                new_adopted_count = max(0, current_adopted_count - pets_reverted_count) # ป้องกันค่าติดลบ
                stats.adopted_count = new_adopted_count
                # หรือจะใช้ stats.adopted_count = F('adopted_count') - pets_reverted_count ก็ได้ แต่ต้องมั่นใจว่า F() object จะไม่ทำให้ค่าติดลบ
                # stats.adopted_count = F('adopted_count') - pets_reverted_count
                stats.save()
                stats.refresh_from_db()
                print(f"    PetStatistics.adopted_count DECREASED by {pets_reverted_count} (from {current_adopted_count} to {new_adopted_count}). Current count: {stats.adopted_count}")
        else:
            print(f"  No change in approval status relevant to pet adoption status for App ID: {self.pk}. (is_approved: {self.is_approved}, old_is_approved: {old_is_approved})")

        print(f"--- AdoptionApplication save END (ID: {self.pk}) ---\n")

    def __str__(self):
        return f"Application by {self.first_name} {self.last_name} on {self.apply_date.strftime('%Y-%m-%d')}"

    def __str__(self):
        return f"Application by {self.first_name} {self.last_name} on {self.apply_date.strftime('%Y-%m-%d')}"

# ... (DonationRecord และโมเดลอื่นๆ) ...
    # ใน myapp/models.py

# เพิ่ม import User ที่ด้านบนสุด ถ้ายังไม่มี
from django.contrib.auth.models import User

class DonationRecord(models.Model):
    # แก้ไขบรรทัดนี้: เพิ่ม null=True, blank=True และเปลี่ยน on_delete เป็น models.SET_NULL ถ้าเหมาะสม
    donation_case = models.ForeignKey(
        DonationCase, 
        on_delete=models.SET_NULL,  # หรือ models.PROTECT หรือตามความเหมาะสม
        null=True, 
        blank=True, 
        related_name='records'
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    slip_image = models.ImageField(upload_to='donation_slips/')
    donated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.donation_case:
            return f"บริจาค {self.amount} บาท ให้เคส {self.donation_case.case_id}"
        else:
            return f"บริจาคทั่วไป {self.amount} บาท โดย {self.user.username if self.user else 'ผู้ไม่ประสงค์ออกนาม'}"
