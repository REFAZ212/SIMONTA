# ===== apps/adminkampus/urls.py =====
from django.urls import path
from . import views

app_name = 'adminkampus'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('mahasiswa/', views.manage_mahasiswa, name='manage_mahasiswa'),
    path('mahasiswa/tambah/', views.tambah_mahasiswa, name='tambah_mahasiswa'),
    path('mahasiswa/<int:mahasiswa_id>/edit/', views.edit_mahasiswa, name='edit_mahasiswa'),
    path('mahasiswa/<int:mahasiswa_id>/delete/', views.delete_mahasiswa, name='delete_mahasiswa'),
    

    path('dosen/', views.manage_dosen, name='manage_dosen'),
    path('tambah-dosen/', views.tambah_dosen, name='tambah_dosen'),
    path('edit-dosen/<int:dosen_id>/', views.edit_dosen, name='edit_dosen'),
    path('hapus_dosen/<int:dosen_id>/', views.hapus_dosen, name='hapus_dosen'),
    path('pembagian-dosen/', views.pembagian_dosen, name='pembagian_dosen'),

    path('pengajuan/', views.pengajuan_ta_list, name='pengajuan_ta_list'),
    
    path('pengajuan/<int:pengajuan_id>/approve/', views.approve_pengajuan, name='approve_pengajuan'),
    path('review-pengajuan/', views.review_pengajuan, name='review_pengajuan'),  # AJAX endpoint
    path('bulk-review-pengajuan/', views.bulk_review_pengajuan, name='bulk_review_pengajuan'),  # AJAX endpoint


    path('jadwal/', views.manage_jadwal_penting, name='manage_jadwal_penting'),
    path('jadwal/tambah/', views.tambah_jadwal_penting, name='tambah_jadwal_penting'),
    path('jadwal/edit/<int:pk>/', views.edit_jadwal_penting, name='edit_jadwal_penting'),
    path('jadwal/hapus/<int:pk>/', views.hapus_jadwal_penting, name='hapus_jadwal_penting'),

    
    path('laporan/', views.laporan, name='laporan'),
    path('pengaturan/', views.pengaturan, name='pengaturan'),

]