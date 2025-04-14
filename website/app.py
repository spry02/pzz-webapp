import re
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session  #type: ignore
import os
from database.connection import DatabaseConnection
import requests
import json
from datetime import datetime, timedelta
import logging
from functools import wraps
import random

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
    return redirect(url_for('dashboard'))

# Dane historyczne dla instrumentów finansowych - zmodyfikowana implementacja
def get_historical_data(symbol, days_back=None):
    # Bazowe wartości dla różnych instrumentów
    base_prices = {
        'WIG20': 2150.0,
        'SILVER': 26.5,
        'GOLD': 2340.0,
        'BTC': 68500.0,
        'NATGAS': 2.15,
        'AAPL': 173.50
    }
    
    # Zmienność dla różnych instrumentów (w %)
    volatility = {
        'WIG20': 1.2,
        'SILVER': 2.0,
        'GOLD': 1.5,
        'BTC': 5.0,
        'NATGAS': 3.0,
        'AAPL': 2.5
    }
    
    # Trendy dla różnych instrumentów (w %)
    trends = {
        'WIG20': 0.02,
        'SILVER': 0.05,
        'GOLD': 0.03,
        'BTC': -0.1,
        'NATGAS': -0.05,
        'AAPL': 0.08
    }
    
    if symbol not in base_prices:
        return [], []
    
    base_price = base_prices[symbol]
    vol = volatility.get(symbol, 2.0)
    trend = trends.get(symbol, 0.0)
    
    prices = []
    dates = []
    
    # Ustal datę początkową na 1 stycznia 2023
    start_date = datetime(2023, 1, 1)
    end_date = datetime.now()
    
    # Oblicz liczbę dni między datą początkową a dzisiejszą
    delta = end_date - start_date
    num_days = delta.days + 1  # +1 aby uwzględnić dzisiejszy dzień
    
    # Niższa wartość początkowa
    price = base_price * 0.65
    
    # Generuj dane dla każdego dnia od początku do dziś
    for i in range(num_days):
        current_date = start_date + timedelta(days=i)
        
        # Deterministyczny trend oparty na indeksie dnia
        progress = i / num_days
        trend_factor = 1.0 + (trend * progress)
        
        # Dodaj kontrolowaną zmienność
        # Używamy deterministycznego seed dla powtarzalności
        random.seed(int(current_date.timestamp()) + hash(symbol))
        random_change = (random.random() - 0.5) * 2 * (vol/100) * price
        
        # Oblicz cenę dla danego dnia
        price = price * trend_factor + random_change
        price = max(price, base_price * 0.3)  # Zapobiegaj zbyt niskim wartościom
        
        prices.append(round(price, 2))
        dates.append(current_date.strftime('%Y-%m-%d'))
    
    return prices, dates

# Symulowane dane zewnętrznych instrumentów (w prawdziwej aplikacji pochodziłyby z API)
def get_external_market_data():
    try:
        # Przygotuj dane dla instrumentów handlowych
        instruments = [
            {
                'symbol': 'SI=F', 
                'name': 'Srebro', 
                'prices': get_historical_data('SILVER', 60)[0],
                'dates': get_historical_data('SILVER', 60)[1]
            },
            {
                'symbol': 'GC=F', 
                'name': 'Złoto',
                'prices': get_historical_data('GOLD', 60)[0],
                'dates': get_historical_data('GOLD', 60)[1]
            },
            {
                'symbol': 'BTC-USD', 
                'name': 'Bitcoin',
                'prices': get_historical_data('BTC', 60)[0],
                'dates': get_historical_data('BTC', 60)[1]
            },
            {
                'symbol': 'NG=F', 
                'name': 'Gaz Ziemny',
                'prices': get_historical_data('NATGAS', 60)[0],
                'dates': get_historical_data('NATGAS', 60)[1]
            },
            {
                'symbol': 'AAPL', 
                'name': 'Apple Inc.',
                'prices': get_historical_data('AAPL', 60)[0],
                'dates': get_historical_data('AAPL', 60)[1]
            }
        ]
        
        # Oblicz wskaźniki dla każdego instrumentu
        for instr in instruments:
            prices = instr['prices']
            if not prices:
                continue
                
            # Aktualny kurs to ostatni na liście
            instr['price'] = prices[-1]
            
            # Oblicz zmianę % względem dnia poprzedniego
            if len(prices) > 1:
                prev_price = prices[-2]
                instr['change'] = round((prices[-1] - prev_price) / prev_price * 100, 2)
            else:
                instr['change'] = 0
                
            # Dodaj wolumen (symulowany)
            instr['volume'] = random.randint(100000, 5000000)
            
            # Dodaj cenę otwarcia (symulowana jako cena z początku dnia)
            instr['opening'] = round(prices[-1] * (1 - random.uniform(-0.01, 0.01)), 2)
            
            # Oblicz min/max z dzisiejszego dnia
            daily_low = min(instr['price'], instr['opening']) * (1 - random.uniform(0, 0.015))
            daily_high = max(instr['price'], instr['opening']) * (1 + random.uniform(0, 0.015))
            instr['min'] = round(daily_low, 2)
            instr['max'] = round(daily_high, 2)
        
        # Dane wskaźników rynkowych
        wig20_prices, wig20_dates = get_historical_data('WIG20', 30)
        wig20_current = wig20_prices[-1]
        wig20_prev = wig20_prices[-2] if len(wig20_prices) > 1 else wig20_current
        
        wig20 = {
            'value': wig20_current,
            'change': round((wig20_current - wig20_prev) / wig20_prev * 100, 2)
        }
        
        # Symulacja danych USD/PLN
        usd_base = 3.92
        usd_change = random.uniform(-0.05, 0.05)
        usd = {
            'value': round(usd_base + usd_change, 4),
            'change': round(usd_change / usd_base * 100, 2)
        }
        
        # Symulacja danych EUR/PLN
        eur_base = 4.31
        eur_change = random.uniform(-0.04, 0.06)
        eur = {
            'value': round(eur_base + eur_change, 4),
            'change': round(eur_change / eur_base * 100, 2)
        }
        
        # Dane Bitcoin już są w instrumentach ale dodajmy je też do wskaźników
        btc_prices = next((instr['prices'] for instr in instruments if instr['symbol'] == 'BTC-USD'), [68500])
        btc_current = btc_prices[-1]
        btc_prev = btc_prices[-2] if len(btc_prices) > 1 else btc_current
        
        btc = {
            'value': btc_current,
            'change': round((btc_current - btc_prev) / btc_prev * 100, 2)
        }
            
        return {
            'market_indicators': {
                'wig20': wig20,
                'usd': usd,
                'eur': eur,
                'btc': btc
            },
            'instruments': instruments
        }
    except Exception as e:
        app.logger.error(f"Error fetching market data: {str(e)}")
        return {
            'market_indicators': {
                'wig20': {'value': 0, 'change': 0},
                'usd': {'value': 0, 'change': 0},
                'eur': {'value': 0, 'change': 0},
                'btc': {'value': 0, 'change': 0}
            },
            'instruments': []
        }

# Dashboard z wykresami instrumentów handlowych
@app.route('/dashboard')
@login_required
def dashboard():
    # Pobierz tylko rzeczywiste instrumenty z API, pomijając instrumenty z bazy danych
    # Wcześniej było: instruments = db.get_instruments()
    instruments = []
    
    # Pobierz dane rynkowe
    market_data = get_external_market_data()
    
    return render_template('dashboard.html', 
                          instruments=instruments,
                          market_data=market_data)

# Endpoint API dla pobierania danych rynkowych
@app.route('/api/market_data')
@login_required
def api_market_data():
    return jsonify(get_external_market_data())

@app.before_request
def redirect_to_http():
    """Redirect HTTPS requests to HTTP"""
    if request.headers.get('X-Forwarded-Proto') == 'https':
        url = request.url.replace('https://', 'http://', 1)
        return redirect(url, code=301)

@app.route('/admin_panel', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if session['rola'] != 'administrator':
        flash("Brak dostępu do panelu administratora", "danger")
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST' and 'action' in request.form:
        action = request.form.get('action')
        user_id = request.form.get('user_id')
        
        if action == 'delete_user':
            if db.delete_user_by_id(user_id):
                flash("Użytkownik został usunięty pomyślnie!", "success")
                return jsonify({'success': True})
            else:
                flash("Błąd podczas usuwania użytkownika.", "danger")
                return jsonify({'error': "Błąd podczas usuwania użytkownika."}), 400
            
        elif action == 'role_user':
            user_role = request.form.get('user_role')
            if user_role == 'administrator':
                user_role = 1
            elif user_role == 'uzytkownik':
                user_role = 2
            
            print(f"Użytkownik: {user_id}, Rola: {user_role}")
            if db.update_user_role(user_id, user_role):
                flash("Użytkownik został zaktualizowany pomyślnie!", "success")
                return jsonify({'success': True})
            else:
                flash("Błąd podczas aktualizacji użytkownika.", "danger")
                return jsonify({'error': "Błąd podczas aktualizacji użytkownika."}), 400
    
    users = db.get_all_users()
    transactions = db.get_all_transactions() 
    return render_template('admin_panel.html', users=users, transactions=transactions)

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
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return jsonify({"error": "Email i hasło są wymagane"}), 400
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Nieprawidłowy format adresu email", "danger")
            return jsonify({"error": "Nieprawidłowy adres e-mail"}), 400
        
        if not (len(password) >= 6 and 
                re.search(r"[A-Za-z]", password) and 
                re.search(r"\d", password) and 
                re.search(r"[!@#$%^&*]", password)):
            flash("Hasło musi zawierać minimum 6 znaków, w tym literę, cyfrę i znak specjalny", "danger")
            return jsonify({"error": "Hasło nie spełnia wymagań bezpieczeństwa"}), 400     

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

        try:
            user = db.verify_user(email, password)
            if user:
                # print(user)
                session['user_id'] = user['user_id']
                session['email'] = user['email']
                session['rola'] = user['rola_nazwa']
                flash("Pomyślnie zalogowano!", "success")
                return jsonify({'success': True, 'redirect': url_for('dashboard')})
            else:
                flash("Nieprawidłowy email lub hasło", "danger")
                return jsonify({'error': 'Nieprawidłowy email lub hasło'}), 401
        except Exception as e:
            app.logger.error(f"Database error: {str(e)}")
            flash("Błąd połączenia z bazą danych", "danger")
            return jsonify({'error': 'Błąd serwera'}), 500

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