## @file database/__init__.py
## @brief Inicjalizacja pakietu database
## @details Eksportuje klasę DatabaseConnection do użytku przez inne moduły

from .connection import DatabaseConnection

__all__ = ['DatabaseConnection']