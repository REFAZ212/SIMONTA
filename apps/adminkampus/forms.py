# ===== apps/adminkampus/forms.py =====
from django import forms
from django.contrib.auth import get_user_model
from apps.mahasiswa.models import Mahasiswa
from apps.dosen.models import Dosen, User
from apps.core.models import JadwalPenting

User = get_user_model()

class MahasiswaForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    
    class Meta:
        model = Mahasiswa
        fields = ['nim', 'nama', 'jurusan', 'angkatan', 'ipk', 'sks_lulus', 'dosen_pembimbing']
        widgets = {
        'nim': forms.TextInput(attrs={'class': 'form-control'}),
        'nama': forms.TextInput(attrs={'class': 'form-control'}),
        'jurusan': forms.TextInput(attrs={'class': 'form-control'}),
        'angkatan': forms.NumberInput(attrs={'class': 'form-control'}),
        'ipk': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        'sks_lulus': forms.NumberInput(attrs={'class': 'form-control'}),
        'dosen_pembimbing': forms.TextInput(attrs={'class': 'form-control'}),
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Edit mode - populate user fields
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
            self.fields['password'].help_text = "Kosongkan jika tidak ingin mengubah password"
    
    def save(self, commit=True):
        mahasiswa = super().save(commit=False)
        
        if not mahasiswa.user:
            # Create new user
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'] or 'defaultpass123',
                role='mahasiswa',
                nim_nip=self.cleaned_data['nim']
            )
            mahasiswa.user = user
        else:
            # Update existing user
            user = mahasiswa.user
            user.username = self.cleaned_data['username']
            user.email = self.cleaned_data['email']
            if self.cleaned_data['password']:
                user.set_password(self.cleaned_data['password'])
            user.save()
        
        if commit:
            mahasiswa.save()
        return mahasiswa
    
SPESIALISASI_CHOICES = [
    ('uiux', 'UI/UX'),
    ('frontend', 'Front End'),
    ('backend', 'Back End'),
    ('fullstack', 'Full Stack'),
    ('dataanalyst', 'Data Analyst'),
    ('cybersecurity', 'Cyber Security'),
]

class DosenForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Dosen
        fields = ['nip', 'nama', 'spesialisasi', 'max_bimbingan']
        widgets = {
            'nip': forms.TextInput(attrs={'class': 'form-control'}),
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
            'spesialisasi': forms.Select(attrs={'class': 'form-select'}),  # gunakan ini saja
            'max_bimbingan': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'] or 'defaultpass123',
            role='dosen',
            nim_nip=self.cleaned_data['nip']
        )

        dosen = super().save(commit=False)
        dosen.user = user

        if commit:
            dosen.save()

        return dosen


class JadwalPentingForm(forms.ModelForm):
    class Meta:
        model = JadwalPenting
        fields = ['nama_jadwal', 'deskripsi', 'tanggal_mulai', 'tanggal_selesai', 'is_active']
        widgets = {
            'nama_jadwal': forms.TextInput(attrs={'class': 'form-control'}),
            'deskripsi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tanggal_mulai': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tanggal_selesai': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class PembagianDosenForm(forms.Form):
    mahasiswa = forms.ModelChoiceField(
        queryset=Mahasiswa.objects.filter(dosen_pembimbing__isnull=True),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    dosen = forms.ModelChoiceField(
        queryset=Dosen.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
