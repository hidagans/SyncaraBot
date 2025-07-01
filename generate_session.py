# generate_sessions.py
from pyrogram import Client
import asyncio
import json
import os

async def generate_session(name, api_id, api_hash):
    """Generate a session string for a userbot"""
    print(f"\nGenerating session for '{name}'...")
    
    async with Client(name, api_id=api_id, api_hash=api_hash, in_memory=True) as app:
        session_string = await app.export_session_string()
        print(f"Session for '{name}' generated successfully!")
        return {
            "name": name,
            "api_id": api_id,
            "api_hash": api_hash,
            "session_string": session_string
        }

async def main():
    print("===== USERBOT SESSION GENERATOR =====")
    print("This script will help you generate session strings for multiple userbots")
    
    api_id = int(input("\nEnter your API ID: "))
    api_hash = input("Enter your API HASH: ")
    
    num_userbots = int(input("\nHow many userbots do you want to create? (1-5): "))
    if num_userbots < 1 or num_userbots > 5:
        print("Please enter a number between 1 and 5")
        return
    
    userbots = []
    
    for i in range(1, num_userbots + 1):
        name = input(f"\nEnter name for userbot #{i} (default: userbot{i}): ") or f"userbot{i}"
        userbot = await generate_session(name, api_id, api_hash)
        userbots.append(userbot)
    
    # Save to file
    with open("userbots_config.json", "w") as f:
        json.dump(userbots, f, indent=4)
    
    print("\n===== ALL SESSIONS GENERATED =====")
    print(f"Generated {len(userbots)} userbot sessions")
    print("Configuration saved to 'userbots_config.json'")
    print("\nTo use these userbots, copy the contents of the JSON file to your config.py USERBOTS section")
    print("IMPORTANT: Keep your session strings secure and don't share them with anyone!")

if __name__ == "__main__":
    asyncio.run(main())
