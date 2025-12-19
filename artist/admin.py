from django.contrib import admin
from .models import Artist, Song, SongPurchase

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("stage_name", "user", "created_at")
    search_fields = ("stage_name", "user__username")

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "price", "play_count", "purchase_count", "upload_date")
    list_filter = ("artist",)
    search_fields = ("title", "artist__stage_name")
    readonly_fields = ("play_count", "purchase_count", "upload_date")

@admin.register(SongPurchase)
class SongPurchaseAdmin(admin.ModelAdmin):
    list_display = ("song", "buyer", "price_paid", "purchase_date")
    list_filter = ("purchase_date", "song__artist")
    search_fields = ("buyer__username", "song__title")