from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.core.paginator import Paginator
from .models import Payment
from artist.models import Song, SongPurchase 

@login_required
def checkout_song(request, song_id):
    """Halaman konfirmasi dan eksekusi pembayaran lagu"""
    song = get_object_or_404(Song, id=song_id)
    
    # 1. Validasi: Cek apakah user sudah memiliki lagu ini
    if SongPurchase.objects.filter(buyer=request.user, song=song).exists():
        messages.info(request, "Lagu ini sudah ada di koleksi Anda.")
        return redirect('user:library')

    if request.method == "POST":
        # A. Simpan transaksi di modul Finance (untuk Laporan Admin)
        Payment.objects.create(
            user=request.user,
            song=song,
            amount=song.price,
            status='SUCCESS'
        )

        # B. Simpan di modul Artist (untuk Koleksi User)
        # Pastikan nama field 'price_at_purchase' sesuai dengan model SongPurchase Anda
        SongPurchase.objects.create(
           song=song,
           buyer=request.user,
           price_paid=song.price  # Ubah ke price_paid
        )

        # C. Update counter pembelian (opsional, jika fungsi ada di model Song)
        if hasattr(song, 'increment_purchase'):
            song.increment_purchase()
        
        messages.success(request, f"Pembayaran berhasil! Lagu {song.title} kini ada di koleksi Anda.")
        return render(request, 'finance/success.html', {'song': song})

    # Tampilkan halaman konfirmasi (GET)
    return render(request, 'finance/checkout.html', {'song': song})

@login_required
def report(request):
    """Laporan Keuangan Konsolidasi untuk Admin"""
    if not request.user.is_staff:
        messages.error(request, "Akses ditolak. Anda bukan admin.")
        return redirect('user:home')

    all_payments = Payment.objects.all().select_related('user', 'song').order_by('-transaction_date')
    total_revenue = all_payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'payments': all_payments,
        'total_revenue': total_revenue,
    }
    return render(request, 'finance/report.html', context)

@login_required
def payment_history(request):
    """Riwayat belanja milik user pribadi"""
    payments = Payment.objects.filter(user=request.user).select_related('song', 'song__artist').order_by('-transaction_date')
    return render(request, 'finance/history.html', {'payments': payments})


def report(request):
    all_payments = Payment.objects.all().order_by('-id')
    
    # Hitung total revenue
    total_revenue = sum(p.amount for p in all_payments)

    # Tambahkan Paginator: 10 transaksi per halaman
    paginator = Paginator(all_payments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'payments': page_obj, # Sekarang 'payments' berisi 10 data per halaman
        'total_revenue': total_revenue,
    }
    return render(request, 'finance/report.html', context)