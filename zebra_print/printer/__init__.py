"""
Printer services module.
Contains printer service implementations.
"""

import platform
from .base import PrinterService
from .zebra_cups import ZebraCUPSPrinter
from .zebra_windows import ZebraWindowsPrinter

def get_zebra_printer(printer_name: str = None) -> PrinterService:
    """Get the appropriate Zebra printer service for the current platform."""
    if platform.system() == "Windows":
        default_name = printer_name or "ZDesigner ZD230-203dpi ZPL"
        return ZebraWindowsPrinter(default_name)
    else:
        default_name = printer_name or "ZTC-ZD230-203dpi-ZPL"
        return ZebraCUPSPrinter(default_name)

__all__ = ['PrinterService', 'ZebraCUPSPrinter', 'ZebraWindowsPrinter', 'get_zebra_printer']