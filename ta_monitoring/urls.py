# ===== ta_monitoring/urls.py =====
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('users/', include('apps.users.urls')),
    path('mahasiswa/', include('apps.mahasiswa.urls', namespace='mahasiswa')),
    path('dosen/', include('apps.dosen.urls')),
    path('adminkampus/', include('apps.adminkampus.urls')),
    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)