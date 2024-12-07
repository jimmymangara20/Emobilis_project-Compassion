from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Child, CustomUser

class CustomUserAdmin(UserAdmin):
    # Specify the fields to display in the admin list view
    list_display = ('username', 'email', 'is_admin', 'is_beneficiary', 'is_supporter', 'is_staff', 'is_active')
    # Add filters for these fields in the admin panel
    list_filter = ('is_admin', 'is_beneficiary', 'is_supporter', 'is_staff', 'is_active')
    # Define the fields to include in the admin detail view
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_admin', 'is_beneficiary', 'is_supporter', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    # Define the fields to include when creating a new user in the admin panel
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_admin', 'is_beneficiary', 'is_supporter', 'is_staff', 'is_active'),
        }),
    )
    # Define the fields used for searching in the admin panel
    search_fields = ('username', 'email')
    ordering = ('username',)

# Register the CustomUser model with the admin
admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Child)

