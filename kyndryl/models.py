import uuid
from django.db import models
from django.core.validators import RegexValidator, FileExtensionValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import random


def validate_file_size(value):
    max_size_mb = 5
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'File size must not exceed {max_size_mb}MB.')


class KyndrylRegistration(models.Model):

    GENDER = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('sc', 'SC'),
        ('st', 'ST'),
        ('ews', 'EWS'),
        ('obc', 'OBC'),
        ('pwd', 'PWD'),
    ]

    QUALIFICATION_CHOICES = [
        ('10th', 'Class 10th'),
        ('12th', 'Class 12th'),
        ('diploma', 'Diploma'),
        ('graduate', 'Graduate'),
        ('postgraduate', 'Postgraduate'),
        ('phd', 'PhD'),
        ('working_professional', 'Working Professional'),
        ('other', 'Other'),
    ]

    CURRENT_EMPLOYMENT_STATUS_CHOICES = [
        ('unemployed', 'Unemployed'),
        ('employed_technical_upgradation_required', 'Employed & Technical Upgradation Required'),
    ]

    BENEFICIARY_BELONGING_CHOICES = [
        ('ews', 'Economically Weaker Section (EWS)'),
        ('tier2_tier3', 'Place of Residence in Tier 2 / Tier 3 City'),
        ('minority_community', 'Minority Community'),
        ('women', 'Women of any category'),
        ('middle_class', 'Jobseeker belonging to Middle Class Family'),
    ]

    CLOUD_COMPUTING_CHOICES = [
        ('basic_level', 'Basic Level'),
        ('middle_level', 'Middle Level'),
        ('advance_level', 'Advance Level'),
    ]

    INDIAN_STATES_UTS = [
        ('', '-- Select State / UT --'),
        # States
        ('Andhra Pradesh', 'Andhra Pradesh'),
        ('Arunachal Pradesh', 'Arunachal Pradesh'),
        ('Assam', 'Assam'),
        ('Bihar', 'Bihar'),
        ('Chhattisgarh', 'Chhattisgarh'),
        ('Goa', 'Goa'),
        ('Gujarat', 'Gujarat'),
        ('Haryana', 'Haryana'),
        ('Himachal Pradesh', 'Himachal Pradesh'),
        ('Jharkhand', 'Jharkhand'),
        ('Karnataka', 'Karnataka'),
        ('Kerala', 'Kerala'),
        ('Madhya Pradesh', 'Madhya Pradesh'),
        ('Maharashtra', 'Maharashtra'),
        ('Manipur', 'Manipur'),
        ('Meghalaya', 'Meghalaya'),
        ('Mizoram', 'Mizoram'),
        ('Nagaland', 'Nagaland'),
        ('Odisha', 'Odisha'),
        ('Punjab', 'Punjab'),
        ('Rajasthan', 'Rajasthan'),
        ('Sikkim', 'Sikkim'),
        ('Tamil Nadu', 'Tamil Nadu'),
        ('Telangana', 'Telangana'),
        ('Tripura', 'Tripura'),
        ('Uttar Pradesh', 'Uttar Pradesh'),
        ('Uttarakhand', 'Uttarakhand'),
        ('West Bengal', 'West Bengal'),
        # Union Territories
        ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
        ('Chandigarh', 'Chandigarh'),
        ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
        ('Delhi', 'Delhi'),
        ('Jammu and Kashmir', 'Jammu and Kashmir'),
        ('Ladakh', 'Ladakh'),
        ('Lakshadweep', 'Lakshadweep'),
        ('Puducherry', 'Puducherry'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=20, null=True, blank=True, choices=GENDER)
    date_of_birth = models.DateField()
    mobile_number = models.CharField(max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit mobile number')]
    )
    email_id = models.EmailField(unique=True)
    aadhar_number = models.CharField(max_length=12,
        validators=[RegexValidator(r'^\d{12}$', 'Enter a valid 12-digit Aadhaar number')]
    )
    highest_qualification = models.CharField(max_length=50, null=True, blank=True, choices=QUALIFICATION_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True,choices=INDIAN_STATES_UTS)
    pin_code = models.CharField(max_length=6,
        validators=[RegexValidator(r'^\d{6}$', 'Enter a valid 6-digit pin code')]
    )
    current_employment_status = models.CharField(max_length=100, null=True, blank=True, choices=CURRENT_EMPLOYMENT_STATUS_CHOICES)
    beneficiary_belonging = models.CharField(max_length=100, null=True, blank=True, choices=BENEFICIARY_BELONGING_CHOICES)
    expertise_in_cloud_computing = models.CharField(max_length=50, null=True, blank=True, choices=CLOUD_COMPUTING_CHOICES)
    father_name = models.CharField(max_length=200, null=True, blank=True)
    father_occupation = models.CharField(max_length=500, null=True, blank=True)
    mother_name = models.CharField(max_length=200, null=True, blank=True)
    mother_occupation = models.CharField(max_length=500, null=True, blank=True)

    photo = models.ImageField(
        upload_to='kyndryl_registration/photos/',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size,
        ]
    )
    aadhaar_card = models.FileField(
        upload_to='kyndryl_registration/aadhaar/',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf']),
            validate_file_size,
        ]
    )
    highest_qualification_certificate_name = models.CharField(
        max_length=200, null=True, blank=True,
        help_text='Name of the certificate e.g. B.Tech Degree, Class 12 Marksheet'
    )
    highest_qualification_certificate = models.FileField(
        upload_to='kyndryl_registration/certificates/',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf']),
            validate_file_size,
        ]
    )

    registration_date = models.DateTimeField(auto_now_add=True)
    registration_number = models.CharField(max_length=50, unique=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['email_id']),
            models.Index(fields=['mobile_number']),
            models.Index(fields=['registration_number']),
        ]
        ordering = ['-registration_date']

    def _generate_registration_number(self):
        """Format: RNDDMMYYYY-6digit_random-8digit_uuid"""
        date_str   = timezone.now().strftime('%d%m%Y')
        unique_id  = str(uuid.uuid4().int)[:8]
        random_6   = str(random.randint(100000, 999999))
        return f"RN{date_str}-{random_6}-{unique_id}"

    def save(self, *args, **kwargs):
        if not self.registration_number:
            # Collision guard — regenerate if the number already exists
            for _ in range(10):
                reg_num = self._generate_registration_number()
                if not KyndrylRegistration.objects.filter(registration_number=reg_num).exists():
                    self.registration_number = reg_num
                    break
            else:
                # Absolute fallback — uuid alone guarantees uniqueness
                self.registration_number = f"RN{timezone.now().strftime('%d%m%Y')}-{str(uuid.uuid4().int)[:14]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.registration_number}"