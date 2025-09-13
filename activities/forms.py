from django import forms
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
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

        # Vérifier unicité username et email
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        if username and User.objects.filter(username=username).exists():
            self.add_error('username', "Ce nom d'utilisateur existe déjà.")
        if email and User.objects.filter(email=email).exists():
            self.add_error('email', "Un compte avec ce courriel existe déjà.")

        # Vérifier que les mots de passe correspondent
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")
        if password and password_confirmation and password != password_confirmation:
            self.add_error('password_confirmation', "Les mots de passe ne correspondent pas.")

        # Vérifier le type de fichier et la taille
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