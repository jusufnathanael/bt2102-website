from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("books/<int:bookid>", views.details, name="details"),
    path("borrow/<int:bookid>", views.borrow, name="borrow"),
    path("reserve/<int:bookid>", views.reserve, name="reserve"),
    path("restore/<int:bookid>", views.restore, name="restore"),
    path("search", views.search, name="search"),

    # ADMIN USER
    path("books/borrowed", views.borrowed, name="borrowed"),
    path("books/reserved", views.reserved, name="reserved"),
    
    # USER AUTHENTICATION
    # path("register", views.register, name="register"),
    # path("login", views.login, name="login"),
    # path("logout", views.logout, name="logout"),
]