from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.task_list,   name='task-list'),
    path('create/', views.task_create, name='task-create'),
    path('<int:pk>/', views.task_detail, name='task-detail'),
]