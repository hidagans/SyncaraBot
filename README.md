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

# Userbot Session String
SESSION_STRING=your_session_string_here

# MongoDB Configuration (optional)
MONGO_URI=your_mongodb_uri_here
DB_NAME=syncara_bot
```

### 3. Generate Session String
```bash
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
- `/analytics [user_id]` - Lihat analytics user (owner only)
- `/learning_insights [user_id]` - Lihat insight pembelajaran (owner only)

### AI Assistant (@Aeris_sync)
- **Private Chat** - Kirim pesan langsung
- **Group Chat** - Mention atau reply ke assistant

## 🔧 System Prompts

Bot mendukung multiple personality:
- **AERIS** - Default assistant dengan AI learning yang canggih
- **KAIROS** - Time-based responses
- **ZEKE** - Technical assistant dengan reasoning tingkat tinggi
- **NOVA** - Creative assistant
- **LYRA** - Music-focused assistant

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

## 📝 License

MIT License - see LICENSE file for details