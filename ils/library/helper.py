from django.db import connection
from datetime import datetime
import re

def initialiseEmptyMessage(request):
    if "message" not in request.session:
        request.session["message"] = []

def getSessionMessage(request):
    message = ""
    if request.session["message"]:
        message = request.session["message"]
        request.session["message"] = []
    return message

def getDueDates(books):
    duedates = []
    c = connection.cursor()
    for book in books:
        # search due date in reserves table
        if book[1] == "RESERVED":
            q = f"SELECT DUEDATE FROM RESERVES WHERE BOOKID = {book[0]}"
            c.execute(q)
            res = c.fetchone()
            if res: duedates += [res[0]]
            else: duedates += [""]
        # search due date in borrows table
        elif book[1] == "BORROWED":
            q = f"SELECT DUEDATE FROM BORROWS WHERE BOOKID = {book[0]}"
            c.execute(q)
            res = c.fetchone()
            if res: duedates += [res[0]]
            else: duedates += [""]
        else:
            duedates += [""]
    return duedates

def getCategories(mycol):
    rawcategories = mycol.distinct("categories")
    # data cleaning
    categories = []
    exists = set()
    for items in rawcategories:
        for item in items.strip('][').replace('\'', '').split(', '):
            if item and item.lower() not in exists:
                exists.add(item.lower())
                categories += [item]
    return sorted(categories)

def formatBook(results, booksall, duedates):
    # format each book
    i = 0
    books = []
    for book in list(results):
        bookaslist = list(book.values())
        # formatting for date
        dateasstring = str(re.findall("([0-9]{4}-[0-9]{2}-[0-9]{2})", bookaslist[4])).strip('[]\'')
        bookaslist[4] = (datetime.strptime(dateasstring, "%Y-%m-%d")).date() if dateasstring else ''
        # formatting for authors and categories
        bookaslist[9] = bookaslist[9].strip('\'][\'').split('\', \'')
        bookaslist[10] = bookaslist[10].strip('\'][\'').split('\', \'')
        # add availabilities from mysql database
        bookaslist += [booksall[i][1]]
        bookaslist += [duedates[i]]
        books += [bookaslist]
        i += 1
    return books