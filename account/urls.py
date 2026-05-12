from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'account'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create-admin/', views.create_admin, name='create_admin'),
    path('manage-admins/', views.manage_admins, name='manage_admins'),
    path('edit-admin/<int:user_id>/', views.edit_admin, name='edit_admin'),
    path('change-password/<int:user_id>/', views.change_admin_password, name='change_password'),
    path('delete-admin/<int:user_id>/', views.delete_admin, name='delete_admin'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]