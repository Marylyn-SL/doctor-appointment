import unittest
import psycopg2

class TestDatabaseOperations(unittest.TestCase):

    DATABASE_URI = "postgresql://da_user:mypasswd@localhost:5432/doctorappointment"
    @classmethod
    def setUpClass(self, cls):
        cls.conn = psycopg2.connect(self.DATABASE_URI)
        cls.cur = cls.conn.cursor()

    @classmethod
    def tearDownClass(cls):
        cls.cur.close()
        cls.conn.close()

    def test_create_guest(self):
        self.cur.execute("INSERT INTO guest (username, password, email, guest_type) VALUES (%s, %s, %s, %s) RETURNING guest_id", ('testuser', 'password', 'test@example.com', 'patient'))
        new_id = self.cur.fetchone()[0]
        self.conn.commit()

        self.cur.execute("SELECT * FROM guest WHERE guest_id = %s", (new_id,))
        guest = self.cur.fetchone()
        self.assertIsNotNone(guest)

if __name__ == '__main__':
    unittest.main()