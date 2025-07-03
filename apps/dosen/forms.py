# ===== apps/dosen/forms.py =====
from django import forms
from .models import JadwalBimbingan
from apps.mahasiswa.models import Mahasiswa, NilaiTA
from django.core.exceptions import ValidationError
from .models import JadwalBimbingan, PendaftaranBimbingan
from datetime import datetime, time

class JadwalBimbinganForm(forms.ModelForm):
    class Meta:
        model = JadwalBimbingan
        fields = ['hari', 'jam_mulai', 'jam_selesai', 'tanggal', 'kuota', 'ruangan', 'keterangan', 'is_recurring']
        
        widgets = {
            'hari': forms.Select(attrs={'class': 'form-control', 'id': 'id_hari'}),
            'jam_mulai': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'id': 'id_jam_mulai'}),
            'jam_selesai': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'id': 'id_jam_selesai'}),
            'tanggal': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_tanggal'}),
            'kuota': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10', 'id': 'id_kuota'}),
            'ruangan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: R. 101 Gedung A', 'id': 'id_ruangan'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Keterangan tambahan (opsional)', 'id': 'id_keterangan'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_is_recurring'}),
        }
        labels = {
            'hari': 'Hari',
            'jam_mulai': 'Jam Mulai',
            'jam_selesai': 'Jam Selesai',
            'tanggal': 'Tanggal Spesifik',
            'kuota': 'Kuota Mahasiswa',
            'ruangan': 'Ruangan',
            'keterangan': 'Keterangan',
            'is_recurring': 'Jadwal Berulang Mingguan'
        }
        help_texts = {
            'tanggal': 'Kosongkan jika jadwal berulang mingguan',
            'kuota': 'Maksimal mahasiswa yang dapat mendaftar',
            'is_recurring': 'Centang jika jadwal ini berulang setiap minggu'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        jam_mulai = cleaned_data.get('jam_mulai')
        jam_selesai = cleaned_data.get('jam_selesai')
        tanggal = cleaned_data.get('tanggal')
        is_recurring = cleaned_data.get('is_recurring')

        if jam_mulai and jam_selesai:
            if jam_mulai >= jam_selesai:
                raise ValidationError('Jam mulai harus lebih kecil dari jam selesai')
            if jam_mulai < time(7, 0) or jam_selesai > time(17, 0):
                raise ValidationError('Jadwal harus dalam jam kerja (07:00 - 17:00)')

        if tanggal and tanggal < datetime.now().date():
            raise ValidationError('Tanggal tidak boleh di masa lampau')

        if is_recurring and tanggal:
            raise ValidationError('Jadwal berulang tidak memerlukan tanggal spesifik')
        elif not is_recurring and not tanggal:
            raise ValidationError('Jadwal tidak berulang memerlukan tanggal spesifik')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.dosen = self.user  # Set dosen sebelum save
        if commit:
            instance.save()
        return instance



class BulkJadwalForm(forms.Form):
    """Form untuk membuat jadwal dalam jumlah banyak"""
    hari = forms.MultipleChoiceField(
        choices=JadwalBimbingan.HARI_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Pilih Hari'
    )
    jam_mulai = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        label='Jam Mulai'
    )
    jam_selesai = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        label='Jam Selesai'
    )
    durasi_per_slot = forms.IntegerField(
        min_value=15,
        max_value=180,
        initial=60,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Durasi per Slot (menit)',
        help_text='Durasi setiap slot bimbingan dalam menit'
    )
    kuota = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Kuota per Slot'
    )
    ruangan = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Ruangan'
    )

    def clean(self):
        cleaned_data = super().clean()
        jam_mulai = cleaned_data.get('jam_mulai')
        jam_selesai = cleaned_data.get('jam_selesai')
        durasi = cleaned_data.get('durasi_per_slot')

        if jam_mulai and jam_selesai and durasi:
            if jam_mulai >= jam_selesai:
                raise ValidationError('Jam mulai harus lebih kecil dari jam selesai')
            
            total_menit = (datetime.combine(datetime.today(), jam_selesai) - 
                          datetime.combine(datetime.today(), jam_mulai)).seconds / 60
            
            if total_menit < durasi:
                raise ValidationError('Durasi slot terlalu besar untuk rentang waktu yang dipilih')

        return cleaned_data


class PendaftaranBimbinganForm(forms.ModelForm):
    class Meta:
        model = PendaftaranBimbingan
        fields = ['topik', 'deskripsi', 'tanggal_bimbingan']
        widgets = {
            'topik': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Topik yang ingin didiskusikan'
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Jelaskan detail topik yang ingin didiskusikan'
            }),
            'tanggal_bimbingan': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }

    def __init__(self, *args, **kwargs):
        self.jadwal = kwargs.pop('jadwal', None)
        super().__init__(*args, **kwargs)
        
        if self.jadwal and not self.jadwal.is_recurring:
            # Jika jadwal tidak berulang, set tanggal otomatis
            self.fields['tanggal_bimbingan'].initial = self.jadwal.tanggal
            self.fields['tanggal_bimbingan'].widget.attrs['readonly'] = True

    def clean_tanggal_bimbingan(self):
        tanggal = self.cleaned_data['tanggal_bimbingan']
        
        if tanggal < datetime.now().date():
            raise ValidationError('Tanggal bimbingan tidak boleh di masa lampau')
        
        if self.jadwal and self.jadwal.is_recurring:
            # Validasi hari untuk jadwal berulang
            hari_indonesia = ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu']
            hari_tanggal = hari_indonesia[tanggal.weekday()]
            
            if hari_tanggal != self.jadwal.hari:
                raise ValidationError(f'Tanggal harus jatuh pada hari {self.jadwal.get_hari_display()}')
        
        return tanggal

class NilaiTAForm(forms.ModelForm):
    class Meta:
        model = NilaiTA
        fields = ['nilai_pembimbing', 'nilai_penguji1', 'nilai_penguji2', 'keterangan', 'tanggal_sidang']
        widgets = {
            'nilai_pembimbing': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'nilai_penguji1': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'nilai_penguji2': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tanggal_sidang': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Hitung nilai rata-rata
        nilai_list = [
            instance.nilai_pembimbing or 0,
            instance.nilai_penguji1 or 0,
            instance.nilai_penguji2 or 0
        ]
        valid_scores = [n for n in nilai_list if n > 0]
        if valid_scores:
            instance.nilai_akhir = sum(valid_scores) / len(valid_scores)
        
        if commit:
            instance.save()
        return instance