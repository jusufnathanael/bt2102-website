# Integrated Library System

*This project is part of AY2020/21S2 BT2102 assignment 1.*

Integrated Library System (ILS) is a database software application that can manage book borrowing, returning and other related operations efficiently and effectively. This application is designed using the Django framework with MySQL and MongoDB databases.

## Setup Instructions

To run this project:

1. Install Python, Django, MySQL, and MongoDB to your local computer.
2. Clone this repository.
3. Set up MySQL database and run the `tables.sql` file inside the sql folder to initialise the tables.
4. Create a MongoDB database called `books` and load the `libboks.json` file.
5. Open ils/ils/settings.py and insert your MySQL password to DATABASES > PASSWORD.
6. From your ils directory, run `python manage.py runserver`.
7. You should be able to view the website from `http://127.0.0.1:8000/library`.

## Features

#### 1. Book Search

- Users can enter the search keyword(s) and the app will return a list of book records whose title contains at least one of the keywords entered.
- In advanced search, users can specify several filters as the search criteria, such as authors, category, and year of publication.

#### 2. Borrowing, Returning, and Reservation Management

- Users can borrow books for a period of 4 weeks if available and up to a maximum of 4 books.
- If a book is currently borrowed by a member, users can proceed to reserve the book instead.
- Users can extend the borrowing period at least 1 week in advance if there is no one reserving the book and up to maximum 2 times.
- Users can also cancel a reservation at any time or convert the reservation to borrowing when the book becomes available.

#### 3. Fines and Payments

- The library charges a fine of $1 per book per day if the member user fails to return a borrowed book on the stipulated due date.
- If the user has any unpaid fines, the user is not allowed to make any further borrowings or reservations and any outstanding reservations will be cancelled automatically by the system.
- Payment of fine can only be made online with credit or debit card.

#### 4. Administrative Functions

Administrative users can access additional administrative function that is not available to member user, which includes displaying the following information:

- all current book borrowings (including the overdue ones),
- all current book reservations,
- all users with unpaid fines, and
- the list of all users.
