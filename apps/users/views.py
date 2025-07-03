# ===== apps/users/views.py =====
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, CustomLoginForm

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'users/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_admin():
            return reverse_lazy('adminkampus:dashboard')
        elif user.is_dosen():
            return reverse_lazy('dosen:dashboard')
        elif user.is_mahasiswa():
            return reverse_lazy('mahasiswa:dashboard')
        return reverse_lazy('core:home')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Akun berhasil dibuat untuk {username}!')
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})