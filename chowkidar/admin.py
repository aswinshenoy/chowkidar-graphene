from django.contrib import admin

from .models import RefreshToken


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token']
    readonly_fields = ['user', 'token', 'issued']
