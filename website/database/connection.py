import mysql.connector
from mysql.connector import Error
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database='Pracownia_Programowania_Zespolowego',
                user=os.getenv('DB_USER', 'root'),
                auth_plugin='mysql_native_password',
                password=os.getenv('DB_PASSWORD', '')
            )
        except Error as e:
            print(f"Error connecting to database: {e}")

    def create_user(self, email, password):
        try:
            cursor = self.connection.cursor()
            
            # Hash password
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Get default user role
            cursor.execute("SELECT rola_id FROM Rola WHERE nazwa = 'uzytkownik'")
            role_id = cursor.fetchone()[0]
            
            # Create user
            sql = """INSERT INTO Uzytkownik (email, haslo_hash, rola_id) 
                     VALUES (%s, %s, %s)"""
            values = (email, hashed, role_id)
            
            cursor.execute(sql, values)
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            cursor.close()

    def verify_user(self, email, password):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.*, r.nazwa as rola_nazwa 
                FROM Uzytkownik u 
                JOIN Rola r ON u.rola_id = r.rola_id 
                WHERE u.email = %s
            """, (email,))
            user = cursor.fetchone()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['haslo_hash'].encode('utf-8')):
                return user
            return None
        except Error as e:
            print(f"Error verifying user: {e}")
            return None
        finally:
            cursor.close()