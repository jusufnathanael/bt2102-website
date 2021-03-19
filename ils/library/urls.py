from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("books/<int:book>id", views.details, name="details"),
    path("borrow/<int:bookid>", views.borrow, name="borrow"),
    path("reserve/<int:bookid>", views.reserve, name="reserve"),
    path("reset/<int:bookid>", views.reset, name="reset"),
    path("search", views.search, name="search")
]