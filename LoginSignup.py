import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

class Database:
    def __init__(self, DATABASE_URI):
        self.connection = psycopg2.connect(DATABASE_URI)
        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)

    def execute_query(self, query, params=None, fetchall=False):
        try:
            self.cursor.execute(query, params)

            if fetchall:
                result = self.cursor.fetchall()
            else:
                result = True
            
            self.connection.commit()

        except Exception as e:
            self.connection.rollback()
            raise e
        
        finally:
            self.cursor.close()
            self.connection.close()

        return result
    
    def create_patient(self, guest_id):
        query = sql.SQL("""
            INSERT INTO patient (guest_id)
            VALUES (%s)
            RETURNING pt_id;
        """)
        params = (guest_id,)
        result = self.execute_query(query, params, fetchall=False)
        return result['pt_id'] if result else None

    def create_doctor(self, guest_id, dr_specialization):
        query = sql.SQL("""
            INSERT INTO doctor (guest_id, dr_specialization)
            VALUES (%s, %s)
            RETURNING dr_id;
        """)
        params = (guest_id, dr_specialization)
        result = self.execute_query(query, params, fetchall=False)
        return result['dr_id'] if result else None
    
    def create_availability(self, doctor_id, avail_starttime, avail_endtime):
        query = sql.SQL("""
            INSERT INTO availability (dr_id, avail_starttime, avail_endtime)
            VALUES (%s, %s, %s);
        """)
        params = (doctor_id, avail_starttime, avail_endtime)
        return self.execute_query(query, params, fetchall=False)


class Guest(UserMixin):
    def __init__(self, guest_id, guest_username, guest_name, guest_passwd, guest_email, guest_type):
        self.id = guest_id
        self.username = guest_username
        self.name = guest_name
        self.password = guest_passwd
        self.email = guest_email
        self.type = guest_type

    @classmethod
    def create_guest(cls, DATABASE_URI, guest_username, guest_name, guest_passwd, guest_email, guest_type):
        guest_passwd = generate_password_hash(guest_passwd)
        query = sql.SQL("""
            INSERT INTO guest (guest_username, guest_name, guest_passwd, guest_email, guest_type)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING guest_id, guest_username, guest_name, guest_passwd, guest_email, guest_type;
        """)
        params = (guest_username, guest_name, guest_passwd, guest_email, guest_type)
        result = Database(DATABASE_URI).execute_query(query, params, fetchall=True)
        return cls(**result[0])

    @classmethod
    def find_by_id(cls, DATABASE_URI, guest_id):
        query = sql.SQL("SELECT * FROM guest WHERE guest_id = {}").format(sql.Literal(guest_id))
        result = Database(DATABASE_URI).execute_query(query, fetchall=True)
        return cls(**result[0]) if result else None

    @classmethod
    def find_by_username(cls, DATABASE_URI, guest_username):
        query = sql.SQL("SELECT * FROM guest WHERE guest_username = {}").format(sql.Literal(guest_username))
        result = Database(DATABASE_URI).execute_query(query, fetchall=True)
        return cls(**result[0]) if result else None

class Doctor(UserMixin):
    def __init__(self, dr_id, dr_specialization, guest_id):
        self.id = dr_id
        self.specialization = dr_specialization
        self.guest_id = guest_id

    @classmethod
    def find_by_guest_id(cls, DATABASE_URI, guest_id):
        query = sql.SQL("SELECT * FROM doctor WHERE guest_id = {}").format(sql.Literal(guest_id))
        result = Database(DATABASE_URI).execute_query(query, fetchall=True)
        return cls(**result[0]) if result else None

class Patient(UserMixin):
    def __init__(self, pt_id, guest_id):
        self.id = pt_id
        self.guest_id = guest_id

    @classmethod
    def find_by_guest_id(cls, DATABASE_URI, guest_id):
        query = sql.SQL("SELECT * FROM patient WHERE guest_id = {}").format(sql.Literal(guest_id))
        result = Database(DATABASE_URI).execute_query(query, fetchall=True)
        return cls(**result[0]) if result else None
