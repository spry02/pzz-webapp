CREATE DATABASE IF NOT EXISTS Pracownia_Programowania_Zespolowego;
USE Pracownia_Programowania_Zespolowego;

CREATE TABLE Uzytkownik (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    haslo_hash TEXT NOT NULL,
    rola ENUM('administrator', 'uzytkownik') NOT NULL,
    data_utworzenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Instrument_Handlowy (
    instrument_id INT AUTO_INCREMENT PRIMARY KEY,
    nazwa VARCHAR(100) UNIQUE NOT NULL,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    data_utworzenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Transakcja (
    transakcja_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    instrument_id INT NOT NULL,
    typ_transakcji ENUM('kupno', 'sprzedaz') NOT NULL,
    ilosc DECIMAL(15, 2) NOT NULL,
    cena DECIMAL(15, 2) NOT NULL,
    data_transakcji TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Uzytkownik(user_id) ON DELETE CASCADE,
    FOREIGN KEY (instrument_id) REFERENCES Instrument_Handlowy(instrument_id) ON DELETE CASCADE
);

CREATE TABLE Rola (
    rola_id INT AUTO_INCREMENT PRIMARY KEY,
    nazwa VARCHAR(50) UNIQUE NOT NULL
);

ALTER TABLE Uzytkownik ADD COLUMN rola_id INT NOT NULL;
ALTER TABLE Uzytkownik ADD CONSTRAINT fk_rola FOREIGN KEY (rola_id) REFERENCES Rola(rola_id);

INSERT INTO Rola (nazwa) VALUES ('administrator'), ('uzytkownik');

INSERT INTO Instrument_Handlowy (nazwa, symbol) VALUES ('Akcje Testowe', 'TST'), ('Obligacje Demo', 'DEM');
