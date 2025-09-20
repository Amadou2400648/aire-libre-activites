from django import forms
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from .models import Activity
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
import os

User = get_user_model()

class SignupForm(forms.ModelForm):
    first_name = forms.CharField(required=True, label="Prénom",error_messages={'required': 'Ce champ est obligatoire.'})
    last_name = forms.CharField(required=True, label="Nom",error_messages={'required': 'Ce champ est obligatoire.'})
    email = forms.EmailField(required=True, label="Courriel",error_messages={'required': 'Ce champ est obligatoire.'})
    username = forms.CharField(required=True, label="Nom d'utilisateur",error_messages={'required': 'Ce champ est obligatoire.'})
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Mot de passe",error_messages={'required': 'Ce champ est obligatoire.'})
    password_confirmation = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirmer le mot de passe",error_messages={'required': 'Ce champ est obligatoire.'})
    avatar = forms.ImageField(required=False, label="Avatar")
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False, label="Biographie")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if username and User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            self.add_error('username', "Ce nom d'utilisateur existe déjà.")

        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            self.add_error('email', "Un compte avec ce courriel existe déjà.")

        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")
        if password and password_confirmation and password != password_confirmation:
            self.add_error('password_confirmation', "Les mots de passe ne correspondent pas.")


        avatar = cleaned_data.get('avatar')
        if avatar:
            ext = os.path.splitext(avatar.name)[1].lower()
            if ext not in ['.png', '.jpg', '.jpeg']:
                self.add_error('avatar', "Le fichier doit être au format PNG, JPG ou JPEG.")

            if avatar.size > 5 * 1024 * 1024:
                self.add_error('avatar', "Le fichier est trop volumineux (5MB maximum).")

class LoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': "Ce champ est obligatoire."}
    )
    password = forms.CharField(
        required=True,
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={'required': "Ce champ est obligatoire."}
    )

class ActivityForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        label="Date et heure de début",
        error_messages={
            "required": "La date et l'heure de début sont obligatoires.",
            "invalid": "Format de date et heure invalide."
        }
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        label="Date et heure de fin",
        error_messages={
            "required": "La date et l'heure de fin sont obligatoires.",
            "invalid": "Format de date et heure invalide."
        }
    )

    class Meta:
        model = Activity
        fields = ["title", "description", "location_city", "category", "start_time", "end_time"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "location_city": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "title": "Titre",
            "description": "Description",
            "location_city": "Ville",
            "category": "Catégorie (facultatif)"
        }
        help_texts = {
            "category": "Ce champ est facultatif."
        }
        error_messages = {
            "title": {
                "required": "Le titre est obligatoire.",
            },
            "description": {
                "required": "La description est obligatoire.",
            },
            "location_city": {
                "required": "La ville est obligatoire.",
            }
        }

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if title and len(title) < 5:
            raise ValidationError("Le titre doit contenir au moins 5 caractères.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get("description")
        if description and len(description) < 10:
            raise ValidationError("La description doit contenir au moins 10 caractères.")
        return description

    def clean_location_city(self):
        city = self.cleaned_data.get("location_city")
        if city and len(city) < 2:
            raise ValidationError("Le nom de la ville doit contenir au moins 2 caractères.")
        return city

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")
        if start and end and end <= start:
            self.add_error("end_time", "La date de fin doit être postérieure à la date de début.")
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        label="Date et heure de début",
        error_messages={
            "required": "La date et l'heure de début sont obligatoires.",
            "invalid": "Format de date et heure invalide."
        }
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        label="Date et heure de fin",
        error_messages={
            "required": "La date et l'heure de fin sont obligatoires.",
            "invalid": "Format de date et heure invalide."
        }
    )
