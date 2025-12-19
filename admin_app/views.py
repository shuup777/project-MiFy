from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from artist.models import Artist, Song, SongPurchase

# ===============================
# Helper function: cek apakah admin
# ===============================
def is_admin(user):
    return user.is_staff or getattr(user, 'is_admin', False)

# ===============================
# Login Admin
# ===============================
def admin_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None and is_admin(user):
            login(request, user)
            return redirect("finance:report")
        else:
            return render(request, "admin_app/login.html", {
                "error": "Username/password salah atau bukan admin"
            })

    return render(request, "admin_app/login.html")

# ===============================
# Dashboard Admin
# ===============================
@login_required(login_url='/user/login/')
@user_passes_test(is_admin, login_url='/user/login/')
def admin_dashboard(request):
    top_artists = Artist.objects.all()
    liked_songs = SongPurchase.objects.select_related('song', 'buyer')
    recommendations = Song.objects.order_by('-play_count')[:5]

    context = {
        "top_artists": top_artists,
        "liked_songs": liked_songs,
        "recommendations": recommendations
    }
    return render(request, "admin_app/dashboard.html", context)

@login_required
def admin_profile_view(request):
    # pastikan hanya admin
    if not request.user.is_superuser:
        return redirect('home')

    return render(request, 'admin_app/profile.html')

# ===============================
# Logout Admin
# ===============================
@login_required(login_url='/user/login/')
def admin_logout_view(request):
    logout(request)
    return redirect('/')