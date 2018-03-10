CREATE TABLE Student(
	sId INT NOT NULL, 
	Name varchar NOT NULL, 
	LastName varchar NOT NULL, 
	Major varchar NOT NULL, 
	GPA FLOAT,
	PRIMARY KEY (sId)
);

CREATE TABLE Course (
  cId INT NOT NULL,
  cName varchar NOT NULL,
  PRIMARY KEY (cId)
);


CREATE TABLE Takes (
	sId INT NOT NULL, 
	cId INT NOT NULL,
	semester varchar NOT NULL,
	year INT varchar NOT NULL, 
	PRIMARY KEY (sId, cId),
  	FOREIGN KEY (sId) REFERENCES Student (sId) ON DELETE CASCADE ON UPDATE CASCADE,
  	FOREIGN KEY (cId) REFERENCES Course (cId) ON DELETE CASCADE ON UPDATE CASCADE
);


INSERT INTO Student VALUES(100, 'John', 'Martin', 'CS', 3);
INSERT INTO Student VALUES(101, 'David', 'Kennerly', 'ECE', 3.5);
INSERT INTO Student VALUES(102, 'Bob', 'Reeves', 'CS', 3.9);
INSERT INTO Student VALUES(103, 'Alex', 'Han', 'CS', 3.6);
INSERT INTO Student VALUES(104, 'Martin', 'Lorenz', 'ECE', 3.1);

INSERT INTO Course VALUES(202, 'Cloud Computing');
INSERT INTO Course VALUES(303, 'VLSI');
INSERT INTO Course VALUES(404, 'Digital Design');

INSERT INTO Takes VALUES(100, 202, 'Fall', 2017);
INSERT INTO Takes VALUES(101, 303, 'Spring', 2016);
INSERT INTO Takes VALUES(102, 404, 'Spring', 2015);
INSERT INTO Takes VALUES(103, 404, 'Fall', 2016);
INSERT INTO Takes VALUES(104, 303, 'Fall', 2017);

SELECT * FROM Student;

SELECT * FROM course WHERE cName='Cloud Computing'; 

SELECT * FROM Takes WHERE semester ='Fall';

SELECT * FROM Takes WHERE semester ='Spring' AND year=2015;

SELECT * FROM Takes ORDER BY semester DESC;

SELECT sId, cId, year FROM Takes;

SELECT * FROM Student, Takes WHERE Student.sId = Takes.sId;

DELETE from Student WHERE sId = 102;

DELETE from Takes WHERE sId = 104;
