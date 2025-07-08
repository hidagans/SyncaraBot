# syncara/modules/system_prompt.py
from datetime import datetime
import pytz
from config.config import OWNER_ID
import json
import xml.etree.ElementTree as ET
import glob
import os

class SystemPrompt:
    _instance = None
    _prompts = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the system prompt templates"""
        # Load all system prompts from system_promt folder
        self._load_system_prompts()
        
        # Set default prompt
        self.current_prompt_name = "AERIS"
        
    def _load_system_prompts(self):
        """Load all system prompts from XML files"""
        try:
            # Get all XML files in system_promt folder
            prompt_files = glob.glob("system_promt/*.xml")
            
            for file_path in prompt_files:
                try:
                    # Get prompt name from filename (without extension)
                    prompt_name = os.path.basename(file_path).split('.')[0].upper()
                    
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        
                    # Extract prompt content
                    if ':"""' in content:
                        # Format: NAME:"""content"""
                        prompt_key, prompt_content = content.split(':"""', 1)
                        prompt_content = prompt_content.rsplit('"""', 1)[0]
                    else:
                        # Just use the whole content
                        prompt_key = prompt_name
                        prompt_content = content
                    
                    # Store in prompts dictionary
                    self._prompts[prompt_key] = prompt_content
                    print(f"Loaded system prompt: {prompt_key}")
                    
                except Exception as e:
                    print(f"Error loading prompt from {file_path}: {str(e)}")
            
            print(f"Loaded {len(self._prompts)} system prompts")
            
            # If no prompts loaded, use default
            if not self._prompts:
                SYSTEM_PROMPT = """
Kamu adalah AERIS, asisten AI Telegram yang canggih. Selain menjawab pertanyaan, kamu juga bisa membuat fitur baru (handler shortcode) secara dinamis sesuai permintaan user. Jika ada permintaan fitur baru (misal: poll, quiz, dsb) yang belum ada, balas dengan menawarkan pembuatan handler baru, misal:

"Saya bisa membuat fitur ini! OWNER bisa balas /approve SHORTCODE untuk mengaktifkan, atau /reject SHORTCODE untuk membatalkan."

Gunakan format shortcode sesuai permintaan user. Handler baru akan aktif setelah OWNER approve.
"""
                self._prompts["DEFAULT"] = SYSTEM_PROMPT
                print("Using default prompt")
                
        except Exception as e:
            print(f"Error loading system prompts: {str(e)}")
            # Use default prompt as fallback
            SYSTEM_PROMPT = """
Kamu adalah AERIS, asisten AI Telegram yang canggih. Selain menjawab pertanyaan, kamu juga bisa membuat fitur baru (handler shortcode) secara dinamis sesuai permintaan user. Jika ada permintaan fitur baru (misal: poll, quiz, dsb) yang belum ada, balas dengan menawarkan pembuatan handler baru, misal:

"Saya bisa membuat fitur ini! OWNER bisa balas /approve SHORTCODE untuk mengaktifkan, atau /reject SHORTCODE untuk membatalkan."

Gunakan format shortcode sesuai permintaan user. Handler baru akan aktif setelah OWNER approve.
"""
            self._prompts["DEFAULT"] = SYSTEM_PROMPT
    
    def set_prompt(self, prompt_name):
        """Set the current prompt by name"""
        prompt_name = prompt_name.upper()
        if prompt_name in self._prompts:
            self.current_prompt_name = prompt_name
            return True
        return False
    
    def get_available_prompts(self):
        """Get list of available prompt names"""
        return list(self._prompts.keys())

    def to_json(self):
        """Convert instance to JSON serializable format"""
        return {
            "current_prompt": self.current_prompt_name,
            "available_prompts": list(self._prompts.keys())
        }

    @staticmethod
    def is_owner(user_id: int) -> bool:
        """Check if user is an owner"""
        return str(user_id) in [str(id) for id in OWNER_ID]

    @staticmethod
    def get_owner_section(user_id: int) -> str:
        """Get the owner section text based on user status"""
        if SystemPrompt.is_owner(user_id):
            return """🔑 OWNER MODE ACTIVE 
- Kamu sedang berbicara dengan owner-ku!
- Aku akan memberikan akses penuh ke semua fitur.
- Perintah administratif dan system settings tersedia.
- Prioritas respons maksimal! """
        return ""

    def get_chat_prompt(self, context: dict) -> str:
        """Get the formatted system prompt with current context"""
        try:
            # Get current time in Asia/Jakarta timezone
            tz = pytz.timezone('Asia/Jakarta')
            current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
            
            # Get shortcode capabilities from registry
            try:
                from syncara.shortcode import registry
                shortcode_capabilities = registry.get_shortcode_docs()
                print(f"Shortcode capabilities loaded: {len(registry.descriptions)} descriptions")
            except ImportError as e:
                print(f"Import error for shortcode registry: {e}")
                try:
                    # Fallback to direct import
                    from syncara.shortcode import SHORTCODE_DESCRIPTIONS
                    shortcode_capabilities = "Available Shortcodes:\n"
                    for shortcode, desc in SHORTCODE_DESCRIPTIONS.items():
                        shortcode_capabilities += f"- [{shortcode}] - {desc}\n"
                except ImportError as e2:
                    print(f"Fallback import error: {e2}")
                    shortcode_capabilities = "Shortcode system not available"
            except Exception as e:
                print(f"Error getting shortcode capabilities: {e}")
                shortcode_capabilities = "Shortcode system not available"
            
            # Add shortcode execution order guidelines
            shortcode_capabilities += "\n\n📋 SHORTCODE EXECUTION GUIDELINES:\n"
            shortcode_capabilities += "- ALWAYS create files before trying to export/show/edit them\n"
            shortcode_capabilities += "- Use CANVAS:CREATE before CANVAS:EXPORT\n"
            shortcode_capabilities += "- Use CANVAS:LIST to check available files first\n"
            shortcode_capabilities += "- Check admin privileges before using USER/GROUP commands\n"
            shortcode_capabilities += "- Test shortcodes in correct order to avoid failures\n"
            
            # Default values
            bot_name = context.get('bot_name', 'Syncara')
            bot_username = context.get('bot_username', 'SyncaraBot')
            user_id = context.get('user_id', 0)
            
            # Get owner list from config
            owner_list = ', '.join([str(id) for id in OWNER_ID])
            
            # Get owner section based on user_id
            is_owner_section = self.get_owner_section(user_id)
            
            # Get the current prompt template
            prompt_template = self._prompts.get(
                self.current_prompt_name, 
                self._prompts.get("DEFAULT", "")
            )
            
            # Format the prompt with all variables
            return prompt_template.format(
                botName=bot_name,
                botUsername=bot_username,
                ownerList=owner_list,
                isOwnerSection=is_owner_section,
                currentTime=current_time,
                shortcode_capabilities=shortcode_capabilities
            )
        except Exception as e:
            print(f"Error in get_chat_prompt: {str(e)}")
            return ""

# Create singleton instance
system_prompt = SystemPrompt()