"""
Ce fichier configure l'administration Django pour les modèles personnalisés de l'application.
Il personnalise l'affichage dans l'interface d'administration avec list_display,
search_fields, ordering, etc.
"""
from django.contrib import admin
from .models import User, Category, Activity


# -------------------------
# Admin pour le modèle User
# -------------------------
@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    """Personnalisation de l'affichage du modèle User dans l'admin."""
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'role', 'is_staff', 'is_active'
    )
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'date_joined')

    search_fields = ('username','first_name', 'last_name')
    ordering = ('username',)

# -----------------------------
# Admin pour le modèle Category
# -----------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Affichage et gestion des catégories dans l'admin."""
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

# ---------------------------
# Admin pour le modèle Activity
# ---------------------------
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """Affichage et gestion des activités dans l'admin."""
    list_display = (
        'title', 'description', 'location_city',
        'start_time', 'end_time', 'proposer', 'category'
    )
    list_filter = ('proposer', 'category', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
