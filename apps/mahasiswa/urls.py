# ===== apps/mahasiswa/urls.py =====
from django.urls import path
from . import views

app_name = 'mahasiswa'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pengajuan-ta/', views.pengajuan_ta, name='pengajuan_ta'),
    path('pengajuan-judul/', views.pengajuan_judul, name='pengajuan_judul'),
    path('pengajuan/detail/<int:pk>/', views.detail_pengajuan, name='detail_pengajuan'),
    
    path('nilai/', views.lihat_nilai, name='lihat_nilai'),
    path('jadwal/', views.jadwal_bimbingan, name='jadwal_bimbingan')

    
]