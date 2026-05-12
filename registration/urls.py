from django.urls import path
from . import views

app_name = 'registration'

urlpatterns = [
    path('register/', views.register_course, name='register'),
    path('register/<uuid:course_id>/', views.register_course, name='register_with_course'),
    path('success/<path:reg_number>/', views.registration_success, name='registration_success'),
    path('my-profile/', views.user_profile, name='user_profile'),
    path('download-certificate/<path:reg_number>/', views.download_certificate, name='download_certificate'),
    path('verify/<str:cert_number>/', views.verify_certificate, name='verify_certificate'),
]