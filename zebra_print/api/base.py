"""
Abstract base class for API services.
Defines the contract for API client and server components.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional

class APIService(ABC):
    """Abstract base class for API services."""
    
    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if API service is running.
        
        Returns:
            bool: True if service is running
        """
        pass
    
    @abstractmethod
    def start(self) -> Tuple[bool, str]:
        """
        Start the API service.
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        pass
    
    @abstractmethod
    def stop(self) -> Tuple[bool, str]:
        """
        Stop the API service.
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, any]:
        """
        Get API service status.
        
        Returns:
            Dict containing status information
        """
        pass

class APIClient(ABC):
    """Abstract base class for API clients."""
    
    @abstractmethod
    def health_check(self, url: str) -> Tuple[bool, Optional[Dict]]:
        """
        Perform health check on API endpoint.
        
        Args:
            url: API endpoint URL
            
        Returns:
            Tuple[bool, Optional[Dict]]: (success, response_data)
        """
        pass
    
    @abstractmethod
    def print_labels(self, url: str, labels: List[Dict], headers: Optional[Dict] = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        Send print request to API endpoint.
        
        Args:
            url: API endpoint URL
            labels: List of label data
            headers: Optional HTTP headers
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (success, message, response_data)
        """
        pass