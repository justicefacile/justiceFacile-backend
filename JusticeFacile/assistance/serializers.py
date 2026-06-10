from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, TexteLoi, DemandeAssistance, Dossier

class ProfileSerializer(serializers.ModelSerializer):
    """Traducteur pour les informations du profil incluant les documents de certification"""
    class Meta:
        model = Profile
        # On expose tous les champs nécessaires pour l'application Flutter
        fields = [
            'role', 'telephone', 'adresse', 'nom_structure', 
            'numero_carte_professionnelle', 'document_carte_pro', 
            'document_diplome', 'document_cni', 'photo_professionnelle', 
            'est_certifie', 'date_creation'
        ]

class UserSerializer(serializers.ModelSerializer):
    """Traducteur pour lire les informations d'un utilisateur existant"""
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'profile']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES, default='CITOYEN', write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'role']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un compte avec cet email existe déjà.")
        return value

    def create(self, validated_data):

        role = validated_data.pop('role', 'CITOYEN')

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


class DemandeAssistanceSerializer(serializers.ModelSerializer):
    # Champ virtuel qui contiendra soit les vraies infos, soit les infos masquées
    citoyen_details = serializers.SerializerMethodField()
    categorie_display = serializers.CharField(source='get_categorie_display', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)

    class Meta:
        model = DemandeAssistance
        fields = [
            'id', 'code_reference', 'titre', 'description', 'categorie', 
            'categorie_display', 'statut', 'statut_display', 'est_anonyme', 
            'consentement_ong', 'citoyen_details', 'date_creation'
        ]
        read_only_fields = ['code_reference', 'statut']

    def get_citoyen_details(self, obj):
        request = self.context.get('request')
        current_user = request.user if request else None

        # Si pas d'utilisateur connecte, on ne donne rien
        if not current_user:
            return {"detail": "Non authentifié"}

        # Si la demande est anonyme
        if obj.est_anonyme:
            # L'auteur de la demande et l'admin ont le droit de voir l'identité réelle
            if current_user == obj.citoyen or current_user.is_staff or getattr(current_user, 'profile', None).role == 'ADMIN':
                return {
                    "id": obj.citoyen.id,
                    "first_name": obj.citoyen.first_name,
                    "last_name": obj.citoyen.last_name,
                    "email": obj.citoyen.email,
                    "telephone": obj.citoyen.profile.telephone if hasattr(obj.citoyen, 'profile') else None,
                    "adresse": obj.citoyen.profile.adresse if hasattr(obj.citoyen, 'profile') else None,
                }
            
            # Pour les experts on applique une restriction
            return {
                "id": None,
                "first_name": "Utilisateur",
                "last_name": f"Anonyme ({obj.code_reference})",
                "email": "identite.masquee@justicefacile.com",
                "telephone": "Masqué (Tchat Uniquement)",
                "adresse": "Masquée pour sécurité",
            }
        
        # Si la demande n'est pas anonyme, tout le monde ayant accès à la voit les vraies infos
        return {
            "id": obj.citoyen.id,
            "first_name": obj.citoyen.first_name,
            "last_name": obj.citoyen.last_name,
            "email": obj.citoyen.email,
            "telephone": obj.citoyen.profile.telephone if hasattr(obj.citoyen, 'profile') else None,
            "adresse": obj.citoyen.profile.adresse if hasattr(obj.citoyen, 'profile') else None,
        }


class DossierSerializer(serializers.ModelSerializer):
    # On imbrique le sérialiseur sécurisé de la demande d'origine
    demande_details = DemandeAssistanceSerializer(source='demande', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    
    # Raccourcis lisibles pour afficher les noms des experts assignés sur Flutter
    nom_juriste = serializers.SerializerMethodField()
    nom_psychologue = serializers.SerializerMethodField()
    nom_ong = serializers.SerializerMethodField()

    class Meta:
        model = Dossier
        fields = [
            'id', 'demande', 'demande_details', 'juriste_assigne', 'nom_juriste',
            'psychologue_assigne', 'nom_psychologue', 'ong_assignee', 'nom_ong',
            'statut', 'statut_display', 'notes_suivi_admin', 'date_creation', 'date_modification'
        ]

    def get_nom_juriste(self, obj):
        if obj.juriste_assigne:
            return f"Me {obj.juriste_assigne.get_full_name() or obj.juriste_assigne.email}"
        return "Aucun juriste assigné"

    def get_nom_psychologue(self, obj):
        if obj.psychologue_assigne:
            return f"Dr {obj.psychologue_assigne.get_full_name() or obj.psychologue_assigne.email}"
        return "Aucun psychologue assigné"

    def get_nom_ong(self, obj):
        if obj.ong_assignee and hasattr(obj.ong_assignee, 'profile'):
            return obj.ong_assignee.profile.nom_structure or "ONG Partenaire"
        return "Aucune ONG assignée"