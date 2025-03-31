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

    def update_user_email(self, old_email, new_email):
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE Uzytkownik SET email = %s WHERE email = %s", (new_email, old_email))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error updating user email: {e}")

    def update_user_password(self, email, old_password, new_password):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT haslo_hash FROM Uzytkownik WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user or not bcrypt.checkpw(old_password.encode('utf-8'), user[0].encode('utf-8')):
                return False
            
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("UPDATE Uzytkownik SET haslo_hash = %s WHERE email = %s", (hashed, email))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error updating user password: {e}")
    
    def delete_user(self, email):
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Uzytkownik WHERE email = %s", (email,))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error deleting user: {e}")
            return False
        finally:
            cursor.close()