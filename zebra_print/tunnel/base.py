"""
Abstract base class for tunnel providers.
Defines the contract that all tunnel implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple

class TunnelProvider(ABC):
    """Abstract base class for tunnel providers like Cloudflare, Ngrok, etc."""
    
    @abstractmethod
    def setup(self) -> Tuple[bool, str]:
        """
        Set up the tunnel provider (one-time setup).
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        pass
    
    @abstractmethod
    def start(self) -> Tuple[bool, str, Optional[str]]:
        """
        Start the tunnel.
        
        Returns:
            Tuple[bool, str, Optional[str]]: (success, message, tunnel_url)
        """
        pass
    
    @abstractmethod
    def stop(self) -> Tuple[bool, str]:
        """
        Stop the tunnel.
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, any]:
        """
        Get current tunnel status.
        
        Returns:
            Dict containing status information
        """
        pass
    
    @abstractmethod
    def is_active(self) -> bool:
        """
        Check if tunnel is currently active.
        
        Returns:
            bool: True if tunnel is active
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the tunnel provider name."""
        pass
    
    @property
    @abstractmethod
    def is_permanent(self) -> bool:
        """Check if this tunnel provides permanent URLs."""
        pass