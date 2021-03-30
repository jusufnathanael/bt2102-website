from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse
from django.db import connection
from datetime import date, timedelta, datetime
import pymongo, re

from .helper import checkUnpaidFines, initialiseEmptyMessage, getSessionMessage
from .helper import getSearchResult, getCategories, formatBook, getBookIDs, convertToInteger
from .helper import getDueDate, getDueDatesForIndex, getDueDatesForSearch

def handler404(request, exception):
    return render(request, 'library/404.html', {})
    
# MAIN FUNCTIONALITY

def index(request):
    if "userid" not in request.session:
        if "admin" in request.session:
            request.session["message"] = "Please log out and sign in as a member user."
            return HttpResponseRedirect(reverse("adminhome"))
        return HttpResponseRedirect(reverse("login"))
    # get system messages
    message = getSessionMessage(request)
    
    userid = request.session["userid"][0]
    checkUnpaidFines(userid)

    # get all books from MongoDB
    myclient = pymongo.MongoClient("mongodb://localhost:27017")
    mydb = myclient['books']
    mycol = mydb['libbooks']
    m = mycol.find({})

    # get book ids and availabilities
    c = connection.cursor()
    q = "SELECT BOOKID, AVAILABILITY FROM BOOK"
    c.execute(q)
    booksall = c.fetchall()
    # get due dates
    duedates = getDueDatesForIndex(booksall)
    # format books
    books = formatBook(m, booksall, [], duedates, 0)
    # get all categories
    allcategories = getCategories(mycol)
    
    return render(request, "library/index.html", {
        "books": books,
        "message": message,
        "allcategories": allcategories
    })


def search(request):
    if "userid" not in request.session:
        if "admin" in request.session:
            request.session["message"] = "Please log out and sign in as a member user."
            return HttpResponseRedirect(reverse("adminhome"))
        return HttpResponseRedirect(reverse("login"))
    # get system messages
    message = getSessionMessage(request)

    initialiseEmptyMessage(request)
    if "userid" not in request.session:
        return HttpResponseRedirect(reverse("index"))

    userid = request.session["userid"][0]
    checkUnpaidFines(userid)
    
    # get search inputs
    title = request.GET["qt"]
    author = request.GET["qa"]
    categories = request.GET.getlist("qc")
    year = request.GET["qy"]

    # format input categories
    string_categories = ""
    for category in categories:
        string_categories += category + "|"
    string_categories = string_categories[:-1]

    # connect to MongoDB and get search results
    myclient = pymongo.MongoClient("mongodb://localhost:27017")
    mydb = myclient['books']
    mycol = mydb['libbooks']
    search = getSearchResult(mycol, title, author, string_categories, year)
    
    # get book ids and availabilities
    c = connection.cursor()
    q = "SELECT BOOKID, AVAILABILITY FROM BOOK"
    c.execute(q)
    booksall = c.fetchall()
    # get book IDs
    bookids = getBookIDs(search)
    # get due dates
    duedates = getDueDatesForSearch(booksall, bookids)
    # format books
    search = getSearchResult(mycol, title, author, string_categories, year)
    books = formatBook(search, booksall, bookids, duedates, 1)
    # get all categories
    allcategories = getCategories(mycol)

    return render(request, "library/index.html", {
        "books": books,
        "allcategories": allcategories,
        "title": title, "categories": categories,
        "year": year, "author": author, "message": message
    })


def details(request, bookid):

    if "userid" not in request.session:
        if "admin" in request.session:
            request.session["message"] = "Please log out and sign in as a member user."
            return HttpResponseRedirect(reverse("adminhome"))
        return HttpResponseRedirect(reverse("login"))
    # get system messages
    message = getSessionMessage(request)

    userid = request.session["userid"][0]
    checkUnpaidFines(userid)

    c = connection.cursor()
    q = f"SELECT * FROM BOOK WHERE BOOKID = {bookid}"
    c.execute(q)
    result = c.fetchone()
    # if book does not exist
    if not result:
        request.session["message"] = "Book does not exist."
        return HttpResponseRedirect(reverse("index"))
    # connect to MongoDB
    myclient = pymongo.MongoClient("mongodb://localhost:27017")
    mydb = myclient['books']
    mycol = mydb['libbooks']
    book = mycol.find({"_id": bookid})
    # format book into list
    book = list(list(book)[0].values())
    # format published date, categories, and authors
    publisheddate = re.findall("([0-9]{4}-[0-9]{2}-[0-9]{2})", book[4])[0]
    book[4] = datetime.strptime(publisheddate, "%Y-%m-%d").date() # published date
    book[9] = book[9].strip('\'][\'').split('\', \'') # authors
    book[10] = book[10].strip('\'][\'').split('\', \'') # categories
    
    c = connection.cursor()
    q = f"SELECT BOOKID, AVAILABILITY FROM BOOK WHERE BOOKID = {bookid}"
    c.execute(q)
    result = c.fetchone()
    # get due dates
    duedate = getDueDate(result)
    # insert availability and due date to book
    book += [result[1]]
    book += duedate
    # get all categories
    allcategories = getCategories(mycol)
    return render(request, "library/book.html", {
        "book": book,
        "allcategories": allcategories
    })



# MEMBER ACCESS

def myaccount(request):

    def getParams(request):
        params = ["name_card", "month", "year", "card_no", "cvv", "name_address",
                  "country", "address", "postcode", "blok", "unit"]
        result = []
        for param in params:
            result += [request.POST[param]]
        return result

    def returnParams(request, details, records, total, ids, message):
        return render(request, "library/payment.html", {
            "name_card": details[0], "month": details[1], "year": details[2],
            "card_no": details[3], "cvv": details[4], "name_address": details[5],
            "country": details[6], "address": details[7], "postcode": details[8],
            "blok": details[9], "unit": details[10], "message": message,
            "outstandings": records, "total": total, "bookids": ids
        })

    def payment(request, borrows, reserves, outstandings):
        button = request.POST["button"]
        
        # if the user wants to check out
        if button == "CHECK OUT":
            details = getParams(request)
            bookids = request.POST.getlist("ids")
            bookids = convertToInteger(bookids)
            # if there are missing fileds except block and unit
            i = 0
            for detail in details:
                if i is not 9 and i is not 10 and detail is "":
                    total = request.POST["total"]
                    message = "Please fill in the missing fields."
                    return returnParams(request, details, outstandings, total, bookids, message)
                i += 1
            # if the payment is successful
            if len(bookids) == 1:
                q_delete = f"DELETE FROM BORROWS WHERE BOOKID = {bookids[0]}"
                q_update = f"UPDATE BOOK SET AVAILABILITY = 'AVAILABLE' WHERE BOOKID = {bookids[0]}"
            else:
                q_delete = f"DELETE FROM BORROWS WHERE BOOKID IN {tuple(bookids)}"
                q_update = f"UPDATE BOOK SET AVAILABILITY = 'AVAILABLE' WHERE BOOKID IN {tuple(bookids)}"
            # update the database
            c = connection.cursor()
            c.execute(q_delete)
            c.execute(q_update)
            request.session["message"] = "Payment successful."
            return HttpResponseRedirect(reverse("myaccount"))
        
        # get selected bookids
        if "bookids" not in request.POST:
            return render(request, "library/myaccount.html", {
                "borrows": borrows, "reserves": reserves,
                "outstandings": outstandings, "total": 0
            })
        results = dict(request.POST)["bookids"]
        bookids = [int(i) for i in results]
        # calculate total fine
        sum = 0
        for record in list(outstandings):
            if list(record)[0] in bookids:
                sum += list(record)[3]
        # if the user wants to calculate the fines
        if button == "Calculate":
            return render(request, "library/myaccount.html", {
                "borrows": borrows, "reserves": reserves,
                "outstandings": outstandings,
                "total": sum, "bookids": bookids
            })
        # if the user wants to pay
        if button == "Pay":
            return render(request, "library/payment.html", {
                "total": sum,
                "outstandings": outstandings,
                "bookids": bookids
            })

    if "userid" not in request.session:
        if "admin" in request.session:
            request.session["message"] = "Please log out and sign in as a member user."
            return HttpResponseRedirect(reverse("adminhome"))
        return HttpResponseRedirect(reverse("login"))
    # get system messages
    message = getSessionMessage(request)
    # get the borrow records
    userid = request.session["userid"][0]
    # if the user has unpaid fines, clear all reservations
    checkUnpaidFines(userid)
    c = connection.cursor()
    q = f"SELECT BOOKID, TITLE, DUEDATE, EXTENSION FROM "\
        f"BORROWS NATURAL JOIN BOOK WHERE USERID = '{userid}'"
    c.execute(q)
    borrows = c.fetchall()
    # get the reserve records
    q = f"WITH T AS (SELECT BOOKID AS TBOOKID, TITLE, DUEDATE AS RESERVEDATE "\
        f"FROM RESERVES NATURAL JOIN BOOK WHERE USERID = '{userid}') "\
        f"SELECT TBOOKID, TITLE, RESERVEDATE, DUEDATE AS BORROWDATE "\
        f"FROM T LEFT JOIN BORROWS ON BOOKID = TBOOKID"
    c.execute(q)
    reserves = c.fetchall()
    # get outstanding fees records
    c = connection.cursor()
    q = f"SELECT BOOKID, TITLE, DUEDATE, DATEDIFF(NOW(), DUEDATE) AS AMOUNT " \
        f"FROM BORROWS NATURAL JOIN BOOK WHERE DATEDIFF(NOW(), DUEDATE) > 0 AND USERID = '{userid}'"
    c.execute(q)
    outstandings = c.fetchall()
    # if the user press calculate or pay buttons
    if request.method == "POST":
        return payment(request, borrows, reserves, outstandings)
    return render(request, "library/myaccount.html", {
        "message": message,
        "borrows": borrows,
        "reserves": reserves,
        "outstandings": outstandings
    })


def borrow(request, bookid):
    initialiseEmptyMessage(request)
    if "userid" not in request.session:
        if "admin" in request.session:
            request.session["message"] = "Please log out and sign in as a member user."
            return HttpResponseRedirect(reverse("adminhome"))
        return HttpResponseRedirect(reverse("login"))
    userid = request.session["userid"][0]
    c = connection.cursor()
    # if the user has unpaid fines
    if checkUnpaidFines(userid):
        request.session["message"] = "You need to pay for the outstanding fees first."
        return HttpResponseRedirect(reverse("myaccount"))
    # select current book
    q = f"SELECT * FROM BOOK WHERE BOOKID = {bookid}"
    c.execute(q)
    book = c.fetchone()
    # check if the user is reserving the book
    q = f"SELECT USERID FROM RESERVES WHERE BOOKID = {bookid}"
    c.execute(q)
    reserve = c.fetchone()
    # check if another user is borrowing the book
    q = f"SELECT USERID FROM BORROWS WHERE BOOKID = {bookid}"
    c.execute(q)
    borrow = c.fetchone()
    # if book does not exist
    if not book:
        message = "Book does not exist."
    # if book is available (not borrowed or reserved) or the reserving user can now borrow the book
    elif list(book)[2] == "AVAILABLE" or (reserve and not borrow):
        # check if the user has reached the borrowing limit
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
            if reserve and not borrow:
                q = f"DELETE FROM RESERVES WHERE BOOKID = {bookid}"
                c.execute(q)
            message = "You have successfully borrowed the book."
    else:
        message = "Book is unavailable."
    # return to index
    request.session["message"] = message
    return HttpResponseRedirect(reverse("myaccount"))


def extend(request, bookid):
    initialiseEmptyMessage(request)
    if "userid" not in request.session:
        if "admin" in request.session:
            request.session["message"] = "Please log out and sign in as a member user."
            return HttpResponseRedirect(reverse("adminhome"))
        return HttpResponseRedirect(reverse("login"))
    # select current book
    c = connection.cursor()
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
        elif checkUnpaidFines(userid):
            request.session["message"] = "You need to pay for the outstanding fees first."
            return HttpResponseRedirect(reverse("myaccount"))
        elif reservation:
            message = "There is another user reserving the book."
        elif list(record)[3] >= 2:
            message = "You have reached the extension limit. Please return the book first before further extension."
        elif (list(record)[2] - date.today()).days > 7:
            message = "You can extend the book at most 1 week in advance."
        # if the extension is succesfull:
        else:
            extension = list(record)[3] + 1
            duedate = (list(record)[2] + timedelta(days=28)).strftime("%Y-%m-%d")
            q = f"UPDATE BORROWS SET EXTENSION = {extension}, DUEDATE = '{duedate}' WHERE BOOKID = {bookid} and USERID = '{userid}'"
            c.execute(q)
            message = "Extension is successful."
    request.session["message"] = message
    return HttpResponseRedirect(reverse("myaccount"))


def reserve(request, bookid):
    initialiseEmptyMessage(request)
    if "userid" not in request.session:
        if "admin" in request.session:
            request.session["message"] = "Please log out and sign in as a member user."
            return HttpResponseRedirect(reverse("adminhome"))
        return HttpResponseRedirect(reverse("login"))
    # select current book
    c = connection.cursor()
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
            request.session["message"] = "You have borrowed this book."
            return HttpResponseRedirect(reverse("myaccount"))
        # if the user has unpaid fines
        if checkUnpaidFines(userid):
            request.session["message"] = "You need to pay for the outstanding fees first."
            return HttpResponseRedirect(reverse("myaccount"))
        # if the reservation is successful
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
    return HttpResponseRedirect(reverse("myaccount"))


def cancel(request, bookid):
    initialiseEmptyMessage(request)
    if "userid" not in request.session:
        if "admin" in request.session:
            request.session["message"] = "Please log out and sign in as a member user."
            return HttpResponseRedirect(reverse("adminhome"))
        return HttpResponseRedirect(reverse("login"))
    userid = request.session["userid"][0]
    # if the user has unpaid fines
    if checkUnpaidFines(userid):
        request.session["message"] = "You need to pay for the outstanding fees first."
        return HttpResponseRedirect(reverse("myaccount"))
    # select current book
    c = connection.cursor()
    q = f"SELECT * FROM BOOK WHERE BOOKID = {bookid}"
    c.execute(q)
    book = c.fetchone()
    # if book does not exist
    if not book:
        message = "Book does not exist."
    # if the user is reserving the book
    elif list(book)[2] == "RESERVED":
        # if the user is borrowing the book
        q = f"SELECT USERID FROM RESERVES WHERE BOOKID = {bookid} AND USERID = '{userid}'"
        c.execute(q)
        reserveUser = c.fetchone()
        if (userid,) == reserveUser:
            q = f"DELETE FROM RESERVES WHERE BOOKID = {bookid} AND USERID = '{userid}'"
            c.execute(q)
            # check if the book is borrowed
            q = f"SELECT BOOKID FROM BORROWS WHERE BOOKID = {bookid}"
            c.execute(q)
            result = c.fetchone()
            if result:
                q = f"UPDATE BOOK SET AVAILABILITY = 'BORROWED' WHERE BOOKID = {bookid}"
            else :
                q = f"UPDATE BOOK SET AVAILABILITY = 'AVAILABLE' WHERE BOOKID = {bookid}"
            c.execute(q)
            message = "You have successfully cancel the reservation."
        else:
            message = "You have not reserved this book yet."
    request.session["message"] = message
    return HttpResponseRedirect(reverse("myaccount"))


def restore(request, bookid):
    initialiseEmptyMessage(request)
    if "userid" not in request.session:
        if "admin" in request.session:
            request.session["message"] = "Please log out and sign in as a member user."
            return HttpResponseRedirect(reverse("adminhome"))
        return HttpResponseRedirect(reverse("login"))
    # select current book
    c = connection.cursor()
    q = f"SELECT * FROM BOOK WHERE BOOKID = {bookid}"
    c.execute(q)
    book = c.fetchone()
    # if book does not exist
    if not book:
        request.session["message"] = "Book does not exist."
        return HttpResponseRedirect(reverse("myaccount"))
    # select userid and bookid from borrows
    userid = request.session["userid"][0]
    q = f"SELECT * FROM BORROWS WHERE USERID = '{userid}' AND BOOKID = {bookid}"
    c.execute(q)
    borrowRecord = c.fetchone()
    # if the user is not borrowing the book
    if not borrowRecord:
        request.session["message"] = f"You are not borrowing the book {book[1]}."
        return HttpResponseRedirect(reverse("myaccount"))
    # check for fines
    checkUnpaidFines(userid)
    bookid, userid, duedate, extension = borrowRecord
    # if the book is overdue
    q = f"SELECT DUEDATE FROM BORROWS WHERE USERID = '{userid}' AND BOOKID = {bookid}"
    c.execute(q)
    duedate = c.fetchone()
    if date.today() > duedate[0]:
        # if the book has unpaid fines, delete all reservations
        request.session["message"] = "You need to pay for the outstanding fees first."
        return HttpResponseRedirect(reverse("myaccount"))
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
    request.session["message"] = "Book returned successfully."
    return HttpResponseRedirect(reverse("myaccount"))



# ADMIN ACCESS

def adminhome(request):
    initialiseEmptyMessage(request)
    # if the member user is logged in
    if "userid" in request.session:
        request.session["message"] = "Please log out and sign in as an administrator."
        return HttpResponseRedirect(reverse("index"))
    # if the user is not logged in
    if "admin" not in request.session:
        return HttpResponseRedirect(reverse("adminlogin"))
    return HttpResponseRedirect(reverse("adminborrowings"))
    #return render(request, "library/temp.html")


def adminborrowings(request):
    initialiseEmptyMessage(request)
    # if the member user is logged in
    if "userid" in request.session:
        request.session["message"] = "Please log out and sign in as an administrator."
        return HttpResponseRedirect(reverse("index"))
    # if the user is not logged in
    if "admin" not in request.session:
        return HttpResponseRedirect(reverse("adminlogin"))
    message = getSessionMessage(request)
    # main code
    c = connection.cursor()
    q = f"SELECT R.USERID, R.BOOKID, B.TITLE, R.DUEDATE, R.EXTENSION "\
        f"FROM BORROWS R LEFT JOIN BOOK B ON R.BOOKID = B.BOOKID"
    c.execute(q)
    results = c.fetchall()
    return render(request, "library/adminborrowings.html", {
        "books": results,
        "message": message
    })


def adminreservations(request):
    initialiseEmptyMessage(request)
    # if the member user is logged in
    if "userid" in request.session:
        request.session["message"] = "Please log out and sign in as an administrator."
        return HttpResponseRedirect(reverse("index"))
    # if the user is not logged in
    if "admin" not in request.session:
        return HttpResponseRedirect(reverse("adminlogin"))
    message = getSessionMessage(request)
    # main code
    c = connection.cursor()
    q = f"SELECT * FROM RESERVES R LEFT JOIN BOOK B ON R.BOOKID = B.BOOKID"
    c.execute(q)
    results = c.fetchall()
    return render(request, "library/adminreservations.html", {
        "books": results,
        "message": message
    })


def adminfines(request):
    initialiseEmptyMessage(request)
    # if the member user is logged in
    if "userid" in request.session:
        request.session["message"] = "Please log out and sign in as an administrator."
        return HttpResponseRedirect(reverse("index"))
    # if the user is not logged in
    if "admin" not in request.session:
        return HttpResponseRedirect(reverse("adminlogin"))
    message = getSessionMessage(request)
    # main code
    c = connection.cursor()
    q = f"SELECT BOOKID, USERID, DUEDATE, DATEDIFF(NOW(), DUEDATE) AS AMOUNT " \
        f"FROM BORROWS WHERE DATEDIFF(NOW(), DUEDATE) > 0"
    c.execute(q)
    records = c.fetchall()
    return render(request, "library/adminfines.html", {
        "records": records,
        "message": message
    })


def adminallusers(request): #shows all member users (username, userID, email)
    initialiseEmptyMessage(request)
    # if the member user is logged in
    if "userid" in request.session:
        request.session["message"] = "Please log out and sign in as an administrator."
        return HttpResponseRedirect(reverse("index"))
    # if the user is not logged in
    if "admin" not in request.session:
        return HttpResponseRedirect(reverse("adminlogin"))
    message = getSessionMessage(request)
    # main code
    c = connection.cursor()
    q = f"SELECT NAME, USERID, EMAIL FROM MEMBERUSER"
    c.execute(q)
    memberusers = c.fetchall()
    return render(request, "library/adminalluser.html", {
        "users": memberusers,
        "message": message
    })



# ADMIN USER AUTHENTICATION

def adminlogin(request):
    initialiseEmptyMessage(request)
    # if the member user is logged in
    if "userid" in request.session:
        request.session["message"] = "Please log out and sign in as an administrator."
        return HttpResponseRedirect(reverse("index"))
    # if the admin user is logged in
    if "admin" in request.session:
        return HttpResponseRedirect(reverse("adminhome"))
    if request.method == "POST":
        # get current userid and password
        adminid = request.POST["adminid"]
        password = request.POST["password"]
        # get all userids from the database
        c = connection.cursor()
        q = f"SELECT USERID FROM ADMINUSER"
        c.execute(q)
        adminids = c.fetchall()
        # get all passwords from the database
        q = f"SELECT PASSWORD FROM ADMINUSER"
        c.execute(q)
        passwords = c.fetchall()
        # if userid and password are correct
        if ((adminid,) in adminids) and ((password,) in passwords):
            request.session["admin"] = [adminid]
            return HttpResponseRedirect(reverse("adminhome"))
        else:
            # if userid exist but no password
            if ((adminid,) in adminids) and (password is None):
                message = "Please input the password."
                id = adminid
            # if userid exist but incorrect password
            elif ((adminid,) in adminids) and ((password,) not in passwords):
                message = "Incorrect password."
                id = adminid
            # if userid does not exist
            elif (adminid,) not in adminids:
                message = "Admin ID does not exist."
                id = ''
            return render(request, "library/adminlogin.html", {
                "message": message,
                "id": id
            })
    # render empty login page
    return render(request, "library/adminlogin.html")

def adminlogout(request):
    if "admin" in request.session:
        del request.session["admin"]
    return HttpResponseRedirect(reverse("adminlogin"))



# MEMBER USER AUTHENTICATION

def register(request):

    def isValid(userid, name, email, password):
        # get all userids and emails from the database
        c = connection.cursor()
        q = f"SELECT USERID FROM MEMBERUSER WHERE USERID = '{userid}'"
        c.execute(q)
        userids = c.fetchall()
        q = f"SELECT EMAIL FROM MEMBERUSER WHERE EMAIL = '{email}'"
        c.execute(q)
        emails = c.fetchall()
        # values must be non-NULL and (userid, email) needs to be unique
        if not userids and not emails and userid and name and email and password\
            and re.match("^[a-zA-Z0-9][a-zA-Z0-9._-]*@[a-zA-Z0-9][a-zA-Z0-9._-]*\.[a-zA-Z]{2,4}$", email):
            return True
        return False
    
    def getInvalidMessages(userid, name, email, password):
        # get all userids and emails from the database
        c = connection.cursor()
        q = f"SELECT USERID FROM MEMBERUSER WHERE USERID = '{userid}'"
        c.execute(q)
        userids = c.fetchall()
        q = f"SELECT EMAIL FROM MEMBERUSER WHERE EMAIL = '{email}'"
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
        if userids:
            messages += ["This User ID has been registered."]
            userid = ""
        if email and not re.match("^[a-zA-Z0-9][a-zA-Z0-9._-]*@[a-zA-Z0-9][a-zA-Z0-9._-]*\.[a-zA-Z]{2,4}$", email):
            messages += ["Invalid email address."]
            email = ""
        if emails:
            messages += ["This email address has been registered."]
            email = ""
        return (messages, userid, email)

    initialiseEmptyMessage(request)
    # if logged in
    if "userid" in request.session:
        return HttpResponseRedirect(reverse("index"))
    if "admin" in request.session:
        request.session["message"] = "Please log out and register as a member user."
        return HttpResponseRedirect(reverse("adminhome"))
    if request.method == "POST":
        # get current userid, name, email, and password
        userid = request.POST["userid"]
        name = request.POST["name"]
        email = request.POST["email"]
        password = request.POST["password"]
        # if the registration is successful
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
    initialiseEmptyMessage(request)
    # if logged in
    if "userid" in request.session:
        return HttpResponseRedirect(reverse("index"))
    # if admin user is logged in
    if "admin" in request.session:
        request.session["message"] = "Please log out and sign in as a member user."
        return HttpResponseRedirect(reverse("adminhome"))
    if request.method == "POST" and "userid" not in request.session:
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
    if "userid" in request.session:
        del request.session["userid"]
    return HttpResponseRedirect(reverse("login"))
