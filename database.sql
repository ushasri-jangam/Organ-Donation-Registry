
CREATE DATABASE IF NOT EXISTS organ_donation_db;
USE organ_donation_db;

-- 1. DONOR TABLE
CREATE TABLE IF NOT EXISTS DONOR (
    Donor_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100),
    Age INT,
    Gender VARCHAR(20),
    Blood_Group VARCHAR(5),
    Phone VARCHAR(15),
    Address VARCHAR(200),
    Registration_Date DATE
);

-- 2. RECIPIENT TABLE
CREATE TABLE IF NOT EXISTS RECIPIENT (
    Recipient_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100),
    Age INT,
    Gender VARCHAR(20),
    Blood_Group VARCHAR(5),
    Organ_Required VARCHAR(50),
    Priority VARCHAR(30),
    Registration_Date DATE
);

-- 3. ORGAN TABLE
CREATE TABLE IF NOT EXISTS ORGAN (
    Organ_ID INT PRIMARY KEY AUTO_INCREMENT,
    Donor_ID INT,
    Organ_Type VARCHAR(50),
    Availability_Status VARCHAR(30) DEFAULT 'Available',
    FOREIGN KEY (Donor_ID) REFERENCES DONOR(Donor_ID)
);

-- 4. HOSPITAL TABLE
CREATE TABLE IF NOT EXISTS HOSPITAL (
    Hospital_ID INT PRIMARY KEY AUTO_INCREMENT,
    Hospital_Name VARCHAR(100),
    Location VARCHAR(150),
    Contact_Number VARCHAR(15)
);

-- 5. COORDINATOR TABLE
CREATE TABLE IF NOT EXISTS COORDINATOR (
    Coordinator_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100),
    Phone VARCHAR(15),
    Hospital_ID INT,
    FOREIGN KEY (Hospital_ID) REFERENCES HOSPITAL(Hospital_ID)
);

-- 6. MEDICAL COMPATIBILITY TABLE
CREATE TABLE IF NOT EXISTS MEDICAL_COMPATIBILITY (
    Compatibility_ID INT PRIMARY KEY AUTO_INCREMENT,
    Donor_ID INT,
    Recipient_ID INT,
    Compatibility_Status VARCHAR(30),
    Remarks VARCHAR(200),
    FOREIGN KEY (Donor_ID) REFERENCES DONOR(Donor_ID),
    FOREIGN KEY (Recipient_ID) REFERENCES RECIPIENT(Recipient_ID)
);

-- 7. TRANSPLANT TABLE
CREATE TABLE IF NOT EXISTS TRANSPLANT (
    Transplant_ID INT PRIMARY KEY AUTO_INCREMENT,
    Donor_ID INT,
    Recipient_ID INT,
    Organ_ID INT,
    Hospital_ID INT,
    Transplant_Date DATE,
    Status VARCHAR(30),
    FOREIGN KEY (Donor_ID) REFERENCES DONOR(Donor_ID),
    FOREIGN KEY (Recipient_ID) REFERENCES RECIPIENT(Recipient_ID),
    FOREIGN KEY (Organ_ID) REFERENCES ORGAN(Organ_ID),
    FOREIGN KEY (Hospital_ID) REFERENCES HOSPITAL(Hospital_ID)
);

-- SAMPLE RECORDS

INSERT IGNORE INTO DONOR VALUES
(1,'Rahul',25,'Male','O+','9876543210','Hyderabad','2026-10-01'),
(2,'Priya',30,'Female','A+','9876543211','Warangal','2026-10-02');

INSERT IGNORE INTO RECIPIENT VALUES
(1,'Arjun',40,'Male','O+','Kidney','High','2026-10-03'),
(2,'Sneha',35,'Female','A+','Liver','Medium','2026-10-04');

INSERT IGNORE INTO ORGAN VALUES
(1,1,'Kidney','Available'),
(2,2,'Liver','Available');

INSERT IGNORE INTO HOSPITAL VALUES
(1,'City Hospital','Hyderabad','9876500000');

INSERT IGNORE INTO COORDINATOR VALUES
(1,'Anil','9876500001',1);

INSERT IGNORE INTO MEDICAL_COMPATIBILITY VALUES
(1,1,1,'Compatible','Sample compatibility record'),
(2,2,2,'Compatible','Sample compatibility record');

-- VIEW
CREATE OR REPLACE VIEW Available_Organ_View AS
SELECT Organ_ID, Donor_ID, Organ_Type, Availability_Status
FROM ORGAN
WHERE Availability_Status = 'Available';

-- TRIGGER
DROP TRIGGER IF EXISTS trg_update_organ_status;

DELIMITER $$

CREATE TRIGGER trg_update_organ_status
AFTER INSERT ON TRANSPLANT
FOR EACH ROW
BEGIN
    UPDATE ORGAN
    SET Availability_Status = 'Unavailable'
    WHERE Organ_ID = NEW.Organ_ID;
END$$

DELIMITER ;

-- STORED PROCEDURE
DROP PROCEDURE IF EXISTS GetAvailableOrgans;

DELIMITER $$

CREATE PROCEDURE GetAvailableOrgans()
BEGIN
    SELECT * FROM ORGAN
    WHERE Availability_Status = 'Available';
END$$

DELIMITER ;

-- DISPLAY RESULTS
SELECT * FROM DONOR;
SELECT * FROM RECIPIENT;
SELECT * FROM ORGAN;
SELECT * FROM HOSPITAL;
SELECT * FROM COORDINATOR;
SELECT * FROM MEDICAL_COMPATIBILITY;
SELECT * FROM TRANSPLANT;

SELECT * FROM Available_Organ_View;

CALL GetAvailableOrgans();