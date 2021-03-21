from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.db import connection
from datetime import date

from . models import Book, MemberUserForm, Memberuser

# Create your views here.
def index(request):
    if "userid" not in request.session:
        request.session["userid"] = []
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


def register(request):
    if request.method == "POST":
        c = connection.cursor()
        value = (request.POST["userid"], request.POST["password"])
        q = f"INSERT INTO MEMBERUSER VALUES {value}"
        c.execute(q)
        request.session["userid"] = [request.POST["userid"]]
        return HttpResponseRedirect(reverse("index"))
    return render(request, "library/register.html")

def login(request):
    print(request.session["userid"])
    if request.session["userid"]:
        return HttpResponseRedirect(reverse("index"))
    if request.method == "POST" and not request.session["userid"]:
        userid = request.POST["userid"]
        password = request.POST["password"]
        c = connection.cursor()
        q = f"SELECT USERID FROM MEMBERUSER"
        c.execute(q)
        userids = c.fetchall()
        q = f"SELECT PASSWORD FROM MEMBERUSER"
        c.execute(q)
        passwords = c.fetchall()
        if ((userid,) in userids) and ((password,) in passwords):
            request.session["userid"] = [userid]
            return HttpResponseRedirect(reverse("index"))
        else:
            if ((userid,) in userids) and (password is None):
                message = "Please input the password."
                id = userid
            elif ((userid,) in userids) and ((password,) not in passwords):
                message = "Incorrect password."
                id = userid
            elif (userid,) not in userids:
                message = "User ID does not exist."
                id = ''
            return render(request, "library/login.html", {
                "message": message,
                "id": id
            })
    return render(request, "library/login.html")

def logout(request):
    print(request.session["userid"])
    request.session["userid"] = []
    return HttpResponseRedirect(reverse("login"))
