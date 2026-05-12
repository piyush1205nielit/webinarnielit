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
]