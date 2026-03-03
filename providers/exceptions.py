"""Dedicated exceptions for data providers."""


class DataProviderError(Exception):
    """Bazowy wyjatek dla providerow danych."""


class InvalidFileStructureError(DataProviderError):
    """Nieprawidlowa struktura pliku wejsciowego."""
