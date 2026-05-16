from django import forms
from .models import Course, Centre

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'course_name', 'course_desc', 'course_type', 'course_duration', 'course_status',
            'course_fees', 'start_date', 'end_date', 'event_date', 'registration_deadline',
            'image', 'syllabus_file', 'video_file', 'video_url',
            'modules_info', 'prerequisites', 'learning_outcomes',
            'mode', 'max_seats', 'available_centres',
            'is_active', 'is_featured'
        ]
        widgets = {
            'course_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter course name'}),
            'course_desc': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Detailed description of the course'}),
            'course_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_course_type'}),
            'course_duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 3 months, 6 weeks (leave blank for single-day events)'}),
            'course_status': forms.Select(attrs={'class': 'form-select'}),
            'course_fees': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0 for free courses'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_start_date'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_end_date'}),
            'event_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_event_date'}),
            'registration_deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_registration_deadline'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.youtube.com/embed/VIDEO_ID or https://player.vimeo.com/video/ID'}),
            'modules_info': forms.Textarea(attrs={'rows': 6, 'class': 'form-control', 'placeholder': 'Enter module details...'}),
            'prerequisites': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Any prerequisites for this course'}),
            'learning_outcomes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'What students will learn'}),
            'mode': forms.Select(attrs={'class': 'form-select', 'id': 'id_mode'}),
            'max_seats': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Maximum number of students (leave empty for unlimited)'}),
            'available_centres': forms.SelectMultiple(attrs={'class': 'form-select', 'id': 'id_available_centres', 'size': '8'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False
        self.fields['syllabus_file'].required = False
        self.fields['video_file'].required = False
        self.fields['video_url'].required = False
        self.fields['available_centres'].required = False
        self.fields['course_duration'].required = False
        self.fields['max_seats'].required = False
        self.fields['start_date'].required = False
        self.fields['end_date'].required = False
        self.fields['event_date'].required = False
        self.fields['registration_deadline'].required = False
        self.fields['available_centres'].help_text = "Select centres where this course will be offered (required for offline/hybrid modes)"


class CentreForm(forms.ModelForm):
    class Meta:
        model = Centre
        fields = ['centre_name', 'centre_address', 'centre_contact', 'centre_email', 'centre_desc']
        widgets = {
            'centre_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter centre name'}),
            'centre_address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Complete address'}),
            'centre_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'centre_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'centre_desc': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Additional information about the centre'}),
        }