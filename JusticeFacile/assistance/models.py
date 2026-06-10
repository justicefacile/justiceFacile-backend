from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class Profile(models.Model):
    ROLE_CHOICES = [
        ('CITOYEN', 'Citoyen'),
        ('VICTIME_VBG', 'Victime de VBG'),
        ('JURISTE', 'Juriste / Avocat'),
        ('PSYCHOLOGUE', 'Psychologue'),
        ('ONG', 'ONG / Association de terrain'),
        ('ADMIN', 'Administrateur Systeme'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CITOYEN')
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    
    # identification du metier des experts.
    nom_structure = models.CharField(
        max_length=150, 
        blank=True, 
        null=True, 
        help_text="Nom du cabinet, de la clinique ou de l'ONG (lieu d'exercice des fonctions)"
    )
    numero_carte_professionnelle = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="Numero d'ordre des avocats, psychologues ou agrement des ONG et association"
    )
    
    # documents necessaires pour creation de compte expert
    document_carte_pro = models.URLField(
        blank=True, 
        null=True, 
        help_text="Lien vers le scan de la carte pro stocké sur Supabase"
    )
    document_diplome = models.URLField(
        blank=True, 
        null=True, 
        help_text="Lien vers le scan du diplôme"
    )
    document_cni = models.URLField(
        blank=True, 
        null=True, 
        help_text="Lien vers le scan de la pièce d'identité nationale (CNI)"
    )
    photo_professionnelle = models.URLField(
        blank=True, 
        null=True, 
        help_text="Lien vers la photo de profil professionnelle de l'expert"
    )
    
    # statut de validation des experts par l'admin
    est_certifie = models.BooleanField(
        default=False, 
        help_text="Définit si l'expert a été validé manuellement par l'administrateur"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.get_role_display()}"


# SIGNALS DJANGO 
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class VerificationEmail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification_code')
    code = models.CharField(max_length=6)
    cree_le = models.DateTimeField(auto_now_add=True)
    est_verifie = models.BooleanField(default=False)

    def __str__(self):
        return f"Code {self.code} pour {self.user.email}"

    def est_expire(self):
    
        return timezone.now() > self.cree_le + timedelta(minutes=15)

    def generer_nouveau_code(self):
        self.code = f"{random.randint(100000, 999999)}"
        self.cree_le = timezone.now()
        self.est_verifie = False
        self.save()

class TexteLoi(models.Model):

    CATEGORIES_CHOICES = [
        ('code_penal', 'Code Pénal'),
        ('code_civil', 'Code Civil'),
        ('code_travail', 'Code du Travail'),
        ('constitution', 'Constitution'),
        ('autre', 'Autre'),
    ]

    titre = models.CharField(max_length=255, help_text="Ex: Article 275 - Meurtre")
    contenu = models.TextField(help_text="Le texte complet de la loi")
    categorie = models.CharField(max_length=50, choices=CATEGORIES_CHOICES, default='autre')
    date_ajout = models.DateTimeField(auto_now_add=True)
    mots_cles = models.CharField(max_length=255, blank=True, help_text="Mots clés pour faciliter la recherche")

    def __str__(self):
        return f"{self.get_categorie_display()} - {self.titre}"

    class Meta:
        verbose_name = "Texte de Loi"
        verbose_name_plural = "Textes de Loi"
        ordering = ['-date_ajout']


""" modele our systeme d'assistance
1- modele pour la demande d'assistance avec les champs suivants"""
class DemandeAssistance(models.Model):
    CATEGORIE_CHOICES = [
        ('VBG', 'Violence Basée sur le Genre (VBG)'),
        ('TRAVAIL', 'Droit du Travail / Licenciement'),
        ('FAMILLE', 'Droit de la Famille (Mariage, Divorce, Succession)'),
        ('FONCIER', 'Litige Foncier / Terrain'),
        ('PENAL', 'Affaires Pénales (Vol, Escroquerie, Agression)'),
        ('AUTRE', 'Autre problème juridique'),
    ]

    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente d\'analyse'),
        ('APPROUVE', 'Approuvée (Dossier créé)'),
        ('REJETE', 'Rejetée / Classée sans suite'),
    ]

    # Le citoyen ou la victime qui soumet la demande
    citoyen = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='demandes_assistance'
    )
    
    # Code de référence unique généré automatiquement (Ex: REQ-F3A19B)
    code_reference = models.CharField(
        max_length=50, 
        unique=True, 
        editable=False,
        help_text="Identifiant unique pour le suivi du dossier"
    )
    
    titre = models.CharField(max_length=255, help_text="Ex: Licenciement abusif après 3 ans")
    description = models.TextField(help_text="Description détaillée de la situation")
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES, default='AUTRE')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    
    #  Anonymat des victimes
    est_anonyme = models.BooleanField(
        default=False, 
        help_text="Si vrai, masque l'identité réelle du citoyen aux experts assignés"
    )
    
    consentement_ong = models.BooleanField(
        default=False, 
        help_text="Spécifique VBG : L'utilisateur accepte d'être contacté et suivi par une ONG"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    # Génération automatique d'un code de suivi unique avant l'insertion en base
    def save(self, *args, **kwargs):
        if not self.code_reference:
            # Crée un code court de 8 caractères en majuscules (ex: REQ-A4E29F)
            self.code_reference = f"REQ-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code_reference} - {self.titre} [{self.get_statut_display()}]"

    class Meta:
        verbose_name = "Demande d'Assistance"
        verbose_name_plural = "Demandes d'Assistance"
        ordering = ['-date_creation']

# 2- modele pour le dossier
class Dossier(models.Model):
    STATUT_DOSSIER_CHOICES = [
        ('EN_COURS', 'En cours de traitement'),
        ('RESOLU', 'Résolu / Clôturé avec succès'),
        ('ARCHIVE', 'Archivé / Classé'),
    ]

    # Relation 1 à 1 avec demande : Une demande approuvée donne naissance à un unique dossier
    demande = models.OneToOneField(
        DemandeAssistance, 
        on_delete=models.CASCADE, 
        related_name='dossier',
        help_text="La demande d'assistance d'origine qui a déclenché ce dossier"
    )
    
    # les assignations
    # On utilise SET_NULL : si un expert quitte la plateforme, le dossier n'est pas supprimé !
    
    juriste_assigne = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='dossiers_juridiques',
        help_text="L'avocat ou parajuriste en charge de la procédure légale"
    )
    
    psychologue_assigne = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='dossiers_psychologiques',
        help_text="Le professionnel de la santé mentale pour le soutien psychologique"
    )
    
    ong_assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='dossiers_sociaux_ong',
        help_text="L'ONG ou association agréée pour la prise en charge sociale et l'hébergement"
    )
    
    # statut du dossier dans le processus de suivi.
    statut = models.CharField(max_length=20, choices=STATUT_DOSSIER_CHOICES, default='EN_COURS')
    notes_suivi_admin = models.TextField(
        blank=True, 
        null=True, 
        help_text="Remarques et coordination de l'administrateur système"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dossier #{self.id} ({self.demande.code_reference}) - Statut: {self.get_statut_display()}"

    class Meta:
        verbose_name = "Dossier de Suivi"
        verbose_name_plural = "Dossiers de Suivi"
        ordering = ['-date_creation']

    