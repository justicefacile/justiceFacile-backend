from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
from .services.supabase_service import fetch_todos
from rest_framework import generics, status,filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer, TexteLoiSerializer
from .models import TexteLoi

# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny] 

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True) 
        
        user = serializer.save() 

        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Compte créé avec succès sur JusticeFacile !',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)



@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')

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

class TexteLoiListCreateView(generics.ListCreateAPIView):
    queryset = TexteLoi.objects.all()
    serializer_class = TexteLoiSerializer
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['titre', 'contenu', 'mots_cles']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

class UserProfileView(APIView):
   
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TexteLoiDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TexteLoi.objects.all()
    serializer_class = TexteLoiSerializer
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
class LogoutView(APIView):
    """
    Endpoint /api/v1/auth/logout/
    Blackliste le refresh token pour déconnecter l'utilisateur.
    """
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