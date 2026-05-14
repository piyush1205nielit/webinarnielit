from django import forms
from public.models import Announcement, CarouselImage

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['content', 'is_active', 'order', 'expires_at']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Enter announcement message'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'expires_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expires_at'].required = False


class CarouselImageForm(forms.ModelForm):
    class Meta:
        model = CarouselImage
        fields = ['image', 'order', 'is_active']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }