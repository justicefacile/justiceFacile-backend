from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    
    ROLES_CHOICES = [
        ('citoyen', 'Citoyen'),
        ('juriste', 'Juriste'),
        ('psychologue', 'Psychologue'),
        ('ong', 'ONG / Association'),
        ('admin', 'Administrateur'),
    ]

    REGIONS_CHOICES = [
        ('centre', 'Centre (Yaoundé)'),
        ('littoral', 'Littoral (Douala)'),
        ('ouest', 'Ouest (Bafoussam)'),
        ('nord', 'Nord (Garoua)'),
        ('extreme_nord', 'Extrême-Nord'),
        ('adamaoua', 'Adamaoua'),
        ('est', 'Est'),
        ('nord_ouest', 'Nord-Ouest'),
        ('sud', 'Sud'),
        ('sud_ouest', 'Sud-Ouest'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    role = models.CharField(max_length=20, choices=ROLES_CHOICES, default='citoyen')

    telephone = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=20, choices=REGIONS_CHOICES, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    
    if created:
        Profile.objects.get_or_create(user=instance)

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

