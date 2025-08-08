#!/usr/bin/env python3
"""
Odoo Integration Examples
Shows how to integrate the label printing API with Odoo.
"""

# ODOO PYTHON CODE EXAMPLES
# Add this to your Odoo module

ODOO_PYTHON_CODE = '''
# In your Odoo model (e.g., stock.picking or custom model)
import requests
import json
from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    # Your printer API endpoint URL (ngrok or fixed IP)
    PRINTER_API_URL = "https://your-ngrok-url.ngrok.io"  # Replace with your actual URL
    
    def print_qr_labels(self):
        """
        Print QR labels for this picking.
        No PDF generation needed - send JSON directly!
        """
        try:
            # Prepare label data from Odoo
            labels_data = []
            
            for move_line in self.move_line_ids:
                label = {
                    "title": f"W-CPN/OUT/{self.name}",
                    "date": fields.Date.today().strftime("%d/%m/%y"),
                    "qr_code": move_line.lot_id.name or f"LOT{move_line.id:08d}"
                }
                labels_data.append(label)
            
            if not labels_data:
                raise UserError("No items to print labels for")
            
            # Send to local printer API
            payload = {"labels": labels_data}
            
            _logger.info(f"Sending {len(labels_data)} labels to printer API")
            
            response = requests.post(
                f"{self.PRINTER_API_URL}/print",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.ok:
                result = response.json()
                message = f"Successfully printed {result.get('labels_count', 0)} labels"
                _logger.info(message)
                
                # Show success message in Odoo
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': message,
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                error_msg = f"Printing failed: {response.text}"
                _logger.error(error_msg)
                raise UserError(error_msg)
                
        except requests.exceptions.Timeout:
            raise UserError("Printer connection timeout. Check if printer service is running.")
        except requests.exceptions.ConnectionError:
            raise UserError("Cannot connect to printer. Check network connectivity.")
        except Exception as e:
            _logger.error(f"Print error: {str(e)}")
            raise UserError(f"Printing error: {str(e)}")

# ALTERNATIVE: Scheduled action for batch printing
class PrintQueueJob(models.Model):
    _name = 'print.queue.job'
    _description = 'Print Queue Job'
    
    name = fields.Char(string='Job Name', required=True)
    labels_data = fields.Text(string='Labels JSON Data', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('queued', 'Queued'),
        ('printed', 'Printed'),
        ('failed', 'Failed')
    ], default='draft')
    error_message = fields.Text(string='Error Message')
    
    @api.model
    def process_print_queue(self):
        """
        Scheduled action to process print queue.
        Run this every 1-2 minutes via Odoo cron.
        """
        PRINTER_API_URL = "https://your-ngrok-url.ngrok.io"
        
        jobs = self.search([('state', '=', 'queued')], limit=10)
        
        for job in jobs:
            try:
                labels_data = json.loads(job.labels_data)
                
                response = requests.post(
                    f"{PRINTER_API_URL}/print",
                    json=labels_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.ok:
                    job.write({'state': 'printed'})
                    _logger.info(f"Print job {job.name} completed successfully")
                else:
                    job.write({
                        'state': 'failed',
                        'error_message': response.text
                    })
                    _logger.error(f"Print job {job.name} failed: {response.text}")
                    
            except Exception as e:
                job.write({
                    'state': 'failed',
                    'error_message': str(e)
                })
                _logger.error(f"Print job {job.name} error: {str(e)}")

# XML Views for Odoo
'''

# ODOO XML VIEW
ODOO_XML_VIEW = '''
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Add button to stock picking form -->
    <record id="view_picking_form_print_labels" model="ir.ui.view">
        <field name="name">stock.picking.form.print.labels</field>
        <field name="model">stock.picking</field>
        <field name="inherit_id" ref="stock.view_picking_form"/>
        <field name="arch" type="xml">
            <header>
                <button name="print_qr_labels" 
                        string="Print QR Labels" 
                        type="object" 
                        class="btn-primary"
                        attrs="{'invisible': [('state', 'not in', ['assigned', 'done'])]}"/>
            </header>
        </field>
    </record>
    
    <!-- Scheduled action for print queue processing -->
    <record id="ir_cron_process_print_queue" model="ir.cron">
        <field name="name">Process Print Queue</field>
        <field name="model_id" ref="model_print_queue_job"/>
        <field name="state">code</field>
        <field name="code">model.process_print_queue()</field>
        <field name="interval_number">2</field>
        <field name="interval_type">minutes</field>
        <field name="numbercall">-1</field>
        <field name="active">True</field>
    </record>
</odoo>
'''

def create_odoo_files():
    """Create Odoo integration files."""
    print("📁 Creating Odoo integration files...")
    
    # Python model file
    with open('odoo_models.py', 'w') as f:
        f.write(ODOO_PYTHON_CODE)
    
    # XML view file
    with open('odoo_views.xml', 'w') as f:
        f.write(ODOO_XML_VIEW)
    
    print("✅ Created odoo_models.py - Add this code to your Odoo module")
    print("✅ Created odoo_views.xml - Add this XML to your Odoo module")
    
    return True

def test_api_locally():
    """Test the API with sample data."""
    import requests
    
    print("🧪 Testing API locally...")
    
    # Test data (same format Odoo will send)
    test_data = {
        "labels": [
            {
                "title": "W-CPN/OUT/00002",
                "date": "12/04/22",
                "qr_code": "01010101160"
            },
            {
                "title": "W-CPN/OUT/00002", 
                "date": "12/04/22",
                "qr_code": "01030402140"
            }
        ]
    }
    
    try:
        # Test health check
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.ok:
            print("✅ API server is healthy")
        else:
            print("❌ API server health check failed")
            return False
        
        # Test print endpoint
        response = requests.post(
            "http://localhost:5000/print",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.ok:
            result = response.json()
            print("✅ Print test successful!")
            print(f"📋 Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Print test failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Make sure it's running:")
        print("   python label_print_api.py")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main integration helper."""
    print("🏷️  Odoo Integration Helper")
    print("=" * 40)
    
    print("1. 📁 Generate Odoo code files")
    print("2. 🧪 Test API locally")
    print("3. 📋 Show integration steps")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == '1':
        create_odoo_files()
        
    elif choice == '2':
        test_api_locally()
        
    elif choice == '3':
        print("\n📋 Integration Steps:")
        print("=" * 40)
        print("1. Start local API server: python label_print_api.py")
        print("2. Setup connectivity (ngrok/VPN): python setup_connectivity.py") 
        print("3. Add Odoo code from odoo_models.py to your module")
        print("4. Add XML views from odoo_views.xml to your module")
        print("5. Update PRINTER_API_URL in Odoo code")
        print("6. Test printing from Odoo interface")
        
        print("\n🔗 API Endpoints:")
        print("   POST /print - Print labels")
        print("   GET /health - Health check") 
        print("   GET /printer/status - Printer status")
        
        print("\n📝 JSON Format:")
        print('   {"labels": [{"title": "W-CPN/OUT/001", "date": "01/01/25", "qr_code": "123456"}]}')
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()