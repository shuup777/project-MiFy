from django import forms
from .models import Artist, Song

class SongUploadForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ["title", "audio_file", "cover_image", "price"]
        widgets = {
            "price": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }

class SongEditForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ["title", "audio_file", "cover_image", "price"]

        labels = {
            "title": "Judul Lagu",
            "audio_file": "File Lagu (Audio)",
            "cover_image": "Cover Lagu",
            "price": "Harga Lagu",
        }

        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Masukkan judul lagu"
            }),
            "audio_file": forms.ClearableFileInput(attrs={
                "accept": "audio/*"
            }),
            "cover_image": forms.ClearableFileInput(attrs={
                "accept": "image/*"
            }),
            "price": forms.NumberInput(attrs={
                "step": "0.01",
                "min": "0",
                "placeholder": "0.00"
            }),
        }

        
class ArtistProfileForm(forms.ModelForm):
    """
    Form untuk mengedit data profil artis.
    """
    class Meta:
        model = Artist
        # Tentukan fields yang bisa diedit oleh artis
        fields = ['photo', 'stage_name', 'bio']
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell us about yourself..."}),
        }
        