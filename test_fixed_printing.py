#!/usr/bin/env python3
"""
Test script for the fixed printing functionality.
"""

from pdf_to_zpl import convert_text_to_zpl, print_zpl_to_zebra

def test_consistent_text_sizing():
    """Test that all text uses consistent sizing."""
    
    # Sample data that mimics your PDF structure
    test_text_lines = [
        "W-CPN/OUT/00001",
        "12/04/22", 
        "01010101160",
        "W-CPN/OUT/00002",
        "12/04/22",
        "01010101161"
    ]
    
    print("🧪 Testing consistent text sizing...")
    zpl = convert_text_to_zpl(test_text_lines)
    
    if zpl:
        print("✅ ZPL generated successfully")
        print("\n📋 Generated ZPL preview:")
        print("-" * 40)
        print(zpl)
        print("-" * 40)
        
        # Check for consistent text sizing (all should be 16,16)
        font_commands = [line for line in zpl.split('\n') if '^A0N' in line]
        sizes = []
        for cmd in font_commands:
            if '^A0N,' in cmd:
                parts = cmd.split('^A0N,')[1].split('^FD')[0]
                sizes.append(parts)
        
        print(f"\n📏 Font sizes found: {sizes}")
        
        if all(size == '16,16' for size in sizes):
            print("✅ All text uses consistent 16x16 font size")
        else:
            print("❌ Inconsistent font sizes detected")
            
        return zpl
    else:
        print("❌ ZPL generation failed")
        return None

def main():
    print("🏷️  Testing Fixed Label Printing")
    print("=" * 40)
    
    # Test the fixes
    zpl = test_consistent_text_sizing()
    
    if zpl:
        print(f"\n🖨️  Ready to print test labels")
        print("📝 Key improvements:")
        print("   • All text now uses consistent 16x16 font size")
        print("   • Added print speed control (^PR2)")
        print("   • Added media darkness setting (^MD5)")  
        print("   • Improved label positioning commands")
        print("   • Added printer calibration commands")
        
        choice = input("\n❓ Print test labels now? (y/N): ").lower()
        if choice == 'y':
            success = print_zpl_to_zebra(zpl)
            if success:
                print("✅ Test labels sent to printer!")
                print("📋 Check the printed labels for:")
                print("   • Consistent text size")
                print("   • Proper alignment")
                print("   • Correct QR code positioning")
            else:
                print("❌ Printing failed")

if __name__ == "__main__":
    main()