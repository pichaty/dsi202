# ใน work/dsi202/pawpal/myapp/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify # นำเข้า slugify
# ตรวจสอบให้แน่ใจว่า Pet model ถูก import แล้ว

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

    # ลบ __str__ ที่ซ้ำกันตรงนี้ออก


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


class AdoptionApplication(models.Model):
    # หากใช้ระบบผู้ใช้ ให้เพิ่มบรรทัดนี้
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adoption_applications', null=True, blank=True)

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
    is_approved = models.BooleanField(default=False) # ฟิลด์ is_approved ควรมีแค่ครั้งเดียวที่นี่


    # เชื่อมใบสมัครกับสัตว์เลี้ยงหลายตัว (ใช้ ManyToManyField)
    pets = models.ManyToManyField(Pet, related_name='applications')

    def save(self, *args, **kwargs):
        print("AdoptionApplication save method called.") # เพิ่มบรรทัดนี้

        is_approved = models.BooleanField(default=False)
    pets = models.ManyToManyField(Pet, related_name='applications')

    def save(self, *args, **kwargs):
        print("\n--- save method START ---") # เพิ่มบรรทัดนี้
        print(f"  AdoptionApplication PK: {self.pk}, is_approved (before super save): {self.is_approved}") # เพิ่มบรรทัดนี้

        is_approved_changed_to_true = False
        if self.pk: # ตรวจสอบว่า instance นี้มีอยู่ในฐานข้อมูลแล้วหรือยัง
            try:
                # ดึงข้อมูล instance เก่าจากฐานข้อมูล ถ้ามี pk
                old_instance = AdoptionApplication.objects.get(pk=self.pk)
                # ตรวจสอบว่า is_approved เปลี่ยนจาก False เป็น True หรือไม่
                is_approved_changed_to_true = self.is_approved and not old_instance.is_approved
                print(f"  is_approved changed from {old_instance.is_approved} to {self.is_approved}") # เพิ่มบรรทัดนี้
                print(f"  is_approved_changed_to_true is {is_approved_changed_to_true}") # เพิ่มบรรทัดนี้
            except AdoptionApplication.DoesNotExist:
                # ถ้าเป็น instance ใหม่ (ยังไม่มีในฐานข้อมูล)
                print("  Old instance not found (likely creating new).") # เพิ่มบรรทัดนี้
                pass # ไม่ต้องทำอะไร

        # เรียก save() ดั้งเดิมก่อน
        print("  Calling super().save()...") # เพิ่มบรรทัดนี้
        super().save(*args, **kwargs)
        print("  super().save() called. Application saved.") # เพิ่มบรรทัดนี้


        # หลังจาก super().save()
        # ตรวจสอบอีกครั้งว่า is_approved ยังคงเป็น True อยู่
        if self.is_approved:
            print("  Application is_approved is True.") # เพิ่มบรรทัดนี้
            # หากสถานะ is_approved ถูกเปลี่ยนจาก False เป็น True ในการบันทึกครั้งนี้
            if is_approved_changed_to_true:
                print("  is_approved_changed_to_true condition met. Proceeding to update pets.") # เพิ่มบรรทัดนี้
                # วนลูปผ่านสัตว์เลี้ยงทั้งหมดที่เกี่ยวข้องกับใบสมัครนี้
                pets_in_application = self.pets.all()
                print(f"  Found {pets_in_application.count()} pet(s) in this application.") # เพิ่มบรรทัดนี้

                for pet in pets_in_application:
                    print(f"  Checking pet: {pet.name} (PK: {pet.pk})...") # เพิ่มบรรทัดนี้
                    print(f"    Current is_adopted status: {pet.is_adopted}") # เพิ่มบรรทัดนี้

                    # ตรวจสอบอีกครั้งว่าสัตว์เลี้ยงยังไม่ได้ถูกรับเลี้ยง (ป้องกันการเขียนทับสถานะ)
                    if not pet.is_adopted:
                        print(f"    Pet {pet.name} is not yet adopted. Attempting to update.") # เพิ่มบรรทัดนี้
                        pet.is_adopted = True
                        try:
                            pet.save() # บันทึกการเปลี่ยนแปลงสถานะของสัตว์เลี้ยงแต่ละตัว
                            print(f"    SUCCESS: Pet {pet.name} status updated to is_adopted=True.") # เพิ่มบรรทัดนี้
                        except Exception as e:
                            print(f"    ERROR: Failed to save pet {pet.name}: {e}") # เพิ่มบรรทัดนี้
                    else:
                        print(f"    Pet {pet.name} is already adopted.") # เพิ่มบรรทัดนี้
            else:
                print("  is_approved was already True or this is a new application. Pet update skipped.") # เพิ่มบรรทัดนี้
        else:
            print("  Application is_approved is False. Pet update skipped.") # เพิ่มบรรทัดนี้


        print("--- save method END ---\n") # เพิ่มบรรทัดนี้

    def __str__(self):
        return f"Application by {self.first_name} {self.last_name} on {self.apply_date.strftime('%Y-%m-%d')}"