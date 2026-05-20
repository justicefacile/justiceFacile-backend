from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, TexteLoi

class ProfileSerializer(serializers.ModelSerializer):
    """Traducteur pour les informations supplémentaires (rôle, téléphone, région)"""
    class Meta:
        model = Profile
        fields = ['role', 'telephone', 'region', 'date_creation']

class UserSerializer(serializers.ModelSerializer):
    """Traducteur pour lire les informations d'un utilisateur existant"""
    # On imbrique le ProfileSerializer pour avoir toutes les infos d'un coup
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'profile']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    role = serializers.ChoiceField(choices=Profile.ROLES_CHOICES, default='citoyen', write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'role']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un compte avec cet email existe déjà.")
        return value

    def create(self, validated_data):

        role = validated_data.pop('role', 'citoyen')

        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        user.profile.role = role
        user.profile.save()

        return user
       

class TexteLoiSerializer(serializers.ModelSerializer):
    categorie_display = serializers.CharField(source='get_categorie_display', read_only=True)

    class Meta:
        model = TexteLoi
        fields = ['id', 'titre', 'contenu', 'categorie', 'categorie_display', 'date_ajout', 'mots_cles']