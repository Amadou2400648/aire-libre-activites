"""
Ce module contient les models qui vont générer la base de données
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinLengthValidator, MaxLengthValidator

class User(AbstractUser):
    """Modifie le modèle User par défaut pour l’adapter à notre application."""
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)

    ADMIN = 1
    PARTICIPANT = 2
    ORGANISATEUR = 3

    ROLES_UTILISATEURS = [
        (ADMIN, 'Admin'),
        (PARTICIPANT, 'Participant'),
        (ORGANISATEUR, 'Organisateur'),
    ]

    role = models.PositiveSmallIntegerField(
        choices=ROLES_UTILISATEURS,
        blank=True,
        null=True,
        verbose_name="Rôle",
    )

    class Meta:
        """Classe interne pour définir des options de configuration du modèle. """
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        default_related_name = 'users_%(class)s_set'
        ordering = ["username"]

    def __str__(self):
        """Renvoie une représentation lisible de l'objet, ici le nom d'utilisateur."""
        return f"{self.username}"

class Category(models.Model):
    """Modèle représentant une catégorie pour les activités."""
    name = models.CharField(verbose_name="Nom de la catégorie", max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        """Options supplémentaires pour le modèle Category."""
        verbose_name="Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["-created_at"]

    def __str__(self):
        """Représentation lisible de l'objet : affiche le nom de la catégorie."""
        return str(self.name)

def validate_start(value):
    """Vérifie que la date de début d'une activité est dans le futur."""
    if value < timezone.now():
        raise ValidationError("La date de début doit être dans le futur.")

class Activity(models.Model):
    """Modèle représentant une activité"""
    title = models.CharField(verbose_name="Titre",
                             validators=[MinLengthValidator(5), MaxLengthValidator(200)])
    description = models.CharField(verbose_name="Description",
                                   validators=[MinLengthValidator(10)],max_length=500)
    location_city = models.CharField(verbose_name="Ville",
                                     validators=[MinLengthValidator(2), MaxLengthValidator(100)])
    start_time = models.DateTimeField(verbose_name="Date et heure de début",
                                      validators=[validate_start])
    end_time = models.DateTimeField(verbose_name="Date et heure de fin")
    proposer = models.ForeignKey(User, verbose_name="Organisateur",
                                 related_name='proposed_activities', on_delete=models.CASCADE)
    attendees = models.ManyToManyField(User, verbose_name="Participants",
                                       related_name='attended_activities')
    category = models.ForeignKey(Category, verbose_name="Catégorie",
                                 related_name='activities',
                                 on_delete=models.SET_NULL,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """Valide que la date de fin d'une activité est après la date de début."""
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError("La date de fin doit être postérieure à la date de début.")
    class Meta:
        """Options supplémentaires pour le modèle Activity."""
        verbose_name="Activité"
        verbose_name_plural = "Activités"
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.title)
