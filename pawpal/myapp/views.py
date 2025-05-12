# work/dsi202/pawpal/myapp/views.py

from django.http import HttpResponse, JsonResponse, Http404
from django.views.generic import DetailView
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from decimal import Decimal

from .models import (
    Pet, UserFavorite, BlogPost, AboutContent, PetStatistics,
    ContactInfo, DonationCase, AdoptionApplication, DonationRecord,
    DonationSettings, PetImage
)

# --- Import เพิ่มเติมสำหรับ PromptPay QR Code ---
from promptpay import qrcode
import base64
from io import BytesIO
# -------------------------------------------

# --- Views for Profile Dropdown ---
@login_required
def user_profile_view(request):
    context = {
        'current_user': request.user
    }
    return render(request, 'myapp/user_profile.html', context)

@login_required
def my_adoption_applications_view(request):
    applications = AdoptionApplication.objects.filter(email=request.user.email).order_by('-apply_date')
    context = {
        'applications': applications
    }
    return render(request, 'myapp/my_adoption_applications.html', context)

@login_required
def my_adopted_pets_view(request):
    approved_applications = AdoptionApplication.objects.filter(
        email=request.user.email,
        status=AdoptionApplication.STATUS_APPROVED
    ).prefetch_related('pets')

    adopted_pets_list = []
    for app in approved_applications:
        for pet in app.pets.filter(is_adopted=True):
            if pet not in adopted_pets_list:
                adopted_pets_list.append(pet)
    context = {
        'adopted_pets': adopted_pets_list
    }
    return render(request, 'myapp/my_adopted_pets.html', context)

@login_required
def my_donations_view(request):
    donations = DonationRecord.objects.filter(user=request.user).order_by('-donated_at')
    context = {
        'donations': donations
    }
    return render(request, 'myapp/my_donations.html', context)

@login_required
def account_settings_view(request):
    return render(request, 'myapp/account_settings.html')

@login_required
def notifications_placeholder_view(request):
    return render(request, 'myapp/notifications_placeholder.html')


# --- Main Application Views ---

def home(request):
    adopt_pets = Pet.objects.filter(is_adopted=False)
    donation_cases = DonationCase.objects.all().order_by('-id')
    context = {
        'adopt_pets': adopt_pets,
        'donation_cases': donation_cases,
    }
    return render(request, 'myapp/home.html', context)

def donate(request):
    donation_cases = DonationCase.objects.all().order_by('-id')
    donation_settings = DonationSettings.objects.first()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    promptpay_id_for_template = "0811072299"  # <<<<===== YOUR PROMPTPAY ID (Keep this if it's a central ID)

    if request.method == 'POST' and is_ajax:
        action = request.POST.get('action')
        amount_str = request.POST.get('donationAmount')

        try:
            amount = Decimal(amount_str) if amount_str else Decimal('0.00')
            if amount <= 0:
                return JsonResponse({'success': False, 'error': 'จำนวนเงินบริจาคไม่ถูกต้อง'})
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'รูปแบบจำนวนเงินไม่ถูกต้อง'})

        # Action: Generate QR Code
        if action == 'generate_qr' and request.POST.get('paymentMethod') == 'PromptPay':
            # Use the central promptpay_id_for_template for general donations
            # If you have specific QR codes for general donation settings, you might fetch it from donation_settings.promptpay_id or similar
            # For now, using the hardcoded one for simplicity in this example.
            target_promptpay_id = promptpay_id_for_template # Or fetch from DonationSettings if you store it there.

            if target_promptpay_id and amount > 0:
                try:
                    payload = qrcode.generate_payload(target_promptpay_id, float(amount))
                    img_obj = qrcode.to_image(payload)
                    buffered = BytesIO()
                    img_obj.save(buffered, format="PNG")
                    qr_code_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    return JsonResponse({
                        'success': True,
                        'action': 'qr_generated',
                        'qr_code_image': qr_code_image_base64,
                        'amount': float(amount),
                        'promptpay_id_display': target_promptpay_id # Display the ID used
                    })
                except Exception as e:
                    error_message = f'เกิดข้อผิดพลาดในการสร้าง QR Code: {str(e)}'
                    return JsonResponse({'success': False, 'error': error_message})
            else:
                return JsonResponse({'success': False, 'error': 'ไม่สามารถสร้าง QR Code ได้ กรุณาตรวจสอบข้อมูล PromptPay ID และจำนวนเงิน'})

        # Action: Submit Slip (after QR generation for general donation)
        elif request.POST.get('paymentMethod') == 'PromptPay' and request.FILES.get('slip_image'):
            slip_image = request.FILES.get('slip_image')
            try:
                DonationRecord.objects.create(
                    donation_case=None, # General donation
                    user=request.user if request.user.is_authenticated else None,
                    amount=amount,
                    payment_method='PromptPay',
                    slip_image=slip_image
                )
                return JsonResponse({'success': True, 'action': 'slip_submitted'})
            except Exception as e:
                error_message = f'เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}'
                return JsonResponse({'success': False, 'error': error_message})
        
        # Action: Handle 'Other' payment method for general donation
        elif request.POST.get('paymentMethod') == 'Other':
            try:
                DonationRecord.objects.create(
                    donation_case=None,
                    user=request.user if request.user.is_authenticated else None,
                    amount=amount,
                    payment_method='Other', # Explicitly 'Other'
                    slip_image=None 
                )
                return JsonResponse({'success': True, 'action': 'other_payment_submitted'})
            except Exception as e:
                error_message = f'เกิดข้อผิดพลาดในการบันทึกข้อมูล (ช่องทางอื่น): {str(e)}'
                return JsonResponse({'success': False, 'error': error_message})

        return JsonResponse({'success': False, 'error': 'Invalid request parameters for POST.'})

    # GET request or initial page load
    context = {
        'donation_cases': donation_cases,
        'donation_settings': donation_settings, # This might hold a sitewide QR if you implement it that way
                                              # but the dynamic QR generation is handled by AJAX.
    }
    return render(request, 'myapp/donate.html', context)


class PetDetailView(DetailView):
    model = Pet
    template_name = 'myapp/pet_detail.html'

def adopt_catalog(request):
    pets = Pet.objects.filter(is_adopted=False)
    return render(request, 'myapp/adopt_catalog.html', {'pets': pets})

def donate_detail(request, pk):
    case = get_object_or_404(DonationCase, pk=pk)
    donation_settings = DonationSettings.objects.first()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    # For donate_detail, promptpay_id_for_template should ideally come from donation_settings
    # or a specific field in the DonationCase model if each case can have a different one.
    # Using the central one from donation_settings if available, else a fallback.
    promptpay_id_for_template = donation_settings.promptpay_qr_code.name if donation_settings and donation_settings.promptpay_qr_code else "YOUR_DEFAULT_PROMPTPAY_ID_FOR_CASES"


    if request.method == 'POST' and is_ajax: # Ensure AJAX for POST handling here too
        action = request.POST.get('action')
        amount_str = request.POST.get('donationAmount')
        payment_method = request.POST.get('paymentMethod') # paymentMethod from the form
        slip_image = request.FILES.get('slip_image')

        try:
            amount = Decimal(amount_str) if amount_str else Decimal('0.00')
            if amount <= 0:
                return JsonResponse({'success': False, 'error': 'จำนวนเงินบริจาคไม่ถูกต้อง'})
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'รูปแบบจำนวนเงินไม่ถูกต้อง'})

        if action == 'generate_qr_case' and payment_method == 'PromptPay':
             # For specific case QR generation, use the central promptpay_id or case-specific if available
            target_promptpay_id_case = promptpay_id_for_template # Default to central, or modify to get from `case` model

            if target_promptpay_id_case and amount > 0:
                try:
                    payload = qrcode.generate_payload(target_promptpay_id_case, float(amount))
                    img_obj = qrcode.to_image(payload)
                    buffered = BytesIO()
                    img_obj.save(buffered, format="PNG")
                    qr_code_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    return JsonResponse({
                        'success': True,
                        'action': 'qr_generated_case',
                        'qr_code_image': qr_code_image_base64,
                        'amount': float(amount),
                        'promptpay_id_display': target_promptpay_id_case
                    })
                except Exception as e:
                    error_message = f'เกิดข้อผิดพลาดในการสร้าง QR Code: {str(e)}'
                    return JsonResponse({'success': False, 'error': error_message})
            else:
                return JsonResponse({'success': False, 'error': 'ไม่สามารถสร้าง QR Code ได้ กรุณาตรวจสอบข้อมูล PromptPay ID และจำนวนเงิน'})

        elif payment_method == 'PromptPay' and slip_image:
            try:
                DonationRecord.objects.create(
                    donation_case=case,
                    user=request.user if request.user.is_authenticated else None,
                    amount=amount,
                    payment_method=payment_method,
                    slip_image=slip_image
                )
                case.amount_raised = Decimal(case.amount_raised) + amount
                case.save()
                return JsonResponse({'success': True, 'action': 'slip_submitted_case'})
            except Exception as e:
                error_message = f'เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}'
                return JsonResponse({'success': False, 'error': error_message})

        elif payment_method == 'Other': # Handling "Other" for case donations
            try:
                DonationRecord.objects.create(
                    donation_case=case,
                    user=request.user if request.user.is_authenticated else None,
                    amount=amount,
                    payment_method=payment_method, # 'Other'
                    slip_image=None
                )
                case.amount_raised = Decimal(case.amount_raised) + amount
                case.save()
                return JsonResponse({'success': True, 'action': 'other_payment_submitted_case'})
            except Exception as e:
                error_message = f'เกิดข้อผิดพลาดในการบันทึกข้อมูล (ช่องทางอื่น): {str(e)}'
                return JsonResponse({'success': False, 'error': error_message})

        return JsonResponse({'success': False, 'error': 'Invalid request parameters for POST on detail page.'})


    context = {
        'case': case,
        'donation_settings': donation_settings, # For displaying the central QR if needed, or other settings.
                                                # Dynamic QR is now handled by AJAX.
    }
    return render(request, 'myapp/donate_detail.html', context)


def donation_thank_you_view(request):
    return render(request, 'myapp/donation_thank_you.htm')

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

def blog_detail(request, blog_id=None, slug=None):
    if blog_id:
        blog = get_object_or_404(BlogPost, id=blog_id)
    elif slug:
        blog = get_object_or_404(BlogPost, slug=slug)
    else:
        raise Http404("Blog post not found.")
    return HttpResponse(f"Blog Detail for: {blog.title}")

@login_required
@require_POST
def toggle_favorite(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    favorite, created = UserFavorite.objects.get_or_create(user=request.user, pet=pet)
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

@login_required
@require_POST
def check_favorites(request):
    try:
        data = json.loads(request.body)
        pet_ids_str = data.get('pet_ids', [])
        if not isinstance(pet_ids_str, list):
            return JsonResponse({'error': 'pet_ids must be a list'}, status=400)
        pet_ids_int = [int(pid_str) for pid_str in pet_ids_str if pid_str.isdigit()]
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON or pet_ids format'}, status=400)

    user_favorites_pet_ids = UserFavorite.objects.filter(
        user=request.user,
        pet_id__in=pet_ids_int
    ).values_list('pet_id', flat=True)
    favorites_status = {str(pid_int): (pid_int in user_favorites_pet_ids) for pid_int in pet_ids_int}
    return JsonResponse({'favorites': favorites_status})

@login_required
def favorites_view(request):
    favorite_pets = Pet.objects.filter(userfavorite__user=request.user).order_by('-userfavorite__created_at')
    return render(request, 'myapp/favorites.html', {'favorite_pets': favorite_pets})

# work/dsi202/pawpal/myapp/views.py

from django.http import HttpResponse, JsonResponse, Http404
from django.views.generic import DetailView
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from decimal import Decimal
from datetime import datetime # <<<--- เพิ่ม import datetime

from .models import (
    Pet, UserFavorite, BlogPost, AboutContent, PetStatistics,
    ContactInfo, DonationCase, AdoptionApplication, DonationRecord,
    DonationSettings, PetImage
)
from promptpay import qrcode
import base64
from io import BytesIO

# ... (โค้ด view อื่นๆ ไม่เปลี่ยนแปลง) ...

@login_required # แนะนำให้ผู้ใช้ต้อง login ก่อนกรอกฟอร์ม
def adoption_form_view(request):
    if request.method == 'POST':
        application = AdoptionApplication()
        application.first_name = request.POST.get('first_name', '')
        application.last_name = request.POST.get('last_name', '')
        application.address = request.POST.get('address', '')
        application.subdistrict = request.POST.get('subdistrict', '')
        application.district = request.POST.get('district', '')
        application.province = request.POST.get('province', '')
        application.postal_code = request.POST.get('postal_code', '')
        application.phone_number = request.POST.get('phone_number', '')
        # ถ้า user login อยู่แล้ว ให้ใช้ email จาก user object เป็น default
        application.email = request.POST.get('email', request.user.email if request.user.is_authenticated else '')
        application.household = request.POST.get('household', '')
        application.other_pets = request.POST.get('other_pets', '')
        application.property_description = request.POST.get('property_description', '')
        application.job_working_hours = request.POST.get('job_working_hours', '')
        application.motivation = request.POST.get('motivation', '')

        # --- START: รับข้อมูลวันเวลานัดหมาย ---
        interview_datetime_str = request.POST.get('interview_datetime', '')
        if interview_datetime_str:
            try:
                # Flatpickr ส่งค่ามาในรูปแบบ "Y-m-d H:i"
                application.interview_datetime = datetime.strptime(interview_datetime_str, '%Y-%m-%d %H:%M')
            except ValueError:
                # หาก format ไม่ถูกต้อง อาจจะตั้งเป็น None หรือแจ้ง error
                application.interview_datetime = None
                # messages.error(request, "Invalid date/time format for interview.") # (Optional)
        else:
            application.interview_datetime = None
        # --- END: รับข้อมูลวันเวลานัดหมาย ---

        application.save() # บันทึกข้อมูลหลักของ application ก่อน

        selected_pet_ids_str = request.POST.get('selected_pet_ids', '')
        pet_ids_list_for_application = []
        if selected_pet_ids_str:
            try:
                pet_ids_list_for_application = [int(id_str) for id_str in selected_pet_ids_str.split(',') if id_str.isdigit()]
                selected_pets_for_save = Pet.objects.filter(id__in=pet_ids_list_for_application)
                if selected_pets_for_save.exists():
                    application.pets.set(selected_pets_for_save) # เพิ่มสัตว์เลี้ยงเข้าไปใน ManyToManyField
            except ValueError:
                # จัดการกรณี ID ไม่ใช่ตัวเลข (ถ้าจำเป็น)
                pass

        # ลบสัตว์เลี้ยงที่สมัครออกจากรายการโปรด (ถ้าผู้ใช้ login อยู่)
        if request.user.is_authenticated and pet_ids_list_for_application:
            UserFavorite.objects.filter(user=request.user, pet_id__in=pet_ids_list_for_application).delete()

        return redirect(reverse('adoption_thank_you'))
    else:
        selected_pet_ids_str = request.GET.get('pets', '')
        selected_pets_for_display = []
        hidden_pet_ids_value = '' # สำหรับส่ง ID สัตว์เลี้ยงไปกับฟอร์ม
        if selected_pet_ids_str:
            try:
                pet_ids_list = [int(id_str) for id_str in selected_pet_ids_str.split(',') if id_str.isdigit()]
                selected_pets_for_display = Pet.objects.filter(id__in=pet_ids_list)
                hidden_pet_ids_value = ",".join(map(str, pet_ids_list))
            except ValueError:
                # ถ้า ID ไม่ใช่ตัวเลข ก็ปล่อยให้ list ว่างไป
                pass

        # ดึงข้อมูลเบื้องต้นของผู้ใช้ที่ login อยู่ (ถ้ามี)
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['first_name'] = request.user.first_name
            initial_data['last_name'] = request.user.last_name
            initial_data['email'] = request.user.email
            # คุณสามารถเพิ่ม field อื่นๆ ที่ต้องการดึงจาก User model ได้

        context = {
            'selected_pets': selected_pets_for_display,
            'selected_pet_ids_for_form': hidden_pet_ids_value,
            'initial_data': initial_data, # ส่ง initial_data ไปยัง template
        }
        return render(request, 'myapp/adoption_form.html', context)

# ... (โค้ด view อื่นๆ ไม่เปลี่ยนแปลง) ...

def adoption_thank_you_view(request):
    return render(request, 'myapp/adoption_thank_you.html')

# ... (โค้ด get_pet_detail_ajax และ chat_view ไม่เปลี่ยนแปลง) ...

def get_pet_detail_ajax(request, pet_id):
    try:
        pet = Pet.objects.prefetch_related('additional_images').get(pk=pet_id)
        is_favorite = False
        if request.user.is_authenticated:
            is_favorite = UserFavorite.objects.filter(user=request.user, pet=pet).exists()

        additional_images_data = [{'url': img.image.url, 'caption': img.caption or ""} for img in pet.additional_images.all() if img.image]
        pet_data = {
            'id': pet.id, 'name': pet.name, 'breed': pet.breed,
            'gender_display': pet.get_gender_display(), 'age': pet.age,
            'vaccinated': pet.vaccinated, 'disability': pet.disability or "-",
            'personality': pet.personality or "-", 'detail': pet.detail or "-",
            'story': pet.story or "This pet doesn't have a story written yet...",
            'photo_url': pet.photo.url if pet.photo else None,
            'is_favorite_by_current_user': is_favorite,
            'additional_images': additional_images_data
        }
        return JsonResponse({'success': True, 'pet': pet_data})
    except Pet.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Pet not found.'}, status=404)
    except Exception as e:
        print(f"Error in get_pet_detail_ajax for pet_id {pet_id}: {str(e)}")
        return JsonResponse({'success': False, 'error': 'An unexpected error occurred.'}, status=500)

# work/dsi202/pawpal/myapp/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required # ถ้าต้องการให้เฉพาะ user ที่ login เข้าแชทได้

@login_required # (Optional)
def chat_view(request):
    # สามารถเพิ่ม context อื่นๆ ที่ต้องการส่งไป template ได้
    return render(request, 'myapp/chat.html')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages # Optional: สำหรับแสดงข้อความแจ้งเตือน
from .models import AdoptionApplication

# ... (Views อื่นๆ) ...

@login_required
def cancel_adoption_application_view(request, application_id):
    application = get_object_or_404(AdoptionApplication, id=application_id)

    # ตรวจสอบว่าเป็นเจ้าของคำขอหรือไม่ (ป้องกันการยกเลิกคำขอของผู้อื่น)
    # สมมติว่าคุณเก็บ email ของผู้ยื่นใน Model AdoptionApplication
    if application.email != request.user.email:
        messages.error(request, "You do not have permission to cancel this application.")
        return redirect('my_adoption_applications') # หรือหน้าอื่นที่เหมาะสม

    # อนุญาตให้ยกเลิกได้เฉพาะบางสถานะ เช่น Pending หรือ Under Review
    if application.status in [AdoptionApplication.STATUS_PENDING, AdoptionApplication.STATUS_UNDER_REVIEW]:
        if request.method == 'POST':
            application.status = AdoptionApplication.STATUS_CANCELED
            application.save()
            messages.success(request, f"Adoption application APP-{application.id:05d} has been canceled.")
            return redirect('my_adoption_applications')
        else:
            # แสดงหน้ายืนยันการยกเลิก (ถ้าต้องการ)
            # return render(request, 'myapp/confirm_cancel_adoption.html', {'application': application})
            # หรือถ้าไม่ต้องการหน้ายืนยัน ก็สามารถยกเลิกได้เลยเมื่อกดปุ่ม (ผ่าน POST request)
            messages.info(request, "This action should ideally be confirmed via a POST request.")
            return redirect('my_adoption_applications')
    else:
        messages.warning(request, f"This application cannot be canceled as it is already {application.get_status_display()}.")
        return redirect('my_adoption_applications')

