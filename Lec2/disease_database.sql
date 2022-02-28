DROP DATABASE Database_name;

CREATE DATABASE Database_name;

USE Database_name;

CREATE TABLE People
  (
   CPR  VARCHAR(12),
   First_name  VARCHAR(40)  NOT NULL,
   Last_name VARCHAR(40) NOT NULL,
   Height  INT,
   Weight  INT,
   Bio_mother  VARCHAR(12) ,
   Bio_father  VARCHAR(12),
   PRIMARY KEY(CPR)
  );


CREATE TABLE Marriages
  (
    Male_CPR  VARCHAR(12),
    Female_CPR  VARCHAR(12),
    Start_date  INT NOT NULL,
    End_date  INT,
    PRIMARY KEY(Male_CPR, Female_CPR, Start_date),
    FOREIGN KEY(Male_CPR) REFERENCES People(CPR),
    FOREIGN KEY(Female_CPR) REFERENCES People(CPR)
  );


CREATE TABLE Disease
  (
    CPR VARCHAR(12),
    Disease_name  VARCHAR(40),
    Start_date  INT,
    PRIMARY KEY(CPR, Disease_name, Start_date),
    FOREIGN KEY(CPR) REFERENCES People(CPR) ON DELETE CASCADE
  );

-- These imports assume that the 'mysql --local-infile' command is used in a folder containing the files
LOAD DATA LOCAL INFILE './persons.csv' INTO TABLE People
FIELDS TERMINATED BY ',' (CPR, First_name, Last_name, @h, @w, @m, @f)
SET Height = NULLIF(@h, ''), Weight = NULLIF(@w, ''), Bio_mother = NULLIF(@m, ''), Bio_father = NULLIF(@f, '');

LOAD DATA LOCAL INFILE './marriage.csv' INTO TABLE Marriages
FIELDS TERMINATED BY ',' (Male_CPR, Female_CPR, Start_date, @e)
SET End_date = NULLIF(@e, '');

LOAD DATA LOCAL INFILE './disease.csv' INTO TABLE Disease
FIELDS TERMINATED BY ',';

-- 1.
SELECT * FROM People
WHERE Bio_father IS NULL;

-- 2.
SELECT COUNT(*) FROM People
WHERE Bio_mother IS NULL;

--3.
SELECT COUNT(*) FROM Disease
WHERE Disease_name LIKE '%Cancer%';

--4.
SELECT COUNT(DISTINCT CPR) FROM Disease
WHERE Disease_name LIKE '%Cancer%';

--5.
SELECT CPR, First_name, Last_name FROM People JOIN Marriages
ON People.CPR = Marriages.Female_CPR;

--6.
INSERT INTO People VALUES ('040396-2345', 'Matt', 'Rahbek', 173, 67, NULL, NULL);
INSERT INTO People VALUES ('271199-1234', 'Samantha', 'Pena', 162, 48, NULL, NULL);
INSERT INTO Marriages VALUES ('040396-2345', '271199-1234', 21122021, NULL);
INSERT INTO People VALUES ('101019-1234', 'Julie', 'Rahbek Pena', 120, 30, '040396-2345', '271199-1234');
INSERT INTO Disease VALUES ('101019-1234', 'Broken nose', 13022022);

--7.  (This could technically be a function, but I can't be bothered)
-- (Also MySQL is only case sensitive with names so this code is fully functional on the pupil server without upper case commands)
-- Delete marriages first
delete Marriages.* from People join Marriages
on (People.CPR = Marriages.Male_CPR and People.Last_name = 'Rapacki')
or (People.CPR = Marriages.Female_CPR and People.Last_name = 'Rapacki');

--Delete father relations
update People as k join People as p
on (p.CPR = k.Bio_father and p.Last_name = 'Rapacki')
set k.Bio_father = NULL;

--Delete mother relations
update People as k join People as p
on (p.CPR = k.Bio_mother and p.Last_name = 'Rapacki')
set k.Bio_mother = NULL;

-- Delete Rapackis. It's crusial that this is done last.
delete from People
where Last_name = 'Rapacki';
