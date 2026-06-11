import threading 
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import random
from rest_framework.permissions import IsAuthenticated, AllowAny
from .services.supabase_service import fetch_todos
from rest_framework import generics, status,filters,viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from .serializers import RegisterSerializer, UserSerializer, TexteLoiSerializer, DemandeAssistanceSerializer, DossierSerializer
from .models import TexteLoi, DemandeAssistance, Dossier, VerificationEmail
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

# Create your views here.

 # 



def envoyer_mail_background(subject, message, from_email, recipient_list):
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print(" [EMAIL] Le mail a été envoyé avec succès .")
    except Exception as e:
        print(f" [EMAIL] Échec de l'envoi (normal sur Railway) : {e}")

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny] 

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if 'role' in data and isinstance(data['role'], str):
            data['role'] = data['role'].upper()
        
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            print(" ERREUR VALIDATION INSCRIPTION :", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        serializer.is_valid(raise_exception=True) 
        user = serializer.save() 

        # Désactiver le compte en attente de vérification
        user.is_active = False
        user.save()

        # Générer le code à 6 chiffres
        code_activation = f"{random.randint(100000, 999999)}"
        VerificationEmail.objects.create(user=user, code=code_activation)

        # Affichage immédiat dans les logs pour le débogage
        print(f" [DEBUG] CODE DE VÉRIFICATION POUR {user.email} -> {code_activation}")

        # ON LANCE L'ENVOI DANS UN THREAD SÉPARÉ (Ne bloque pas le téléphone)
        email_thread = threading.Thread(
            target=envoyer_mail_background,
            args=(
                "Votre code de vérification - JusticeFacile",
                f"Bonjour,\n\nVotre code de vérification est : {code_activation}.",
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
        )
    
        email_thread.start()

        response_data = serializer.data  # Format plat : {'id', 'username', 'email'}
        
        # On double les données sous forme imbriquée au cas où Flutter cherche 'user'
        response_data['user'] = serializer.data 
        
        # On ajoute les messages et emails requis
        response_data['message'] = 'Compte créé ! Veuillez vérifier vos logs.'
        response_data['email'] = user.email

        print(" [DEBUG] Réponse envoyée à Flutter :", response_data)

        return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')

    #  Vérifier si l'utilisateur existe et s'il est vérifié
    try:
        user_check = User.objects.get(username=email)
        if hasattr(user_check, 'verification_code') and not user_check.verification_code.est_verifie:
            return Response(
                {'error': 'Votre adresse email n\'a pas encore été vérifiée. Veuillez valider votre code.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
    except User.DoesNotExist:
        pass

    user = authenticate(request, username=email, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Connexion réussie.',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    else:
        return Response(
            {'error': 'Identifiants incorrects. Veuillez réessayer.'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "http://127.0.0.1:8000/"


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({"error": "L'email et le code sont requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=email)
            verification = user.verification_code

            if verification.est_verifie:
                return Response({"message": "Ce compte est déjà vérifié."}, status=status.HTTP_400_BAD_REQUEST)

            if verification.code != code:
                return Response({"error": "Code incorrect."}, status=status.HTTP_400_BAD_REQUEST)

            if verification.est_expire():
                return Response({"error": "Ce code a expiré. Veuillez en demander un nouveau."}, status=status.HTTP_400_BAD_REQUEST)

            # Tout est bon  On active l'utilisateur
            verification.est_verifie = True
            verification.save()
            
            user.is_active = True
            user.save()

            # On génère immédiatement ses jetons d'accès pour le connecter sur l'application 
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Email vérifié avec succès ! Bienvenue sur JusticeFacile.",
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)

class ResendVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"error": "L'email est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=email)
            verification = user.verification_code

            if verification.est_verifie:
                return Response({"message": "Ce compte est déjà vérifié."}, status=status.HTTP_400_BAD_REQUEST)

            # Génération et sauvegarde du nouveau code de verifiaction
            verification.generer_nouveau_code()

            # Envoi de l'email
            try:
                send_mail(
                    subject="Votre nouveau code de vérification - JusticeFacile",
                    message=f"Bonjour,\n\nVoici votre nouveau code de vérification : {verification.code}.\nIl expire dans 15 minutes.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception:
                pass

            return Response({"message": "Un nouveau code de vérification a été envoyé par email."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)
        


class UserProfileView(APIView):
   
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutView(APIView):
  
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
           
            refresh_token = request.data.get("refresh")
            
            if not refresh_token:
                return Response({"error": "Le token de rafraîchissement est requis."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Déconnexion réussie. Token blacklisté."}, status=status.HTTP_205_RESET_CONTENT)
        
        except Exception as e:
            return Response({"error": "Token invalide ou déjà déconnecté."}, status=status.HTTP_400_BAD_REQUEST)
        

class TexteLoiListCreateView(generics.ListCreateAPIView):
    queryset = TexteLoi.objects.all()
    serializer_class = TexteLoiSerializer
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['titre', 'contenu', 'mots_cles']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

class TexteLoiDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TexteLoi.objects.all()
    serializer_class = TexteLoiSerializer
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    

# vue de création de demande d'assistance et de listing des demandes d'un citoyen
class DemandeAssistanceListCreateView(generics.ListCreateAPIView):
    serializer_class = DemandeAssistanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or (hasattr(user, 'profile') and user.profile.role == 'ADMIN'):
            return DemandeAssistance.objects.all()
        return DemandeAssistance.objects.filter(citoyen=user)

    def perform_create(self, serializer):
        serializer.save(citoyen=self.request.user)


# Vue pour lister les dossiers assignés
class DossierListView(generics.ListAPIView):
    serializer_class = DossierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or (hasattr(user, 'profile') and user.profile.role == 'ADMIN'):
            return Dossier.objects.all()
        if not hasattr(user, 'profile'):
            return Dossier.objects.none()
        
        role = user.profile.role
        if role == 'JURISTE':
            return Dossier.objects.filter(juriste_assigne=user)
        elif role == 'PSYCHOLOGUE':
            return Dossier.objects.filter(psychologue_assigne=user)
        elif role == 'ONG':
            return Dossier.objects.filter(ong_assignee=user)
        elif role in ['CITOYEN', 'VICTIME_VBG']:
            return Dossier.objects.filter(demande__citoyen=user)
        return Dossier.objects.none()


# Vue pour voir les détails d'un dossier spécifique
class DossierDetailView(generics.RetrieveAPIView):
    serializer_class = DossierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Même sécurité stricte pour s'assurer que personne ne triche sur l'ID dans l'URL
        user = self.request.user
        if user.is_staff or (hasattr(user, 'profile') and user.profile.role == 'ADMIN'):
            return Dossier.objects.all()
        if not hasattr(user, 'profile'):
            return Dossier.objects.none()
        
        role = user.profile.role
        if role == 'JURISTE':
            return Dossier.objects.filter(juriste_assigne=user)
        elif role == 'PSYCHOLOGUE':
            return Dossier.objects.filter(psychologue_assigne=user)
        elif role == 'ONG':
            return Dossier.objects.filter(ong_assignee=user)
        elif role in ['CITOYEN', 'VICTIME_VBG']:
            return Dossier.objects.filter(demande__citoyen=user)
        return Dossier.objects.none()


def inscription(request):
    return render(request, 'assistance/register.html')
def connexion(request):
    return render(request, 'assistance/login.html')
def dashboardVic(request):
    return render(request, 'assistance/vbg.html')
def dossiers(request):
    return render(request, 'assistance/dossiers.html')
def dashboardPsy(request):
    return render(request, 'assistance/dashboard.html')

def todo_list(request):
    todos = fetch_todos()
    return render(request, 'assistance/todo_list.html', {'todos': todos})