from django.contrib import admin
from django.conf import settings
from django.conf.urls import include, url
from django.urls import path


from collaborative.views import redirect_wizard_or_admin, root
from collaborative import views


urlpatterns = [
    url(r'^$', views.root),
    url('', include('social_django.urls', namespace='social')),

    # Authentication & Redirection to Wizard URLs
    path('admin/', admin.site.urls),
    path('request-access/', views.request_access, name='request-access'),
    path('setup-check/', views.redirect_wizard_or_admin, name='setup-check'),

    # # Create a new sheet table (enters wizard)
    # path('setup-begin/', views.setup_begin, name='setup-begin'),
    # # Build the database table from the sheet
    # path('setup-refine-schema/<int:id>/', views.setup_refine_schema,
    #      name='setup-refine-schema'),
    # # Import data from sheet into table
    # path('setup-import/<int:id>/', views.setup_import,
    #      name='setup-import'),

    # Setup password and OAuth
    path('setup-auth/', views.setup_auth, name='setup-auth'),
    # Success page
    path('setup-complete/', views.setup_complete, name='setup-complete'),

    # Waits for migration to run, redirects to next page
    path('setup-wait/', views.setup_wait, name='setup-wait'),
    # API call to create and run migrations
    path('setup-migrate/', views.setup_migrate, name='setup-migrate'),
]
