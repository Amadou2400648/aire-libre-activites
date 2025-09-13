
from django.shortcuts import render,redirect
from django.contrib.auth import logout, authenticate, login
from django.http import HttpResponse
from .forms import SignupForm, LoginForm
from django.contrib import messages
from django.core.files.storage import FileSystemStorage


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

def profil():
    return HttpResponse("Hello, world")


def proposer_activite():
    return HttpResponse("Hello, world")
