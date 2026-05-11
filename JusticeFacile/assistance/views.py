from django.shortcuts import render
from .services.supabase_service import fetch_todos
# Create your views here.

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