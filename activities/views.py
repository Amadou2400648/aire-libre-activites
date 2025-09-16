
from django.shortcuts import render,redirect
from django.contrib.auth import logout, authenticate, login
from django.http import HttpResponse
from .forms import SignupForm, LoginForm
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

User = get_user_model()

#page d'accueil
def index(request):
    return render(request, "activities/index.html")

#inscription ou affichage de la page d'inscription
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])

            avatar = form.cleaned_data.get('avatar')
            if avatar:
                fs = FileSystemStorage()
                filename = fs.save(avatar.name, avatar)
                uploaded_file_url = fs.url(filename)
                user.avatar = filename

            bio = form.cleaned_data.get('bio')
            if bio:
                user.bio = bio

            user.save()

            messages.success(request, "Votre compte a été créé avec succès !")
            return redirect('login')
    else:
        form = SignupForm()

    return render(request, 'activities/signup.html', {
        'title': "Formulaire d'inscription",
        'form': form
    })

#cocnnexion ou affichage de la page de connexion
def login_user(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue {user.first_name} !")
                return redirect('index')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:

        form = LoginForm()

    return render(request, 'activities/login.html', {
        'title': "Formulaire de connexion",
        'form': form
    })

def logout_user(request):
    logout(request)

    storage = messages.get_messages(request)
    for _ in storage:
        pass
    return redirect('login')

def profil(request):
    if not request.user.is_authenticated:
        raise PermissionDenied("Vous devez être connecté pour accéder à cette page.")

    user = request.user

    return render(request, 'activities/profil.html',{'user':user,'title': "Mon profil",})

def update_profil(request):
    if not request.user.is_authenticated:
        raise PermissionDenied("Vous devez être connecté pour accéder à cette page.")

    user = request.user

    if request.method == "POST":

        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        bio = request.POST.get('bio', '').strip()
        avatar = request.FILES.get('avatar')

        errors = {}
        if not first_name:
            errors['first_name'] = "Le prénom est requis."
        if not last_name:
            errors['last_name'] = "Le nom est requis."
        if not email:
            errors['email'] = "Le courriel est requis."

        # Vérifier que le username/email n'existe pas chez un autre utilisateur
        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            errors['email'] = "Ce courriel est déjà utilisé."

        if errors:
            return render(request, 'activities/update-profil.html', {
                'user': user,
                'errors': errors,
                'title': "Formulaire de modification du profil",
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'bio': bio
            })

        # Mise à jour des informations
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.bio = bio or ''

        if avatar:
            fs = FileSystemStorage()
            filename = fs.save(avatar.name, avatar)
            user.avatar = filename

        user.save()
        messages.success(request, "Votre profil a été modifié avec succès !")
        return redirect('profil')

    else:
        # GET : afficher le formulaire avec les valeurs actuelles
        return render(request, 'activities/update-profil.html', {
            'user': user,
            'title': "Formulaire de modification du profil",
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'bio': user.bio or ''
        })


def proposer_activite():
    return HttpResponse("Hello, world")
