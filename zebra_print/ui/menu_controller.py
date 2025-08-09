"""
Menu controller for the CLI interface.
Handles user interaction and menu navigation.
"""

import os
import sys
import time
from typing import Dict, List, Optional, Tuple
from zebra_print.core.system_status import SystemStatus
from zebra_print.core.label_service import LabelService

class MenuController:
    """Controls the CLI menu system and user interactions."""
    
    def __init__(self, system_status: SystemStatus, label_service: LabelService):
        self.system_status = system_status
        self.label_service = label_service
        self.running = True
    
    def display_banner(self):
        """Display application banner."""
        print("\n" + "="*60)
        print("         ZEBRA PRINT CONTROL SYSTEM")
        print("         Advanced Label Printing Solution")
        print("="*60)
    
    def display_main_menu(self):
        """Display the main menu options."""
        print("\n[INFO] MAIN MENU:")
        print("1. [STATUS] System Status")
        print("2. [START] Start API Server")
        print("3. [STOP] Stop API Server")
        print("4. [TUNNEL] Setup Tunnel")
        print("5. [URL] Start Tunnel")
        print("6. [STOP]  Stop Tunnel")
        print("7. [PRINTER]️  Printer Management")
        print("8. [TEST] Test Functions")
        print("9. [SEND] Integration Test")
        print("A. [AUTH] API Security")
        print("0. [EXIT] Exit")
        print("-" * 40)
    
    def display_system_status(self):
        """Display comprehensive system status."""
        print("\n[STATUS] SYSTEM STATUS:")
        print("=" * 50)
        
        try:
            status = self.system_status.get_overall_status()
            
            # API Status
            api_status = status['api']
            api_icon = "[ONLINE]" if api_status['running'] else "[OFFLINE]"
            print(f"\n{api_icon} API Server:")
            print(f"   Status: {'Running' if api_status['running'] else 'Stopped'}")
            if api_status['details']:
                details = api_status['details']
                print(f"   URL: {details.get('url', 'N/A')}")
                if 'pid' in details:
                    print(f"   PID: {details['pid']}")
            
            # Printer Status
            printer_status = status['printer']
            printer_icon = "[ONLINE]" if printer_status['ready'] else "[OFFLINE]"
            print(f"\n{printer_icon} Printer:")
            print(f"   Ready: {'Yes' if printer_status['ready'] else 'No'}")
            if printer_status['details']:
                details = printer_status['details']
                print(f"   Name: {details.get('name', 'N/A')}")
                print(f"   State: {details.get('state', 'Unknown')}")
                print(f"   Connection: {details.get('connection', 'Unknown')}")
                print(f"   Queue: {details.get('jobs_queued', 0)} jobs")
            
            # Tunnel Status
            tunnel_info = status['tunnel']
            if tunnel_info:
                tunnel_icon = "[ONLINE]"
                print(f"\n{tunnel_icon} Tunnel ({tunnel_info['name']}):")
                print(f"   Type: {'Permanent' if tunnel_info['is_permanent'] else 'Temporary'}")
                tunnel_status = tunnel_info.get('status', {})
                if tunnel_status.get('url'):
                    print(f"   URL: {tunnel_status['url']}")
                if tunnel_status.get('active'):
                    print(f"   Status: Active")
            else:
                print(f"\n[OFFLINE] Tunnel: Not configured")
            
            # Overall Integration Status
            integration_icon = "[ONLINE]" if status['integration_ready'] else "[OFFLINE]"
            print(f"\n{integration_icon} Integration:")
            print(f"   Ready: {'Yes' if status['integration_ready'] else 'No'}")
            
            if status['webhook_url']:
                print(f"   Webhook URL: {status['webhook_url']}")
            
            # Recommendations
            actions = self.system_status.get_recommended_actions()
            if actions:
                print(f"\n[INFO] RECOMMENDED ACTIONS:")
                for i, action in enumerate(actions, 1):
                    print(f"   {i}. {action}")
                    
        except Exception as e:
            print(f"[ERROR] Error getting system status: {e}")
        
        print("\n" + "=" * 50)
    
    def display_printer_menu(self):
        """Display printer management menu."""
        print("\n[PRINTER]️  PRINTER MANAGEMENT:")
        print("1. [INFO] Printer Status")
        print("2. [CONFIG] Setup/Configure Printer")
        print("3. [TEST] Test Connection")
        print("4. [DOCUMENT] Print Test Label")
        print("5. [INPUT] List All Printers")
        print("6. [DEBUG] Debug Printer Setup")
        print("0. [BACK]  Back to Main Menu")
    
    def display_test_menu(self):
        """Display test functions menu."""
        print("\n[TEST] TEST FUNCTIONS:")
        print("1. [HEALTH] API Health Check")
        print("2. [TUNNEL] Tunnel Connection Test")
        print("3. [DOCUMENT] Print Sample Label (Local API)")
        print("4. [WORLD] Print Sample Label (via Tunnel)")
        print("5. [INFO] Custom Label Test")
        print("6. [NETWORK] Network Diagnostics (Windows)")
        print("0. [BACK]  Back to Main Menu")
    
    def handle_printer_management(self):
        """Handle printer management operations."""
        while True:
            self.display_printer_menu()
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self._show_printer_status()
            elif choice == "2":
                self._setup_printer()
            elif choice == "3":
                self._test_printer_connection()
            elif choice == "4":
                self._print_test_label()
            elif choice == "5":
                self._list_all_printers()
            elif choice == "6":
                self._debug_printer_setup()
            else:
                print("[ERROR] Invalid option")
            
            input("\nPress Enter to continue...")
    
    def handle_test_functions(self):
        """Handle test function operations."""
        while True:
            self.display_test_menu()
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self._test_api_health()
            elif choice == "2":
                self._test_tunnel_connection()
            elif choice == "3":
                self._test_local_print()
            elif choice == "4":
                self._test_tunnel_print()
            elif choice == "5":
                self._test_custom_label()
            elif choice == "6":
                self._run_network_diagnostics()
            else:
                print("[ERROR] Invalid option")
            
            input("\nPress Enter to continue...")
    
    def _show_printer_status(self):
        """Show detailed printer status."""
        print("\n[STATUS] PRINTER STATUS:")
        printer_service = self.system_status.printer_service
        status = printer_service.get_status()
        
        for key, value in status.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    def _setup_printer(self):
        """Setup/configure printer."""
        print("\n[CONFIG] PRINTER SETUP:")
        printer_service = self.system_status.printer_service
        
        if hasattr(printer_service, 'setup_printer'):
            print("Setting up printer automatically...")
            success, message = printer_service.setup_printer()
            
            if success:
                print(f"[OK] {message}")
            else:
                print(f"[ERROR] {message}")
        else:
            print("[ERROR] Printer setup not supported by this printer service")
    
    def _test_printer_connection(self):
        """Test printer connection."""
        print("\n[TEST] TESTING PRINTER CONNECTION:")
        printer_service = self.system_status.printer_service
        success, message = printer_service.test_connection()
        
        if success:
            print(f"[OK] {message}")
        else:
            print(f"[ERROR] {message}")
    
    def _print_test_label(self):
        """Print test label."""
        print("\n[DOCUMENT] PRINTING TEST LABEL:")
        printer_service = self.system_status.printer_service
        
        if hasattr(printer_service, 'print_test_label'):
            success, message = printer_service.print_test_label()
            
            if success:
                print(f"[OK] {message}")
            else:
                print(f"[ERROR] {message}")
        else:
            print("[ERROR] Test label printing not supported by this printer service")
    
    def _list_all_printers(self):
        """List all available printers."""
        print("\n[INPUT] AVAILABLE PRINTERS:")
        printer_service = self.system_status.printer_service
        
        if hasattr(printer_service, 'get_printer_list'):
            printers = printer_service.get_printer_list()
            
            if printers:
                for name, status in printers.items():
                    print(f"   * {name}: {status}")
            else:
                print("   No printers found")
        else:
            print("[ERROR] Printer listing not supported by this printer service")
    
    def _test_api_health(self):
        """Test API health."""
        print("\n[HEALTH] TESTING API HEALTH:")
        api_status = self.system_status.api_service.get_status()
        
        if api_status['running']:
            url = f"http://{api_status['host']}:{api_status['port']}/health"
            success, data = self.label_service.test_api_connection(url)
            
            if success:
                print(f"[OK] API is healthy")
                if data:
                    print(f"   Response: {data}")
            else:
                print(f"[ERROR] API health check failed: {data}")
        else:
            print("[ERROR] API server is not running")
    
    def _test_tunnel_connection(self):
        """Test tunnel connection."""
        print("\n[TUNNEL] TESTING TUNNEL CONNECTION:")
        active_tunnel = self.system_status.get_active_tunnel()
        
        if active_tunnel:
            tunnel_status = active_tunnel.get_status()
            url = tunnel_status.get('url')
            
            if url:
                success, data = self.label_service.test_tunnel_connection(url, active_tunnel.name)
                
                if success:
                    print(f"[OK] Tunnel connection successful")
                    if data:
                        print(f"   Response: {data}")
                else:
                    print(f"[ERROR] Tunnel connection failed: {data}")
            else:
                print("[ERROR] Tunnel URL not available")
        else:
            print("[ERROR] No active tunnel found")
    
    def _test_local_print(self):
        """Test local API printing."""
        print("\n[DOCUMENT] TESTING LOCAL API PRINT:")
        api_status = self.system_status.api_service.get_status()
        
        if api_status['running']:
            # Get authentication token
            token = self._get_token_for_testing()
            if not token:
                print("[ERROR] No token provided - test cancelled")
                return
            
            labels = [self.label_service.create_sample_label("LOCAL")]
            url = f"http://{api_status['host']}:{api_status['port']}/print"
            
            # Add authentication header
            headers = {'Authorization': f'Bearer {token}'}
            success, message, data = self.label_service.api_client.print_labels(url, labels, headers)
            
            if success:
                print(f"[OK] {message}")
            else:
                print(f"[ERROR] {message}")
                
            if data:
                print(f"   Response: {data}")
        else:
            print("[ERROR] API server is not running")
    
    def _test_tunnel_print(self):
        """Test tunnel printing."""
        print("\n[WORLD] TESTING TUNNEL PRINT:")
        active_tunnel = self.system_status.get_active_tunnel()
        
        if active_tunnel:
            tunnel_status = active_tunnel.get_status()
            url = tunnel_status.get('url')
            
            if url:
                # Get authentication token
                token = self._get_token_for_testing()
                if not token:
                    print("[ERROR] No token provided - test cancelled")
                    return
                
                labels = [self.label_service.create_sample_label("TUNNEL")]
                print_url = f"{url}/print"
                
                # Add authentication header
                headers = {'Authorization': f'Bearer {token}'}
                success, message, data = self.label_service.api_client.print_labels(print_url, labels, headers)
                
                if success:
                    print(f"[OK] {message}")
                else:
                    print(f"[ERROR] {message}")
                    
                if data:
                    print(f"   Response: {data}")
            else:
                print("[ERROR] Tunnel URL not available")
        else:
            print("[ERROR] No active tunnel found")
    
    def _test_custom_label(self):
        """Test custom label creation and printing."""
        print("\n[INFO] CUSTOM LABEL TEST:")
        print("Enter label details:")
        
        title = input("Title: ").strip() or "CUSTOM-LABEL"
        date = input("Date (DD/MM/YY): ").strip() or "08/08/25"
        qr_code = input("QR Code data: ").strip() or f"CUSTOM{int(time.time())}"
        
        label = self.label_service.create_custom_label(title, date, qr_code)
        is_valid, message = self.label_service.validate_label_data(label)
        
        if is_valid:
            print(f"[OK] Label validation: {message}")
            print(f"   Created: {label}")
            
            # Ask where to print
            print("\nPrint via:")
            print("1. Local API")
            print("2. Tunnel")
            choice = input("Select (1-2): ").strip()
            
            if choice == "1":
                api_status = self.system_status.api_service.get_status()
                if api_status['running']:
                    url = f"http://{api_status['host']}:{api_status['port']}/print"
                    success, msg, data = self.label_service.print_labels_local([label], url)
                    print(f"{'[OK]' if success else '[ERROR]'} {msg}")
                else:
                    print("[ERROR] API server not running")
                    
            elif choice == "2":
                active_tunnel = self.system_status.get_active_tunnel()
                if active_tunnel:
                    tunnel_status = active_tunnel.get_status()
                    url = tunnel_status.get('url')
                    if url:
                        success, msg, data = self.label_service.print_labels_tunnel([label], url, active_tunnel.name)
                        print(f"{'[OK]' if success else '[ERROR]'} {msg}")
                    else:
                        print("[ERROR] Tunnel URL not available")
                else:
                    print("[ERROR] No active tunnel")
        else:
            print(f"[ERROR] Label validation failed: {message}")
    
    def run(self):
        """Run the main menu loop."""
        try:
            while self.running:
                self.display_banner()
                self.display_system_status()
                self.display_main_menu()
                
                choice = input("Select option: ").strip()
                
                if choice == "0":
                    self.running = False
                    print("\n[BYE] Goodbye!")
                elif choice == "1":
                    # Status already shown above
                    input("\nPress Enter to continue...")
                elif choice == "2":
                    self._start_api_server()
                elif choice == "3":
                    self._stop_api_server()
                elif choice == "4":
                    self._setup_tunnel()
                elif choice == "5":
                    self._start_tunnel()
                elif choice == "6":
                    self._stop_tunnel()
                elif choice == "7":
                    self.handle_printer_management()
                elif choice == "8":
                    self.handle_test_functions()
                elif choice == "9":
                    self._integration_test()
                elif choice.upper() == "A":
                    self._api_security_menu()
                else:
                    print("[ERROR] Invalid option")
                    input("\nPress Enter to continue...")
                    
        except KeyboardInterrupt:
            print("\n\n[BYE] Exiting...")
            self.running = False
        except Exception as e:
            print(f"\n[ERROR] An error occurred: {e}")
            input("\nPress Enter to continue...")
    
    def _start_api_server(self):
        """Start API server."""
        print("\n[START] STARTING API SERVER...")
        
        # Check if API is already running (supervisor mode)
        try:
            import requests
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print("[OK] API server already running (managed by supervisor)")
                print("[INFO] In Docker mode, API runs automatically via supervisor")
                input("\nPress Enter to continue...")
                return
        except:
            pass
        
        success, message = self.system_status.api_service.start()
        print(f"{'[OK]' if success else '[ERROR]'} {message}")
        input("\nPress Enter to continue...")
    
    def _stop_api_server(self):
        """Stop API server."""
        print("\n[STOP] STOPPING API SERVER...")
        success, message = self.system_status.api_service.stop()
        print(f"{'[OK]' if success else '[ERROR]'} {message}")
        input("\nPress Enter to continue...")
    
    def _setup_tunnel(self):
        """Setup tunnel."""
        print("\n[TUNNEL] TUNNEL SETUP:")
        print("1. Cloudflare Named Tunnel (Permanent URL with Custom Domain)")
        print("2. Cloudflare Quick Tunnel (Temporary URL)")
        print("3. Ngrok (Temporary URL)")
        choice = input("Select tunnel type (1-3): ").strip()
        
        if choice == "1":
            # Cloudflare Named Tunnel with custom domain
            self._setup_cloudflare_named_tunnel()
        elif choice == "2":
            # Cloudflare Quick Tunnel
            if "cloudflare_quick" in self.system_status.tunnel_providers:
                tunnel = self.system_status.tunnel_providers["cloudflare_quick"]
                print(f"\n[CONFIG] Setting up Cloudflare Quick Tunnel...")
                success, message = tunnel.setup()
                print(f"{'[OK]' if success else '[ERROR]'} {message}")
                if success:
                    print("\n[INFO] Quick tunnels provide instant URLs without domain ownership!")
                    print("[INFO] Perfect for testing - no DNS setup required!")
            else:
                print("[ERROR] Cloudflare Quick tunnel provider not available")
        elif choice == "3":
            # Ngrok
            if "ngrok" in self.system_status.tunnel_providers:
                tunnel = self.system_status.tunnel_providers["ngrok"]
                print(f"\n[CONFIG] Setting up Ngrok tunnel...")
                success, message = tunnel.setup()
                print(f"{'[OK]' if success else '[ERROR]'} {message}")
            else:
                print("[ERROR] Ngrok tunnel provider not available")
        else:
            print("[ERROR] Invalid option")
        
        input("\nPress Enter to continue...")
    
    def _setup_cloudflare_named_tunnel(self):
        """Setup Cloudflare Named Tunnel with custom domain input."""
        print("\n[SETUP] CLOUDFLARE NAMED TUNNEL SETUP")
        print("=" * 40)
        
        # Import here to avoid circular imports
        from zebra_print.tunnel.cloudflare_named import CloudflareNamedTunnel
        
        print("[INFO]  Named tunnels provide permanent URLs with your custom domain")
        print("[INFO] Examples:")
        print("   * tln-zebra-01.abcfood.app")
        print("   * printer-hq.mycompany.com")
        print("   * zebra-label.mydomain.org")
        print()
        
        # Get custom domain from user
        while True:
            domain = input("[TUNNEL] Enter your custom domain: ").strip()
            
            if not domain:
                print("[ERROR] Domain cannot be empty")
                continue
            
            if '.' not in domain:
                print("[ERROR] Please enter a valid domain (e.g., subdomain.yourdomain.com)")
                continue
            
            if ' ' in domain or domain != domain.lower():
                print("[ERROR] Domain should be lowercase without spaces")
                continue
            
            # Confirm domain
            print(f"[TARGET] Your webhook URL will be: https://{domain}/print")
            confirm = input("[OK] Is this correct? (y/n): ").strip().lower()
            
            if confirm in ['y', 'yes']:
                break
            else:
                print("Let's try again...")
                continue
        
        # Initialize Named Tunnel with custom domain
        tunnel = CloudflareNamedTunnel(custom_domain=domain)
        
        # Set the custom domain
        success, message = tunnel.set_custom_domain(domain)
        if not success:
            print(f"[ERROR] Failed to set domain: {message}")
            return
        
        print(f"[OK] {message}")
        
        # Check authentication
        print("\n[AUTH] Checking Cloudflare authentication...")
        import os
        cert_path = os.path.expanduser("~/.cloudflared/cert.pem")
        
        if not os.path.exists(cert_path):
            print("[ERROR] Cloudflare authentication required")
            print("[URL] Please run this command first:")
            print("   cloudflared tunnel login")
            print("\nThis will:")
            print("1. Open browser to Cloudflare login")
            print("2. Select your domain")
            print("3. Authorize cloudflared")
            
            auth_done = input("\n[OK] Press Enter after completing authentication...")
            
            # Check again
            if not os.path.exists(cert_path):
                print("[ERROR] Authentication still not detected. Please complete authentication first.")
                return
        
        # Setup the tunnel
        print(f"\n[CONFIG] Setting up Named Tunnel for {domain}...")
        success, message = tunnel.setup()
        
        if success:
            print(f"[OK] {message}")
            print(f"[TUNNEL] Your permanent webhook URL: https://{domain}/print")
            print("[INFO] Use this URL in your Odoo webhook configuration")
        else:
            print(f"[ERROR] Setup failed: {message}")
            
            if "authentication" in message.lower():
                print("\n[INFO] Try running: cloudflared tunnel login")
            elif "dns" in message.lower() or "domain" in message.lower():
                print(f"\n[INFO] Make sure {domain} is managed by Cloudflare DNS")
                print("   1. Add domain to Cloudflare")
                print("   2. Update nameservers")
                print("   3. Verify domain is active")
    
    def _start_tunnel(self):
        """Start tunnel."""
        print("\n[URL] STARTING TUNNEL:")
        active_tunnel = self.system_status.get_active_tunnel()
        
        if active_tunnel and active_tunnel.is_active():
            print(f"[OK] {active_tunnel.name.title()} tunnel already active")
            status = active_tunnel.get_status()
            if status.get('url'):
                print(f"   URL: {status['url']}")
        else:
            print("1. Cloudflare Named (Permanent with Custom Domain)")
            print("2. Cloudflare Quick (Temporary)")
            print("3. Ngrok (Temporary)")
            choice = input("Select tunnel (1-3): ").strip()
            
            if choice == "1":
                tunnel_name = "cloudflare_named"
            elif choice == "2":
                tunnel_name = "cloudflare_quick"
            elif choice == "3":
                tunnel_name = "ngrok"
            else:
                print("[ERROR] Invalid option")
                input("\nPress Enter to continue...")
                return
            
            if tunnel_name in self.system_status.tunnel_providers:
                tunnel = self.system_status.tunnel_providers[tunnel_name]
                
                # Check if tunnel is configured first
                if tunnel_name == "cloudflare_named":
                    stored_config = self.system_status.db.get_tunnel_config(tunnel_name)
                    if not stored_config or not stored_config.is_configured:
                        print("[ERROR] Named tunnel not configured yet")
                        print("[INFO] Please run 'Setup Tunnel' first and configure your domain")
                        input("\nPress Enter to continue...")
                        return
                
                print(f"\n[START] Starting {tunnel_name.replace('_', ' ').title()} tunnel...")
                success, message, url = tunnel.start()
                
                if success:
                    print(f"[OK] {message}")
                    if url:
                        print(f"[TUNNEL] URL: {url}")
                        if tunnel_name == "cloudflare_named":
                            print(f"[URL] Webhook URL: {url}/print")
                else:
                    print(f"[ERROR] {message}")
            else:
                print(f"[ERROR] {tunnel_name.title()} tunnel provider not available")
        
        input("\nPress Enter to continue...")
    
    def _stop_tunnel(self):
        """Stop tunnel."""
        print("\n[STOP]  STOPPING TUNNEL...")
        active_tunnel = self.system_status.get_active_tunnel()
        
        if active_tunnel:
            success, message = active_tunnel.stop()
            print(f"{'[OK]' if success else '[ERROR]'} {message}")
        else:
            print("[OK] No active tunnel to stop")
        
        input("\nPress Enter to continue...")
    
    def _integration_test(self):
        """Run comprehensive integration test."""
        print("\n[SEND] INTEGRATION TEST:")
        print("Testing complete system integration...")
        
        # Check if system is ready
        if not self.system_status.is_system_ready():
            print("[ERROR] System not ready for integration test")
            actions = self.system_status.get_recommended_actions()
            print("   Required actions:")
            for action in actions:
                print(f"   * {action}")
        else:
            print("[OK] System is ready")
            
            # Test webhook URL
            status = self.system_status.get_overall_status()
            webhook_url = status.get('webhook_url')
            
            if webhook_url:
                print(f"[URL] Webhook URL: {webhook_url}")
                
                # Create test labels
                labels = [
                    self.label_service.create_sample_label("INT-TEST-1"),
                    self.label_service.create_sample_label("INT-TEST-2")
                ]
                
                print("[SEND] Sending test labels via webhook...")
                active_tunnel = self.system_status.get_active_tunnel()
                
                success, message, data = self.label_service.print_labels_tunnel(
                    labels, webhook_url.replace('/print', ''), active_tunnel.name if active_tunnel else 'cloudflare'
                )
                
                if success:
                    print(f"[OK] Integration test successful: {message}")
                    print("   Your Odoo webhook integration is ready!")
                else:
                    print(f"[ERROR] Integration test failed: {message}")
            else:
                print("[ERROR] Webhook URL not available")
        
        input("\nPress Enter to continue...")
    
    def _api_security_menu(self):
        """Handle API security and token management."""
        while True:
            print("\n[AUTH] API SECURITY MANAGEMENT:")
            print("1. [INFO] List API Tokens")
            print("2. [KEY] Generate New Token") 
            print("3. [DELETE]  Revoke Token")
            print("4. [TEST] Test Authentication")
            print("5. [DOCS] Show Integration Examples")
            print("6. [SEARCH] Show Default Token")
            print("0. [BACK]  Back to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self._list_api_tokens()
            elif choice == "2":
                self._generate_api_token()
            elif choice == "3":
                self._revoke_api_token()
            elif choice == "4":
                self._test_authentication()
            elif choice == "5":
                self._show_integration_examples()
            elif choice == "6":
                self._show_default_token()
            else:
                print("[ERROR] Invalid option")
            
            input("\nPress Enter to continue...")
    
    def _list_api_tokens(self):
        """List all API tokens."""
        print("\n[INFO] API TOKENS:")
        
        try:
            import requests
            api_status = self.system_status.api_service.get_status()
            
            if not api_status['running']:
                print("[ERROR] API server not running. Start it first.")
                return
            
            # Get token information
            info_url = f"http://{api_status['host']}:{api_status['port']}/auth/info"
            
            response = requests.get(info_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self._display_tokens(data['tokens'])
                
                if data['total_tokens'] == 1 and data['tokens'][0]['name'] == 'default':
                    print("\n[INFO] You have a default token generated at startup")
                    print("[INFO] Check the container logs for the token value:")
                    print("   docker logs zebra-print-control | grep '[KEY] Generated'")
            else:
                print("[ERROR] Failed to get token information")
                print("[INFO] Generate your first token using option 2")
                
        except Exception as e:
            print(f"[ERROR] Error listing tokens: {e}")
    
    def _display_tokens(self, tokens):
        """Display token information in a table format."""
        if not tokens:
            print("   No tokens found")
            return
        
        print(f"   {'Name':<15} {'Status':<8} {'Created':<20} {'Last Used':<20}")
        print("   " + "-" * 70)
        
        for token in tokens:
            status = "Active" if token['is_active'] else "Revoked"
            created = token['created_at'][:19] if token['created_at'] else "Unknown"
            last_used = token['last_used'][:19] if token['last_used'] else "Never"
            
            print(f"   {token['name']:<15} {status:<8} {created:<20} {last_used:<20}")
    
    def _generate_api_token(self):
        """Generate a new API token."""
        print("\n[KEY] GENERATE NEW API TOKEN:")
        
        try:
            import requests
            api_status = self.system_status.api_service.get_status()
            
            if not api_status['running']:
                print("[ERROR] API server not running. Start it first.")
                return
            
            # First check if there's a default token that can be retrieved
            info_url = f"http://{api_status['host']}:{api_status['port']}/auth/info"
            info_response = requests.get(info_url, timeout=5)
            
            if info_response.status_code == 200:
                info_data = info_response.json()
                if (info_data['total_tokens'] == 1 and 
                    info_data['tokens'][0]['name'] == 'default' and 
                    info_data['tokens'][0]['is_active']):
                    
                    print("[INFO] You already have a default token!")
                    print("[INFO] To get the token value, check the startup logs:")
                    print("   docker logs zebra-print-control | grep '[KEY] Generated'")
                    
                    choice = input("\nGenerate additional token? (y/N): ").strip().lower()
                    if choice not in ['y', 'yes']:
                        return
        
            name = input("Token name (default): ").strip() or "default"
            description = input("Description (optional): ").strip()
            
            url = f"http://{api_status['host']}:{api_status['port']}/auth/token"
            payload = {"name": name}
            if description:
                payload["description"] = description
            
            response = requests.post(url, json=payload, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                token = data['token']
                
                print(f"\n[OK] Token generated successfully!")
                print(f"[KEY] Token: {token}")
                print(f"[INPUT] Name: {name}")
                print(f"\n[AUTH] SAVE THIS TOKEN - you cannot retrieve it again!")
                print(f"\n[INFO] Webhook Integration Examples:")
                print(f"   Header: Authorization: Bearer {token}")
                print(f"   Query:  /print?token={token}")
                
                # Update webhook URL in tunnel status
                self._update_webhook_url_with_token(token)
                
            else:
                error_data = response.json()
                print(f"[ERROR] Failed to generate token: {error_data.get('message', 'Unknown error')}")
                
                if "Authentication required" in error_data.get('message', ''):
                    print("\n[INFO] To generate additional tokens, you need an existing valid token")
                    print("[INFO] Get your default token from startup logs:")
                    print("   docker logs zebra-print-control | grep '[KEY] Generated'")
                elif "already exists" in error_data.get('message', ''):
                    print(f"\n[INFO] Token name '{name}' already exists. Try a different name.")
                    print("[INFO] Use option 1 to see existing token names.")
                
        except Exception as e:
            print(f"[ERROR] Error generating token: {e}")
    
    def _revoke_api_token(self):
        """Revoke an API token."""
        print("\n[DELETE]  REVOKE API TOKEN:")
        
        # First list existing tokens
        self._list_api_tokens()
        
        name = input("\nEnter token name to revoke: ").strip()
        if not name:
            print("[ERROR] Token name required")
            return
        
        confirm = input(f"[WARNING]️  Are you sure you want to revoke '{name}'? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("[ERROR] Revocation cancelled")
            return
        
        try:
            import requests
            api_status = self.system_status.api_service.get_status()
            url = f"http://{api_status['host']}:{api_status['port']}/auth/token/{name}"
            
            # This requires authentication - user needs valid token
            token = input("Enter valid API token for authentication: ").strip()
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.delete(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print(f"[OK] Token '{name}' revoked successfully")
            else:
                error_data = response.json()
                print(f"[ERROR] Failed to revoke token: {error_data.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"[ERROR] Error revoking token: {e}")
    
    def _test_authentication(self):
        """Test API authentication with user's token."""
        print("\n[TEST] TEST API AUTHENTICATION:")
        
        token = input("Enter API token to test: ").strip()
        if not token:
            print("[ERROR] Token required")
            return
        
        try:
            import requests
            api_status = self.system_status.api_service.get_status()
            
            # Test protected endpoint
            url = f"http://{api_status['host']}:{api_status['port']}/printer/status"
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print("[OK] Authentication successful!")
                data = response.json()
                print(f"   Response: {data}")
            elif response.status_code == 401:
                print("[ERROR] Authentication failed - invalid or revoked token")
            else:
                print(f"[ERROR] Unexpected response: {response.status_code}")
                
        except Exception as e:
            print(f"[ERROR] Test failed: {e}")
    
    def _show_integration_examples(self):
        """Show webhook integration examples."""
        print("\n[DOCS] WEBHOOK INTEGRATION EXAMPLES:")
        print("=" * 50)
        
        # Get tunnel URL
        active_tunnel = self.system_status.get_active_tunnel()
        webhook_url = "https://your-domain.com"
        
        if active_tunnel:
            status = active_tunnel.get_status()
            if status.get('url'):
                webhook_url = status['url']
        
        print(f"\n[URL] Your Webhook URL: {webhook_url}/print")
        print(f"\n1. **Authorization Header (Recommended)**:")
        print(f"   URL: {webhook_url}/print")
        print(f"   Headers: Authorization: Bearer zp_your_token_here")
        print(f"   Body: {{\"labels\": [...]}}")
        
        print(f"\n2. **Query Parameter**:")
        print(f"   URL: {webhook_url}/print?token=zp_your_token_here")
        print(f"   Body: {{\"labels\": [...]}}")
        
        print(f"\n3. **Request Body**:")
        print(f"   URL: {webhook_url}/print")
        print(f"   Body: {{\"token\": \"zp_your_token_here\", \"labels\": [...]}}")
        
        print(f"\n[INFO] **Odoo Webhook Configuration:**")
        print(f"   * URL: {webhook_url}/print")
        print(f"   * Method: POST")
        print(f"   * Headers: Authorization: Bearer zp_your_token_here")
        print(f"   * Content-Type: application/json")
    
    def _show_default_token(self):
        """Show the default token from startup logs."""
        print("\n[SEARCH] DEFAULT TOKEN:")
        
        try:
            import subprocess
            
            # Get the default token from container logs
            result = subprocess.run([
                'docker', 'logs', 'zebra-print-control'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                token_line = None
                
                for line in reversed(lines):  # Check from newest to oldest
                    if "[KEY] Generated default API token:" in line:
                        token_line = line
                        break
                
                if token_line:
                    token = token_line.split("[KEY] Generated default API token: ")[1].strip()
                    print(f"[KEY] Default Token: {token}")
                    print(f"\n[INFO] Use this token for webhook authentication:")
                    print(f"   Authorization: Bearer {token}")
                    
                    # Show current webhook URL with token
                    active_tunnel = self.system_status.get_active_tunnel()
                    if active_tunnel:
                        status = active_tunnel.get_status()
                        if status.get('url'):
                            webhook_url = status['url']
                            print(f"\n[TUNNEL] Ready-to-use Webhook URL:")
                            print(f"   {webhook_url}/print")
                            print(f"   Header: Authorization: Bearer {token}")
                else:
                    print("[ERROR] Default token not found in logs")
                    print("[INFO] Generate a new token using option 2")
            else:
                print("[ERROR] Failed to read container logs")
                
        except Exception as e:
            print(f"[ERROR] Error retrieving token: {e}")
    
    def _update_webhook_url_with_token(self, token):
        """Update internal webhook URL tracking with token."""
        # This method can be enhanced to update stored webhook configurations
        pass
    
    def _get_token_for_testing(self):
        """Get token for testing - automatically use default token or prompt user."""
        try:
            # Get available tokens from API
            import requests
            api_status = self.system_status.api_service.get_status()
            
            if api_status['running']:
                info_url = f"http://{api_status['host']}:{api_status['port']}/auth/info"
                response = requests.get(info_url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    active_tokens = [t for t in data['tokens'] if t['is_active']]
                    
                    # First try to find and use the default token
                    default_token = next((t for t in active_tokens if t['name'] == 'default'), None)
                    if default_token:
                        print(f"\n[INFO] Found default token, but need the actual value for testing")
                        print(f"[INFO] The default token was generated when the API started")
                        print(f"[INFO] You can find it in the console output where you started the API")
                        print(f"[INFO] Look for: '[KEY] Generated default API token: <token_value>'")
                        
                        print(f"\n[OPTION] You can:")
                        print(f"   1. Copy the default token from startup logs")
                        print(f"   2. Generate a new token using 'A. API Security' menu")
                        print(f"   3. Skip this test")
                        
                        choice = input(f"\nEnter token value or press Enter to skip: ").strip()
                        return choice if choice else None
                    
                    if active_tokens:
                        print(f"\n[INFO] Found {len(active_tokens)} active token(s):")
                        for token in active_tokens:
                            print(f"   - {token['name']}")
                        
                        print("\n[KEY] Enter your API token for testing:")
                        print("   (You can find your tokens in 'A. API Security' -> 'Generate New Token')")
                        user_token = input("Token: ").strip()
                        return user_token if user_token else None
                    else:
                        print("[ERROR] No active tokens found")
                        print("[INFO] Generate a token first using 'A. API Security' menu")
                        return None
                else:
                    print(f"[ERROR] Failed to get token info from API: HTTP {response.status_code}")
                    return None
            else:
                print("[ERROR] API server not running")
                return None
                        
        except Exception as e:
            print(f"[ERROR] Error getting token info: {e}")
            return None
    
    def _get_default_token_value(self):
        """Get the actual default token value from API startup logs or generate a new one."""
        try:
            # For now, we'll generate a temporary token for testing
            # In a real deployment, this would be stored securely
            import requests
            import secrets
            
            api_status = self.system_status.api_service.get_status()
            
            # Try to get the actual token value by generating a new default token
            # This is a workaround since we don't have access to the original token value
            generate_url = f"http://{api_status['host']}:{api_status['port']}/auth/token/default-test"
            
            # Create a test token for this session
            test_token_data = {
                'name': 'test-session',
                'description': 'Temporary token for testing'
            }
            
            # For testing purposes, return a placeholder that the user should replace
            print("[INFO] For testing, please generate a token from the API Security menu")
            print("[INFO] Or check the API startup logs for the default token")
            
            # Return None to prompt user for manual token entry
            return None
            
        except Exception as e:
            print(f"[ERROR] Could not get default token: {e}")
            return None
    
    def _run_network_diagnostics(self):
        """Run network diagnostics for Windows troubleshooting."""
        print("\n[NETWORK] NETWORK DIAGNOSTICS:")
        print("Running Windows network connectivity tests...")
        
        try:
            import socket
            import platform
            
            if platform.system() != "Windows":
                print("[INFO] This diagnostic is designed for Windows")
                print("[INFO] On other systems, check firewall and network settings")
                return
            
            # Test 1: Basic localhost connectivity
            print("\n[TEST 1] Localhost connectivity...")
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect(("127.0.0.1", 80))
                sock.close()
                print("[OK] Localhost connectivity works")
            except Exception:
                print("[INFO] Port 80 not available (normal)")
            
            # Test 2: Check if API port is available
            print(f"\n[TEST 2] API port {self.system_status.api_service.port} availability...")
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(("127.0.0.1", self.system_status.api_service.port))
                sock.close()
                
                if result == 0:
                    print(f"[OK] Something is listening on port {self.system_status.api_service.port}")
                    
                    # Try API health check
                    try:
                        import requests
                        response = requests.get(f"http://127.0.0.1:{self.system_status.api_service.port}/health", timeout=2)
                        if response.status_code == 200:
                            print("[OK] API health check successful")
                        else:
                            print(f"[WARNING] API responded with status {response.status_code}")
                    except requests.exceptions.Timeout:
                        print("[ERROR] API health check timed out")
                    except Exception as e:
                        print(f"[ERROR] API health check failed: {e}")
                        
                else:
                    print(f"[INFO] Port {self.system_status.api_service.port} is available (nothing listening)")
                    
            except Exception as e:
                print(f"[ERROR] Port test failed: {e}")
            
            # Test 3: Windows Firewall check
            print(f"\n[TEST 3] Windows Firewall status...")
            try:
                import subprocess
                result = subprocess.run([
                    "netsh", "advfirewall", "show", "allprofiles", "state"
                ], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                if result.returncode == 0:
                    if "ON" in result.stdout.upper():
                        print("[WARNING] Windows Firewall is ENABLED")
                        print("[INFO] This might block localhost connections")
                        print("[INFO] Try temporarily disabling firewall for testing")
                    else:
                        print("[OK] Windows Firewall appears to be disabled")
                else:
                    print("[INFO] Could not check firewall status")
            except Exception as e:
                print(f"[ERROR] Firewall check failed: {e}")
            
            # Test 4: Process check
            print(f"\n[TEST 4] API process status...")
            api_status = self.system_status.api_service.get_status()
            if api_status['running']:
                print(f"[OK] API process is running (PID: {api_status.get('pid', 'unknown')})")
            else:
                print("[WARNING] API process is not running")
                print("[INFO] Start the API server first (option 2 from main menu)")
            
            # Recommendations
            print(f"\n[RECOMMENDATIONS]")
            print("If API connection still fails:")
            print("1. Try running as Administrator")
            print("2. Temporarily disable Windows Firewall")
            print("3. Check Windows Defender/Antivirus settings")
            print("4. Try a different port (modify settings)")
            print("5. Check if another process is using the port")
            print("6. Restart the application")
            
        except Exception as e:
            print(f"[ERROR] Diagnostics failed: {e}")
    
    def _debug_printer_setup(self):
        """Debug printer setup and configuration."""
        print("\n[DEBUG] PRINTER SETUP DEBUGGING:")
        print("Analyzing printer configuration...")
        
        try:
            import platform
            if platform.system() != "Windows":
                print("[INFO] This debug is designed for Windows")
                return
            
            # Test 1: Get detailed printer information
            print("\n[TEST 1] Printer Information...")
            try:
                import subprocess
                cmd = [
                    "powershell", "-Command",
                    "Get-Printer | Select-Object Name, PrinterStatus, PortName, DriverName | Format-Table -AutoSize"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                if result.returncode == 0:
                    print("Available Printers:")
                    print(result.stdout)
                else:
                    print(f"[ERROR] Could not get printer info: {result.stderr}")
            except Exception as e:
                print(f"[ERROR] Printer info failed: {e}")
            
            # Test 2: Check current printer name
            current_printer = self.system_status.printer_service._printer_name
            print(f"\n[TEST 2] Current Configured Printer: '{current_printer}'")
            
            # Test 3: Test printer existence
            print(f"\n[TEST 3] Testing printer existence...")
            status = self.system_status.printer_service.get_status()
            print(f"Printer exists: {status['exists']}")
            print(f"Printer enabled: {status['enabled']}")
            print(f"Printer state: {status['state']}")
            print(f"Connection type: {status['connection']}")
            
            # Test 4: Try simple ZPL test
            print(f"\n[TEST 4] Testing ZPL printing methods...")
            simple_zpl = "^XA^FO50,50^A0,50,50^FDTEST^FS^XZ"
            
            # Test the actual print method
            success, message = self.system_status.printer_service.print_zpl(simple_zpl)
            print(f"Print test result: {success}")
            print(f"Print message: {message}")
            
            # Test 5: Check available printer ports
            print(f"\n[TEST 5] Checking printer ports...")
            try:
                cmd = [
                    "powershell", "-Command",
                    f"Get-Printer -Name '{current_printer}' | Select-Object Name, PortName, ShareName | Format-List"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                if result.returncode == 0:
                    print("Printer Details:")
                    print(result.stdout)
                else:
                    print(f"[WARNING] Could not get detailed printer info")
            except Exception as e:
                print(f"[ERROR] Port check failed: {e}")
            
            # Recommendations
            print(f"\n[RECOMMENDATIONS]")
            if not status['exists']:
                print("❌ Printer not found:")
                print(f"   - Check if '{current_printer}' is the correct printer name")
                print("   - Try option '5. List All Printers' to see available printers")
                print("   - You may need to update the printer name in settings")
            elif status['connection'] == 'USB':
                print("⚠️  USB Printer detected:")
                print("   - USB printers may need special ZPL driver setup")
                print("   - Try installing Zebra driver in 'ZPL' or 'Raw' mode")
                print("   - Check if printer supports direct ZPL printing")
            else:
                print("ℹ️  Printer setup appears correct")
                print("   - If printing still fails, try different ZPL commands")
                print("   - Check printer queue for stuck jobs")
                
        except Exception as e:
            print(f"[ERROR] Debug failed: {e}")