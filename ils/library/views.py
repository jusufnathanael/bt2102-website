from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.db import connection
from datetime import date, timedelta

# TODO: add initialiseEmptyUserID() to all the functions below

def initialiseEmptyUserID(request):
    if "userid" not in request.session:
        request.session["userid"] = []
        request.session["message"] = []

def index(request):
    initialiseEmptyUserID(request)
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


def myborrowings(request):
    initialiseEmptyUserID(request)
    if not request.session["userid"]:
        return HttpResponseRedirect(reverse("login"))
    userid = request.session["userid"][0]
    # get the borrow records
    c = connection.cursor()
    q = f"SELECT * FROM BORROWS WHERE USERID = '{userid}'"
    c.execute(q)
    borrows = c.fetchall()
    return render(request, "library/mybooks.html", {
        "borrows": borrows
    })

def myreservations(request):
    initialiseEmptyUserID(request)
    if not request.session["userid"]:
        return HttpResponseRedirect(reverse("login"))
    userid = request.session["userid"][0]
    # get the reserve records
    c = connection.cursor()
    q = f"SELECT * FROM RESERVES WHERE USERID = '{userid}'"
    c.execute(q)
    reserves = c.fetchall()
    return render(request, "library/mybooks.html", { 
        "reserves": reserves
    })

def myfees(request):
    # select records from the database
    userid = request.session["userid"][0]
    c = connection.cursor()
    q = f"SELECT BOOKID, USERID, DUEDATE, DATEDIFF(NOW(), DUEDATE) AS AMOUNT " \
        f"FROM BORROWS WHERE DATEDIFF(NOW(), DUEDATE) > 0 AND USERID = '{userid}'"
    c.execute(q)
    records = c.fetchall()
    # keep user's selections
    if request.method == "POST":
        # get selected bookids
        if "bookids" not in request.POST:
            return render(request, "library/payment.html", {
                "records": records,
                "total": 0
            })
        results = dict(request.POST)["bookids"]
        print(request.POST["button"])
        bookids = [int(i) for i in results]
        # calculate the sum of fine
        sum = 0
        for record in list(records):
            if list(record)[0] in bookids:
                sum += list(record)[3]
        type = request.POST["button"]
        # if calculate fees
        if type == "calculate fees":
            return render(request, "library/payment.html", {
                "records": records,
                "bookids": bookids,
                "total": sum
            })
        # if payment
        return render(request, "library/pay.html", {
            "total": sum
        })
    return render(request, "library/payment.html", {
        "records": records,
        "total": 0
    })


def borrow(request, bookid):
    initialiseEmptyUserID(request)
    if not request.session["userid"]:
        return HttpResponseRedirect(reverse("login"))
    c = connection.cursor()
    # select current book
    q = f"SELECT * FROM BOOK WHERE BOOKID = {bookid}"
    c.execute(q)
    book = c.fetchone()
    # if book does not exist
    if not book:
        message = "Book does not exist."
    # if book is available (not borrowed or reserved)
    elif list(book)[2] == "AVAILABLE":
        # check if the user has reached the borrowing limit
        userid = request.session["userid"][0]
        q = f"SELECT COUNT(*) FROM BORROWS GROUP BY USERID HAVING USERID = '{userid}'"
        c.execute(q)
        number = c.fetchone()
        if number and list(number)[0] >= 4:
            message = "You have reached your borrowing limit (max. 4 books)."
        else:
            # insert into the record and update the book status
            duedate = date.today() + timedelta(days=27)
            value = (bookid, userid, duedate.strftime("%Y-%m-%d"), 0)
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


def extend(request, bookid):
    initialiseEmptyUserID(request)
    if not request.session["userid"]:
        return HttpResponseRedirect(reverse("login"))
    c = connection.cursor()
    # select current book
    q = f"SELECT * FROM BOOK WHERE BOOKID = {bookid}"
    c.execute(q)
    book = c.fetchone()
    # if book does not exist
    if not book:
        message = "Book does not exist."
    else:
        # check if the user borrow the book
        userid = request.session["userid"][0]
        q = f"SELECT * FROM BORROWS WHERE USERID = '{userid}' AND BOOKID = {bookid}"
        c.execute(q)
        record = c.fetchone()
        # check if there is any other user reserving the book
        q = f"SELECT USERID FROM RESERVES WHERE BOOKID = {bookid}"
        c.execute(q)
        reservation = c.fetchone()
        if not record:
            message = "You are not borrowing this book."
        elif reservation:
            message = "There is another user reserving the book." 
        elif date.today() > list(record)[2]:
            message = "You have an outstanding fine. Please proceed to the payment before extending the book."
        elif list(record)[3] >= 2:
            message = "You have reached the extension limit. Please return the book first before further extension."
        elif (list(record)[2] - date.today()).days > 7:
            message = "You can extend the book at least 1 week in advance."
        # if the extension is succesfull:
        else:
            extension = list(record)[3] + 1
            print(extension)
            duedate = (list(record)[2] + timedelta(days=28)).strftime("%Y-%m-%d")
            q = f"UPDATE BORROWS SET EXTENSION = {extension}, DUEDATE = '{duedate}' WHERE BOOKID = {bookid} and USERID = '{userid}'"
            c.execute(q)
            message = "Extension is successfull."
    request.session["message"] = message
    return HttpResponseRedirect(reverse("index"))


def reserve(request, bookid):
    initialiseEmptyUserID(request)
    if not request.session["userid"]:
        return HttpResponseRedirect(reverse("login"))
    c = connection.cursor()
    # select current book
    q = f"SELECT * FROM BOOK WHERE BOOKID = {bookid}"
    c.execute(q)
    book = c.fetchone()
    # if book does not exist
    if not book:
        message = "Book does not exist."
    # if the book is being borrowed
    elif list(book)[2] == "BORROWED":
        # if the user is borrowing the book
        q = f"SELECT USERID FROM BORROWS WHERE BOOKID = {bookid}"
        c.execute(q)
        borrowUser = c.fetchone()
        userid = request.session["userid"][0]
        if (userid,) == borrowUser:
            message = "You have borrowed this book."
        # if the reservation is successfull
        else: 
            q = f"INSERT INTO RESERVES VALUES ({bookid}, '{userid}', NULL)"
            c.execute(q)
            q = f"UPDATE BOOK SET AVAILABILITY = 'RESERVED' WHERE BOOKID = {bookid}"
            c.execute(q)
            message = "You have succesfully reserved the book."
    # if the book is available to borrow
    elif list(book)[2] == "AVAILABLE":
        message = "Book is available, please go ahead to borrow the book."
    # if the book is currently reserved
    elif list(book)[2] == "RESERVED":
        message = "Book is being reserved, please try again later."
    request.session["message"] = message
    return HttpResponseRedirect(reverse("index"))


def restore(request, bookid):
    initialiseEmptyUserID(request)
    if not request.session["userid"]:
        return HttpResponseRedirect(reverse("login"))
    # select current book
    c = connection.cursor()
    q = f"SELECT * FROM BOOK WHERE BOOKID = {bookid}"
    c.execute(q)
    book = c.fetchone()
    # if book does not exist
    if not book:
        request.session["message"] = "Book does not exist."
        return HttpResponseRedirect(reverse("index"))
    # select userid and bookid from borrows
    userid = request.session["userid"][0]
    q = f"SELECT * FROM BORROWS WHERE USERID = '{userid}' AND BOOKID = {bookid}"
    c.execute(q)
    borrowRecord = c.fetchone()
    # if the user is not borrowing the book
    if not borrowRecord:
        request.session["message"] = f"You are not borrowing the book {book[1]}."
        return HttpResponseRedirect(reverse("index"))
    # check for fines
    bookid, userid, duedate, extension = borrowRecord
    # if the user needs to pay for fine
    if date.today() > duedate:
        fine = (date.today() - duedate).days
        request.session["message"] = f"You need to pay for the fine first."
        return render(request, "library/payment.html", {
            "fine": fine
        })
    # book returned successfully
    q = f"UPDATE BOOK SET AVAILABILITY = 'AVAILABLE' WHERE BOOKID = {bookid}"
    c.execute(q)
    q = f"DELETE FROM BORROWS WHERE USERID = '{userid}' and BOOKID = {bookid}"
    c.execute(q)
    # check for any book reservation
    q = f"SELECT BOOKID FROM RESERVES WHERE BOOKID = {bookid}"
    c.execute(q)
    result = c.fetchone()
    if result:
        duedate = date.today() + timedelta(days=13)
        d = duedate.strftime("%Y-%m-%d")
        q = f"UPDATE RESERVES SET DUEDATE = '{d}' WHERE BOOKID = {bookid}"
        c.execute(q)
        q = f"UPDATE BOOK SET AVAILABILITY = 'RESERVED' WHERE BOOKID = {bookid}"
        c.execute(q)
    else:
        q = f"UPDATE BOOK SET AVAILABILITY = 'AVAILABLE' WHERE BOOKID = {bookid}"
        c.execute(q)
    request.session["message"] = f"Book returned successfully."
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

    def isValid(userid, name, email, password):
        # get all userids and emails from the database
        c = connection.cursor()
        q = f"SELECT USERID FROM MEMBERUSER"
        c.execute(q)
        userids = c.fetchall()
        q = f"SELECT EMAIL FROM MEMBERUSER"
        c.execute(q)
        emails = c.fetchall()
        # values must be non-NULL and (userid, email) needs to be unique
        if (userid,) not in userids and (email,) not in emails and userid and name and email and password:
            return True
        return False
    
    def getInvalidMessages(userid, name, email, password):
        # get all userids and emails from the database
        c = connection.cursor()
        q = f"SELECT USERID FROM MEMBERUSER"
        c.execute(q)
        userids = c.fetchall()
        q = f"SELECT EMAIL FROM MEMBERUSER"
        c.execute(q)
        emails = c.fetchall()
        messages = []
        # values must be non-NULL
        if not name:
            messages += ["Please insert your name."]
        if not userid:
            messages += ["Please insert a user ID."]
        if not email:
            messages += ["Please insert an email."]
        if not password:
            messages += ["Please input a password."]
        # userid and email must be unique
        if (userid,) in userids:
            messages += ["This User ID has been registered."]
            userid = ""
        if (email,) in emails:
            messages += ["This email address has been registered."]
            email = ""
        return (messages, userid, email)

    initialiseEmptyUserID(request)
    # if logged in
    if request.session["userid"]:
        return HttpResponseRedirect(reverse("index"))
    if request.method == "POST":
        # get current userid, name, email, and password
        userid = request.POST["userid"]
        name = request.POST["name"]
        email = request.POST["email"]
        password = request.POST["password"]
        # if the registration is successfull
        if isValid(userid, name, email, password):
            c = connection.cursor()
            value = (userid, name, email, password)
            q = f"INSERT INTO MEMBERUSER VALUES {value}"
            c.execute(q)
            request.session["userid"] = [userid]
            request.session["message"] = "You have successfully registered."
            return HttpResponseRedirect(reverse("index"))
        # if registration fails
        messages, userid, email = getInvalidMessages(userid, name, email, password)
        return render(request, "library/register.html", {
            "messages": messages, "name": name, "userid": userid, "email": email
        })
    # render empty registration page
    return render(request, "library/register.html")


def login(request):
    initialiseEmptyUserID(request)
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
