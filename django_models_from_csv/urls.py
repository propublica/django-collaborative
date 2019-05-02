from django.contrib import admin
from django.conf import settings
from django.conf.urls import include, url
from django.urls import path

from django_models_from_csv import views


app_name = "csv_models"

urlpatterns = [
    # Create a new sheet table (enters wizard)
    path('begin/', views.begin, name='begin'),
    # Build the database table from the sheet
    path('refine-schema/<int:id>/', views.refine_schema,
         name='refine-schema'),
    # Import data from sheet into table
    path('import-data/<int:id>/', views.import_data,
         name='import-data'),

    # Waits for migration to run, redirects to next page
    path('wait/', views.wait, name='wait'),
    # API call to create and run migrations
    path('migrate/', views.migrate, name='migrate'),
]
