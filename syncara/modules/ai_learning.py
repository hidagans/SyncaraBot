# syncara/modules/ai_learning.py
from syncara.database import users
from syncara.console import console
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
            
            # Analisis sentiment dan mood
            mood_patterns = self._analyze_mood_patterns(conversations)
            
            # Analisis learning effectiveness
            learning_effectiveness = self._analyze_learning_effectiveness(conversations)
            
            patterns = {
                "question_types": question_patterns,
                "topics": topic_patterns,
                "time_patterns": time_patterns,
                "response_preferences": response_preferences,
                "mood_patterns": mood_patterns,
                "learning_effectiveness": learning_effectiveness,
                "last_updated": datetime.utcnow(),
                "analysis_version": "2.0"
            }
            
            # Simpan analisis ke database
            await users.update_one(
                {"user_id": user_id},
                {"$set": {"ai_learning_patterns": patterns}}
            )
            
            console.info(f"🧠 Updated learning patterns for user {user_id}")
            return patterns
            
        except Exception as e:
            console.error(f"Error analyzing user patterns: {e}")
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
            elif any(word in message for word in ["bisakah", "can", "bisa", "could"]):
                question_types.append("capability")
            elif "?" in message:
                question_types.append("general_question")
            else:
                question_types.append("statement")
        
        return Counter(question_types).most_common()
    
    def _analyze_topic_patterns(self, conversations):
        """Analisis topik yang sering dibahas"""
        topics = []
        
        topic_keywords = {
            "technology": ["coding", "program", "software", "app", "website", "tech", "computer", "ai", "python", "javascript"],
            "music": ["lagu", "musik", "song", "music", "playlist", "artist", "band", "album"],
            "education": ["belajar", "study", "course", "tutorial", "education", "school", "university", "college"],
            "entertainment": ["film", "movie", "game", "fun", "entertainment", "hobby", "anime", "series"],
            "business": ["bisnis", "business", "money", "work", "job", "career", "startup", "finance"],
            "health": ["sehat", "health", "olahraga", "exercise", "diet", "medical", "fitness"],
            "travel": ["travel", "trip", "vacation", "jalan", "wisata", "liburan", "hotel"],
            "food": ["makanan", "food", "resep", "recipe", "makan", "masak", "restaurant"],
            "sports": ["sport", "football", "basketball", "badminton", "tennis", "gym"],
            "science": ["science", "physics", "chemistry", "biology", "research", "experiment"]
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
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hours.append(dt.hour)
                    days.append(dt.strftime('%A'))
                except:
                    continue
        
        return {
            "peak_hours": Counter(hours).most_common(3),
            "peak_days": Counter(days).most_common(3),
            "total_interactions": len(conversations),
            "avg_daily_interactions": len(conversations) / max(len(set(days)), 1)
        }
    
    def _analyze_response_preferences(self, conversations):
        """Analisis preferensi respons user"""
        response_lengths = []
        emoji_usage = []
        formality_levels = []
        
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
            
            # Analisis formalitas
            formal_words = ["anda", "bapak", "ibu", "dengan hormat", "terima kasih"]
            informal_words = ["kamu", "lo", "gue", "aku", "wkwk", "hehe"]
            
            formal_count = sum(1 for word in formal_words if word in response.lower())
            informal_count = sum(1 for word in informal_words if word in response.lower())
            
            if formal_count > informal_count:
                formality_levels.append("formal")
            else:
                formality_levels.append("informal")
        
        return {
            "preferred_length": Counter(response_lengths).most_common(1)[0][0] if response_lengths else "medium",
            "likes_emoji": sum(emoji_usage) > len(emoji_usage) / 2 if emoji_usage else True,
            "preferred_formality": Counter(formality_levels).most_common(1)[0][0] if formality_levels else "informal",
            "avg_response_length": sum(len(conv.get("response", "")) for conv in conversations) / max(len(conversations), 1)
        }
    
    def _analyze_mood_patterns(self, conversations):
        """Analisis pola mood dan sentiment"""
        positive_words = ["bagus", "senang", "suka", "baik", "mantap", "keren", "amazing", "good", "great", "love"]
        negative_words = ["buruk", "sedih", "tidak", "bad", "hate", "angry", "marah", "bosan", "boring"]
        question_words = ["?", "apa", "bagaimana", "kenapa", "what", "how", "why"]
        
        mood_scores = []
        interaction_types = []
        
        for conv in conversations:
            message = conv.get("message", "").lower()
            
            positive_count = sum(1 for word in positive_words if word in message)
            negative_count = sum(1 for word in negative_words if word in message)
            question_count = sum(1 for word in question_words if word in message)
            
            # Mood score (-1 to 1)
            if positive_count > negative_count:
                mood_scores.append(1)
            elif negative_count > positive_count:
                mood_scores.append(-1)
            else:
                mood_scores.append(0)
            
            # Interaction type
            if question_count > 0:
                interaction_types.append("questioning")
            elif positive_count > 0:
                interaction_types.append("positive")
            elif negative_count > 0:
                interaction_types.append("negative")
            else:
                interaction_types.append("neutral")
        
        return {
            "avg_mood": sum(mood_scores) / max(len(mood_scores), 1),
            "interaction_types": Counter(interaction_types).most_common(),
            "mood_stability": 1 - (len(set(mood_scores)) / max(len(mood_scores), 1))  # 0-1, higher = more stable
        }
    
    def _analyze_learning_effectiveness(self, conversations):
        """Analisis efektivitas pembelajaran AI"""
        if len(conversations) < 5:
            return {"effectiveness_score": 0.5, "improvement_areas": ["Need more data"]}
        
        recent_convs = conversations[-10:]  # Last 10 conversations
        older_convs = conversations[-20:-10] if len(conversations) >= 20 else []
        
        # Analisis repeat questions (pertanyaan berulang)
        recent_questions = [conv.get("message", "") for conv in recent_convs]
        older_questions = [conv.get("message", "") for conv in older_convs]
        
        repeat_questions = 0
        for recent_q in recent_questions:
            for older_q in older_questions:
                if self._similarity_score(recent_q, older_q) > 0.7:
                    repeat_questions += 1
                    break
        
        # Analisis response quality improvement
        recent_responses = [len(conv.get("response", "")) for conv in recent_convs]
        older_responses = [len(conv.get("response", "")) for conv in older_convs] if older_convs else recent_responses
        
        avg_recent_length = sum(recent_responses) / max(len(recent_responses), 1)
        avg_older_length = sum(older_responses) / max(len(older_responses), 1)
        
        length_improvement = (avg_recent_length - avg_older_length) / max(avg_older_length, 1)
        
        # Calculate effectiveness score
        repeat_penalty = repeat_questions / max(len(recent_questions), 1)
        effectiveness_score = max(0, 1 - repeat_penalty + (length_improvement * 0.1))
        
        improvement_areas = []
        if repeat_penalty > 0.3:
            improvement_areas.append("Reduce repetitive responses")
        if length_improvement < 0:
            improvement_areas.append("Improve response detail")
        if effectiveness_score < 0.6:
            improvement_areas.append("General learning enhancement needed")
        
        return {
            "effectiveness_score": min(effectiveness_score, 1.0),
            "repeat_question_rate": repeat_penalty,
            "response_improvement": length_improvement,
            "improvement_areas": improvement_areas or ["Good learning progress"]
        }
    
    def _similarity_score(self, text1, text2):
        """Calculate simple similarity score between two texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0
    
    async def get_personalized_prompt(self, user_id, base_prompt):
        """Buat prompt yang dipersonalisasi berdasarkan analisis user"""
        try:
            patterns = await self.analyze_user_patterns(user_id)
            if not patterns:
                return base_prompt
            
            personalized_prompt = base_prompt + "\n\n📊 **User Personalization:**\n"
            
            # Tambahkan preferensi berdasarkan analisis
            if patterns.get("response_preferences"):
                prefs = patterns["response_preferences"]
                personalized_prompt += f"• Response style: {prefs['preferred_length']} length, {prefs['preferred_formality']} tone"
                if prefs['likes_emoji']:
                    personalized_prompt += " with emojis"
                personalized_prompt += "\n"
            
            # Tambahkan topik yang disukai
            if patterns.get("topics"):
                top_topics = [topic for topic, count in patterns["topics"][:3]]
                if top_topics:
                    personalized_prompt += f"• Interested topics: {', '.join(top_topics)}\n"
            
            # Tambahkan tipe pertanyaan yang sering
            if patterns.get("question_types"):
                top_questions = [qtype for qtype, count in patterns["question_types"][:2]]
                if top_questions:
                    personalized_prompt += f"• Common question types: {', '.join(top_questions)}\n"
            
            # Tambahkan mood context
            if patterns.get("mood_patterns"):
                mood = patterns["mood_patterns"]
                avg_mood = mood.get("avg_mood", 0)
                if avg_mood > 0.3:
                    personalized_prompt += "• User generally has positive mood\n"
                elif avg_mood < -0.3:
                    personalized_prompt += "• User may need more encouragement\n"
            
            # Tambahkan learning effectiveness
            if patterns.get("learning_effectiveness"):
                effectiveness = patterns["learning_effectiveness"]
                score = effectiveness.get("effectiveness_score", 0.5)
                if score > 0.8:
                    personalized_prompt += "• High learning effectiveness - can provide advanced content\n"
                elif score < 0.4:
                    personalized_prompt += "• Focus on clarity and avoid repetition\n"
            
            personalized_prompt += "\nAdapt your response accordingly! 🎯"
            
            return personalized_prompt
            
        except Exception as e:
            console.error(f"Error creating personalized prompt: {e}")
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
                "word_count": len(response.split()),
                "feedback": feedback,
                "sentiment_score": self._calculate_sentiment(response)
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
            
            console.info(f"📊 Tracked response quality for user {user_id}")
            
        except Exception as e:
            console.error(f"Error tracking response quality: {e}")
    
    def _calculate_sentiment(self, text):
        """Simple sentiment calculation"""
        positive_words = ["bagus", "senang", "suka", "baik", "mantap", "keren", "amazing", "good", "great"]
        negative_words = ["buruk", "sedih", "tidak suka", "bad", "hate", "angry", "marah"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 1
        elif negative_count > positive_count:
            return -1
        else:
            return 0
    
    async def get_learning_insights(self, user_id):
        """Dapatkan insight pembelajaran untuk user"""
        try:
            user_data = await users.find_one({"user_id": user_id})
            if not user_data:
                return None
            
            patterns = user_data.get("ai_learning_patterns", {})
            
            insights = {
                "total_interactions": user_data.get("interaction_count", 0),
                "conversation_count": len(user_data.get("conversation_history", [])),
                "patterns": patterns,
                "quality_data": user_data.get("ai_learning_quality", []),
                "learning_summary": self._generate_learning_summary(patterns),
                "recommendations": self._generate_recommendations(patterns)
            }
            
            return insights
            
        except Exception as e:
            console.error(f"Error getting learning insights: {e}")
            return None
    
    def _generate_learning_summary(self, patterns):
        """Generate summary of learning patterns"""
        if not patterns:
            return "No learning data available"
        
        summary = []
        
        # Topic preferences
        if patterns.get("topics"):
            top_topic = patterns["topics"][0][0] if patterns["topics"] else "general"
            summary.append(f"Most interested in: {top_topic}")
        
        # Question style
        if patterns.get("question_types"):
            top_question = patterns["question_types"][0][0] if patterns["question_types"] else "general"
            summary.append(f"Prefers {top_question} questions")
        
        # Response style
        if patterns.get("response_preferences"):
            prefs = patterns["response_preferences"]
            summary.append(f"Likes {prefs.get('preferred_length', 'medium')} responses")
        
        # Learning effectiveness
        if patterns.get("learning_effectiveness"):
            score = patterns["learning_effectiveness"].get("effectiveness_score", 0.5)
            if score > 0.8:
                summary.append("High learning effectiveness")
            elif score < 0.4:
                summary.append("Needs learning improvement")
        
        return "; ".join(summary) if summary else "Basic learning data available"
    
    def _generate_recommendations(self, patterns):
        """Generate recommendations for improving interaction"""
        if not patterns:
            return ["Collect more interaction data"]
        
        recommendations = []
        
        # Based on effectiveness score
        if patterns.get("learning_effectiveness"):
            effectiveness = patterns["learning_effectiveness"]
            for area in effectiveness.get("improvement_areas", []):
                recommendations.append(f"Improvement: {area}")
        
        # Based on response preferences
        if patterns.get("response_preferences"):
            prefs = patterns["response_preferences"]
            if prefs.get("preferred_formality") == "formal":
                recommendations.append("Use more formal language")
            else:
                recommendations.append("Keep casual, friendly tone")
        
        # Based on mood patterns
        if patterns.get("mood_patterns"):
            mood = patterns["mood_patterns"]
            if mood.get("avg_mood", 0) < 0:
                recommendations.append("Provide more encouragement and positive responses")
        
        return recommendations if recommendations else ["Continue current interaction style"]

# Create singleton instance
ai_learning = AILearning() 