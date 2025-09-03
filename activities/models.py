from django.db import models
from django.contrib.auth.models import AbstractUser,Group, Permission
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinLengthValidator, MaxLengthValidator

class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True,blank=True )
    bio = models.TextField(max_length=500, null=True,blank=True )

    groups = models.ManyToManyField(
        Group,
        verbose_name="groupes",
        blank=True,
        related_name="custom_user_set"
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="permissions utilisateur",
        blank=True,
        related_name="custom_user_set"
    )
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        default_related_name = 'users_%(class)s_set'

    def __str__(self):
        return str(self.username)

class Category(models.Model):
    name = models.CharField(verbose_name="Nom de la catégorie", max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name="Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.name)


def validate_start(value):
    if value < timezone.now():
        raise ValidationError("La date de début doit être dans le futur.")

class Activity(models.Model):
    title = models.CharField(verbose_name="Titre", validators=[MinLengthValidator(5), MaxLengthValidator(200)])
    description = models.CharField(verbose_name="Description", validators=[MinLengthValidator(10)])
    location_city = models.CharField(verbose_name="Ville", validators=[MinLengthValidator(2), MaxLengthValidator(100)])
    start_time = models.DateTimeField(verbose_name="Date et heure de début",validators=[validate_start])
    end_time = models.DateTimeField(verbose_name="Date et heure de fin")
    proposer = models.ForeignKey(User, verbose_name="Organisateur", related_name='proposed_activities', on_delete=models.CASCADE)
    attendees = models.ManyToManyField(User, verbose_name="Participants", related_name='attended_activities')
    category = models.ForeignKey(Category, verbose_name="Catégorie", related_name='activities',on_delete=models.SET_NULL,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError("La date de fin doit être postérieure à la date de début.")
    class Meta:
        verbose_name="Activité"
        verbose_name_plural = "Activités"
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.title)