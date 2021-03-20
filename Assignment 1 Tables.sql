CREATE DATABASE `library` ;

USE `library`;

/*Table structure for table `customers` */

DROP TABLE IF EXISTS `memberUser`;

CREATE TABLE `memberUser` (
  `userID` varchar(50) NOT NULL UNIQUE,
  `password` varchar(50) NOT NULL,
  PRIMARY KEY (`userID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*Data for the table `customers` */

insert  into `memberUser`(`userID`,`password`) values

('IonaTanan', '123iona'),
('Aldo', '123aldo');

DROP TABLE IF EXISTS `adminUser`;

CREATE TABLE `adminUser` (
  `userID` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  PRIMARY KEY (`userID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*Data for the table `customers` */

insert  into `adminUser`(`userID`,`password`) values

('IonaTanan', '123iona');

DROP TABLE IF EXISTS `book`;

CREATE TABLE `book` (
  `bookID` int(4) NOT NULL,
  `title` varchar(50) NOT NULL,
  `availability` varchar(12) CONSTRAINT availType CHECK (availability IN ('AVAILABLE', 'BORROWED', 'RESERVED', 'UNAVAILABLE')),
  `userID` varchar(50), /*if someone reserves it*/
  PRIMARY KEY (`bookID`),
  FOREIGN KEY (`userID`) REFERENCES memberUser(`userID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*Data for the table `customers` */

insert  into `book`(`bookID`, `title`, `availability`, `userID`) values

(1, 'Unlocking Android', 'AVAILABLE', NULL),
(2, 'BT2102', 'AVAILABLE', NULL);

DROP TABLE IF EXISTS `borrows`;

CREATE TABLE `borrows` (
  `bookID` int(4) NOT NULL,
  `userID` varchar(50) NOT NULL,
  `dueDate` date,
  `stats` varchar(8) CONSTRAINT statsType CHECK (stats IN ('BORROWED', 'RETURNED')),
  `extension` int(1) CHECK (extension < 3),
  PRIMARY KEY (`bookID`, `userID`),
  FOREIGN KEY (`bookID`) REFERENCES book(`bookID`),
  FOREIGN KEY (`userID`) REFERENCES memberUser(`userID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*Data for the table `customers` */

insert  into `borrows`(`bookID`, `userID`, `dueDate`, `stats`, `extension`) values

(1, 'IonaTanan', '2020-02-28', 'BORROWED', 0);


/*
DROP TABLE IF EXISTS `author`;

CREATE TABLE `author` (
  `authorName` varchar(200) NOT NULL,
  `bookID` int(4) NOT NULL,
  PRIMARY KEY (`authorName`),
  FOREIGN KEY (`bookID`) REFERENCES book(`bookID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



insert  into `author`(`authorName`, `bookID`) values

('W. Frank', 1);

DROP TABLE IF EXISTS `category`;

CREATE TABLE `category` (
  `categoryType` varchar(200) NOT NULL,
  `bookID` int(4) NOT NULL,
  PRIMARY KEY (`categoryType`),
  FOREIGN KEY (`bookID`) REFERENCES book(`bookID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



insert  into `category`(`categoryType`, `bookID`) values

('Open Source', 1); */

