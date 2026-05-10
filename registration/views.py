from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models, IntegrityError
from django.urls import reverse
from course.models import Course
from .models import Student, Certificate
from .forms import StudentRegistrationForm, UserLookupForm


def register_course(request, course_id=None):
    """Course registration page with pre-selected course"""
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        
        # Check if form is valid
        if form.is_valid():
            try:
                student = form.save()
                messages.success(
                    request, 
                    f'Registration successful! Your Registration Number is: {student.registration_number}'
                )
                return redirect('registration:registration_success', reg_number=student.registration_number)
            except IntegrityError as e:
                # Handle database integrity error
                if 'UNIQUE constraint failed' in str(e):
                    messages.error(
                        request, 
                        'You have already registered for this course. Please use a different email or mobile number.'
                    )
                else:
                    messages.error(request, f'Registration failed. Please try again.')
        else:
            # Display all form errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    
    else:
        initial = {}
        if course_id:
            course = get_object_or_404(Course, id=course_id, is_active=True)
            if not course.is_available_for_registration():
                messages.error(request, f'Sorry, {course.course_name} is no longer available for registration.')
                return redirect('public:courses')
            initial['course_enrolled'] = course
        
        form = StudentRegistrationForm(initial=initial)
    
    # Get related courses for suggestions
    related_courses = []
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        related_courses = Course.objects.filter(
            is_active=True,
            course_status__in=['open', 'active']
        ).exclude(id=course_id)[:4]
    
    context = {
        'form': form,
        'course_readonly': course_id is not None,
        'pre_selected_course': get_object_or_404(Course, id=course_id) if course_id else None,
        'related_courses': related_courses,
    }
    return render(request, 'registration/register.html', context)


def registration_success(request, reg_number):
    """Registration success page"""
    student = get_object_or_404(Student, registration_number=reg_number)
    return render(request, 'registration/registration_success.html', {'student': student})


def user_profile(request):
    """User profile lookup page - no authentication required"""
    students = None
    lookup_done = False
    search_value = None
    search_type = None
    
    if request.method == 'POST':
        lookup_by = request.POST.get('lookup_by', 'email')
        email_id = request.POST.get('email_id', '').strip()
        mobile_number = request.POST.get('mobile_number', '').strip()
        
        if lookup_by == 'email' and email_id:
            students = Student.objects.filter(email_id__iexact=email_id).exclude(status='cancelled')
            lookup_done = True
            search_value = email_id
            search_type = 'email'
            if not students.exists():
                messages.info(request, f'No registrations found with email: {email_id}')
        elif lookup_by == 'mobile' and mobile_number:
            students = Student.objects.filter(mobile_number=mobile_number).exclude(status='cancelled')
            lookup_done = True
            search_value = mobile_number
            search_type = 'mobile'
            if not students.exists():
                messages.info(request, f'No registrations found with mobile number: {mobile_number}')
    
    context = {
        'students': students,
        'lookup_done': lookup_done,
        'search_value': search_value,
        'search_type': search_type,
    }
    return render(request, 'registration/user_profile.html', context)


def download_certificate(request, reg_number):
    try:
        student = Student.objects.get(registration_number=reg_number)
        if student.status != 'completed':
            messages.error(request, 'Certificate is only available for completed courses.')
            return redirect('registration:user_profile')
        
        certificate, created = Certificate.objects.get_or_create(student=student)
        
        return render(request, 'registration/certificate_view.html', {
            'student': student,
            'certificate': certificate
        })
    except Student.DoesNotExist:
        messages.error(request, 'Registration not found.')
        return redirect('registration:user_profile')


def verify_certificate(request, cert_number):
    """Public certificate verification"""
    certificate = get_object_or_404(Certificate, certificate_number=cert_number)
    return render(request, 'registration/verify_certificate.html', {'certificate': certificate})