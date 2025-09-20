
from django.shortcuts import render,redirect
from django.contrib.auth import logout, authenticate, login
from django.http import HttpResponse
from .forms import SignupForm, LoginForm, ActivityForm
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from .models import Activity, Category
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.shortcuts import get_object_or_404
import requests
from django.urls import reverse

User = get_user_model()

#page d'accueil
def index(request):
    view_filter = request.GET.get("view", "all")
    category = request.GET.get("category")

    activities = Activity.objects.filter(start_time__gte=timezone.now()).order_by("start_time")

    if category and category != "None":
        activities = activities.filter(category_id=category)

    if view_filter == "mine" and request.user.is_authenticated:
        activities = activities.filter(proposer=request.user)
    elif view_filter == "attending" and request.user.is_authenticated:
        activities = activities.filter(attendees=request.user)

    paginator = Paginator(activities, 3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "view_filter": view_filter,
        "category_filter": category,
    }
    return render(request, "activities/index.html", context)

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

#deconnexion de l'utilisateur
def logout_user(request):
    logout(request)

    storage = messages.get_messages(request)
    for _ in storage:
        pass
    return redirect('login')

#Affichage du profil
def profil(request):
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

#Modification du profil
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
            fs = FileSystemStorage()
            filename = fs.save(avatar.name, avatar)
            user.avatar = filename

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

#Formulaire pour l'enregistrement de l'activité
def proposer_activite(request):
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

#Détail de l'activité
def activity_detail(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    aqi = None

    try:
        api_url = f"https://api.waqi.info/feed/{activity.location_city}/?token=233817a21811b13d4cd9a4d15eaece97973ed527"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            aqi = data["data"]["aqi"]
    except Exception:
        aqi = "Non disponible"

    connecte = False
    if request.user.is_authenticated:
        connecte = activity.attendees.filter(id=request.user.id).exists()

        if request.method == "POST":
            if "inscrit" in request.POST:
                activity.attendees.add(request.user)
                return redirect(reverse("activity_detail", args=[activity.id]))
            elif "desinscrit" in request.POST:
                activity.attendees.remove(request.user)
                return redirect(reverse("activity_detail", args=[activity.id]))

    context = {
        "activity": activity,
        "aqi": aqi,
        "connecte": connecte,
    }
    return render(request, "activities/detail-activite.html", context)
