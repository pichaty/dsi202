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


