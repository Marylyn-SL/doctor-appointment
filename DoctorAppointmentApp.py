from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from LoginSignup import Database, Guest, Patient, Doctor
from datetime import datetime, timedelta

app = Flask(__name__)

DATABASE_URI = "postgresql://da_user:mypasswd@localhost:5432/doctorappointment"
app.config['SECRET_KEY'] = 'da-admin'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

def execute_query(query, params=None, fetchall=False):
    connection = psycopg2.connect(DATABASE_URI)
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(query, params)

        if fetchall:
            result = cursor.fetchall()
        else:
            result = None

        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()

    return result

def fetch_appointments(guest_id, guest_type):
    query = f"""
    SELECT appt_id, appt_datetime, appt_status, guest_patient.guest_name AS patient_name, guest_doctor.guest_name AS doctor_name, dr_specialization
    FROM appointment
    INNER JOIN patient ON appointment.pt_id = patient.pt_id
    INNER JOIN doctor ON appointment.dr_id = doctor.dr_id
    INNER JOIN guest AS guest_patient ON patient.guest_id = guest_patient.guest_id
    INNER JOIN guest AS guest_doctor ON doctor.guest_id = guest_doctor.guest_id
    WHERE {guest_type}.guest_id = {guest_id};
    """

    return execute_query(query, fetchall=True)

def fetch_doctors():
    query = """
    SELECT dr_id, guest_doctor.guest_name AS doctor_name, dr_specialization
    FROM doctor
    INNER JOIN guest guest_doctor ON doctor.guest_id = guest_doctor.guest_id;
    """

    return execute_query(query, fetchall=True)

def fetch_doctor_availability_by_doctor(doctor_id):
    query = """
    SELECT avail_id, avail_day, avail_starttime, avail_endtime, recurrent
    FROM availability
    WHERE dr_id = %s;
    """
    return execute_query(query, params=(doctor_id,), fetchall=True)

def fetch_doctor_availability(guest_id, and_condition=''):
    query = f"""
    SELECT avail_id, avail_day, avail_starttime, avail_endtime, recurrent
    FROM availability
    WHERE dr_id IN (SELECT dr_id FROM doctor WHERE guest_id = %s)
    {and_condition};
    """
    return execute_query(query, params=(guest_id,), fetchall=True)


@login_manager.user_loader
def load_guest(guest_id):
    return Guest.find_by_id(DATABASE_URI, guest_id)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        email = request.form['email'] 
        type = request.form['type']  

        existing_guest = Guest.find_by_username(DATABASE_URI, username)
        if existing_guest:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('index'))
        else:
            new_guest = Guest.create_guest(DATABASE_URI, username, name, password, email, type)

            if type == 'patient':
                patient_id = Database(DATABASE_URI).create_patient(new_guest.id)
            elif type == 'doctor':
                if 'dr_specialization' in request.form:
                    dr_specialization = request.form.get('dr_specialization')
                    doctor_id = Database(DATABASE_URI).create_doctor(new_guest.id, dr_specialization)
                else:
                    flash('Doctor specialization is required for doctor signup.', 'error')
                    return redirect(url_for('signup'))

            login_user(new_guest)
            flash('Account successfully created!', 'success')
            return redirect(url_for('index'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if (current_user.is_authenticated):
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        guest = Guest.find_by_username(DATABASE_URI, username)

        if guest and check_password_hash(guest.password.strip(), password):
            login_user(guest)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/')
def index():
    guest_name = current_user.name if current_user.is_authenticated else ''
    return render_template('index.html', authenticated=current_user.is_authenticated, guest_name=guest_name, current_user=current_user)

@app.route('/add_availability', methods=['POST'])
@login_required
def add_availability():
    try:
        guest_id = int(request.json['guest_id'])
        day = request.json['avail_day']
        start_time = request.json['start_time']
        end_time = request.json['end_time']
        # start_time = datetime.strptime(request.json['start_time'], '%Y-%m-%dT%H:%M')
        # end_time = datetime.strptime(request.json['end_time'], '%Y-%m-%dT%H:%M')
        doctor = Doctor.find_by_guest_id(DATABASE_URI, guest_id)
        recurrent = bool(request.json['recurrent'])
    except (KeyError, ValueError):
        return jsonify({'error': 'Invalid data format'}), 400

    and_condition = f" AND avail_day='{day}' AND avail_starttime='{start_time}' AND avail_endtime='{end_time}'"
    availability = fetch_doctor_availability(guest_id,and_condition)
    
    if len(availability) > 0:
        success = True
        flash('Availability already exists', 'info')
    else:
        success = Database(DATABASE_URI).create_availability(doctor.id, day, start_time, end_time, recurrent)

    if success:
        flash('Availability added successfully.', 'success')
        return jsonify({'message': 'Availability added successfully', 'doctorId': str(doctor.guest_id)}), 200
    else:
        flash('Error adding availability. Please try again.', 'error')
        return jsonify({'error': 'Error adding availability. Please try again.'}), 400

@app.route('/appointments/<int:guest_id>/json')
def fetch_appointments_json(guest_id):
    guest_type = request.args.get('userType')
    appointments = fetch_appointments(guest_id, guest_type)
    return jsonify(appointments)

@app.route('/doctors/json')
def fetch_doctors_json():
    doctors = fetch_doctors()
    return jsonify(doctors)

@app.route('/doctor_availability/<int:doctor_id>/json')
def fetch_doctor_availability_json(doctor_id):
    guest_type = request.args.get('userType')
    if guest_type == 'patient':
        availability = fetch_doctor_availability_by_doctor(doctor_id)
    else:
        availability = fetch_doctor_availability(doctor_id)
    return jsonify(availability)

@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    appointment_datetime = request.form['datetime']
    status = "Scheduled"
    patient_id = request.form['patient_id']
    doctor_id = request.form['doctor_name']

    appointment_datetime = datetime.strptime(appointment_datetime, '%Y-%m-%dT%H:%M')
    appointment_day = appointment_datetime.strftime('%A')
    appointment_time = datetime.strptime(appointment_datetime.strftime('%H:%M'), '%H:%M')
    if appointment_datetime < datetime.now():
        status = "Completed"

    doctor = Doctor.find_by_id(DATABASE_URI, doctor_id)
    add_appointment_flag = False
    error_message = ''
    
    appointments = fetch_appointments(doctor.guest_id, 'doctor')
    availabilities = fetch_doctor_availability(doctor.guest_id)
    for availability in availabilities:
        avail_starttime = datetime.strptime(availability['avail_starttime'], '%H:%M')
        avail_endtime = datetime.strptime(availability['avail_endtime'], '%H:%M')
        if appointment_day.lower() == availability['avail_day'].lower() and appointment_time >= avail_starttime and appointment_time <= avail_endtime:
            print("appointment available")
            add_appointment_flag = True
            break
    
    if not add_appointment_flag:
        error_message = 'No availability for this doctor at this time, please choose another'
        return redirect(url_for('index'))
    
    for appointment in appointments:
        # Add 30 min by default to the existing appointment and compare with the new appointment
        appointment_endtime = appointment['appt_datetime'] + timedelta(minutes=30)
        if appointment_datetime <= appointment_endtime:
            add_appointment_flag = False
            error_message = 'Appointment conflicts with another appointment, please choose another time'
            break
    
    if add_appointment_flag:
        query = """
        INSERT INTO appointment (appt_datetime, appt_status, pt_id, dr_id)
        VALUES (%s, %s, %s, %s);
        """
        params = (appointment_datetime, status, patient_id, doctor_id)
        execute_query(query, params)
    else:
        print(error_message)
        flash(error_message, 'error')

    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
