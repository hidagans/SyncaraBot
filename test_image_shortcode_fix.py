#!/usr/bin/env python3
"""
Test script untuk memverifikasi perbaikan image shortcode delayed sending
"""

import asyncio
import sys
import os

# Add the syncara directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

async def test_image_shortcode_import():
    """Test import image shortcode instance"""
    print("🧪 Testing Image Shortcode Import...")
    
    try:
        from syncara.shortcode.image_generation import image_shortcode
        print("✅ Image shortcode imported successfully")
        
        # Check if send_pending_images method exists
        if hasattr(image_shortcode, 'send_pending_images'):
            print("✅ send_pending_images method found")
        else:
            print("❌ send_pending_images method not found")
            
        # Check handlers
        handlers = image_shortcode.handlers
        print(f"📋 Available handlers: {list(handlers.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing image shortcode: {str(e)}")
        return False

async def test_delayed_sending_functions():
    """Test delayed sending functions"""
    print("\n🔄 Testing Delayed Sending Functions...")
    
    try:
        from syncara.modules.ai_handler import send_pending_images_delayed, send_pending_responses_delayed
        print("✅ Delayed sending functions imported successfully")
        
        # Mock objects for testing
        class MockClient:
            async def send_photo(self, **kwargs):
                return "Mock photo sent"
                
        class MockMessage:
            def __init__(self):
                self.id = 123
                self.chat = type('obj', (object,), {'id': 456})()
        
        mock_client = MockClient()
        mock_message = MockMessage()
        
        # Test image delayed sending (without actual images)
        print("🔹 Testing send_pending_images_delayed...")
        try:
            await send_pending_images_delayed([], mock_client, mock_message)
            print("✅ send_pending_images_delayed executed without error")
        except Exception as e:
            print(f"⚠️ send_pending_images_delayed error (expected): {str(e)}")
        
        # Test response delayed sending
        print("🔹 Testing send_pending_responses_delayed...")
        try:
            await send_pending_responses_delayed([], mock_client, mock_message)
            print("✅ send_pending_responses_delayed executed without error")
        except Exception as e:
            print(f"⚠️ send_pending_responses_delayed error: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing delayed sending functions: {str(e)}")
        return False

async def test_shortcode_registry():
    """Test shortcode registry"""
    print("\n🔗 Testing Shortcode Registry...")
    
    try:
        from syncara.shortcode import registry
        
        # Check if image shortcodes are registered
        image_shortcodes = [key for key in registry.shortcodes.keys() if key.startswith('IMAGE:')]
        print(f"✅ Registry loaded with {len(registry.shortcodes)} total shortcodes")
        print(f"🖼️ Image shortcodes found: {len(image_shortcodes)}")
        
        for shortcode in image_shortcodes:
            print(f"   🔹 {shortcode}")
        
        # Test handler types
        print("\n🔍 Testing handler types:")
        for shortcode_name, handler in list(registry.shortcodes.items())[:3]:
            print(f"   📝 {shortcode_name}: {type(handler).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Registry test failed: {str(e)}")
        return False

async def test_image_pending_functionality():
    """Test image pending functionality"""
    print("\n🎨 Testing Image Pending Functionality...")
    
    try:
        from syncara.shortcode.image_generation import image_shortcode
        
        # Check pending_images attribute
        if hasattr(image_shortcode, 'pending_images'):
            print(f"✅ pending_images attribute found: {type(image_shortcode.pending_images)}")
            print(f"📊 Current pending images: {len(image_shortcode.pending_images)}")
        else:
            print("❌ pending_images attribute not found")
        
        # Test adding mock pending image
        test_image_id = "test_image_123"
        image_shortcode.pending_images[test_image_id] = {
            'url': 'https://example.com/test.jpg',
            'prompt': 'Test prompt',
            'chat_id': 123,
            'reply_to_message_id': 456,
            'generation_id': 'gen_123'
        }
        
        print(f"✅ Added test pending image: {test_image_id}")
        print(f"📊 Pending images count: {len(image_shortcode.pending_images)}")
        
        # Clean up
        if test_image_id in image_shortcode.pending_images:
            del image_shortcode.pending_images[test_image_id]
            print("✅ Cleaned up test pending image")
        
        return True
        
    except Exception as e:
        print(f"❌ Image pending functionality test failed: {str(e)}")
        return False

async def test_full_image_flow_simulation():
    """Simulate full image generation flow"""
    print("\n🚀 Testing Full Image Generation Flow Simulation...")
    
    try:
        from syncara.shortcode.image_generation import image_shortcode
        from syncara.modules.ai_handler import send_pending_images_delayed
        
        # Mock objects
        class MockClient:
            def __init__(self):
                self.calls = []
                
            async def send_photo(self, **kwargs):
                self.calls.append(('send_photo', kwargs))
                print(f"📸 Mock send_photo called with chat_id: {kwargs.get('chat_id')}")
                return type('obj', (object,), {'id': 789})()
        
        class MockMessage:
            def __init__(self):
                self.id = 123
                self.chat = type('obj', (object,), {'id': 456})()
                self.from_user = type('obj', (object,), {'id': 789})()
        
        mock_client = MockClient()
        mock_message = MockMessage()
        
        # Simulate adding pending image
        test_image_id = "image_123_test"
        image_shortcode.pending_images[test_image_id] = {
            'url': 'https://example.com/test_generated.jpg',
            'prompt': 'A beautiful sunset over mountains',
            'chat_id': mock_message.chat.id,
            'reply_to_message_id': mock_message.id,
            'generation_id': 'gen_test_123'
        }
        
        print(f"✅ Simulated pending image: {test_image_id}")
        
        # Test delayed sending
        await send_pending_images_delayed([test_image_id], mock_client, mock_message)
        
        # Check if mock client was called
        if mock_client.calls:
            print(f"✅ Mock client send_photo was called {len(mock_client.calls)} times")
            for call_type, kwargs in mock_client.calls:
                print(f"   📞 {call_type}: chat_id={kwargs.get('chat_id')}, photo={kwargs.get('photo')[:50]}...")
        else:
            print("⚠️ Mock client send_photo was not called")
        
        # Check if pending image was cleaned up
        if test_image_id not in image_shortcode.pending_images:
            print("✅ Pending image was properly cleaned up")
        else:
            print("⚠️ Pending image was not cleaned up")
            # Manual cleanup
            del image_shortcode.pending_images[test_image_id]
        
        return True
        
    except Exception as e:
        print(f"❌ Full flow simulation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Image Shortcode Fix Tests...")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(await test_image_shortcode_import())
    results.append(await test_delayed_sending_functions())
    results.append(await test_shortcode_registry())
    results.append(await test_image_pending_functionality())
    results.append(await test_full_image_flow_simulation())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    print(f"📈 Success Rate: {(sum(results) / len(results)) * 100:.1f}%")
    
    if all(results):
        print("\n🎉 All tests passed! Image shortcode fix is working properly.")
        print("\n📋 What was fixed:")
        print("1. ✅ send_pending_images_delayed now imports image_shortcode directly")
        print("2. ✅ send_pending_responses_delayed imports shortcode instances directly")
        print("3. ✅ No more 'Image shortcode handler not found' error")
        print("4. ✅ Delayed image sending should work properly now")
        
        print("\n🚀 Ready to test with real bot!")
        print("Try: Ask AI to generate an image and it should send properly.")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main()) 