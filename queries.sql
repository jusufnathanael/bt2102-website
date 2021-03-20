/*check list of borrowed books*/

SELECT bookID, dueDate
	FROM borrows
    WHERE stats = 'BORROWED';
    
/*check list of outstanding amount*/
SELECT bookID, dueDate, DATEDIFF(NOW(), dueDate) AS amount
	FROM borrows
    WHERE stats = 'BORROWED' AND DATEDIFF(NOW(), dueDate) > 0;

/*when extending a book*/
UPDATE borrows
	SET dueDate = DATE_ADD(dueDate, INTERVAL 2 WEEK), extension = extension + 1
    WHERE bookID = 1;/*idk how to filter it according to the book chosen, from python?*/

/*when borrowing a book*/
UPDATE book
	SET availability = 'BORROWED' /*if converting from reservation: , userID = NULL*/
    WHERE bookID = 2;
    
insert  into `borrows`(`bookID`, `userID`, `dueDate`, `stats`, `extension`) values
(2, 'Aldo', DATE_ADD(NOW(), INTERVAL 4 WEEK), 'BORROWED', 0);

/*create new member user & password */
insert  into `memberUser`(`userID`,`password`) values
('Aldo', '123aldo');

/*create new admin user & password */
insert  into `adminUser`(`userID`,`password`) values
('Aldo', '123aldo');

/*main view for book list*/
SELECT bk.bookID, bk.title, bk.availability, br.dueDate
	FROM book bk INNER JOIN borrows br
    ON bk.bookID = br.bookID;

/*when reserving a book*/
UPDATE book
	SET userID = 'Aldo', availability = 'RESERVED'
    WHERE bookID = 2;
    
/*when canceling reservation */
UPDATE book
	SET userID = NULL, availability = 'AVAILABLE'
    WHERE bookID = 2;

/*when returning a book*/
UPDATE borrows
	SET stats = 'RETURNED', dueDate = NOW()
    WHERE bookID = 1;
    
UPDATE book
	SET availability = 'AVAILABLE'
    WHERE bookID = 1;

/*after paying outstanding amount*/
UPDATE borrows
	SET dueDate = NOW(), stats = 'RETURNED'
    WHERE bookID = 1;

SELECT * FROM borrows;

/*admin user view: book reservation*/
SELECT bookID, userID
	FROM book
    WHERE userID IS NOT NULL;

/*admin user view: all CURRENT book borrowings*/
SELECT bookID, userID, dueDate, extension
	FROM borrows
    WHERE stats = 'BORROWED';

/*admin user view: all PAST book borrowings*/
SELECT bookID, userID, dueDate
	FROM borrows
    WHERE stats = 'RETURNED';

/*admin user view: ALL book borrowings, no need to show extensions*/
SELECT bookID, userID, dueDate, stats
	FROM borrows;

/*admin user view: outstanding amounts*/
SELECT bookID, userID, dueDate, DATEDIFF(NOW(), dueDate) AS amount
	FROM borrows
    WHERE DATEDIFF(NOW(), dueDate) > 0;
