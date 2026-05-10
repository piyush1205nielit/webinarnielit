import uuid
from django.db import models
from django.utils.text import slugify
from django.utils import timezone

def course_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return f'courses/images/{instance.course_name[:20]}_{instance.id}.{ext}'

def course_syllabus_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return f'courses/syllabus/{instance.course_name[:20]}_{instance.id}.{ext}'

class Centre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    centre_name = models.CharField(max_length=200)
    centre_address = models.TextField()
    centre_contact = models.CharField(max_length=15)
    centre_email = models.EmailField()
    centre_desc = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.centre_name
    
    class Meta:
        ordering = ['centre_name']


class Course(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('ongoing', 'Ongoing'),
        ('open', 'Open for Registration'),
        ('closed', 'Registration Closed'),
        ('completed', 'Completed'),
    ]

    MODE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('hybrid', 'Hybrid'),
    ]
    
    COURSE_TYPE_CHOICES = [
        ('regular', 'Regular Course (Multiple Days/Weeks)'),
        ('workshop', 'Single Day Workshop/Event'),
        ('Online Bootcamp', 'Online Bootcamp'),
        ('seminar', 'Seminar'),
        ('webinar', 'Webinar'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_name = models.CharField(max_length=200)
    course_desc = models.TextField()
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    course_duration = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., 3 months, 6 weeks (for regular courses)")
    
    # New field for course type
    course_type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES, default='regular')
    course_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    course_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    is_free = models.BooleanField(default=False, null=True, blank=True)

    # Date fields - all optional
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    event_date = models.DateField(null=True, blank=True, help_text="For single day events/workshops")
    registration_deadline = models.DateField(null=True, blank=True)

    image = models.ImageField(upload_to=course_image_upload_path, blank=True, null=True)
    syllabus_file = models.FileField(upload_to=course_syllabus_upload_path, blank=True, null=True)
    
    modules_info = models.TextField(blank=True, null=True, help_text="Enter module details, topics covered, syllabus structure")
    prerequisites = models.TextField(blank=True, null=True)
    learning_outcomes = models.TextField(blank=True, null=True)

    mode = models.CharField(max_length=20, null=True, blank=True, choices=MODE_CHOICES, default='offline')
    max_seats = models.PositiveIntegerField(default=30, null=True, blank=True)

    # Many-to-Many relationship with centres
    available_centres = models.ManyToManyField(Centre, blank=True, related_name='available_courses', 
                                                help_text="Select centres where this course is offered")

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.course_name)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if self.course_fees == 0 or self.course_fees is None:
            self.is_free = True
        else:
            self.is_free = False
        super().save(*args, **kwargs)
    
    @property
    def display_fees(self):
        if self.is_free or not self.course_fees or self.course_fees == 0:
            return "Free"
        return f"₹{self.course_fees:,.2f}"
    
    def get_seats_available(self):
        from registration.models import Student
        if not self.max_seats:
            return 999
        registered_count = Student.objects.filter(
            course_enrolled=self, 
            status__in=['pending', 'confirmed']
        ).count()
        return self.max_seats - registered_count
    
    def is_available_for_registration(self):
        if not self.is_active:
            return False
        if self.course_status not in ['open', 'active']:
            return False
        if self.get_seats_available() <= 0:
            return False
        if self.registration_deadline and self.registration_deadline < timezone.now().date():
            return False
        return True
    
    def get_display_date(self):
        """Get formatted date string for display"""
        if self.course_type == 'workshop' and self.event_date:
            return f"Event Date: {self.event_date.strftime('%d %B %Y')}"
        elif self.start_date:
            if self.end_date:
                return f"{self.start_date.strftime('%d %B %Y')} - {self.end_date.strftime('%d %B %Y')}"
            else:
                return f"Starts: {self.start_date.strftime('%d %B %Y')}"
        return "Dates to be announced"
    
    def get_available_centres(self):
        """Return available centres based on course mode"""
        if self.mode == 'online':
            return Centre.objects.all()
        return self.available_centres.all()
    
    def __str__(self):
        return f"{self.course_name} ({self.course_duration})"
    
    class Meta:
        ordering = ['-created_at']