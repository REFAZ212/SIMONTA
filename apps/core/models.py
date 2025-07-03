# ===== apps/core/models.py =====
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class JadwalPenting(models.Model):
    nama_jadwal = models.CharField(max_length=200)
    deskripsi = models.TextField()
    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Jadwal Penting"
    
    def __str__(self):
        return self.nama_jadwal

class Notifikasi(models.Model):
    TIPE_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Peringatan'),
        ('success', 'Sukses'),
        ('danger', 'Penting'),
    ]
    
    judul = models.CharField(max_length=200)
    pesan = models.TextField()
    tipe = models.CharField(max_length=20, choices=TIPE_CHOICES, default='info')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='core_notifikasi')
    is_read = models.BooleanField(default=False)
    is_global = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Notifikasi"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.judul