"""
Unit tests for database functionality.
"""

import pytest
from datetime import datetime
from zebra_print.database.db_manager import DatabaseManager
from zebra_print.database.models import TunnelConfig, SystemState, PrinterConfig


class TestDatabaseManager:
    """Test database manager functionality."""
    
    def test_database_initialization(self, temp_db):
        """Test database initializes with correct tables."""
        db = DatabaseManager(temp_db)
        
        # Test database file is created
        assert db.db_path.exists()
        
        # Test connection works
        with db.get_connection() as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            
            table_names = [table[0] for table in tables]
            assert 'tunnel_configs' in table_names
            assert 'system_state' in table_names
            assert 'printer_configs' in table_names
    
    def test_tunnel_config_crud(self, temp_db):
        """Test tunnel configuration CRUD operations."""
        db = DatabaseManager(temp_db)
        
        # Create
        config = TunnelConfig(
            name="test_tunnel",
            is_configured=True,
            is_active=False,
            domain_mapping="test.example.com",
            config_data={"key": "value"}
        )
        db.save_tunnel_config(config)
        
        # Read
        retrieved = db.get_tunnel_config("test_tunnel")
        assert retrieved is not None
        assert retrieved.name == "test_tunnel"
        assert retrieved.is_configured is True
        assert retrieved.domain_mapping == "test.example.com"
        assert retrieved.config_data == {"key": "value"}
        
        # Update status
        db.update_tunnel_status("test_tunnel", True, "https://test.example.com")
        updated = db.get_tunnel_config("test_tunnel")
        assert updated.is_active is True
        assert updated.current_url == "https://test.example.com"
    
    def test_system_state_management(self, temp_db):
        """Test system state management."""
        db = DatabaseManager(temp_db)
        
        state = SystemState(
            component="api_server",
            is_configured=True,
            is_running=False,
            config_data={"port": 5000},
            last_status="stopped"
        )
        db.save_system_state(state)
        
        retrieved = db.get_system_state("api_server")
        assert retrieved is not None
        assert retrieved.component == "api_server"
        assert retrieved.is_configured is True
        assert retrieved.config_data == {"port": 5000}
    
    def test_printer_config_management(self, temp_db):
        """Test printer configuration management."""
        db = DatabaseManager(temp_db)
        
        config = PrinterConfig(
            name="Test-Printer",
            connection_type="USB",
            device_uri="usb://test",
            is_default=True,
            is_configured=True
        )
        db.save_printer_config(config)
        
        retrieved = db.get_default_printer()
        assert retrieved is not None
        assert retrieved.name == "Test-Printer"
        assert retrieved.is_default is True


class TestDataModels:
    """Test data model classes."""
    
    def test_tunnel_config_model(self):
        """Test TunnelConfig model."""
        config = TunnelConfig(
            name="cloudflare",
            domain_mapping="example.com"
        )
        
        assert config.name == "cloudflare"
        assert config.is_configured is False  # Default
        assert config.domain_mapping == "example.com"
        assert isinstance(config.created_at, datetime)
    
    def test_system_state_model(self):
        """Test SystemState model."""
        state = SystemState(
            component="printer",
            is_configured=True
        )
        
        assert state.component == "printer"
        assert state.is_configured is True
        assert state.is_running is False  # Default
        assert isinstance(state.updated_at, datetime)
    
    def test_printer_config_model(self):
        """Test PrinterConfig model."""
        config = PrinterConfig(
            name="ZTC-ZD230",
            connection_type="USB"
        )
        
        assert config.name == "ZTC-ZD230"
        assert config.connection_type == "USB"
        assert config.is_configured is False  # Default
        assert isinstance(config.created_at, datetime)