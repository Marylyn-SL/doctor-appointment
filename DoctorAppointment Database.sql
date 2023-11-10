CREATE DATABASE DoctorAppointment;

-- Create the User table
CREATE TABLE Guest (
    guest_id SERIAL PRIMARY KEY,
    guest_name VARCHAR(255) NOT NULL,
    guest_passwd CHAR(255) NOT NULL,
    guest_phone VARCHAR(20),
    guest_email VARCHAR(255) UNIQUE NOT NULL,
    guest_type VARCHAR(20) NOT NULL
);

-- Create the Patient table
CREATE TABLE Patient (
    pt_id SERIAL PRIMARY KEY,
    guest_id INT REFERENCES Guest(guest_id)
);

-- Create the Doctor table
CREATE TABLE Doctor (
    dr_id SERIAL PRIMARY KEY,
    dr_specialization VARCHAR(255),
    guest_id INT REFERENCES Guest(guest_id)
);

-- Create the Appointment table
CREATE TABLE Appointment (
    appt_id SERIAL PRIMARY KEY,
    appt_date DATE NOT NULL,
    appt_time TIME NOT NULL,
    appt_status VARCHAR(20) NOT NULL,
    pt_id INT REFERENCES Patient(pt_id),
    dr_id INT REFERENCES Doctor(dr_id)
);
