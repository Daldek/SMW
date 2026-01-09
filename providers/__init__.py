"""Data providers for water quality monitoring system."""

from providers.base import DataProvider
from providers.excel import ExcelProvider

__all__ = ["DataProvider", "ExcelProvider"]
