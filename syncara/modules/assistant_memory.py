from syncara.database import users
from datetime import datetime
import json

async def kenalan_dan_update(client, user):
    """Kenalan dengan user dan simpan/update ke database"""
    user_data = await users.find_one({"user_id": user.id})
    if not user_data:
        # User baru, simpan ke database dengan struktur yang lebih lengkap
        await users.insert_one({
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "last_interaction": datetime.utcnow(),
            "first_seen": datetime.utcnow(),
            "interaction_count": 1,
            "preferences": {
                "communication_style": "default",  # formal, casual, friendly
                "response_length": "medium",  # short, medium, long
                "emoji_usage": True,
                "language_preference": "id",  # id, en, mixed
                "topics_of_interest": [],
                "avoided_topics": []
            },
            "conversation_history": [],
            "learning_data": {
                "frequently_asked": [],
                "successful_responses": [],
                "user_feedback": []
            },
            "notes": "",
            "personality_notes": ""
        })
        await client.send_message(
            user.id,
            f"Halo {user.first_name or user.username}! Aku AERIS, asisten AI kamu. Senang kenalan denganmu! 😊\n\nAku akan belajar preferensimu seiring waktu untuk memberikan pengalaman yang lebih baik!"
        )
    else:
        # User lama, update waktu interaksi dan increment counter
        await users.update_one(
            {"user_id": user.id},
            {"$set": {
                "last_interaction": datetime.utcnow(),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name
            },
             "$inc": {"interaction_count": 1}}
        )
        # Contoh: assistant bisa mengingat dan menyapa user lama
        await client.send_message(
            user.id,
            f"Halo lagi, {user.first_name or user.username}! Aku masih ingat kamu kok 😁\n\nIni interaksi ke-{user_data.get('interaction_count', 0) + 1} kita!"
        )

async def get_user_memory(user_id):
    """Ambil data user (ingatan) dari database berdasarkan user_id"""
    return await users.find_one({"user_id": user_id})

async def update_user_preferences(user_id, preferences):
    """Update preferensi user"""
    try:
        await users.update_one(
            {"user_id": user_id},
            {"$set": {"preferences": preferences}}
        )
        return True
    except Exception as e:
        print(f"Error updating user preferences: {e}")
        return False

async def add_conversation_entry(user_id, message, response, context=None):
    """Tambah entry ke riwayat percakapan"""
    try:
        entry = {
            "timestamp": datetime.utcnow(),
            "message": message,
            "response": response,
            "context": context or {}
        }
        
        await users.update_one(
            {"user_id": user_id},
            {"$push": {"conversation_history": entry}}
        )
        
        # Batasi riwayat ke 50 entry terakhir
        await users.update_one(
            {"user_id": user_id},
            {"$slice": ["conversation_history", -50]}
        )
        
        return True
    except Exception as e:
        print(f"Error adding conversation entry: {e}")
        return False

async def get_recent_conversations(user_id, limit=10):
    """Ambil percakapan terbaru untuk konteks"""
    try:
        user_data = await users.find_one({"user_id": user_id})
        if user_data and "conversation_history" in user_data:
            return user_data["conversation_history"][-limit:]
        return []
    except Exception as e:
        print(f"Error getting recent conversations: {e}")
        return []

async def learn_from_interaction(user_id, message, response, feedback=None):
    """Belajar dari interaksi untuk meningkatkan respons di masa depan"""
    try:
        # Tambah ke riwayat
        await add_conversation_entry(user_id, message, response)
        
        # Update learning data
        learning_update = {}
        
        # Jika ada feedback, simpan
        if feedback:
            learning_update["$push"] = {"learning_data.user_feedback": {
                "timestamp": datetime.utcnow(),
                "message": message,
                "response": response,
                "feedback": feedback
            }}
        
        # Analisis tipe pertanyaan untuk frequently asked
        question_types = analyze_question_type(message)
        if question_types:
            learning_update["$push"] = {"learning_data.frequently_asked": {
                "timestamp": datetime.utcnow(),
                "question_type": question_types,
                "message": message
            }}
        
        if learning_update:
            await users.update_one({"user_id": user_id}, learning_update)
        
        return True
    except Exception as e:
        print(f"Error learning from interaction: {e}")
        return False

def analyze_question_type(message):
    """Analisis tipe pertanyaan untuk learning"""
    message_lower = message.lower()
    
    question_types = []
    
    if any(word in message_lower for word in ["apa", "what", "siapa", "who"]):
        question_types.append("information")
    
    if any(word in message_lower for word in ["bagaimana", "how", "cara", "gimana"]):
        question_types.append("how_to")
    
    if any(word in message_lower for word in ["kenapa", "why", "mengapa"]):
        question_types.append("explanation")
    
    if any(word in message_lower for word in ["kapan", "when", "jam", "waktu"]):
        question_types.append("time")
    
    if any(word in message_lower for word in ["dimana", "where", "lokasi", "tempat"]):
        question_types.append("location")
    
    return question_types

async def get_user_context(user_id):
    """Dapatkan konteks lengkap user untuk AI response yang lebih baik"""
    try:
        user_data = await users.find_one({"user_id": user_id})
        if not user_data:
            return None
        
        context = {
            "user_info": {
                "name": user_data.get("first_name", ""),
                "username": user_data.get("username", ""),
                "interaction_count": user_data.get("interaction_count", 0),
                "first_seen": user_data.get("first_seen"),
                "last_interaction": user_data.get("last_interaction")
            },
            "preferences": user_data.get("preferences", {}),
            "recent_conversations": user_data.get("conversation_history", [])[-5:],
            "learning_data": user_data.get("learning_data", {}),
            "notes": user_data.get("notes", ""),
            "personality_notes": user_data.get("personality_notes", "")
        }
        
        return context
    except Exception as e:
        print(f"Error getting user context: {e}")
        return None

async def update_personality_notes(user_id, notes):
    """Update catatan kepribadian user"""
    try:
        await users.update_one(
            {"user_id": user_id},
            {"$set": {"personality_notes": notes}}
        )
        return True
    except Exception as e:
        print(f"Error updating personality notes: {e}")
        return False 