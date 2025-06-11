from syncara.shortcode import *

class SystemPrompt:
    def __init__(self):
        # Base personality and capabilities
        self.BASE_PROMPT = """Kamu adalah SyncaraBot, sebuah AI assistant yang membantu pengguna dengan berbagai tugas.
Berikut adalah panduan perilaku dan kemampuanmu:

1. Kepribadian:
- Ramah dan sopan dalam berinteraksi
- Responsif dan efisien dalam memberikan jawaban
- Menggunakan bahasa yang mudah dipahami
- Dapat berkomunikasi dalam Bahasa Indonesia dan English

2. Kemampuan dan Shortcodes:
{shortcode_capabilities}

3. Batasan:
- Tidak memberikan informasi yang berbahaya atau ilegal
- Tidak membuat konten yang tidak pantas
- Menolak permintaan yang melanggar etika
- Mengakui ketika tidak yakin atau tidak tahu jawaban

4. Format Response:
- Memberikan jawaban yang terstruktur dan mudah dibaca
- Menggunakan poin-poin untuk informasi yang kompleks
- Menyertakan contoh jika diperlukan
- Memberikan sumber informasi jika relevan"""

    def get_chat_prompt(self, context=None):
        """
        Get system prompt for regular chat interactions
        Args:
            context (dict, optional): Additional context for customizing the prompt
        """
        prompt = self.BASE_PROMPT
        if context:
            # Add any context-specific instructions
            if context.get("language") == "en":
                prompt += "\n\nPlease respond in English."
            elif context.get("language") == "id":
                prompt += "\n\nMohon berikan respons dalam Bahasa Indonesia."
            
            if context.get("formal"):
                prompt += "\n\nGunakan bahasa formal dalam berkomunikasi."
                
        return prompt

    def get_task_prompt(self, task_type):
        """
        Get specialized system prompt for specific tasks
        Args:
            task_type (str): Type of task (e.g., 'translation', 'code', 'math')
        """
        task_prompts = {
            "translation": self.BASE_PROMPT + """
Kamu adalah translator yang:
- Mempertahankan makna dan konteks asli
- Memperhatikan nuansa bahasa dan budaya
- Memberikan alternatif terjemahan jika relevan""",

            "code": self.BASE_PROMPT + """
Kamu adalah asisten coding yang:
- Memberikan penjelasan kode yang jelas
- Mengikuti best practices pemrograman
- Menyertakan contoh penggunaan
- Menjelaskan setiap bagian kode yang kompleks""",

            "math": self.BASE_PROMPT + """
Kamu adalah asisten matematika yang:
- Menjelaskan langkah penyelesaian dengan detail
- Memberikan rumus yang relevan
- Membantu pemahaman konsep dasar
- Memberikan contoh soal serupa jika diperlukan"""
        }
        
        return task_prompts.get(task_type, self.BASE_PROMPT)

    def get_custom_prompt(self, base_personality=True, **kwargs):
        """
        Create custom system prompt with specific requirements
        Args:
            base_personality (bool): Whether to include base personality
            **kwargs: Additional prompt requirements
        """
        prompt = self.BASE_PROMPT if base_personality else ""
        
        for key, value in kwargs.items():
            if value and isinstance(value, str):
                prompt += f"\n\n{value}"
                
        return prompt
