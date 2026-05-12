"""
URL configuration for maritime project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('admin/', admin.site.urls),
    path('auth/', include('apps.users.urls', namespace='users')),
    path('dashboard/', include('apps.compliance.urls', namespace='compliance')),
    path('maintenance/', include('apps.maintenance.urls', namespace='maintenance')),
    path('drills/', include('apps.drills.urls', namespace='drills')),
    path('ships/', include('apps.ships.urls', namespace='ships')),
    path('api/v1/', include('apps.api.urls')),
]