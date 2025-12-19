from django.db import models
from django.contrib.auth.models import AbstractUser
from artist.models import Artist, Song, SongPurchase
from django.conf import settings

class TopArtist(models.Model):
    name = models.CharField(max_length=100)
    genre = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class LikedSong(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    song_name = models.CharField(max_length=100)
    artist = models.ForeignKey(TopArtist, on_delete=models.SET_NULL, null=True)
    liked_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} likes {self.song_name}"
