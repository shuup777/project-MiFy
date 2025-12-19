from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import home_view

urlpatterns = [
    # Django admin bawaan
    path("admin/", admin.site.urls),

    # User app
    path("user/", include(("user.urls", "user"), namespace="user")),

    # Admin custom app
    path("admin_app/", include(("admin_app.urls", "admin_app"), namespace="admin_app")),

    # Artist app (SEMUA URL ARTIST DI SINI)
    path("artists/", include(("artist.urls", "artists"), namespace="artists")),

    # Finance app
    path("finance/", include(("finance.urls", "finance"), namespace="finance")),

    # Homepage
    path("", home_view, name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
