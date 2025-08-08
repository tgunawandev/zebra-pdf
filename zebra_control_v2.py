#!/usr/bin/env python3
"""
Zebra Print Control System v2.0
Modern, modular architecture for Zebra printer integration.

Usage:
    python3 zebra_control_v2.py

Features:
- Modular architecture with proper separation of concerns
- Clean interfaces and dependency injection
- Support for multiple tunnel providers (Cloudflare, Ngrok)
- Comprehensive system status monitoring
- Integration testing capabilities
- Focused UI layer separated from business logic
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from zebra_print.main import main

if __name__ == "__main__":
    main()