from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # Menampilkan kolom yang informatif di halaman admin
    list_display = ('transaction_date', 'user', 'song', 'amount', 'status')
    # Menambahkan filter di sisi kanan
    list_filter = ('status', 'transaction_date')
    # Menambahkan fitur pencarian
    search_fields = ('user__username', 'song__title')