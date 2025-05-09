# ใน work/dsi202/pawpal/myapp/views.py

from django.http import HttpResponse,JsonResponse, Http404, HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.db.models import Q
import json
from .models import Pet, UserFavorite, BlogPost, AboutContent, PetStatistics, ContactInfo, DonationCase, AdoptionApplication # ตรวจสอบว่า import ครบ

from django.shortcuts import render, get_object_or_404, redirect
# myapp/views.py

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse # เพิ่ม import นี้สำหรับ redirect


#1. FBV: หน้า Home

def home(request):
    adopt_pets = Pet.objects.filter(is_adopted=False)
    donation_cases = DonationCase.objects.all()

    return render(request, 'myapp/home.html', {
        'adopt_pets': adopt_pets,
        'donation_cases': donation_cases,
    })

def donate(request):
    """
    View for the donation page that displays donation options and active cases
    """
    # Get pets to display at the top (ตาม screenshot เหมือนจะดึง Pet ปกติมาแสดง)
    # อาจจะต้องพิจารณาว่าจะแสดง Pet ทั่วไป หรือ Pet ที่มี DonationCase เกี่ยวข้อง
    # ในโค้ดเดิมดึง Pet.objects.all()[:3] ซึ่งดึง 3 ตัวแรก
    # ถ้าต้องการดึง Pet ที่มี DonationCase อาจจะต้องปรับ query
    pets_in_need_cases = DonationCase.objects.all() # ดึง DonationCase ทั้งหมด
    pets_for_gallery = [case.pet for case in pets_in_need_cases[:3]] # ดึง Pet จาก 3 เคสแรก

    # Get donation cases to display (อาจจะแสดงทั้งหมด หรือจำกัดจำนวนตามต้องการ)
    # ในโค้ดเดิมดึงมา 2 เคสแรก: DonationCase.objects.all().order_by('-id')[:2]
    # ถ้าต้องการแสดงทั้งหมด: donation_cases = DonationCase.objects.all().order_by('-id')
    donation_cases = DonationCase.objects.all().order_by('-id')


    context = {
        'pets': pets_for_gallery, # เปลี่ยนเป็น Pet ที่เกี่ยวข้องกับเคสบริจาค
        'donation_cases': donation_cases,
    }

    return render(request, 'myapp/donate.html', context)


#3. CBV: Pet Detail
class PetDetailView(DetailView):
    model = Pet
    template_name = 'myapp/pet_detail.html'


def adopt_catalog(request):
     # กรองเฉพาะสัตว์เลี้ยงที่ยังไม่ถูกรับเลี้ยง
     pets = Pet.objects.filter(is_adopted=False)
     return render(request, 'myapp/adopt_catalog.html', {'pets': pets})


def donate_detail(request, pk):
    """
    View for the donation case detail page
    """
    # ดึง DonationCase object หรือแสดง 404 ถ้าไม่พบ โดยใช้ pk ที่รับมา
    case = get_object_or_404(DonationCase, pk=pk)
    context = {
        'case': case
    }
    return render(request, 'myapp/donate_detail.html', context)


def about(request):
    return render(request, 'myapp/about.html')


def about_us(request):
    # เปลี่ยนจาก About เป็น AboutContent
    about = AboutContent.objects.first()
    stats = PetStatistics.objects.first()  # เปลี่ยนจาก Stats เป็น PetStatistics
    contact = ContactInfo.objects.first()  # เปลี่ยนจาก Contact เป็น ContactInfo
    blog_posts = BlogPost.objects.all().order_by('-created_at')[:4]

    context = {
        'about': about,
        'stats': stats,
        'contact': contact,
        'blog_posts': blog_posts,
    }

    return render(request, 'myapp/about.html', context)


def blog_detail(request, blog_id=None, slug=None):
    # ถ้าใช้ blog_id
    if blog_id:
        blog = get_object_or_404(BlogPost, id=blog_id)
    # หรือถ้าใช้ slug
    elif slug:
        blog = get_object_or_404(BlogPost, slug=slug)
    else:
        raise Http404("Blog post not found.") # กรณีไม่มีทั้ง blog_id และ slug

    context = {
        'blog': blog,
    }

    return render(request, 'myapp/blog_detail.html', context)

# Add these views to views.py

@login_required
def toggle_favorite(request, pet_id):
    """Toggle a pet's favorite status for the current user"""
    pet = get_object_or_404(Pet, id=pet_id)

    # Check if pet is already a favorite
    favorite, created = UserFavorite.objects.get_or_create(
        user=request.user,
        pet=pet
    )

    # If it wasn't created, it already existed, so delete it
    removed = False
    is_favorite = True
    if not created:
        favorite.delete()
        is_favorite = False
        removed = True

    # สามารถดึงจำนวน favorite ใหม่เพื่ออัปเดตที่ header ได้ที่นี่
    favorite_count = UserFavorite.objects.filter(user=request.user).count()

    return JsonResponse({
        'is_favorite': is_favorite,
        'removed': removed,
        'pet_id': pet_id,
        'favorite_count': favorite_count # ส่งจำนวน favorite กลับไปด้วย
    })

@login_required
@require_POST
def check_favorites(request):
    """Check if multiple pets are in user's favorites"""
    data = json.loads(request.body)
    pet_ids = data.get('pet_ids', [])

    # Get user's favorite pets
    user_favorites = UserFavorite.objects.filter(
        user=request.user,
        pet_id__in=pet_ids
    ).values_list('pet_id', flat=True)

    # Create a dictionary with pet_id as key and favorite status as value
    favorites = {str(pet_id): (int(pet_id) in user_favorites) for pet_id in pet_ids}

    return JsonResponse({'favorites': favorites})

@login_required
def favorites_view(request):
    """Display user's favorite pets"""
    favorite_pets = Pet.objects.filter(
        userfavorite__user=request.user
    ).order_by('-userfavorite__created_at')

    return render(request, 'myapp/favorites.html', {
        'favorite_pets': favorite_pets
    })

# myapp/views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Pet

@login_required
def toggle_favorite_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    user = request.user

    if user in pet.favorited_by.all():
        pet.favorited_by.remove(user)
        favorited = False
    else:
        pet.favorited_by.add(user)
        favorited = True

    return JsonResponse({'favorited': favorited})


# ใน work/dsi202/pawpal/myapp/views.py

from django.shortcuts import render, redirect, get_object_or_404
# ต้อง import โมเดล AdoptionApplication ที่สร้างในขั้นตอนที่ 1
from .models import Pet, AdoptionApplication
from django.contrib.auth.decorators import login_required
from django.urls import reverse # เพิ่ม import นี้สำหรับ redirect

@login_required # แนะนำให้จำกัดสิทธิ์เฉพาะผู้ใช้ที่ Login แล้ว
def adoption_form_view(request):
    if request.method == 'POST':
        # ดึงข้อมูลที่ผู้ใช้กรอกจากฟอร์ม
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        subdistrict = request.POST.get('subdistrict')
        district = request.POST.get('district')
        province = request.POST.get('province')
        postal_code = request.POST.get('postal_code')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        household = request.POST.get('household')
        other_pets = request.POST.get('other_pets')
        property_description = request.POST.get('property_description')
        job_working_hours = request.POST.get('job_working_hours')
        motivation = request.POST.get('motivation')

        # ดึง selected_pet_ids จาก hidden input (รับค่าได้หลายตัวเนื่องจากใช้ชื่อซ้ำกัน)
        selected_pet_ids_post = request.POST.getlist('selected_pet_ids')
        print(f"DEBUG: selected_pet_ids_post from form: {selected_pet_ids_post}") # Debug 1

        selected_pets_for_save = []
        if selected_pet_ids_post:
            pet_ids_str = selected_pet_ids_post[0] if selected_pet_ids_post else ''
            print(f"DEBUG: pet_ids_str extracted: {pet_ids_str}") # Debug 2
            try:
                # แยก id และแปลงเป็น int
                pet_ids_list_post = [int(id) for id in pet_ids_str.split(',') if id.isdigit()]
                print(f"DEBUG: pet_ids_list_post (parsed IDs): {pet_ids_list_post}") # Debug 3

                # ดึง Pet objects จาก ID ที่ได้
                selected_pets_for_save = Pet.objects.filter(id__in=pet_ids_list_post)
                print(f"DEBUG: selected_pets_for_save (QuerySet before saving): {selected_pets_for_save}") # Debug 4

            except Exception as e:
                print(f"DEBUG: Error during parsing or fetching pets: {e}") # Debug 5
                # จัดการข้อผิดพลาดตามความเหมาะสม เช่น แสดงข้อความ error ให้ผู้ใช้ทราบ

        # สร้าง instance ของโมเดล AdoptionApplication
        try:
            application = AdoptionApplication.objects.create(
                # user=request.user, # ยกเลิกคอมเมนต์บรรทัดนี้ถ้าใช้ระบบผู้ใช้
                first_name=request.POST.get('first_name'), # ใช้ request.POST.get() โดยตรง
                last_name=request.POST.get('last_name'),
                address=request.POST.get('address'),
                subdistrict=request.POST.get('subdistrict'),
                district=request.POST.get('district'),
                province=request.POST.get('province'),
                postal_code=request.POST.get('postal_code'),
                phone_number=request.POST.get('phone_number'),
                email=request.POST.get('email'),
                household=request.POST.get('household'),
                other_pets=request.POST.get('other_pets'),
                property_description=request.POST.get('property_description'),
                job_working_hours=request.POST.get('job_working_hours'),
                motivation=request.POST.get('motivation'),
            )
            print(f"DEBUG: AdoptionApplication created with ID: {application.pk}") # Debug 6
        except Exception as e:
            print(f"DEBUG: Error creating AdoptionApplication: {e}") # Debug 7
            # ควรมีการจัดการข้อผิดพลาดในการสร้าง object ด้วย


        # เพิ่มสัตว์เลี้ยงที่ถูกเลือกใน ManyToManyField
        if selected_pets_for_save.exists(): # ตรวจสอบว่ามีสัตว์เลี้ยงใน QuerySet ก่อนเรียก set()
            try:
                application.pets.set(selected_pets_for_save)
                print("DEBUG: application.pets.set() called successfully.") # Debug 8
            except Exception as e:
                print(f"DEBUG: Error setting pets ManyToMany: {e}") # Debug 9
        else:
            print("DEBUG: selected_pets_for_save is empty. Skipping application.pets.set().") # Debug 10


        # Redirect ไปยังหน้าขอบคุณ
        return redirect(reverse('adoption_thank_you'))

    else: # สำหรับ GET request (แสดงฟอร์ม)
        # ... (ส่วนของ GET request เหมือนเดิม) ...
        selected_pet_ids = request.GET.get('pets')
        selected_pets = []

        if selected_pet_ids:
             # กรองเฉพาะ id ที่เป็นตัวเลข และดึง Pet object
            pet_ids_list = [int(id) for id in selected_pet_ids.split(',') if id.isdigit()]
            # ดึงข้อมูล Pet objects จากฐานข้อมูล
            selected_pets = Pet.objects.filter(id__in=pet_ids_list)

        context = {
            'selected_pets': selected_pets
        }
        return render(request, 'myapp/adoption_form.html', context)


# View สำหรับแสดงหน้าขอบคุณ
def adoption_thank_you_view(request):
    return render(request, 'myapp/adoption_thank_you.html')
from django.views.decorators.csrf import csrf_exempt # เพิ่ม import นี้เพื่อยกเว้น CSRF token ชั่วคราวสำหรับการทดสอบ (ควรแก้ไขในภายหลัง)
from django.http import HttpResponse

@csrf_exempt # ยกเว้น CSRF token สำหรับ view นี้ชั่วคราว
def process_donation_view(request):
    if request.method == 'POST':
        # ในที่นี้เราจะยังไม่เขียน logic การประมวลผลการบริจาคจริงจัง
        # แค่แสดงข้อความยืนยันว่าได้รับข้อมูลแล้ว
        donation_amount = request.POST.get('donationAmount')
        payment_method = request.POST.get('paymentMethod')
        # สามารถดึงข้อมูลอื่นๆ ที่ส่งมาจากฟอร์มได้ที่นี่

        print(f"Received donation of {donation_amount} via {payment_method}")

        # คุณอาจจะ redirect ไปหน้าขอบคุณ หรือแสดงข้อความยืนยัน
        return HttpResponse("Thank you for your donation (Processing logic to be implemented).")
    else:
        # ถ้าไม่ใช่ method POST อาจจะ redirect กลับไปหน้าบริจาค หรือแสดง error
        return HttpResponse("Method not allowed.", status=405)