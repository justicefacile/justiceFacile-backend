from django.contrib import admin
from .models import Profile, TexteLoi

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'region', 'date_creation')
    list_filter = ('role', 'region')

@admin.register(TexteLoi)
class TexteLoiAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'date_ajout')
    search_fields = ('titre', 'contenu', 'mots_cles')
    list_filter = ('categorie',)