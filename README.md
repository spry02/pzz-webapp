# pzz-webapp
![Data aktualizacji](https://img.shields.io/badge/Data_aktualizacji-2025--04--24-brightgreen)
![Wersja](https://img.shields.io/badge/Wersja-1.0-brightgreen)

Aplikacja webowa "Demonstracyjna Giełda" - Pracownia Programowania Zespołowego

## 🔎 Przegląd projektu
Demonstracyjna Giełda to aplikacja webowa pozwalająca na symulację działania platformy handlu instrumentami finansowymi. Aplikacja umożliwia rejestrację, logowanie, przeglądanie wykresów instrumentów handlowych oraz symulację zakupu i sprzedaży aktywów z użyciem dźwigni finansowej.

## ✅ Zaimplementowane funkcje
- System rejestracji i logowania użytkowników
- Dashboard z wizualizacją instrumentów handlowych
- Interaktywne wykresy notowań (Chart.js)
- Symulacja zmian cen instrumentów w czasie rzeczywistym
- Funkcje kupna i sprzedaży instrumentów
- Zarządzanie profilem użytkownika (zmiana danych, usuwanie konta)
- Responsywny interfejs użytkownika

## 🛠️ Stos technologiczny
- **Backend**: Python (Flask)
- **Frontend**: HTML5, CSS3, JavaScript
- **Baza danych**: MySQL
- **Biblioteki UI**: Bootstrap 5, Font Awesome
- **Wizualizacja danych**: Chart.js

## 🚀 Instalacja i uruchomienie
1. Sklonuj repozytorium
2. Zainstaluj zależności:
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

## 📝 Dokumentacja
W tym repozytorium znajdują się:
- [Dokumentacja techniczna bazy danych](./docs/database/technical-documentation.md)
- [Diagram ERD bazy danych](./docs/database/diagram_erd.png)
- [Dokumentacja wymagań projektu](./docs/project-requirements/project-requirements.md)
- [Dokumentacja techniczna projektu](./docs/technical-documentation/technical-documentation.md)
- [Dokumentacja użytkownika](./docs/user-documentation/user-documentation.md)

## 🔄 Aktualne funkcjonalności
- Obsługa kont użytkowników (rejestracja, logowanie, edycja profilu)
- Dashboard z wykresami instrumentów handlowych
- Symulacja zmian cen w czasie rzeczywistym
- Interfejs do kupna i sprzedaży instrumentów
