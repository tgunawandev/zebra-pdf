"""
Unit tests for label service functionality.
"""

import pytest
from zebra_print.core.label_service import LabelService
from zebra_print.api.http_client import HTTPAPIClient


class TestLabelService:
    """Test label service functionality."""
    
    def test_sample_label_creation(self):
        """Test sample label creation."""
        api_client = HTTPAPIClient()
        service = LabelService(api_client)
        
        label = service.create_sample_label("TEST")
        
        assert 'title' in label
        assert 'date' in label
        assert 'qr_code' in label
        assert label['title'].startswith("W-CPN/OUT/TEST")
        assert "TEST" in label['qr_code']
    
    def test_custom_label_creation(self):
        """Test custom label creation."""
        api_client = HTTPAPIClient()
        service = LabelService(api_client)
        
        label = service.create_custom_label(
            "CUSTOM-TITLE",
            "01/01/25", 
            "QR12345"
        )
        
        assert label['title'] == "CUSTOM-TITLE"
        assert label['date'] == "01/01/25"
        assert label['qr_code'] == "QR12345"
    
    def test_label_validation_valid(self, sample_label_data):
        """Test validation of valid label data."""
        api_client = HTTPAPIClient()
        service = LabelService(api_client)
        
        is_valid, message = service.validate_label_data(sample_label_data)
        
        assert is_valid is True
        assert message == "Valid"
    
    def test_label_validation_missing_fields(self):
        """Test validation with missing required fields."""
        api_client = HTTPAPIClient()
        service = LabelService(api_client)
        
        # Missing title
        incomplete_label = {
            "date": "01/01/25",
            "qr_code": "QR123"
        }
        
        is_valid, message = service.validate_label_data(incomplete_label)
        
        assert is_valid is False
        assert "Missing required field: title" in message
    
    def test_label_validation_invalid_values(self):
        """Test validation with invalid field values."""
        api_client = HTTPAPIClient()
        service = LabelService(api_client)
        
        # Empty title
        invalid_label = {
            "title": "",
            "date": "01/01/25",
            "qr_code": "QR123"
        }
        
        is_valid, message = service.validate_label_data(invalid_label)
        
        assert is_valid is False
        assert "Invalid value for field: title" in message
    
    def test_labels_request_validation(self, sample_label_data):
        """Test validation of multiple labels."""
        api_client = HTTPAPIClient()
        service = LabelService(api_client)
        
        labels = [sample_label_data, sample_label_data.copy()]
        
        is_valid, message = service.validate_labels_request(labels)
        
        assert is_valid is True
        assert message == "Valid"
    
    def test_labels_request_validation_empty(self):
        """Test validation with empty labels list."""
        api_client = HTTPAPIClient()
        service = LabelService(api_client)
        
        is_valid, message = service.validate_labels_request([])
        
        assert is_valid is False
        assert "Labels must be a non-empty list" in message
    
    def test_labels_request_validation_invalid_item(self, sample_label_data):
        """Test validation with one invalid label in list."""
        api_client = HTTPAPIClient()
        service = LabelService(api_client)
        
        invalid_label = sample_label_data.copy()
        del invalid_label['title']
        
        labels = [sample_label_data, invalid_label]
        
        is_valid, message = service.validate_labels_request(labels)
        
        assert is_valid is False
        assert "Label 1:" in message
        assert "Missing required field: title" in message