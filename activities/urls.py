from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_user, name="login"),
    path('', views.proposer_activite, name='proposer_activite'),
    path("proposer/", views.proposer_activite, name="proposer_activite"),
    path("profil/<int:pk>/", views.profil, name="profil"),
    path("logout/", views.logout_user, name="logout"),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)