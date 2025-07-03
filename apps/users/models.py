# ===== apps/users/models.py =====
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin Kampus'),
        ('dosen', 'Dosen'),
        ('mahasiswa', 'Mahasiswa'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='mahasiswa')
    nim_nip = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_dosen(self):
        return self.role == 'dosen'
    
    def is_mahasiswa(self):
        return self.role == 'mahasiswa'
