from django.contrib import admin
from django.conf import settings
from django.conf.urls import include, url
from django.urls import path


from collaborative.views import redirect_wizard_or_admin, root
from collaborative import views


urlpatterns = [
    url(r'^$', views.root),
    url('', include('social_django.urls', namespace='social')),
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # Authentication & Redirection to Wizard URLs
    path('admin/', admin.site.urls),
    path('request-access/', views.request_access, name='request-access'),
    path('setup-check/', views.redirect_wizard_or_admin, name='setup-check'),

    # DB Schema & CSV Importing Endpoints (can be used to edit, too)
    path('db-config/',
         include('django_models_from_csv.urls', namespace="db-config")),

    # Setup password and OAuth
    path('setup-auth/', views.setup_auth, name='setup-auth'),
    # Success page
    path('setup-complete/', views.setup_complete, name='setup-complete'),
]
