
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Pet
from django.shortcuts import render
from .models import Pet, DonationCase
from django.shortcuts import render, get_object_or_404
# myapp/views.py
from .models import BlogPost, AboutContent, PetStatistics, ContactInfo  # เปลี่ยนจาก Stats เป็น PetStatistics
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
from django.shortcuts import get_object_or_404, render
from .models import Pet, UserFavorite


#1. FBV: หน้า Home

def home(request):
    adopt_pets = Pet.objects.all()  # ไม่ slice
    donation_cases = DonationCase.objects.all()  # ไม่ slice
     
    return render(request, 'myapp/home.html', {
        'adopt_pets': adopt_pets,
        'donation_cases': donation_cases,
    })


def donate(request):
    """
    View for the donation page that displays donation options and active cases
    """
    # Get pets to display at the top 
    pets = Pet.objects.all()[:3]
    
    # Get donation cases
    donation_cases = DonationCase.objects.all().order_by('-id')[:2]
    
    context = {
        'pets': pets,
        'donation_cases': donation_cases,
    }
    
    return render(request, 'myapp/donate.html', context)


#3. CBV: Pet Detail
class PetDetailView(DetailView):
    model = Pet
    template_name = 'myapp/pet_detail.html'

    

def adopt_catalog(request):
     pets = Pet.objects.all()
     return render(request, 'myapp/adopt_catalog.html', {'pets': pets})

# myapp/views.py

from django.shortcuts import render

def donate(request):
    return render(request, 'myapp/donate.html')  # สร้าง template นี้ด้วย

# myapp/views.py

def donate_detail(request, pk):
    return HttpResponse(f"Donation detail page for donation #{pk}")


def about(request):
    return render(request, 'myapp/about.html')

from django.shortcuts import render
from .models import AboutContent, PetStatistics, BlogPost, ContactInfo

# myapp/views.py

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
    
    return JsonResponse({
        'is_favorite': is_favorite,
        'removed': removed,
        'pet_id': pet_id
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