from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/me/', views.UserProfileView.as_view(), name='me'),
    path('auth/verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('auth/resend-verification/', views.ResendVerificationView.as_view(), name='resend_verification'),
    path('auth/google/', views.GoogleLoginView.as_view(), name='google_login'),
    path('auth/password/reset/', include([
        path('', include('dj_rest_auth.urls')), 
    ])),

    path('textes-loi/', views.TexteLoiListCreateView.as_view(), name='textes_loi_list'),
    path('textes-loi/<int:pk>/', views.TexteLoiDetailView.as_view(), name='texte_loi_detail'),
    
    path('demandes/', views.DemandeAssistanceListCreateView.as_view(), name='demandes_list_create'),
    path('dossiers/', views.DossierListView.as_view(), name='dossiers_list'),
    path('dossiers/<int:pk>/', views.DossierDetailView.as_view(), name='dossier_detail'),
    
    path('', views.inscription, name='register1'),
    path('login/', views.connexion, name='login1'),
    path('assistance/', views.dashboardVic, name='assistance'),
    path('dashboard/', views.dashboardPsy, name='dashboard'),
    path('dossiers1/', views.dossiers, name='dossier'),
    path('todos/', views.todo_list, name='todo_list'),
]