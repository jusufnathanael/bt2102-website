from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.db import connection
from datetime import date

from . models import Book, MemberUserForm, Memberuser

# TODO: add checkEmptySession() to all the functions below

def checkEmptySession(request):
    if "userid" not in request.session:
        request.session["userid"] = []
        request.session["message"] = []

def index(request):
    checkEmptySession(request)
    if not request.session["userid"]:
        return HttpResponseRedirect(reverse("login"))
    c = connection.cursor()
    q = "SELECT * FROM BOOK"
    c.execute(q)
    results = c.fetchall()
    message = ""
    if request.session["message"]:
        message = request.session["message"]
        request.session["message"] = []
    return render(request, "library/index.html", {
        "books": results,
        "message": message
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
    # select current book
    q = f"SELECT * FROM BOOK WHERE BOOKID = {bookid}"
    c.execute(q)
    book = c.fetchone()
    status = list(book)[2]
    if status == "AVAILABLE":
        # insert into the record and update the book status
        value = (bookid, request.session["userid"][0], date.today().strftime("%Y-%m-%d"), 'BORROWED', 0)
        q = f"INSERT INTO BORROWS VALUES {value}"
        c.execute(q)
        q = f"UPDATE BOOK SET AVAILABILITY = 'BORROWED' WHERE BOOKID = {bookid}"
        c.execute(q)
        message = "You have successfully borrowed the book."
    else:
        message = "Book is unavailable."
    # return to index
    request.session["message"] = message
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



# USER AUTHENTICATION

def register(request):
    checkEmptySession(request)
    # if logged in
    if request.session["userid"]:
        return HttpResponseRedirect(reverse("index"))
    if request.method == "POST":
        # get current userid and password
        userid = request.POST["userid"]
        password = request.POST["password"]
        # get all userids from the database
        c = connection.cursor()
        q = f"SELECT USERID FROM MEMBERUSER"
        c.execute(q)
        userids = c.fetchall()
        # if registration is successfull
        if (userid,) not in userids and userid and password:
            value = (userid, password)
            q = f"INSERT INTO MEMBERUSER VALUES {value}"
            c.execute(q)
            request.session["userid"] = [userid]
            return HttpResponseRedirect(reverse("index"))
        # if userid already existed
        else:
            # if either userid or password (or both) is blank
            if not userid or not password:
                message = "Please insert user ID and password."
            # if userid existed
            elif (userid,) in userids:
                message = "User ID existed."
            return render(request, "library/register.html", {
                "message": message
            })
    # render empty registration page
    return render(request, "library/register.html")

def login(request):
    checkEmptySession(request)
    # if logged in
    if request.session["userid"]:
        return HttpResponseRedirect(reverse("index"))
    if request.method == "POST" and not request.session["userid"]:
        # get current userid and password
        userid = request.POST["userid"]
        password = request.POST["password"]
        # get all userids from the database
        c = connection.cursor()
        q = f"SELECT USERID FROM MEMBERUSER"
        c.execute(q)
        userids = c.fetchall()
        # get all passwords from the database
        q = f"SELECT PASSWORD FROM MEMBERUSER"
        c.execute(q)
        passwords = c.fetchall()
        # if userid and password are correct
        if ((userid,) in userids) and ((password,) in passwords):
            request.session["userid"] = [userid]
            return HttpResponseRedirect(reverse("index"))
        else:
            # if userid exist but no password
            if ((userid,) in userids) and (password is None):
                message = "Please input the password."
                id = userid
            # if userid exist but incorrect password
            elif ((userid,) in userids) and ((password,) not in passwords):
                message = "Incorrect password."
                id = userid
            # if userid does not exist
            elif (userid,) not in userids:
                message = "User ID does not exist."
                id = ''
            return render(request, "library/login.html", {
                "message": message,
                "id": id
            })
    # render empty login page
    return render(request, "library/login.html")

def logout(request):
    # clear userid from session
    request.session["userid"] = []
    return HttpResponseRedirect(reverse("login"))
