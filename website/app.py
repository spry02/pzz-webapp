from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os

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

# Funkcja dekorująca sprawdzająca, czy użytkownik jest zalogowany
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Rejestracja
@app.route('/register', methods=['GET', 'POST'])
def register():
    app.logger.debug(f"Zarejestruj ścieżkę wywołaną metodą: {request.method}")
    if request.method == 'GET':
        app.logger.debug("Renderowanie szablonu rejestracji")
        return render_template('register.html')
    
    # Obsługa formularza rejestracji
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"error": "Nazwa użytkownika i hasło są wymagane"}), 400

    if not username.isalnum():
        return jsonify({"error": "Nazwa użytkownika może zawierać tylko litery i cyfry"}), 400

# Logowanie
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    # Obsługa formularza logowania
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"error": "Nazwa użytkownika i hasło są wymagane"}), 400

    # Zaloguj użytkownika
    session['username'] = username
    flash("Pomyślnie zalogowano!", "success")
    return jsonify({"success": True, "redirect": url_for('index')})

# Wylogowanie
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Zostałeś wylogowany.", "success")
    return redirect(url_for('login'))  # Przekierowanie na stronę logowania

if __name__ == '__main__':
    # Upewnij się, że wszystkie wymagane katalogi istnieją
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)