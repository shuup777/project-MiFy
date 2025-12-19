from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q # Untuk pencarian yang lebih fleksibel
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm
from .models import UserProfile, Notification
from artist.models import Song, SongPurchase
from artist.models import Artist
from django.db.models import Count

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Redirect berdasarkan Role
            if user.is_superuser or user.is_staff:
                messages.success(request, f"Selamat datang Admin {user.username}!")
                return redirect('admin_app:admin_dashboard') 
            else:
                messages.success(request, f"Halo {user.username}!")
                return redirect('user:home') 
    else:
        form = UserLoginForm()
    return render(request, 'user_app/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Akun berhasil dibuat. Silakan login.')
            return redirect('user:login')
    else:
        form = UserRegisterForm()
    return render(request, 'user_app/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Anda telah logout.")
    return redirect('user:login')

@login_required
def home_view(request):
    """Halaman eksplorasi lagu dengan fitur Search"""
    query = request.GET.get('q')
    if query:
        # Mencari berdasarkan judul lagu atau nama panggung artis
        songs = Song.objects.filter(
            Q(title__icontains=query) | 
            Q(artist__stage_name__icontains=query)
        ).distinct()
    else:
        songs = Song.objects.all().order_by('-id')
    
    # Ambil daftar ID lagu yang sudah dibeli agar tombol berubah menjadi 'Putar'
    owned_songs = SongPurchase.objects.filter(buyer=request.user).values_list('song_id', flat=True)
    
    # =========================
    # TAMBAHAN DASHBOARD USER
    # =========================

    # Top Artist (berdasarkan total lagu dilike)
    top_artists = Artist.objects.annotate(
        total_likes=Count('songs__liked_by')
    ).order_by('-total_likes')[:5]

    # Liked song milik user
    liked_songs = Song.objects.filter(liked_by=request.user)[:5]

    # Recommendation (lagu terpopuler)
    recommendations = Song.objects.order_by('-play_count')[:5]

    return render(request, 'user_app/home.html', {
        'songs': songs,
        'owned_songs': owned_songs,
        'query': query,

        'top_artists': top_artists,
        'liked_songs': liked_songs,
        'recommendations': recommendations,
    })

@login_required
def library_view(request):
    """Menampilkan koleksi lagu yang sudah dibeli"""
    purchases = SongPurchase.objects.filter(buyer=request.user).select_related('song')
    return render(request, 'user_app/library.html', {'purchases': purchases})

@login_required
def profile_view(request):
    """Mengelola profil user"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil Anda berhasil diperbarui.')
            return redirect('user:profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'user_app/profile.html', {'form': form, 'profile': profile})

@login_required
def notifications_view(request):
    """Menampilkan pemberitahuan untuk user"""
    notes = Notification.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'user_app/notifications.html', {'notifications': notes})