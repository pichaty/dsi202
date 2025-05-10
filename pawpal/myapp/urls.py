from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),  # FBV
    path('pets/<int:pk>/', views.PetDetailView.as_view(), name='pet_detail'),  # CBV Detail
    path('adopt/', views.adopt_catalog, name='adopt_catalog'),
    path('donate/', views.donate, name='donate'),
    # path('donate/<int:donation_id>/', views.donate_detail, name='donate_detail'), # มีบรรทัดซ้ำด้านล่าง
    path('about/', views.about_us, name='about'),
    # path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'), # พิจารณาว่าจะใช้ blog_id หรือ slug
    path('toggle-favorite/<int:pet_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('check-favorites/', views.check_favorites, name='check_favorites'),
    path('favorites/', views.favorites_view, name='favorites'),
    # path('pets/<int:pet_id>/favorite/', views.toggle_favorite_pet, name='toggle_favorite_pet'), # พิจารณาว่าซ้ำซ้อนกับ toggle_favorite หรือไม่
     path('adopt/apply/', views.adoption_form_view, name='adoption_form'), # URL สำหรับหน้าฟอร์ม
    path('adopt/thank-you/', views.adoption_thank_you_view, name='adoption_thank_you'), # URL สำหรับหน้าขอบคุณ
    path('donate/', views.donate, name='donate'),
    path('donate/<int:pk>/', views.donate_detail, name='donate_detail'), # ใช้บรรทัดนี้สำหรับ donate detail
    path('donate/<int:pk>/', views.donate_detail, name='donate_detail'),
    path('donate/thank-you/', views.donation_thank_you_view, name='donation_thank_you'),
     path('ajax/get-pet-detail/<int:pet_id>/', views.get_pet_detail_ajax, name='ajax_get_pet_detail'),
    # เพิ่มบรรทัดนี้เพื่อสร้าง URL pattern ชื่อ 'process_donation'
    # สามารถเลือก URL path ที่เหมาะสมได้ เช่น 'process-donation/' หรือ 'donate/process/'
    # path('process-donation/', views.process_donation_view, name='process_donation'),
]