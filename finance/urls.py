from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Jalur utama untuk proses pembelian lagu
    path('buy/<int:song_id>/', views.checkout_song, name='checkout_song'),
    
    # Jalur riwayat belanja (sebelumnya subscription_detail)
    path('history/', views.payment_history, name='payment_history'),
    
    # Bagian Admin: Laporan Keuangan (Penjualan Lagu)
    path('report/', views.report, name='report'),

    path('buy/<int:song_id>/', views.checkout_song, name='buy_song'),
]