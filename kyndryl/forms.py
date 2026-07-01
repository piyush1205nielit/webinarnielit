from django import forms
from .models import KyndrylRegistration

BENEFICIARY_CHOICES_WITH_EMPTY = [
    ('', '-- Select Category --')
] + list(KyndrylRegistration.BENEFICIARY_BELONGING_CHOICES)


class KyndrylRegistrationForm(forms.ModelForm):

    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        label='Date of Birth',
    )

    beneficiary_belonging = forms.ChoiceField(
        choices=BENEFICIARY_CHOICES_WITH_EMPTY,
        required=True,
        label='Beneficiary Category',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = KyndrylRegistration
        exclude = ['id', 'registration_number', 'registration_date', 'updated_at']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
            }),
            'father_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Father's full name",
            }),
            'father_occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Father's occupation",
            }),
            'mother_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Mother's full name",
            }),
            'mother_occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Mother's occupation",
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'email_id': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'you@example.com',
            }),
            'mobile_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10-digit mobile number',
                'maxlength': '10',
            }),
            'aadhar_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12-digit Aadhaar number',
                'maxlength': '12',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'House/Flat No., Street, Area, Locality',
            }),
            # state is now a Select — driven by model choices
            'state': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City',
            }),
            'pin_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '6-digit PIN code',
                'maxlength': '6',
            }),
            'highest_qualification': forms.Select(attrs={'class': 'form-select'}),
            'highest_qualification_certificate_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. B.Tech Degree, Class 12 Marksheet',
            }),
            'current_employment_status': forms.Select(attrs={'class': 'form-select'}),
            'expertise_in_cloud_computing': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpg,image/jpeg,image/png',
            }),
            'aadhaar_card': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpg,image/jpeg,image/png,application/pdf',
            }),
            'highest_qualification_certificate': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpg,image/jpeg,image/png,application/pdf',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Empty labels for optional selects
        for field_name in ['gender', 'highest_qualification',
                           'current_employment_status', 'expertise_in_cloud_computing']:
            if field_name in self.fields:
                self.fields[field_name].empty_label = '-- Select --'

        # Pre-populate beneficiary on edit
        if self.instance and self.instance.pk:
            self.initial['beneficiary_belonging'] = self.instance.beneficiary_belonging

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        qs = KyndrylRegistration.objects.filter(mobile_number=mobile)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('This mobile number is already registered.')
        return mobile

    def clean_aadhar_number(self):
        aadhar = self.cleaned_data.get('aadhar_number')
        qs = KyndrylRegistration.objects.filter(aadhar_number=aadhar)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('This Aadhaar number is already registered.')
        return aadhar

    def clean_date_of_birth(self):
        from django.utils import timezone
        dob = self.cleaned_data.get('date_of_birth')
        if dob and dob >= timezone.now().date():
            raise forms.ValidationError('Date of birth must be in the past.')
        return dob