from django.urls import path
from . import views;

urlpatterns = [
    path('', views.inscription, name='register'),
    path('login/', views.connexion, name='login'),
    path('assistance/', views.dashboardVic, name='assistance'),
    path('dashboard/', views.dashboardPsy, name='dashboard'),
    path('dossiers/', views.dossiers, name='dossier'),
    path('todos/', views.todo_list, name='todo_list'),
]