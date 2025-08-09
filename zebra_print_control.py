#!/usr/bin/env python3
"""
Zebra Label Printing Control Panel
Complete solution for Odoo to local Zebra printer integration.
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime
from pathlib import Path

class ZebraLabelControl:
    """Main control class for Zebra label printing system."""
    
    def __init__(self):
        self.api_port = 5000
        self.printer_name = "ZTC-ZD230-203dpi-ZPL"
        
    # =================== UTILITY METHODS ===================
    
    def clear_screen(self):
        """Clear terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def run_command(self, command, timeout=30):
        """Run shell command safely."""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, 
                                  text=True, timeout=timeout)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    # =================== STATUS CHECKS ===================
    
    def check_api_server(self):
        """Check if API server is running."""
        try:
            response = requests.get(f"http://localhost:{self.api_port}/health", timeout=2)
            return response.ok
        except:
            return False
    
    def check_printer(self):
        """Check printer status."""
        success, stdout, _ = self.run_command(f'lpstat -p {self.printer_name}', timeout=5)
        return success and 'idle' in stdout.lower()
    
    def get_tunnel_info(self):
        """Get active tunnel information."""
        # Check Cloudflare tunnel
        if os.path.exists('.cloudflare_tunnel'):
            try:
                with open('.cloudflare_tunnel', 'r') as f:
                    tunnel_data = json.load(f)
                tunnel_url = tunnel_data.get('tunnel_url')
                
                if tunnel_url:
                    # Test if tunnel is active
                    response = requests.get(f"{tunnel_url}/health", timeout=5)
                    if response.ok:
                        return {'type': 'cloudflare', 'url': tunnel_url, 'permanent': True}
            except:
                pass
        
        # Check ngrok tunnel
        if os.path.exists('.ngrok_url'):
            try:
                with open('.ngrok_url', 'r') as f:
                    tunnel_url = f.read().strip()
                
                if tunnel_url:
                    # Test if tunnel is active
                    response = requests.get(f"{tunnel_url}/health", 
                                          timeout=5,
                                          headers={'ngrok-skip-browser-warning': 'true'})
                    if response.ok:
                        return {'type': 'ngrok', 'url': tunnel_url, 'permanent': False}
            except:
                pass
        
        return None
    
    # =================== API SERVER MANAGEMENT ===================
    
    def start_api_server(self):
        """Start API server in background."""
        if self.check_api_server():
            return True, "API server is already running"
        
        try:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            api_script = os.path.join(script_dir, 'label_print_api.py')
            
            # Check if the API script exists
            if not os.path.exists(api_script):
                return False, f"API script not found: {api_script}"
            
            # Cross-platform process creation
            import platform
            if platform.system() == "Windows":
                # Windows doesn't support start_new_session the same way
                process = subprocess.Popen(
                    [sys.executable, api_script],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                # Unix/Linux
                process = subprocess.Popen(
                    [sys.executable, api_script],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            
            # Save PID for management
            pid_file = os.path.join(script_dir, '.server.pid')
            with open(pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait and verify
            time.sleep(2)
            if self.check_api_server():
                return True, f"API server started (PID: {process.pid})"
            else:
                return False, "API server failed to start"
        except Exception as e:
            return False, f"Error starting API server: {e}"
    
    def stop_api_server(self):
        """Stop API server."""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            pid_file = os.path.join(script_dir, '.server.pid')
            
            # Try to stop using PID file first
            if os.path.exists(pid_file):
                try:
                    with open(pid_file, 'r') as f:
                        pid = int(f.read().strip())
                    
                    import platform
                    if platform.system() == "Windows":
                        # Windows process termination
                        try:
                            import psutil
                            process = psutil.Process(pid)
                            process.terminate()
                            time.sleep(1)
                            if process.is_running():
                                process.kill()
                        except ImportError:
                            # Fallback if psutil not available
                            subprocess.run(['taskkill', '/pid', str(pid), '/f'], check=False)
                        except Exception:
                            # Final fallback
                            subprocess.run(['taskkill', '/pid', str(pid), '/f'], check=False)
                    else:
                        # Unix/Linux process termination
                        try:
                            os.kill(pid, 15)  # SIGTERM
                            time.sleep(1)
                            os.kill(pid, 9)   # SIGKILL
                        except ProcessLookupError:
                            pass  # Process already dead
                        except Exception:
                            # Fallback to pkill
                            success, _, _ = self.run_command('pkill -f label_print_api.py', timeout=5)
                    
                    # Remove PID file
                    os.remove(pid_file)
                    
                except Exception:
                    pass
            
            # Fallback: try system-specific process killing
            import platform
            if platform.system() == "Windows":
                # Use tasklist and taskkill
                self.run_command('taskkill /f /im python.exe /fi "WINDOWTITLE eq *label_print_api*"', timeout=5)
            else:
                # Use pkill for Unix/Linux
                self.run_command('pkill -f label_print_api.py', timeout=5)
            
            return True, "API server stopped"
        except Exception as e:
            return False, f"Error stopping API server: {e}"
    
    # =================== TUNNEL MANAGEMENT ===================
    
    def setup_cloudflare_tunnel(self):
        """Setup Cloudflare tunnel with permanent URL."""
        print("[CLOUDFLARE] Setting up Cloudflare Tunnel...")
        print("[BROWSER] A browser will open for one-time authentication")
        input("[ENTER] Press Enter when ready...")
        
        # Check if cloudflared exists
        success, _, _ = self.run_command('which cloudflared')
        if not success:
            return False, "Cloudflared not installed. Visit: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
        
        # Login to Cloudflare
        print("[AUTH] Authenticating with Cloudflare...")
        success, _, stderr = self.run_command('cloudflared tunnel login', timeout=120)
        if not success:
            return False, f"Authentication failed: {stderr}"
        
        # Create tunnel
        tunnel_name = "zebra-printer"
        print(f"[CONFIG] Creating tunnel: {tunnel_name}")
        success, stdout, stderr = self.run_command(f'cloudflared tunnel create {tunnel_name}', timeout=30)
        
        if not success:
            return False, f"Failed to create tunnel: {stderr}"
        
        # Extract tunnel ID
        tunnel_id = None
        for line in stderr.split('\n'):
            if 'Created tunnel' in line and '.json' in line:
                parts = line.split()
                for part in parts:
                    if len(part) == 36 and part.count('-') == 4:  # UUID format
                        tunnel_id = part
                        break
                break
        
        if not tunnel_id:
            return False, "Could not extract tunnel ID"
        
        # Generate permanent URL
        subdomain = f"zebra-printer-{tunnel_id[:8]}"
        tunnel_url = f"https://{subdomain}.trycloudflare.com"
        
        # Save tunnel info
        tunnel_info = {
            'tunnel_id': tunnel_id,
            'tunnel_name': tunnel_name,
            'tunnel_url': tunnel_url,
            'subdomain': subdomain
        }
        
        with open('.cloudflare_tunnel', 'w') as f:
            json.dump(tunnel_info, f, indent=2)
        
        # Create config
        config_dir = Path.home() / ".cloudflared"
        config_dir.mkdir(exist_ok=True)
        
        config_content = f"""tunnel: {tunnel_id}
credentials-file: {config_dir}/{tunnel_id}.json

ingress:
  - hostname: {subdomain}.trycloudflare.com
    service: http://localhost:{self.api_port}
  - service: http_status:404
"""
        
        with open(config_dir / "config.yml", 'w') as f:
            f.write(config_content)
        
        return True, f"Cloudflare tunnel created: {tunnel_url}"
    
    def start_tunnel(self):
        """Start the configured tunnel."""
        # Try Cloudflare first
        if os.path.exists('.cloudflare_tunnel'):
            try:
                with open('.cloudflare_tunnel', 'r') as f:
                    tunnel_data = json.load(f)
                
                tunnel_name = tunnel_data.get('tunnel_name')
                if not tunnel_name:
                    return False, "Invalid tunnel configuration"
                
                # Start tunnel in background
                process = subprocess.Popen(
                    ['cloudflared', 'tunnel', 'run', tunnel_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                # Save PID
                with open('.cloudflare_pid', 'w') as f:
                    f.write(str(process.pid))
                
                time.sleep(3)
                
                # Test tunnel
                tunnel_url = tunnel_data.get('tunnel_url')
                response = requests.get(f"{tunnel_url}/health", timeout=10)
                if response.ok:
                    return True, f"Cloudflare tunnel started: {tunnel_url}"
                else:
                    return False, "Tunnel started but not responding"
                    
            except Exception as e:
                return False, f"Error starting Cloudflare tunnel: {e}"
        
        # Fallback to ngrok
        return self.start_ngrok_tunnel()
    
    def start_ngrok_tunnel(self):
        """Start ngrok tunnel (fallback option)."""
        success, _, _ = self.run_command('which ngrok')
        if not success:
            return False, "Ngrok not installed"
        
        # Kill existing ngrok
        self.run_command('pkill -f ngrok', timeout=5)
        time.sleep(1)
        
        # Start ngrok
        subprocess.Popen(
            ['ngrok', 'http', str(self.api_port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(5)  # Wait for startup
        
        # Get tunnel URL
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.ok:
                data = response.json()
                tunnels = data.get('tunnels', [])
                
                for tunnel in tunnels:
                    public_url = tunnel.get('public_url', '')
                    if public_url.startswith('https://'):
                        # Save URL
                        with open('.ngrok_url', 'w') as f:
                            f.write(public_url)
                        
                        return True, f"Ngrok tunnel started: {public_url}"
            
            return False, "Failed to get ngrok tunnel URL"
        except Exception as e:
            return False, f"Error starting ngrok: {e}"
    
    def stop_tunnel(self):
        """Stop active tunnel."""
        try:
            # Stop both types
            self.run_command('pkill -f cloudflared', timeout=5)
            self.run_command('pkill -f ngrok', timeout=5)
            
            # Clean up files
            for file in ['.cloudflare_pid', '.ngrok_url']:
                if os.path.exists(file):
                    os.remove(file)
            
            return True, "Tunnel stopped"
        except Exception as e:
            return False, f"Error stopping tunnel: {e}"
    
    # =================== SYSTEM TESTING ===================
    
    def test_complete_system(self):
        """Test the complete system end-to-end."""
        print("[TEST] TESTING COMPLETE SYSTEM")
        print("=" * 35)
        
        # Test API Server
        print("1. [API]  Testing API server...")
        if not self.check_api_server():
            print("[ERROR] API server not running")
            return False
        print("[OK] API server OK")
        
        # Test Printer
        print("2. [PRINTER]  Testing printer...")
        if not self.check_printer():
            print("[ERROR] Printer not ready")
            return False
        print("[OK] Printer OK")
        
        # Test Tunnel
        print("3. [TUNNEL] Testing tunnel...")
        tunnel_info = self.get_tunnel_info()
        if not tunnel_info:
            print("[ERROR] Tunnel not active")
            return False
        print(f"[OK] Tunnel OK ({tunnel_info['type']})")
        
        # End-to-end test
        print("4. [LABEL]  Testing end-to-end printing...")
        test_data = {
            "labels": [{
                "title": "W-CPN/OUT/TEST",
                "date": datetime.now().strftime("%d/%m/%y"),
                "qr_code": "SYSTEM123"
            }]
        }
        
        try:
            headers = {'Content-Type': 'application/json'}
            if tunnel_info['type'] == 'ngrok':
                headers['ngrok-skip-browser-warning'] = 'true'
            
            response = requests.post(
                f"{tunnel_info['url']}/print",
                json=test_data,
                headers=headers,
                timeout=30
            )
            
            if response.ok:
                result = response.json()
                print("[OK] Print test successful!")
                print(f"   Job: {result.get('job_info', 'N/A')}")
                print("\n[LABEL]  Check your printer!")
                return True
            else:
                print(f"[ERROR] Print test failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] Print test error: {e}")
            return False
    
    def test_print_labels(self):
        """Interactive label print testing."""
        print("\n[LABEL]  LABEL PRINT TESTING")
        print("=" * 30)
        
        # Check prerequisites
        if not self.check_api_server():
            print("[ERROR] API server not running")
            choice = input("Start API server? (Y/n): ").lower()
            if choice != 'n':
                success, message = self.start_api_server()
                if not success:
                    print(f"[ERROR] {message}")
                    return
                print(f"[OK] {message}")
            else:
                return
        
        # Show test options
        print("[INFO] Test Options:")
        print("1. [START] Quick Test (Sample Data)")
        print("2. [EDIT]  Custom Test (Your Data)")
        print("3. [TUNNEL] Test via Tunnel")
        print("0. [BACK]  Back")
        
        choice = input("\nChoose test type (0-3): ").strip()
        
        if choice == '1':
            self._quick_print_test()
        elif choice == '2':
            self._custom_print_test()
        elif choice == '3':
            self._tunnel_print_test()
        elif choice != '0':
            print("[ERROR] Invalid choice")
    
    def _quick_print_test(self):
        """Quick print test with sample data."""
        print("\n[START] QUICK PRINT TEST")
        print("-" * 20)
        
        test_data = {
            "labels": [{
                "title": "W-CPN/OUT/QUICKTEST",
                "date": datetime.now().strftime("%d/%m/%y"),
                "qr_code": "QUICK123"
            }]
        }
        
        print("[DOCUMENT] Sample label data:")
        print(f"   Title: {test_data['labels'][0]['title']}")
        print(f"   Date: {test_data['labels'][0]['date']}")
        print(f"   QR Code: {test_data['labels'][0]['qr_code']}")
        
        confirm = input("\n[PRINTER]  Print this test label? (Y/n): ").lower()
        if confirm != 'n':
            self._send_print_request(f"http://localhost:{self.api_port}/print", test_data)
    
    def _custom_print_test(self):
        """Custom print test with user input."""
        print("\n[EDIT]  CUSTOM PRINT TEST")
        print("-" * 20)
        
        print("Enter label information:")
        title = input("[INPUT] Title (default: W-CPN/OUT/CUSTOM): ").strip()
        if not title:
            title = "W-CPN/OUT/CUSTOM"
        
        date = input("[DATE] Date (default: today): ").strip()
        if not date:
            date = datetime.now().strftime("%d/%m/%y")
        
        qr_code = input("[QR] QR Code (default: CUSTOM123): ").strip()
        if not qr_code:
            qr_code = "CUSTOM123"
        
        test_data = {
            "labels": [{
                "title": title,
                "date": date,
                "qr_code": qr_code
            }]
        }
        
        print(f"\n[DOCUMENT] Your label:")
        print(f"   Title: {title}")
        print(f"   Date: {date}")
        print(f"   QR Code: {qr_code}")
        
        confirm = input("\n[PRINTER]  Print this label? (Y/n): ").lower()
        if confirm != 'n':
            self._send_print_request(f"http://localhost:{self.api_port}/print", test_data)
    
    def _tunnel_print_test(self):
        """Test printing via tunnel (as Odoo would)."""
        print("\n[TUNNEL] TUNNEL PRINT TEST")
        print("-" * 20)
        
        tunnel_info = self.get_tunnel_info()
        if not tunnel_info:
            print("[ERROR] No active tunnel found")
            choice = input("Set up tunnel first? (Y/n): ").lower()
            if choice != 'n':
                self.manage_tunnel()
            return
        
        print(f"[TUNNEL] Testing via: {tunnel_info['url']}")
        
        test_data = {
            "labels": [{
                "title": "W-CPN/OUT/TUNNEL",
                "date": datetime.now().strftime("%d/%m/%y"),
                "qr_code": "TUNNEL123"
            }]
        }
        
        print("[DOCUMENT] Test data:")
        print(f"   Title: {test_data['labels'][0]['title']}")
        print(f"   Date: {test_data['labels'][0]['date']}")
        print(f"   QR Code: {test_data['labels'][0]['qr_code']}")
        
        confirm = input(f"\n[PRINTER]  Print via {tunnel_info['type']} tunnel? (Y/n): ").lower()
        if confirm != 'n':
            headers = {'Content-Type': 'application/json'}
            if tunnel_info['type'] == 'ngrok':
                headers['ngrok-skip-browser-warning'] = 'true'
            
            self._send_print_request(f"{tunnel_info['url']}/print", test_data, headers)
    
    def _send_print_request(self, url, data, headers=None):
        """Send print request and show results."""
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        try:
            print(f"[SEND] Sending request to: {url}")
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.ok:
                result = response.json()
                print("[OK] Print request successful!")
                print(f"   [STATUS] Labels sent: {result.get('labels_count', 0)}")
                print(f"   [ID] Job ID: {result.get('job_info', 'N/A')}")
                print(f"   [TIME] Timestamp: {result.get('timestamp', 'N/A')}")
                print("\n[LABEL]  Check your printer - label should be printing!")
            else:
                print(f"[ERROR] Print request failed!")
                print(f"   HTTP Status: {response.status_code}")
                print(f"   Error: {response.text}")
        except requests.exceptions.Timeout:
            print("[ERROR] Request timed out - check printer connection")
        except Exception as e:
            print(f"[ERROR] Request error: {e}")
    
    # =================== USER INTERFACE ===================
    
    def print_header(self):
        """Print application header."""
        print("[LABEL]  " + "=" * 50)
        print("    ZEBRA LABEL PRINTING CONTROL PANEL")
        print("    Odoo -> Permanent URL -> Local Printer")
        print("=" * 54)
    
    def print_status(self):
        """Print current system status."""
        print("\n[STATUS] SYSTEM STATUS:")
        print("-" * 20)
        
        # API Server
        api_running = self.check_api_server()
        print(f"[API]  API Server:  {'[OK] RUNNING' if api_running else '[ERROR] STOPPED'}")
        if api_running:
            print(f"    Local URL: http://localhost:{self.api_port}")
        
        # Printer
        printer_ready = self.check_printer()
        print(f"[PRINTER]  Printer:    {'[OK] READY' if printer_ready else '[ERROR] NOT READY'}")
        
        # Tunnel
        tunnel_info = self.get_tunnel_info()
        if tunnel_info:
            status = "PERMANENT" if tunnel_info['permanent'] else "TEMPORARY"
            print(f"[TUNNEL] Tunnel:     [OK] ACTIVE ({tunnel_info['type'].upper()}) - {status}")
            print(f"    Public URL: {tunnel_info['url']}")
        else:
            print("[TUNNEL] Tunnel:     [ERROR] INACTIVE")
        
        # Overall Status
        if api_running and printer_ready and tunnel_info:
            print(f"\n[TARGET] ODOO INTEGRATION: [OK] READY")
            if tunnel_info:
                print(f"    Webhook URL: {tunnel_info['url']}/print")
        else:
            print(f"\n[TARGET] ODOO INTEGRATION: [ERROR] NOT READY")
    
    def quick_start(self):
        """Quick start wizard for new users."""
        print("\n[START] QUICK START WIZARD")
        print("=" * 25)
        
        # Step 1: API Server
        print("Step 1: Starting API server...")
        success, message = self.start_api_server()
        if not success:
            print(f"[ERROR] {message}")
            return
        print(f"[OK] {message}")
        
        # Step 2: Tunnel Setup
        print("\nStep 2: Setting up tunnel...")
        tunnel_info = self.get_tunnel_info()
        
        if not tunnel_info:
            print("[TUNNEL] Choose tunnel type:")
            print("1. [CLOUDFLARE] Cloudflare (PERMANENT URL - Recommended)")
            print("2. [NGROK] Ngrok (Temporary URL)")
            
            choice = input("Choose (1-2): ").strip()
            
            if choice == '1':
                success, message = self.setup_cloudflare_tunnel()
                if not success:
                    print(f"[ERROR] {message}")
                    return
                print(f"[OK] {message}")
            
            # Start tunnel
            success, message = self.start_tunnel()
            if not success:
                print(f"[ERROR] {message}")
                return
            print(f"[OK] {message}")
        else:
            print(f"[OK] Using existing {tunnel_info['type']} tunnel")
            # Ensure it's running
            success, message = self.start_tunnel()
            if success:
                print(f"[OK] {message}")
        
        # Step 3: Test
        print("\nStep 3: Testing system...")
        if self.test_complete_system():
            print("\n[SUCCESS] QUICK START COMPLETE!")
            print("Your system is ready for Odoo integration!")
        else:
            print("\n[ERROR] System test failed")
    
    def show_odoo_config(self):
        """Show Odoo configuration."""
        tunnel_info = self.get_tunnel_info()
        if not tunnel_info:
            print("[ERROR] No active tunnel. Set up tunnel first.")
            return
        
        print("\n[INFO] ODOO WEBHOOK CONFIGURATION")
        print("=" * 35)
        print(f"[TUNNEL] Webhook URL: {tunnel_info['url']}/print")
        print("[POST] Method: POST")
        print("[DOCUMENT] Content-Type: application/json")
        print()
        print("[INPUT] JSON Format:")
        print('{\n  "labels": [{\n    "title": "W-CPN/OUT/00001",')
        print('    "date": "08/08/25",\n    "qr_code": "01010101160"\n  }]\n}')
        
        if tunnel_info['permanent']:
            print("\n[OK] This URL is PERMANENT - configure once!")
        else:
            print("\n[WARNING]  This URL changes on restart - update Odoo each time")
    
    def main_menu(self):
        """Display main menu and handle user input."""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_status()
            
            print("\n[TARGET] ACTIONS:")
            print("1. [START] Quick Start (New Users)")
            print("2. [API]  Start/Stop API Server")
            print("3. [TUNNEL] Setup/Manage Tunnel")
            print("4. [TEST] Test Complete System")
            print("5. [LABEL]  Test Print Labels")
            print("6. [INFO] Show Odoo Configuration")
            print("0. [ERROR] Exit")
            
            choice = input(f"\n>> Choose (0-6): ").strip()
            
            if choice == '0':
                print("\n[BYE] Goodbye!")
                break
            elif choice == '1':
                self.quick_start()
            elif choice == '2':
                self.manage_api_server()
            elif choice == '3':
                self.manage_tunnel()
            elif choice == '4':
                self.test_complete_system()
            elif choice == '5':
                self.test_print_labels()
            elif choice == '6':
                self.show_odoo_config()
            else:
                print("[ERROR] Invalid choice")
            
            if choice != '0':
                input("\n[ENTER] Press Enter to continue...")
    
    def manage_api_server(self):
        """Manage API server."""
        print("\n[API]  API SERVER MANAGEMENT")
        if self.check_api_server():
            print("Status: [OK] RUNNING")
            action = input("Stop server? (y/N): ").lower()
            if action == 'y':
                success, message = self.stop_api_server()
                print(f"{'[OK]' if success else '[ERROR]'} {message}")
        else:
            print("Status: [ERROR] STOPPED")
            action = input("Start server? (Y/n): ").lower()
            if action != 'n':
                success, message = self.start_api_server()
                print(f"{'[OK]' if success else '[ERROR]'} {message}")
    
    def manage_tunnel(self):
        """Manage tunnel."""
        print("\n[TUNNEL] TUNNEL MANAGEMENT")
        tunnel_info = self.get_tunnel_info()
        
        if tunnel_info:
            print(f"Status: [OK] ACTIVE ({tunnel_info['type']})")
            print(f"URL: {tunnel_info['url']}")
            action = input("Stop tunnel? (y/N): ").lower()
            if action == 'y':
                success, message = self.stop_tunnel()
                print(f"{'[OK]' if success else '[ERROR]'} {message}")
        else:
            print("Status: [ERROR] INACTIVE")
            print("1. [CLOUDFLARE] Setup Cloudflare (Permanent)")
            print("2. [NGROK] Start Ngrok (Temporary)")
            choice = input("Choose (1-2): ").strip()
            
            if choice == '1':
                success, message = self.setup_cloudflare_tunnel()
                print(f"{'[OK]' if success else '[ERROR]'} {message}")
                if success:
                    success, message = self.start_tunnel()
                    print(f"{'[OK]' if success else '[ERROR]'} {message}")
            elif choice == '2':
                success, message = self.start_ngrok_tunnel()
                print(f"{'[OK]' if success else '[ERROR]'} {message}")

def main():
    """Main application entry point."""
    control = ZebraLabelControl()
    control.main_menu()

if __name__ == "__main__":
    main()