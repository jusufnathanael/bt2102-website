from django.urls import path
from . import views

urlpatterns = [
    # MAIN FUNCTIONALITIES
    path("", views.index, name="index"),
    path("books/<int:bookid>", views.details, name="details"),
    path("search", views.search, name="search"),

    # MEMBER USER FUNCTIONALITIES
    path("myaccount/", views.myaccount, name="myaccount"),
    path("borrow/<int:bookid>", views.borrow, name="borrow"),
    path("extend/<int:bookid>", views.extend, name="extend"),
    path("reserve/<int:bookid>", views.reserve, name="reserve"),
    path("restore/<int:bookid>", views.restore, name="restore"),
    path("cancel/<int:bookid>", views.cancel, name="cancel"),

    # ADMIN USER FUNCTIONALITIES
    path("admin/home", views.adminhome, name="adminhome"),
    path("admin/borrowings", views.adminborrowings, name="adminborrowings"),
    path("admin/reservations", views.adminreservations, name="adminreservations"),
    path("admin/fines", views.adminfines, name="adminfines"),
    path("admin/users", views.adminallusers, name="adminallusers"),
    
    # ADMIN USER AUTHENTICATION
    path("admin/login", views.adminlogin, name="adminlogin"),
    path("admin/logout", views.adminlogout, name="adminlogout"),

    # MEMBER USE AUTHENTICATION
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
]