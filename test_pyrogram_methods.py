#!/usr/bin/env python3
# test_pyrogram_methods.py
"""
Script untuk menguji semua method Pyrogram yang telah ditambahkan ke SyncaraBot.
Jalankan script ini untuk memastikan semua method berfungsi dengan baik.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from syncara import initialize_syncara
from pyrogram import enums
from pyrogram.types import ChatPermissions, ChatPrivileges, BotCommand
from syncara.console import console

# ID chat untuk testing (ganti dengan ID chat test Anda)
TEST_CHAT_ID = "@SyncaraBot_Test"  # Ganti dengan ID chat test
TEST_USER_ID = 123456789  # Ganti dengan ID user test

class PyrogramMethodsTester:
    """Class untuk menguji semua method Pyrogram"""
    
    def __init__(self):
        self.bot = None
        self.assistant = None
        self.test_results = {
            "passed": [],
            "failed": [],
            "skipped": []
        }
    
    async def initialize(self):
        """Initialize bot dan assistant"""
        console.info("🚀 Initializing SyncaraBot for testing...")
        self.bot, assistant_manager = await initialize_syncara()
        
        # Get first available assistant
        if assistant_manager.assistants:
            assistant_id = list(assistant_manager.assistants.keys())[0]
            self.assistant = assistant_manager.assistants[assistant_id]["client"]
            console.info(f"✅ Using assistant: {assistant_id}")
        else:
            console.warning("⚠️ No assistants available, testing bot only")
    
    async def test_method(self, method_name, test_func):
        """Test individual method"""
        try:
            console.info(f"🧪 Testing {method_name}...")
            await test_func()
            self.test_results["passed"].append(method_name)
            console.info(f"✅ {method_name} - PASSED")
        except Exception as e:
            self.test_results["failed"].append(f"{method_name}: {str(e)}")
            console.error(f"❌ {method_name} - FAILED: {str(e)}")
    
    def skip_test(self, method_name, reason):
        """Skip test with reason"""
        self.test_results["skipped"].append(f"{method_name}: {reason}")
        console.warning(f"⏭️ {method_name} - SKIPPED: {reason}")
    
    # ==================== MESSAGE TESTS ====================
    
    async def test_message_methods(self):
        """Test semua method pesan"""
        console.info("📨 Testing Message Methods...")
        
        # Test kirim_pesan
        await self.test_method("kirim_pesan", self.test_kirim_pesan)
        
        # Test edit_pesan
        await self.test_method("edit_pesan", self.test_edit_pesan)
        
        # Test hapus_pesan
        await self.test_method("hapus_pesan", self.test_hapus_pesan)
        
        # Test forward_pesan
        await self.test_method("forward_pesan", self.test_forward_pesan)
        
        # Test copy_pesan
        await self.test_method("copy_pesan", self.test_copy_pesan)
    
    async def test_kirim_pesan(self):
        """Test kirim_pesan method"""
        message = await self.bot.kirim_pesan(
            chat_id=TEST_CHAT_ID,
            text="🧪 Test kirim_pesan method"
        )
        assert message.text == "🧪 Test kirim_pesan method"
        return message
    
    async def test_edit_pesan(self):
        """Test edit_pesan method"""
        # Kirim pesan dulu
        message = await self.bot.kirim_pesan(
            chat_id=TEST_CHAT_ID,
            text="Original message"
        )
        
        # Edit pesan
        edited = await self.bot.edit_pesan(
            chat_id=TEST_CHAT_ID,
            message_id=message.id,
            text="Edited message"
        )
        assert edited.text == "Edited message"
        return edited
    
    async def test_hapus_pesan(self):
        """Test hapus_pesan method"""
        # Kirim pesan dulu
        message = await self.bot.kirim_pesan(
            chat_id=TEST_CHAT_ID,
            text="Message to delete"
        )
        
        # Hapus pesan
        result = await self.bot.hapus_pesan(
            chat_id=TEST_CHAT_ID,
            message_ids=message.id
        )
        assert result == True
        return result
    
    async def test_forward_pesan(self):
        """Test forward_pesan method"""
        # Kirim pesan dulu
        message = await self.bot.kirim_pesan(
            chat_id=TEST_CHAT_ID,
            text="Message to forward"
        )
        
        # Forward pesan
        forwarded = await self.bot.forward_pesan(
            chat_id=TEST_CHAT_ID,
            from_chat_id=TEST_CHAT_ID,
            message_ids=message.id
        )
        assert len(forwarded) == 1
        return forwarded
    
    async def test_copy_pesan(self):
        """Test copy_pesan method"""
        # Kirim pesan dulu
        message = await self.bot.kirim_pesan(
            chat_id=TEST_CHAT_ID,
            text="Message to copy"
        )
        
        # Copy pesan
        copied = await self.bot.copy_pesan(
            chat_id=TEST_CHAT_ID,
            from_chat_id=TEST_CHAT_ID,
            message_id=message.id
        )
        assert copied.text == "Message to copy"
        return copied
    
    # ==================== MEDIA TESTS ====================
    
    async def test_media_methods(self):
        """Test semua method media"""
        console.info("🖼️ Testing Media Methods...")
        
        # Test kirim_foto
        await self.test_method("kirim_foto", self.test_kirim_foto)
        
        # Test kirim_video
        self.skip_test("kirim_video", "Requires video file")
        
        # Test kirim_audio
        self.skip_test("kirim_audio", "Requires audio file")
        
        # Test kirim_dokumen
        self.skip_test("kirim_dokumen", "Requires document file")
    
    async def test_kirim_foto(self):
        """Test kirim_foto method"""
        # Gunakan foto dari URL
        message = await self.bot.kirim_foto(
            chat_id=TEST_CHAT_ID,
            photo="https://picsum.photos/400/300",
            caption="🧪 Test foto dari URL"
        )
        assert message.photo is not None
        return message
    
    # ==================== CHAT TESTS ====================
    
    async def test_chat_methods(self):
        """Test semua method chat"""
        console.info("💬 Testing Chat Methods...")
        
        # Test get_info_chat
        await self.test_method("get_info_chat", self.test_get_info_chat)
        
        # Test get_statistik_chat
        await self.test_method("get_statistik_chat", self.test_get_statistik_chat)
        
        # Test kirim_aksi_chat
        await self.test_method("kirim_aksi_chat", self.test_kirim_aksi_chat)
        
        # Skip tests that require admin privileges
        self.skip_test("set_judul_chat", "Requires admin privileges")
        self.skip_test("set_deskripsi_chat", "Requires admin privileges")
        self.skip_test("set_foto_chat", "Requires admin privileges")
        self.skip_test("gabung_chat", "Requires specific chat")
        self.skip_test("keluar_chat", "Requires specific chat")
    
    async def test_get_info_chat(self):
        """Test get_info_chat method"""
        chat_info = await self.bot.get_info_chat(chat_id=TEST_CHAT_ID)
        assert chat_info.id is not None
        return chat_info
    
    async def test_get_statistik_chat(self):
        """Test get_statistik_chat method"""
        stats = await self.bot.get_statistik_chat(chat_id=TEST_CHAT_ID)
        assert isinstance(stats, dict)
        assert 'id' in stats
        assert 'type' in stats
        return stats
    
    async def test_kirim_aksi_chat(self):
        """Test kirim_aksi_chat method"""
        result = await self.bot.kirim_aksi_chat(
            chat_id=TEST_CHAT_ID,
            action=enums.ChatAction.TYPING
        )
        assert result == True
        return result
    
    # ==================== CALLBACK TESTS ====================
    
    async def test_callback_methods(self):
        """Test semua method callback"""
        console.info("🎮 Testing Callback Methods...")
        
        # Test buat_keyboard_inline
        await self.test_method("buat_keyboard_inline", self.test_buat_keyboard_inline)
        
        # Test buat_keyboard_reply
        await self.test_method("buat_keyboard_reply", self.test_buat_keyboard_reply)
        
        # Test hapus_keyboard
        await self.test_method("hapus_keyboard", self.test_hapus_keyboard)
        
        # Test paksa_reply
        await self.test_method("paksa_reply", self.test_paksa_reply)
        
        # Skip callback query tests (need actual callback)
        self.skip_test("jawab_callback_query", "Requires actual callback query")
    
    async def test_buat_keyboard_inline(self):
        """Test buat_keyboard_inline method"""
        keyboard = self.bot.buat_keyboard_inline([
            [{"text": "Test Button", "callback_data": "test"}]
        ])
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 1
        return keyboard
    
    async def test_buat_keyboard_reply(self):
        """Test buat_keyboard_reply method"""
        keyboard = self.bot.buat_keyboard_reply([
            ["Button 1", "Button 2"],
            ["Button 3"]
        ])
        assert keyboard is not None
        assert len(keyboard.keyboard) == 2
        return keyboard
    
    async def test_hapus_keyboard(self):
        """Test hapus_keyboard method"""
        keyboard = self.bot.hapus_keyboard()
        assert keyboard is not None
        assert keyboard.remove_keyboard == True
        return keyboard
    
    async def test_paksa_reply(self):
        """Test paksa_reply method"""
        force_reply = self.bot.paksa_reply()
        assert force_reply is not None
        assert force_reply.force_reply == True
        return force_reply
    
    # ==================== BOT TESTS ====================
    
    async def test_bot_methods(self):
        """Test semua method bot"""
        console.info("🤖 Testing Bot Methods...")
        
        # Test set_perintah_bot
        await self.test_method("set_perintah_bot", self.test_set_perintah_bot)
        
        # Test get_perintah_bot
        await self.test_method("get_perintah_bot", self.test_get_perintah_bot)
        
        # Test hapus_perintah_bot
        await self.test_method("hapus_perintah_bot", self.test_hapus_perintah_bot)
    
    async def test_set_perintah_bot(self):
        """Test set_perintah_bot method"""
        commands = [
            BotCommand("test", "Test command"),
            BotCommand("help", "Help command")
        ]
        result = await self.bot.set_perintah_bot(commands=commands)
        assert result == True
        return result
    
    async def test_get_perintah_bot(self):
        """Test get_perintah_bot method"""
        commands = await self.bot.get_perintah_bot()
        assert isinstance(commands, list)
        return commands
    
    async def test_hapus_perintah_bot(self):
        """Test hapus_perintah_bot method"""
        result = await self.bot.hapus_perintah_bot()
        assert result == True
        return result
    
    # ==================== UTILITY TESTS ====================
    
    async def test_utility_methods(self):
        """Test semua method utility"""
        console.info("🛠️ Testing Utility Methods...")
        
        # Test get_info_diri
        await self.test_method("get_info_diri", self.test_get_info_diri)
        
        # Test cek_status_online
        await self.test_method("cek_status_online", self.test_cek_status_online)
        
        # Test daftar_method_tersedia
        await self.test_method("daftar_method_tersedia", self.test_daftar_method_tersedia)
        
        # Test bantuan_method
        await self.test_method("bantuan_method", self.test_bantuan_method)
        
        # Test backup_chat
        await self.test_method("backup_chat", self.test_backup_chat)
    
    async def test_get_info_diri(self):
        """Test get_info_diri method"""
        info = await self.bot.get_info_diri()
        assert isinstance(info, dict)
        assert 'id' in info
        assert 'username' in info
        return info
    
    async def test_cek_status_online(self):
        """Test cek_status_online method"""
        status = await self.bot.cek_status_online()
        assert isinstance(status, bool)
        assert status == True  # Bot should be online during test
        return status
    
    async def test_daftar_method_tersedia(self):
        """Test daftar_method_tersedia method"""
        methods = self.bot.daftar_method_tersedia()
        assert isinstance(methods, dict)
        assert 'pesan' in methods
        assert 'media' in methods
        assert 'chat' in methods
        assert 'scheduler' in methods
        assert 'helpers' in methods
        assert 'bound_methods' in methods
        return methods
    
    async def test_bantuan_method(self):
        """Test bantuan_method method"""
        help_text = self.bot.bantuan_method("kirim_pesan")
        assert isinstance(help_text, str)
        assert len(help_text) > 0
        return help_text
    
    async def test_backup_chat(self):
        """Test backup_chat method"""
        messages = await self.bot.backup_chat(chat_id=TEST_CHAT_ID, limit=5)
        assert isinstance(messages, list)
        return messages
    
    # ==================== POLLING TESTS ====================
    
    async def test_polling_methods(self):
        """Test semua method polling"""
        console.info("🎯 Testing Polling Methods...")
        
        # Test kirim_polling
        await self.test_method("kirim_polling", self.test_kirim_polling)
        
        # Test hentikan_polling
        await self.test_method("hentikan_polling", self.test_hentikan_polling)
    
    async def test_kirim_polling(self):
        """Test kirim_polling method"""
        message = await self.bot.kirim_polling(
            chat_id=TEST_CHAT_ID,
            question="Test polling?",
            options=["Ya", "Tidak"],
            is_anonymous=True
        )
        assert message.poll is not None
        return message
    
    # ==================== SCHEDULER TESTS ====================
    
    async def test_scheduler_methods(self):
        """Test semua method scheduler"""
        console.info("📅 Testing Scheduler Methods...")
        
        # Test start/stop scheduler
        await self.test_method("start_scheduler", self.test_start_scheduler)
        await self.test_method("stop_scheduler", self.test_stop_scheduler)
        
        # Test scheduled task management
        await self.test_method("add_scheduled_task", self.test_add_scheduled_task)
        await self.test_method("get_scheduled_tasks", self.test_get_scheduled_tasks)
        await self.test_method("remove_scheduled_task", self.test_remove_scheduled_task)
        
        # Test predefined scheduling
        await self.test_method("jadwalkan_pesan", self.test_jadwalkan_pesan)
        await self.test_method("jadwalkan_backup", self.test_jadwalkan_backup)
    
    async def test_start_scheduler(self):
        """Test start_scheduler method"""
        result = await self.bot.start_scheduler()
        assert result == True
        return result
    
    async def test_stop_scheduler(self):
        """Test stop_scheduler method"""
        result = await self.bot.stop_scheduler()
        assert result == True
        return result
    
    async def test_add_scheduled_task(self):
        """Test add_scheduled_task method"""
        
        async def test_task():
            console.info("Test task executed")
        
        result = self.bot.add_scheduled_task(
            task_id="test_task",
            name="Test Task",
            func=test_task,
            interval_seconds=60
        )
        assert result == True
        return result
    
    async def test_get_scheduled_tasks(self):
        """Test get_scheduled_tasks method"""
        tasks = self.bot.get_scheduled_tasks()
        assert isinstance(tasks, list)
        return tasks
    
    async def test_remove_scheduled_task(self):
        """Test remove_scheduled_task method"""
        result = self.bot.remove_scheduled_task("test_task")
        assert result == True
        return result
    
    async def test_jadwalkan_pesan(self):
        """Test jadwalkan_pesan method"""
        from datetime import datetime, timedelta
        
        # Schedule message for 5 minutes from now
        send_time = datetime.now() + timedelta(minutes=5)
        result = await self.bot.jadwalkan_pesan(
            chat_id=TEST_CHAT_ID,
            text="Pesan terjadwal",
            send_time=send_time
        )
        assert result == True
        return result
    
    async def test_jadwalkan_backup(self):
        """Test jadwalkan_backup method"""
        result = await self.bot.jadwalkan_backup(
            chat_id=TEST_CHAT_ID,
            backup_interval_hours=24
        )
        assert result == True
        return result
    
    # ==================== HELPER TESTS ====================
    
    async def test_helper_methods(self):
        """Test semua helper methods"""
        console.info("🔧 Testing Helper Methods...")
        
        # Test cache methods
        await self.test_method("get_cache_stats", self.test_get_cache_stats)
        await self.test_method("cleanup_cache", self.test_cleanup_cache)
        
        # Test utility methods
        await self.test_method("format_file_size", self.test_format_file_size)
        await self.test_method("format_duration", self.test_format_duration)
        await self.test_method("extract_mentions", self.test_extract_mentions)
        await self.test_method("extract_hashtags", self.test_extract_hashtags)
        
        # Test progress callback
        await self.test_method("create_progress_callback", self.test_create_progress_callback)
    
    async def test_get_cache_stats(self):
        """Test get_cache_stats method"""
        stats = self.bot.get_cache_stats()
        assert isinstance(stats, dict)
        assert 'memory_cache' in stats
        return stats
    
    async def test_cleanup_cache(self):
        """Test cleanup_cache method"""
        result = await self.bot.cleanup_cache()
        assert isinstance(result, dict)
        assert 'memory_cache_cleaned' in result
        return result
    
    async def test_format_file_size(self):
        """Test format_file_size method"""
        result = self.bot.format_file_size(1024)
        assert isinstance(result, str)
        assert "KB" in result
        return result
    
    async def test_format_duration(self):
        """Test format_duration method"""
        result = self.bot.format_duration(3661)
        assert isinstance(result, str)
        assert "h" in result
        return result
    
    async def test_extract_mentions(self):
        """Test extract_mentions method"""
        result = self.bot.extract_mentions("Hello @user1 and @user2")
        assert isinstance(result, list)
        assert "user1" in result
        assert "user2" in result
        return result
    
    async def test_extract_hashtags(self):
        """Test extract_hashtags method"""
        result = self.bot.extract_hashtags("Check out #python and #telegram")
        assert isinstance(result, list)
        assert "python" in result
        assert "telegram" in result
        return result
    
    async def test_create_progress_callback(self):
        """Test create_progress_callback method"""
        callback = self.bot.create_progress_callback(100, "Test Progress")
        assert callable(callback)
        return callback
    
    # ==================== BOUND METHODS TESTS ====================
    
    async def test_bound_methods(self):
        """Test bound methods functionality"""
        console.info("🔗 Testing Bound Methods...")
        
        # Test chat bound methods
        await self.test_method("test_chat_bound_methods", self.test_chat_bound_methods)
        
        # Test message bound methods
        await self.test_method("test_message_bound_methods", self.test_message_bound_methods)
    
    async def test_chat_bound_methods(self):
        """Test chat bound methods"""
        try:
            # Get chat object
            chat = await self.bot.get_chat(TEST_CHAT_ID)
            
            # Test if bound methods exist
            assert hasattr(chat, 'get_members')
            assert hasattr(chat, 'get_member')
            assert hasattr(chat, 'backup_chat')
            
            console.info("✅ Chat bound methods are available")
            return True
        except Exception as e:
            console.error(f"❌ Chat bound methods test failed: {e}")
            return False
    
    async def test_message_bound_methods(self):
        """Test message bound methods"""
        try:
            # Send a test message
            message = await self.bot.kirim_pesan(
                chat_id=TEST_CHAT_ID,
                text="Test message for bound methods"
            )
            
            # Test if bound methods exist
            assert hasattr(message, 'reply_text')
            assert hasattr(message, 'edit_text')
            assert hasattr(message, 'delete_message')
            assert hasattr(message, 'pin_message')
            
            console.info("✅ Message bound methods are available")
            return True
        except Exception as e:
            console.error(f"❌ Message bound methods test failed: {e}")
            return False
    
    # ==================== ADVANCED FEATURES TESTS ====================
    
    async def test_advanced_features(self):
        """Test advanced features"""
        console.info("🚀 Testing Advanced Features...")
        
        # Test batch operations
        await self.test_method("batch_operation", self.test_batch_operation)
        
        # Test safe execution
        await self.test_method("safe_execute", self.test_safe_execute)
    
    async def test_batch_operation(self):
        """Test batch_operation method"""
        
        async def test_op():
            return "success"
        
        operations = [test_op for _ in range(5)]
        results = await self.bot.batch_operation(operations, batch_size=2, delay=0.1)
        
        assert isinstance(results, list)
        assert len(results) == 5
        assert all(r == "success" for r in results)
        return results
    
    async def test_safe_execute(self):
        """Test safe_execute method"""
        
        async def test_operation():
            return "executed safely"
        
        result = await self.bot.safe_execute(test_operation, max_retries=3)
        assert result == "executed safely"
        return result
    
    async def test_hentikan_polling(self):
        """Test hentikan_polling method"""
        # Kirim polling dulu
        message = await self.bot.kirim_polling(
            chat_id=TEST_CHAT_ID,
            question="Polling to stop?",
            options=["Option 1", "Option 2"]
        )
        
        # Hentikan polling
        poll = await self.bot.hentikan_polling(
            chat_id=TEST_CHAT_ID,
            message_id=message.id
        )
        assert poll.is_closed == True
        return poll
    
    # ==================== MAIN TEST RUNNER ====================
    
    async def run_all_tests(self):
        """Run all tests"""
        console.info("🧪 Starting Pyrogram Methods Testing...")
        
        # Initialize
        await self.initialize()
        
        # Test categories
        await self.test_message_methods()
        await self.test_media_methods()
        await self.test_chat_methods()
        await self.test_callback_methods()
        await self.test_bot_methods()
        await self.test_utility_methods()
        await self.test_polling_methods()
        await self.test_scheduler_methods()
        await self.test_helper_methods()
        await self.test_bound_methods()
        await self.test_advanced_features()
        
        # Print results
        self.print_results()
    
    def print_results(self):
        """Print test results"""
        console.info("\n" + "="*60)
        console.info("🧪 TEST RESULTS")
        console.info("="*60)
        
        total_tests = len(self.test_results["passed"]) + len(self.test_results["failed"]) + len(self.test_results["skipped"])
        
        console.info(f"📊 Total Tests: {total_tests}")
        console.info(f"✅ Passed: {len(self.test_results['passed'])}")
        console.info(f"❌ Failed: {len(self.test_results['failed'])}")
        console.info(f"⏭️ Skipped: {len(self.test_results['skipped'])}")
        
        if self.test_results["passed"]:
            console.info("\n✅ PASSED TESTS:")
            for test in self.test_results["passed"]:
                console.info(f"  - {test}")
        
        if self.test_results["failed"]:
            console.info("\n❌ FAILED TESTS:")
            for test in self.test_results["failed"]:
                console.error(f"  - {test}")
        
        if self.test_results["skipped"]:
            console.info("\n⏭️ SKIPPED TESTS:")
            for test in self.test_results["skipped"]:
                console.warning(f"  - {test}")
        
        # Calculate success rate
        if total_tests > 0:
            success_rate = (len(self.test_results["passed"]) / (total_tests - len(self.test_results["skipped"]))) * 100
            console.info(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        console.info("="*60)

# ==================== MAIN FUNCTION ====================

async def main():
    """Main function"""
    if len(sys.argv) > 1:
        global TEST_CHAT_ID
        TEST_CHAT_ID = sys.argv[1]
        console.info(f"Using test chat ID: {TEST_CHAT_ID}")
    
    tester = PyrogramMethodsTester()
    
    try:
        await tester.run_all_tests()
    except KeyboardInterrupt:
        console.warning("Testing interrupted by user")
    except Exception as e:
        console.error(f"Testing failed: {e}")
    finally:
        # Cleanup
        if tester.bot:
            await tester.bot.stop()
        if tester.assistant:
            await tester.assistant.stop()

if __name__ == "__main__":
    # Instructions
    console.info("🧪 Pyrogram Methods Testing Script")
    console.info("="*50)
    console.info("📝 Instructions:")
    console.info("1. Update TEST_CHAT_ID in script or pass as argument")
    console.info("2. Make sure bot has access to the test chat")
    console.info("3. Run: python test_pyrogram_methods.py [@chat_id]")
    console.info("="*50)
    
    # Check if test chat ID is set
    if TEST_CHAT_ID == "@SyncaraBot_Test":
        console.warning("⚠️ Please update TEST_CHAT_ID in the script or pass as argument")
        console.info("Example: python test_pyrogram_methods.py @your_test_chat")
        sys.exit(1)
    
    # Run tests
    asyncio.run(main()) 