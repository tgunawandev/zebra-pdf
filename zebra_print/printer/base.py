"""
Abstract base class for printer services.
Defines the contract that all printer implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Tuple

class PrinterService(ABC):
    """Abstract base class for printer services."""
    
    @abstractmethod
    def is_ready(self) -> bool:
        """
        Check if printer is ready to print.
        
        Returns:
            bool: True if printer is ready
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, any]:
        """
        Get printer status information.
        
        Returns:
            Dict containing status information
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test printer connection.
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the printer name."""
        pass