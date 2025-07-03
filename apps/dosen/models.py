# apps/dosen/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import datetime, time
User = get_user_model()

class Spesialisasi(models.Model):
    nama = models.CharField(max_length=100, unique=True)
    deskripsi = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Spesialisasi"

    def __str__(self):
        return self.nama

class Dosen(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nip = models.CharField(max_length=50, unique=True)
    nama = models.CharField(max_length=150)
    spesialisasi = models.CharField(max_length=50, choices=[
        ('uiux', 'UI/UX'),
        ('frontend', 'Front End'),
        ('backend', 'Back End'),
        ('fullstack', 'Full Stack'),
        ('dataanalyst', 'Data Analyst'),
        ('cybersecurity', 'Cyber Security'),
    ])
    max_bimbingan = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = "Dosen"

    def __str__(self):
        return f"{self.nip} - {self.nama}"

    def current_bimbingan_count(self):
        return self.mahasiswa_set.count()

    def available_slots(self):
        return self.max_bimbingan - self.current_bimbingan_count()

class JadwalBimbingan(models.Model):
    
    HARI_CHOICES = [
        ('senin', 'Senin'),
        ('selasa', 'Selasa'),
        ('rabu', 'Rabu'),
        ('kamis', 'Kamis'),
        ('jumat', 'Jumat'),
        ('sabtu', 'Sabtu'),
        ('minggu', 'Minggu'),
    ]

    STATUS_CHOICES = [
        ('tersedia', 'Tersedia'),
        ('terisi', 'Terisi'),
        ('tidak_aktif', 'Tidak Aktif'),
    ]
    dosen = models.ForeignKey(User, on_delete=models.CASCADE, 
                            null=True,  # Hanya untuk development!
                            related_name='jadwal_bimbingan')
    hari = models.CharField(max_length=10, choices=HARI_CHOICES)
    jam_mulai = models.TimeField()
    jam_selesai = models.TimeField()
    tanggal = models.DateField(null=True, blank=True)
    kuota = models.PositiveIntegerField(default=1)
    ruangan = models.CharField(max_length=100, blank=True)
    keterangan = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='tersedia')
    is_recurring = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dosen.username} - {self.hari} ({self.jam_mulai}-{self.jam_selesai})"

    def clean(self):
        """Validasi yang tidak memerlukan akses ke dosen"""


        if self.jam_mulai >= self.jam_selesai:
            raise ValidationError('Jam mulai harus lebih kecil dari jam selesai')

        # Validasi overlap hanya jika dosen sudah ada
        overlapping = JadwalBimbingan.objects.filter(
            dosen=self.dosen,
            hari=self.hari,
            status='tersedia'
        ).exclude(pk=self.pk)

        if self.tanggal:
            overlapping = overlapping.filter(tanggal=self.tanggal)
        elif self.is_recurring:
            overlapping = overlapping.filter(is_recurring=True)

        for jadwal in overlapping:
            if (self.jam_mulai < jadwal.jam_selesai and
                self.jam_selesai > jadwal.jam_mulai):
                raise ValidationError('Jadwal bertabrakan dengan jadwal lain')

    def save(self, *args, **kwargs):
        # Pastikan dosen ada sebelum save
        if not self.dosen:
            raise ValueError("Instance JadwalBimbingan harus memiliki dosen")
        
        self.full_clean()
        super().save(*args, **kwargs)

class PendaftaranBimbingan(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Menunggu Konfirmasi'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
        ('completed', 'Selesai'),
        ('cancelled', 'Dibatalkan'),
    ]
    
    jadwal = models.ForeignKey(JadwalBimbingan, on_delete=models.CASCADE)
    mahasiswa = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'groups__name': 'Mahasiswa'}
    )
    tanggal_bimbingan = models.DateField()
    topik = models.CharField(max_length=200)
    deskripsi = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    catatan_dosen = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['jadwal', 'mahasiswa', 'tanggal_bimbingan']
        verbose_name = 'Pendaftaran Bimbingan'
        verbose_name_plural = 'Pendaftaran Bimbingan'
    
    def __str__(self):
        return f"{self.mahasiswa.get_full_name()} - {self.jadwal} ({self.tanggal_bimbingan})"

# Model Mahasiswa dihapus karena sudah ada di apps/mahasiswa
# Gunakan string reference 'mahasiswa.Mahasiswa' di PengajuanJudul

class PengajuanJudul(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
    ]
    
    # Gunakan string reference untuk menghindari circular import
    # Tambahkan related_name yang unik untuk menghindari konflik
    mahasiswa = models.ForeignKey(
        'mahasiswa.Mahasiswa', 
        on_delete=models.CASCADE,
        related_name='dosen_pengajuan_judul'
    )
    judul = models.CharField(max_length=255)
    tanggal_pengajuan = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    catatan = models.TextField(blank=True, null=True)

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status)

    def __str__(self):
        return self.judul