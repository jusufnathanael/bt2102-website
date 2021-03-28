# bt2102-website

To run this project:

1. Make sure you have Python, Django, and MySQL installed in your local computer.
2. Clone this repository.
3. Set up MySQL database and run the `tables.sql` file inside the sql folder to initialise the tables.
4. Create a MongoDB database named `books` and load the `libboks.json` file.
5. Go to ils > ils > settings.py, insert your MySQL password to DATABASES > PASSWORD.
6. From your ils directory, run `python manage.py runserver`.
7. You should be able to view the website from `http://127.0.0.1:8000/`.
