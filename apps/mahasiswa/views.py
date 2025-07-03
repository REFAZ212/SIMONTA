from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.db.models import Q
from .models import Mahasiswa, PengajuanTA, NilaiTA, PengajuanJudul, HistoryPengajuan
from .forms import PengajuanTAForm, PengajuanJudulForm
from apps.core.models import JadwalPenting, Notifikasi
from apps.dosen.models import JadwalBimbingan


@login_required
def dashboard(request):
    if not request.user.is_mahasiswa():
        raise Http404("Akses ditolak")

    try:
        mahasiswa = request.user.mahasiswa
    except Mahasiswa.DoesNotExist:
        messages.error(request, "Profil mahasiswa belum dibuat. Hubungi admin.")
        return redirect('core:home')

    pengajuan_ta = PengajuanTA.objects.filter(mahasiswa=request.user).order_by('-tanggal_pengajuan')

    pengajuan_judul = PengajuanJudul.objects.filter(mahasiswa=mahasiswa).order_by('-tanggal_pengajuan')
    jadwal_penting = JadwalPenting.objects.filter(is_active=True)

    notifikasi = Notifikasi.objects.filter(
        Q(user=request.user) | Q(is_global=True)
    ).order_by('-created_at')[:5]

    context = {
        'mahasiswa': mahasiswa,
        'pengajuan_ta': pengajuan_ta,
        'pengajuan_judul': pengajuan_judul,
        'jadwal_penting': jadwal_penting,
        'notifikasi': notifikasi,
    }
    return render(request, 'mahasiswa/dashboard.html', context)



@login_required
def pengajuan_ta(request):
    if not request.user.is_mahasiswa():
        messages.error(request, 'Anda tidak memiliki akses sebagai mahasiswa.')
        return redirect('dashboard')

    try:
        mahasiswa = request.user.mahasiswa
    except Mahasiswa.DoesNotExist:
        messages.error(request, 'Profil mahasiswa tidak ditemukan.')
        return redirect('dashboard')

    if not mahasiswa.is_eligible_for_ta():
        messages.warning(request, "Anda belum memenuhi syarat untuk mengajukan tugas akhir.")
        return redirect('mahasiswa:dashboard')

    # Cek apakah sudah pernah mengajukan
    if PengajuanTA.objects.filter(mahasiswa=request.user).exists():
        messages.warning(request, "Anda sudah mengajukan TA sebelumnya.")
        return redirect('mahasiswa:dashboard')

    if request.method == 'POST':
        form = PengajuanTAForm(request.POST)
        if form.is_valid():
            pengajuan = form.save(commit=False)
            pengajuan.mahasiswa = request.user  # ⬅️ Pastikan ini User, bukan Mahasiswa
            pengajuan.save()
            messages.success(request, "Pengajuan TA berhasil dikirim.")
            return redirect('mahasiswa:dashboard')
        else:
            messages.error(request, "Terdapat kesalahan dalam formulir.")
    else:
        form = PengajuanTAForm()

    return render(request, 'mahasiswa/pengajuan_ta.html', {
        'form': form,
        'mahasiswa': mahasiswa,  # Untuk ditampilkan di template, jika perlu
    })


@login_required
def pengajuan_judul(request):
    if not request.user.is_mahasiswa():
        messages.error(request, 'Anda tidak memiliki akses sebagai mahasiswa.')
        return redirect('dashboard')

    try:
        mahasiswa = request.user.mahasiswa
    except Mahasiswa.DoesNotExist:
        messages.error(request, 'Profil mahasiswa tidak ditemukan.')
        return redirect('core:home')

    existing_pengajuan = PengajuanJudul.objects.filter(
        mahasiswa=mahasiswa, 
        status__in=['pending', 'reviewed', 'revision']
    ).first()

    if existing_pengajuan:
        messages.warning(request, 'Anda masih memiliki pengajuan yang sedang diproses.')
        return redirect('detail_pengajuan', pk=existing_pengajuan.pk)
    
    if request.method == 'POST':
        form = PengajuanJudulForm(request.POST)
        if form.is_valid():
            pengajuan = form.save(commit=False)
            pengajuan.mahasiswa = mahasiswa
            pengajuan.save()
            
            HistoryPengajuan.objects.create(
                pengajuan=pengajuan,
                status_lama='',
                status_baru='pending',
                keterangan='Pengajuan tugas akhir dibuat',
                diubah_oleh=request.user
            )
            
            messages.success(request, 'Pengajuan tugas akhir berhasil dikirim!')
            return redirect('detail_pengajuan', pk=pengajuan.pk)
    else:
        form = PengajuanJudulForm()
    
    return render(request, 'mahasiswa/pengajuan_judul.html', {
        'form': form,
        'mahasiswa': mahasiswa
    })


@login_required
def lihat_nilai(request):
    if not request.user.is_mahasiswa():
        raise Http404("Akses ditolak")
    
    mahasiswa = get_object_or_404(Mahasiswa, user=request.user)
    nilai_ta = NilaiTA.objects.filter(mahasiswa=mahasiswa)
    
    return render(request, 'mahasiswa/lihat_nilai.html', {
        'mahasiswa': mahasiswa,
        'nilai_ta': nilai_ta
    })


from django.contrib import messages
@login_required
def jadwal_bimbingan(request):
    jadwal_list = JadwalBimbingan.objects.filter(status='tersedia')  # atau filter sesuai kebutuhan
    context = {
        'jadwal_list': jadwal_list
    }
    return render(request, 'mahasiswa/jadwal_bimbingan.html', context)


@login_required
def detail_pengajuan(request, pk):
    pengajuan = PengajuanJudul.objects.get(pk=pk)
    return render(request, 'mahasiswa/detail_pengajuan.html', {'pengajuan': pengajuan})
