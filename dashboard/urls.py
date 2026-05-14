from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('students/', views.students_list, name='students_list'),
    path('students/<uuid:pk>/', views.student_detail, name='student_detail'),
    path('approve/', views.approve_certificate, name='approve_certificate'),
    path('approve-bulk/', views.approve_bulk, name='approve_bulk'),
    path('update-status-bulk/', views.update_status_bulk, name='update_status_bulk'),
    path('delete-bulk/', views.delete_bulk, name='delete_bulk'),
    path('update-status/', views.update_status, name='update_status'),
    path('reports/', views.reports, name='reports'),
    path('export-excel/', views.export_students_excel, name='export_excel'),
    path('export-pdf/', views.export_students_pdf, name='export_pdf'),

    # Announcement URLs
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/create/', views.announcement_create, name='announcement_create'),
    path('announcements/<uuid:pk>/edit/', views.announcement_edit, name='announcement_edit'),
    path('announcements/<uuid:pk>/delete/', views.announcement_delete, name='announcement_delete'),
    path('announcements/reorder/', views.announcement_reorder, name='announcement_reorder'),
    
    # Carousel URLs
    path('carousel/', views.carousel_list, name='carousel_list'),
    path('carousel/create/', views.carousel_create, name='carousel_create'),
    path('carousel/<uuid:pk>/edit/', views.carousel_edit, name='carousel_edit'),
    path('carousel/<uuid:pk>/delete/', views.carousel_delete, name='carousel_delete'),
    path('carousel/reorder/', views.carousel_reorder, name='carousel_reorder'),

]