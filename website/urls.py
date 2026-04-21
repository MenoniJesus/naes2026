from django.urls import include, path

from .views import ContatoView, IndexView, RegisterView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("contato/", ContatoView.as_view(), name="contato"),
    path("register/", RegisterView.as_view(), name="register"),
    path("", include("django.contrib.auth.urls")),
]