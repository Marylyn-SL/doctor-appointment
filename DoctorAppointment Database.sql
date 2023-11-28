CREATE DATABASE DoctorAppointment;

CREATE TABLE Guest (
    guest_id SERIAL PRIMARY KEY,
    guest_username VARCHAR(255) NOT NULL,
    guest_name VARCHAR(255) NOT NULL,
    guest_passwd CHAR(255) NOT NULL,
    guest_email VARCHAR(255) UNIQUE NOT NULL,
    guest_type VARCHAR(20) NOT NULL
);

CREATE TABLE Patient (
    pt_id SERIAL PRIMARY KEY,
    guest_id INT REFERENCES Guest(guest_id)
);

CREATE TABLE Doctor (
    dr_id SERIAL PRIMARY KEY,
    dr_specialization VARCHAR(255),
    guest_id INT REFERENCES Guest(guest_id)
);

CREATE TABLE Appointment (
    appt_id SERIAL PRIMARY KEY,
    appt_datetime TIMESTAMP NOT NULL,
    appt_status VARCHAR(20) NOT NULL,
    pt_id INT REFERENCES Patient(pt_id),
    dr_id INT REFERENCES Doctor(dr_id)
);

CREATE TABLE Availability (
    avail_id SERIAL PRIMARY KEY,
    avail_starttime TIMESTAMP NOT NULL,
    avail_endtime TIMESTAMP NOT NULL,
    dr_id INT REFERENCES Doctor(dr_id)
);

-- Example
INSERT INTO Guest (guest_id, guest_name, guest_passwd, guest_email, guest_type)
VALUES (
    1, 'marylyn slim', 1234, 'marylyn@gmail.com', 'patient' 
);

INSERT INTO Guest (guest_id, guest_name, guest_passwd, guest_email, guest_type)
VALUES (
    2, 'elias ghali', 4321, 'elias@gmail.com', 'doctor' 
);

INSERT INTO Patient (pt_id, guest_id)
VALUES (
    1, 1
);

INSERT INTO Doctor (dr_id, dr_specialization, guest_id)
VALUES (
    2, 'dentist', 2
);

INSERT INTO Appointment (appt_id, appt_datetime, appt_status, pt_id, dr_id)
VALUES (
    20, '2023-11-14 07:00:00', 'PENDING', 1, 2
);