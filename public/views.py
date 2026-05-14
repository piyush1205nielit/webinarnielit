from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db import models
from course.models import Course, Centre
from registration.models import Student
from django.utils import timezone
from public.models import Announcement, CarouselImage
from django.http import HttpResponse, Http404
from django.conf import settings
from django.views.static import serve
import os

def home(request):
    """Public home page with hero section and featured content"""
    featured_courses = Course.objects.filter(is_active=True, is_featured=True)[:4]
    upcoming_courses = Course.objects.filter(
        is_active=True, 
        course_status__in=['open', 'active']
    )[:4]
    popular_courses = Course.objects.filter(is_active=True).order_by('-students__count')[:4]
    
    centres = Centre.objects.all()[:6]
    total_students = Student.objects.count()
    total_courses = Course.objects.count()
    total_centres = Centre.objects.count()

    # Get active announcements (not expired)
    announcements = Announcement.objects.filter(is_active=True).exclude(expires_at__lt=timezone.now())[:5]
    
    # Get active carousel images ordered by order field
    carousel_images = CarouselImage.objects.filter(is_active=True)
    
    context = {
        'featured_courses': featured_courses,
        'upcoming_courses': upcoming_courses,
        'centres': centres,
        'total_students': total_students,
        'total_courses': total_courses,
        'total_centres': total_centres,
        'announcements': announcements,
        'carousel_images': carousel_images,
    }
    return render(request, 'public/home.html', context)

def courses(request):
    """Public courses listing page"""
    courses_list = Course.objects.filter(is_active=True, course_status__in=['open', 'active'])
    
    # Filters
    search = request.GET.get('search')
    mode = request.GET.get('mode')
    course_type = request.GET.get('type')
    
    if search:
        courses_list = courses_list.filter(
            models.Q(course_name__icontains=search) | 
            models.Q(course_desc__icontains=search)
        )
    if mode:
        courses_list = courses_list.filter(mode=mode)
    if course_type:
        courses_list = courses_list.filter(course_status=course_type)
    
    paginator = Paginator(courses_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'modes': Course.MODE_CHOICES,
        'status_choices': Course.STATUS_CHOICES,
    }
    return render(request, 'public/courses.html', context)

def course_detail(request, slug):
    """Public course detail page"""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    related_courses = Course.objects.filter(
        is_active=True, 
        mode=course.mode
    ).exclude(id=course.id)[:3]
    
    context = {
        'course': course,
        'related_courses': related_courses,
        'now': timezone.now().date(),
    }
    return render(request, 'public/course_detail.html', context)

def centres(request):
    """Public centres listing page"""
    centres_list = Centre.objects.all()
    
    search = request.GET.get('search')
    if search:
        centres_list = centres_list.filter(
            models.Q(centre_name__icontains=search) |
            models.Q(centre_address__icontains=search)
        )
    
    paginator = Paginator(centres_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'public/centres.html', {'page_obj': page_obj})

def centre_detail(request, pk):
    """Public centre detail page"""
    centre = get_object_or_404(Centre, pk=pk)
    courses_at_centre = Course.objects.filter(
        is_active=True,
        students__preferred_centre=centre
    ).distinct()[:6]
    
    return render(request, 'public/centre_detail.html', {
        'centre': centre,
        'courses_at_centre': courses_at_centre
    })

def about(request):
    """About us page"""
    return render(request, 'public/about.html')

def contact(request):
    """Contact page"""
    return render(request, 'public/contact.html')


def serve_media(request, path):
    """Serve media files in production"""
    if settings.DEBUG:
        return serve(request, path, document_root=settings.MEDIA_ROOT)
    
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return HttpResponse(f.read(), content_type='image/jpeg')
    raise Http404("File not found")

def announcements(request):
    """Announcements page"""
    from public.models import Announcement
    
    # Get all announcements, ordered by creation date (newest first)
    announcements_list = Announcement.objects.filter(is_active=True).order_by('-created_at')
    
    context = {'announcements': announcements_list,}
    
    return render(request, 'public/announcements.html', context)