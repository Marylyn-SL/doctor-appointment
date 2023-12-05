var doctors = []
var isAuthenticated = false
var userType = ''
var userId

document.addEventListener("DOMContentLoaded", function () {
    fetch('/appointments/json')
        .then(response => response.json())
        .then(appointments => {
            displayAppointments(appointments);
            updateNavbar();
        });

        const flashMessages = document.querySelector(".flash-messages");
        if (flashMessages) {
        setTimeout(() => {
            flashMessages.style.display = "none";
        }, 1000);
        }

    fetch('/doctors/json')
        .then(response => response.json())
        .then(doctorsData => {
            doctors = doctorsData;
        });

        const roleSelect = document.getElementById('type');
        const medicalLicenseField = document.getElementById('medicalLicenseField');
        const doctorSpecializationField = document.getElementById('doctorSpecializationField');

        if (roleSelect && medicalLicenseField && doctorSpecializationField) {
            roleSelect.addEventListener('change', function () {
                medicalLicenseField.style.display = this.value === 'doctor' ? 'block' : 'none';
                doctorSpecializationField.style.display = this.value === 'doctor' ? 'block' : 'none';
            });
        }
});

function displayAppointments(appointments) {
    const appointmentsList = document.getElementById('appointments-list');

    if(isAuthenticated){
        appointmentsList.innerHTML = '<h2>Appointments</h2>';
        if (appointments.length === 0) {
            appointmentsList.innerHTML += '<p>No appointments available.</p>';
        } else {
            const table = document.createElement('table');
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Appointment ID</th>
                        <th>Date/Time</th>
                        <th>Status</th>
                        <th>Patient Name</th>
                        <th>Doctor Name</th>
                        <th>Doctor Specialization</th>
                    </tr>
                </thead>
                <tbody>
                    ${appointments.map(appointment => `
                        <tr>
                            <td>${appointment.appt_id}</td>
                            <td>${appointment.appt_datetime}</td>
                            <td>${appointment.appt_status}</td>
                            <td>${appointment.patient_name}</td>
                            <td>${appointment.doctor_name}</td>
                            <td>${appointment.dr_specialization}</td>
                        </tr>`).join('')}
                </tbody>
            `;
            appointmentsList.appendChild(table);
        }
    }
}

function updateNavbar() {
    const navbar = document.getElementById('navbar');
    if(navbar == null)
        return
    userType = navbar.getAttribute('data-user-type');
    isAuthenticated = navbar.getAttribute('data-authenticated') === 'True';
    userId = navbar.getAttribute('data-id');

    if (isAuthenticated) {
        const username = navbar.getAttribute('data-username');
        const guestName = navbar.getAttribute('data-guest-name') || username;

        if (userType === 'doctor') {
            navbar.innerHTML = `
            <div class="user-info">
                <p>Welcome, ${guestName}!</p>
            </div>               
            <div class="text-center mb-4">
                <button onclick="openAvailabilityForm()" class="btn btn-success">Add Availability</button>
            </div>

            <div class="text-center">
                <a href="/logout" class="btn btn-outline-danger">Logout</a>
            </div>
            `;
            openAvailabilityForm();
        } else {
            navbar.innerHTML = `
            <div class="user-info">
                <p>Welcome, ${guestName}!</p>
            </div>
            <div class="text-center mb-4">
                <button onclick="openAppointmentForm()" class="btn btn-primary">Add Appointment</button>
            </div>
            <div class="text-center">
                <a href="/logout" class="btn btn-outline-danger">Logout</a>
            </div>     
            `;
            openAvailabilityForm();
        }
    } else {
        navbar.innerHTML = `
        <div class="user-info">
            <p>You are not logged in. <a href="/login">Login</a> or <a href="/signup">Sign Up</a>.</p>
        <div>
        `;
    }
}

function getCurrentUserId() {
    if (isAuthenticated) {
        return userId;
    }
    return null;
}

function openAvailabilityForm() {
    var x = document.getElementById("availability-form");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}

function closeAvailabilityForm() {
    document.getElementById('availability-form').style.display = "none";
}

function addAvailability() {
    const startTime = document.getElementById('start_time').value;
    const endTime = document.getElementById('end_time').value;
    const guestId = getCurrentUserId();

    fetch('/add_availability', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            start_time: startTime,
            end_time: endTime,
            guest_id: guestId,
        }),
    })
    .then(response => response.json())
    .then(result => {
        console.log('Availability added:', result);
        closeAvailabilityForm();
        fetchDoctorAvailability(result.doctorId);
    })
    .catch(error => {
        console.error('Error adding availability:', error);
    });
}

function openAppointmentForm() {
    var x = document.getElementById("appointment-form");
    if (x.style.display === "none") {
        x.style.display = "block";

        const patientIdInput = document.getElementById('patient_id');
        if (patientIdInput) {
            patientIdInput.value = current_user.id;
        }
        const appointmentDatetimeInput = document.getElementById('datetime');
        if (appointmentDatetimeInput) {
            const appointmentDatetime = new Date(appointmentDatetimeInput.value);
            const status = appointmentDatetime < new Date() ? 'Completed' : 'Scheduled';
            console.log('Status:', status);
        }

    } else {
        x.style.display = "none";
    }
    fillDoctorsDropdown()
}

function fillDoctorsDropdown() {
    const doctorsDropdown = document.getElementById('doctor_name');

    doctorsDropdown.innerHTML = '';

    const placeholderOption = document.createElement('option');
    placeholderOption.value = '';
    placeholderOption.text = 'Select a doctor';
    doctorsDropdown.appendChild(placeholderOption);

    const sortedDoctors = doctors.sort((a, b) => a.doctor_name.localeCompare(b.doctor_name));

    sortedDoctors.forEach(doctor => {
        const option = document.createElement('option');
        option.value = doctor.dr_id;
        option.id = doctor.dr_id;
        option.text = `${doctor.doctor_name} - ${doctor.dr_specialization}`;
        doctorsDropdown.appendChild(option);
    });

    doctorsDropdown.addEventListener('change', function () {
        const selectedOption = this.options[this.selectedIndex];
        const doctorId = selectedOption.getAttribute('data-doctor-id');
        fetchDoctorAvailability(doctorId);
    });
}

function fetchDoctorAvailability(doctorId) {
    fetch(`/doctor_availability/${doctorId}/json`)
        .then(response => response.json())
        .then(availability => {
            console.log('Doctor Availability:', availability);
        });
}

function closeAppointmentForm() {
    document.getElementById('appointment-form').innerHTML = `
        <div class="modal-content">
            <span class="close" onclick="closeAppointmentForm()">&times;</span>
            <h2>Add Appointment</h2>
        </div>
    `;
}