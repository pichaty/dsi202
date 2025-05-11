# work/dsi202/pawpal/myapp/views.py

from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.db.models import Q, Prefetch
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from decimal import Decimal

from .models import (
    Pet, UserFavorite, BlogPost, AboutContent, PetStatistics,
    ContactInfo, DonationCase, AdoptionApplication, DonationRecord, DonationSettings, PetImage
)
from django.contrib.auth.models import User # Import User model

# ... (โค้ด views ที่มีอยู่แล้ว) ...

# --- New Views for Profile Dropdown ---
@login_required
def user_profile_view(request):
    """
    แสดงข้อมูลผู้ใช้งานเบื้องต้น
    """
    context = {
        'current_user': request.user
    }
    return render(request, 'myapp/user_profile.html', context)

@login_required
def my_adoption_applications_view(request):
    """
    แสดงสถานะคำขอรับเลี้ยงสัตว์ของผู้ใช้
    กรองจาก email ของผู้ใช้ที่ล็อกอิน เนื่องจาก AdoptionApplication ปัจจุบันไม่มี ForeignKey ไปยัง User โดยตรง
    """
    applications = AdoptionApplication.objects.filter(email=request.user.email).order_by('-apply_date')
    context = {
        'applications': applications
    }
    return render(request, 'myapp/my_adoption_applications.html', context)

@login_required
def my_adopted_pets_view(request):
    """
    แสดงสัตว์เลี้ยงที่ผู้ใช้เคยรับเลี้ยงและได้รับการอนุมัติแล้ว
    กรองจาก email และ is_approved = True
    """
    # ดึง application ที่อนุมัติแล้วและ email ตรงกับ user ปัจจุบัน
    approved_applications = AdoptionApplication.objects.filter(
        email=request.user.email,
        is_approved=True
    ).prefetch_related('pets') # prefetch_related เพื่อประสิทธิภาพในการดึงข้อมูล pets

    adopted_pets_list = []
    for app in approved_applications:
        for pet in app.pets.filter(is_adopted=True): # ตรวจสอบว่า pet is_adopted จริงๆ
            if pet not in adopted_pets_list: # ป้องกันการแสดงสัตว์เลี้ยงซ้ำหากอยู่ในหลาย application (กรณีพิเศษ)
                adopted_pets_list.append(pet)
    
    context = {
        'adopted_pets': adopted_pets_list
    }
    return render(request, 'myapp/my_adopted_pets.html', context)

@login_required
def my_donations_view(request):
    """
    แสดงประวัติการบริจาคของผู้ใช้
    """
    donations = DonationRecord.objects.filter(user=request.user).order_by('-donated_at')
    context = {
        'donations': donations
    }
    return render(request, 'myapp/my_donations.html', context)

@login_required
def account_settings_view(request):
    """
    หน้าหลักสำหรับการตั้งค่าบัญชี อาจมีลิงก์ไปยังหน้าย่อยๆ ของ allauth
    """
    # หน้านี้สามารถมีลิงก์ไปยัง:
    # {% url 'account_change_password' %}
    # {% url 'account_email' %}
    # {% url 'socialaccount_connections' %} (ถ้าใช้ social login)
    return render(request, 'myapp/account_settings.html')

@login_required
def notifications_placeholder_view(request):
    """
    Placeholder view for notifications.
    """
    # For now, this can just render a simple template or redirect
    # to the chat page if that's the primary notification method.
    # return redirect('chat_view_name') # If you have a named URL for chat
    return render(request, 'myapp/notifications_placeholder.html')


# 1. FBV: หน้า Home
def home(request):
    adopt_pets = Pet.objects.filter(is_adopted=False)
    donation_cases = DonationCase.objects.all()

    return render(request, 'myapp/home.html', {
        'adopt_pets': adopt_pets,
        'donation_cases': donation_cases,
    })

# 2. FBV: หน้า Donate (แก้ไขส่วนนี้)
def donate(request):
    pets_in_need_cases = DonationCase.objects.all()
    pets_for_gallery = [case.pet for case in pets_in_need_cases[:3]] if pets_in_need_cases else []
    donation_cases = DonationCase.objects.all().order_by('-id')
    donation_settings = DonationSettings.objects.first()

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST':
        # Handle General Donation form submission (AJAX)
        amount_str = request.POST.get('donationAmount')
        payment_method = request.POST.get('paymentMethod')
        slip_image = request.FILES.get('slip_image')
        # donation_type = request.POST.get('donationType') # อาจจะเก็บไว้ถ้าต้องการ

        try:
            amount = Decimal(amount_str) if amount_str else Decimal('0.00')
            if amount <= 0:
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'จำนวนเงินบริจาคไม่ถูกต้อง'})
                # สำหรับ non-AJAX (ซึ่งไม่ควรเกิดขึ้นแล้วถ้า JavaScript ทำงานถูก)
                # สามารถเพิ่มการ redirect หรือ render พร้อม error message ได้ถ้าต้องการ
        except (ValueError, TypeError):
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'รูปแบบจำนวนเงินไม่ถูกต้อง'})

        if payment_method == 'PromptPay' and not slip_image:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'กรุณาแนบสลิปสำหรับการบริจาคด้วย PromptPay'})

        try:
            DonationRecord.objects.create(
                donation_case=None, # สำหรับ General Donation (ถ้าโมเดลอนุญาตให้เป็น NULL)
                user=request.user if request.user.is_authenticated else None,
                amount=amount,
                payment_method=payment_method,
                slip_image=slip_image
            )

            if is_ajax:
                return JsonResponse({'success': True})
            else:
                # Fallback สำหรับกรณีที่ JavaScript ไม่ทำงาน หรือ request ไม่ใช่ AJAX
                return redirect('donation_thank_you') # หรือ URL อื่นที่เหมาะสม

        except Exception as e:
            print(f"Error saving general donation: {e}") # Log error ไว้ที่ server
            if is_ajax:
                return JsonResponse({'success': False, 'error': f'เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}'})
            # Fallback สำหรับ non-AJAX
            # context = { ... context เดิม ... , 'error_message': 'เกิดข้อผิดพลาดในการบันทึกข้อมูล'}
            # return render(request, 'myapp/donate.html', context)


    # สำหรับ GET request
    context = {
        'pets': pets_for_gallery,
        'donation_cases': donation_cases,
        'donation_settings': donation_settings,
    }
    return render(request, 'myapp/donate.html', context)


# 3. CBV: Pet Detail
class PetDetailView(DetailView):
    model = Pet
    template_name = 'myapp/pet_detail.html'


# 4. FBV: Adopt Catalog
def adopt_catalog(request):
     pets = Pet.objects.filter(is_adopted=False)
     return render(request, 'myapp/adopt_catalog.html', {'pets': pets})


# 5. FBV: Donate Detail
def donate_detail(request, pk):
    case = get_object_or_404(DonationCase, pk=pk)
    donation_settings = DonationSettings.objects.first()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST':
        amount_str = request.POST.get('donationAmount')
        payment_method = request.POST.get('paymentMethod')
        slip_image = request.FILES.get('slip_image')
        # case_id = request.POST.get('case_id') # ไม่จำเป็นต้องใช้ case_id จากฟอร์ม เพราะเรามี pk จาก URL

        try:
            amount = Decimal(amount_str) if amount_str else Decimal('0.00')
            if amount <= 0:
                 if is_ajax:
                     return JsonResponse({'success': False, 'error': 'จำนวนเงินบริจาคไม่ถูกต้อง'})
                 # Fallback
                 context = {'case': case, 'donation_settings': donation_settings, 'error_message': 'จำนวนเงินบริจาคไม่ถูกต้อง'}
                 return render(request, 'myapp/donate_detail.html', context)
        except (ValueError, TypeError):
             if is_ajax:
                return JsonResponse({'success': False, 'error': 'รูปแบบจำนวนเงินไม่ถูกต้อง'})
             # Fallback
             context = {'case': case, 'donation_settings': donation_settings, 'error_message': 'รูปแบบจำนวนเงินไม่ถูกต้อง'}
             return render(request, 'myapp/donate_detail.html', context)

        if payment_method == 'PromptPay' and not slip_image:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'กรุณาแนบสลิปสำหรับการบริจาคด้วย PromptPay'})
            # Fallback
            context = {'case': case, 'donation_settings': donation_settings, 'error_message': 'กรุณาแนบสลิปสำหรับการบริจาคด้วย PromptPay'}
            return render(request, 'myapp/donate_detail.html', context)

        try:
            DonationRecord.objects.create(
                donation_case=case,
                user=request.user if request.user.is_authenticated else None,
                amount=amount,
                payment_method=payment_method,
                slip_image=slip_image
            )
            # อัปเดต amount_raised ใน DonationCase
            case.amount_raised += amount
            case.save()

            if is_ajax:
                return JsonResponse({'success': True})
            else:
                return redirect('donation_thank_you')

        except Exception as e:
            print(f"Error saving donation for case {pk}: {e}")
            if is_ajax:
                return JsonResponse({'success': False, 'error': f'เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}'})
            # Fallback
            context = {'case': case, 'donation_settings': donation_settings, 'error_message': 'เกิดข้อผิดพลาดในการบันทึกข้อมูล'}
            return render(request, 'myapp/donate_detail.html', context)

    # สำหรับ GET requests
    context = {
        'case': case,
        'donation_settings': donation_settings
    }
    return render(request, 'myapp/donate_detail.html', context)

# 6. FBV: Donation Thank You Page
def donation_thank_you_view(request):
    return render(request, 'myapp/donation_thank_you.htm')

# 7. FBV: About Us Page (เดิมชื่อ about, เปลี่ยนเป็น about_us เพื่อความชัดเจน)
def about_us(request):
    about = AboutContent.objects.first()
    stats = PetStatistics.objects.first()
    contact = ContactInfo.objects.first()
    blog_posts = BlogPost.objects.all().order_by('-created_at')[:4]

    context = {
        'about': about,
        'stats': stats,
        'contact': contact,
        'blog_posts': blog_posts,
    }
    return render(request, 'myapp/about.html', context)

# 8. FBV: Blog Detail (ถ้ามี)
def blog_detail(request, blog_id=None, slug=None):
    if blog_id:
        blog = get_object_or_404(BlogPost, id=blog_id)
    elif slug:
        blog = get_object_or_404(BlogPost, slug=slug)
    else:
        raise Http404("Blog post not found.")

    context = {
        'blog': blog,
    }
    # return render(request, 'myapp/blog_detail.html', context) # ถ้ามี template นี้
    return HttpResponse(f"Blog Detail for: {blog.title}") # Placeholder


# 9. FBV: Toggle Favorite
@login_required
def toggle_favorite(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    favorite, created = UserFavorite.objects.get_or_create(
        user=request.user,
        pet=pet
    )
    removed = False
    is_favorite = True
    if not created:
        favorite.delete()
        is_favorite = False
        removed = True
    favorite_count = UserFavorite.objects.filter(user=request.user).count()
    return JsonResponse({
        'is_favorite': is_favorite,
        'removed': removed,
        'pet_id': pet_id,
        'favorite_count': favorite_count
    })

# 10. FBV: Check Favorites (AJAX)
@login_required
@require_POST # ทำให้รับเฉพาะ POST request
def check_favorites(request):
    try:
        data = json.loads(request.body)
        pet_ids = data.get('pet_ids', [])
        if not isinstance(pet_ids, list): # ตรวจสอบประเภทข้อมูล
            return JsonResponse({'error': 'pet_ids must be a list'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_favorites = UserFavorite.objects.filter(
        user=request.user,
        pet_id__in=pet_ids
    ).values_list('pet_id', flat=True)
    
    # แปลง pet_id ใน user_favorites เป็น string เพื่อให้เปรียบเทียบได้ถูกต้อง
    # หรือแปลง pet_id ที่รับมาจาก client เป็น int
    favorites_set = set(map(str, user_favorites))
    favorites = {str(pet_id): str(pet_id) in favorites_set for pet_id in pet_ids}

    return JsonResponse({'favorites': favorites})

# 11. FBV: Favorites Page
@login_required
def favorites_view(request):
    favorite_pets = Pet.objects.filter(
        userfavorite__user=request.user
    ).order_by('-userfavorite__created_at')
    return render(request, 'myapp/favorites.html', {
        'favorite_pets': favorite_pets
    })

# 12. FBV: Toggle Favorite Pet (อาจซ้ำซ้อนกับ toggle_favorite, พิจารณารวมหรือลบ)
# @login_required
# def toggle_favorite_pet(request, pet_id):
#     pet = get_object_or_404(Pet, id=pet_id)
#     user = request.user
#     if user in pet.favorited_by.all():
#         pet.favorited_by.remove(user)
#         favorited = False
#     else:
#         pet.favorited_by.add(user)
#         favorited = True
#     return JsonResponse({'favorited': favorited})


# 13. FBV: Adoption Form View
@login_required
def adoption_form_view(request):
    if request.method == 'POST':
        # ดึงข้อมูลจากฟอร์ม
        # (ควรมีการ validate ข้อมูลด้วย Django Forms เพื่อความปลอดภัยและ UX ที่ดี)
        application = AdoptionApplication.objects.create(
            # user=request.user, # ถ้าต้องการผูกกับ User ที่ login
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
            address=request.POST.get('address', ''),
            subdistrict=request.POST.get('subdistrict', ''),
            district=request.POST.get('district', ''),
            province=request.POST.get('province', ''),
            postal_code=request.POST.get('postal_code', ''),
            phone_number=request.POST.get('phone_number', ''),
            email=request.POST.get('email', ''),
            household=request.POST.get('household', ''),
            other_pets=request.POST.get('other_pets', ''),
            property_description=request.POST.get('property_description', ''),
            job_working_hours=request.POST.get('job_working_hours', ''),
            motivation=request.POST.get('motivation', ''),
        )
        
        selected_pet_ids_str = request.POST.get('selected_pet_ids', '')
        pet_ids_list_for_application = [] # เก็บ ID ของสัตว์เลี้ยงที่จะผูกกับ application

        if selected_pet_ids_str:
            try:
                pet_ids_list_for_application = [int(id_str) for id_str in selected_pet_ids_str.split(',') if id_str.isdigit()]
                selected_pets_for_save = Pet.objects.filter(id__in=pet_ids_list_for_application)
                if selected_pets_for_save.exists():
                    application.pets.set(selected_pets_for_save)
            except ValueError:
                pass # จัดการ error ถ้า id ไม่ใช่ตัวเลข

        # หลังจากสร้าง Application และผูกสัตว์เลี้ยงสำเร็จแล้ว
        # ให้ลบสัตว์เลี้ยงที่อยู่ใน pet_ids_list_for_application ออกจาก UserFavorite ของผู้ใช้ปัจจุบัน
        if request.user.is_authenticated and pet_ids_list_for_application:
            UserFavorite.objects.filter(user=request.user, pet_id__in=pet_ids_list_for_application).delete()
            print(f"DEBUG: Removed pets {pet_ids_list_for_application} from favorites for user {request.user.username}")

        return redirect(reverse('adoption_thank_you'))

    else: # GET request
        # ... (โค้ดส่วน GET request เหมือนเดิม) ...
        selected_pet_ids_str = request.GET.get('pets', '') # จากปุ่ม "Let's Adopt" ใน favorites.html
        selected_pets_for_display = []
        hidden_pet_ids_value = '' # สำหรับ input hidden ในฟอร์ม

        if selected_pet_ids_str:
            try:
                pet_ids_list = [int(id_str) for id_str in selected_pet_ids_str.split(',') if id_str.isdigit()]
                selected_pets_for_display = Pet.objects.filter(id__in=pet_ids_list)
                hidden_pet_ids_value = ",".join(map(str, pet_ids_list)) # สร้าง string สำหรับ input hidden
            except ValueError:
                 pass

        context = {
            'selected_pets': selected_pets_for_display,
            'selected_pet_ids_for_form': hidden_pet_ids_value, # ส่งไปให้ template ใช้ใน hidden input
        }
        return render(request, 'myapp/adoption_form.html', context)

# 14. FBV: Adoption Thank You Page
def adoption_thank_you_view(request):
    return render(request, 'myapp/adoption_thank_you.html')


def get_pet_detail_ajax(request, pet_id):
    try:
        pet = Pet.objects.prefetch_related('additional_images').get(pk=pet_id) # ใช้ prefetch_related เพื่อประสิทธิภาพ
        is_favorite = False
        if request.user.is_authenticated:
            is_favorite = UserFavorite.objects.filter(user=request.user, pet=pet).exists()
        additional_images_data = []
        for img in pet.additional_images.all(): # วนลูปดึงข้อมูลรูปภาพเพิ่มเติม
            additional_images_data.append({
                'url': img.image.url,
                'caption': img.caption or ""
            })
        pet_data = {
            'id': pet.id,
            'name': pet.name, # หรือ pet.pet_identifier ถ้ามี
            'breed': pet.breed,
            'gender_display': pet.get_gender_display(),
            'age': pet.age,
            'vaccinated': pet.vaccinated,
            'disability': pet.disability or "-",
            'personality': pet.personality or "-",
            'detail': pet.detail or "-",
            'story': pet.story or "This pet doesn't have a story written yet...",
            'photo_url': pet.photo.url if pet.photo else None, # ส่ง None ถ้าไม่มีรูปหลัก
            'is_favorite_by_current_user': is_favorite,
            'additional_images': additional_images_data # << เพิ่มข้อมูลรูปภาพเพิ่มเติม
        }
        return JsonResponse({'success': True, 'pet': pet_data})
    except Pet.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Pet not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    