from django.conf import settings
from django.shortcuts import render

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, 'MAINTENANCE_MODE', False) and request.path != '/admin/':
            return render(request, 'maintenance.html', status=503)

        return self.get_response(request)
