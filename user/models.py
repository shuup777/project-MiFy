from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

# --- 1. SUBSCRIPTION (HIERARKI OOP) ---

class Subscription(models.Model):
    # ... (Field sama seperti sebelumnya) ...
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='subscription_obj')
    start_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='ACTIVE')

    # --- LOGIKA FITUR DETAIL (ABSTRACT) ---
    def get_ad_duration(self):
        """Mengembalikan durasi iklan dalam detik"""
        return 15 # Default logic (anggap saja iklan)

    def can_download(self):
        return False

    def audio_quality_label(self):
        return "Standard (128kbps)"

class FreeSubscription(Subscription):
    # PENGGUNA GRATIS
    def get_ad_duration(self):
        return 15  # ADA JEDA 15 DETIK (Iklan)

    def can_download(self):
        return False # TIDAK BISA DOWNLOAD
    
    def audio_quality_label(self):
        return "Standard (128kbps)"

class PremiumSubscription(Subscription):
    # PENGGUNA BERBAYAR
    next_billing_date = models.DateField(null=True, blank=True)

    def get_ad_duration(self):
        return 0   # TIDAK ADA JEDA (Langsung main)

    def can_download(self):
        return True # BISA DOWNLOAD
    
    def audio_quality_label(self):
        return "High Definition (320kbps)" # KUALITAS TINGGI

# --- 2. USER PROFILE & PREFERENCES (Sama seperti sebelumnya) ---
class UserProfile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='profile_obj')
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    profile_picture_url = models.URLField(blank=True)
    # ... field lain ...

# --- 3. CLASS USER (INTI LOGIKA PENGHUBUNG) ---
class User(AbstractUser):
    # --- field yang sudah ada sebelumnya ---
    liked_songs = models.ManyToManyField('artist.Song', related_name='liked_by', blank=True)

    # --- TAMBAHAN UNTUK ADMIN ---
    is_admin = models.BooleanField(default=False)
    ADMIN_ROLES = (
        ('system', 'System Admin'),
        ('finance', 'Finance Admin'),
    )
    admin_role = models.CharField(max_length=20, choices=ADMIN_ROLES, null=True, blank=True)

    # --- property dan method yang sudah ada sebelumnya ---
    @property
    def subscription(self):
        # Polimorfisme: Mengembalikan objek anak (Free/Premium)
        if hasattr(self.subscription_obj, 'premiumsubscription'):
            return self.subscription_obj.premiumsubscription
        elif hasattr(self.subscription_obj, 'freesubscription'):
            return self.subscription_obj.freesubscription
        return self.subscription_obj

    # --- METHOD UNTUK DIAKSES DI VIEW/TEMPLATE ---

    def get_wait_time(self):
        """Mengambil data durasi jeda dari subscription"""
        return self.subscription.get_ad_duration()

    def is_download_allowed(self):
        """Mengecek apakah tombol download boleh muncul"""
        return self.subscription.can_download()

    def play_song_logic(self, song):
        """
        Logika saat tombol play ditekan:
        1. Catat history
        2. Kembalikan info apakah perlu jeda iklan
        """
        # Simulasi mencatat history (karena model Music ada di temanmu)
        print(f"Mencatat {self.username} memutar {song}")
        
        # Return detail config untuk pemutar musik
        return {
            'ad_duration': self.get_wait_time(),
            'quality': self.subscription.audio_quality_label(),
            'can_download': self.is_download_allowed()
        }
    
    def upgrade_subscription(self):
        """Upgrade logika: Hapus Free -> Buat Premium"""
        current = self.subscription
        if isinstance(current, FreeSubscription):
            current.delete()
            PremiumSubscription.objects.create(user=self)

class UserPreferences(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='preferences')
    theme = models.CharField(max_length=20, default='light')
    audio_quality = models.CharField(max_length=20, default='standard')

    def __str__(self):
        return f"{self.user.username} preferences"

class Notification(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Notif for {self.user.username} at {self.timestamp}"