from django.urls import path
from . import views

app_name = 'certificate'

urlpatterns = [
    # Student URLs
    path('view/<str:reg_number>/', views.view_certificate, name='view_certificate'),
    path('verify/<str:cert_number>/', views.verify_certificate, name='verify_certificate'),

    path('qr/<str:cert_number>/', views.certificate_qr_code, name='certificate_qr_code'), 
    
    # Admin URLs
    path('admin/designs/', views.design_list, name='design_list'),
    path('admin/designs/create/', views.design_create, name='design_create'),
    path('admin/designs/<uuid:pk>/edit/', views.design_edit, name='design_edit'),
    path('admin/designs/<uuid:pk>/preview/', views.design_preview, name='design_preview'),
    path('admin/designs/<uuid:pk>/delete/', views.design_delete, name='design_delete'),
    path('admin/issue/<uuid:student_id>/', views.issue_certificate, name='issue_certificate'),
    path('admin/issued/', views.issued_certificates_list, name='issued_list'),
]