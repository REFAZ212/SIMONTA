# ===== apps/core/views.py =====
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import JadwalPenting, Notifikasi

def home(request):
    jadwal_penting = JadwalPenting.objects.filter(is_active=True)
    context = {
        'jadwal_penting': jadwal_penting,
    }
    return render(request, 'core/home.html', context)

@login_required
def dashboard(request):
    # Redirect berdasarkan role
    if request.user.is_admin():
        return redirect('adminkampus:dashboard')
    elif request.user.is_dosen():
        return redirect('dosen:dashboard')
    elif request.user.is_mahasiswa():
        return redirect('mahasiswa:dashboard')
    return render(request, 'core/home.html')