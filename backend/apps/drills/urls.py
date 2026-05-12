from django.urls import path
from . import views

app_name = 'drills'

urlpatterns = [
    path('', views.drill_list,   name='drill-list'),
    path('create/', views.drill_create, name='drill-create'),
    path('<int:pk>/', views.drill_detail, name='drill-detail'),
]