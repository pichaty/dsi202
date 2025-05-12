# work/dsi202/pawpal/myapp/views.py

from django.http import HttpResponse, JsonResponse, Http404
from django.views.generic import DetailView
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from decimal import Decimal
from datetime import datetime # ถูกต้อง
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from .models import Notification

from .models import (
    Pet, UserFavorite, BlogPost, AboutContent, PetStatistics,
    ContactInfo, DonationCase, AdoptionApplication, DonationRecord,
    DonationSettings, PetImage, Conversation, ChatMessage
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
    # เปลี่ยนระยะเวลาเป็น 24 ชั่วโมง
    time_threshold = timezone.now() - timezone.timedelta(hours=24)

    active_statuses = [
        AdoptionApplication.STATUS_PENDING,
        AdoptionApplication.STATUS_UNDER_REVIEW
    ]
    recent_completed_statuses = [
        AdoptionApplication.STATUS_APPROVED,
        AdoptionApplication.STATUS_REJECTED,
        AdoptionApplication.STATUS_CANCELED
    ]

    current_applications = AdoptionApplication.objects.filter(
        email=request.user.email
    ).filter(
        Q(status__in=active_statuses) |
        (Q(status__in=recent_completed_statuses) & Q(apply_date__gte=time_threshold))
    ).order_by('-apply_date').prefetch_related('pets')

    context = {
        'applications': current_applications,
        'page_title': 'Current & Recent adoption status'
    }
    return render(request, 'myapp/my_adoption_applications.html', context)

@login_required
def adoption_application_history_view(request):
    # กำหนดสถานะที่ถือว่าเสร็จสิ้นแล้ว
    completed_statuses = [
        AdoptionApplication.STATUS_REJECTED,
        AdoptionApplication.STATUS_APPROVED,
        AdoptionApplication.STATUS_CANCELED
    ]

    # ดึงข้อมูลคำขอรับเลี้ยงที่มีสถานะตรงกับที่กำหนด
    history_applications = AdoptionApplication.objects.filter(
        email=request.user.email,
        status__in=completed_statuses
    ).order_by('-apply_date').prefetch_related('pets')

    context = {
        'applications': history_applications,
        'page_title': 'History adoption status' # อัปเดตชื่อหัวข้อของหน้า
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
            if pet not in adopted_pets_list: # Ensure unique pets if they can be in multiple approved apps (though unlikely for adoption)
                adopted_pets_list.append(pet)
    context = {
        'adopted_pets': adopted_pets_list
    }
    return render(request, 'myapp/my_adopted_pets.html', context)

# work/dsi202/pawpal/myapp/views.py

@login_required
def my_donations_view(request):
    donations = DonationRecord.objects.filter(user=request.user) \
                                      .select_related('donation_case', 'donation_case__pet') \
                                      .order_by('-donated_at')
    context = {
        'donations': donations
    }
    return render(request, 'myapp/my_donations.html', context)

@login_required
def account_settings_view(request):
    # This is a placeholder, actual settings form would be needed
    return render(request, 'myapp/account_settings.html')




# --- Main Application Views ---

def home(request):
    adopt_pets = Pet.objects.filter(is_adopted=False).prefetch_related('additional_images')
    donation_cases = DonationCase.objects.all().order_by('-id').select_related('pet')
    context = {
        'adopt_pets': adopt_pets,
        'donation_cases': donation_cases,
    }
    return render(request, 'myapp/home.html', context)

def donate(request):
    donation_cases = DonationCase.objects.all().order_by('-id').select_related('pet')
    donation_settings = DonationSettings.objects.first()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    # Assuming a default or primary PromptPay ID for general donations if no specific case is chosen
    promptpay_id_for_template = donation_settings.promptpay_qr_code.name if donation_settings and hasattr(donation_settings, 'promptpay_qr_code') and donation_settings.promptpay_qr_code else "0811072299" # Fallback

    if request.method == 'POST' and is_ajax:
        action = request.POST.get('action')
        amount_str = request.POST.get('donationAmount')
        payment_method = request.POST.get('paymentMethod') # Ensure this is captured
        slip_image = request.FILES.get('slip_image') # Ensure this is captured

        try:
            amount = Decimal(amount_str) if amount_str else Decimal('0.00')
            if amount <= 0:
                return JsonResponse({'success': False, 'error': 'จำนวนเงินบริจาคไม่ถูกต้อง'})
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'รูปแบบจำนวนเงินไม่ถูกต้อง'})

        if action == 'generate_qr' and payment_method == 'PromptPay':
            target_promptpay_id = promptpay_id_for_template

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
                        'promptpay_id_display': target_promptpay_id
                    })
                except Exception as e:
                    error_message = f'เกิดข้อผิดพลาดในการสร้าง QR Code: {str(e)}'
                    return JsonResponse({'success': False, 'error': error_message})
            else:
                return JsonResponse({'success': False, 'error': 'ไม่สามารถสร้าง QR Code ได้ กรุณาตรวจสอบข้อมูล PromptPay ID และจำนวนเงิน'})

        elif payment_method == 'PromptPay' and slip_image: # Ensure this condition is met for slip submission
            try:
                DonationRecord.objects.create(
                    donation_case=None, # General donation
                    user=request.user if request.user.is_authenticated else None,
                    amount=amount,
                    payment_method='PromptPay', # Explicitly set
                    slip_image=slip_image
                )
                # Optionally, send a success message or redirect
                return JsonResponse({'success': True, 'action': 'slip_submitted', 'message': 'ส่งสลิปสำเร็จ ขอบคุณสำหรับการบริจาค'})
            except Exception as e:
                error_message = f'เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}'
                return JsonResponse({'success': False, 'error': error_message})

        elif payment_method == 'Other': # Handling 'Other' payment method
            try:
                DonationRecord.objects.create(
                    donation_case=None, # General donation
                    user=request.user if request.user.is_authenticated else None,
                    amount=amount,
                    payment_method='Other', # Explicitly set
                    slip_image=None # No slip for 'Other' usually
                )
                return JsonResponse({'success': True, 'action': 'other_payment_submitted', 'message': 'บันทึกการบริจาคช่องทางอื่นสำเร็จ ขอบคุณค่ะ'})
            except Exception as e:
                error_message = f'เกิดข้อผิดพลาดในการบันทึกข้อมูล (ช่องทางอื่น): {str(e)}'
                return JsonResponse({'success': False, 'error': error_message})

        return JsonResponse({'success': False, 'error': 'Invalid request parameters for POST.'})

    context = {
        'donation_cases': donation_cases,
        'donation_settings': donation_settings,
        'promptpay_id_display': promptpay_id_for_template # Pass this to template for display
    }
    return render(request, 'myapp/donate.html', context)


class PetDetailView(DetailView):
    model = Pet
    template_name = 'myapp/pet_detail.html'
    context_object_name = 'pet' # ensure context name is 'pet'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('additional_images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_favorite'] = UserFavorite.objects.filter(user=self.request.user, pet=self.object).exists()
        else:
            context['is_favorite'] = False
        return context


def adopt_catalog(request):
    pets = Pet.objects.filter(is_adopted=False).prefetch_related('additional_images')
    return render(request, 'myapp/adopt_catalog.html', {'pets': pets})

def donate_detail(request, pk):
    case = get_object_or_404(DonationCase.objects.select_related('pet'), pk=pk)
    donation_settings = DonationSettings.objects.first()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # --- ปรับ Logic การดึง promptpay_id ที่ถูกต้อง ---
    # 1. ใช้ promptpay_id จาก DonationCase ถ้ามี และไม่เป็นค่าว่าง
    # 2. ถ้าไม่มีใน Case หรือเป็นค่าว่าง ให้ใช้ default_promptpay_id จาก DonationSettings
    # 3. ถ้าไม่มีใน Settings หรือเป็นค่าว่าง ให้ใช้ค่า Fallback
    promptpay_id_for_template = None
    if hasattr(case, 'promptpay_id') and case.promptpay_id: # ตรวจสอบว่าเคสนี้มี field และค่า promptpay_id หรือไม่
        promptpay_id_for_template = case.promptpay_id
    elif donation_settings and hasattr(donation_settings, 'default_promptpay_id') and donation_settings.default_promptpay_id: # ถ้าไม่มี ให้ใช้ ID หลักจาก Settings
        promptpay_id_for_template = donation_settings.default_promptpay_id
    else:
        promptpay_id_for_template = "0811072299" # ถ้าไม่มีทั้งคู่ ให้ใช้ค่า Fallback
    # --- สิ้นสุดการปรับ Logic ---

    if request.method == 'POST' and is_ajax:
        action = request.POST.get('action')
        amount_str = request.POST.get('donationAmount')
        payment_method = request.POST.get('paymentMethod')
        slip_image = request.FILES.get('slip_image')

        try:
            amount = Decimal(amount_str) if amount_str else Decimal('0.00')
            if amount <= 0:
                return JsonResponse({'success': False, 'error': 'จำนวนเงินบริจาคไม่ถูกต้อง'})
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'รูปแบบจำนวนเงินไม่ถูกต้อง'})

        if action == 'generate_qr_case' and payment_method == 'PromptPay':
            target_promptpay_id_case = promptpay_id_for_template # ใช้ ID ที่ได้จาก logic ด้านบน

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
                record = DonationRecord.objects.create(
                    donation_case=case,
                    user=request.user if request.user.is_authenticated else None,
                    amount=amount,
                    payment_method=payment_method,
                    slip_image=slip_image
                )
                case.amount_raised = Decimal(case.amount_raised or 0) + amount
                case.save()
                return JsonResponse({'success': True, 'action': 'slip_submitted_case', 'message': 'ส่งสลิปสำเร็จ ขอบคุณสำหรับการบริจาค'})
            except Exception as e:
                error_message = f'เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}'
                return JsonResponse({'success': False, 'error': error_message})

        elif payment_method == 'Other':
            try:
                record = DonationRecord.objects.create(
                    donation_case=case,
                    user=request.user if request.user.is_authenticated else None,
                    amount=amount,
                    payment_method=payment_method,
                    slip_image=None
                )
                case.amount_raised = Decimal(case.amount_raised or 0) + amount
                case.save()
                return JsonResponse({'success': True, 'action': 'other_payment_submitted_case', 'message': 'บันทึกการบริจาคช่องทางอื่นสำเร็จ ขอบคุณค่ะ'})
            except Exception as e:
                error_message = f'เกิดข้อผิดพลาดในการบันทึกข้อมูล (ช่องทางอื่น): {str(e)}'
                return JsonResponse({'success': False, 'error': error_message})

        return JsonResponse({'success': False, 'error': 'Invalid request parameters for POST on detail page.'})

    context = {
        'case': case,
        'donation_settings': donation_settings,
        'promptpay_id_display': promptpay_id_for_template
    }
    return render(request, 'myapp/donate_detail.html', context)

def donation_thank_you_view(request):
    return render(request, 'myapp/donation_thank_you.htm')

def about_us(request):
    about = AboutContent.objects.first()
    stats = PetStatistics.objects.first()
    contact = ContactInfo.objects.first()
    blog_posts = BlogPost.objects.all().order_by('-created_at')[:4] # Get latest 4 posts
    context = {
        'about': about,
        'stats': stats,
        'contact': contact,
        'blog_posts': blog_posts,
    }
    return render(request, 'myapp/about.html', context)

def blog_detail(request, blog_id=None, slug=None):
    # This view is currently just returning an HttpResponse.
    # It would typically render a template with the blog post details.
    if blog_id:
        blog = get_object_or_404(BlogPost, id=blog_id)
    elif slug:
        blog = get_object_or_404(BlogPost, slug=slug)
    else:
        # This should ideally not happen if URLs are set up correctly.
        # Maybe redirect to a blog list page or raise a 404.
        raise Http404("Blog post not found.")
    # Example: return render(request, 'myapp/blog_detail_template.html', {'blog': blog})
    return HttpResponse(f"Blog Detail for: {blog.title} (ID: {blog.id}, Slug: {blog.slug})")

@login_required
@require_POST
def toggle_favorite(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    favorite, created = UserFavorite.objects.get_or_create(user=request.user, pet=pet)
    is_favorite = True # Assume it's now a favorite
    if not created: # If it already existed, it means we are removing it
        favorite.delete()
        is_favorite = False
    # favorite_count is not directly used in the client-side JS you provided for this specific action,
    # but it's good to return if you plan to update a global counter.
    favorite_count = UserFavorite.objects.filter(user=request.user).count()
    return JsonResponse({
        'is_favorite': is_favorite, # True if added/kept, False if removed
        'pet_id': pet_id,
        'favorite_count': favorite_count # Current total favorites for the user
    })

@login_required
@require_POST # Expects POST request with JSON body
def check_favorites(request):
    try:
        data = json.loads(request.body.decode('utf-8')) # Ensure request body is decoded
        pet_ids_str = data.get('pet_ids', [])
        if not isinstance(pet_ids_str, list):
            return JsonResponse({'error': 'pet_ids must be a list'}, status=400)
        # Convert pet_ids to integers, handling potential non-integer strings
        pet_ids_int = []
        for pid_str in pet_ids_str:
            try:
                pet_ids_int.append(int(pid_str))
            except ValueError:
                # Optionally log or ignore non-integer IDs
                pass
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e: # Catch other potential errors during parsing
        return JsonResponse({'error': f'Error processing request: {str(e)}'}, status=400)


    user_favorites_pet_ids = set(UserFavorite.objects.filter(
        user=request.user,
        pet_id__in=pet_ids_int
    ).values_list('pet_id', flat=True)) # Use set for efficient lookup

    favorites_status = {str(pid_int): (pid_int in user_favorites_pet_ids) for pid_int in pet_ids_int}
    return JsonResponse({'favorites': favorites_status})

@login_required
def favorites_view(request):
    # Get pets that the current user has favorited, ordered by when they were favorited
    favorite_pets = Pet.objects.filter(userfavorite__user=request.user).order_by('-userfavorite__created_at').prefetch_related('additional_images')
    return render(request, 'myapp/favorites.html', {'favorite_pets': favorite_pets})


@login_required
def adoption_form_view(request):
    if request.method == 'POST':
        # Create a new application instance
        application = AdoptionApplication()
        application.first_name = request.POST.get('first_name', '').strip()
        application.last_name = request.POST.get('last_name', '').strip()
        application.address = request.POST.get('address', '').strip()
        application.subdistrict = request.POST.get('subdistrict', '').strip()
        application.district = request.POST.get('district', '').strip()
        application.province = request.POST.get('province', '').strip()
        application.postal_code = request.POST.get('postal_code', '').strip()
        application.phone_number = request.POST.get('phone_number', '').strip()
        # Use authenticated user's email if available, otherwise from form (though should be auth user)
        application.email = request.POST.get('email', request.user.email if request.user.is_authenticated else '').strip()

        application.household = request.POST.get('household', '')
        application.other_pets = request.POST.get('other_pets', '')
        application.property_description = request.POST.get('property_description', '')
        application.job_working_hours = request.POST.get('job_working_hours', '')
        application.motivation = request.POST.get('motivation', '')

        interview_datetime_str = request.POST.get('interview_datetime', '')
        if interview_datetime_str:
            try:
                # Assuming your datetime-local input sends in "YYYY-MM-DDTHH:MM" format
                application.interview_datetime = datetime.strptime(interview_datetime_str.replace("T", " "), '%Y-%m-%d %H:%M')
            except ValueError:
                application.interview_datetime = None # Or handle error, e.g., messages.error
                messages.error(request, "รูปแบบวันและเวลานัดสัมภาษณ์ไม่ถูกต้อง กรุณาใช้รูปแบบ YYYY-MM-DD HH:MM.") # Notify user
        else:
            application.interview_datetime = None

        # Save the application first to get an ID
        application.save()

        # Handle selected pets
        selected_pet_ids_str = request.POST.get('selected_pet_ids', '') # This comes from a hidden input
        pet_ids_list_for_application = []
        if selected_pet_ids_str:
            try:
                pet_ids_list_for_application = [int(id_str.strip()) for id_str in selected_pet_ids_str.split(',') if id_str.strip().isdigit()]
                selected_pets_for_save = Pet.objects.filter(id__in=pet_ids_list_for_application, is_adopted=False) # Ensure pets are not already adopted
                if selected_pets_for_save.exists():
                    application.pets.set(selected_pets_for_save) # Use .set() for ManyToMany relationships
                else:
                    # Handle case where selected pets are not valid (e.g., already adopted or don't exist)
                    messages.warning(request, "สัตว์เลี้ยงบางตัวที่คุณเลือกอาจไม่พร้อมสำหรับการรับอุปการะอีกต่อไป")
            except ValueError:
                messages.error(request, "มีข้อผิดพลาดในการประมวลผล ID สัตว์เลี้ยงที่เลือก")
                pass # Or handle error more explicitly

        # Remove selected pets from user's favorites if authenticated
        if request.user.is_authenticated and pet_ids_list_for_application:
            UserFavorite.objects.filter(user=request.user, pet_id__in=pet_ids_list_for_application).delete()

        messages.success(request, "ส่งใบคำขอรับเลี้ยงสำเร็จแล้ว! เจ้าหน้าที่จะติดต่อกลับเร็วๆ นี้")
        return redirect(reverse('adoption_thank_you')) # Redirect to a thank you page

    else: # GET request
        selected_pet_ids_str = request.GET.get('pets', '') # Get pet IDs from query parameters
        selected_pets_for_display = []
        hidden_pet_ids_value = '' # For the hidden input in the form

        if selected_pet_ids_str:
            try:
                pet_ids_list = [int(id_str.strip()) for id_str in selected_pet_ids_str.split(',') if id_str.strip().isdigit()]
                # Fetch only pets that are not yet adopted
                selected_pets_for_display = Pet.objects.filter(id__in=pet_ids_list, is_adopted=False)
                hidden_pet_ids_value = ",".join(map(str, [pet.id for pet in selected_pets_for_display])) # Only include valid pet IDs
                if len(selected_pets_for_display) != len(pet_ids_list):
                    messages.warning(request, "สัตว์เลี้ยงบางตัวที่คุณเลือกอาจไม่พร้อมสำหรับการรับอุปการะแล้ว")
            except ValueError:
                messages.error(request, "ID สัตว์เลี้ยงที่ส่งมาไม่ถูกต้อง")
                pass # Or redirect to catalog with an error

        # Pre-fill form with user data if authenticated
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['first_name'] = request.user.first_name
            initial_data['last_name'] = request.user.last_name
            initial_data['email'] = request.user.email
            # You might have a UserProfile model to store phone number
            # if hasattr(request.user, 'userprofile') and request.user.userprofile.phone_number:
            # initial_data['phone_number'] = request.user.userprofile.phone_number

        context = {
            'selected_pets': selected_pets_for_display,
            'selected_pet_ids_for_form': hidden_pet_ids_value,
            'initial_data': initial_data, # Pass initial data to the template
        }
        return render(request, 'myapp/adoption_form.html', context)


def adoption_thank_you_view(request):
    return render(request, 'myapp/adoption_thank_you.html')


# AJAX view to get pet details for modal display
def get_pet_detail_ajax(request, pet_id):
    try:
        pet = Pet.objects.prefetch_related('additional_images').get(pk=pet_id)
        is_favorite = False
        if request.user.is_authenticated:
            is_favorite = UserFavorite.objects.filter(user=request.user, pet=pet).exists()

        additional_images_data = [{'url': img.image.url, 'caption': img.caption or ""} for img in pet.additional_images.all() if img.image]

        pet_data = {
            'id': pet.id,
            'name': pet.name,
            'breed': pet.breed,
            'gender_display': pet.get_gender_display(), # Use the display name for choices
            'age': pet.age, # Assuming age is stored as a string or number
            'vaccinated': pet.vaccinated,
            'disability': pet.disability if pet.disability else "-",
            'personality': pet.personality if pet.personality else "-",
            'detail': pet.detail if pet.detail else "-",
            'story': pet.story if pet.story else "เรื่องราวของน้องยังไม่ได้ถูกบันทึกไว้...",
            'photo_url': pet.photo.url if pet.photo else None, # Handle cases where photo might be missing
            'is_favorite_by_current_user': is_favorite,
            'additional_images': additional_images_data
        }
        return JsonResponse({'success': True, 'pet': pet_data})
    except Pet.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Pet not found.'}, status=404)
    except Exception as e:
        # Log the error for debugging
        print(f"Error in get_pet_detail_ajax for pet_id {pet_id}: {str(e)}")
        return JsonResponse({'success': False, 'error': 'An unexpected error occurred.'}, status=500)


@login_required
def chat_view(request):
    # For simplicity, this view just renders the chat page.
    # Real implementation would involve fetching conversations, messages, etc.
    # Or handling WebSocket connections if using Django Channels directly in view (less common).
    return render(request, 'myapp/chat.html')

@login_required
def cancel_adoption_application_view(request, application_id):
    application = get_object_or_404(AdoptionApplication, id=application_id)

    # Ensure the logged-in user is the owner of the application
    if application.email != request.user.email: # Or link to request.user directly if application stores user FK
        messages.error(request, "คุณไม่มีสิทธิ์ยกเลิกคำขอนี้")
        return redirect('my_adoption_applications')

    # Check if the application is in a cancelable state
    if application.status in [AdoptionApplication.STATUS_PENDING, AdoptionApplication.STATUS_UNDER_REVIEW]:
        if request.method == 'POST':
            application.status = AdoptionApplication.STATUS_CANCELED
            application.save()
            messages.success(request, f"คำขอรับเลี้ยงหมายเลข APP-{application.id:05d} ได้ถูกยกเลิกแล้ว")
            return redirect('my_adoption_applications')
        else:
            # For GET requests, you might want to show a confirmation page
            # or simply redirect if direct cancellation via GET is not supported/intended.
            # The current template form submits via POST, so this GET path might not be hit often
            # for cancellation itself, but could be reached if someone types the URL.
            messages.info(request, "โปรดยืนยันการยกเลิกผ่านปุ่มในหน้าสถานะ") # Or render a confirmation template
            return redirect('my_adoption_applications') # Redirect back
    else:
        messages.warning(request, f"ไม่สามารถยกเลิกคำขอนี้ได้ เนื่องจากสถานะปัจจุบันคือ '{application.get_status_display()}'")
        return redirect('my_adoption_applications')
    
@login_required
def notifications_view(request): # เปลี่ยนชื่อ view function
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()

    # ตัวอย่าง: หากผู้ใช้คลิกที่การแจ้งเตือน สามารถส่ง parameter เพื่อ mark as read
    notification_id_to_read = request.GET.get('read_id')
    if notification_id_to_read:
        try:
            notif = Notification.objects.get(id=notification_id_to_read, recipient=request.user)
            notif.is_read = True
            notif.save()
            if notif.link:
                return redirect(notif.link) # Redirect ไปยังลิงก์ของการแจ้งเตือนนั้น
            else:
                return redirect('notifications_list') # Redirect กลับมาหน้า notifications
        except Notification.DoesNotExist:
            pass # หรือจัดการ error

    # Mark all as read (ถ้าต้องการปุ่ม "Mark all as read")
    if request.GET.get('mark_all_read') == 'true':
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return redirect('notifications_list')


    context = {
        'notifications_list': notifications, # ส่ง list ของ notifications ไปยัง template
        'unread_notifications_count': unread_count, # ส่งจำนวนที่ยังไม่อ่าน
        'page_title': 'Notifications'
    }
    return render(request, 'myapp/notifications_list.html', context) # เปลี่ยนชื่อ template
