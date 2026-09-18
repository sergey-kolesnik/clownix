"""Маршруты приложения blog."""

from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.home, name="home"),
    path("category/<slug:slug>/", views.category_view, name="category"),
    path("post/<slug:slug>/", views.post_detail, name="post_detail"),
    path("search/", views.search, name="search"),
]
