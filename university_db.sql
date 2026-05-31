CREATE DATABASE university_db;
use university_db;

CREATE TABLE Department (
Dep_ID varchar(30) primary key,
Dname varchar(30) not null , 
Room varchar(20) ,
Floor INT CHECK(Floor >= 0));

CREATE TABLE Student(
S_ID INT auto_increment primary key  ,
Dep_ID varchar(30) not null , 
Fname varchar(30) not null,
Lname varchar(30) not null,
Email varchar(100) unique,
std_level INT DEFAULT 1 CHECK(std_level >= 1 AND std_level <= 4),
foreign key(Dep_ID) references Department(Dep_ID)
ON DELETE RESTRICT 
ON UPDATE CASCADE 
);

CREATE TABLE Student_Phone(
Phone_number varchar(20) not null CHECK (Phone_number REGEXP '^[0-9+]+$'),
S_ID INT not null,
primary key(S_ID ,Phone_number),
foreign key(S_ID) references Student(S_ID)
ON DELETE CASCADE 
ON UPDATE CASCADE 
);

ALTER TABLE Student_Phone
ADD CONSTRAINT unique_Phone_no UNIQUE (Phone_number);

ALTER TABLE Student_Phone
DROP CHECK student_phone_chk_1,
ADD CONSTRAINT chk_phone_number 
CHECK (Phone_number REGEXP '^(010|011|012|015)[0-9]{8}$');



CREATE TABLE Instructor(
I_ID INT auto_increment primary key,
Dep_ID varchar(30) not null,
Iname varchar(30) not null,
Email varchar(100) unique, 
Salary decimal(10,2) CHECK(Salary > 0),
foreign key(Dep_ID) references Department(Dep_ID)
ON DELETE RESTRICT 
ON UPDATE CASCADE
);

CREATE TABLE Course( 
C_ID varchar(30) primary key ,
Cname varchar(30) not null ,
Credits Int not null CHECK(Credits >= 0 AND Credits <= 3),
Dep_ID varchar(30) not null,
foreign key(Dep_ID) references Department(Dep_ID)
ON DELETE RESTRICT 
ON UPDATE CASCADE 
);

CREATE TABLE Section(
Sec_ID INT not null CHECK (Sec_ID > 0) ,
C_ID varchar(30) not null,
Sec_name varchar(30),
Hall varchar(30),
I_ID INT ,
primary key(Sec_ID,C_ID),
foreign key(C_ID) references Course(C_ID)
ON DELETE CASCADE
ON UPDATE CASCADE ,
foreign key(I_ID) references Instructor(I_ID)
ON DELETE SET NULL 
ON UPDATE CASCADE 
);


CREATE TABLE Enrollment(
S_ID INT not null,
Sec_ID INT not null,
C_ID varchar(30) not null,
grade varchar(20) CHECK(grade IN ('A+', 'A','A-', 'B+', 'B','B-', 'C+', 'C' ,'C-', 'D+', 'D', 'D-' ,'F')),
primary key(S_ID,Sec_ID,C_ID),
UNIQUE (S_ID, C_ID),
foreign key(S_ID) references Student(S_ID)
ON DELETE CASCADE 
ON UPDATE CASCADE ,
foreign key(Sec_ID,C_ID) references Section(Sec_ID,C_ID)
ON DELETE CASCADE 
ON UPDATE CASCADE 
);

INSERT INTO Department (Dep_ID, Dname, Room, Floor) VALUES
('CS', 'Computer Science', 'R101', 1),
('DS', 'Data Science', 'R102', 1),
('CY', 'Cyber Security', 'R303', 3),
('AI', 'Artificial Intelligence','R201',2);

select* from Department;


INSERT INTO Student (Dep_ID, Fname, Lname, Email, std_level) VALUES
('DS', 'Amr', 'Khaled', 'amr.khaled@alexu.edu.eg', 2),
('CS', 'Lujy', 'Walid', 'lujy.walid@alexu.edu.eg', 2),
('CS', 'Omar', 'Hassan', 'omar.hassan@alexu.edu.eg', 3),
('DS', 'Jomana', 'Mahmoud', 'jomana.mahmoud@alexu.edu.eg', 1),
('DS', 'Fayrouz', 'Mohamed', 'fayrouz.mohamed@alexu.edu.eg', 2),
('CY', 'Miriam', 'Selim', 'miriam.selim@alexu.edu.eg', 1),
('CY', 'Karim', 'Fathy', 'karim.fathy@alexu.edu.eg', 4),
('AI', 'Patrick', 'Michael', 'patrick.michael@alexu.edu.eg', 3),
('AI', 'Jana', 'Ayman', 'jana.ayman@alexu.edu.eg', 4),
('DS', 'Menna', 'Adel', 'menna.adel@alexu.edu.eg', 2);

SELECT S_ID, Fname, Lname, Dep_ID, std_level FROM Student ORDER BY S_ID;

SELECT S_ID FROM Student ORDER BY S_ID;


SELECT MAX(S_ID) FROM Student;

INSERT INTO Student_Phone (S_ID, Phone_number) VALUES
(1, '01060019858'),
(1, '01112345679'),
(2, '01023456789'),
(3, '01034567890'),
(3, '01134567891'),
(4, '01045678901'),
(5, '01056789012'),
(6, '01067890123'),
(7, '01078901234'),
(7, '01178901235'),
(8, '01089012345'),
(9, '01090123456'),
(10, '01001234567'),
(10, '01101234568');


SELECT * FROM Student_Phone ORDER BY S_ID;

SELECT s.S_ID, s.Fname, s.Lname, sp.Phone_number
FROM Student s
LEFT JOIN Student_Phone sp ON s.S_ID = sp.S_ID
ORDER BY s.S_ID;

SELECT s.Fname, s.Lname, COUNT(sp.Phone_number) as Phone_Count
FROM Student s
JOIN Student_Phone sp ON s.S_ID = sp.S_ID
GROUP BY s.S_ID
HAVING Phone_Count > 1;

INSERT INTO Instructor (Dep_ID, Iname, Email, Salary) VALUES
('CS', 'Dr.Magda', 'magda.magda@alexu.edu.eg', 25000.00),
('CS', 'Dr.Mohamed Waleed', 'mohamed.waleed@alexu.edu.eg', 18000.00),
('DS', 'Dr.Sara Saed', 'sara.saed@alexu.edu.eg', 26000.00),
('DS', 'Dr.bothaina Elsobky', 'bothaina.@alexu.edu.eg', 17000.00),
('CY', 'Dr.Mayar Mostafa', 'Mayar.mostafa@alexu.edu.eg', 19000.00),
('CY', 'Dr.Yasser Fouad', 'yasser.fouad@alexu.edu.eg', 24500.00),
('AI', 'Dr.Mahmoud Elkholy', 'kholio@alexu.edu.eg', 20000.00),
('AI', 'Dr.Mahmoud Gamal', 'mahmoud.gamal@alexu.edu.eg', 18500.00);

SELECT * FROM Instructor;

SELECT i.I_ID, i.Iname, d.Dname, i.Salary
FROM Instructor i
JOIN Department d ON i.Dep_ID = d.Dep_ID
ORDER BY i.Salary DESC;

SELECT MAX(Salary) as Highest, MIN(Salary) as Lowest FROM Instructor;


INSERT INTO Course (C_ID, Cname, Credits, Dep_ID) VALUES
('CS101', 'Introduction to Programming', 3, 'CS'),
('CS201', 'Data Structures', 3, 'CS'),
('CS301', 'Operating Systems', 3, 'CS'),
('DS101', 'Introduction to Data Science', 3, 'DS'),
('DS201', 'Data Visualization', 3, 'DS'),
('DS202', 'Introduction to Data Base', 3, 'DS'),
('CY101', 'Network Security', 3, 'CY'),
('CY201', 'Cryptography', 3, 'CY'),
('CY301', 'Ethical Hacking', 2, 'CY'),
('AI101', 'Introduction to AI', 3, 'AI'),
('AI201', 'Deep Learning', 3, 'AI'),
('AI301', 'Natural Language Processing', 3, 'AI');

SELECT * FROM Course;

SELECT d.Dname, c.C_ID, c.Cname, c.Credits
FROM Course c
JOIN Department d ON c.Dep_ID = d.Dep_ID
ORDER BY d.Dname, c.C_ID;

SELECT d.Dname, COUNT(*) as Course_Count
FROM Course c
JOIN Department d ON c.Dep_ID = d.Dep_ID
GROUP BY d.Dname;

INSERT INTO Section (Sec_ID, C_ID, Sec_name, Hall, I_ID) VALUES
(1, 'CS101', 'SecProg A', 'Hall 101', 1),
(2, 'CS101', 'SecProg B', 'Hall 102', 2),
(1, 'CS201', 'SecDST A', 'Hall 103', 1),
(1, 'CS301', 'SecOS A', 'Hall 104', 2),
(1, 'DS101', 'SecDS A', 'Hall 201', 3),
(2, 'DS101', 'SecDS B', 'Hall 202', 4),
(1, 'DS201', 'SecDV A', 'Hall 203', 3),
(1, 'DS202', 'SecDB A', 'Hall 204', 4),
(1, 'CY101', 'SecNS A', 'Hall 301', 5),
(1, 'CY201', 'SecCRYP A', 'Hall 302', 6),
(1, 'CY301', 'SecHack A', 'Hall 303', 5),
(1, 'AI101', 'SecAI A', 'Hall 401', 7),
(1, 'AI201', 'SecDL A', 'Hall 402', 8),
(1, 'AI301', 'SecNLP A', 'Hall 403', 7);

SELECT * FROM Section;

SELECT 
    s.Sec_ID, 
    s.C_ID, 
    c.Cname, 
    s.Sec_name, 
    s.Hall, 
    i.Iname
FROM Section s
JOIN Course c ON s.C_ID = c.C_ID
LEFT JOIN Instructor i ON s.I_ID = i.I_ID
ORDER BY s.C_ID, s.Sec_ID;


INSERT INTO Enrollment (S_ID, Sec_ID, C_ID) VALUES
(1, 1, 'DS101'),
(1, 1, 'DS201'),
(2, 1, 'CS101'),
(2, 1, 'CS201'),
(3, 2, 'CS101'),
(3, 1, 'CS201'),
(3, 1, 'CS301'),
(4, 1, 'DS101'),
(5, 2, 'DS101'),
(5, 1, 'DS201'),
(6, 1, 'CY101'),
(7, 1, 'CY101'),
(7, 1, 'CY201'),
(7, 1, 'CY301'),
(8, 1, 'AI101'),
(8, 1, 'AI201'),
(9, 1, 'AI101'),
(9, 1, 'AI201'),
(9, 1, 'AI301'),
(10, 1, 'DS101'),
(10, 1, 'DS202');

SELECT * FROM Enrollment;

SELECT 
    s.Fname, 
    s.Lname, 
    c.Cname, 
    e.grade
FROM Enrollment e
JOIN Student s ON e.S_ID = s.S_ID
JOIN Course c ON e.C_ID = c.C_ID
ORDER BY s.Fname;

UPDATE Enrollment 
SET grade = 'A' 
WHERE S_ID = 1 AND Sec_ID = 1 AND C_ID = 'DS101';


INSERT INTO Student (Dep_ID, Fname, Lname, Email, std_level)
VALUES ('CS', 'Test', 'Level', 'wrong1@alexu.edu.eg', 10);

INSERT INTO Student (Dep_ID, Fname, Lname, Email)
VALUES ('CS', 'Duplicate', 'Email', 'amr.khaled@alexu.edu.eg');

INSERT INTO Student (Dep_ID, Fname, Lname, Email)
VALUES ('XYZ', 'Wrong', 'Dep', 'wrong.dep@alexu.edu.eg');

DELETE FROM Department WHERE Dep_ID = 'CS';

INSERT INTO Student_Phone (S_ID, Phone_number)
VALUES (1, '010ABC123');

INSERT INTO Section (Sec_ID, C_ID, Sec_name, Hall, I_ID)
VALUES (1, 'CS101', 'Duplicate', 'Hall X', 1);

INSERT INTO Enrollment (S_ID, Sec_ID, C_ID)
VALUES (1, 2, 'DS101');   -- enrolled this course already

INSERT INTO Enrollment (S_ID, Sec_ID, C_ID)
VALUES (999, 1, 'DS101'); -- wrong s_id

INSERT INTO Enrollment (S_ID, Sec_ID, C_ID)
VALUES (1, 999, 'DS101'); -- wrong sec_id

select* from Student;
select* from Student_phone;

DELETE FROM Student WHERE S_ID = 7;
SELECT * FROM Student_Phone WHERE S_ID = 7; 

SELECT S.S_ID, S.Fname, S.Lname,
C.C_ID, C.Cname, C.Credits
FROM Student S
JOIN Enrollment E ON S.S_ID = E.S_ID
JOIN Course C ON E.C_ID = C.C_ID
ORDER BY S.S_ID, C.C_ID;



SELECT Sec.Sec_ID, Sec.Sec_name, Sec.Hall,
C.Cname AS CourseName,
I.Iname AS InstructorName
FROM Section Sec
JOIN Course C ON Sec.C_ID = C.C_ID
LEFT JOIN Instructor I ON Sec.I_ID = I.I_ID;


SELECT S.S_ID, S.Fname, S.Lname, 
S.std_level, D.Dname
FROM Student S
JOIN Department D ON S.Dep_ID = D.Dep_ID
WHERE S.std_level = 1;




SELECT D.Dep_ID, D.Dname, AVG(I.Salary) AS avg_salary
FROM Department D
JOIN Instructor I ON D.Dep_ID = I.Dep_ID
GROUP BY D.Dep_ID, D.Dname;



SELECT S.S_ID, S.Fname, S.Lname, 
C.Cname, E.grade
FROM Student S
JOIN Enrollment E ON S.S_ID = E.S_ID
JOIN Course C ON E.C_ID = C.C_ID
WHERE E.grade = 'A';


SELECT 
MAX(Salary) AS Highest_Salary,
MIN(Salary) AS Lowest_Salary
FROM Instructor;


SELECT Sec.Sec_ID, Sec.Sec_name, COUNT(E.S_ID) AS enrolled_students
FROM Section Sec
LEFT JOIN Enrollment E ON Sec.Sec_ID = E.Sec_ID
GROUP BY Sec.Sec_ID, Sec.Sec_name;



SELECT S.S_ID, S.Fname, S.Lname, 
S.std_level, D.Dname
FROM Student S
JOIN Department D ON S.Dep_ID = D.Dep_ID
WHERE S.std_level = 1;


SELECT S.S_ID, S.Fname, S.Lname, COUNT(P.Phone_number) AS phone_count
FROM Student S
JOIN Student_Phone P ON S.S_ID = P.S_ID
GROUP BY S.S_ID, S.Fname, S.Lname
HAVING COUNT(P.Phone_number) > 1;




SELECT D.Dep_ID, D.Dname, COUNT(C.C_ID) AS course_count
FROM Department D
LEFT JOIN Course C ON D.Dep_ID = C.Dep_ID
GROUP BY D.Dep_ID, D.Dname;



SELECT I.I_ID, I.Iname, I.Salary
FROM Instructor I
ORDER BY I.Salary DESC



DELIMITER $$
CREATE TRIGGER check_credit_limit
BEFORE INSERT ON Enrollment
FOR EACH ROW
BEGIN
    DECLARE current_credits INT DEFAULT 0;
    DECLARE new_course_credit INT DEFAULT 0;

    SELECT COALESCE(SUM(c.Credits), 0)
    INTO current_credits
    FROM Enrollment e
    JOIN Course c ON e.C_ID = c.C_ID
    WHERE e.S_ID = NEW.S_ID 
      AND e.grade IS NULL;

    SELECT c.Credits
    INTO new_course_credit
    FROM Course c
    WHERE c.C_ID = NEW.C_ID;

    IF (current_credits + new_course_credit) > 19 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Student cannot register more than 19 credit hours.';
    END IF;

END$$

DELIMITER ;



DELIMITER $$
CREATE TRIGGER section_capacity
BEFORE INSERT ON Enrollment
FOR EACH ROW
BEGIN
    DECLARE current_count INT DEFAULT 0;
    
    SELECT COUNT(*) 
    INTO current_count
    FROM Enrollment
    WHERE Sec_ID = NEW.Sec_ID
      AND C_ID = NEW.C_ID
      AND grade IS NULL;  
    IF current_count >= 30 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Section is full. Maximum 30 students allowed.';
    END IF;
END$$
DELIMITER ;


DROP TRIGGER IF EXISTS section_capacity;


DELIMITER $$
CREATE TRIGGER section_capacity
BEFORE INSERT ON Enrollment
FOR EACH ROW
BEGIN
    DECLARE current_count INT DEFAULT 0;
    
    SELECT COUNT(*) 
    INTO current_count
    FROM Enrollment
    WHERE Sec_ID = NEW.Sec_ID
      AND C_ID = NEW.C_ID
      AND grade IS NULL;  
    IF current_count >= 5 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Section is full. Maximum 5 students allowed.';
    END IF;
END$$
DELIMITER ;

