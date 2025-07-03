from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from apps.dosen.models import Dosen

User = get_user_model()


class Mahasiswa(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nim = models.CharField(max_length=20, unique=True)
    nama = models.CharField(max_length=100)
    jurusan = models.CharField(max_length=100)
    angkatan = models.IntegerField()
    ipk = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    sks_lulus = models.IntegerField(default=0)
    dosen_pembimbing = models.ForeignKey(Dosen, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name_plural = "Mahasiswa"

    def __str__(self):
        return f"{self.nama} ({self.nim})"

    def is_eligible_for_ta(self):
        return self.ipk >= 2.5 and self.sks_lulus >= 120


class PengajuanTA(models.Model):
    BIDANG_MINAT_CHOICES = [
        ('web_development', 'Web Development'),
        ('mobile_development', 'Mobile Development'),
        ('data_science', 'Data Science & Analytics'),
        ('artificial_intelligence', 'Artificial Intelligence'),
        ('cyber_security', 'Cyber Security'),
        ('game_development', 'Game Development'),
        ('network_systems', 'Network & Systems'),
        ('other', 'Lainnya'),
    ]

    SEMESTER_CHOICES = [
        ('7', 'Semester 7'),
        ('8', 'Semester 8'),
        ('9', 'Semester 9'),
        ('10', 'Semester 10+'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Menunggu Persetujuan'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
    ]

    mahasiswa = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pengajuan_ta')
    bidang_minat = models.CharField(max_length=50, choices=BIDANG_MINAT_CHOICES, default='other')
    keterangan = models.TextField(blank=True, default='', help_text='Minimal 50 karakter')
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES, default='7')
    ipk = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00), MaxValueValidator(4.00)])
    sks_lulus = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    persetujuan = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tanggal_pengajuan = models.DateTimeField(default=timezone.now)
    tanggal_diperbarui = models.DateTimeField(auto_now=True)
    catatan_admin = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Pengajuan Tugas Akhir'
        verbose_name_plural = 'Pengajuan Tugas Akhir'
        ordering = ['-tanggal_pengajuan']

    def __str__(self):
        return f"Pengajuan TA - {self.mahasiswa.username} ({self.get_status_display()})"

    def clean(self):
        if self.keterangan and len(self.keterangan.strip()) < 50:
            raise ValidationError({'keterangan': 'Keterangan harus minimal 50 karakter.'})
        if not self.persetujuan and self.pk is None:
            raise ValidationError({'persetujuan': 'Anda harus menyetujui pernyataan untuk melanjutkan.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class PengajuanJudul(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Menunggu Review'),
        ('reviewed', 'Sedang Direview'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
        ('revision', 'Perlu Revisi'),
    ]

    BIDANG_CHOICES = [
        ('artificial_intelligence', 'Artificial Intelligence'),
        ('machine_learning', 'Machine Learning'),
        ('web_development', 'Web Development'),
        ('mobile_development', 'Mobile Development'),
        ('data_science', 'Data Science'),
        ('cybersecurity', 'Cybersecurity'),
        ('network', 'Network & Infrastructure'),
        ('game_development', 'Game Development'),
        ('iot', 'Internet of Things (IoT)'),
        ('blockchain', 'Blockchain'),
        ('computer_vision', 'Computer Vision'),
        ('nlp', 'Natural Language Processing'),
        ('other', 'Lainnya'),
    ]

    METODOLOGI_CHOICES = [
        ('quantitative', 'Kuantitatif'),
        ('qualitative', 'Kualitatif'),
        ('mixed', 'Mixed Method'),
        ('experimental', 'Eksperimental'),
        ('case_study', 'Studi Kasus'),
        ('design_research', 'Design Research'),
        ('action_research', 'Action Research'),
    ]

    mahasiswa = models.ForeignKey(Mahasiswa, on_delete=models.CASCADE)
    dosen_pembimbing = models.ForeignKey(Dosen, null=True, blank=True, on_delete=models.SET_NULL)
    judul = models.CharField(max_length=150, blank=True, default='')
    judul_inggris = models.CharField(max_length=150, blank=True, default='')
    deskripsi = models.TextField(blank=True, default='')
    bidang_penelitian = models.CharField(max_length=50, choices=BIDANG_CHOICES, default='other')
    metodologi = models.CharField(max_length=50, choices=METODOLOGI_CHOICES, default='case_study')
    teknologi = models.TextField(blank=True, default='')
    latar_belakang = models.TextField(blank=True, default='')
    tujuan = models.TextField(blank=True, default='')
    manfaat = models.TextField(blank=True, default='')
    waktu_mulai = models.DateField(default=date.today)
    waktu_selesai = models.DateField(null=True, blank=True, help_text='Kosongkan jika belum ditentukan')
    rencana_kerja = models.TextField(blank=True, default='')
    catatan = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tanggal_pengajuan = models.DateTimeField(default=timezone.now)
    tanggal_review = models.DateTimeField(null=True, blank=True)
    tanggal_keputusan = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Pengajuan Judul Tugas Akhir'
        verbose_name_plural = 'Pengajuan Judul Tugas Akhir'
        ordering = ['-tanggal_pengajuan']

    def __str__(self):
        judul_display = self.judul if self.judul else "Judul belum diisi"
        return f"{self.mahasiswa.nama} - {judul_display[:50]}..."

    def get_status_display_color(self):
        colors = {
            'pending': 'warning',
            'reviewed': 'info',
            'approved': 'success',
            'rejected': 'danger',
            'revision': 'secondary',
        }
        return colors.get(self.status, 'secondary')

    def clean(self):
        if self.waktu_selesai and self.waktu_mulai and self.waktu_selesai <= self.waktu_mulai:
            raise ValidationError({'waktu_selesai': 'Waktu selesai harus setelah waktu mulai.'})

    def save(self, *args, **kwargs):
        if not self.waktu_selesai and self.waktu_mulai:
            self.waktu_selesai = self.waktu_mulai + timedelta(days=180)
        elif not self.waktu_selesai:
            self.waktu_selesai = date.today() + timedelta(days=180)
        super().save(*args, **kwargs)


class HistoryPengajuan(models.Model):
    pengajuan = models.ForeignKey(PengajuanJudul, on_delete=models.CASCADE, related_name='history')
    status_lama = models.CharField(max_length=20)
    status_baru = models.CharField(max_length=20)
    keterangan = models.TextField(blank=True, default='')
    tanggal_perubahan = models.DateTimeField(default=timezone.now)
    diubah_oleh = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-tanggal_perubahan']

    def __str__(self):
        return f"{self.pengajuan.mahasiswa.nama} - {self.status_lama} to {self.status_baru}"


class Notifikasi(models.Model):
    TIPE_CHOICES = (
        ('success', 'Sukses'),
        ('warning', 'Peringatan'),
        ('info', 'Info'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mahasiswa_notifikasi')
    judul = models.CharField(max_length=100, default='')
    pesan = models.TextField(default='')
    tipe = models.CharField(max_length=20, choices=TIPE_CHOICES, default='info')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.judul or f"Notifikasi untuk {self.user.username}"


class NilaiTA(models.Model):
    mahasiswa = models.ForeignKey(Mahasiswa, on_delete=models.CASCADE)
    dosen_penguji = models.ForeignKey(Dosen, on_delete=models.CASCADE)
    nilai_pembimbing = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    nilai_penguji1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    nilai_penguji2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    nilai_akhir = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    keterangan = models.TextField(blank=True, default='')
    tanggal_sidang = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Nilai TA"

    def __str__(self):
        return f"Nilai {self.mahasiswa.nama}"
