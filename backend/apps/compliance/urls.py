from django.urls import path
from . import views

app_name = 'compliance'


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]