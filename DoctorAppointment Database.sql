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