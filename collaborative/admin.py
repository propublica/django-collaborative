from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.models import LogEntry
from django.apps import apps
from import_export.resources import modelresource_factory

from collaborative.models import Metadata, Contact

UserAdmin.list_display = ("username","email","first_name","last_name")
# UserAdmin.list_editable = ("first_name", "last_name")

UserAdmin.add_fieldsets = ((None, {
    'fields': ('username', 'email', 'password1', 'password2'),
    'classes': ('wide',)
}),)


## NOTE: This works for foreign key where
# Contact has a FK -> Metadata
class ContactInline(admin.TabularInline):
    model = Contact


class MetadataAdmin(admin.ModelAdmin):
    inlines = [
        ContactInline
    ]

admin.site.register(Metadata, MetadataAdmin)

admin.site.register(LogEntry)

