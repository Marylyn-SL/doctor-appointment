import unittest
import psycopg2
from DoctorAppointmentApp import app, current_user

class TestAccessControl(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        self.db_conn = psycopg2.connect("postgresql://da_user:mypasswd@localhost:5432/doctorappointment")
        self.db_cursor = self.db_conn.cursor()

        self.db_cursor.execute("INSERT INTO guest (username, password, email, guest_type) VALUES ('testuser', 'testpassword', 'test@example.com', 'patient')")
        self.db_conn.commit()

    def tearDown(self):
        self.db_cursor.execute("DELETE FROM guest WHERE username='testuser'")
        self.db_conn.commit()
        self.db_cursor.close()
        self.db_conn.close()

    def login_as_patient(self):
        return self.app.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)

    def test_patient_access(self):
        with self.app:
            self.login_as_patient()
            response = self.app.get('/index')
            self.assertEqual(response.status_code, 200)

    def test_unauthenticated_access(self):
        self.assertEqual(current_user, '')

if __name__ == '__main__':
    unittest.main()