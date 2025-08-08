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
        print("\n📋 MAIN MENU:")
        print("1. 📊 System Status")
        print("2. 🚀 Start API Server")
        print("3. 🛑 Stop API Server")
        print("4. 🌐 Setup Tunnel")
        print("5. 🔗 Start Tunnel")
        print("6. ⏹️  Stop Tunnel")
        print("7. 🖨️  Printer Management")
        print("8. 🧪 Test Functions")
        print("9. 📤 Integration Test")
        print("A. 🔐 API Security")
        print("0. 🚪 Exit")
        print("-" * 40)
    
    def display_system_status(self):
        """Display comprehensive system status."""
        print("\n📊 SYSTEM STATUS:")
        print("=" * 50)
        
        try:
            status = self.system_status.get_overall_status()
            
            # API Status
            api_status = status['api']
            api_icon = "🟢" if api_status['running'] else "🔴"
            print(f"\n{api_icon} API Server:")
            print(f"   Status: {'Running' if api_status['running'] else 'Stopped'}")
            if api_status['details']:
                details = api_status['details']
                print(f"   URL: {details.get('url', 'N/A')}")
                if 'pid' in details:
                    print(f"   PID: {details['pid']}")
            
            # Printer Status
            printer_status = status['printer']
            printer_icon = "🟢" if printer_status['ready'] else "🔴"
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
                tunnel_icon = "🟢"
                print(f"\n{tunnel_icon} Tunnel ({tunnel_info['name']}):")
                print(f"   Type: {'Permanent' if tunnel_info['is_permanent'] else 'Temporary'}")
                tunnel_status = tunnel_info.get('status', {})
                if tunnel_status.get('url'):
                    print(f"   URL: {tunnel_status['url']}")
                if tunnel_status.get('active'):
                    print(f"   Status: Active")
            else:
                print(f"\n🔴 Tunnel: Not configured")
            
            # Overall Integration Status
            integration_icon = "🟢" if status['integration_ready'] else "🔴"
            print(f"\n{integration_icon} Integration:")
            print(f"   Ready: {'Yes' if status['integration_ready'] else 'No'}")
            
            if status['webhook_url']:
                print(f"   Webhook URL: {status['webhook_url']}")
            
            # Recommendations
            actions = self.system_status.get_recommended_actions()
            if actions:
                print(f"\n💡 RECOMMENDED ACTIONS:")
                for i, action in enumerate(actions, 1):
                    print(f"   {i}. {action}")
                    
        except Exception as e:
            print(f"❌ Error getting system status: {e}")
        
        print("\n" + "=" * 50)
    
    def display_printer_menu(self):
        """Display printer management menu."""
        print("\n🖨️  PRINTER MANAGEMENT:")
        print("1. 📋 Printer Status")
        print("2. 🔧 Setup/Configure Printer")
        print("3. 🧪 Test Connection")
        print("4. 📄 Print Test Label")
        print("5. 📝 List All Printers")
        print("0. ⬅️  Back to Main Menu")
    
    def display_test_menu(self):
        """Display test functions menu."""
        print("\n🧪 TEST FUNCTIONS:")
        print("1. 🏥 API Health Check")
        print("2. 🌐 Tunnel Connection Test")
        print("3. 📄 Print Sample Label (Local API)")
        print("4. 🌍 Print Sample Label (via Tunnel)")
        print("5. 📋 Custom Label Test")
        print("0. ⬅️  Back to Main Menu")
    
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
            else:
                print("❌ Invalid option")
            
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
            else:
                print("❌ Invalid option")
            
            input("\nPress Enter to continue...")
    
    def _show_printer_status(self):
        """Show detailed printer status."""
        print("\n📊 PRINTER STATUS:")
        printer_service = self.system_status.printer_service
        status = printer_service.get_status()
        
        for key, value in status.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    def _setup_printer(self):
        """Setup/configure printer."""
        print("\n🔧 PRINTER SETUP:")
        printer_service = self.system_status.printer_service
        
        if hasattr(printer_service, 'setup_printer'):
            print("Setting up printer automatically...")
            success, message = printer_service.setup_printer()
            
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
        else:
            print("❌ Printer setup not supported by this printer service")
    
    def _test_printer_connection(self):
        """Test printer connection."""
        print("\n🧪 TESTING PRINTER CONNECTION:")
        printer_service = self.system_status.printer_service
        success, message = printer_service.test_connection()
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    def _print_test_label(self):
        """Print test label."""
        print("\n📄 PRINTING TEST LABEL:")
        printer_service = self.system_status.printer_service
        
        if hasattr(printer_service, 'print_test_label'):
            success, message = printer_service.print_test_label()
            
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
        else:
            print("❌ Test label printing not supported by this printer service")
    
    def _list_all_printers(self):
        """List all available printers."""
        print("\n📝 AVAILABLE PRINTERS:")
        printer_service = self.system_status.printer_service
        
        if hasattr(printer_service, 'get_printer_list'):
            printers = printer_service.get_printer_list()
            
            if printers:
                for name, status in printers.items():
                    print(f"   • {name}: {status}")
            else:
                print("   No printers found")
        else:
            print("❌ Printer listing not supported by this printer service")
    
    def _test_api_health(self):
        """Test API health."""
        print("\n🏥 TESTING API HEALTH:")
        api_status = self.system_status.api_service.get_status()
        
        if api_status['running']:
            url = f"http://{api_status['host']}:{api_status['port']}/health"
            success, data = self.label_service.test_api_connection(url)
            
            if success:
                print(f"✅ API is healthy")
                if data:
                    print(f"   Response: {data}")
            else:
                print(f"❌ API health check failed: {data}")
        else:
            print("❌ API server is not running")
    
    def _test_tunnel_connection(self):
        """Test tunnel connection."""
        print("\n🌐 TESTING TUNNEL CONNECTION:")
        active_tunnel = self.system_status.get_active_tunnel()
        
        if active_tunnel:
            tunnel_status = active_tunnel.get_status()
            url = tunnel_status.get('url')
            
            if url:
                success, data = self.label_service.test_tunnel_connection(url, active_tunnel.name)
                
                if success:
                    print(f"✅ Tunnel connection successful")
                    if data:
                        print(f"   Response: {data}")
                else:
                    print(f"❌ Tunnel connection failed: {data}")
            else:
                print("❌ Tunnel URL not available")
        else:
            print("❌ No active tunnel found")
    
    def _test_local_print(self):
        """Test local API printing."""
        print("\n📄 TESTING LOCAL API PRINT:")
        api_status = self.system_status.api_service.get_status()
        
        if api_status['running']:
            # Get authentication token
            token = self._get_default_token()
            if not token:
                print("❌ No authentication token available")
                print("💡 Generate a token first using 'A. API Security' menu")
                return
            
            labels = [self.label_service.create_sample_label("LOCAL")]
            url = f"http://{api_status['host']}:{api_status['port']}/print"
            
            # Add authentication header
            headers = {'Authorization': f'Bearer {token}'}
            success, message, data = self.label_service.api_client.print_labels(url, labels, headers)
            
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
                
            if data:
                print(f"   Response: {data}")
        else:
            print("❌ API server is not running")
    
    def _test_tunnel_print(self):
        """Test tunnel printing."""
        print("\n🌍 TESTING TUNNEL PRINT:")
        active_tunnel = self.system_status.get_active_tunnel()
        
        if active_tunnel:
            tunnel_status = active_tunnel.get_status()
            url = tunnel_status.get('url')
            
            if url:
                # Get authentication token
                token = self._get_default_token()
                if not token:
                    print("❌ No authentication token available")
                    print("💡 Generate a token first using 'A. API Security' menu")
                    return
                
                labels = [self.label_service.create_sample_label("TUNNEL")]
                print_url = f"{url}/print"
                
                # Add authentication header
                headers = {'Authorization': f'Bearer {token}'}
                success, message, data = self.label_service.api_client.print_labels(print_url, labels, headers)
                
                if success:
                    print(f"✅ {message}")
                else:
                    print(f"❌ {message}")
                    
                if data:
                    print(f"   Response: {data}")
            else:
                print("❌ Tunnel URL not available")
        else:
            print("❌ No active tunnel found")
    
    def _test_custom_label(self):
        """Test custom label creation and printing."""
        print("\n📋 CUSTOM LABEL TEST:")
        print("Enter label details:")
        
        title = input("Title: ").strip() or "CUSTOM-LABEL"
        date = input("Date (DD/MM/YY): ").strip() or "08/08/25"
        qr_code = input("QR Code data: ").strip() or f"CUSTOM{int(time.time())}"
        
        label = self.label_service.create_custom_label(title, date, qr_code)
        is_valid, message = self.label_service.validate_label_data(label)
        
        if is_valid:
            print(f"✅ Label validation: {message}")
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
                    print(f"{'✅' if success else '❌'} {msg}")
                else:
                    print("❌ API server not running")
                    
            elif choice == "2":
                active_tunnel = self.system_status.get_active_tunnel()
                if active_tunnel:
                    tunnel_status = active_tunnel.get_status()
                    url = tunnel_status.get('url')
                    if url:
                        success, msg, data = self.label_service.print_labels_tunnel([label], url, active_tunnel.name)
                        print(f"{'✅' if success else '❌'} {msg}")
                    else:
                        print("❌ Tunnel URL not available")
                else:
                    print("❌ No active tunnel")
        else:
            print(f"❌ Label validation failed: {message}")
    
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
                    print("\n👋 Goodbye!")
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
                    print("❌ Invalid option")
                    input("\nPress Enter to continue...")
                    
        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            self.running = False
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            input("\nPress Enter to continue...")
    
    def _start_api_server(self):
        """Start API server."""
        print("\n🚀 STARTING API SERVER...")
        
        # Check if API is already running (supervisor mode)
        try:
            import requests
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API server already running (managed by supervisor)")
                print("ℹ️ In Docker mode, API runs automatically via supervisor")
                input("\nPress Enter to continue...")
                return
        except:
            pass
        
        success, message = self.system_status.api_service.start()
        print(f"{'✅' if success else '❌'} {message}")
        input("\nPress Enter to continue...")
    
    def _stop_api_server(self):
        """Stop API server."""
        print("\n🛑 STOPPING API SERVER...")
        success, message = self.system_status.api_service.stop()
        print(f"{'✅' if success else '❌'} {message}")
        input("\nPress Enter to continue...")
    
    def _setup_tunnel(self):
        """Setup tunnel."""
        print("\n🌐 TUNNEL SETUP:")
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
                print(f"\n🔧 Setting up Cloudflare Quick Tunnel...")
                success, message = tunnel.setup()
                print(f"{'✅' if success else '❌'} {message}")
                if success:
                    print("\n💡 Quick tunnels provide instant URLs without domain ownership!")
                    print("💡 Perfect for testing - no DNS setup required!")
            else:
                print("❌ Cloudflare Quick tunnel provider not available")
        elif choice == "3":
            # Ngrok
            if "ngrok" in self.system_status.tunnel_providers:
                tunnel = self.system_status.tunnel_providers["ngrok"]
                print(f"\n🔧 Setting up Ngrok tunnel...")
                success, message = tunnel.setup()
                print(f"{'✅' if success else '❌'} {message}")
            else:
                print("❌ Ngrok tunnel provider not available")
        else:
            print("❌ Invalid option")
        
        input("\nPress Enter to continue...")
    
    def _setup_cloudflare_named_tunnel(self):
        """Setup Cloudflare Named Tunnel with custom domain input."""
        print("\n🏗️ CLOUDFLARE NAMED TUNNEL SETUP")
        print("=" * 40)
        
        # Import here to avoid circular imports
        from zebra_print.tunnel.cloudflare_named import CloudflareNamedTunnel
        
        print("ℹ️  Named tunnels provide permanent URLs with your custom domain")
        print("📋 Examples:")
        print("   • tln-zebra-01.abcfood.app")
        print("   • printer-hq.mycompany.com")
        print("   • zebra-label.mydomain.org")
        print()
        
        # Get custom domain from user
        while True:
            domain = input("🌐 Enter your custom domain: ").strip()
            
            if not domain:
                print("❌ Domain cannot be empty")
                continue
            
            if '.' not in domain:
                print("❌ Please enter a valid domain (e.g., subdomain.yourdomain.com)")
                continue
            
            if ' ' in domain or domain != domain.lower():
                print("❌ Domain should be lowercase without spaces")
                continue
            
            # Confirm domain
            print(f"🎯 Your webhook URL will be: https://{domain}/print")
            confirm = input("✅ Is this correct? (y/n): ").strip().lower()
            
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
            print(f"❌ Failed to set domain: {message}")
            return
        
        print(f"✅ {message}")
        
        # Check authentication
        print("\n🔐 Checking Cloudflare authentication...")
        import os
        cert_path = os.path.expanduser("~/.cloudflared/cert.pem")
        
        if not os.path.exists(cert_path):
            print("❌ Cloudflare authentication required")
            print("🔗 Please run this command first:")
            print("   cloudflared tunnel login")
            print("\nThis will:")
            print("1. Open browser to Cloudflare login")
            print("2. Select your domain")
            print("3. Authorize cloudflared")
            
            auth_done = input("\n✅ Press Enter after completing authentication...")
            
            # Check again
            if not os.path.exists(cert_path):
                print("❌ Authentication still not detected. Please complete authentication first.")
                return
        
        # Setup the tunnel
        print(f"\n🔧 Setting up Named Tunnel for {domain}...")
        success, message = tunnel.setup()
        
        if success:
            print(f"✅ {message}")
            print(f"🌐 Your permanent webhook URL: https://{domain}/print")
            print("📋 Use this URL in your Odoo webhook configuration")
        else:
            print(f"❌ Setup failed: {message}")
            
            if "authentication" in message.lower():
                print("\n💡 Try running: cloudflared tunnel login")
            elif "dns" in message.lower() or "domain" in message.lower():
                print(f"\n💡 Make sure {domain} is managed by Cloudflare DNS")
                print("   1. Add domain to Cloudflare")
                print("   2. Update nameservers")
                print("   3. Verify domain is active")
    
    def _start_tunnel(self):
        """Start tunnel."""
        print("\n🔗 STARTING TUNNEL:")
        active_tunnel = self.system_status.get_active_tunnel()
        
        if active_tunnel and active_tunnel.is_active():
            print(f"✅ {active_tunnel.name.title()} tunnel already active")
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
                print("❌ Invalid option")
                input("\nPress Enter to continue...")
                return
            
            if tunnel_name in self.system_status.tunnel_providers:
                tunnel = self.system_status.tunnel_providers[tunnel_name]
                
                # Check if tunnel is configured first
                if tunnel_name == "cloudflare_named":
                    stored_config = self.system_status.db.get_tunnel_config(tunnel_name)
                    if not stored_config or not stored_config.is_configured:
                        print("❌ Named tunnel not configured yet")
                        print("💡 Please run 'Setup Tunnel' first and configure your domain")
                        input("\nPress Enter to continue...")
                        return
                
                print(f"\n🚀 Starting {tunnel_name.replace('_', ' ').title()} tunnel...")
                success, message, url = tunnel.start()
                
                if success:
                    print(f"✅ {message}")
                    if url:
                        print(f"🌐 URL: {url}")
                        if tunnel_name == "cloudflare_named":
                            print(f"🔗 Webhook URL: {url}/print")
                else:
                    print(f"❌ {message}")
            else:
                print(f"❌ {tunnel_name.title()} tunnel provider not available")
        
        input("\nPress Enter to continue...")
    
    def _stop_tunnel(self):
        """Stop tunnel."""
        print("\n⏹️  STOPPING TUNNEL...")
        active_tunnel = self.system_status.get_active_tunnel()
        
        if active_tunnel:
            success, message = active_tunnel.stop()
            print(f"{'✅' if success else '❌'} {message}")
        else:
            print("✅ No active tunnel to stop")
        
        input("\nPress Enter to continue...")
    
    def _integration_test(self):
        """Run comprehensive integration test."""
        print("\n📤 INTEGRATION TEST:")
        print("Testing complete system integration...")
        
        # Check if system is ready
        if not self.system_status.is_system_ready():
            print("❌ System not ready for integration test")
            actions = self.system_status.get_recommended_actions()
            print("   Required actions:")
            for action in actions:
                print(f"   • {action}")
        else:
            print("✅ System is ready")
            
            # Test webhook URL
            status = self.system_status.get_overall_status()
            webhook_url = status.get('webhook_url')
            
            if webhook_url:
                print(f"🔗 Webhook URL: {webhook_url}")
                
                # Create test labels
                labels = [
                    self.label_service.create_sample_label("INT-TEST-1"),
                    self.label_service.create_sample_label("INT-TEST-2")
                ]
                
                print("📤 Sending test labels via webhook...")
                active_tunnel = self.system_status.get_active_tunnel()
                
                success, message, data = self.label_service.print_labels_tunnel(
                    labels, webhook_url.replace('/print', ''), active_tunnel.name if active_tunnel else 'cloudflare'
                )
                
                if success:
                    print(f"✅ Integration test successful: {message}")
                    print("   Your Odoo webhook integration is ready!")
                else:
                    print(f"❌ Integration test failed: {message}")
            else:
                print("❌ Webhook URL not available")
        
        input("\nPress Enter to continue...")
    
    def _api_security_menu(self):
        """Handle API security and token management."""
        while True:
            print("\n🔐 API SECURITY MANAGEMENT:")
            print("1. 📋 List API Tokens")
            print("2. 🔑 Generate New Token") 
            print("3. 🗑️  Revoke Token")
            print("4. 🧪 Test Authentication")
            print("5. 📖 Show Integration Examples")
            print("6. 🔍 Show Default Token")
            print("0. ⬅️  Back to Main Menu")
            
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
                print("❌ Invalid option")
            
            input("\nPress Enter to continue...")
    
    def _list_api_tokens(self):
        """List all API tokens."""
        print("\n📋 API TOKENS:")
        
        try:
            import requests
            api_status = self.system_status.api_service.get_status()
            
            if not api_status['running']:
                print("❌ API server not running. Start it first.")
                return
            
            # Get token information
            info_url = f"http://{api_status['host']}:{api_status['port']}/auth/info"
            
            response = requests.get(info_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self._display_tokens(data['tokens'])
                
                if data['total_tokens'] == 1 and data['tokens'][0]['name'] == 'default':
                    print("\n💡 You have a default token generated at startup")
                    print("💡 Check the container logs for the token value:")
                    print("   docker logs zebra-print-control | grep '🔑 Generated'")
            else:
                print("❌ Failed to get token information")
                print("💡 Generate your first token using option 2")
                
        except Exception as e:
            print(f"❌ Error listing tokens: {e}")
    
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
        print("\n🔑 GENERATE NEW API TOKEN:")
        
        try:
            import requests
            api_status = self.system_status.api_service.get_status()
            
            if not api_status['running']:
                print("❌ API server not running. Start it first.")
                return
            
            # First check if there's a default token that can be retrieved
            info_url = f"http://{api_status['host']}:{api_status['port']}/auth/info"
            info_response = requests.get(info_url, timeout=5)
            
            if info_response.status_code == 200:
                info_data = info_response.json()
                if (info_data['total_tokens'] == 1 and 
                    info_data['tokens'][0]['name'] == 'default' and 
                    info_data['tokens'][0]['is_active']):
                    
                    print("💡 You already have a default token!")
                    print("💡 To get the token value, check the startup logs:")
                    print("   docker logs zebra-print-control | grep '🔑 Generated'")
                    
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
                
                print(f"\n✅ Token generated successfully!")
                print(f"🔑 Token: {token}")
                print(f"📝 Name: {name}")
                print(f"\n🔐 SAVE THIS TOKEN - you cannot retrieve it again!")
                print(f"\n💡 Webhook Integration Examples:")
                print(f"   Header: Authorization: Bearer {token}")
                print(f"   Query:  /print?token={token}")
                
                # Update webhook URL in tunnel status
                self._update_webhook_url_with_token(token)
                
            else:
                error_data = response.json()
                print(f"❌ Failed to generate token: {error_data.get('message', 'Unknown error')}")
                
                if "Authentication required" in error_data.get('message', ''):
                    print("\n💡 To generate additional tokens, you need an existing valid token")
                    print("💡 Get your default token from startup logs:")
                    print("   docker logs zebra-print-control | grep '🔑 Generated'")
                elif "already exists" in error_data.get('message', ''):
                    print(f"\n💡 Token name '{name}' already exists. Try a different name.")
                    print("💡 Use option 1 to see existing token names.")
                
        except Exception as e:
            print(f"❌ Error generating token: {e}")
    
    def _revoke_api_token(self):
        """Revoke an API token."""
        print("\n🗑️  REVOKE API TOKEN:")
        
        # First list existing tokens
        self._list_api_tokens()
        
        name = input("\nEnter token name to revoke: ").strip()
        if not name:
            print("❌ Token name required")
            return
        
        confirm = input(f"⚠️  Are you sure you want to revoke '{name}'? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Revocation cancelled")
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
                print(f"✅ Token '{name}' revoked successfully")
            else:
                error_data = response.json()
                print(f"❌ Failed to revoke token: {error_data.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error revoking token: {e}")
    
    def _test_authentication(self):
        """Test API authentication with user's token."""
        print("\n🧪 TEST API AUTHENTICATION:")
        
        token = input("Enter API token to test: ").strip()
        if not token:
            print("❌ Token required")
            return
        
        try:
            import requests
            api_status = self.system_status.api_service.get_status()
            
            # Test protected endpoint
            url = f"http://{api_status['host']}:{api_status['port']}/printer/status"
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print("✅ Authentication successful!")
                data = response.json()
                print(f"   Response: {data}")
            elif response.status_code == 401:
                print("❌ Authentication failed - invalid or revoked token")
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    def _show_integration_examples(self):
        """Show webhook integration examples."""
        print("\n📖 WEBHOOK INTEGRATION EXAMPLES:")
        print("=" * 50)
        
        # Get tunnel URL
        active_tunnel = self.system_status.get_active_tunnel()
        webhook_url = "https://your-domain.com"
        
        if active_tunnel:
            status = active_tunnel.get_status()
            if status.get('url'):
                webhook_url = status['url']
        
        print(f"\n🔗 Your Webhook URL: {webhook_url}/print")
        print(f"\n1️⃣ **Authorization Header (Recommended)**:")
        print(f"   URL: {webhook_url}/print")
        print(f"   Headers: Authorization: Bearer zp_your_token_here")
        print(f"   Body: {{\"labels\": [...]}}")
        
        print(f"\n2️⃣ **Query Parameter**:")
        print(f"   URL: {webhook_url}/print?token=zp_your_token_here")
        print(f"   Body: {{\"labels\": [...]}}")
        
        print(f"\n3️⃣ **Request Body**:")
        print(f"   URL: {webhook_url}/print")
        print(f"   Body: {{\"token\": \"zp_your_token_here\", \"labels\": [...]}}")
        
        print(f"\n📋 **Odoo Webhook Configuration:**")
        print(f"   • URL: {webhook_url}/print")
        print(f"   • Method: POST")
        print(f"   • Headers: Authorization: Bearer zp_your_token_here")
        print(f"   • Content-Type: application/json")
    
    def _show_default_token(self):
        """Show the default token from startup logs."""
        print("\n🔍 DEFAULT TOKEN:")
        
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
                    if "🔑 Generated default API token:" in line:
                        token_line = line
                        break
                
                if token_line:
                    token = token_line.split("🔑 Generated default API token: ")[1].strip()
                    print(f"🔑 Default Token: {token}")
                    print(f"\n💡 Use this token for webhook authentication:")
                    print(f"   Authorization: Bearer {token}")
                    
                    # Show current webhook URL with token
                    active_tunnel = self.system_status.get_active_tunnel()
                    if active_tunnel:
                        status = active_tunnel.get_status()
                        if status.get('url'):
                            webhook_url = status['url']
                            print(f"\n🌐 Ready-to-use Webhook URL:")
                            print(f"   {webhook_url}/print")
                            print(f"   Header: Authorization: Bearer {token}")
                else:
                    print("❌ Default token not found in logs")
                    print("💡 Generate a new token using option 2")
            else:
                print("❌ Failed to read container logs")
                
        except Exception as e:
            print(f"❌ Error retrieving token: {e}")
    
    def _update_webhook_url_with_token(self, token):
        """Update internal webhook URL tracking with token."""
        # This method can be enhanced to update stored webhook configurations
        pass
    
    def _get_default_token(self):
        """Get any available token for testing."""
        try:
            import subprocess
            
            # First try to get default token from container logs
            result = subprocess.run([
                'docker', 'logs', 'zebra-print-control'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                
                for line in reversed(lines):  # Check from newest to oldest
                    if "🔑 Generated default API token:" in line:
                        token = line.split("🔑 Generated default API token: ")[1].strip()
                        return token
            
            # If no default token found in logs, try to get from API info
            import requests
            api_status = self.system_status.api_service.get_status()
            
            if api_status['running']:
                info_url = f"http://{api_status['host']}:{api_status['port']}/auth/info"
                response = requests.get(info_url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    active_tokens = [t for t in data['tokens'] if t['is_active']]
                    
                    if active_tokens:
                        # Ask user to provide token since we can't retrieve the value
                        print(f"\n💡 Found {len(active_tokens)} active tokens but need token value for testing")
                        print("Available tokens:")
                        for token in active_tokens:
                            print(f"   - {token['name']}")
                        
                        user_token = input("\nEnter token value for testing (or press Enter to skip): ").strip()
                        return user_token if user_token else None
                        
        except Exception:
            pass
        
        return None