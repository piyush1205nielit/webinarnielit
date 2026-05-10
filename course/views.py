from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db import models
from django.http import JsonResponse
from .models import Course, Centre
from .forms import CourseForm, CentreForm

def is_admin(user):
    return user.is_authenticated and user.is_staff

# API Views
def get_all_centres(request):
    """API endpoint to get all centres for the select all feature"""
    centres = Centre.objects.all().values('id', 'centre_name', 'centre_address')
    return JsonResponse({
        'centres': list(centres)
    })

def get_course_centres(request):
    """API endpoint to get centres for a course"""
    course_id = request.GET.get('course_id')
    if course_id:
        try:
            course = Course.objects.get(id=course_id)
            if course.mode == 'online':
                centres = Centre.objects.all().values('id', 'centre_name', 'centre_address')
                return JsonResponse({
                    'mode': 'online',
                    'centres': list(centres)
                })
            else:
                centres = course.available_centres.all().values('id', 'centre_name', 'centre_address')
                return JsonResponse({
                    'mode': 'offline',
                    'centres': list(centres)
                })
        except Course.DoesNotExist:
            return JsonResponse({'mode': 'unknown', 'centres': []})
    return JsonResponse({'mode': 'unknown', 'centres': []})


# Admin Views - Course Management
@user_passes_test(is_admin)
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'course/course_list_admin.html', {'courses': courses})

@user_passes_test(is_admin)
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course created successfully!')
            return redirect('course:course_list')
    else:
        form = CourseForm()
    return render(request, 'course/course_form.html', {'form': form, 'title': 'Create Course'})

@user_passes_test(is_admin)
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('course:course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'course/course_form.html', {'form': form, 'title': 'Edit Course'})

@user_passes_test(is_admin)
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('course:course_list')
    return render(request, 'course/course_confirm_delete.html', {'object': course})

# Admin Views - Centre Management
@user_passes_test(is_admin)
def centre_list(request):
    centres = Centre.objects.all()
    return render(request, 'course/centre_list.html', {'centres': centres})

@user_passes_test(is_admin)
def centre_create(request):
    if request.method == 'POST':
        form = CentreForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Centre created successfully!')
            return redirect('course:centre_list')
    else:
        form = CentreForm()
    return render(request, 'course/centre_form.html', {'form': form, 'title': 'Create Centre'})

@user_passes_test(is_admin)
def centre_edit(request, pk):
    centre = get_object_or_404(Centre, pk=pk)
    if request.method == 'POST':
        form = CentreForm(request.POST, instance=centre)
        if form.is_valid():
            form.save()
            messages.success(request, 'Centre updated successfully!')
            return redirect('course:centre_list')
    else:
        form = CentreForm(instance=centre)
    return render(request, 'course/centre_form.html', {'form': form, 'title': 'Edit Centre'})

@user_passes_test(is_admin)
def centre_delete(request, pk):
    centre = get_object_or_404(Centre, pk=pk)
    if request.method == 'POST':
        centre.delete()
        messages.success(request, 'Centre deleted successfully!')
        return redirect('course:centre_list')
    return render(request, 'course/centre_confirm_delete.html', {'object': centre})