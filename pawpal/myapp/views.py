
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Pet
from django.shortcuts import render
from .models import Pet, DonationCase
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
