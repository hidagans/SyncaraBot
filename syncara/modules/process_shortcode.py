import re

async def process_shortcode(client, message, text):
    """Process shortcodes in AI response text"""
    try:
        # Import registry di dalam fungsi untuk menghindari circular import
        from syncara.shortcode import registry
        from syncara.console import console
        
        # Pattern untuk mendeteksi shortcode [CATEGORY:ACTION] atau [CATEGORY:ACTION:PARAMS]
        pattern = r'\[([^:]+):([^:\]]+)(?::([^\]]*))?\]'
        
        # Temukan semua shortcode dalam text
        matches = re.finditer(pattern, text)
        
        for match in matches:
            try:
                full_match = match.group(0)  # Shortcode lengkap [CATEGORY:ACTION] atau [CATEGORY:ACTION:PARAMS]
                category = match.group(1)    # Contoh: GROUP atau CHANNEL
                action = match.group(2)      # Contoh: PIN_MESSAGE atau START
                params = match.group(3)      # Contoh: message_id atau None untuk shortcode tanpa params
                
                # Handle None params (for shortcodes without parameters)
                if params is None:
                    params = ""
                else:
                    # Handle current_message_id
                    if "current_message_id" in params:
                        params = params.replace("current_message_id", str(message.id))
                
                # Construct shortcode key
                shortcode_key = f"{category}:{action}"
                
                # Execute shortcode using registry
                success = await registry.execute_shortcode(
                    shortcode_key, 
                    client, 
                    message, 
                    params
                )
                
                # Hapus shortcode dari text jika berhasil diproses
                if success:
                    text = text.replace(full_match, '')
                else:
                    console.warning(f"Shortcode not found or failed: {shortcode_key}")
                
            except Exception as e:
                console.error(f"Error processing shortcode {match.group(0)}: {str(e)}")
                continue
        
        # Bersihkan multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
        
    except Exception as e:
        # Import console di sini juga untuk error handling
        try:
            from syncara.console import console
            console.error(f"Error in process_shortcode: {str(e)}")
        except:
            print(f"Error in process_shortcode: {str(e)}")
        return text