# finance/models.py
from django.db import models
from django.conf import settings
from artist.models import Song  # Import model lagu teman Anda

class Payment(models.Model):
    STATUS_CHOICES = [
        ('SUCCESS', 'Berhasil'),
        ('FAILED', 'Gagal'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SUCCESS')

    def __str__(self):
        return f"{self.user.username} - {self.song.title} - Rp{self.amount}"