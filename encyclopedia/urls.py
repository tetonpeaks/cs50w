from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:name>", views.wikipage, name="wikipage"),
    path("search", views.search, name="search"),
    path("newwiki", views.newwiki, name="newwiki"),
    path("wiki/editwiki/<str:name>", views.editwiki, name="editwiki"),
    path("randomwiki", views.randomwiki, name="randomwiki"),
]
