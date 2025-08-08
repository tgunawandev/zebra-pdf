"""
Database models for persistent storage.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class TunnelConfig:
    """Tunnel configuration model."""
    name: str                    # cloudflare, ngrok
    is_configured: bool = False  # Has been set up
    is_active: bool = False      # Currently running
    current_url: Optional[str] = None
    domain_mapping: Optional[str] = None  # For named tunnels
    config_data: Optional[Dict[str, Any]] = None
    last_used: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class SystemState:
    """System state model."""
    component: str               # api, printer, tunnel
    is_configured: bool = False
    is_running: bool = False
    config_data: Optional[Dict[str, Any]] = None
    last_status: Optional[str] = None
    updated_at: datetime = datetime.now()

@dataclass
class PrinterConfig:
    """Printer configuration model."""
    name: str
    connection_type: str  # USB, Network
    device_uri: Optional[str] = None
    is_default: bool = False
    is_configured: bool = False
    last_tested: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()