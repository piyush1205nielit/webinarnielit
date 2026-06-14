from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from course.models import Course, Centre
from .models import Student

INDIAN_STATES = [
    ('', '-- Select State/UT --'),
    ('Andaman and Nicobar Islands', 'Andaman and Nicobar Islands'),
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chandigarh', 'Chandigarh'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Dadra and Nagar Haveli and Daman and Diu', 'Dadra and Nagar Haveli and Daman and Diu'),
    ('Delhi', 'Delhi'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jammu and Kashmir', 'Jammu and Kashmir'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Ladakh', 'Ladakh'),
    ('Lakshadweep', 'Lakshadweep'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Puducherry', 'Puducherry'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'),
]

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 'father_name', 'date_of_birth', 'gender', 'category',
            'email_id', 'mobile_number', 'state', 'city', 'institute_name',
            'course_enrolled', 'preferred_centre'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter father's full name"}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'email_id': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '9876543210', 'pattern': '[0-9]{10}', 'maxlength': '10'}),
            'state': forms.Select(choices=INDIAN_STATES, attrs={'class': 'form-select'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your city'}),
            'institute_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your school/college/institute name'}),
            'course_enrolled': forms.Select(attrs={'class': 'form-select', 'id': 'id_course_enrolled'}),
            'preferred_centre': forms.Select(attrs={'class': 'form-select', 'id': 'id_preferred_centre'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['course_enrolled'].queryset = Course.objects.filter(
            is_active=True,
            course_status__in=['open', 'active']
        )

        self.fields['preferred_centre'].required = False
        self.fields['state'].required = False
        self.fields['city'].required = False
        self.fields['institute_name'].required = False
        self.fields['gender'].required = False

        course_id = None
        if self.data.get('course_enrolled'):
            course_id = self.data.get('course_enrolled')
        elif self.initial.get('course_enrolled'):
            course = self.initial.get('course_enrolled')
            course_id = course.id if hasattr(course, 'id') else course

        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                if course.mode == 'online':
                    self.fields['preferred_centre'].required = False
                    self.fields['preferred_centre'].queryset = Centre.objects.all()
                else:
                    self.fields['preferred_centre'].required = True
                    self.fields['preferred_centre'].queryset = course.available_centres.all()
            except (ValueError, Course.DoesNotExist):
                self.fields['preferred_centre'].queryset = Centre.objects.none()
        else:
            self.fields['preferred_centre'].queryset = Centre.objects.none()

    def clean_email_id(self):
        email_id = self.cleaned_data.get('email_id')
        course_enrolled = self.cleaned_data.get('course_enrolled')

        if email_id and course_enrolled:
            existing = Student.objects.filter(
                email_id=email_id,
                course_enrolled=course_enrolled
            ).exclude(status='cancelled').first()

            if existing:
                raise ValidationError(
                    f"You have already registered for {course_enrolled.course_name} with this email address. "
                    f"Your registration number is: {existing.registration_number}"
                )
        return email_id

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        course_enrolled = self.cleaned_data.get('course_enrolled')

        if mobile_number and course_enrolled:
            existing = Student.objects.filter(
                mobile_number=mobile_number,
                course_enrolled=course_enrolled
            ).exclude(status='cancelled').first()

            if existing:
                raise ValidationError(
                    f"You have already registered for {course_enrolled.course_name} with this mobile number. "
                    f"Your registration number is: {existing.registration_number}"
                )
        return mobile_number

    def clean(self):
        cleaned_data = super().clean()
        course_enrolled = cleaned_data.get('course_enrolled')
        preferred_centre = cleaned_data.get('preferred_centre')

        if course_enrolled and course_enrolled.get_seats_available() <= 0:
            raise ValidationError(f"Sorry, {course_enrolled.course_name} has no seats available.")

        if course_enrolled and course_enrolled.mode != 'online':
            if not preferred_centre:
                self.add_error('preferred_centre', "Please select a preferred centre for this course.")

        return cleaned_data


class UserLookupForm(forms.Form):
    lookup_by = forms.ChoiceField(
        choices=[('email', 'Email ID'), ('mobile', 'Mobile Number')],
        widget=forms.RadioSelect,
        initial='email'
    )
    email_id = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}))
    mobile_number = forms.CharField(required=False, max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '9876543210', 'pattern': '[0-9]{10}'}))

    def clean(self):
        cleaned_data = super().clean()
        lookup_by = cleaned_data.get('lookup_by')
        email_id = cleaned_data.get('email_id')
        mobile_number = cleaned_data.get('mobile_number')

        if lookup_by == 'email' and not email_id:
            raise ValidationError({'email_id': 'Email is required'})
        if lookup_by == 'mobile' and not mobile_number:
            raise ValidationError({'mobile_number': 'Mobile number is required'})

        return cleaned_data