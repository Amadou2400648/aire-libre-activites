from django.db import models

class Category(models.Model):
    name = models.CharField(verbose_name="Nom de la catégorie", max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Catégories"
        ordering = ["name"]

    def __str__(self):
        return str(self.name)


class Activity(models.Model):
    title = models.CharField(verbose_name="Titre", max_length=255)
    description = models.CharField(verbose_name="Description", max_length=255)
    location_city = models.CharField(verbose_name="Ville", max_length=255)
    start_time = models.DateTimeField(verbose_name="Date et heure de début")
    end_time = models.DateTimeField(verbose_name="Date et heure de fin")

