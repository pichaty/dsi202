from django.db import models


class Pet(models.Model):
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
    age = models.CharField(max_length=100,default=False)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    personality = models.CharField(max_length=200)
    story = models.TextField(blank=True)
    vaccinated = models.BooleanField(default=False)
    disability = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='pets/', blank=True, null=True)
    pet_type = models.CharField(max_length=10, choices=PET_TYPE_CHOICES)
    detail = models.CharField(max_length=200, blank=True)
    

    def __str__(self):
        return self.name

class DonationCase(models.Model):
    case_id = models.CharField(max_length=10, unique=True)  # e.g., "No. D07"
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

# models.py
from django.db import models

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

# ในไฟล์ models.py
from django.db import models
from django.utils.text import slugify

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    is_new = models.BooleanField(default=False)
    url = models.URLField(max_length=5000, blank=True, null=True)  # เพิ่มความยาวเป็น 5000
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

