from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse
from django.db import connection

from . models import Book

# Create your views here.
def index(request):
    c = connection.cursor()
    q = "SELECT * FROM BOOK"
    c.execute(q)
    results = c.fetchall()
    return render(request, "library/index.html", {
        "books": results
    })

def details(request):
    return HttpResponse("")

def borrow(request, bookid):
    c = connection.cursor()
    q = f"UPDATE BOOK SET AVAILABILITY = 'BORROWED' WHERE BOOKID = {bookid}"
    c.execute(q)
    q = "SELECT * FROM BOOK"
    c.execute(q)
    results = c.fetchall()
    return HttpResponseRedirect(reverse("index"))

def reserve(request, bookid):
    c = connection.cursor()
    q = f"UPDATE BOOK SET AVAILABILITY = 'RESERVED' WHERE BOOKID = {bookid}"
    c.execute(q)
    q = "SELECT * FROM BOOK"
    c.execute(q)
    results = c.fetchall()
    return HttpResponseRedirect(reverse("index"))

def reset(request, bookid):
    c = connection.cursor()
    q = f"UPDATE BOOK SET AVAILABILITY = 'AVAILABLE' WHERE BOOKID = {bookid}"
    c.execute(q)
    q = "SELECT * FROM BOOK"
    c.execute(q)
    results = c.fetchall()
    return HttpResponseRedirect(reverse("index"))

def search(request):
    title = request.GET["q"]
    # if the query matches
    c = connection.cursor()
    q = f"SELECT * FROM BOOK WHERE TITLE REGEXP '{title}'"
    c.execute(q)
    results = c.fetchall()
    return render(request, "library/index.html", {
        "books": results
    })