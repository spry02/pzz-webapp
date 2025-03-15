# Dokumentacja Bazy Danych

## Diagram ERD
![Diagram ERD](./erd-diagram.png)

## Tabele w Bazie Danych

### 1️⃣ Tabela `Uzytkownik`
Przechowuje dane użytkowników aplikacji.

**Kolumny:**
- `user_id` – unikalny identyfikator użytkownika (SERIAL PRIMARY KEY).
- `email` – adres e-mail użytkownika (unikalny).
- `haslo_hash` – zaszyfrowane hasło użytkownika.
- `rola_id` – klucz obcy wskazujący na tabelę `Rola`.
- `data_utworzenia` – data rejestracji użytkownika.

**Relacja:**
- `rola_id` jest kluczem obcym, wskazującym na `rola_id` w tabeli `Rola`.

### 2️⃣ Tabela `Rola`
Przechowuje dostępne role użytkowników.

**Kolumny:**
- `rola_id` – unikalny identyfikator roli (SERIAL PRIMARY KEY).
- `nazwa` – nazwa roli (np. administrator, uzytkownik).

**Relacja:**
- Jeden użytkownik może mieć jedną rolę, ale wiele użytkowników może mieć tę samą rolę (relacja 1:N).

### 3️⃣ Tabela `InstrumentHandlowy`
Przechowuje instrumenty dostępne na giełdzie (np. akcje, obligacje).

**Kolumny:**
- `instrument_id` – unikalny identyfikator instrumentu (SERIAL PRIMARY KEY).
- `nazwa` – nazwa instrumentu (np. "Akcje Testowe").
- `symbol` – skrót symbolu giełdowego (np. TST).
- `data_utworzenia` – data dodania instrumentu.

**Relacja:**
- Każdy instrument może pojawiać się w wielu transakcjach (relacja 1:N).

### 4️⃣ Tabela `Transakcja`
Przechowuje informacje o dokonanych transakcjach.

**Kolumny:**
- `transakcja_id` – unikalny identyfikator transakcji (SERIAL PRIMARY KEY).
- `user_id` – klucz obcy wskazujący na `user_id` w `Uzytkownik`.
- `instrument_id` – klucz obcy wskazujący na `instrument_id` w `InstrumentHandlowy`.
- `typ_transakcji` – określa typ transakcji (kupno / sprzedaz).
- `ilosc` – ilość jednostek instrumentu w transakcji.
- `cena` – cena jednostkowa instrumentu.
- `data_transakcji` – czas wykonania transakcji.

**Relacje:**
- `user_id` łączy się z `Uzytkownik(user_id)`, oznacza to, że każda transakcja jest przypisana do konkretnego użytkownika (relacja 1:N).
- `instrument_id` łączy się z `InstrumentHandlowy(instrument_id)`, co oznacza, że każda transakcja dotyczy konkretnego instrumentu (relacja 1:N).

## Podsumowanie relacji
- Użytkownik może wykonać wiele transakcji (1:N).
- Instrument handlowy może być częścią wielu transakcji (1:N).
- Użytkownik ma jedną rolę, ale wiele użytkowników może mieć tę samą rolę (1:N).