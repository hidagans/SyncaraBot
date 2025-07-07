# SyncaraBot 🤖

Bot Telegram dengan AI Assistant menggunakan Replicate API

## 🚀 Fitur

- **Bot Manager** - Mengelola userbot assistant
- **AI Assistant** - Chat AI dengan GPT-4 via Replicate
- **System Prompts** - Multiple personality (AERIS, KAIROS, ZEKE, NOVA, LYRA)
- **Image Analysis** - Analisis gambar dengan AI
- **Music Player** - Fitur musik player
- **Shortcode System** - Sistem perintah khusus
- **🧠 AI Learning System** - Sistem pembelajaran AI yang canggih
- **📊 Analytics & Insights** - Analisis pola penggunaan user
- **🎯 Personalized Responses** - Respons yang dipersonalisasi berdasarkan preferensi user
- **💾 Advanced Memory** - Sistem memori yang menyimpan riwayat dan preferensi

## 📋 Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Konfigurasi Environment
Buat file `.env` dengan konfigurasi berikut:

```env
# Bot Configuration
API_ID=your_api_id_here
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here

# Replicate API Key
API_KEY=your_replicate_api_key_here

# Assistant Session Strings
AERIS_SESSION_STRING=your_aeris_session_string_here
KAIROS_SESSION_STRING=your_kairos_session_string_here
ZEKE_SESSION_STRING=your_zeke_session_string_here
NOVA_SESSION_STRING=your_nova_session_string_here
LYRA_SESSION_STRING=your_lyra_session_string_here

# Legacy (untuk backward compatibility)
SESSION_STRING=your_default_session_string_here

# MongoDB Configuration (optional)
MONGO_URI=your_mongodb_uri_here
DB_NAME=syncara_bot
```

### 3. Generate Session Strings
```bash
# Generate session untuk semua assistant
python manage_assistants.py

# Atau generate session manual
python generate_session.py
```

### 4. Jalankan Bot
```bash
python -m syncara
```

## 💡 Cara Penggunaan

### Bot Manager (@SyncaraBot)
- `/start` - Menu utama
- `/test` - Test command
- `/debug` - Debug info (owner only)
- `/assistants` - Lihat status semua assistant (owner only)
- `/assistant_info [ASSISTANT]` - Info detail assistant (owner only)
- `/test_assistant [ASSISTANT]` - Test assistant tertentu (owner only)
- `/analytics [user_id]` - Lihat analytics user (owner only)
- `/learning_insights [user_id]` - Lihat insight pembelajaran (owner only)

### AI Assistants
- **AERIS** (@Aeris_sync) - Default assistant dengan AI learning
- **KAIROS** (@Kairos_sync) - Time-based responses
- **ZEKE** (@Zeke_sync) - Technical assistant dengan reasoning
- **NOVA** (@Nova_sync) - Creative assistant
- **LYRA** (@Lyra_sync) - Music-focused assistant

**Cara Penggunaan:**
- **Private Chat** - Kirim pesan langsung ke assistant
- **Group Chat** - Mention atau reply ke assistant

**Contoh Penggunaan:**
```
🤖 AERIS: "Halo! Bisa bantu aku belajar tentang AI?"
⏰ KAIROS: "Buatkan jadwal produktif untuk hari ini"
🧠 ZEKE: "Analisis kode Python ini dan berikan solusi"
✨ NOVA: "Bantu aku brainstorming ide untuk project kreatif"
🎵 LYRA: "Rekomendasi musik untuk mood kerja"
```

## 🔧 System Prompts

Bot mendukung multiple personality dengan karakteristik unik:

### 🤖 **AERIS** - Default Assistant
- **Personality**: Ramah, ekspresif, dengan AI learning yang canggih
- **Specialty**: General assistant dengan kemampuan reasoning dan problem solving
- **Style**: Santai, fleksibel, sedikit nyeleneh tapi tetap sopan
- **Best for**: Percakapan umum, bantuan sehari-hari, dan pembelajaran AI

### ⏰ **KAIROS** - Time Management Expert
- **Personality**: Terorganisir, tepat waktu, efisien
- **Specialty**: Manajemen waktu, scheduling, dan produktivitas
- **Style**: Terstruktur, fokus pada efisiensi, memberikan timeline yang jelas
- **Best for**: Perencanaan, jadwal, deadline management, dan tips produktivitas

### 🧠 **ZEKE** - Technical Reasoning Assistant
- **Personality**: Analitis, logis, sistematis
- **Specialty**: Technical problem solving dan reasoning tingkat tinggi
- **Style**: Jelas, terstruktur, menjelaskan proses berpikir secara bertahap
- **Best for**: Masalah teknis, coding, analisis kompleks, dan troubleshooting

### ✨ **NOVA** - Creative Innovation Assistant
- **Personality**: Kreatif, inovatif, penuh imajinasi
- **Specialty**: Creative thinking, ide generation, dan artistic expression
- **Style**: Ekspresif, artistik, penuh inspirasi dan metafora kreatif
- **Best for**: Brainstorming, desain, creative writing, dan solusi inovatif

### 🎵 **LYRA** - Music & Audio Expert
- **Personality**: Passionate, energik, musikal
- **Specialty**: Musik, audio, dan entertainment
- **Style**: Ritmis, penuh energi musik, memberikan rekomendasi personal
- **Best for**: Rekomendasi musik, playlist curation, audio analysis, dan entertainment

## 🧠 AI Learning Features

### Advanced Memory System
- **User Preferences**: Menyimpan preferensi komunikasi user
- **Conversation History**: Riwayat percakapan untuk konteks
- **Learning Patterns**: Analisis pola penggunaan untuk personalisasi
- **Response Quality Tracking**: Tracking kualitas respons untuk pembelajaran

### Analytics & Insights
- **Question Pattern Analysis**: Analisis tipe pertanyaan yang sering diajukan
- **Topic Interest Tracking**: Tracking topik yang disukai user
- **Time Pattern Analysis**: Analisis pola waktu interaksi
- **Response Preference Learning**: Belajar preferensi respons user

### Personalized Responses
- **Adaptive Communication**: Menyesuaikan gaya komunikasi berdasarkan preferensi
- **Context-Aware Responses**: Respons yang mempertimbangkan riwayat percakapan
- **Smart Prompting**: Prompt yang dipersonalisasi untuk setiap user

## 🤖 Multiple Assistant System

### Assistant Manager
- **5 Assistant Support**: AERIS, KAIROS, ZEKE, NOVA, LYRA
- **Independent Personalities**: Setiap assistant punya personality unik
- **Session Management**: Mengelola session string untuk setiap assistant
- **Dynamic Loading**: Load assistant berdasarkan konfigurasi

### Setup Multiple Assistant
1. **Buat Akun Telegram** untuk setiap assistant
2. **Generate Session String** dengan `python manage_assistants.py`
3. **Update .env** dengan session string masing-masing assistant
4. **Restart Bot** untuk load semua assistant

### Assistant Management Commands
- `/assistants` - Lihat status semua assistant
- `/assistant_info [ASSISTANT]` - Info detail assistant
- `/test_assistant [ASSISTANT]` - Test assistant tertentu

## 📝 License

MIT License - see LICENSE file for details