#!/usr/bin/env python3
"""
Test script untuk memverifikasi perbaikan pattern shortcode
Khususnya untuk channel shortcodes tanpa parameter
"""

import re
import asyncio
import sys
import os

# Add the syncara directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_shortcode_patterns():
    """Test shortcode pattern recognition"""
    print("🧪 Testing Shortcode Pattern Recognition...")
    
    # New pattern from ai_handler.py
    shortcode_pattern = r'\[([A-Z]+:[A-Z_]+)(?::([^\]]*))?\]'
    
    # Test cases
    test_cases = [
        # Channel shortcodes without params
        "[CHANNEL:START]",
        "[CHANNEL:STOP]", 
        "[CHANNEL:STATUS]",
        "[CHANNEL:SCHEDULE]",
        "[CHANNEL:STATS]",
        
        # Channel shortcodes with params
        "[CHANNEL:POST:daily_tips]",
        "[CHANNEL:POST:fun_facts]",
        
        # Other shortcodes with params
        "[IMAGE:GEN:cute cat]",
        "[USER:PROMOTE:123456]",
        "[GROUP:PIN_MESSAGE:789]",
        
        # Other shortcodes without params
        "[USERBOT:STATUS]",
        "[CANVAS:LIST]",
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🔹 Testing: {test_case}")
        
        matches = list(re.finditer(shortcode_pattern, test_case))
        
        if matches:
            match = matches[0]
            shortcode_name = match.group(1).strip()
            params = match.group(2)
            
            if params is None:
                params_str = ""
            else:
                params_str = params.strip()
            
            print(f"   ✅ Match found!")
            print(f"   📝 Shortcode: {shortcode_name}")
            print(f"   📋 Params: '{params_str}'")
            
            results.append(True)
        else:
            print(f"   ❌ No match found!")
            results.append(False)
    
    return results

def test_process_shortcode_pattern():
    """Test process_shortcode.py pattern"""
    print("\n🔧 Testing process_shortcode.py Pattern...")
    
    # New pattern from process_shortcode.py
    pattern = r'\[([^:]+):([^:\]]+)(?::([^\]]*))?\]'
    
    test_cases = [
        "[CHANNEL:START]",
        "[CHANNEL:POST:daily_tips]", 
        "[IMAGE:GEN:cute cat in space]",
        "[USER:INFO]",
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🔹 Testing: {test_case}")
        
        matches = list(re.finditer(pattern, test_case))
        
        if matches:
            match = matches[0]
            category = match.group(1)
            action = match.group(2)
            params = match.group(3)
            
            if params is None:
                params = ""
            
            shortcode_key = f"{category}:{action}"
            
            print(f"   ✅ Match found!")
            print(f"   📝 Category: {category}")
            print(f"   ⚡ Action: {action}")
            print(f"   📋 Params: '{params}'")
            print(f"   🔑 Shortcode Key: {shortcode_key}")
            
            results.append(True)
        else:
            print(f"   ❌ No match found!")
            results.append(False)
    
    return results

async def test_shortcode_registry():
    """Test if channel shortcodes are in registry"""
    print("\n🔗 Testing Shortcode Registry...")
    
    try:
        from syncara.shortcode import registry
        
        # Channel shortcodes to check
        channel_shortcodes = [
            'CHANNEL:START',
            'CHANNEL:STOP',
            'CHANNEL:STATUS',
            'CHANNEL:SCHEDULE',
            'CHANNEL:STATS',
            'CHANNEL:POST'
        ]
        
        results = []
        
        print(f"📊 Total shortcodes in registry: {len(registry.shortcodes)}")
        
        for shortcode in channel_shortcodes:
            if shortcode in registry.shortcodes:
                print(f"   ✅ {shortcode} - Found in registry")
                results.append(True)
            else:
                print(f"   ❌ {shortcode} - NOT found in registry")
                results.append(False)
        
        # Show all CHANNEL shortcodes in registry
        found_channel_shortcodes = [key for key in registry.shortcodes.keys() if key.startswith('CHANNEL:')]
        print(f"\n📢 Found CHANNEL shortcodes in registry: {len(found_channel_shortcodes)}")
        for shortcode in found_channel_shortcodes:
            print(f"   🔹 {shortcode}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error testing registry: {str(e)}")
        return [False]

async def test_channel_shortcode_execution():
    """Test channel shortcode execution simulation"""
    print("\n🚀 Testing Channel Shortcode Execution Simulation...")
    
    try:
        from syncara.shortcode.channel_management import channel_shortcode
        
        # Mock objects
        class MockClient:
            def __init__(self):
                self.messages = []
                
            async def send_message(self, **kwargs):
                self.messages.append(kwargs)
                print(f"📨 Mock message sent to chat {kwargs.get('chat_id')}: {kwargs.get('text', '')[:50]}...")
                return type('Message', (), {'id': 123})()
        
        class MockMessage:
            def __init__(self):
                self.id = 123
                self.chat = type('Chat', (), {'id': 456})()
                self.from_user = type('User', (), {'id': 1})()  # Set as owner
        
        mock_client = MockClient()
        mock_message = MockMessage()
        
        # Test channel shortcode handlers
        test_shortcodes = [
            ('CHANNEL:STATUS', ''),
            ('CHANNEL:SCHEDULE', ''),
        ]
        
        results = []
        
        for shortcode_name, params in test_shortcodes:
            print(f"\n🔹 Testing {shortcode_name}...")
            
            try:
                if shortcode_name in channel_shortcode.handlers:
                    handler = channel_shortcode.handlers[shortcode_name]
                    result = await handler(mock_client, mock_message, params)
                    
                    if result:
                        print(f"   ✅ {shortcode_name} executed successfully")
                        print(f"   📨 Messages sent: {len(mock_client.messages)}")
                        results.append(True)
                    else:
                        print(f"   ⚠️ {shortcode_name} returned False")
                        results.append(False)
                else:
                    print(f"   ❌ {shortcode_name} handler not found")
                    results.append(False)
                    
            except Exception as e:
                print(f"   ❌ {shortcode_name} execution error: {str(e)}")
                results.append(False)
        
        return results
        
    except Exception as e:
        print(f"❌ Error testing channel shortcode execution: {str(e)}")
        return [False]

async def main():
    """Main test function"""
    print("🚀 Starting Shortcode Pattern Fix Tests...")
    print("=" * 70)
    
    # Test pattern recognition
    print("\n📋 PATTERN RECOGNITION TESTS")
    print("-" * 40)
    pattern_results = test_shortcode_patterns()
    
    print("\n📋 PROCESS SHORTCODE PATTERN TESTS")
    print("-" * 40)  
    process_pattern_results = test_process_shortcode_pattern()
    
    # Test registry
    print("\n📋 REGISTRY TESTS")
    print("-" * 40)
    registry_results = await test_shortcode_registry()
    
    # Test execution
    print("\n📋 EXECUTION TESTS")
    print("-" * 40)
    execution_results = await test_channel_shortcode_execution()
    
    # Summary
    all_results = pattern_results + process_pattern_results + registry_results + execution_results
    
    print("\n" + "=" * 70)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(all_results)}")
    print(f"❌ Failed: {len(all_results) - sum(all_results)}")
    print(f"📈 Success Rate: {(sum(all_results) / len(all_results)) * 100:.1f}%")
    
    if all(all_results):
        print("\n🎉 All tests passed! Shortcode pattern fix is working.")
        print("\n📋 What was fixed:")
        print("1. ✅ Pattern now supports shortcodes without parameters")
        print("2. ✅ [CHANNEL:START], [CHANNEL:STATUS], etc. should work now")
        print("3. ✅ Both [SHORTCODE] and [SHORTCODE:params] formats supported")
        print("4. ✅ Registry contains channel shortcodes")
        print("5. ✅ Channel shortcode handlers work correctly")
        
        print("\n🚀 Ready to test with real bot!")
        print("Now try: [CHANNEL:START], [CHANNEL:STATUS], [CHANNEL:SCHEDULE]")
    else:
        print("\n⚠️ Some tests failed. Channel shortcodes may still have issues.")
        
        failed_categories = []
        if not all(pattern_results):
            failed_categories.append("Pattern Recognition")
        if not all(process_pattern_results):
            failed_categories.append("Process Pattern")
        if not all(registry_results):
            failed_categories.append("Registry")
        if not all(execution_results):
            failed_categories.append("Execution")
            
        print(f"❌ Failed categories: {', '.join(failed_categories)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main()) 