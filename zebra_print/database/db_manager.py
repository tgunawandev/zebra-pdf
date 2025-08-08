"""
SQLite database manager for persistent storage.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from .models import TunnelConfig, SystemState, PrinterConfig

class DatabaseManager:
    """SQLite database manager for persistent configuration."""
    
    def __init__(self, db_path: str = "zebra_print.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def init_database(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            # Tunnel configurations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tunnel_configs (
                    name TEXT PRIMARY KEY,
                    is_configured BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT FALSE,
                    current_url TEXT,
                    domain_mapping TEXT,
                    config_data TEXT,  -- JSON
                    last_used TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # System state table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_state (
                    component TEXT PRIMARY KEY,
                    is_configured BOOLEAN DEFAULT FALSE,
                    is_running BOOLEAN DEFAULT FALSE,
                    config_data TEXT,  -- JSON
                    last_status TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Printer configurations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS printer_configs (
                    name TEXT PRIMARY KEY,
                    connection_type TEXT,
                    device_uri TEXT,
                    is_default BOOLEAN DEFAULT FALSE,
                    is_configured BOOLEAN DEFAULT FALSE,
                    last_tested TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    # Tunnel Config Methods
    def save_tunnel_config(self, config: TunnelConfig):
        """Save tunnel configuration."""
        with self.get_connection() as conn:
            config_json = json.dumps(config.config_data) if config.config_data else None
            
            conn.execute("""
                INSERT OR REPLACE INTO tunnel_configs 
                (name, is_configured, is_active, current_url, domain_mapping, 
                 config_data, last_used, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                config.name, config.is_configured, config.is_active,
                config.current_url, config.domain_mapping, config_json,
                config.last_used, datetime.now()
            ))
            conn.commit()
    
    def get_tunnel_config(self, name: str) -> Optional[TunnelConfig]:
        """Get tunnel configuration."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM tunnel_configs WHERE name = ?", (name,)
            ).fetchone()
            
            if row:
                config_data = json.loads(row['config_data']) if row['config_data'] else None
                return TunnelConfig(
                    name=row['name'],
                    is_configured=bool(row['is_configured']),
                    is_active=bool(row['is_active']),
                    current_url=row['current_url'],
                    domain_mapping=row['domain_mapping'],
                    config_data=config_data,
                    last_used=row['last_used'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
            return None
    
    def get_all_tunnel_configs(self) -> List[TunnelConfig]:
        """Get all tunnel configurations."""
        configs = []
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM tunnel_configs").fetchall()
            
            for row in rows:
                config_data = json.loads(row['config_data']) if row['config_data'] else None
                configs.append(TunnelConfig(
                    name=row['name'],
                    is_configured=bool(row['is_configured']),
                    is_active=bool(row['is_active']),
                    current_url=row['current_url'],
                    domain_mapping=row['domain_mapping'],
                    config_data=config_data,
                    last_used=row['last_used'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                ))
        
        return configs
    
    def update_tunnel_status(self, name: str, is_active: bool, current_url: Optional[str] = None):
        """Update tunnel active status."""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE tunnel_configs 
                SET is_active = ?, current_url = ?, updated_at = ?
                WHERE name = ?
            """, (is_active, current_url, datetime.now(), name))
            conn.commit()
    
    # System State Methods
    def save_system_state(self, state: SystemState):
        """Save system state."""
        with self.get_connection() as conn:
            config_json = json.dumps(state.config_data) if state.config_data else None
            
            conn.execute("""
                INSERT OR REPLACE INTO system_state 
                (component, is_configured, is_running, config_data, last_status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                state.component, state.is_configured, state.is_running,
                config_json, state.last_status, datetime.now()
            ))
            conn.commit()
    
    def get_system_state(self, component: str) -> Optional[SystemState]:
        """Get system state."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM system_state WHERE component = ?", (component,)
            ).fetchone()
            
            if row:
                config_data = json.loads(row['config_data']) if row['config_data'] else None
                return SystemState(
                    component=row['component'],
                    is_configured=bool(row['is_configured']),
                    is_running=bool(row['is_running']),
                    config_data=config_data,
                    last_status=row['last_status'],
                    updated_at=row['updated_at']
                )
            return None
    
    # Printer Config Methods
    def save_printer_config(self, config: PrinterConfig):
        """Save printer configuration."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO printer_configs 
                (name, connection_type, device_uri, is_default, is_configured, 
                 last_tested, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                config.name, config.connection_type, config.device_uri,
                config.is_default, config.is_configured, config.last_tested,
                datetime.now()
            ))
            conn.commit()
    
    def get_default_printer(self) -> Optional[PrinterConfig]:
        """Get default printer configuration."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM printer_configs WHERE is_default = TRUE"
            ).fetchone()
            
            if row:
                return PrinterConfig(
                    name=row['name'],
                    connection_type=row['connection_type'],
                    device_uri=row['device_uri'],
                    is_default=bool(row['is_default']),
                    is_configured=bool(row['is_configured']),
                    last_tested=row['last_tested'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
            return None