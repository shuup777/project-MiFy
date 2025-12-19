from django.urls import path
from . import views
from admin_app import views

app_name = 'admin_app'

urlpatterns = [
    path("login/", views.admin_login_view, name="admin_login"),
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("logout/", views.admin_logout_view, name="admin_logout"),
    path("profile/", views.admin_profile_view, name="admin_profile"),
]