# ===== apps/mahasiswa/forms.py =====
from django import forms
from .models import PengajuanTA, PengajuanJudul
from django.contrib.auth import get_user_model

User = get_user_model()

class PengajuanTAForm(forms.ModelForm):
    class Meta:
        model = PengajuanTA
        exclude = ['mahasiswa']
        fields = [
            'bidang_minat',
            'keterangan', 
            'semester',
            'ipk',
            'sks_lulus',
            'persetujuan'
        ]
        widgets = {
            'bidang_minat': forms.Select(attrs={
                'class': 'form-control'
            }),
            'keterangan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Jelaskan alasan dan rencana penelitian Anda (minimal 50 karakter)'
            }),
            'semester': forms.Select(attrs={
                'class': 'form-control'
            }),
            'ipk': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.00',
                'max': '4.00'
            }),
            'sks_lulus': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'persetujuan': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def clean_keterangan(self):
        keterangan = self.cleaned_data.get('keterangan', '')
        if keterangan and len(keterangan.strip()) < 50:
            raise forms.ValidationError('Keterangan harus minimal 50 karakter.')
        return keterangan

    def clean_persetujuan(self):
        persetujuan = self.cleaned_data.get('persetujuan')
        if not persetujuan:
            raise forms.ValidationError('Anda harus menyetujui pernyataan untuk melanjutkan.')
        return persetujuan

class PengajuanJudulForm(forms.ModelForm):
    class Meta:
        model = PengajuanJudul
        fields = [
            'judul',
            'judul_inggris',
            'deskripsi',
            'bidang_penelitian',
            'metodologi',
            'teknologi',
            'latar_belakang',
            'tujuan',
            'manfaat',
            'waktu_mulai',
            'waktu_selesai',
            'rencana_kerja',
            'catatan'
        ]
        widgets = {
            'judul': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan judul penelitian'
            }),
            'judul_inggris': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter research title in English'
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Berikan deskripsi singkat tentang penelitian'
            }),
            'bidang_penelitian': forms.Select(attrs={
                'class': 'form-control'
            }),
            'metodologi': forms.Select(attrs={
                'class': 'form-control'
            }),
            'teknologi': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Sebutkan teknologi, tools, atau framework yang akan digunakan'
            }),
            'latar_belakang': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Jelaskan latar belakang masalah yang akan diteliti'
            }),
            'tujuan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Sebutkan tujuan yang ingin dicapai dari penelitian ini'
            }),
            'manfaat': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Jelaskan manfaat yang diharapkan dari penelitian ini'
            }),
            'waktu_mulai': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'waktu_selesai': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'rencana_kerja': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Outline rencana kerja atau timeline penelitian'
            }),
            'catatan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Catatan tambahan (opsional)'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        waktu_mulai = cleaned_data.get('waktu_mulai')
        waktu_selesai = cleaned_data.get('waktu_selesai')
        
        if waktu_mulai and waktu_selesai and waktu_selesai <= waktu_mulai:
            raise forms.ValidationError({
                'waktu_selesai': 'Waktu selesai harus setelah waktu mulai.'
            })
        
        return cleaned_data

    def clean_judul(self):
        judul = self.cleaned_data.get('judul', '')
        if judul and len(judul.strip()) < 10:
            raise forms.ValidationError('Judul harus minimal 10 karakter.')
        return judul