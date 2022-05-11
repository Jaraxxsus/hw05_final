from django.urls import path

from . import views

app_name = "about"

urlpatterns = [
    path("author/", views.AboutAuthorView.as_view(), name="author"),
    path("tech/", views.AboutTechnologyView.as_view(), name="technology")
]
