from django import forms
from .models import UploadedImage

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['image', 'title', 'details', 'phone']

class ImageEditForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ['title', 'details', 'phone']  # Editable fields
