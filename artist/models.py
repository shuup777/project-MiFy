from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.db import models
from django.db.models import F

class Artist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stage_name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='artist_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.stage_name or getattr(self.user, "username", "Artist")


class Song(models.Model):
    # relasi ke artis
    title = models.CharField(max_length=200)
    cover_image = models.ImageField(upload_to='covers/')
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="songs"
    )
    

    # informasi utama lagu
    title = models.CharField(max_length=255)

    audio_file = models.FileField(upload_to="songs/")
    cover_image = models.ImageField(
        upload_to="song_covers/",
        null=True,
        blank=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    upload_date = models.DateTimeField(auto_now_add=True)

    # statistik
    play_count = models.PositiveIntegerField(default=0)
    purchase_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-upload_date"]
        indexes = [
            models.Index(fields=["artist"]),
        ]

    def __str__(self):
        return f"{self.title} — {self.artist.stage_name}"

    def increment_play(self):
        Song.objects.filter(pk=self.pk).update(
            play_count=F("play_count") + 1
        )

    def increment_purchase(self):
        Song.objects.filter(pk=self.pk).update(
            purchase_count=F("purchase_count") + 1
        )


class SongPurchase(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="purchases")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="song_purchases")
    purchase_date = models.DateTimeField(default=timezone.now)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-purchase_date"]

    def __str__(self):
        return f"{self.buyer} bought {self.song.title} for {self.price_paid}"