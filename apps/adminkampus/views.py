# ===== apps/adminkampus/views.py =====
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.db import models
from apps.users.models import User
from apps.mahasiswa.models import Mahasiswa, PengajuanTA, Notifikasi
from apps.dosen.models import Dosen, Spesialisasi
from apps.core.models import JadwalPenting, Notifikasi
from .forms import MahasiswaForm, DosenForm, JadwalPentingForm, PembagianDosenForm
import openpyxl
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_POST
import json
from datetime import datetime


@login_required
def dashboard(request):
    if not request.user.is_admin():
        raise Http404("Akses ditolak")
    
    # Statistik untuk dashboard
    total_mahasiswa = Mahasiswa.objects.count()
    total_dosen = Dosen.objects.count()
    pengajuan_pending = PengajuanTA.objects.filter(status='pending').count()
    
    # Ganti 'created_at' dengan 'tanggal_pengajuan'
    recent_pengajuan = PengajuanTA.objects.order_by('-tanggal_pengajuan')[:5]
    
    context = {
        'total_mahasiswa': total_mahasiswa,
        'total_dosen': total_dosen,
        'pengajuan_pending': pengajuan_pending,
        'recent_pengajuan': recent_pengajuan,
    }
    return render(request, 'adminkampus/dashboard.html', context)

@login_required
def manage_mahasiswa(request):
    if not request.user.is_admin:
        raise Http404("Akses ditolak")
    
    mahasiswa_list = Mahasiswa.objects.all().order_by('nama')
    return render(request, 'adminkampus/manage_mahasiswa.html', {'mahasiswa_list': mahasiswa_list})

@login_required
def tambah_mahasiswa(request):
    if not request.user.is_admin:
        raise Http404("Akses ditolak")

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        nim = request.POST.get('nim')
        nama = request.POST.get('nama')
        jurusan = request.POST.get('jurusan')
        angkatan = request.POST.get('angkatan')
        ipk = request.POST.get('ipk') or 0
        sks_lulus = request.POST.get('sks_lulus') or 0
        dosen_id = request.POST.get('dosen_pembimbing')

        # 1. Buat user baru
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah digunakan.")
            return redirect('adminkampus:tambah_mahasiswa')

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
        )

        # 2. Cari dosen jika ada
        dosen = Dosen.objects.filter(id=dosen_id).first() if dosen_id else None

        # 3. Simpan mahasiswa dan hubungkan dengan user
        Mahasiswa.objects.create(
            user=user,
            nim=nim,
            nama=nama,
            jurusan=jurusan,
            angkatan=angkatan,
            ipk=ipk,
            sks_lulus=sks_lulus,
            dosen_pembimbing=dosen
        )

        messages.success(request, "Mahasiswa berhasil ditambahkan!")
        return redirect('adminkampus:manage_mahasiswa')

    # Ambil data dosen untuk dropdown
    dosen_list = Dosen.objects.all()
    return render(request, 'adminkampus/form_mahasiswa.html', {'title': 'Tambah Mahasiswa', 'dosen_list': dosen_list})
@login_required
def edit_mahasiswa(request, mahasiswa_id):
    # Cek apakah user adalah admin
    if not request.user.is_admin:
        raise Http404("Akses ditolak")
    
    # Ambil data mahasiswa berdasarkan ID
    mahasiswa = get_object_or_404(Mahasiswa, id=mahasiswa_id)
    
    if request.method == 'POST':
        # Ketika form disubmit, kirim instance mahasiswa yang akan diedit
        form = MahasiswaForm(request.POST, instance=mahasiswa)
        if form.is_valid():
            form.save()
            messages.success(request, "Data mahasiswa berhasil diupdate!")
            return redirect('adminkampus:manage_mahasiswa')
        # Jika form tidak valid, akan render ulang dengan error
    else:
        # Ketika GET request, tampilkan form dengan data mahasiswa yang sudah ada
        form = MahasiswaForm(instance=mahasiswa)
    
    # Render template dengan context yang lengkap
    context = {
        'form': form,
        'title': 'Edit Mahasiswa',
        'mahasiswa': mahasiswa,  # Tambahkan data mahasiswa ke context
        'is_edit': True,  # Flag untuk membedakan edit vs tambah
    }
    
    return render(request, 'adminkampus/form_mahasiswa.html', context)
@login_required
def delete_mahasiswa(request, mahasiswa_id):
    if not request.user.is_admin:
        raise Http404("Akses ditolak")
    
    mahasiswa = get_object_or_404(Mahasiswa, id=mahasiswa_id)
    
    if request.method == 'POST':
        nama = mahasiswa.nama
        nim = mahasiswa.nim
        try:
            mahasiswa.delete()
            messages.success(request, f'Data mahasiswa {nama} ({nim}) berhasil dihapus!')
        except Exception as e:
            messages.error(request, f'Gagal menghapus data mahasiswa: {str(e)}')
        
    # Jika GET request, redirect ke list (karena kita pakai modal)
    return redirect('adminkampus:manage_mahasiswa')

@login_required
def manage_dosen(request):
    if not request.user.is_admin():
        raise Http404("Akses ditolak")
    
    dosen_list = Dosen.objects.all().order_by('nama')
    return render(request, 'adminkampus/manage_dosen.html', {'dosen_list': dosen_list})

@login_required
def tambah_dosen(request):
    if not request.user.is_admin():
        raise Http404("Akses ditolak")
    
    if request.method == 'POST':
        form = DosenForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Dosen berhasil ditambahkan!")
            return redirect('adminkampus:manage_dosen')
    else:
        form = DosenForm()
    
    return render(request, 'adminkampus/form_dosen.html', {'form': form, 'title': 'Tambah Dosen'})\

def edit_dosen(request, dosen_id):
    # Implementasi edit dosen
    pass

def hapus_dosen(request, dosen_id):
    """
    View untuk menghapus data dosen
    """
    dosen = get_object_or_404(Dosen, id=dosen_id)
    
    if request.method == 'POST':
        nama_dosen = dosen.nama  # Simpan nama untuk pesan
        dosen.delete()
        messages.success(request, f'Dosen {nama_dosen} berhasil dihapus.')
        return redirect('admin:adminkampus_dosen_changelist')  # Redirect ke list dosen
    
    # Jika GET request, tampilkan konfirmasi
    context = {
        'dosen': dosen,
        'title': 'Hapus Dosen'
    }
    return render(request, 'admin/hapus_dosen_confirm.html', context)


@login_required
@require_POST
def review_pengajuan(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Akses ditolak'}, status=403)

    try:
        data = json.loads(request.body)
        pengajuan_id = data.get('id')
        action = data.get('action')
        note = data.get('note', '')

        pengajuan = get_object_or_404(PengajuanTA, id=pengajuan_id)

        if action not in ['approve', 'reject']:
            return JsonResponse({'success': False, 'message': 'Invalid action'}, status=400)

        if action == 'reject' and not note:
            return JsonResponse({'success': False, 'message': 'Catatan wajib diisi untuk penolakan'}, status=400)

        pengajuan.status = action if action == 'approve' else 'rejected'
        pengajuan.catatan_admin = note
        pengajuan.save()

        # Notifikasi
        Notifikasi.objects.create(
            judul=f"Status Pengajuan TA: {pengajuan.status.title()}",
            pesan=f"Pengajuan TA Anda dengan judul '{pengajuan.judul}' telah {pengajuan.get_status_display().lower()}. {note}",
            user=pengajuan.mahasiswa.user,
            tipe='success' if action == 'approve' else 'warning'
        )

        return JsonResponse({
            'success': True,
            'message': f"Pengajuan berhasil {pengajuan.get_status_display().lower()}",
            'status': pengajuan.status,
            'status_display': pengajuan.get_status_display()
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@require_POST
def bulk_review_pengajuan(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Akses ditolak'}, status=403)

    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        action = data.get('action')
        note = data.get('note', '')

        if not ids:
            return JsonResponse({'success': False, 'message': 'Tidak ada pengajuan yang dipilih'}, status=400)

        if action not in ['approve', 'reject']:
            return JsonResponse({'success': False, 'message': 'Invalid action'}, status=400)

        if action == 'reject' and not note:
            return JsonResponse({'success': False, 'message': 'Catatan wajib diisi untuk penolakan massal'}, status=400)

        pengajuan_list = PengajuanTA.objects.filter(id__in=ids)
        count = 0

        for pengajuan in pengajuan_list:
            pengajuan.status = action if action == 'approve' else 'rejected'
            pengajuan.catatan_admin = note
            pengajuan.save()

            Notifikasi.objects.create(
                judul=f"Status Pengajuan TA: {pengajuan.status.title()}",
                pesan=f"Pengajuan TA Anda dengan judul '{pengajuan.judul}' telah {pengajuan.get_status_display().lower()}. {note}",
                user=pengajuan.mahasiswa.user,
                tipe='success' if action == 'approve' else 'warning'
            )
            count += 1

        return JsonResponse({
            'success': True,
            'message': f"{count} pengajuan berhasil {action}"
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
def pengajuan_ta_list(request):
    if not request.user.is_admin():
        raise Http404("Akses ditolak")

    # Ganti 'created_at' ke 'tanggal_pengajuan' karena field tersebut tersedia
    pengajuan_list = PengajuanTA.objects.all().order_by('-tanggal_pengajuan')
    return render(request, 'adminkampus/pengajuan_ta_list.html', {'pengajuan_list': pengajuan_list})


@login_required
def approve_pengajuan(request, pengajuan_id):
    if not request.user.is_admin():
        raise Http404("Akses ditolak")

    pengajuan = get_object_or_404(PengajuanTA, id=pengajuan_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        catatan = request.POST.get('catatan', '')

        if action == 'approve':
            pengajuan.status = 'approved'
            messages.success(request, "Pengajuan berhasil disetujui!")
        elif action == 'reject':
            pengajuan.status = 'rejected'
            messages.info(request, "Pengajuan ditolak!")

        pengajuan.catatan_admin = catatan
        pengajuan.save()

        Notifikasi.objects.create(
            judul=f"Status Pengajuan TA: {pengajuan.status.title()}",
            pesan=f"Pengajuan TA Anda dengan judul '{pengajuan.judul}' telah {pengajuan.get_status_display().lower()}. {catatan}",
            user=pengajuan.mahasiswa.user,
            tipe='success' if action == 'approve' else 'warning'
        )

        return redirect('adminkampus:pengajuan_ta_list')

    return render(request, 'adminkampus/approve_pengajuan.html', {'pengajuan': pengajuan})
@login_required
def manage_jadwal_penting(request):
    if not request.user.is_admin():
        raise Http404("Akses ditolak")
    
    jadwal_list = JadwalPenting.objects.all().order_by('-tanggal_mulai')
    return render(request, 'adminkampus/manage_jadwal_penting.html', {
        'jadwal_list': jadwal_list
    })

@login_required
def tambah_jadwal_penting(request):
    if not request.user.is_admin():
        raise Http404("Akses ditolak")
    
    if request.method == 'POST':
        form = JadwalPentingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Jadwal penting berhasil ditambahkan!")
            return redirect('adminkampus:manage_jadwal_penting')
    else:
        form = JadwalPentingForm()

    return render(request, 'adminkampus/form_jadwal_penting.html', {
        'form': form,
        'judul': 'Buat Jadwal Penting'
    })

@login_required
def edit_jadwal_penting(request, pk):
    if not request.user.is_admin():
        raise Http404("Akses ditolak")

    jadwal = get_object_or_404(JadwalPenting, pk=pk)

    if request.method == 'POST':
        form = JadwalPentingForm(request.POST, instance=jadwal)
        if form.is_valid():
            form.save()
            messages.success(request, "Jadwal penting berhasil diperbarui!")
            return redirect('adminkampus:manage_jadwal_penting')
    else:
        form = JadwalPentingForm(instance=jadwal)

    return render(request, 'adminkampus/form_jadwal_penting.html', {
        'form': form,
        'judul': 'Edit Jadwal Penting'
    })

@login_required
def hapus_jadwal_penting(request, pk):
    if not request.user.is_admin():
        raise Http404("Akses ditolak")

    jadwal = get_object_or_404(JadwalPenting, pk=pk)
    jadwal.delete()
    messages.success(request, "Jadwal penting berhasil dihapus.")
    return redirect('adminkampus:manage_jadwal_penting')

@login_required
def pembagian_dosen(request):
    if not request.user.is_admin():
        raise Http404("Akses ditolak")

    if request.method == 'POST':
        form = PembagianDosenForm(request.POST)
        if form.is_valid():
            mahasiswa = form.cleaned_data['mahasiswa']
            dosen = form.cleaned_data['dosen']
            mahasiswa.dosen_pembimbing = dosen
            mahasiswa.save()
            messages.success(request, f"{mahasiswa.nama} berhasil dipasangkan dengan {dosen.nama}")
            return redirect('adminkampus:pembagian_dosen')
    else:
        form = PembagianDosenForm()

    return render(request, 'adminkampus/pembagian_dosen.html', {'form': form})
@login_required
def laporan(request):
    if not request.user.is_admin():
        raise Http404("Akses ditolak")

    total_mahasiswa = Mahasiswa.objects.count()
    total_dosen = Dosen.objects.count()
    mahasiswa_tanpa_dosen = Mahasiswa.objects.filter(dosen_pembimbing__isnull=True)

    if request.GET.get('export') == 'excel':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Laporan"

        ws.append(["NIM", "Nama", "Jurusan", "Angkatan", "IPK", "Sks Lulus", "Dosen Pembimbing"])
        for mhs in mahasiswa_tanpa_dosen:
            ws.append([mhs.nim, mhs.nama, mhs.jurusan, mhs.angkatan, float(mhs.ipk), mhs.sks_lulus, mhs.dosen_pembimbing.nama if mhs.dosen_pembimbing else "-"])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = f"Laporan_Mahasiswa_{timezone.now().date()}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response

    context = {
        'total_mahasiswa': total_mahasiswa,
        'total_dosen': total_dosen,
        'mahasiswa_tanpa_dosen': mahasiswa_tanpa_dosen,
    }

    return render(request, 'adminkampus/laporan.html', context)


@login_required
def pengaturan(request):
    """
    Main admin settings page view
    """
    # Get system statistic
    context = {
        
    }
    
    return render(request, 'adminkampus/pengaturan.html', context)





