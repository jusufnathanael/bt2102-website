from django.db import connection
from datetime import datetime, date
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

def getSearchResult(mycol, title, author, categories, year):
    return mycol.aggregate([\
        {"$match": {"$and": [\
            {"title": {"$regex": title,"$options": "i"},\
            "authors": {"$regex": author, "$options": "i"},\
            "categories": {"$regex": categories},\
            "publishedDate": {"$regex": year, "$options": "i"}\
            }
        ]}},
    ])

def checkUnpaidFines(userid):
    # if the user has unpaid fines
    c = connection.cursor()
    q = f"SELECT DUEDATE FROM BORROWS WHERE USERID = '{userid}'"
    c.execute(q)
    duedates = c.fetchall()
    for duedate in duedates:
        if date.today() > duedate[0]:
            # get the bookIDs to change to borrow
            q = f"SELECT R.BOOKID FROM reserves r LEFT JOIN BORROWS b "\
                f"on r.bookID = b.bookID where b.userid IS NOT NULL and r.userid = '{userid}'"
            c.execute(q)
            results = c.fetchall()
            if results and len(results) == 1:
                q = f"UPDATE BOOK SET AVAILABILITY = 'BORROWED' WHERE BOOKID = {results[0][0]}"
            elif len(results) > 1:
                bookids = []
                for id in results:
                    bookids += [id[0]]
                q = f"UPDATE BOOK SET AVAILABILITY = 'BORROWED' WHERE BOOKID IN {tuple(bookids)}"
            c.execute(q)
            # get the bookIDs to change to available
            q = f"SELECT R.BOOKID FROM reserves r LEFT JOIN BORROWS b "\
                f"on r.bookID = b.bookID where b.userid IS NULL and r.userid = '{userid}'"
            c.execute(q)
            results = c.fetchall()
            if results and len(results) == 1:
                q = f"UPDATE BOOK SET AVAILABILITY = 'AVAILABLE' WHERE BOOKID = {results[0][0]}"
            elif len(results) > 1:
                bookids = []
                for id in results:
                    bookids += [id[0]]
                q = f"UPDATE BOOK SET AVAILABILITY = 'AVAILABLE' WHERE BOOKID IN {tuple(bookids)}"
            c.execute(q)
            # delete all reservations
            q = f"DELETE FROM RESERVES WHERE USERID = '{userid}'"
            c.execute(q)
            return True
    return False

def getDueDate(book):
    c = connection.cursor()
    # search due date in reserves table
    if book[1] == "RESERVED":
        q = f"SELECT DUEDATE FROM RESERVES WHERE BOOKID = {book[0]}"
        c.execute(q)
        res = c.fetchone()
        if res: return [res[0]]
        else: return [""]
    # search due date in borrows table
    if book[1] == "BORROWED":
        q = f"SELECT DUEDATE FROM BORROWS WHERE BOOKID = {book[0]}"
        c.execute(q)
        res = c.fetchone()
        if res: return [res[0]]
        else: return [""]
    return [""]

def getDueDatesForIndex(books):
    duedates = []
    for book in books:
        duedates += getDueDate(book)
    return duedates

def getDueDatesForSearch(books, bookids):
    duedates = []
    for book in books:
        if book[0] in bookids:
            duedates += getDueDate(book)
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

def getAvailability(booksall, bookids,type, i):
    # search all books (from views.index)
    if type == 0:
        return booksall[i][1]
    # search with filter (from views.search)
    c = connection.cursor()
    q = f"SELECT AVAILABILITY FROM BOOK WHERE BOOKID = {bookids[i]}"
    c.execute(q)
    return c.fetchone()[0]

def formatBook(results, booksall, bookids, duedates, type):
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
        bookaslist += [getAvailability(booksall, bookids, type, i)]
        # add due dates from mysql database
        bookaslist += [duedates[i]]
        books += [bookaslist]
        i += 1
    return books

def getBookIDs(results):
    books = []
    for book in list(results):
        bookaslist = list(book.values())
        books += [bookaslist[0]]
    return books

def convertToInteger(alist):
    results = []
    for item in alist:
        results += [int(item)]
    return results