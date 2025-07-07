#!/usr/bin/env python3
# manage_assistants.py
"""
Script untuk mengelola multiple assistant SyncaraBot
"""

import os
import sys
import asyncio
from pyrogram import Client
from config.assistants_config import (
    ASSISTANT_CONFIG, 
    get_assistant_status, 
    update_assistant_session,
    generate_session_instructions
)

def print_banner():
    """Print banner SyncaraBot"""
    print("""
🤖 SYNCARABOT ASSISTANT MANAGER 🤖
=====================================
    """)

def print_assistant_status():
    """Print status semua assistant"""
    print("📊 **STATUS ASSISTANT:**\n")
    
    status = get_assistant_status()
    for assistant_id, info in status.items():
        emoji = info["emoji"]
        name = info["name"]
        username = info["username"]
        enabled = "✅" if info["enabled"] else "❌"
        has_session = "✅" if info["has_session"] else "❌"
        description = info["description"]
        
        print(f"{emoji} **{name}** (@{username})")
        print(f"   Status: {enabled} Enabled | {has_session} Session")
        print(f"   Description: {description}")
        print()

def generate_session_for_assistant(assistant_id):
    """Generate session string untuk assistant tertentu"""
    assistant_id = assistant_id.upper()
    
    if assistant_id not in ASSISTANT_CONFIG:
        print(f"❌ Assistant {assistant_id} tidak ditemukan!")
        return
    
    config = ASSISTANT_CONFIG[assistant_id]
    print(f"📱 **Generating Session untuk {config['name']}**\n")
    
    # Get API credentials
    print("🔑 **Masukkan API Credentials:**")
    api_id = input("API ID: ").strip()
    api_hash = input("API Hash: ").strip()
    
    if not api_id or not api_hash:
        print("❌ API ID dan API Hash harus diisi!")
        return
    
    try:
        # Create client
        client = Client(
            f"syncara_{assistant_id.lower()}",
            api_id=int(api_id),
            api_hash=api_hash
        )
        
        print(f"\n📱 **Login ke {config['name']}**")
        print("1. Buka Telegram di HP/Desktop")
        print("2. Masukkan kode yang dikirim ke Telegram")
        print("3. Tunggu sampai login berhasil\n")
        
        # Start client
        client.start()
        
        # Get session string
        session_string = client.export_session_string()
        
        print(f"✅ **Session String untuk {config['name']}:**")
        print(f"```{session_string}```")
        print()
        
        # Save to .env format
        env_var = f"{assistant_id}_SESSION_STRING"
        print(f"💾 **Tambahkan ke file .env:**")
        print(f"{env_var}={session_string}")
        print()
        
        # Update config
        update_assistant_session(assistant_id, session_string)
        print(f"✅ {config['name']} session berhasil diupdate!")
        
        # Stop client
        client.stop()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_assistant(assistant_id):
    """Test assistant tertentu"""
    assistant_id = assistant_id.upper()
    
    if assistant_id not in ASSISTANT_CONFIG:
        print(f"❌ Assistant {assistant_id} tidak ditemukan!")
        return
    
    config = ASSISTANT_CONFIG[assistant_id]
    
    if not config["enabled"]:
        print(f"❌ Assistant {assistant_id} tidak enabled!")
        return
    
    print(f"🧪 **Testing {config['name']}**\n")
    
    try:
        # Create test client
        client = Client(
            f"test_{assistant_id.lower()}",
            api_id=int(os.getenv("API_ID")),
            api_hash=os.getenv("API_HASH"),
            session_string=config["session_string"]
        )
        
        # Start client
        client.start()
        
        # Get me info
        me = client.get_me()
        print(f"✅ {config['name']} berhasil connect!")
        print(f"   Username: @{me.username}")
        print(f"   Name: {me.first_name}")
        print(f"   ID: {me.id}")
        
        # Stop client
        client.stop()
        
    except Exception as e:
        print(f"❌ Error testing {config['name']}: {str(e)}")

def show_help():
    """Show help menu"""
    print("""
📋 **COMMANDS:**

1. **status** - Lihat status semua assistant
2. **generate [ASSISTANT]** - Generate session string untuk assistant
3. **test [ASSISTANT]** - Test assistant tertentu
4. **help** - Tampilkan menu ini
5. **exit** - Keluar dari program

**Contoh:**
- `generate AERIS` - Generate session untuk AERIS
- `test ZEKE` - Test assistant ZEKE
- `status` - Lihat status semua assistant

**Assistant yang tersedia:**
- AERIS 🤖 - Default assistant
- KAIROS ⏰ - Time-based assistant  
- ZEKE 🧠 - Technical assistant
- NOVA ✨ - Creative assistant
- LYRA 🎵 - Music assistant
    """)

def main():
    """Main function"""
    print_banner()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    while True:
        try:
            command = input("🤖 SyncaraBot > ").strip().lower()
            
            if command == "exit" or command == "quit":
                print("👋 Goodbye!")
                break
                
            elif command == "help":
                show_help()
                
            elif command == "status":
                print_assistant_status()
                
            elif command.startswith("generate "):
                assistant = command.split(" ", 1)[1].upper()
                generate_session_for_assistant(assistant)
                
            elif command.startswith("test "):
                assistant = command.split(" ", 1)[1].upper()
                test_assistant(assistant)
                
            elif command == "":
                continue
                
            else:
                print("❌ Command tidak dikenal. Ketik 'help' untuk bantuan.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 