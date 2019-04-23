"""collaborative URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls import include, url
from django.urls import path
from django.views.generic.base import RedirectView

from collaborative import views


urlpatterns = [
    url(r'^$', RedirectView.as_view(url='admin/')),
    url('', include('social_django.urls', namespace='social')),
    path('admin/', admin.site.urls),
    path('request-access/', views.request_access, name='request-access'),
    path('setup-check/', views.setup_check, name='setup-check'),
    path('setup-begin/', views.setup_begin, name='setup-begin'),
    path('setup-refine-schema/',
         views.setup_refine_schema,
         name='setup-refine-schema'),
    path('setup-import/', views.setup_import, name='setup-import'),
    path('setup-auth/', views.setup_auth, name='setup-auth'),
    path('setup-complete/', views.setup_complete, name='setup-complete'),
    path('setup-wait/', views.setup_wait, name='setup-wait'),
    path('setup-migrate/', views.setup_migrate, name='setup-migrate'),
]
