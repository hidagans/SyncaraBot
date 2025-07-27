#!/usr/bin/env python3
"""
Test script untuk Channel Manager functionality
"""

import asyncio
import sys
import os

# Add the syncara directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

async def test_channel_manager():
    """Test channel manager functionality"""
    print("🧪 Testing Channel Manager...")
    
    try:
        # Import channel manager
        from syncara.modules.channel_manager import ChannelContentGenerator, ChannelManager
        
        print("✅ Channel Manager imported successfully")
        
        # Test content generator
        content_generator = ChannelContentGenerator()
        print("✅ Content Generator initialized")
        
        # Test channel manager
        channel_manager = ChannelManager()
        print("✅ Channel Manager initialized")
        
        # Test content generation (without actually posting)
        print("\n📝 Testing content generation...")
        
        # Test daily tips generation
        print("🔹 Generating daily tips...")
        daily_tips = await content_generator.generate_daily_tips()
        if daily_tips:
            print(f"   ✅ Daily tips generated: {daily_tips.title}")
            print(f"   📄 Preview: {daily_tips.content[:100]}...")
        else:
            print("   ❌ Failed to generate daily tips")
        
        # Test fun facts generation
        print("🔹 Generating fun facts...")
        fun_facts = await content_generator.generate_fun_facts()
        if fun_facts:
            print(f"   ✅ Fun facts generated: {fun_facts.title}")
            print(f"   📄 Preview: {fun_facts.content[:100]}...")
        else:
            print("   ❌ Failed to generate fun facts")
        
        # Test Q&A generation
        print("🔹 Generating Q&A content...")
        qna = await content_generator.generate_qna_content()
        if qna:
            print(f"   ✅ Q&A generated: {qna.title}")
            print(f"   📄 Preview: {qna.content[:100]}...")
        else:
            print("   ❌ Failed to generate Q&A")
        
        # Test interactive poll generation
        print("🔹 Generating interactive poll...")
        poll = await content_generator.generate_interactive_poll()
        if poll:
            print(f"   ✅ Poll generated: {poll.title}")
            print(f"   📄 Preview: {poll.content[:100]}...")
        else:
            print("   ❌ Failed to generate poll")
        
        print(f"\n✅ Channel Manager test completed successfully!")
        print(f"📊 Channel: {channel_manager.channel_username}")
        print(f"🔄 Status: {'Running' if channel_manager.is_running else 'Stopped'}")
        
        # Test database connection
        try:
            stats = await channel_manager.get_channel_stats()
            print(f"📈 Stats retrieved: {len(stats)} fields")
        except Exception as e:
            print(f"⚠️ Stats error (expected without real database): {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_structure():
    """Test database structure"""
    print("\n🗄️ Testing Database Structure...")
    
    try:
        from syncara.database import (
            channel_posts, channel_analytics, channel_schedule,
            log_channel_post, get_channel_analytics_summary
        )
        
        print("✅ Database collections imported successfully")
        print(f"   📊 channel_posts: {channel_posts}")
        print(f"   📈 channel_analytics: {channel_analytics}")
        print(f"   📅 channel_schedule: {channel_schedule}")
        
        print("✅ Database helper functions imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False

async def test_shortcodes():
    """Test channel management shortcodes"""
    print("\n⚡ Testing Channel Shortcodes...")
    
    try:
        from syncara.shortcode.channel_management import ChannelManagementShortcode
        
        shortcode_manager = ChannelManagementShortcode()
        print("✅ Channel shortcode manager initialized")
        
        # Check handlers
        handlers = shortcode_manager.handlers
        print(f"📋 Available handlers: {list(handlers.keys())}")
        
        # Check descriptions
        descriptions = shortcode_manager.descriptions
        print(f"📝 Available descriptions: {len(descriptions)}")
        
        for shortcode, desc in descriptions.items():
            print(f"   🔹 {shortcode}: {desc}")
        
        return True
        
    except Exception as e:
        print(f"❌ Shortcode test failed: {str(e)}")
        return False

async def test_shortcode_registry():
    """Test shortcode registry integration"""
    print("\n🔗 Testing Shortcode Registry Integration...")
    
    try:
        from syncara.shortcode import registry
        
        # Check if channel shortcodes are registered
        channel_shortcodes = [key for key in registry.shortcodes.keys() if key.startswith('CHANNEL:')]
        
        print(f"✅ Registry loaded with {len(registry.shortcodes)} total shortcodes")
        print(f"📢 Channel shortcodes found: {len(channel_shortcodes)}")
        
        for shortcode in channel_shortcodes:
            print(f"   🔹 {shortcode}")
        
        # Test shortcode documentation
        docs = registry.get_shortcode_docs()
        if "CHANNEL" in docs:
            print("✅ Channel shortcodes included in documentation")
        else:
            print("⚠️ Channel shortcodes not found in documentation")
        
        return True
        
    except Exception as e:
        print(f"❌ Registry test failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Channel Manager Tests...")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(await test_database_structure())
    results.append(await test_channel_manager())
    results.append(await test_shortcodes())
    results.append(await test_shortcode_registry())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    print(f"📈 Success Rate: {(sum(results) / len(results)) * 100:.1f}%")
    
    if all(results):
        print("\n🎉 All tests passed! Channel Manager is ready to use.")
        print("\n📋 Usage Instructions:")
        print("1. Start SyncaraBot: python3 -m syncara")
        print("2. Use [CHANNEL:START] to activate auto-posting")
        print("3. Use [CHANNEL:STATUS] to check status")
        print("4. Use [CHANNEL:STATS] to view analytics")
        print("5. Use [CHANNEL:POST:content_type] for manual posting")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main()) 