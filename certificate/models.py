import uuid
from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from registration.models import Student

class CertificateDesign(models.Model):
    """Model for fully customizable certificate design"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # ==================== HEADER SECTION ====================
    header_title = models.CharField(max_length=500, default="NIELIT Delhi", help_text="Institute name at the top")
    header_subtitle = models.CharField(max_length=500, blank=True, help_text="Brief intro / one liner about the institute")
    
    # ==================== LOGO SECTION ====================
    logo_position = models.CharField(
        max_length=20,
        choices=[
            ('center', 'Center'),
            ('left', 'Left'),
            ('right', 'Right'),
            ('both', 'Both Sides'),
            ('none', 'No Logo'),
        ],
        default='center'
    )
    institute_logo = models.ImageField(
        upload_to='certificates/logos/', blank=True, null=True,
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg'])]
    )
    secondary_logo = models.ImageField(
        upload_to='certificates/logos/', blank=True, null=True,
        help_text="Optional second logo (for both sides layout)",
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg'])]
    )
    logo_size = models.IntegerField(default=80, help_text="Logo size in pixels")
    
    # ==================== CERTIFICATE TITLE SECTION ====================
    certificate_title = models.CharField(max_length=200, default="CERTIFICATE OF COMPLETION")
    title_font_size = models.IntegerField(default=28, help_text="Font size for title")
    title_color = models.CharField(max_length=20, default="#1e3a8a", help_text="Color for title (hex)")
    
    # ==================== BODY TEXT SECTION ====================
    # Customizable body text template with placeholders
    # Available placeholders: {student_name}, {course_name}, {start_date}, {end_date}, 
    # {event_date}, {registration_number}, {institute_name}, {duration}
    # body_text_template = models.TextField(
    #     default="This certificate is proudly presented to {student_name} for successfully completing the course {course_name} from {start_date} to {end_date}.",
    #     help_text="Use placeholders: {student_name}, {course_name}, {start_date}, {end_date}, {event_date}, {registration_number}, {institute_name}, {duration}"
    # )
    # body_font_size = models.IntegerField(default=14, help_text="Font size for body text")
    # body_text_color = models.CharField(max_length=20, default="#000000", help_text="Color for body text (hex)")

    line_1_text = models.CharField(max_length=500, default="This certificate is proudly presented to", help_text="Line 1 text (simple text)")
    line_2_student_name = models.BooleanField(default=True, help_text="Show student name on line 2")
    line_2_custom_text = models.CharField(max_length=200, blank=True, help_text="Custom text instead of student name")
    line_2_font_size = models.IntegerField(default=32, help_text="Font size for line 2")
    line_2_color = models.CharField(max_length=20, default="#1e3a8a", help_text="Color for line 2")

    line_3_text = models.CharField(max_length=500, default="for successfully completing the", help_text="Line 3 text (simple text)")

    line_4_show_course = models.BooleanField(default=True, help_text="Show course/event name on line 4")
    line_4_custom_text = models.CharField(max_length=200, blank=True, help_text="Custom text instead of course name")
    line_4_font_size = models.IntegerField(default=20, help_text="Font size for line 4")
    line_4_color = models.CharField(max_length=20, default="#1e3a8a", help_text="Color for line 4")

    line_5_date_range = models.BooleanField(default=True, help_text="Show date range on line 5")
    line_5_custom_text = models.CharField(max_length=200, blank=True, help_text="Custom text for date line")
    line_5_font_size = models.IntegerField(default=14, help_text="Font size for line 5")
    line_5_color = models.CharField(max_length=20, default="#000000", help_text="Color for line 5")
    
    # ==================== SIGNATURE SECTION ====================
    signatory_count = models.IntegerField(
        choices=[(1, 'One Signatory'), (2, 'Two Signatories')],
        default=2
    )
    signature_1_position = models.CharField(
        max_length=20,
        choices=[('left', 'Left'), ('center', 'Center'), ('right', 'Right')],
        default='left'
    )
    signature_1_name = models.CharField(max_length=200, blank=True)
    signature_1_designation = models.CharField(max_length=200, blank=True)
    signature_1_image = models.ImageField(
        upload_to='certificates/signatures/', blank=True, null=True,
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg'])]
    )
    
    signature_2_name = models.CharField(max_length=200, null=True, blank=True)
    signature_2_designation = models.CharField(max_length=200, null=True, blank=True)
    signature_2_image = models.ImageField(
        upload_to='certificates/signatures/', blank=True, null=True,
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'svg'])]
    )
    
    # ==================== FOOTER SECTION ====================
    show_certificate_number = models.BooleanField(default=True)
    show_registration_number = models.BooleanField(default=True)
    show_student_id = models.BooleanField(default=True)
    show_issue_date = models.BooleanField(default=True)
    footer_font_size = models.IntegerField(default=9, help_text="Font size for footer text")
    
    # ==================== STYLING ====================
    border_color = models.CharField(max_length=20, default="#1e3a8a")
    border_width = models.IntegerField(default=3, help_text="Border width in pixels")
    background_image = models.ImageField(
        upload_to='certificates/backgrounds/', blank=True, null=True,
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])]
    )

     # QR Code Settings
    show_qr_code = models.BooleanField(default=True, help_text="Show QR code on certificate")
    qr_code_position = models.CharField(
        max_length=20,
        choices=[
            ('bottom-left', 'Bottom Left'),
            ('bottom-right', 'Bottom Right'),
            ('bottom-center', 'Bottom Center'),
        ],
        default='bottom-right'
    )
    qr_code_size = models.IntegerField(default=80, help_text="QR code size in pixels")
    
    # ==================== STATUS ====================
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_active', '-created_at']
    
    def __str__(self):
        return f"Certificate Design ({self.certificate_title})"
    
    def save(self, *args, **kwargs):
        if self.is_active:
            CertificateDesign.objects.filter(is_active=True).exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)


class StudentCertificate(models.Model):
    """Model for student certificates"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='student_certificate')
    design = models.ForeignKey(CertificateDesign, on_delete=models.SET_NULL, null=True)
    
    certificate_number = models.CharField(max_length=100, unique=True, blank=True)
    issue_date = models.DateField(help_text="Date when certificate is issued")
    
    
    # Metadata
    issued_by = models.CharField(max_length=100, blank=True, help_text="Name of issuing authority")
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-issue_date']
    
    def save(self, *args, **kwargs):
        if not self.certificate_number:
            year = self.issue_date.strftime('%Y') if self.issue_date else timezone.now().strftime('%Y')
            course_code = self.student.course_enrolled.course_name[:15].replace(' ', '_').upper()
            unique_id = str(self.student.id)[:8]
            self.certificate_number = f"NIELIT-{year}-{course_code}-{unique_id}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.name} - {self.certificate_number}"