from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .forms import LoginForm, CreateAdminForm, EditAdminForm, ChangePasswordForm, CustomPasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.urls import reverse

def is_admin(user):
    return user.is_authenticated and user.is_staff

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
    
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect(reverse('dashboard:index'))
        messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    
    return render(request, 'account/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('public:home')

@login_required
@user_passes_test(is_admin)
def create_admin(request):
    if request.method == 'POST':
        form = CreateAdminForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_staff = True
            user.save()
            messages.success(request, f'Admin user {user.username} created successfully!')
            return redirect('account:manage_admins')
    else:
        form = CreateAdminForm()
    
    return render(request, 'account/create_admin.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def manage_admins(request):
    """List all admin users"""
    admins = User.objects.filter(is_staff=True).exclude(id=request.user.id)
    
    search = request.GET.get('search')
    if search:
        admins = admins.filter(
            models.Q(username__icontains=search) |
            models.Q(first_name__icontains=search) |
            models.Q(last_name__icontains=search) |
            models.Q(email__icontains=search)
        )
    
    paginator = Paginator(admins, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'account/manage_admins.html', {'page_obj': page_obj})

@login_required
@user_passes_test(is_admin)
def edit_admin(request, user_id):
    """Edit admin user"""
    admin_user = get_object_or_404(User, id=user_id, is_staff=True)
    
    if request.method == 'POST':
        form = EditAdminForm(request.POST, instance=admin_user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Admin user {admin_user.username} updated successfully!')
            return redirect('account:manage_admins')
    else:
        form = EditAdminForm(instance=admin_user)
    
    return render(request, 'account/edit_admin.html', {'form': form, 'admin_user': admin_user})

@login_required
@user_passes_test(is_admin)
def change_admin_password(request, user_id):
    """Change admin user password"""
    admin_user = get_object_or_404(User, id=user_id, is_staff=True)
    
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            admin_user.set_password(new_password)
            admin_user.save()
            messages.success(request, f'Password for {admin_user.username} changed successfully!')
            return redirect('account:manage_admins')
    else:
        form = ChangePasswordForm()
    
    return render(request, 'account/change_password.html', {'form': form, 'admin_user': admin_user})

@login_required
@user_passes_test(is_admin)
def delete_admin(request, user_id):
    """Delete admin user"""
    admin_user = get_object_or_404(User, id=user_id, is_staff=True)
    
    if request.method == 'POST':
        username = admin_user.username
        admin_user.delete()
        messages.success(request, f'Admin user {username} deleted successfully!')
        return redirect('account:manage_admins')
    
    return render(request, 'account/delete_admin.html', {'admin_user': admin_user})

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'account/password_reset.html'
    success_url = '/account/login/'
    
    def form_valid(self, form):
        messages.success(self.request, 'Password reset email sent successfully!')
        return super().form_valid(form)