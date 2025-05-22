## @file database/connection.py
## @brief Moduł obsługujący połączenie z bazą danych
## @details Zawiera klasę DatabaseConnection do zarządzania operacjami bazodanowymi

import mysql.connector
from mysql.connector import Error
import bcrypt
import os
from dotenv import load_dotenv
from decimal import Decimal

load_dotenv()

## @brief Klasa obsługująca połączenie z bazą danych i operacje na niej
class DatabaseConnection:
    ## @brief Inicjalizacja klasy i nawiązanie połączenia z bazą danych
    def __init__(self):
        self.connection = None
        self.connect()

    ## @brief Nawiązuje połączenie z bazą danych
    ## @return True w przypadku sukcesu, False w przypadku błędu
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', ''),
                database='Pracownia_Programowania_Zespolowego',
                user=os.getenv('DB_USER', ''),
                auth_plugin='mysql_native_password',
                password=os.getenv('DB_PASSWORD', '')
            )
            return True
        except Error as e:
            print(f"Error connecting to database: {e}")
            return False

    ## @brief Sprawdza i w razie potrzeby odnawia połączenie z bazą danych
    def ensure_connection(self):
        try:
            self.connection.ping(reconnect=True, attempts=3, delay=5)
        except Error:
            self.connect()

    ## @brief Tworzy nowego użytkownika w bazie danych
    ## @param email Adres email użytkownika
    ## @param password Hasło użytkownika
    ## @return True w przypadku sukcesu, False w przypadku błędu
    def create_user(self, email, password):
        cursor = None
        self.ensure_connection()

        if not self.connection:
            return False

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
            if cursor:
                cursor.close()

    ## @brief Weryfikuje poprawność danych logowania użytkownika
    ## @param email Adres email użytkownika
    ## @param password Hasło użytkownika
    ## @return Dane użytkownika w przypadku sukcesu, None w przypadku błędu
    def verify_user(self, email, password):
        cursor = None
        self.ensure_connection()  # Add connection check
        
        if not self.connection:
            print("No database connection available")
            return None

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
            if cursor:
                cursor.close()

    ## @brief Aktualizuje adres email użytkownika
    ## @param old_email Stary adres email
    ## @param new_email Nowy adres email
    ## @return True w przypadku sukcesu, None w przypadku błędu
    def update_user_email(self, old_email, new_email):
        self.ensure_connection()
        
        if not self.connection:
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE Uzytkownik SET email = %s WHERE email = %s", (new_email, old_email))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error updating user email: {e}")

    ## @brief Aktualizuje hasło użytkownika
    ## @param email Adres email użytkownika
    ## @param old_password Stare hasło
    ## @param new_password Nowe hasło
    ## @return True w przypadku sukcesu, False w przypadku błędu
    def update_user_password(self, email, old_password, new_password):
        self.ensure_connection()
        
        if not self.connection:
            return False

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
    
    ## @brief Usuwa użytkownika z bazy danych
    ## @param email Adres email użytkownika
    ## @return True w przypadku sukcesu, False w przypadku błędu
    def delete_user(self, email):
        self.ensure_connection()
        
        if not self.connection:
            return False

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
            
    ## @brief Pobiera listę wszystkich instrumentów handlowych
    ## @return Lista instrumentów handlowych
    def get_instruments(self):
        self.ensure_connection()
        
        if not self.connection:
            return []

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Instrument_Handlowy")
            instruments = cursor.fetchall()
            return instruments
        except Error as e:
            print(f"Error fetching instruments: {e}")
            return []
        finally:
            cursor.close()
            
    ## @brief Tworzy nową transakcję w bazie danych
    ## @param user_id Identyfikator użytkownika
    ## @param instrument_id Identyfikator instrumentu
    ## @param transaction_type Typ transakcji (kupno/sprzedaz)
    ## @param amount Ilość
    ## @param price Cena jednostkowa
    ## @return Identyfikator utworzonej transakcji lub None w przypadku błędu
    def create_transaction(self, user_id, instrument_id, transaction_type, amount, price):
        self.ensure_connection()
        
        if not self.connection:
            return None

        try:
            cursor = self.connection.cursor()
            sql = """INSERT INTO Transakcja (user_id, instrument_id, typ_transakcji, ilosc, cena) 
                     VALUES (%s, %s, %s, %s, %s)"""
            values = (user_id, instrument_id, transaction_type, Decimal(amount), Decimal(price))
            
            cursor.execute(sql, values)
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error creating transaction: {e}")
            return None
        finally:
            cursor.close()
            
    ## @brief Pobiera listę wszystkich użytkowników
    ## @return Lista użytkowników
    def get_all_users(self):
        cursor = None
        self.ensure_connection()
        
        if not self.connection:
            return []

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.user_id, u.email, r.nazwa as rola_nazwa, u.data_utworzenia
                FROM Uzytkownik u
                JOIN Rola r ON u.rola_id = r.rola_id
                ORDER BY u.data_utworzenia DESC
            """)
            users = cursor.fetchall()
            return users
        except Error as e:
            print(f"Error fetching users: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    ## @brief Usuwa użytkownika z bazy danych na podstawie identyfikatora
    ## @param user_id Identyfikator użytkownika
    ## @return True w przypadku sukcesu, False w przypadku błędu
    def delete_user_by_id(self, user_id):
        cursor = None
        self.ensure_connection()
        
        if not self.connection:
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Uzytkownik WHERE user_id = %s", (user_id,))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error deleting user: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    ## @brief Aktualizuje rolę użytkownika
    ## @param user_id Identyfikator użytkownika
    ## @param role_id Identyfikator nowej roli
    ## @return True w przypadku sukcesu, False w przypadku błędu
    def update_user_role(self, user_id, role_id):
        cursor = None
        self.ensure_connection()
        
        if not self.connection:
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE Uzytkownik SET rola_id = %s WHERE user_id = %s", (role_id, user_id))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error updating user role: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    ## @brief Pobiera listę wszystkich transakcji
    ## @return Lista transakcji
    def get_all_transactions(self):
        cursor = None
        self.ensure_connection()
        
        if not self.connection:
            return []

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.*, i.nazwa as instrument_nazwa, i.symbol, u.email as user_email
                FROM Transakcja t
                JOIN Instrument_Handlowy i ON t.instrument_id = i.instrument_id
                JOIN Uzytkownik u ON t.user_id = u.user_id
                ORDER BY t.data_transakcji DESC
            """)
            transactions = cursor.fetchall()
            return transactions
        except Error as e:
            print(f"Error fetching transactions: {e}")
            return []
        finally:
            if cursor:
                cursor.close()