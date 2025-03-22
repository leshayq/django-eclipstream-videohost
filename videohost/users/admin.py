from django.contrib import admin
from .models import CustomUser, Subscriptions
from django.contrib.auth.admin import UserAdmin

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

@admin.register(Subscriptions)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'notify', 'created_at',)
    readonly_fields = ('follower', 'following', 'created_at',)
