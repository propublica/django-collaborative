from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.models import LogEntry
from django.apps import apps


UserAdmin.list_display = ("username","email","first_name","last_name")
# UserAdmin.list_editable = ("first_name", "last_name")

UserAdmin.add_fieldsets = ((None, {
    'fields': ('username', 'email', 'password1', 'password2'),
    'classes': ('wide',)
}),)

admin.site.register(LogEntry)

# Auto-register Admins for all models. This avoids needing to
# write code and inject it into an admin.py for our auto-generated
# models
models = apps.get_models()
for model in models:
    if "collaborative.models" not in str(model):
        continue
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

