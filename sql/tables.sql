CREATE DATABASE `library` ;
USE `library`;

/* Table structure for MemberUser */

DROP TABLE IF EXISTS `MemberUser`;
CREATE TABLE `MemberUser` (
  `userID` varchar(50) NOT NULL UNIQUE,
  `name` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL UNIQUE CHECK (email REGEXP '^[a-zA-Z0-9][a-zA-Z0-9._-]*@[a-zA-Z0-9][a-zA-Z0-9._-]*\.[a-zA-Z]{2,4}$'),
  `password` varchar(50) NOT NULL,
  PRIMARY KEY (`userID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/* Table structure for AdminUser */

DROP TABLE IF EXISTS `AdminUser`;
CREATE TABLE `AdminUser` (
  `userID` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL UNIQUE CHECK (email REGEXP '^[a-zA-Z0-9][a-zA-Z0-9._-]*@[a-zA-Z0-9][a-zA-Z0-9._-]*\.[a-zA-Z]{2,4}$'),
  `password` varchar(50) NOT NULL,
  PRIMARY KEY (`userID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/* Table structure for Book */

DROP TABLE IF EXISTS `book`;
CREATE TABLE `book` (
  `bookID` int(4) NOT NULL,
  `title` varchar(50) NOT NULL,
  `availability` varchar(12) CONSTRAINT availType CHECK (availability IN ('AVAILABLE', 'BORROWED', 'RESERVED', 'UNAVAILABLE')),
  PRIMARY KEY (`bookID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/* Table structure for Borrows */

DROP TABLE IF EXISTS `borrows`;
CREATE TABLE `borrows` (
  `bookID` int(4) NOT NULL UNIQUE,
  `userID` varchar(50) NOT NULL,
  `dueDate` date NOT NULL,
  `extension` int(1) CHECK (extension < 3),
  PRIMARY KEY (`bookID`, `userID`),
  FOREIGN KEY (`bookID`) REFERENCES Book(`bookID`),
  FOREIGN KEY (`userID`) REFERENCES MemberUser(`userID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/* Table structure for Borrows */

DROP TABLE IF EXISTS `reserves`;
CREATE TABLE `reserves` (
  `bookID` int(4) NOT NULL UNIQUE,
  `userID` varchar(50) NOT NULL,
  `dueDate` date DEFAULT NULL,
  PRIMARY KEY (`bookID`, `userID`),
  FOREIGN KEY (`bookID`) REFERENCES Book(`bookID`) ON DELETE CASCADE,
  FOREIGN KEY (`userID`) REFERENCES MemberUser(`userID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

