# syncara/modules/ai_learning.py
from syncara.database import users
from datetime import datetime, timedelta
import json
import re
from collections import Counter

class AILearning:
    def __init__(self):
        self.learning_patterns = {}
        self.response_quality = {}
    
    async def analyze_user_patterns(self, user_id):
        """Analisis pola penggunaan user untuk personalisasi"""
        try:
            user_data = await users.find_one({"user_id": user_id})
            if not user_data or "conversation_history" not in user_data:
                return None
            
            conversations = user_data["conversation_history"]
            if not conversations:
                return None
            
            # Analisis pola pertanyaan
            question_patterns = self._analyze_question_patterns(conversations)
            
            # Analisis topik yang sering dibahas
            topic_patterns = self._analyze_topic_patterns(conversations)
            
            # Analisis waktu interaksi
            time_patterns = self._analyze_time_patterns(conversations)
            
            # Analisis panjang respons yang disukai
            response_preferences = self._analyze_response_preferences(conversations)
            
            patterns = {
                "question_types": question_patterns,
                "topics": topic_patterns,
                "time_patterns": time_patterns,
                "response_preferences": response_preferences,
                "last_updated": datetime.utcnow()
            }
            
            # Simpan analisis ke database
            await users.update_one(
                {"user_id": user_id},
                {"$set": {"ai_learning_patterns": patterns}}
            )
            
            return patterns
            
        except Exception as e:
            print(f"Error analyzing user patterns: {e}")
            return None
    
    def _analyze_question_patterns(self, conversations):
        """Analisis tipe pertanyaan yang sering diajukan"""
        question_types = []
        
        for conv in conversations:
            message = conv.get("message", "").lower()
            
            if any(word in message for word in ["apa", "what"]):
                question_types.append("information")
            elif any(word in message for word in ["bagaimana", "how", "cara", "gimana"]):
                question_types.append("how_to")
            elif any(word in message for word in ["kenapa", "why", "mengapa"]):
                question_types.append("explanation")
            elif any(word in message for word in ["kapan", "when"]):
                question_types.append("time")
            elif any(word in message for word in ["dimana", "where"]):
                question_types.append("location")
            elif any(word in message for word in ["siapa", "who"]):
                question_types.append("person")
            elif "?" in message:
                question_types.append("general_question")
        
        return Counter(question_types).most_common()
    
    def _analyze_topic_patterns(self, conversations):
        """Analisis topik yang sering dibahas"""
        topics = []
        
        topic_keywords = {
            "technology": ["coding", "program", "software", "app", "website", "tech", "computer"],
            "music": ["lagu", "musik", "song", "music", "playlist", "artist"],
            "education": ["belajar", "study", "course", "tutorial", "education", "school"],
            "entertainment": ["film", "movie", "game", "fun", "entertainment", "hobby"],
            "business": ["bisnis", "business", "money", "work", "job", "career"],
            "health": ["sehat", "health", "olahraga", "exercise", "diet", "medical"]
        }
        
        for conv in conversations:
            message = conv.get("message", "").lower()
            
            for topic, keywords in topic_keywords.items():
                if any(keyword in message for keyword in keywords):
                    topics.append(topic)
        
        return Counter(topics).most_common()
    
    def _analyze_time_patterns(self, conversations):
        """Analisis pola waktu interaksi"""
        hours = []
        days = []
        
        for conv in conversations:
            timestamp = conv.get("timestamp")
            if timestamp:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hours.append(dt.hour)
                days.append(dt.strftime('%A'))
        
        return {
            "peak_hours": Counter(hours).most_common(3),
            "peak_days": Counter(days).most_common(3)
        }
    
    def _analyze_response_preferences(self, conversations):
        """Analisis preferensi respons user"""
        response_lengths = []
        emoji_usage = []
        
        for conv in conversations:
            response = conv.get("response", "")
            
            # Analisis panjang respons
            length = len(response)
            if length < 100:
                response_lengths.append("short")
            elif length < 500:
                response_lengths.append("medium")
            else:
                response_lengths.append("long")
            
            # Analisis penggunaan emoji
            emoji_count = len(re.findall(r'[^\w\s]', response))
            emoji_usage.append(emoji_count > 2)
        
        return {
            "preferred_length": Counter(response_lengths).most_common(1)[0][0] if response_lengths else "medium",
            "likes_emoji": sum(emoji_usage) > len(emoji_usage) / 2 if emoji_usage else True
        }
    
    async def get_personalized_prompt(self, user_id, base_prompt):
        """Buat prompt yang dipersonalisasi berdasarkan analisis user"""
        try:
            patterns = await self.analyze_user_patterns(user_id)
            if not patterns:
                return base_prompt
            
            personalized_prompt = base_prompt + "\n\n"
            
            # Tambahkan preferensi berdasarkan analisis
            if patterns.get("response_preferences"):
                prefs = patterns["response_preferences"]
                personalized_prompt += f"User prefers {prefs['preferred_length']} responses"
                if prefs['likes_emoji']:
                    personalized_prompt += " and uses emojis"
                personalized_prompt += ".\n"
            
            # Tambahkan topik yang disukai
            if patterns.get("topics"):
                top_topics = [topic for topic, count in patterns["topics"][:3]]
                personalized_prompt += f"User is interested in: {', '.join(top_topics)}.\n"
            
            # Tambahkan tipe pertanyaan yang sering
            if patterns.get("question_types"):
                top_questions = [qtype for qtype, count in patterns["question_types"][:2]]
                personalized_prompt += f"User often asks {', '.join(top_questions)} questions.\n"
            
            return personalized_prompt
            
        except Exception as e:
            print(f"Error creating personalized prompt: {e}")
            return base_prompt
    
    async def track_response_quality(self, user_id, message, response, feedback=None):
        """Track kualitas respons untuk pembelajaran"""
        try:
            quality_metrics = {
                "timestamp": datetime.utcnow(),
                "message": message,
                "response": response,
                "response_length": len(response),
                "has_emoji": bool(re.findall(r'[^\w\s]', response)),
                "feedback": feedback
            }
            
            await users.update_one(
                {"user_id": user_id},
                {"$push": {"ai_learning_quality": quality_metrics}}
            )
            
            # Batasi data quality ke 100 entry terakhir
            await users.update_one(
                {"user_id": user_id},
                {"$slice": ["ai_learning_quality", -100]}
            )
            
        except Exception as e:
            print(f"Error tracking response quality: {e}")
    
    async def get_learning_insights(self, user_id):
        """Dapatkan insight pembelajaran untuk user"""
        try:
            user_data = await users.find_one({"user_id": user_id})
            if not user_data:
                return None
            
            insights = {
                "total_interactions": user_data.get("interaction_count", 0),
                "conversation_count": len(user_data.get("conversation_history", [])),
                "patterns": user_data.get("ai_learning_patterns", {}),
                "quality_data": user_data.get("ai_learning_quality", [])
            }
            
            return insights
            
        except Exception as e:
            print(f"Error getting learning insights: {e}")
            return None

# Create singleton instance
ai_learning = AILearning() 