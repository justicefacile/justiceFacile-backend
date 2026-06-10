from django.contrib import admin
from .models import Profile, TexteLoi, DemandeAssistance, Dossier

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # On affiche les vrais champs existants, dont la validation administrative
    list_display = ('user', 'role', 'telephone', 'nom_structure', 'est_certifie', 'date_creation')
    
    # On filtre par rôle et par statut de certification 
    list_filter = ('role', 'est_certifie', 'date_creation')
    
    # Permet de chercher un utilisateur par son email ou son nom de structure
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'nom_structure')
    
    # Permet de certifier un expert directement depuis la liste globale
    list_editable = ('est_certifie',)

@admin.register(TexteLoi)
class TexteLoiAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'date_ajout')
    list_filter = ('categorie', 'date_ajout')
    search_fields = ('titre', 'contenu', 'mots_cles')

@admin.register(DemandeAssistance)
class DemandeAssistanceAdmin(admin.ModelAdmin):
    list_display = ('code_reference', 'citoyen', 'categorie', 'statut', 'est_anonyme', 'date_creation')
    list_filter = ('categorie', 'statut', 'est_anonyme', 'date_creation')
    search_fields = ('code_reference', 'titre', 'description', 'citoyen__email')
    # Permet à l'admin de changer le statut de la demande directement 
    list_editable = ('statut',)

@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    # Permet de voir directement qui travaille sur quel dossier depuis la liste
    list_display = ('id', 'get_ref', 'get_categorie', 'juriste_assigne', 'psychologue_assigne', 'ong_assignee', 'statut')
    list_filter = ('statut', 'demande__categorie', 'date_creation')
    search_fields = ('id', 'demande__code_reference', 'juriste_assigne__email', 'ong_assignee__username')
    list_editable = ('statut',)

    # Astuce facile pour afficher des informations de la Demande liée dans les colonnes
    @admin.display(description="Réf. Demande")
    def get_ref(self, obj):
        return obj.demande.code_reference

    @admin.display(description="Catégorie")
    def get_categorie(self, obj):
        return obj.demande.get_categorie_display()