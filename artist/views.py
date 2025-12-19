from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.db.models import Sum, Count
from django.http import Http404, JsonResponse
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .form import SongUploadForm, SongEditForm, ArtistProfileForm
from .models import Artist, Song, SongPurchase

# Helper: get Artist instance for current user or 404
def get_current_artist_or_404(user):
    try:
        return Artist.objects.get(user=user)
    except Artist.DoesNotExist:
        raise Http404("Artist profile not found. You must be an artist to access this page.")


class ArtistRegisterForm(UserCreationForm):
    stage_name = forms.CharField(max_length=120, required=True)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ("stage_name",)



def artist_login(request):
    """
    Simple login view for artists. POST authenticates and logs in the user,
    then redirects to the artist dashboard. GET renders the login form.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.POST.get('next') or request.GET.get('next')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # ensure user has an Artist profile
            try:
                Artist.objects.get(user=user)
            except Artist.DoesNotExist:
                messages.error(request, "Akun tidak terdaftar sebagai artis.")
                return redirect("artists:artist_login")

            auth_login(request, user)
            if next_url:
                return redirect(next_url)
            return redirect("artists:dashboard")
        else:
            messages.error(request, "Username atau Password salah.")
            return redirect("artists:artist_login")

    # pass next param from GET to template so form can include it
    context = { 'next': request.GET.get('next', '') }
    return render(request, "artists/login_artist.html", context)


def artist_register(request):
    """Register a new user and create an associated Artist profile."""
    if request.method == "POST":
        form = ArtistRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            stage = form.cleaned_data.get("stage_name")
            Artist.objects.create(user=user, stage_name=stage)
            messages.success(request, "Akun artis berhasil dibuat. Silakan login.")
            return redirect("artists:artist_login")
    else:
        form = ArtistRegisterForm()

    return render(request, "artists/register_artist.html", {"form": form})

@login_required
def edit_profile(request):
    artist = request.user.artist

    if request.method == 'POST':
        form = ArtistProfileForm(request.POST, request.FILES, instance=artist)
        if form.is_valid():
            form.save()
            return redirect('artists:profile_artist')
    else:
        form = ArtistProfileForm(instance=artist)

    return render(request, 'artists/edit_profile.html', {
        'artist': artist,
        'form': form
    })

@login_required
def artist_profile(request):
    """
    Menampilkan profil artis yang sedang login.
    """
    artist = get_current_artist_or_404(request.user)

    # Calculate statistics
    songs = artist.songs.all()
    total_songs = songs.count()
    total_plays = songs.aggregate(total=Sum("play_count"))["total"] or 0
    total_purchases = songs.aggregate(total=Sum("purchase_count"))["total"] or 0

    context = {
        "artist": artist,
        "total_songs": total_songs,
        "total_plays": total_plays,
        "total_purchases": total_purchases,
    }

    return render(request, "artists/profile_artist.html", context)

@login_required

def artist_dashboard(request):
    artist = get_current_artist_or_404(request.user)
    songs = artist.songs.all().select_related("artist")
    # overall stats
    total_plays = songs.aggregate(total=Sum("play_count"))["total"] or 0
    total_purchases = songs.aggregate(total=Sum("purchase_count"))["total"] or 0
    total_income = SongPurchase.objects.filter(song__artist=artist).aggregate(
        total=Sum("price_paid")
    )["total"] or Decimal("0.00")

    context = {
        "artist": artist,
        "songs": songs,
        "total_plays": total_plays,
        "total_purchases": total_purchases,
        "total_income": total_income,
    }
    return render(request, "artists/dashboard.html", context)

@login_required
def upload_song(request):
    artist = get_current_artist_or_404(request.user)

    if request.method == "POST":
        form = SongUploadForm(request.POST, request.FILES)
        if form.is_valid():
            song = form.save(commit=False)
            song.artist = artist
            song.save()
            messages.success(request, "Lagu berhasil diupload.")
            return redirect(reverse("artists:dashboard"))
    else:
        form = SongUploadForm()

    return render(request, "artists/upload_song.html", {"form": form, "artist": artist})


@login_required
def edit_song(request, song_id):
    song = get_object_or_404(Song, id=song_id, artist=request.user.artist)

    if request.method == "POST":
        form = SongEditForm(request.POST, request.FILES, instance=song)
        if form.is_valid():
            form.save()
            return redirect('artists:dashboard')
    else:
        form = SongEditForm(instance=song)

    return render(request, 'artists/edit_song.html', {
        'form': form,
        'song': song
    })

@login_required
def delete_song(request, song_id):
    artist = get_current_artist_or_404(request.user)
    song = get_object_or_404(Song, id=song_id, artist=artist)
    if request.method == "POST":
        song.delete()
        messages.success(request, "Lagu berhasil dihapus.")
        return redirect(reverse("artists:dashboard"))
    # Perhatikan: template yang dirender adalah "artists/confirm_delete.html"
    return render(request, "artists/confirm_delete.html", {"song": song})


def song_list(request):
    """
    Public list of songs (for users to browse).
    """
    songs = Song.objects.select_related("artist").all()
    return render(request, "artists/song_list.html", {"songs": songs})


def song_detail(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    return render(request, "artists/song_detail.html", {"song": song})


from django.views.decorators.http import require_POST

@login_required
@require_POST
def increment_play_api(request, song_id):
    """
    Simple endpoint for incrementing play_count when user plays a song.
    - Accepts POST (AJAX / fetch).
    - Returns JSON with new play_count.
    NOTE: For production you should protect this (rate-limit, CSRF, auth) to avoid abuse.
    """
    song = get_object_or_404(Song, id=song_id)
    # increment safely
    Song.objects.filter(id=song.id).update(play_count=models.F('play_count') + 1)
    song.refresh_from_db(fields=['play_count'])
    return JsonResponse({"song_id": song.id, "play_count": song.play_count})


# ... bagian awal views.py yang sudah ada

@login_required
def your_songs(request):
    """
    Menampilkan semua lagu yang diupload oleh artis yang sedang login.
    """
    artist = get_current_artist_or_404(request.user)
    songs = artist.songs.all()
    return render(request, "artists/your_songs.html", {"songs": songs, "artist": artist})

# Sales / reporting views (artist-facing)
@login_required
def sales_report(request):
    """
    Returns per-song sales & income.
    """
    artist = get_current_artist_or_404(request.user)
    songs = artist.songs.all()

    report = []
    total_income_sum = Decimal("0.00")
    total_purchases_sum = 0
    
    for song in songs:
        # 1. Hitung Income (Sudah Benar)
        purchase_data = SongPurchase.objects.filter(song=song).aggregate(
            total_income=Sum("price_paid"),
            total_purchases=Count("id")  # <-- Menggunakan Count untuk jumlah pembelian
        )

        income = purchase_data["total_income"] or Decimal("0.00")
        purchases = purchase_data["total_purchases"]  # <-- Ambil hasil Count

        report.append({
            "song": song,
            "plays": song.play_count, # Pastikan song.play_count adalah field/property yang valid
            "purchases": purchases, # <-- Gunakan nilai hasil Count
            "income": income,
        })

        # Tambahkan ke total keseluruhan
        total_income_sum += income
        total_purchases_sum += purchases

    context = {
        "report": report, 
        "artist": artist,
        "total_income_sum": total_income_sum, # Tambahkan ini
        "total_purchases_sum": total_purchases_sum, # Tambahkan ini
    }

    return render(request, "artists/sales_report.html", context)


def play_song(request, id):
    song = get_object_or_404(Song, id=id)

    return render(request, 'artists/play_song.html', {
        'song': song
    })