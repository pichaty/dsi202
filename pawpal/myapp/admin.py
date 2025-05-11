# ใน work/dsi202/pawpal/myapp/admin.py

from django.contrib import admin
from django.contrib import admin
from django.utils.html import format_html
from .models import Pet, DonationCase, DonationSettings, DonationRecord # เพิ่ม DonationSettings, DonationRecord
from django.contrib import admin
from .models import Product
from django.contrib import admin
from .models import Pet, PetImage
# Import ValidationError จาก django.core.exceptions ถ้ายังไม่มี
from django.core.exceptions import ValidationError

#test
class DonationCaseInline(admin.TabularInline):
    model = DonationCase
    extra = 0
    readonly_fields = ('case_id', 'title', 'amount_needed', 'amount_raised')
    can_delete = False
    show_change_link = True

class PetImageInline(admin.TabularInline): # หรือ admin.StackedInline
    model = PetImage
    extra = 1 # จำนวนฟอร์มสำหรับเพิ่มรูปภาพใหม่ที่จะแสดง
    fields = ('image', 'caption') # ฟิลด์ที่ต้องการให้แสดงใน inline form
    # readonly_fields = ('uploaded_at',) # ถ้าต้องการแสดงวันที่อัปโหลดแต่ไม่ให้แก้ไข


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'pet_type', 'breed', 'gender', 'age', 'vaccinated', 'image_tag','detail','story')
    list_filter = ('pet_type', 'gender', 'vaccinated','detail','story')
    search_fields = ('name', 'breed', 'story', 'personality','story')
    inlines = [DonationCaseInline, PetImageInline] 

    def image_tag(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="60" height="60" style="object-fit: cover;" />', obj.photo.url)
        return "-"
    image_tag.short_description = 'Photo'

@admin.register(DonationCase)
class DonationCaseAdmin(admin.ModelAdmin):
    list_display = ('case_id', 'pet', 'title', 'amount_needed', 'amount_raised')
    search_fields = ('case_id', 'title', 'description', 'pet__name')
    list_filter = ('hospital',)

@admin.register(DonationSettings)
class DonationSettingsAdmin(admin.ModelAdmin):
    """Admin สำหรับตั้งค่าการบริจาคส่วนกลาง"""
    list_display = ('promptpay_qr_code_preview',) # เพิ่ม preview รูปในรายการ

    def has_add_permission(self, request):
        # อนุญาตให้เพิ่มได้แค่ 1 รายการเท่านั้น
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # ไม่อนุญาตให้ลบ (หรือจะอนุญาตก็ได้ถ้าจำเป็น)
        # return False # ถ้าต้องการไม่อนุญาตให้ลบเลย
        return super().has_delete_permission(request, obj)


    def promptpay_qr_code_preview(self, obj):
        if obj.promptpay_qr_code:
            return format_html('<img src="{}" width="100" height="auto" />', obj.promptpay_qr_code.url)
        return "No QR Code"
    promptpay_qr_code_preview.short_description = 'QR Code Preview'


# เพิ่ม DonationRecord ใน Admin ด้วย เพื่อดูรายการบริจาคที่เข้ามา
@admin.register(DonationRecord)
class DonationRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'donation_case', 'user', 'amount', 'payment_method', 'donated_at', 'slip_image_preview')
    list_filter = ('payment_method', 'donated_at', 'donation_case__title')
    search_fields = ('donation_case__case_id', 'donation_case__title', 'user__username', 'user__email')
    readonly_fields = ('donated_at',) # ให้ฟิลด์เวลาบริจาคแก้ไขไม่ได้

    def slip_image_preview(self, obj):
        if obj.slip_image:
            # แสดงรูปสลิปขนาดเล็กในรายการ
            return format_html('<img src="{}" width="50" height="auto" style="max-height: 80px; object-fit: contain;" />', obj.slip_image.url)
        return "No Slip"
    slip_image_preview.short_description = 'Slip Image'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')  # จะแสดงชื่อและรูปภาพในหน้าลิสต์

# admin.py
from django.contrib import admin
from .models import AboutContent, PetStatistics, BlogPost, ContactInfo

@admin.register(AboutContent)
class AboutContentAdmin(admin.ModelAdmin):
    """แอดมินสำหรับเนื้อหาหน้า About Us"""
    fieldsets = (
        ('What We Do', {
            'fields': ('what_we_do_title', 'what_we_do_content', 'what_we_do_content2', 'tagline')
        }),
        ('Why We Do It', {
            'fields': ('why_we_do_title', 'why_we_do_content', 'why_we_do_content2')
        }),
    )

    def has_add_permission(self, request):
        # ป้องกันการสร้างรายการซ้ำ ให้แก้ไขได้เฉพาะข้อมูลที่มีอยู่แล้ว
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(PetStatistics)
class PetStatisticsAdmin(admin.ModelAdmin):
    """แอดมินสำหรับสถิติข้อมูลสัตว์เลี้ยง"""
    fieldsets = (
        ('General', {
            'fields': ('stats_title',)
        }),
        ('Treated Animals', {
            'fields': ('treated_count', 'treated_label')
        }),
        ('Adopted Animals', {
            'fields': ('adopted_count', 'adopted_label')
        }),
        ('Neutered Animals', {
            'fields': ('neutered_count', 'neutered_label')
        }),
    )

    def has_add_permission(self, request):
        # ป้องกันการสร้างรายการซ้ำ ให้แก้ไขได้เฉพาะข้อมูลที่มีอยู่แล้ว
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

# ในไฟล์ admin.py
from django.contrib import admin
from .models import BlogPost

from django.utils.html import format_html


from django.utils.html import format_html

from django.utils.html import format_html

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_new', 'created_at', 'url_display')
    search_fields = ('title', 'content')
    list_filter = ('is_new', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'image', 'is_new')
        }),
        ('การเชื่อมโยง', {
            'fields': ('url', 'slug'),
            # ลบ 'collapse' ออก เพื่อให้ฟิลด์ url และ slug แสดงอยู่
        }),
    )

    def url_display(self, obj):
        if obj.url:
            # ใช้ format_html เพื่อสร้างลิงก์ที่เปิดในแท็บใหม่
            return format_html('<a href="{0}" target="_blank">{0}</a>', obj.url)
        return "No URL"

    url_display.short_description = 'URL'


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    """แอดมินสำหรับข้อมูลการติดต่อ"""
    fieldsets = (
        ('Contact Details', {
            'fields': ('phone', 'opening_hours', 'closing_days', 'description')
        }),
    )

    def has_add_permission(self, request):
        # ป้องกันการสร้างรายการซ้ำ ให้แก้ไขได้เฉพาะข้อมูลที่มีอยู่แล้ว
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

#adopt

# ใน work/dsi202/pawpal/myapp/admin.py

# ใน work/dsi202/pawpal/myapp/admin.py

from django.contrib import admin
from .models import AdoptionApplication, Pet # ตรวจสอบว่า Pet ก็ถูก import ด้วยถ้ายังไม่มี

@admin.register(AdoptionApplication)
class AdoptionApplicationAdmin(admin.ModelAdmin):
    # แก้ไข list_display โดยเปลี่ยน 'is_approved' เป็น 'status'
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'apply_date', 'display_applied_pets', 'status') # <--- แก้ไขตรงนี้
    list_filter = ('status', 'apply_date') # <--- เปลี่ยน 'is_approved' เป็น 'status'
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'address', 'motivation', 'pets__name', 'pets__id')
    date_hierarchy = 'apply_date'
    readonly_fields = ('apply_date',)

    fieldsets = (
        (None, {
            # แก้ไข fieldsets โดยเปลี่ยน 'is_approved' เป็น 'status'
            'fields': ('status', ('first_name', 'last_name'), ('email', 'phone_number')) # <--- แก้ไขตรงนี้
        }),
        ('Address Information', {
            'fields': ('address', 'subdistrict', 'district', 'province', 'postal_code')
        }),
        ('Adoption Details', {
            'fields': ('household', 'other_pets', 'property_description', 'job_working_hours', 'motivation')
        }),
        ('Applied Pets', {
            'fields': ('pets',)
        }),
        ('Timestamps', {
            'fields': ('apply_date',),
        }),
    )
    filter_horizontal = ('pets',)

    def display_applied_pets(self, obj):
        return ", ".join([f"{pet.name} (ID: {pet.id})" for pet in obj.pets.all()])
    display_applied_pets.short_description = 'Applied for Pets'

    # หากมี action approve_selected_applications ให้ปรับปรุง logic ตรงนี้
    def approve_selected_applications(self, request, queryset):
        updated_count = 0
        for application in queryset:
            if application.status != AdoptionApplication.STATUS_APPROVED: # ตรวจสอบสถานะปัจจุบัน
                application.status = AdoptionApplication.STATUS_APPROVED  # เปลี่ยนสถานะเป็น approved
                application.save() # เรียก save() method ของ AdoptionApplication
                updated_count +=1
        if updated_count > 0:
            self.message_user(request, f"{updated_count} adoption applications were successfully approved.")
        else:
            self.message_user(request, "No applications were updated (they might have been already approved).")

    approve_selected_applications.short_description = "Approve selected applications"

    actions = [approve_selected_applications]
