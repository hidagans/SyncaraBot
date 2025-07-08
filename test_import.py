#!/usr/bin/env python3
"""
Test script untuk verifikasi import Pyrogram compatibility
"""

import sys
import traceback

def test_import():
    try:
        print("🔍 Testing Pyrogram compatibility...")
        
        # Test import pyrogram
        print("  ✓ Importing pyrogram...")
        import pyrogram
        print(f"  ✓ Pyrogram version: {pyrogram.__version__}")
        
        # Test import compatibility layer
        print("  ✓ Importing compatibility layer...")
        from syncara.modules.pyrogram_compatibility import (
            AVAILABLE_TYPES, 
            print_compatibility_info
        )
        print("  ✓ Compatibility layer imported successfully")
        
        # Print compatibility info
        print("\n📋 Compatibility Information:")
        print_compatibility_info()
        
        # Test import main modules
        print("\n🔧 Testing main module imports...")
        from syncara.modules.pyrogram_integration import CompletePyrogramMethods
        print("  ✓ pyrogram_integration imported")
        
        from syncara.modules.pyrogram_methods import PyrogramMethods
        print("  ✓ pyrogram_methods imported")
        
        from syncara.modules.pyrogram_chat_methods import ChatMethods
        print("  ✓ pyrogram_chat_methods imported")
        
        from syncara.modules.pyrogram_callback_methods import CallbackMethods
        print("  ✓ pyrogram_callback_methods imported")
        
        print("\n✅ All imports successful!")
        
        # Show missing types summary
        missing_types = [type_name for type_name, available in AVAILABLE_TYPES.items() if not available]
        if missing_types:
            print(f"\n⚠️  Missing types (using fallbacks): {', '.join(missing_types)}")
        else:
            print("\n🎉 All Pyrogram types available!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_basic_functionality():
    try:
        print("\n🧪 Testing basic functionality...")
        
        from syncara.modules.pyrogram_compatibility import (
            create_chat_permissions,
            create_bot_command,
            create_inline_keyboard_markup,
            AVAILABLE_TYPES
        )
        
        # Test chat permissions
        permissions = create_chat_permissions(can_send_messages=True, can_send_media_messages=False)
        print(f"  ✓ Chat permissions: {type(permissions)}")
        
        # Test bot command
        command = create_bot_command("test", "Test command")
        print(f"  ✓ Bot command: {type(command)}")
        
        # Test inline keyboard
        keyboard = create_inline_keyboard_markup([[{"text": "Test", "callback_data": "test"}]])
        print(f"  ✓ Inline keyboard: {type(keyboard)}")
        
        print("✅ Basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 SyncaraBot Pyrogram Compatibility Test")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_import():
        success = False
    
    # Test basic functionality
    if not test_basic_functionality():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! SyncaraBot should work with your Pyrogram version.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    sys.exit(0 if success else 1) 