# work/dsi202/pawpal/myapp/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('pets/<int:pk>/', views.PetDetailView.as_view(), name='pet_detail'),
    path('adopt/', views.adopt_catalog, name='adopt_catalog'),
    path('adopt/apply/', views.adoption_form_view, name='adoption_form'),
    path('adopt/thank-you/', views.adoption_thank_you_view, name='adoption_thank_you'),
    path('donate/', views.donate, name='donate'),
    path('donate/<int:pk>/', views.donate_detail, name='donate_detail'),
    path('donate/thank-you/', views.donation_thank_you_view, name='donation_thank_you'),
    path('about/', views.about_us, name='about'),
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail_by_id'), # ให้ชื่อไม่ซ้ำ
    path('blog/slug/<slug:slug>/', views.blog_detail, name='blog_detail_by_slug'), # ให้ชื่อไม่ซ้ำ

    path('toggle-favorite/<int:pet_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('check-favorites/', views.check_favorites, name='check_favorites'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('ajax/get-pet-detail/<int:pet_id>/', views.get_pet_detail_ajax, name='ajax_get_pet_detail'),

    # New URLs for profile dropdown
    path('accounts/profile/', views.user_profile_view, name='user_profile'),
    path('accounts/my-adoptions/', views.my_adoption_applications_view, name='my_adoption_applications'),
    path('accounts/my-pets/', views.my_adopted_pets_view, name='my_adopted_pets'),
    path('accounts/my-donations/', views.my_donations_view, name='my_donations'),
    path('accounts/settings/', views.account_settings_view, name='account_settings'),
    # path('notifications/', views.notifications_placeholder_view, name='notifications_placeholder'), # Placeholder
     path('chat/', views.chat_view, name='chat_page'), # <--- เพิ่ม URL สำหรับหน้าแชท
      path('accounts/my-adoptions/cancel/<int:application_id>/', views.cancel_adoption_application_view, name='cancel_adoption_application'),
      path('accounts/my-adoptions/history/', views.adoption_application_history_view, name='adoption_application_history'),
       path('notifications/', views.notifications_view, name='notifications_list'),
    path('quiz/', views.quiz_start, name='quiz_start'),
    path('quiz/question/<int:question_id>/', views.quiz_question, name='quiz_question'),
    path('quiz/results/', views.quiz_results, name='quiz_results'),
     path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
]