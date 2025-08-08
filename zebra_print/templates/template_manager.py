"""
Label template management system.
Handles ZPL template storage, retrieval, and rendering with dynamic data.
"""

import sqlite3
import os
import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class TemplateManager:
    """Manages label templates for flexible printing."""
    
    def __init__(self, db_path: str = "/app/data/zebra_print.db"):
        self.db_path = db_path
        self._ensure_tables()
        self._ensure_default_template()
    
    def _get_connection(self):
        """Get database connection."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        return sqlite3.connect(self.db_path)
    
    def _ensure_tables(self):
        """Ensure template tables exist in database."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS label_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    zpl_template TEXT NOT NULL,
                    required_fields TEXT NOT NULL,
                    label_size TEXT DEFAULT '30x50mm',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def _ensure_default_template(self):
        """Ensure default template exists."""
        templates = self.get_all_templates()
        if not any(t['name'] == 'standard' for t in templates):
            self.create_template(
                name="standard",
                description="Standard QR code label with title, date, and QR code",
                zpl_template=self._get_standard_zpl_template(),
                required_fields=["title", "date", "qr_code"],
                label_size="30x50mm"
            )
    
    def _get_standard_zpl_template(self) -> str:
        """Get the standard ZPL template based on current implementation."""
        return """^XA
^JUS
^MMT
^MNY
^MTT
^PON
^PMN
^LRN
^CI0
^XZ

^XA
^LL236
^PW394
^LH0,0
^LT0
^PR2
^MD5
^JMA
^FO30,30^BQN,2,5^FDLA,{{qr_code}}^FS
^FO145,35^A0N,16,16^FD{{title}}^FS
^FO145,60^A0N,16,16^FD{{date}}^FS
^FO145,85^A0N,16,16^FD{{qr_code}}^FS
^XZ"""
    
    def create_template(self, name: str, description: str, zpl_template: str, 
                       required_fields: List[str], label_size: str = "30x50mm") -> bool:
        """Create a new label template."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO label_templates 
                    (name, description, zpl_template, required_fields, label_size)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, description, zpl_template, json.dumps(required_fields), label_size))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False  # Template name already exists
        except Exception:
            return False
    
    def get_template(self, name: str) -> Optional[Dict]:
        """Get a specific template by name."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT name, description, zpl_template, required_fields, label_size, is_active
                FROM label_templates WHERE name = ? AND is_active = 1
            """, (name,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'name': row[0],
                    'description': row[1],
                    'zpl_template': row[2],
                    'required_fields': json.loads(row[3]),
                    'label_size': row[4],
                    'is_active': bool(row[5])
                }
            return None
    
    def get_all_templates(self) -> List[Dict]:
        """Get all active templates."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT name, description, zpl_template, required_fields, label_size, 
                       created_at, updated_at, is_active
                FROM label_templates WHERE is_active = 1 ORDER BY name
            """)
            
            templates = []
            for row in cursor.fetchall():
                templates.append({
                    'name': row[0],
                    'description': row[1],
                    'zpl_template': row[2],
                    'required_fields': json.loads(row[3]),
                    'label_size': row[4],
                    'created_at': row[5],
                    'updated_at': row[6],
                    'is_active': bool(row[7])
                })
            
            return templates
    
    def render_template(self, template_name: str, data: Dict) -> Tuple[bool, str]:
        """Render template with provided data."""
        template = self.get_template(template_name)
        if not template:
            return False, f"Template '{template_name}' not found"
        
        # Check required fields
        missing_fields = []
        for field in template['required_fields']:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Missing required fields: {missing_fields}"
        
        # Render ZPL template
        zpl = template['zpl_template']
        for field, value in data.items():
            placeholder = f"{{{{{field}}}}}"
            zpl = zpl.replace(placeholder, str(value))
        
        return True, zpl
    
    def render_multiple_labels(self, template_name: str, label_data_list: List[Dict]) -> Tuple[bool, str]:
        """Render template for multiple labels."""
        template = self.get_template(template_name)
        if not template:
            return False, f"Template '{template_name}' not found"
        
        zpl_commands = []
        
        # Add printer initialization once
        init_commands = [
            "^XA", "^JUS", "^MMT", "^MNY", "^MTT", "^PON", "^PMN", "^LRN", "^CI0", "^XZ", ""
        ]
        zpl_commands.extend(init_commands)
        
        # Render each label
        for i, data in enumerate(label_data_list):
            success, rendered_zpl = self.render_template(template_name, data)
            if not success:
                return False, rendered_zpl
            
            # Skip the initialization part of individual templates
            label_zpl = rendered_zpl.split("^XZ\n\n^XA", 1)[-1] if "^XZ\n\n^XA" in rendered_zpl else rendered_zpl
            zpl_commands.append("^XA")
            zpl_commands.extend(label_zpl.split('\n')[1:])  # Skip first ^XA
            
            # Add spacing between labels
            if i < len(label_data_list) - 1:
                zpl_commands.append("")
        
        return True, "\n".join(zpl_commands)
    
    def update_template(self, name: str, description: str = None, zpl_template: str = None,
                       required_fields: List[str] = None, label_size: str = None) -> bool:
        """Update an existing template."""
        try:
            with self._get_connection() as conn:
                updates = []
                params = []
                
                if description is not None:
                    updates.append("description = ?")
                    params.append(description)
                
                if zpl_template is not None:
                    updates.append("zpl_template = ?")
                    params.append(zpl_template)
                
                if required_fields is not None:
                    updates.append("required_fields = ?")
                    params.append(json.dumps(required_fields))
                
                if label_size is not None:
                    updates.append("label_size = ?")
                    params.append(label_size)
                
                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(name)
                    
                    query = f"UPDATE label_templates SET {', '.join(updates)} WHERE name = ?"
                    cursor = conn.execute(query, params)
                    conn.commit()
                    return cursor.rowcount > 0
                
                return False
        except Exception:
            return False
    
    def delete_template(self, name: str) -> bool:
        """Delete a template (mark as inactive)."""
        if name == "standard":
            return False  # Don't allow deleting standard template
        
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    UPDATE label_templates SET is_active = 0 
                    WHERE name = ?
                """, (name,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
    
    def validate_template_fields(self, template_name: str, data: Dict) -> Tuple[bool, List[str]]:
        """Validate that data contains all required fields for template."""
        template = self.get_template(template_name)
        if not template:
            return False, [f"Template '{template_name}' not found"]
        
        missing_fields = []
        for field in template['required_fields']:
            if field not in data:
                missing_fields.append(field)
        
        return len(missing_fields) == 0, missing_fields