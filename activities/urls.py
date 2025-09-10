from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('', views.proposer_activite, name='proposer_activite'),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("proposer/", views.proposer_activite, name="proposer_activite"),
    path("profil/<int:pk>/", views.profil, name="profil"),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)