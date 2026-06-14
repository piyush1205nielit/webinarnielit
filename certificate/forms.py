from django import forms
from .models import CertificateDesign

class CertificateDesignForm(forms.ModelForm):
    class Meta:
        model = CertificateDesign
        fields = '__all__'
        exclude = ['created_at', 'updated_at']
        widgets = {
            # Header
            'header_title': forms.TextInput(attrs={'class': 'form-control'}),
            'header_subtitle': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Logo
            'logo_position': forms.Select(attrs={'class': 'form-select'}),
            'logo_size': forms.NumberInput(attrs={'class': 'form-control', 'min': 40, 'max': 150}),
            
            # Title
            'certificate_title': forms.TextInput(attrs={'class': 'form-control'}),
            'title_font_size': forms.NumberInput(attrs={'class': 'form-control', 'min': 16, 'max': 48}),
            'title_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color', 'style': 'height: 38px'}),
            
            # Custom Body Text
            'line_1_text': forms.TextInput(attrs={'class': 'form-control'}),
            'line_2_student_name': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'line_2_custom_text': forms.TextInput(attrs={'class': 'form-control'}),
            'line_2_font_size': forms.NumberInput(attrs={'class': 'form-control', 'min': 16, 'max': 48}),
            'line_2_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color', 'style': 'height: 38px'}),
            'line_3_text': forms.TextInput(attrs={'class': 'form-control'}),
            'line_4_show_course': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'line_4_custom_text': forms.TextInput(attrs={'class': 'form-control'}),
            'line_4_font_size': forms.NumberInput(attrs={'class': 'form-control', 'min': 14, 'max': 36}),
            'line_4_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color', 'style': 'height: 38px'}),
            'line_5_date_range': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'line_5_custom_text': forms.TextInput(attrs={'class': 'form-control'}),
            'line_5_font_size': forms.NumberInput(attrs={'class': 'form-control', 'min': 10, 'max': 20}),
            'line_5_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color', 'style': 'height: 38px'}),
            
            # Signatures
            'signatory_count': forms.Select(attrs={'class': 'form-select'}),
            'signature_1_position': forms.Select(attrs={'class': 'form-select'}),
            'signature_1_name': forms.TextInput(attrs={'class': 'form-control'}),
            'signature_1_designation': forms.TextInput(attrs={'class': 'form-control'}),
            'signature_2_name': forms.TextInput(attrs={'class': 'form-control'}),
            'signature_2_designation': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Footer
            'show_certificate_number': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_registration_number': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_student_id': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_issue_date': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'footer_font_size': forms.NumberInput(attrs={'class': 'form-control', 'min': 8, 'max': 14}),
            
            # Styling
            'border_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color', 'style': 'height: 38px'}),
            'border_width': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make file fields optional
        self.fields['institute_logo'].required = False
        self.fields['secondary_logo'].required = False
        self.fields['signature_1_image'].required = False
        self.fields['signature_2_image'].required = False
        self.fields['background_image'].required = False

class IssueCertificateForm(forms.Form):
    issue_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    issued_by = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name of issuing authority'})
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Any remarks (optional)'})
    )