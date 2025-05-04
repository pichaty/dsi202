from django.contrib import admin
from django.contrib import admin
from django.utils.html import format_html
from .models import Pet, DonationCase
from django.contrib import admin
from .models import Product


class DonationCaseInline(admin.TabularInline):
    model = DonationCase
    extra = 0
    readonly_fields = ('case_id', 'title', 'amount_needed', 'amount_raised')
    can_delete = False
    show_change_link = True

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'pet_type', 'breed', 'gender', 'age', 'vaccinated', 'image_tag','detail','story')
    list_filter = ('pet_type', 'gender', 'vaccinated','detail','story')
    search_fields = ('name', 'breed', 'story', 'personality','story')
    inlines = [DonationCaseInline]

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


