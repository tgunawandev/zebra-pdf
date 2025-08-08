"""
Core label printing business logic.
Handles label data processing and printing operations.
"""

from typing import Dict, List, Tuple
from datetime import datetime
from zebra_print.api.base import APIClient

class LabelService:
    """Core service for label printing operations."""
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
    
    def create_sample_label(self, prefix: str = "TEST") -> Dict:
        """Create a sample label for testing."""
        return {
            "title": f"W-CPN/OUT/{prefix}",
            "date": datetime.now().strftime("%d/%m/%y"),
            "qr_code": f"{prefix}{datetime.now().strftime('%H%M%S')}"
        }
    
    def create_custom_label(self, title: str, date: str, qr_code: str) -> Dict:
        """Create a custom label with provided data."""
        return {
            "title": title,
            "date": date,
            "qr_code": qr_code
        }
    
    def validate_label_data(self, label: Dict) -> Tuple[bool, str]:
        """Validate label data structure."""
        required_fields = ['title', 'date', 'qr_code']
        
        for field in required_fields:
            if field not in label:
                return False, f"Missing required field: {field}"
            if not label[field] or not isinstance(label[field], str):
                return False, f"Invalid value for field: {field}"
        
        return True, "Valid"
    
    def validate_labels_request(self, labels: List[Dict]) -> Tuple[bool, str]:
        """Validate a list of labels for printing."""
        if not isinstance(labels, list) or len(labels) == 0:
            return False, "Labels must be a non-empty list"
        
        for i, label in enumerate(labels):
            is_valid, message = self.validate_label_data(label)
            if not is_valid:
                return False, f"Label {i}: {message}"
        
        return True, "Valid"
    
    def print_labels_local(self, labels: List[Dict], api_url: str) -> Tuple[bool, str, Dict]:
        """Print labels to local API server."""
        # Validate labels
        is_valid, message = self.validate_labels_request(labels)
        if not is_valid:
            return False, f"Validation error: {message}", {}
        
        # Send print request
        return self.api_client.print_labels(api_url, labels)
    
    def print_labels_tunnel(self, labels: List[Dict], tunnel_url: str, tunnel_type: str = 'cloudflare') -> Tuple[bool, str, Dict]:
        """Print labels via tunnel (as Odoo would)."""
        # Validate labels
        is_valid, message = self.validate_labels_request(labels)
        if not is_valid:
            return False, f"Validation error: {message}", {}
        
        # Prepare headers based on tunnel type
        headers = {'Content-Type': 'application/json'}
        if tunnel_type == 'ngrok':
            headers['ngrok-skip-browser-warning'] = 'true'
        
        # Send print request
        return self.api_client.print_labels(f"{tunnel_url}/print", labels, headers)
    
    def test_api_connection(self, api_url: str) -> Tuple[bool, Dict]:
        """Test connection to API server."""
        return self.api_client.health_check(api_url)
    
    def test_tunnel_connection(self, tunnel_url: str, tunnel_type: str = 'cloudflare') -> Tuple[bool, Dict]:
        """Test connection to tunnel endpoint."""
        headers = {}
        if tunnel_type == 'ngrok':
            headers['ngrok-skip-browser-warning'] = 'true'
        
        # For tunnel test, we use health endpoint
        health_url = f"{tunnel_url}/health"
        return self.api_client.health_check(health_url)