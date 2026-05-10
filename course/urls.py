from django.urls import path
from . import views

app_name = 'course'

urlpatterns = [
    # API endpoints
    path('api/get-all-centres/', views.get_all_centres, name='get_all_centres'),
    path('api/get-course-centres/', views.get_course_centres, name='get_course_centres'),
    
    # Admin URLs - Course Management
    path('admin/list/', views.course_list, name='course_list'),
    path('admin/create/', views.course_create, name='course_create'),
    path('admin/<uuid:pk>/edit/', views.course_edit, name='course_edit'),
    path('admin/<uuid:pk>/delete/', views.course_delete, name='course_delete'),
    
    # Admin URLs - Centre Management
    path('admin/centres/', views.centre_list, name='centre_list'),
    path('admin/centres/create/', views.centre_create, name='centre_create'),
    path('admin/centres/<uuid:pk>/edit/', views.centre_edit, name='centre_edit'),
    path('admin/centres/<uuid:pk>/delete/', views.centre_delete, name='centre_delete'),
]

