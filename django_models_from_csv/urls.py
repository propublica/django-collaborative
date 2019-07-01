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
    path('refine-and-import/<int:id>/', views.refine_and_import,
         name='refine-and-import'),
    path('refine-and-import/<str:name>/', views.refine_and_import_by_name,
         name='refine-and-import'),
]
