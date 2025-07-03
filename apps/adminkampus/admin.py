# apps/adminkampus/admin.py
from django.contrib import admin
from .models import Mahasiswa, SyaratTA
from .models import Dosen
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import path

@admin.register(Mahasiswa)
class MahasiswaAdmin(admin.ModelAdmin):
    list_display = ['nim', 'nama', 'jurusan', 'angkatan', 'ipk', 'sks_lulus', 'dosen_pembimbing']
    list_filter = ['jurusan', 'angkatan']
    search_fields = ['nim', 'nama', 'jurusan']
    ordering = ['nim']
    
    # Mengaktifkan aksi hapus
    actions = ['delete_selected']
    
    # Kustomisasi form
    fieldsets = (
        ('Data Mahasiswa', {
            'fields': ('nim', 'nama', 'jurusan', 'angkatan')
        }),
        ('Akademik', {
            'fields': ('ipk', 'sks_lulus', 'dosen_pembimbing')
        }),
    )
    
    # Mengizinkan hapus dari halaman detail
    def has_delete_permission(self, request, obj=None):
        return True

@admin.register(SyaratTA)
class SyaratTAAdmin(admin.ModelAdmin):
    list_display = ['min_ipk', 'min_sks', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']

@admin.register(Dosen)
class DosenAdmin(admin.ModelAdmin):
    list_display = ['nama', 'nip', 'email', 'aksi']
    
    def aksi(self, obj):
        from django.utils.html import format_html
        return format_html(
            '<a class="button" href="{}">Edit</a>&nbsp;'
            '<a class="button" href="{}" onclick="return confirm(\'Yakin ingin menghapus?\')">Hapus</a>',
            f'/admin/adminkampus/dosen/{obj.id}/change/',
            f'/admin/hapus-dosen/{obj.id}/'
        )
    aksi.short_description = 'Aksi'
    aksi.allow_tags = True
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('hapus-dosen/<int:dosen_id>/', self.hapus_dosen_view, name='hapus_dosen'),
        ]
        return custom_urls + urls
    
    def hapus_dosen_view(self, request, dosen_id):
        dosen = get_object_or_404(Dosen, id=dosen_id)
        if request.method == 'POST':
            nama_dosen = dosen.nama
            dosen.delete()
            messages.success(request, f'Dosen {nama_dosen} berhasil dihapus.')
        return redirect('/admin/adminkampus/dosen/')