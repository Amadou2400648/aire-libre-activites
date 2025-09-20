"""
Ce module contient les vues pour gérer les activités,
l'inscription des utilisateurs et la connexion.
"""

from datetime import datetime

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone

from .forms import ActivityForm, LoginForm, SignupForm
from .models import Activity, Category


User = get_user_model()


def index(request):
    """Permet d'afficher la liste des activités à l'accueil"""
    view_filter = request.GET.get("view", "toutes_activites")
    category = request.GET.get("category")
    liste_categories = Category.objects.all()

    activities = Activity.objects.filter(start_time__gte=timezone.now()).order_by("start_time")

    if category and category != "None":
        activities = activities.filter(category_id=category)

    if view_filter == "mes_activites" and request.user.is_authenticated:
        activities = activities.filter(proposer=request.user)
    elif view_filter == "mes_inscriptions" and request.user.is_authenticated:
        activities = activities.filter(attendees=request.user)

    paginator = Paginator(activities, 3)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    context = {
        "page": page,
        "categories":liste_categories,
        "view_filter": view_filter,
        "category_filter": category,
    }
    return render(request, "activities/index.html", context)


def signup(request):
    """Permet d'afficher la page d'inscription ou de soumettre le formulaire d'inscription"""
    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])

            avatar = form.cleaned_data.get('avatar')
            if avatar:
                now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"user_avatar_{now_str}"

                fs = FileSystemStorage()
                saved_filename = fs.save(filename, avatar)
                user.avatar = saved_filename

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


def login_user(request):
    """Permet de se connecter ou d'afficher de la page de connexion"""
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
    """Permet de se déconnecter"""
    if not request.user.is_authenticated:
        raise PermissionDenied("Vous devez être connecté pour accéder à cette page.")

    logout(request)
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    return redirect('login')


def profil(request):
    """Permet d'afficher la page du profil"""
    if not request.user.is_authenticated:
        raise PermissionDenied("Vous devez être connecté pour accéder à cette page.")

    user = request.user

    activites_proposees = Activity.objects.filter(proposer=user).order_by('-start_time')
    inscriptions = Activity.objects.filter(attendees=user).order_by('-start_time')

    context = {
        'user': user,
        'title': "Mon profil",
        'activites_proposees': activites_proposees,
        'inscriptions': inscriptions,
    }
    return render(request, 'activities/profil.html', context)


def update_profil(request):
    """Permet de modifier le profil utilisateur"""
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

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.bio = bio or ''

        if avatar:
            now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"user_avatar_{now_str}"

            fs = FileSystemStorage()
            saved_filename = fs.save(filename, avatar)
            user.avatar = saved_filename

        user.save()
        messages.success(request, "Votre profil a été modifié avec succès !")
        return redirect('profil')

    else:

        return render(request, 'activities/update-profil.html', {
            'user': user,
            'title': "Formulaire de modification du profil",
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'bio': user.bio or ''
        })


def proposer_activite(request):
    """Permet d'enregistrer une activité ou d'afficher le formulaire d'enregistrement des activités"""
    if not request.user.is_authenticated:
        raise PermissionDenied("Vous devez être connecté pour accéder à cette page.")

    if request.method == "POST":
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.proposer = request.user
            activity.save()
            messages.success(request, "L'activité a été créée avec succès !")
            return redirect("index")
    else:
        form = ActivityForm()

    return render(request, "activities/activity_create.html", {"form": form})


def get_air_quality(city: str):
    """Permet de se connecter à l'API et d'avoir les informations de la qualité de l'air"""
    token = settings.AQICN_TOKEN
    api_url = f"https://api.waqi.info/feed/{city}/?token={token}"

    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                air_quality = data["data"]["aqi"]
                return air_quality if air_quality is not None else "Non disponible"
            else:
                return "Ville introuvable"
        return "Erreur API"
    except requests.RequestException:
        return "Qualité de l'air non disponible"


def activity_detail(request, pk):
    """Permet d'afficher les détails d'une activité"""
    activity = get_object_or_404(Activity, pk=pk)
    air_quality = get_air_quality(activity.location_city)

    est_inscrit = activity.attendees.filter(id=request.user.id).exists()

    if request.method == "POST":
        if "inscrit" in request.POST:
            activity.attendees.add(request.user)
            return redirect("activity_detail", activity.id)
        elif "desinscrit" in request.POST:
            activity.attendees.remove(request.user)
            return redirect("activity_detail", activity.id)

    context = {
        "activity": activity,
        "air_quality": air_quality,
        "est_inscrit": est_inscrit,
    }
    return render(request, "activities/detail-activite.html", context)
