from django.urls import path
from . import views

app_name = 'public'

urlpatterns = [
    path('0000', views.home, name='home'),
    path('', views.maintenance_page, name='maintenance_page'),
    path('1122', views.home_page_2, name='home2'),
    path('courses/', views.courses, name='courses'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('centres/', views.centres, name='centres'),
    path('centre/<uuid:pk>/', views.centre_detail, name='centre_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('announcements/', views.announcements, name='announcements'),
]