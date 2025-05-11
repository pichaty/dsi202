# work/dsi202/pawpal/myapp/views.py

from django.http import HttpResponse, JsonResponse, Http404
from django.views.generic import DetailView # ListView ไม่ได้ถูกใช้ในโค้ดปัจจุบัน
from django.db.models import Q # Q object ไม่ได้ถูกใช้ในโค้ดปัจจุบัน
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from decimal import Decimal
# User model ถูก import แต่ไม่ได้ถูกใช้งานโดยตรงใน view functions บางตัว (request.user เพียงพอ)
# from django.contrib.auth.models import User

from .models import (
    Pet, UserFavorite, BlogPost, AboutContent, PetStatistics,
    ContactInfo, DonationCase, AdoptionApplication, DonationRecord,
    DonationSettings, PetImage # PetImage ถูก import แต่ไม่ได้ถูกใช้โดยตรงใน views นี้
)

# --- Views for Profile Dropdown ---
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
    (ถ้ามีการเพิ่ม ForeignKey ไปยัง User ใน Model `AdoptionApplication` ควรเปลี่ยนมา filter ด้วย `user=request.user`)
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
    """
    # ดึง application ที่อนุมัติแล้วและ email ตรงกับ user ปัจจุบัน
    # ใช้ค่าจาก choices ใน Model เพื่อความถูกต้องและอ่านง่าย
    approved_applications = AdoptionApplication.objects.filter(
        email=request.user.email,
        status=AdoptionApplication.STATUS_APPROVED # เปลี่ยนจาก is_approved=True
    ).prefetch_related('pets') # prefetch_related เพื่อประสิทธิภาพในการดึงข้อมูล pets

    adopted_pets_list = []
    for app in approved_applications:
        # ตรวจสอบว่า pet is_adopted จริงๆ ซึ่งควรจะถูกตั้งค่าใน Model `AdoptionApplication` save method
        for pet in app.pets.filter(is_adopted=True):
            if pet not in adopted_pets_list: # ป้องกันการแสดงสัตว์เลี้ยงซ้ำ
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
    หน้าหลักสำหรับการตั้งค่าบัญชี
    """
    return render(request, 'myapp/account_settings.html')

@login_required
def notifications_placeholder_view(request):
    """
    Placeholder view for notifications.
    """
    return render(request, 'myapp/notifications_placeholder.html')


# --- Main Application Views ---

# 1. FBV: หน้า Home
def home(request):
    adopt_pets = Pet.objects.filter(is_adopted=False)
    donation_cases = DonationCase.objects.all().order_by('-id') # เพิ่มการเรียงลำดับ
    context = {
        'adopt_pets': adopt_pets,
        'donation_cases': donation_cases,
    }
    return render(request, 'myapp/home.html', context)

# 2. FBV: หน้า Donate
def donate(request):
    donation_cases = DonationCase.objects.all().order_by('-id')
    # pets_for_gallery อาจจะไม่จำเป็นแล้วถ้า mission card ใช้รูป static
    # pets_in_need_cases = DonationCase.objects.all()
    # pets_for_gallery = [case.pet for case in pets_in_need_cases[:3]] if pets_in_need_cases else []
    donation_settings = DonationSettings.objects.first()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST':
        amount_str = request.POST.get('donationAmount')
        payment_method = request.POST.get('paymentMethod')
        slip_image = request.FILES.get('slip_image')

        try:
            amount = Decimal(amount_str) if amount_str else Decimal('0.00')
            if amount <= 0:
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'จำนวนเงินบริจาคไม่ถูกต้อง'})
                # Non-AJAX fallback (ควรมี error handling ที่ template ด้วย)
        except (ValueError, TypeError):
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'รูปแบบจำนวนเงินไม่ถูกต้อง'})

        if payment_method == 'PromptPay' and not slip_image:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'กรุณาแนบสลิปสำหรับการบริจาคด้วย PromptPay'})

        try:
            DonationRecord.objects.create(
                donation_case=None,
                user=request.user if request.user.is_authenticated else None,
                amount=amount,
                payment_method=payment_method,
                slip_image=slip_image
            )
            if is_ajax:
                return JsonResponse({'success': True})
            return redirect('donation_thank_you')
        except Exception as e:
            print(f"Error saving general donation: {e}")
            if is_ajax:
                return JsonResponse({'success': False, 'error': f'เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}'})
            # Non-AJAX fallback

    context = {
        # 'pets': pets_for_gallery, # ถ้าไม่ใช้แล้ว ลบออกได้
        'donation_cases': donation_cases,
        'donation_settings': donation_settings,
    }
    return render(request, 'myapp/donate.html', context)

# 3. CBV: Pet Detail
class PetDetailView(DetailView):
    model = Pet
    template_name = 'myapp/pet_detail.html'
    # context_object_name = 'pet' # Django ตั้งชื่อนี้โดย default อยู่แล้ว

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

        try:
            amount = Decimal(amount_str) if amount_str else Decimal('0.00')
            if amount <= 0:
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'จำนวนเงินบริจาคไม่ถูกต้อง'})
                # Fallback for non-AJAX
                context = {'case': case, 'donation_settings': donation_settings, 'error_message': 'จำนวนเงินบริจาคไม่ถูกต้อง'}
                return render(request, 'myapp/donate_detail.html', context)
        except (ValueError, TypeError):
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'รูปแบบจำนวนเงินไม่ถูกต้อง'})
            context = {'case': case, 'donation_settings': donation_settings, 'error_message': 'รูปแบบจำนวนเงินไม่ถูกต้อง'}
            return render(request, 'myapp/donate_detail.html', context)

        if payment_method == 'PromptPay' and not slip_image:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'กรุณาแนบสลิปสำหรับการบริจาคด้วย PromptPay'})
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
            case.amount_raised += amount
            case.save()

            if is_ajax:
                return JsonResponse({'success': True})
            return redirect('donation_thank_you')
        except Exception as e:
            print(f"Error saving donation for case {pk}: {e}")
            if is_ajax:
                return JsonResponse({'success': False, 'error': f'เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}'})
            context = {'case': case, 'donation_settings': donation_settings, 'error_message': 'เกิดข้อผิดพลาดในการบันทึกข้อมูล'}
            return render(request, 'myapp/donate_detail.html', context)

    context = {
        'case': case,
        'donation_settings': donation_settings
    }
    return render(request, 'myapp/donate_detail.html', context)

# 6. FBV: Donation Thank You Page
def donation_thank_you_view(request):
    return render(request, 'myapp/donation_thank_you.htm') # ตรวจสอบนามสกุลไฟล์ .htm หรือ .html

# 7. FBV: About Us Page
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

# 8. FBV: Blog Detail
def blog_detail(request, blog_id=None, slug=None):
    if blog_id:
        blog = get_object_or_404(BlogPost, id=blog_id)
    elif slug:
        blog = get_object_or_404(BlogPost, slug=slug)
    else:
        raise Http404("Blog post not found.")
    # context = {'blog': blog,}
    # return render(request, 'myapp/blog_detail.html', context) # ถ้ามี template นี้จริง
    return HttpResponse(f"Blog Detail for: {blog.title}") # Placeholder response

# 9. FBV: Toggle Favorite
@login_required
@require_POST # ควรใช้ POST สำหรับการเปลี่ยนแปลงข้อมูล
def toggle_favorite(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    favorite, created = UserFavorite.objects.get_or_create(
        user=request.user,
        pet=pet
    )
    removed = False
    is_favorite = True
    if not created: # ถ้าไม่ได้สร้างใหม่ แสดงว่ามีอยู่แล้ว -> ลบออก
        favorite.delete()
        is_favorite = False
        removed = True
    favorite_count = UserFavorite.objects.filter(user=request.user).count()
    return JsonResponse({
        'is_favorite': is_favorite,
        'removed': removed, # ส่งสถานะว่าลบออกหรือไม่ (สำหรับ favorites page)
        'pet_id': pet_id,
        'favorite_count': favorite_count
    })

# 10. FBV: Check Favorites (AJAX)
@login_required
@require_POST
def check_favorites(request):
    try:
        data = json.loads(request.body)
        pet_ids_str = data.get('pet_ids', []) # pet_ids จาก client อาจเป็น string หรือ int
        if not isinstance(pet_ids_str, list):
            return JsonResponse({'error': 'pet_ids must be a list'}, status=400)

        # แปลง ID ทั้งหมดเป็น int เพื่อ query และ map กลับเป็น string สำหรับ key ใน dict
        pet_ids_int = []
        for pid_str in pet_ids_str:
            try:
                pet_ids_int.append(int(pid_str))
            except ValueError:
                # จัดการกรณี ID ไม่ใช่ตัวเลข (อาจจะข้ามไปหรือ log error)
                pass

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_favorites_pet_ids = UserFavorite.objects.filter(
        user=request.user,
        pet_id__in=pet_ids_int # ใช้ list ของ int IDs
    ).values_list('pet_id', flat=True)

    # สร้าง dict สำหรับ response โดยใช้ string ID เป็น key
    favorites_status = {str(pid_int): (pid_int in user_favorites_pet_ids) for pid_int in pet_ids_int}

    return JsonResponse({'favorites': favorites_status})

# 11. FBV: Favorites Page
@login_required
def favorites_view(request):
    favorite_pets = Pet.objects.filter(
        userfavorite__user=request.user # Django ORM relationship lookup
    ).order_by('-userfavorite__created_at')
    return render(request, 'myapp/favorites.html', {'favorite_pets': favorite_pets})

# 12. FBV: Adoption Form View
@login_required
def adoption_form_view(request):
    if request.method == 'POST':
        application = AdoptionApplication() # สร้าง instance เปล่าก่อน
        # หากมีการผูกกับ user ที่ login ให้ทำที่นี่
        # if request.user.is_authenticated:
        # application.user = request.user # ถ้ามีฟิลด์ user ใน Model

        application.first_name = request.POST.get('first_name', '')
        application.last_name = request.POST.get('last_name', '')
        application.address = request.POST.get('address', '')
        application.subdistrict = request.POST.get('subdistrict', '')
        application.district = request.POST.get('district', '')
        application.province = request.POST.get('province', '')
        application.postal_code = request.POST.get('postal_code', '')
        application.phone_number = request.POST.get('phone_number', '')
        application.email = request.POST.get('email', request.user.email) # ใช้ email ของ user ที่ login เป็น default
        application.household = request.POST.get('household', '')
        application.other_pets = request.POST.get('other_pets', '')
        application.property_description = request.POST.get('property_description', '')
        application.job_working_hours = request.POST.get('job_working_hours', '')
        application.motivation = request.POST.get('motivation', '')
        # status จะเป็น default 'pending' ตามที่ตั้งใน Model

        application.save() # save ครั้งแรกเพื่อให้ได้ ID

        selected_pet_ids_str = request.POST.get('selected_pet_ids', '')
        pet_ids_list_for_application = []

        if selected_pet_ids_str:
            try:
                pet_ids_list_for_application = [int(id_str) for id_str in selected_pet_ids_str.split(',') if id_str.isdigit()]
                selected_pets_for_save = Pet.objects.filter(id__in=pet_ids_list_for_application)
                if selected_pets_for_save.exists():
                    application.pets.set(selected_pets_for_save) # ผูกสัตว์เลี้ยงหลังจาก application มี ID
            except ValueError:
                pass # จัดการ error ถ้า id ไม่ใช่ตัวเลข

        if request.user.is_authenticated and pet_ids_list_for_application:
            UserFavorite.objects.filter(user=request.user, pet_id__in=pet_ids_list_for_application).delete()
            # print(f"DEBUG: Removed pets {pet_ids_list_for_application} from favorites for user {request.user.username}")

        return redirect(reverse('adoption_thank_you'))
    else: # GET request
        selected_pet_ids_str = request.GET.get('pets', '')
        selected_pets_for_display = []
        hidden_pet_ids_value = ''

        if selected_pet_ids_str:
            try:
                pet_ids_list = [int(id_str) for id_str in selected_pet_ids_str.split(',') if id_str.isdigit()]
                selected_pets_for_display = Pet.objects.filter(id__in=pet_ids_list)
                hidden_pet_ids_value = ",".join(map(str, pet_ids_list))
            except ValueError:
                pass
        context = {
            'selected_pets': selected_pets_for_display,
            'selected_pet_ids_for_form': hidden_pet_ids_value,
        }
        return render(request, 'myapp/adoption_form.html', context)

# 13. FBV: Adoption Thank You Page (ย้ายเลขมาต่อกันเฉยๆ)
def adoption_thank_you_view(request):
    return render(request, 'myapp/adoption_thank_you.html')

# 14. FBV: AJAX Get Pet Detail
def get_pet_detail_ajax(request, pet_id):
    try:
        # ใช้ prefetch_related เพื่อดึง additional_images มาพร้อมกัน ลดจำนวน query
        pet = Pet.objects.prefetch_related('additional_images').get(pk=pet_id)
        is_favorite = False
        if request.user.is_authenticated:
            is_favorite = UserFavorite.objects.filter(user=request.user, pet=pet).exists()

        additional_images_data = []
        for img in pet.additional_images.all():
            additional_images_data.append({
                'url': img.image.url if img.image else None, # ป้องกันกรณี image field ว่าง
                'caption': img.caption or ""
            })

        pet_data = {
            'id': pet.id,
            'name': pet.name,
            'breed': pet.breed,
            'gender_display': pet.get_gender_display(),
            'age': pet.age,
            'vaccinated': pet.vaccinated,
            'disability': pet.disability or "-",
            'personality': pet.personality or "-",
            'detail': pet.detail or "-",
            'story': pet.story or "This pet doesn't have a story written yet...",
            'photo_url': pet.photo.url if pet.photo else None,
            'is_favorite_by_current_user': is_favorite,
            'additional_images': additional_images_data
        }
        return JsonResponse({'success': True, 'pet': pet_data})
    except Pet.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Pet not found.'}, status=404)
    except Exception as e:
        # Log a more detailed error on the server for debugging
        print(f"Error in get_pet_detail_ajax for pet_id {pet_id}: {str(e)}")
        return JsonResponse({'success': False, 'error': 'An unexpected error occurred.'}, status=500)