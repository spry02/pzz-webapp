from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session #type: ignore
import os
from database.connection import DatabaseConnection

from functools import wraps
from datetime import timedelta
import logging
# Konfiguracja logowania, aby wykluczyć komunikaty debugowania PIL
logging.basicConfig(level=logging.INFO)
logging.getLogger('PIL').setLevel(logging.INFO)


## ----------------- KOD APLIKACJI FLASK ----------------- ##

# Inicjalizacja aplikacji Flask
app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Wyłączanie automatycznego przeładowywania aplikacji
app.config['DEBUG'] = True
app.config['USE_RELOADER'] = True

db = DatabaseConnection()

# Funkcja dekorująca sprawdzająca, czy użytkownik jest zalogowany
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # ✅ Poprawione (było 'username')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Wpuszczenie tylko zalogowanego użytkownika
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Dashboard z wykresami instrumentów handlowych
@app.route('/dashboard')
@login_required
def dashboard():
    # Pobierz listę instrumentów handlowych z bazy danych
    instruments = get_instruments()
    return render_template('dashboard.html', instruments=instruments)

# Funkcja do pobierania instrumentów handlowych
def get_instruments():
    try:
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Instrument_Handlowy")
        instruments = cursor.fetchall()
        return instruments
    except Exception as e:
        print(f"Error fetching instruments: {e}")
        return []
    finally:
        cursor.close()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    app.logger.debug(f"Edytuj profil ścieżka wywołana metodą: {request.method}")
    if request.method=='POST' and 'typ' in request.form:
        typ = request.form.get('typ')
        if typ == 'usernameEdit':
            email = request.form.get('username')
            if db.update_user_email(session['email'], email):
                session['email'] = email
                flash("Nickname został zmieniony pomyślnie!", "success")
                return jsonify({'success': True, 'redirect': url_for('edit_profile')})
            else:
                flash("Podany adres email jest już zajęty.", "danger")
                return jsonify({'error': "Błąd podczas zmiany adresu email."}), 405
            
        elif typ == 'passwordEdit':
            passwordOld = request.form.get('passwordOld')
            passwordNew = request.form.get('passwordNew')
            if db.update_user_password(session['email'], passwordOld, passwordNew):
                flash("Hasło zostało zmienione pomyślnie!", "success")
                return redirect(url_for('edit_profile'))
            else:
                flash("Podane hasło jest niepoprawne.", "danger")
                return jsonify({'error': "Błąd podczas zmiany hasła."}), 406
            
        elif typ == 'userDelete':
            if db.delete_user(session['email']):
                flash("Konto zostało usunięte pomyślnie!", "success")
                return jsonify({'success': True, 'redirect': url_for('logout')})
            else:
                flash("Błąd podczas usuwania konta.", "danger")
                return jsonify({'error': "Błąd podczas usuwania konta."}), 407
    return render_template('edit_profile.html', username=session['email'])

# Rejestracja
@app.route('/register', methods=['GET', 'POST'])
def register():
    app.logger.debug(f"Zarejestruj ścieżkę wywołaną metodą: {request.method}")
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')

        if not email or not password:
            return jsonify({"error": "Email i hasło są wymagane"}), 400

        if db.create_user(email, password):
            flash("Konto zostało utworzone pomyślnie!", "success")
            return jsonify({'success': True, 'redirect': url_for('login')})
        else:
            flash(f"Użytkownik o nazwie {email} już istnieje", "danger")
            return jsonify({"error": "Błąd podczas tworzenia konta."}), 400

    return render_template('register.html')

# Logowanie
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')

        user = db.verify_user(email, password)
        if user:
            session['user_id'] = user['user_id']
            session['email'] = user['email']
            session['rola'] = user['rola_nazwa']
            flash("Pomyślnie zalogowano!", "success")
            return jsonify({'success': True, 'redirect': url_for('dashboard')})  # Zmiana przekierowania na dashboard
        else:
            flash("Nieprawidłowy email lub hasło", "danger")
            return jsonify({'error': 'Nieprawidłowy email lub hasło'}), 401
    return render_template('login.html')

# Wylogowanie
@app.route('/logout')
def logout():
    session.clear() 
    flash("Zostałeś wylogowany.", "success")
    return redirect(url_for('login'))

@app.route('/api/transaction', methods=['POST'])
@login_required
def create_transaction():
    data = request.json
    if not data:
        return jsonify({'success': False, 'message': 'Brak danych'}), 400
    
    try:
        user_id = session['user_id']
        symbol = data['symbol']
        transaction_type = data['type']  # 'kupno' or 'sprzedaz'
        amount = float(data['amount'])
        price = float(data['price'])
        
        # Get instrument_id from symbol
        cursor = db.connection.cursor()
        cursor.execute("SELECT instrument_id FROM Instrument_Handlowy WHERE symbol = %s", (symbol,))
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            return jsonify({'success': False, 'message': 'Nieznany symbol instrumentu'}), 404
        
        instrument_id = result[0]
        
        # Create the transaction
        transaction_id = db.create_transaction(user_id, instrument_id, transaction_type, amount, price)
        
        if transaction_id:
            return jsonify({'success': True, 'transaction_id': transaction_id})
        else:
            return jsonify({'success': False, 'message': 'Błąd podczas tworzenia transakcji'}), 500
    
    except Exception as e:
        app.logger.error(f"Error creating transaction: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)