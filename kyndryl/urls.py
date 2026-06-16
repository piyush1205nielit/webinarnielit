from django.urls import path
from . import views

app_name = 'kyndryl'

urlpatterns = [
    path('register/', views.RegistrationCreateView.as_view(), name='register'),
    path('register/success/<str:registration_number>/', views.RegistrationSuccessView.as_view(), name='register_success'),
    path('profile/<uuid:pk>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/<uuid:pk>/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('registrations/', views.RegistrationListView.as_view(), name='registration_list'),
]