"""
Integration tests for the modular Zebra Print Control System.
"""

import pytest
import time
from zebra_print.main import ZebraPrintApplication
from zebra_print.database.models import SystemState


class TestModularSystem:
    """Test the complete modular system integration."""
    
    def test_application_initialization(self):
        """Test application initializes correctly."""
        app = ZebraPrintApplication()
        
        assert app.api_service is not None
        assert app.printer_service is not None
        assert app.tunnel_providers is not None
        assert app.system_status is not None
        assert app.label_service is not None
        assert app.menu_controller is not None
    
    def test_system_status_overview(self):
        """Test system status provides complete overview."""
        app = ZebraPrintApplication()
        status = app.system_status.get_overall_status()
        
        # Check required status keys
        assert 'api' in status
        assert 'printer' in status
        assert 'integration_ready' in status
        
        # API status structure
        assert 'running' in status['api']
        assert 'details' in status['api']
        
        # Printer status structure
        assert 'ready' in status['printer']
        assert 'details' in status['printer']
    
    def test_label_service_functionality(self):
        """Test label service core functionality."""
        app = ZebraPrintApplication()
        
        # Test sample label creation
        sample_label = app.label_service.create_sample_label("TEST")
        assert sample_label['title'].startswith("W-CPN/OUT/TEST")
        assert 'date' in sample_label
        assert 'qr_code' in sample_label
        
        # Test label validation
        is_valid, message = app.label_service.validate_label_data(sample_label)
        assert is_valid
        assert message == "Valid"
        
        # Test custom label creation
        custom_label = app.label_service.create_custom_label(
            "CUSTOM-TITLE", "01/01/25", "QR123"
        )
        assert custom_label['title'] == "CUSTOM-TITLE"
        assert custom_label['date'] == "01/01/25"
        assert custom_label['qr_code'] == "QR123"
    
    def test_tunnel_providers_available(self):
        """Test all tunnel providers are available."""
        app = ZebraPrintApplication()
        
        expected_providers = ['cloudflare', 'cloudflare_named', 'ngrok']
        for provider in expected_providers:
            assert provider in app.tunnel_providers
            assert hasattr(app.tunnel_providers[provider], 'setup')
            assert hasattr(app.tunnel_providers[provider], 'start')
            assert hasattr(app.tunnel_providers[provider], 'stop')
    
    @pytest.mark.slow
    def test_api_service_lifecycle(self):
        """Test API service start/stop lifecycle."""
        app = ZebraPrintApplication()
        
        # Ensure API is stopped initially
        if app.api_service.is_running():
            app.api_service.stop()
            time.sleep(1)
        
        assert not app.api_service.is_running()
        
        # Test start
        success, message = app.api_service.start()
        if success:  # Only test if start succeeds (may fail if port in use)
            time.sleep(3)  # Wait for startup
            assert app.api_service.is_running()
            
            # Test stop
            success, message = app.api_service.stop()
            assert success
            time.sleep(1)
            assert not app.api_service.is_running()


class TestSystemComponents:
    """Test individual system components."""
    
    def test_database_integration(self):
        """Test database integration works."""
        app = ZebraPrintApplication()
        db = app.system_status.db
        
        # Test system state storage
        test_state = SystemState(
            component="test_component",
            is_configured=True,
            is_running=False
        )
        db.save_system_state(test_state)
        
        retrieved_state = db.get_system_state("test_component")
        assert retrieved_state is not None
        assert retrieved_state.component == "test_component"
        assert retrieved_state.is_configured is True
        assert retrieved_state.is_running is False
    
    def test_printer_service_status(self):
        """Test printer service provides status."""
        app = ZebraPrintApplication()
        status = app.printer_service.get_status()
        
        assert 'name' in status
        assert 'exists' in status
        assert 'state' in status
        assert status['name'] == "ZTC-ZD230-203dpi-ZPL"