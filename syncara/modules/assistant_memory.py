from syncara.database import users
from syncara.console import console
from datetime import datetime
import json

async def kenalan_dan_update(client, user, send_greeting=True, interaction_context="unknown"):
    """Kenalan dengan user dan simpan/update ke database
    
    Args:
        client: Pyrogram client
        user: User object
        send_greeting: Boolean, kirim greeting message atau tidak (default: True)
        interaction_context: String, context interaction ("private", "group", "unknown")
    """
    try:
        user_data = await users.find_one({"user_id": user.id})
        if not user_data:
            # User baru, simpan ke database dengan struktur yang lebih lengkap
            new_user_data = {
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "last_interaction": datetime.utcnow(),
                "first_seen": datetime.utcnow(),
                "interaction_count": 1,
                "interaction_contexts": {
                    "private_count": 1 if interaction_context == "private" else 0,
                    "group_count": 1 if interaction_context == "group" else 0,
                    "has_private_chat": interaction_context == "private",
                    "last_context": interaction_context,
                    "preferred_context": interaction_context if interaction_context != "unknown" else "group"
                },
                "preferences": {
                    "communication_style": "default",  # formal, casual, friendly
                    "response_length": "medium",  # short, medium, long
                    "emoji_usage": True,
                    "language_preference": "id",  # id, en, mixed
                    "topics_of_interest": [],
                    "avoided_topics": [],
                    "preferred_formality": "informal",  # formal, informal
                    "help_level": "beginner"  # beginner, intermediate, advanced
                },
                "conversation_history": [],
                "learning_data": {
                    "frequently_asked": [],
                    "successful_responses": [],
                    "user_feedback": [],
                    "interaction_patterns": []
                },
                "notes": "",
                "personality_notes": "",
                "mood_history": [],
                "learning_progress": {
                    "topics_learned": [],
                    "skill_level": {},
                    "learning_goals": []
                }
            }
            
            await users.insert_one(new_user_data)
            
            if send_greeting:
                welcome_message = f"Halo {user.first_name or user.username}! Aku AERIS, asisten AI kamu. Senang kenalan denganmu! 😊\n\n" \
                                 f"Aku akan belajar preferensimu seiring waktu untuk memberikan pengalaman yang lebih baik!"
                
                await client.send_message(user.id, welcome_message)
            
            console.info(f"👋 New user registered: {user.first_name} (@{user.username}) - ID: {user.id} - Context: {interaction_context}")
            
        else:
            # User lama, update waktu interaksi dan increment counter
            interaction_count = user_data.get('interaction_count', 0) + 1
            
            # Update interaction contexts
            contexts = user_data.get('interaction_contexts', {})
            if interaction_context == "private":
                contexts['private_count'] = contexts.get('private_count', 0) + 1
                contexts['has_private_chat'] = True
            elif interaction_context == "group":
                contexts['group_count'] = contexts.get('group_count', 0) + 1
            
            contexts['last_context'] = interaction_context
            
            # Determine preferred context based on usage
            private_count = contexts.get('private_count', 0)
            group_count = contexts.get('group_count', 0)
            if private_count > group_count:
                contexts['preferred_context'] = "private"
            elif group_count > private_count:
                contexts['preferred_context'] = "group"
            else:
                contexts['preferred_context'] = contexts.get('preferred_context', 'group')
            
            update_data = {
                "last_interaction": datetime.utcnow(),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "interaction_count": interaction_count,
                "interaction_contexts": contexts
            }
            
            await users.update_one({"user_id": user.id}, {"$set": update_data})
            
            if send_greeting:
                # Personalized greeting based on interaction history
                if interaction_count <= 3:
                    greeting = f"Halo lagi, {user.first_name or user.username}! Aku masih ingat kamu kok 😁\nIni interaksi ke-{interaction_count} kita!"
                elif interaction_count <= 10:
                    greeting = f"Hai {user.first_name or user.username}! Senang ketemu lagi! 🙂"
                elif interaction_count <= 50:
                    greeting = f"Halo {user.first_name or user.username}! Kamu udah jadi teman dekat aku nih! 😊"
                else:
                    greeting = f"Hai bestie {user.first_name or user.username}! Kamu udah kayak keluarga buat aku! 🥰"
                
                await client.send_message(user.id, greeting)
            
            console.info(f"🔄 Updated user: {user.first_name} (@{user.username}) - Interaction #{interaction_count} - Context: {interaction_context}")
            
    except Exception as e:
        console.error(f"Error in kenalan_dan_update: {str(e)}")

async def get_user_memory(user_id):
    """Ambil data user (ingatan) dari database berdasarkan user_id"""
    try:
        return await users.find_one({"user_id": user_id})
    except Exception as e:
        console.error(f"Error getting user memory: {e}")
        return None

async def update_user_preferences(user_id, preferences):
    """Update preferensi user"""
    try:
        await users.update_one(
            {"user_id": user_id},
            {"$set": {"preferences": preferences, "preferences_updated": datetime.utcnow()}}
        )
        console.info(f"📝 Updated preferences for user {user_id}")
        return True
    except Exception as e:
        console.error(f"Error updating user preferences: {e}")
        return False

async def add_conversation_entry(user_id, message, response, context=None):
    """Tambah entry ke riwayat percakapan dengan enhanced context"""
    try:
        entry = {
            "timestamp": datetime.utcnow(),
            "message": message,
            "response": response,
            "message_length": len(message),
            "response_length": len(response),
            "context": context or {},
            "interaction_type": _classify_interaction_type(message),
            "mood_indicator": _detect_mood(message)
        }
        
        # Push entry baru dan batasi ke 50 entry terakhir dalam satu operasi
        await users.update_one(
            {"user_id": user_id},
            {
                "$push": {
                    "conversation_history": {
                        "$each": [entry],
                        "$slice": -50
                    }
                }
            }
        )
        
        # Update interaction patterns
        await _update_interaction_patterns(user_id, entry)
        
        console.info(f"💬 Added conversation entry for user {user_id}")
        return True
    except Exception as e:
        console.error(f"Error adding conversation entry: {e}")
        return False

def _classify_interaction_type(message):
    """Classify the type of interaction"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["?", "apa", "bagaimana", "kenapa", "dimana", "kapan", "siapa"]):
        return "question"
    elif any(word in message_lower for word in ["tolong", "bantu", "help", "bisa", "minta"]):
        return "request"
    elif any(word in message_lower for word in ["terima kasih", "thanks", "makasih", "good", "bagus"]):
        return "appreciation"
    elif any(word in message_lower for word in ["halo", "hai", "hello", "selamat"]):
        return "greeting"
    else:
        return "statement"

def _detect_mood(message):
    """Detect mood from message"""
    message_lower = message.lower()
    
    positive_indicators = ["senang", "bahagia", "bagus", "keren", "mantap", "suka", "love"]
    negative_indicators = ["sedih", "marah", "kesal", "bosan", "tidak suka", "hate", "bad"]
    neutral_indicators = ["?", "apa", "bagaimana", "tolong"]
    
    positive_count = sum(1 for indicator in positive_indicators if indicator in message_lower)
    negative_count = sum(1 for indicator in negative_indicators if indicator in message_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    elif any(indicator in message_lower for indicator in neutral_indicators):
        return "neutral"
    else:
        return "neutral"

async def _update_interaction_patterns(user_id, entry):
    """Update interaction patterns for user"""
    try:
        pattern = {
            "timestamp": entry["timestamp"],
            "type": entry["interaction_type"],
            "mood": entry["mood_indicator"],
            "message_length": entry["message_length"],
            "hour": entry["timestamp"].hour,
            "day_of_week": entry["timestamp"].strftime("%A")
        }
        
        await users.update_one(
            {"user_id": user_id},
            {
                "$push": {
                    "learning_data.interaction_patterns": {
                        "$each": [pattern],
                        "$slice": -100  # Keep last 100 patterns
                    }
                }
            }
        )
        
    except Exception as e:
        console.error(f"Error updating interaction patterns: {e}")

async def get_recent_conversations(user_id, limit=10):
    """Ambil percakapan terbaru untuk konteks"""
    try:
        user_data = await users.find_one({"user_id": user_id})
        if user_data and "conversation_history" in user_data:
            return user_data["conversation_history"][-limit:]
        return []
    except Exception as e:
        console.error(f"Error getting recent conversations: {e}")
        return []

async def learn_from_interaction(user_id, message, response, feedback=None):
    """Belajar dari interaksi untuk meningkatkan respons di masa depan"""
    try:
        # Tambah ke riwayat dengan enhanced context
        context = {
            "has_shortcode": "[" in response and "]" in response,
            "response_quality": _assess_response_quality(message, response),
            "user_satisfaction": _estimate_satisfaction(feedback)
        }
        
        await add_conversation_entry(user_id, message, response, context)
        
        # Update learning data
        learning_update = {}
        
        # Jika ada feedback, simpan
        if feedback:
            feedback_entry = {
                "timestamp": datetime.utcnow(),
                "message": message,
                "response": response,
                "feedback": feedback,
                "feedback_type": _classify_feedback(feedback)
            }
            learning_update["$push"] = {"learning_data.user_feedback": feedback_entry}
        
        # Analisis tipe pertanyaan untuk frequently asked
        question_types = analyze_question_type(message)
        if question_types:
            question_entry = {
                "timestamp": datetime.utcnow(),
                "question_type": question_types,
                "message": message,
                "success_rate": _calculate_success_rate(user_id, question_types)
            }
            learning_update["$push"] = {"learning_data.frequently_asked": question_entry}
        
        # Track successful responses
        if _is_successful_response(message, response, feedback):
            success_entry = {
                "timestamp": datetime.utcnow(),
                "message": message,
                "response": response,
                "success_factors": _identify_success_factors(response)
            }
            if "$push" not in learning_update:
                learning_update["$push"] = {}
            learning_update["$push"]["learning_data.successful_responses"] = success_entry
        
        if learning_update:
            await users.update_one({"user_id": user_id}, learning_update)
        
        console.info(f"🎓 Learned from interaction with user {user_id}")
        return True
    except Exception as e:
        console.error(f"Error learning from interaction: {e}")
        return False

def _assess_response_quality(message, response):
    """Assess the quality of the response"""
    score = 0.5  # Base score
    
    # Length appropriateness
    if 50 <= len(response) <= 1000:
        score += 0.1
    
    # Has helpful content
    helpful_indicators = ["cara", "langkah", "tips", "solusi", "jawaban", "contoh"]
    if any(indicator in response.lower() for indicator in helpful_indicators):
        score += 0.2
    
    # Has structure (lists, formatting)
    if any(char in response for char in ["•", "-", "1.", "2.", "\n"]):
        score += 0.1
    
    # Relevant to question
    message_words = set(message.lower().split())
    response_words = set(response.lower().split())
    overlap = len(message_words.intersection(response_words))
    if overlap > 2:
        score += 0.1
    
    return min(score, 1.0)

def _estimate_satisfaction(feedback):
    """Estimate user satisfaction from feedback"""
    if not feedback:
        return 0.5
    
    feedback_lower = feedback.lower()
    
    positive_words = ["bagus", "terima kasih", "membantu", "good", "thanks", "helpful"]
    negative_words = ["tidak", "salah", "kurang", "bad", "wrong", "unhelpful"]
    
    positive_count = sum(1 for word in positive_words if word in feedback_lower)
    negative_count = sum(1 for word in negative_words if word in feedback_lower)
    
    if positive_count > negative_count:
        return 0.8
    elif negative_count > positive_count:
        return 0.2
    else:
        return 0.5

def _classify_feedback(feedback):
    """Classify feedback type"""
    feedback_lower = feedback.lower()
    
    if any(word in feedback_lower for word in ["bagus", "terima kasih", "membantu", "good", "thanks"]):
        return "positive"
    elif any(word in feedback_lower for word in ["tidak", "salah", "kurang", "bad", "wrong"]):
        return "negative"
    elif any(word in feedback_lower for word in ["saran", "suggestion", "improve", "better"]):
        return "suggestion"
    else:
        return "neutral"

async def _calculate_success_rate(user_id, question_types):
    """Calculate success rate for specific question types"""
    try:
        user_data = await users.find_one({"user_id": user_id})
        if not user_data:
            return 0.5
        
        feedback_data = user_data.get("learning_data", {}).get("user_feedback", [])
        
        relevant_feedback = [f for f in feedback_data if any(qt in f.get("message", "").lower() for qt in question_types)]
        
        if not relevant_feedback:
            return 0.5
        
        positive_feedback = sum(1 for f in relevant_feedback if f.get("feedback_type") == "positive")
        
        return positive_feedback / len(relevant_feedback)
        
    except Exception as e:
        console.error(f"Error calculating success rate: {e}")
        return 0.5

def _is_successful_response(message, response, feedback):
    """Determine if a response was successful"""
    # Has feedback and it's positive
    if feedback and _classify_feedback(feedback) == "positive":
        return True
    
    # Response is substantial and relevant
    if len(response) > 100 and _assess_response_quality(message, response) > 0.7:
        return True
    
    return False

def _identify_success_factors(response):
    """Identify factors that made a response successful"""
    factors = []
    
    if len(response) > 200:
        factors.append("detailed")
    
    if any(char in response for char in ["•", "-", "1.", "2."]):
        factors.append("structured")
    
    if any(word in response.lower() for word in ["contoh", "cara", "langkah", "tips"]):
        factors.append("practical")
    
    if response.count("😊") + response.count("🙂") + response.count("😄") > 0:
        factors.append("friendly")
    
    return factors

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
    
    if any(word in message_lower for word in ["tolong", "bantu", "help", "bisa"]):
        question_types.append("assistance")
    
    return question_types

async def get_user_context(user_id):
    """Dapatkan konteks lengkap user untuk AI response yang lebih baik"""
    try:
        user_data = await users.find_one({"user_id": user_id})
        if not user_data:
            return None
        
        # Enhanced context with more detailed information
        context = {
            "user_info": {
                "name": user_data.get("first_name", ""),
                "username": user_data.get("username", ""),
                "interaction_count": user_data.get("interaction_count", 0),
                "first_seen": user_data.get("first_seen"),
                "last_interaction": user_data.get("last_interaction"),
                "relationship_level": _determine_relationship_level(user_data.get("interaction_count", 0))
            },
            "preferences": user_data.get("preferences", {}),
            "recent_conversations": user_data.get("conversation_history", [])[-5:],
            "learning_data": user_data.get("learning_data", {}),
            "notes": user_data.get("notes", ""),
            "personality_notes": user_data.get("personality_notes", ""),
            "interaction_summary": _generate_interaction_summary(user_data),
            "mood_context": _get_recent_mood_context(user_data),
            "learning_progress": user_data.get("learning_progress", {})
        }
        
        return context
    except Exception as e:
        console.error(f"Error getting user context: {e}")
        return None

def _determine_relationship_level(interaction_count):
    """Determine relationship level based on interaction count"""
    if interaction_count < 5:
        return "new"
    elif interaction_count < 20:
        return "familiar"
    elif interaction_count < 50:
        return "friend"
    else:
        return "close_friend"

def _generate_interaction_summary(user_data):
    """Generate summary of user interactions"""
    interaction_count = user_data.get("interaction_count", 0)
    conv_history = user_data.get("conversation_history", [])
    
    if not conv_history:
        return "No interaction history"
    
    # Recent interaction types
    recent_types = [conv.get("interaction_type", "unknown") for conv in conv_history[-10:]]
    most_common_type = max(set(recent_types), key=recent_types.count) if recent_types else "unknown"
    
    # Average response quality
    quality_scores = [conv.get("context", {}).get("response_quality", 0.5) for conv in conv_history]
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.5
    
    return {
        "total_interactions": interaction_count,
        "recent_interaction_type": most_common_type,
        "avg_response_quality": avg_quality,
        "conversation_span_days": _calculate_conversation_span(conv_history)
    }

def _get_recent_mood_context(user_data):
    """Get recent mood context"""
    conv_history = user_data.get("conversation_history", [])
    if not conv_history:
        return "neutral"
    
    recent_moods = [conv.get("mood_indicator", "neutral") for conv in conv_history[-5:]]
    mood_counts = {mood: recent_moods.count(mood) for mood in set(recent_moods)}
    
    return max(mood_counts, key=mood_counts.get) if mood_counts else "neutral"

def _calculate_conversation_span(conv_history):
    """Calculate how many days user has been interacting"""
    if not conv_history:
        return 0
    
    first_conv = conv_history[0].get("timestamp")
    last_conv = conv_history[-1].get("timestamp")
    
    if first_conv and last_conv:
        return (last_conv - first_conv).days
    
    return 0

async def update_personality_notes(user_id, notes):
    """Update catatan kepribadian user"""
    try:
        await users.update_one(
            {"user_id": user_id},
            {"$set": {"personality_notes": notes, "personality_updated": datetime.utcnow()}}
        )
        console.info(f"📝 Updated personality notes for user {user_id}")
        return True
    except Exception as e:
        console.error(f"Error updating personality notes: {e}")
        return False

async def update_learning_progress(user_id, topic, skill_level):
    """Update learning progress for specific topics"""
    try:
        await users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    f"learning_progress.skill_level.{topic}": skill_level,
                    "learning_progress.last_updated": datetime.utcnow()
                },
                "$addToSet": {"learning_progress.topics_learned": topic}
            }
        )
        console.info(f"📚 Updated learning progress for user {user_id}: {topic} -> {skill_level}")
        return True
    except Exception as e:
        console.error(f"Error updating learning progress: {e}")
        return False 