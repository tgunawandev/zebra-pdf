"""
Database module for persistent storage.
Uses SQLite for configuration and state management.
"""

from .db_manager import DatabaseManager
from .models import TunnelConfig, SystemState

__all__ = ['DatabaseManager', 'TunnelConfig', 'SystemState']