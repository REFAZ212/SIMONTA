from django.db import models
from django.contrib.auth.models import User
from django.conf import settings




class SyaratTA(models.Model):
    min_ipk = models.DecimalField(max_digits=3, decimal_places=2, default=2.5)
    min_sks = models.IntegerField(default=120)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
        
    class Meta:
        verbose_name_plural = "Syarat TA"
        
    def __str__(self):
        return f"IPK >= {self.min_ipk}, SKS >= {self.min_sks}"

class Mahasiswa(models.Model):
    nim = models.CharField(max_length=20, unique=True, verbose_name="NIM")
    nama = models.CharField(max_length=100, verbose_name="Nama Lengkap")
    jurusan = models.CharField(max_length=100, verbose_name="Jurusan")
    angkatan = models.IntegerField(verbose_name="Angkatan")
    ipk = models.DecimalField(max_digits=3, decimal_places=2, verbose_name="IPK")
    sks_lulus = models.IntegerField(verbose_name="SKS Lulus")
    dosen_pembimbing = models.CharField(max_length=100, verbose_name="Dosen Pembimbing", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Data Mahasiswa"
        ordering = ['nim']
        
    def __str__(self):
        return f"{self.nim} - {self.nama}"
class PengajuanTA(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
    ]

    mahasiswa = models.ForeignKey(Mahasiswa, on_delete=models.CASCADE)
    tanggal_pengajuan = models.DateTimeField(auto_now_add=True)  # menggantikan `created_at`
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    catatan_admin = models.TextField(blank=True, null=True)  # diganti dari `catatan` untuk konsistensi
    bidang_minat = models.CharField(max_length=100, blank=True, null=True)
    ipk = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    sks_lulus = models.PositiveIntegerField(blank=True, null=True)
    semester = models.PositiveSmallIntegerField(blank=True, null=True)
    persetujuan = models.BooleanField(default=False)
    keterangan = models.TextField(blank=True, null=True)
    tanggal_diperbarui = models.DateTimeField(auto_now=True)

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, 'Tidak diketahui')

    def __str__(self):
        return f"{self.judul} - {self.mahasiswa}"
    
class Notifikasi(models.Model):
    TIPE_CHOICES = (
        ('success', 'Sukses'),
        ('warning', 'Peringatan'),
        ('info', 'Info'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    judul = models.CharField(max_length=100)
    pesan = models.TextField()
    tipe = models.CharField(max_length=20, choices=TIPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return self.judul


    def __str__(self):
        return f"{self.mahasiswa.nama} - {self.judul}"
    
class Dosen(models.Model):
    nip = models.CharField(max_length=20, unique=True, verbose_name="NIP")
    nama = models.CharField(max_length=100, verbose_name="Nama Lengkap")
    email = models.EmailField(max_length=100, verbose_name="Email")
    spesialisasi = models.CharField(max_length=100, verbose_name="Spesialisasi")

    def __str__(self):
        return f"{self.nip} - {self.nama}"
