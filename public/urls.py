from django.urls import path
from . import views

app_name = 'public'

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.courses, name='courses'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('centres/', views.centres, name='centres'),
    path('centre/<uuid:pk>/', views.centre_detail, name='centre_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]