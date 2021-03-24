from django.urls import path
from . import views

urlpatterns = [
    # MAIN FUNCTIONALITY
    path("", views.index, name="index"),
    path("books/<int:bookid>", views.details, name="details"),
    path("search", views.search, name="search"),
    path("borrow/<int:bookid>", views.borrow, name="borrow"),
    path("extend/<int:bookid>", views.extend, name="extend"),
    path("reserve/<int:bookid>", views.reserve, name="reserve"),
    path("restore/<int:bookid>", views.restore, name="restore"),

    # MEMBER USER
    path("myaccount/borrowings", views.myborrowings, name="myborrowings"),
    path("myaccount/reservations", views.myreservations, name="myreservations"),
    path("myaccount/fees", views.myfees, name="myfees"),

    # ADMIN USER
    path("books/borrowed", views.borrowed, name="borrowed"),
    path("books/reserved", views.reserved, name="reserved"),
    
    # USER AUTHENTICATION
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
]