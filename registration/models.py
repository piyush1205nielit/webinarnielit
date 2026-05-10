import uuid
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from course.models import Course, Centre

class Student(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('sc', 'SC'),
        ('st', 'ST'),
        ('ews', 'EWS'),
        ('obc', 'OBC'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    mobile_number = models.CharField(max_length=10, validators=[
        RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit mobile number')
    ])
    date_of_birth = models.DateField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    email_id = models.EmailField()
    father_name = models.CharField(max_length=200)
    course_enrolled = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students')
    preferred_centre = models.ForeignKey(Centre, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')  # CHANGED: Allow NULL
    is_approved = models.BooleanField(default=False)

    registration_date = models.DateTimeField(auto_now_add=True)
    registration_number = models.CharField(max_length=50, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['email_id', 'course_enrolled']]
        indexes = [
            models.Index(fields=['email_id', 'course_enrolled']),
            models.Index(fields=['mobile_number', 'course_enrolled']),
            models.Index(fields=['registration_number']),
        ]
        ordering = ['-registration_date']
    
    def save(self, *args, **kwargs):
        if not self.registration_number:
            year = timezone.now().strftime('%Y')
            unique_id = str(uuid.uuid4().int)[:8]
            self.registration_number = f"NIELIT/{year}/{unique_id}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.mobile_number}"


class Certificate(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='certificate')
    certificate_number = models.CharField(max_length=100, unique=True, blank=True)
    issue_date = models.DateField(auto_now_add=True)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.certificate_number:
            unique_id = str(uuid.uuid4().int)[:8]
            self.certificate_number = f"CERT/{unique_id}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Certificate - {self.student.name}"