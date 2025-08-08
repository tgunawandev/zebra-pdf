"""
HTTP client implementation for API communication.
Handles HTTP requests to the label printing API.
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
from zebra_print.api.base import APIClient

class HTTPAPIClient(APIClient):
    """HTTP-based API client implementation."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
    
    def health_check(self, url: str) -> Tuple[bool, Optional[Dict]]:
        """Perform health check on API endpoint."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return True, data
                except:
                    return True, {'status': 'ok', 'raw_response': response.text}
            else:
                return False, {
                    'error': f"HTTP {response.status_code}",
                    'response': response.text[:200]
                }
                
        except requests.exceptions.Timeout:
            return False, {'error': 'Request timeout'}
        except requests.exceptions.ConnectionError:
            return False, {'error': 'Connection failed'}
        except Exception as e:
            return False, {'error': str(e)}
    
    def print_labels(self, url: str, labels: List[Dict], headers: Optional[Dict] = None) -> Tuple[bool, str, Optional[Dict]]:
        """Send print request to API endpoint."""
        try:
            # Prepare headers
            request_headers = {'Content-Type': 'application/json'}
            if headers:
                request_headers.update(headers)
            
            # Prepare payload
            payload = {'labels': labels}
            
            # Send request
            response = self.session.post(
                url,
                data=json.dumps(payload),
                headers=request_headers,
                timeout=self.timeout
            )
            
            # Parse response
            response_data = None
            try:
                response_data = response.json()
            except:
                response_data = {'raw_response': response.text[:500]}
            
            if response.status_code == 200:
                return True, "Labels printed successfully", response_data
            else:
                error_msg = response_data.get('error', f"HTTP {response.status_code}")
                return False, f"Print failed: {error_msg}", response_data
                
        except requests.exceptions.Timeout:
            return False, "Request timeout", {'error': 'timeout'}
        except requests.exceptions.ConnectionError:
            return False, "Connection failed", {'error': 'connection_failed'}
        except Exception as e:
            return False, f"Request failed: {str(e)}", {'error': str(e)}
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()