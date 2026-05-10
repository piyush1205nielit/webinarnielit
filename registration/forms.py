from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from course.models import Course, Centre
from .models import Student

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 'date_of_birth', 'category', 'email_id', 
            'mobile_number', 'father_name', 'course_enrolled', 
            'preferred_centre'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'email_id': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '9876543210', 'pattern': '[0-9]{10}', 'maxlength': '10'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Father's/Guardian's name"}),
            'course_enrolled': forms.Select(attrs={'class': 'form-select', 'id': 'id_course_enrolled'}),
            'preferred_centre': forms.Select(attrs={'class': 'form-select', 'id': 'id_preferred_centre'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set available courses
        self.fields['course_enrolled'].queryset = Course.objects.filter(
            is_active=True, 
            course_status__in=['open', 'active']
        )
        
        # Make preferred_centre not required by default
        self.fields['preferred_centre'].required = False
        
        # Handle course_enrolled selection for filtering centres
        course_id = None
        
        # Check if we have a course_id from POST data
        if self.data.get('course_enrolled'):
            course_id = self.data.get('course_enrolled')
        # Check if we have an initial value
        elif self.initial.get('course_enrolled'):
            course = self.initial.get('course_enrolled')
            course_id = course.id if hasattr(course, 'id') else course
        
        # Filter centres based on course mode
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
        """Validate email for duplicate registration"""
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
        """Validate mobile for duplicate registration"""
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
        
        # Check seat availability
        if course_enrolled and course_enrolled.get_seats_available() <= 0:
            raise ValidationError(f"Sorry, {course_enrolled.course_name} has no seats available.")
        
        # Validate centre selection for offline/hybrid courses only
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