

from datetime import datetime
import re


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
    return categories


def formatBook(results, availabilities):
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
        bookaslist += availabilities[i]
        books += [bookaslist]
        i += 1
    return books