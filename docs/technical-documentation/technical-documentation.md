# Dokumentacja Techniczna - Demonstracyjna Giełda

![Data aktualizacji](https://img.shields.io/badge/Data_aktualizacji-2025--04--24-brightgreen)
![Wersja](https://img.shields.io/badge/Wersja-1.0-brightgreen)
![Status](https://img.shields.io/badge/Status-Produkcyjny-success)

## 📋 Spis treści

1. [Przegląd systemu](#-przegląd-systemu)
2. [Architektura aplikacji](#-architektura-aplikacji)
3. [Stack technologiczny](#-stack-technologiczny)
4. [Struktura projektu](#-struktura-projektu)
5. [Baza danych](#-baza-danych)
6. [API i endpointy](#-api-i-endpointy)
7. [Autoryzacja i uwierzytelnianie](#-autoryzacja-i-uwierzytelnianie)
8. [Funkcjonalności](#-funkcjonalności)
9. [Instalacja i uruchomienie](#-instalacja-i-uruchomienie)
10. [Znane problemy i ograniczenia](#-znane-problemy-i-ograniczenia)

## 🔍 Przegląd systemu

"Demonstracyjna Giełda" to aplikacja webowa zaprojektowana do symulacji działania platformy handlu instrumentami finansowymi. System umożliwia użytkownikom rejestrację, logowanie, przeglądanie wykresów instrumentów handlowych oraz przeprowadzanie wirtualnych transakcji kupna i sprzedaży aktywów z wykorzystaniem dźwigni finansowej.

Głównym celem aplikacji jest edukacyjna symulacja rynku giełdowego w bezpiecznym środowisku, bez ryzyka utraty rzeczywistych środków finansowych.

## 🏗 Architektura aplikacji

Aplikacja wykorzystuje klasyczną architekturę MVC (Model-View-Controller):

1. **Model** - Reprezentowany przez `db.py` oraz strukturę bazy danych, odpowiedzialny za przechowywanie i zarządzanie danymi.
2. **View** - Szablony HTML z wykorzystaniem Jinja2 w katalogu `website/templates/`.
3. **Controller** - Logika aplikacji zaimplementowana w `app.py`, obsługująca żądania użytkowników i aktualizująca model.

Aplikacja została zaprojektowana jako wielowarstwowa:
- **Warstwa prezentacji**: Interfejs użytkownika (UI) oparty na HTML/CSS/JavaScript
- **Warstwa logiki biznesowej**: Flask (Python)
- **Warstwa dostępu do danych**: Moduł bazy danych i API
- **Warstwa danych**: MySQL

## 🛠 Stack technologiczny

### Backend
- **Python 3.x**: Główny język programowania
- **Flask**: Lekki framework webowy dla Pythona
- **MySQL**: Relacyjna baza danych

### Frontend
- **HTML5/CSS3**: Struktura i stylizacja interfejsu użytkownika
- **JavaScript**: Logika front-endowa i dynamiczne elementy UI
- **Bootstrap 5**: Framework CSS dla responsywnego designu
- **Chart.js**: Biblioteka do tworzenia wykresów
- **Font Awesome**: Zestaw ikon i elementów graficznych

### Narzędzia i biblioteki
- **Jinja2**: System szablonów dla Flask
- **MySQL Connector**: Adapter łączący Python z bazą danych MySQL
- **dotenv**: Zarządzanie zmiennymi środowiskowymi
- **Flask-Session**: Zarządzanie sesjami użytkowników
- **Werkzeug**: Narzędzia do hashowania haseł i innych funkcji bezpieczeństwa

## 📁 Struktura projektu
```
pzz-webapp/
├── database/
│ └── migrations/ 
│   └── 001_initial_schema.sql 
├── docs/ 
│ ├── database/ 
│ │ ├── diagram_erd.png 
│ │ └── technical-documentation.md 
│ └── project-requirements/ 
│   └── project-requirements.md 
├── website/ 
│ ├── static/ 
│ │ └── style.css 
│ ├── templates/ 
│ │ ├── admin_panel.html 
│ │ ├── dashboard.html 
│ │ ├── edit_profile.html 
│ │ ├── login.html 
│ │ └── register.html 
│ └── app.py 
└── README.md
```

## 💾 Baza danych

### Schemat bazy danych

Aplikacja wykorzystuje relacyjną bazę danych MySQL z następującymi tabelami:

1. **Uzytkownik**: Przechowuje informacje o użytkownikach systemu
   - `user_id`: Unikalny identyfikator (klucz główny)
   - `email`: Adres e-mail użytkownika (unikalny)
   - `haslo_hash`: Zaszyfrowane hasło 
   - `rola_id`: ID roli użytkownika (klucz obcy do tabeli Rola)
   - `data_utworzenia`: Data rejestracji użytkownika

2. **Rola**: Przechowuje dostępne role w systemie
   - `rola_id`: Unikalny identyfikator roli (klucz główny)
   - `nazwa`: Nazwa roli (np. administrator, uzytkownik)

3. **Instrument_Handlowy**: Reprezentuje dostępne instrumenty finansowe
   - `instrument_id`: Unikalny identyfikator (klucz główny)
   - `nazwa`: Pełna nazwa instrumentu
   - `symbol`: Unikalny symbol giełdowy
   - `data_utworzenia`: Data dodania instrumentu

4. **Transakcja**: Przechowuje informacje o transakcjach
   - `transakcja_id`: Unikalny identyfikator (klucz główny)
   - `user_id`: ID użytkownika dokonującego transakcji (klucz obcy)
   - `instrument_id`: ID instrumentu, którego dotyczy transakcja (klucz obcy)
   - `typ_transakcji`: Rodzaj transakcji (kupno/sprzedaz)
   - `ilosc`: Liczba jednostek instrumentu
   - `cena`: Cena jednostkowa instrumentu
   - `data_transakcji`: Data i czas transakcji

### Diagram ERD

Diagram związków encji (ERD) jest dostępny w pliku [diagram_erd.png](./docs/database/diagram_erd.png).

## 🌐 API i endpointy

### Endpointy stron

| Metoda | Endpoint | Opis | Wymagane uwierzytelnienie |
|--------|----------|------|---------------------------|
| GET/POST | `/register` | Rejestracja nowego użytkownika | Nie |
| GET/POST | `/login` | Logowanie użytkownika | Nie |
| GET | `/logout` | Wylogowanie użytkownika | Tak |
| GET | `/dashboard` | Główny panel użytkownika z wykresami | Tak |
| GET/POST | `/edit_profile` | Edycja danych profilu | Tak |
| GET/POST | `/admin_panel` | Panel administracyjny | Tak (tylko admin) |

### API REST

| Metoda | Endpoint | Opis | Format danych |
|--------|----------|------|---------------|
| GET | `/api/market_data` | Pobieranie danych rynkowych | JSON |
| POST | `/api/transaction` | Utworzenie nowej transakcji | JSON |

## 🔐 Autoryzacja i uwierzytelnianie

System wykorzystuje oparty na sesjach mechanizm uwierzytelniania:

1. **Rejestracja**: Hasła są hashowane przed zapisaniem w bazie danych.
2. **Logowanie**: Sprawdzenie poprawności danych i utworzenie sesji użytkownika.
3. **Kontrola dostępu**: Dekorator `@login_required` weryfikuje sesję użytkownika.
4. **Role**: System ról zapewnia dodatkowe poziomy uprawnień (administrator/użytkownik).

## ✨ Funkcjonalności

### 1. System rejestracji i logowania
- Rejestracja nowych użytkowników z walidacją formularzy
- Logowanie z wykorzystaniem sesji
- Hashowanie haseł dla bezpieczeństwa

### 2. Panel użytkownika
- Podgląd danych konta
- Edycja profilu (zmiana e-maila, hasła)
- Usuwanie konta

### 3. Dashboard giełdowy
- Wizualizacja instrumentów finansowych
- Interaktywne wykresy z wykorzystaniem Chart.js
- Symulacja zmian cen w czasie rzeczywistym

### 4. System transakcji
- Kupno i sprzedaż instrumentów
- Historia transakcji
- Zarządzanie wirtualnym portfelem

### 5. Panel administracyjny
- Zarządzanie użytkownikami
- Zmiana ról użytkowników
- Usuwanie użytkowników

## 🚀 Instalacja i uruchomienie

### Wymagania wstępne
- Python 3.x
- MySQL

### Instrukcja instalacji

1. Sklonuj repozytorium:
    ```
    git clone https://github.com/spry02/pzz-webapp.git cd pzz-webapp
    ```
2. Zainstaluj wymagane zależności:
    ```
    pip install -r requirements.txt
    ```

3. Skonfiguruj bazę danych:
    ```
    mysql -u root < database/migrations/001_initial_schema.sql
    ```

4. Utwórz plik `.env` z parametrami połączenia do bazy danych:
    ```
    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=twoje_haslo
    ```

5. Uruchom aplikację:
    ```
    python website/app.py
    ```

6. Otwórz przeglądarkę i przejdź pod adres `http://localhost:5000`

## ⚠️ Znane problemy i ograniczenia

1. Aplikacja przekierowuje zapytania HTTPS na HTTP, co może powodować problemy z bezpieczeństwem w środowisku produkcyjnym.
2. System nie obsługuje dwuskładnikowego uwierzytelniania (2FA).
3. Aplikacja ma ograniczone możliwości personalizacji ustawień użytkownika.

---

**© 2025 Demonstracyjna Giełda / Pracownia Programowania Zespołowego**
