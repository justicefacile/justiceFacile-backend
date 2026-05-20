from django.urls import path
from . import views;

urlpatterns = [
    path('api/auth/register/', views.RegisterView.as_view(), name='register'),
    path('api/auth/login/', views.login_view, name='login'),
    path('', views.inscription, name='register1'),
    path('login/', views.connexion, name='login1'),
    path('api/textes-loi/', views.TexteLoiListCreateView.as_view(), name='textes_loi_list'),
    path('api/textes-loi/<int:pk>/', views.TexteLoiDetailView.as_view(), name='texte_loi_detail'),
    path('assistance/', views.dashboardVic, name='assistance'),
    path('dashboard/', views.dashboardPsy, name='dashboard'),
    path('dossiers/', views.dossiers, name='dossier'),
    path('todos/', views.todo_list, name='todo_list'),
]