"""
URL configuration for JusticeFacile project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from assistance.views import GoogleLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('assistance.urls')),
    # les routes d'authentification de dj-rest-auth sont mis ici car elles ne font pas partie integrante de mon aplli mais sont directement installéés dans mon projet.
    path('api/v1/auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('api/v1/auth/', include('dj_rest_auth.urls')),
]
