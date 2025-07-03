# ===== apps/dosen/urls.py =====
from django.urls import path
from . import views

app_name = 'dosen'

urlpatterns = [
    
    path('dashboard/', views.dashboard, name='dashboard'),

    path('jadwal/', views.daftar_jadwal, name='daftar_jadwal'),
    path('jadwal/buat/', views.buat_jadwal, name='buat_jadwal'),
    path('jadwal/buat-bulk/', views.buat_jadwal_bulk, name='buat_jadwal_bulk'),
    # urls.py
    path('jadwal/edit/<int:pk>/', views.edit_jadwal, name='edit_jadwal'),

    path('jadwal/detail/<int:jadwal_id>/', views.detail_jadwal, name='detail_jadwal'),
    path('jadwal/hapus/<int:pk>/', views.delete_jadwal, name='delete_jadwal'),
    path('jadwal/toggle/<int:jadwal_id>/', views.toggle_status_jadwal, name='toggle_status_jadwal'),
    path('pendaftaran/update/<int:pendaftaran_id>/', views.update_status_pendaftaran, name='update_status_pendaftaran'),
    

    
    # apps/dosen/urls.py
    path('nilai/', views.nilai_mahasiswa_dummy, name='nilai_mahasiswa_dummy'),


    path('pengajuan/', views.pengajuan_judul_list, name='pengajuan_judul_list'),
    path('review-pengajuan/', views.review_pengajuan_list, name='review_pengajuan'),
    path('pengajuan/<int:pengajuan_id>/detail/', views.detail_pengajuan, name='detail_pengajuan'),
    path('pengajuan/<int:pengajuan_id>/approve/', views.approve_pengajuan, name='approve_pengajuan'),
    path('pengajuan/<int:pengajuan_id>/reject/', views.reject_pengajuan, name='reject_pengajuan'), # AJAX endpoint
    
]
