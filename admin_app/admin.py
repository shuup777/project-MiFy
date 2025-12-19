from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'is_admin', 'admin_role')
    list_filter = ('is_staff', 'is_superuser', 'is_admin', 'admin_role')