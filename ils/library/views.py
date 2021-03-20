from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse
from django.db import connection
from datetime import date

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

def details(request, bookid):
    c = connection.cursor()
    q = f"SELECT * FROM BOOK WHERE BOOKID = {bookid}"
    c.execute(q)
    result = c.fetchone()
    return render(request, "library/book.html", {
        "book": result
    })

def borrow(request, bookid):
    c = connection.cursor()
    q = f"UPDATE BOOK SET AVAILABILITY = 'BORROWED' WHERE BOOKID = {bookid}"
    c.execute(q)
    '''
    value = (bookid, 'Aldo', date.today().strftime("%Y-%m-%d"), 'BORROWED', 0)
    q = f"INSERT INTO BORROWS VALUES {value}"
    c.execute(q)
    '''
    return HttpResponseRedirect(reverse("index"))

def reserve(request, bookid):
    c = connection.cursor()
    q = f"UPDATE BOOK SET AVAILABILITY = 'RESERVED' WHERE BOOKID = {bookid}"
    c.execute(q)
    q = "SELECT * FROM BOOK"
    c.execute(q)
    results = c.fetchall()
    return HttpResponseRedirect(reverse("index"))

def restore(request, bookid):
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

def borrowed(request):
    c = connection.cursor()
    q = f"SELECT * FROM BOOK WHERE AVAILABILITY = 'BORROWED'"
    c.execute(q)
    results = c.fetchall()
    return render(request, "library/index.html", {
        "books": results
    })

def reserved(request):
    c = connection.cursor()
    q = f"SELECT * FROM BOOK WHERE AVAILABILITY = 'RESERVED'"
    c.execute(q)
    results = c.fetchall()
    return render(request, "library/index.html", {
        "books": results
    })

'''
def register(request):
    return render(request, "library/login.html")

def login(request):
    return render(request, "library/login.html")

def logout(request):
    return render(request, "library/login.html")
'''