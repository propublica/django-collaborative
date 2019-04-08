from django.contrib.auth.admin import UserAdmin

UserAdmin.list_display = ("username","email","first_name","last_name")
UserAdmin.list_editable = ("first_name", "last_name")
