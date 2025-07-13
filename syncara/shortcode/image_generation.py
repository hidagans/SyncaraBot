from syncara.services.replicate import generate_image
from syncara.console import console
import asyncio

class ImageGenerationShortcode:
    def __init__(self):
        self.handlers = {
            'IMAGE:GEN': self.image_gen,
        }
        self.descriptions = {
            'IMAGE:GEN': 'Generate image from text prompt. Usage: [IMAGE:GEN:prompt]'
        }
        self.pending_images = {}

    async def image_gen(self, client, message, params):
        """
        Shortcode: [IMAGE:GEN:prompt]
        Optionally support JSON for advanced params.
        """
        import json
        prompt = params.strip()
        # Advanced: jika params diawali '{', anggap JSON
        if prompt.startswith('{'):
            try:
                data = json.loads(prompt)
                prompt = data.get('prompt')
                image = data.get('image')
                mask = data.get('mask')
                seed = data.get('seed')
                resolution = data.get('resolution')
                style_type = data.get('style_type')
                aspect_ratio = data.get('aspect_ratio')
                magic_prompt_option = data.get('magic_prompt_option')
                style_reference_images = data.get('style_reference_images')
            except Exception as e:
                console.error(f"[IMAGE:GEN] Invalid JSON: {e}")
                return False
        else:
            image = mask = seed = resolution = style_type = aspect_ratio = magic_prompt_option = style_reference_images = None
            
        if not prompt:
            console.error("[IMAGE:GEN] Empty prompt")
            return False
            
        try:
            # Generate image
            image_url = await generate_image(
                prompt=prompt,
                image=image,
                mask=mask,
                seed=seed,
                resolution=resolution,
                style_type=style_type,
                aspect_ratio=aspect_ratio,
                magic_prompt_option=magic_prompt_option,
                style_reference_images=style_reference_images
            )
            
            # Store for delayed sending
            image_id = f"image_{message.id}_{len(self.pending_images)}"
            self.pending_images[image_id] = {
                'image_url': image_url,
                'prompt': prompt,
                'chat_id': message.chat.id,
                'reply_to_message_id': message.id
            }
            
            console.info(f"[IMAGE:GEN] Generated image for delayed sending: {image_id}")
            return image_id
            
        except Exception as e:
            console.error(f"[IMAGE:GEN] Error: {e}")
            return False
    
    async def send_pending_images(self, client, image_ids):
        """Send pending images"""
        sent_images = []
        
        for image_id in image_ids:
            if image_id in self.pending_images:
                image_data = self.pending_images[image_id]
                
                try:
                    await client.send_photo(
                        chat_id=image_data['chat_id'],
                        photo=image_data['image_url'],
                        caption=f"🎨 Prompt: {image_data['prompt']}",
                        reply_to_message_id=image_data['reply_to_message_id']
                    )
                    sent_images.append(image_id)
                    console.info(f"[IMAGE:GEN] Sent image: {image_id}")
                    
                except Exception as e:
                    console.error(f"[IMAGE:GEN] Error sending image {image_id}: {e}")
                    
                # Clean up
                del self.pending_images[image_id]
                
        return sent_images

# Create instance untuk diimpor oleh __init__.py
image_shortcode = ImageGenerationShortcode() 