USE `library`;

/* Data for the table MemberUser */

insert into `MemberUser`(`userID`,`name`,`email`,`password`) values
('IonaTanan', 'Iona Tanan', 'iona@gmail.com', '123iona'),
('Aldo', 'Aldo', 'aldo@gmail.com', '123aldo'),
('10230', 'Testing', 'ts@mail.co', 'abcdef'),
('full', 'asdfad', 'coco@coco.co', '123'),
('12', 'testjskdfj', 'user@usdafksdjfakdf.com', 'sdfjk'),
('fullname', 'fullnamesame', 'fullname@gmail.com', '123');

/* Data for the table AdminUser */

insert  into `AdminUser`(`userID`,`name`,`email`,`password`) values
('IonaTanan', 'Iona Tanan', 'ionatanan@gmail.com', '123iona');

/* Data for the table `Book` */

insert into `book`(`bookID`, `title`, `availability`) values
(1, 'Unlocking Android', 'AVAILABLE'),
(2, 'BT2102', 'AVAILABLE'),
(3, 'CS2113T', 'AVAILABLE'),
(4, 'CG2023', 'AVAILABLE'),
(5, 'CS2102', 'AVAILABLE'),
(6, 'BT2102', 'AVAILABLE'),
(7, 'Test 123', 'AVAILABLE');

/* Data for the table `borrows` */

insert  into `borrows`(`bookID`, `userID`, `dueDate`, `extension`) values
(2, 'IonaTanan', '2020-02-28', 0);

/* Data for the table `reserves` */

insert  into `reserves`(`bookID`, `userID`, `dueDate`) values
(1, 'Aldo', NULL);