from django.shortcuts import render

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