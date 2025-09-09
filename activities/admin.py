from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Activity


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    # Champs affichés dans la liste des utilisateurs
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'role', 'is_staff', 'is_active'
    )
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'date_joined')

    # Champs affichés dans le formulaire d’édition
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'description', 'location_city',
        'start_time', 'end_time', 'proposer', 'category'
    )
    list_filter = ('proposer', 'category', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
