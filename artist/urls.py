# artists/urls.py
from django.urls import path
from . import views

app_name = "artists"

urlpatterns = [
    path('', views.artist_dashboard, name="dashboard"),
    
    path("login/", views.artist_login, name="artist_login"), 

    path("register/", views.artist_register, name="artist_register"), 
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    path("profile/", views.artist_profile, name="profile_artist"),

    path("upload/", views.upload_song, name="upload_song"), # gunakan nama yang lebih deskriptif
    path("your-songs/", views.your_songs, name="your_songs"),
    path("sales-report/", views.sales_report, name="sales_report"), # Menggunakan underscore (Pythonic)

    path("song/<int:song_id>/edit/", views.edit_song, name="edit"), # Lebih ringkas
    path("song/<int:song_id>/delete/", views.delete_song, name="delete"), # Lebih ringkas
    path('songs/<int:id>/play/', views.play_song, name='play'),  # ← WAJIB ADA

    # 4. PUBLIC FACING (Jika diaplikasikan)
    path("all-songs/", views.song_list, name="song_list"), # Mengganti 'songs/' agar tidak konflik dengan path lain
    path("all-songs/<int:song_id>/", views.song_detail, name="song_detail"),

    # 5. API ENDPOINT
    # Menggunakan 'api/' sebagai prefix jelas
    path("api/song/<int:song_id>/play/", views.increment_play_api, name="api_increment_play"),
]