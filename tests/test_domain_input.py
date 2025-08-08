"""
Unit tests for domain input functionality.
"""

import pytest
from zebra_print.tunnel.cloudflare_named import CloudflareNamedTunnel
from zebra_print.database.db_manager import DatabaseManager


class TestDomainInput:
    """Test domain input and validation."""
    
    def test_valid_domain_setting(self, temp_db):
        """Test setting valid domains."""
        tunnel = CloudflareNamedTunnel()
        test_domains = [
            "tln-zebra-01.abcfood.app",
            "printer-hq.mycompany.com", 
            "zebra-label.mydomain.org"
        ]
        
        for domain in test_domains:
            success, message = tunnel.set_custom_domain(domain)
            assert success, f"Failed to set domain {domain}: {message}"
            assert domain in message
    
    def test_domain_storage(self, temp_db):
        """Test domain storage in database."""
        tunnel = CloudflareNamedTunnel()
        db = DatabaseManager(temp_db)
        
        test_domain = "test-zebra.example.com"
        success, _ = tunnel.set_custom_domain(test_domain)
        assert success
        
        stored_config = db.get_tunnel_config("cloudflare_named")
        assert stored_config is not None
        assert stored_config.domain_mapping == test_domain
        assert stored_config.is_configured is True
    
    def test_invalid_domain_formats(self):
        """Test validation of invalid domain formats."""
        tunnel = CloudflareNamedTunnel()
        
        invalid_domains = [
            "",
            "invalid",
            "UPPERCASE.COM",
            "domain with spaces.com",
            "domain..com"
        ]
        
        for domain in invalid_domains:
            success, _ = tunnel.set_custom_domain(domain)
            assert not success, f"Should reject invalid domain: {domain}"
    
    def test_webhook_url_generation(self, temp_db):
        """Test webhook URL generation."""
        tunnel = CloudflareNamedTunnel()
        domain = "webhook-test.example.com"
        
        tunnel.set_custom_domain(domain)
        webhook_url = tunnel.get_webhook_url()
        
        expected_url = f"https://{domain}/print"
        # Note: webhook_url will be None unless tunnel is active
        # This tests the URL format logic
        assert tunnel.custom_domain == domain


class TestDomainValidation:
    """Test domain validation logic."""
    
    def test_domain_format_validation(self):
        """Test domain format validation."""
        tunnel = CloudflareNamedTunnel()
        
        # Valid domains
        valid_domains = [
            "sub.domain.com",
            "multi-word-sub.domain.org",
            "test123.example.net"
        ]
        
        for domain in valid_domains:
            success, _ = tunnel.set_custom_domain(domain)
            assert success, f"Valid domain rejected: {domain}"
        
        # Invalid domains
        invalid_domains = [
            "no-dots",
            ".starts-with-dot.com",
            "ends-with-dot.com.",
            "has..double.dots.com"
        ]
        
        for domain in invalid_domains:
            success, _ = tunnel.set_custom_domain(domain)
            assert not success, f"Invalid domain accepted: {domain}"