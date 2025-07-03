# ===== apps/dosen/views.py =====
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from .models import Dosen, JadwalBimbingan
from apps.mahasiswa.models import Mahasiswa, NilaiTA
from .forms import JadwalBimbinganForm, NilaiTAForm
from apps.mahasiswa.models import Mahasiswa, PengajuanJudul, Notifikasi
from django.contrib.auth import get_user_model
# apps/dosen/views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta, time
from .models import JadwalBimbingan, PendaftaranBimbingan
from .forms import JadwalBimbinganForm, BulkJadwalForm
import json
from django.views.decorators.http import require_http_methods
import logging
from django.core.exceptions import ValidationError
from django.conf import settings

@login_required
def dashboard(request):
    if not request.user.is_dosen():
        raise Http404("Akses ditolak")
    
    try:
        dosen = request.user.dosen
    except Dosen.DoesNotExist:
        messages.error(request, "Profil dosen belum dibuat. Hubungi admin.")
        return redirect('dosen:dashboard')
    
    # Data untuk dashboard
    mahasiswa_bimbingan = Mahasiswa.objects.filter(dosen_pembimbing=dosen)
    
    # PERBAIKAN: Karena field dosen di JadwalBimbingan adalah ForeignKey ke User
    jadwal_bimbingan = JadwalBimbingan.objects.filter(dosen=request.user).order_by('-created_at')[:5]
    
    context = {
        'dosen': dosen,
        'mahasiswa_bimbingan': mahasiswa_bimbingan,
        'jadwal_bimbingan': jadwal_bimbingan,
    }
    return render(request, 'dosen/dashboard.html', context)

@login_required
def buat_jadwal(request):
    # Pastikan user adalah dosen
    if not request.user.is_dosen():
        raise Http404("Akses ditolak")

    if request.method == 'POST':
        form = JadwalBimbinganForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                jadwal = form.save()
                messages.success(request, 'Jadwal berhasil dibuat!')
                return redirect('dosen:daftar_jadwal')
            except Exception as e:
                messages.error(request, f'Gagal menyimpan jadwal: {str(e)}')
        else:
            messages.error(request, 'Terdapat kesalahan dalam form. Silakan periksa kembali.')
    else:
        form = JadwalBimbinganForm(user=request.user)

    context = {
        'form': form,
        'title': 'Buat Jadwal Bimbingan'
    }
    return render(request, 'dosen/buat_jadwal.html', context)

@login_required
def daftar_jadwal(request):
    """
    View untuk menampilkan daftar jadwal bimbingan
    dengan debug info untuk troubleshooting
    """
    user = request.user
    
    # Debug: Print informasi untuk troubleshooting
    print(f"User: {user.username}")
    print(f"User ID: {user.id}")
    
    # Cek apakah user memiliki method is_dosen
    try:
        is_dosen = user.is_dosen() if hasattr(user, 'is_dosen') else True
        print(f"Is Dosen: {is_dosen}")
    except:
        is_dosen = True  # Default untuk development
        print("Method is_dosen() tidak ditemukan, menggunakan default True")
    
    # Ambil semua jadwal yang dibuat oleh user ini
    jadwal_list = JadwalBimbingan.objects.filter(dosen=user).order_by('-created_at', 'hari', 'jam_mulai')
    
    # Debug: Print jumlah jadwal yang ditemukan
    print(f"Jumlah jadwal ditemukan: {jadwal_list.count()}")
    
    # Debug: Print detail setiap jadwal
    for i, jadwal in enumerate(jadwal_list):
        print(f"Jadwal {i+1}: {jadwal.hari} {jadwal.jam_mulai}-{jadwal.jam_selesai} (ID: {jadwal.id}, Dosen: {jadwal.dosen.username})")
    
    context = {
        'jadwal_list': jadwal_list,
        'debug': settings.DEBUG,  # Tampilkan debug info hanya di development
        'user': user,
    }
    
    return render(request, 'dosen/daftar_jadwal.html', context)



@login_required
@user_passes_test(lambda u: u.is_dosen())  # PERBAIKAN: Gunakan lambda function
def buat_jadwal_bulk(request):
    """View untuk membuat jadwal dalam jumlah banyak"""
    if request.method == 'POST':
        form = BulkJadwalForm(request.POST)
        if form.is_valid():
            created_count = 0
            hari_list = form.cleaned_data['hari']
            jam_mulai = form.cleaned_data['jam_mulai']
            jam_selesai = form.cleaned_data['jam_selesai']
            durasi = form.cleaned_data['durasi_per_slot']
            kuota = form.cleaned_data['kuota']
            ruangan = form.cleaned_data['ruangan']
            
            # Hitung jumlah slot berdasarkan durasi
            total_menit = (datetime.combine(datetime.today(), jam_selesai) - 
                          datetime.combine(datetime.today(), jam_mulai)).seconds / 60
            jumlah_slot = int(total_menit // durasi)
            
            for hari in hari_list:
                current_time = jam_mulai
                for i in range(jumlah_slot):
                    slot_mulai = current_time
                    slot_selesai = (datetime.combine(datetime.today(), current_time) + 
                                   timedelta(minutes=durasi)).time()
                    
                    # Cek apakah jadwal sudah ada
                    existing = JadwalBimbingan.objects.filter(
                        dosen=request.user,  # SUDAH BENAR: menggunakan request.user
                        hari=hari,
                        jam_mulai=slot_mulai,
                        jam_selesai=slot_selesai,
                        is_recurring=True
                    ).exists()
                    
                    if not existing:
                        JadwalBimbingan.objects.create(
                            dosen=request.user,  # SUDAH BENAR: menggunakan request.user
                            hari=hari,
                            jam_mulai=slot_mulai,
                            jam_selesai=slot_selesai,
                            kuota=kuota,
                            ruangan=ruangan,
                            is_recurring=True,
                            status='tersedia'
                        )
                        created_count += 1
                    
                    current_time = slot_selesai
            
            messages.success(request, f'{created_count} jadwal berhasil dibuat!')
            return redirect('dosen:daftar_jadwal')
    else:
        form = BulkJadwalForm()
    
    context = {
        'form': form,
        'title': 'Buat Jadwal Bulk',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': 'dosen:dashboard'},
            {'name': 'Jadwal Bimbingan', 'url': 'dosen:daftar_jadwal'},
            {'name': 'Buat Jadwal Bulk', 'url': None}
        ]
    }
    return render(request, 'dosen/buat_jadwal_bulk.html', context)

@login_required
def edit_jadwal(request, pk):
    """
    View untuk mengedit jadwal bimbingan
    """
    jadwal = get_object_or_404(JadwalBimbingan, pk=pk, dosen=request.user)
    
    if request.method == 'POST':
        form = JadwalBimbinganForm(request.POST, instance=jadwal, user=request.user)
        if form.is_valid():
            try:
                jadwal = form.save()
                messages.success(request, 'Jadwal berhasil diperbarui!')
                return redirect('dosen:daftar_jadwal')
            except Exception as e:
                messages.error(request, f'Gagal memperbarui jadwal: {str(e)}')
        else:
            messages.error(request, 'Terdapat kesalahan dalam form. Silakan periksa kembali.')
    else:
        form = JadwalBimbinganForm(instance=jadwal, user=request.user)
    
    context = {
        'form': form,
        'jadwal': jadwal,
        'title': 'Edit Jadwal Bimbingan'
    }
    return render(request, 'dosen/edit_jadwal.html', context)

@login_required
def delete_jadwal(request, pk):
    """
    View untuk menghapus jadwal bimbingan
    """
    jadwal = get_object_or_404(JadwalBimbingan, pk=pk, dosen=request.user)
    
    if request.method == 'POST':
        jadwal_info = f"{jadwal.hari} {jadwal.jam_mulai}-{jadwal.jam_selesai}"
        jadwal.delete()
        messages.success(request, f'Jadwal {jadwal_info} berhasil dihapus!')
        return redirect('dosen:daftar_jadwal')
    

@login_required
@user_passes_test(Dosen)
def detail_jadwal(request, jadwal_id):
    """View untuk melihat detail jadwal dan pendaftaran"""
    jadwal = get_object_or_404(JadwalBimbingan, id=jadwal_id, dosen=request.user)
    
    # Ambil pendaftaran untuk jadwal ini
    pendaftaran_list = PendaftaranBimbingan.objects.filter(jadwal=jadwal)
    
    # Filter berdasarkan status
    status_filter = request.GET.get('status')
    if status_filter:
        pendaftaran_list = pendaftaran_list.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(pendaftaran_list, 10)
    page_number = request.GET.get('page')
    pendaftaran_page = paginator.get_page(page_number)
    
    context = {
        'jadwal': jadwal,
        'pendaftaran_page': pendaftaran_page,
        'status_choices': PendaftaranBimbingan.STATUS_CHOICES,
        'current_status': status_filter,
        'title': f'Detail Jadwal - {jadwal}',
        'breadcrumb': [
            {'name': 'Dashboard', 'url': 'dosen:dashboard'},
            {'name': 'Jadwal Bimbingan', 'url': 'dosen:daftar_jadwal'},
            {'name': 'Detail Jadwal', 'url': None}
        ]
    }
    return render(request, 'dosen/detail_jadwal.html', context)

@login_required
@user_passes_test(Dosen) 
def toggle_status_jadwal(request, jadwal_id):
    """AJAX view untuk toggle status jadwal"""
    if request.method == 'POST':
        jadwal = get_object_or_404(JadwalBimbingan, id=jadwal_id, dosen=request.user)
        
        if jadwal.status == 'tersedia':
            jadwal.status = 'tidak_aktif'
        else:
            jadwal.status = 'tersedia'
        
        jadwal.save()
        
        return JsonResponse({
            'success': True,
            'new_status': jadwal.status,
            'status_display': jadwal.get_status_display()
        })
    
    return JsonResponse({'success': False})

@login_required
@user_passes_test(Dosen)
def update_status_pendaftaran(request, pendaftaran_id):
    """View untuk update status pendaftaran bimbingan"""
    pendaftaran = get_object_or_404(PendaftaranBimbingan, id=pendaftaran_id, jadwal__dosen=request.user)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        catatan = request.POST.get('catatan', '')
        
        if status in ['approved', 'rejected', 'completed']:
            pendaftaran.status = status
            pendaftaran.catatan_dosen = catatan
            pendaftaran.save()
            
            messages.success(request, f'Status pendaftaran berhasil diubah menjadi {pendaftaran.get_status_display()}')
        else:
            messages.error(request, 'Status tidak valid!')
    
    return redirect('dosen:detail_jadwal', jadwal_id=pendaftaran.jadwal.id)

# apps/dosen/views.py
@login_required
def nilai_mahasiswa_dummy(request):
    # Halaman kosong / placeholder penilaian
    return render(request, 'dosen/nilai_mahasiswa.html', {'mahasiswa_id': None})


@login_required
def pengajuan_judul_list(request):
    if not request.user.is_dosen():
        raise Http404("Akses ditolak")
    
    PengajuanJudul.objects.filter(dosen_pembimbing=request.user.dosen)

    return render(request, 'dosen/pengajuan_judul_list.html', {'pengajuan_list': pengajuan_judul_list})


@login_required
def review_pengajuan_list(request):
    """
    View untuk menampilkan daftar pengajuan judul yang perlu direview oleh dosen
    """
    # Pastikan user adalah dosen
    try:
        dosen = Dosen.objects.get(user=request.user)
    except Dosen.DoesNotExist:
        messages.error(request, 'Anda tidak memiliki akses sebagai dosen.')
        return redirect('dashboard')  # Redirect ke dashboard umum
    
    # Ambil pengajuan yang ditujukan untuk dosen ini
    pengajuan_queryset = PengajuanJudul.objects.filter(
        dosen_pembimbing=dosen
    ).select_related('mahasiswa', 'dosen_pembimbing')
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        pengajuan_queryset = pengajuan_queryset.filter(
            Q(mahasiswa__nim__icontains=search_query) |
            Q(mahasiswa__nama__icontains=search_query) |
            Q(judul__icontains=search_query)
        )
    
    # Handle status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        pengajuan_queryset = pengajuan_queryset.filter(status=status_filter)
    
    # Handle date filter
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    if start_date:
        pengajuan_queryset = pengajuan_queryset.filter(tanggal_pengajuan__date__gte=start_date)
    if end_date:
        pengajuan_queryset = pengajuan_queryset.filter(tanggal_pengajuan__date__lte=end_date)
    
    # Handle sorting
    sort_by = request.GET.get('sort', '-tanggal_pengajuan')
    pengajuan_queryset = pengajuan_queryset.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(pengajuan_queryset, 10)  # 10 items per page
    page_number = request.GET.get('page')
    pengajuan_list = paginator.get_page(page_number)
    
    # Hitung statistik
    all_pengajuan = PengajuanJudul.objects.filter(dosen_pembimbing=dosen)
    stats = {
        'pending_count': all_pengajuan.filter(status='pending').count(),
        'approved_count': all_pengajuan.filter(status='approved').count(),
        'rejected_count': all_pengajuan.filter(status='rejected').count(),
        'total_count': all_pengajuan.count(),
    }
    
    context = {
        'pengajuan_list': pengajuan_list,
        'is_paginated': pengajuan_list.has_other_pages(),
        'page_obj': pengajuan_list,
        'search_query': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        **stats,  # Unpack stats ke context
    }
    
    return render(request, 'dosen/review_pengajuan.html', context)

@login_required
def detail_pengajuan(request, pengajuan_id):
    """
    Ajax view untuk mendapatkan detail pengajuan
    """
    try:
        dosen = Dosen.objects.get(user=request.user)
    except Dosen.DoesNotExist:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    pengajuan = get_object_or_404(
        PengajuanJudul, 
        id=pengajuan_id, 
        dosen_pembimbing=dosen
    )
    
    data = {
        'id': pengajuan.id,
        'mahasiswa': {
            'nama': pengajuan.mahasiswa.nama,
            'nim': pengajuan.mahasiswa.nim,
            'email': getattr(pengajuan.mahasiswa, 'email', ''),
        },
        'judul': pengajuan.judul,
        'judul_inggris': pengajuan.judul_inggris,
        'deskripsi': pengajuan.deskripsi,
        'bidang_penelitian': pengajuan.get_bidang_penelitian_display(),
        'metodologi': pengajuan.get_metodologi_display(),
        'teknologi': pengajuan.teknologi,
        'latar_belakang': pengajuan.latar_belakang,
        'tujuan': pengajuan.tujuan,
        'manfaat': pengajuan.manfaat,
        'waktu_mulai': pengajuan.waktu_mulai.strftime('%d %B %Y') if pengajuan.waktu_mulai else '',
        'waktu_selesai': pengajuan.waktu_selesai.strftime('%d %B %Y') if pengajuan.waktu_selesai else '',
        'rencana_kerja': pengajuan.rencana_kerja,
        'status': pengajuan.get_status_display(),
        'tanggal_pengajuan': pengajuan.tanggal_pengajuan.strftime('%d %B %Y, %H:%M'),
        'catatan': pengajuan.catatan,
    }
    
    return JsonResponse(data)

@login_required
@require_http_methods(["POST"])
def approve_pengajuan(request, pengajuan_id):
    """
    View untuk menyetujui pengajuan
    """
    try:
        dosen = Dosen.objects.get(user=request.user)
    except Dosen.DoesNotExist:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    pengajuan = get_object_or_404(
        PengajuanJudul, 
        id=pengajuan_id, 
        dosen_pembimbing=dosen,
        status='pending'
    )
    
    # Parse JSON data
    try:
        data = json.loads(request.body)
        catatan = data.get('catatan', '')
    except:
        catatan = request.POST.get('catatan', '')
    
    # Update pengajuan
    pengajuan.status = 'approved'
    pengajuan.catatan = catatan
    pengajuan.tanggal_keputusan = timezone.now()
    pengajuan.save()
    
    messages.success(request, f'Pengajuan dari {pengajuan.mahasiswa.nama} berhasil disetujui.')
    
    return JsonResponse({
        'success': True,
        'message': 'Pengajuan berhasil disetujui.'
    })

@login_required
@require_http_methods(["POST"])
def reject_pengajuan(request, pengajuan_id):
    """
    View untuk menolak pengajuan
    """
    try:
        dosen = Dosen.objects.get(user=request.user)
    except Dosen.DoesNotExist:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    pengajuan = get_object_or_404(
        PengajuanJudul, 
        id=pengajuan_id, 
        dosen_pembimbing=dosen,
        status='pending'
    )
    
    # Parse JSON data
    try:
        data = json.loads(request.body)
        catatan = data.get('catatan', '')
    except:
        catatan = request.POST.get('catatan', '')
    
    if not catatan.strip():
        return JsonResponse({
            'success': False,
            'error': 'Alasan penolakan harus diisi.'
        }, status=400)
    
    # Update pengajuan
    pengajuan.status = 'rejected'
    pengajuan.catatan = catatan
    pengajuan.tanggal_keputusan = timezone.now()
    pengajuan.save()
    
    messages.success(request, f'Pengajuan dari {pengajuan.mahasiswa.nama} telah ditolak.')
    
    return JsonResponse({
        'success': True,
        'message': 'Pengajuan berhasil ditolak.'
    })