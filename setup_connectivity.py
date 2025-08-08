#!/usr/bin/env python3
"""
Cloud-to-Local Connectivity Setup
Provides different solutions for connecting Odoo (cloud) to local printer.
"""

import subprocess
import os
import json
from pathlib import Path

def setup_ngrok_tunnel():
    """
    Setup 1: Ngrok Tunnel (Recommended for development/testing)
    Exposes local API server to the internet via secure tunnel.
    """
    print("🌐 Setting up Ngrok tunnel for cloud-to-local connectivity")
    print("=" * 60)
    
    # Check if ngrok is installed
    try:
        result = subprocess.run(['which', 'ngrok'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Ngrok not found. Installing...")
            print("📥 Please install ngrok:")
            print("   1. Download from: https://ngrok.com/download")
            print("   2. Or install via snap: sudo snap install ngrok")
            print("   3. Sign up for free account and get auth token")
            return False
        
        print("✅ Ngrok found")
        
        # Create ngrok config
        ngrok_config = {
            "version": "2",
            "tunnels": {
                "label-printer": {
                    "addr": "5000",
                    "proto": "http",
                    "bind_tls": True,
                    "inspect": False
                }
            }
        }
        
        config_path = Path.home() / ".ngrok2" / "ngrok.yml"
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            import yaml
            yaml.dump(ngrok_config, f)
        
        print("✅ Ngrok configuration created")
        print(f"📄 Config saved to: {config_path}")
        
        # Start instructions
        print("\n🚀 To start the tunnel:")
        print("   1. Start the API server: python label_print_api.py")
        print("   2. In another terminal: ngrok start label-printer")
        print("   3. Copy the HTTPS URL and use it in Odoo webhook")
        
        return True
        
    except ImportError:
        print("❌ PyYAML not installed. Install with: pip install pyyaml")
        return False
    except Exception as e:
        print(f"❌ Error setting up ngrok: {e}")
        return False

def create_systemd_service():
    """
    Setup 2: Systemd Service (For production)
    Creates a system service that starts automatically.
    """
    print("\n🔧 Creating systemd service for production deployment")
    print("=" * 60)
    
    current_dir = os.path.abspath(os.path.dirname(__file__))
    python_path = subprocess.run(['which', 'python3'], capture_output=True, text=True).stdout.strip()
    
    service_content = f"""[Unit]
Description=Label Printing API Server
After=network.target

[Service]
Type=simple
User={os.getlogin()}
WorkingDirectory={current_dir}
ExecStart={python_path} {current_dir}/label_print_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = "/tmp/label-printer.service"
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    print(f"✅ Service file created: {service_file}")
    print("\n📋 To install the service:")
    print(f"   sudo mv {service_file} /etc/systemd/system/")
    print("   sudo systemctl daemon-reload")
    print("   sudo systemctl enable label-printer")
    print("   sudo systemctl start label-printer")
    print("   sudo systemctl status label-printer")
    
    return True

def setup_polling_queue():
    """
    Setup 3: Polling/Queue System (Most secure)
    Local app polls a shared database/queue for print jobs.
    """
    print("\n🔄 Setting up polling/queue system")
    print("=" * 60)
    
    # Create a simple SQLite-based queue system
    queue_script = """#!/usr/bin/env python3
import sqlite3
import time
import json
import requests
from datetime import datetime

# Database setup
def init_db():
    conn = sqlite3.connect('print_queue.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS print_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_data TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Queue processor
def process_queue():
    while True:
        try:
            conn = sqlite3.connect('print_queue.db')
            cursor = conn.cursor()
            
            # Get pending jobs
            cursor.execute("SELECT id, job_data FROM print_jobs WHERE status = 'pending' ORDER BY created_at LIMIT 1")
            job = cursor.fetchone()
            
            if job:
                job_id, job_data = job
                print(f"Processing job {job_id}")
                
                # Send to local API
                response = requests.post('http://localhost:5000/print', 
                                       json=json.loads(job_data),
                                       timeout=30)
                
                if response.ok:
                    cursor.execute("UPDATE print_jobs SET status = 'completed', processed_at = ? WHERE id = ?", 
                                 (datetime.now(), job_id))
                    print(f"Job {job_id} completed successfully")
                else:
                    cursor.execute("UPDATE print_jobs SET status = 'failed' WHERE id = ?", (job_id,))
                    print(f"Job {job_id} failed: {response.text}")
            
            conn.commit()
            conn.close()
            time.sleep(5)  # Poll every 5 seconds
            
        except Exception as e:
            print(f"Queue processing error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    init_db()
    print("Starting queue processor...")
    process_queue()
"""
    
    with open('queue_processor.py', 'w') as f:
        f.write(queue_script)
    
    print("✅ Queue processor created: queue_processor.py")
    print("📋 Setup instructions:")
    print("   1. Install requests: pip install requests")
    print("   2. Run queue processor: python queue_processor.py")
    print("   3. Odoo writes to print_queue.db instead of direct API calls")
    
    return True

def main():
    """Main setup menu."""
    print("🏷️  Label Printing API - Connectivity Setup")
    print("=" * 50)
    print("Choose your connectivity solution:\n")
    
    print("1. 🌐 Ngrok Tunnel (Development/Testing)")
    print("   - Quick setup")
    print("   - Secure HTTPS tunnel")
    print("   - Good for development and small scale\n")
    
    print("2. 🔧 Systemd Service (Production)")
    print("   - Runs as system service")
    print("   - Auto-starts on boot")
    print("   - Requires port forwarding/VPN\n")
    
    print("3. 🔄 Polling/Queue System (Most Secure)")
    print("   - No exposed ports")
    print("   - Uses shared database")
    print("   - Most secure option\n")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == '1':
        setup_ngrok_tunnel()
    elif choice == '2':
        create_systemd_service()
    elif choice == '3':
        setup_polling_queue()
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()