from django.urls import path
from . import views

urlpatterns = [
    path('', views.ship_list,   name='ship-list'),
    path('create/',  views.ship_create, name='ship-create'),
    path('<int:pk>/', views.ship_detail, name='ship-detail'),
]