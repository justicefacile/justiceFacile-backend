from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/me/', views.UserProfileView.as_view(), name='me'),
    path('textes-loi/', views.TexteLoiListCreateView.as_view(), name='textes_loi_list'),
    path('textes-loi/<int:pk>/', views.TexteLoiDetailView.as_view(), name='texte_loi_detail'),
    path('', views.inscription, name='register1'),
    path('login/', views.connexion, name='login1'),
    path('assistance/', views.dashboardVic, name='assistance'),
    path('dashboard/', views.dashboardPsy, name='dashboard'),
    path('dossiers/', views.dossiers, name='dossier'),
    path('todos/', views.todo_list, name='todo_list'),
]