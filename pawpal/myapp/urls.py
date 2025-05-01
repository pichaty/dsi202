from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # FBV
    path('pets/<int:pk>/', views.PetDetailView.as_view(), name='pet_detail'),  # CBV Detail
    path('adopt/', views.adopt_catalog, name='adopt_catalog'),
    path('donate/', views.donate, name='donate'),
    path('donate/<int:donation_id>/', views.donate_detail, name='donate_detail'),
    path('about/', views.about, name='about'),


]