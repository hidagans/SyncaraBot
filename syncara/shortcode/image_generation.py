from syncara.services.replicate import generate_image
from syncara.console import console
from datetime import datetime
import asyncio
import json
from typing import Dict, Any, Optional

class ImageGenerationShortcode:
    def __init__(self):
        self.handlers = {
            'IMAGE:GEN': self.image_gen,
            'IMAGE:HISTORY': self.image_history,
            'IMAGE:STATS': self.image_stats,
        }
        self.descriptions = {
            'IMAGE:GEN': 'Generate image from text prompt. Usage: [IMAGE:GEN:prompt]',
            'IMAGE:HISTORY': 'Show image generation history. Usage: [IMAGE:HISTORY:]',
            'IMAGE:STATS': 'Show image generation statistics. Usage: [IMAGE:STATS:]',
        }
        self.pending_images = {}
        self._db_initialized = False

    async def _ensure_db_connection(self):
        """Ensure database connection is available"""
        if not self._db_initialized:
            try:
                from syncara.database import image_generations, image_history, log_system_event, log_error
                self.image_generations = image_generations
                self.image_history = image_history
                self.log_system_event = log_system_event
                self.log_error = log_error
                self._db_initialized = True
            except ImportError:
                console.error("Database not available for image generation persistence")

    async def image_gen(self, client, message, params):
        """
        Shortcode: [IMAGE:GEN:prompt]
        Optionally support JSON for advanced params.
        """
        try:
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
            
            # Record generation request to database
            generation_id = await self._record_generation_request(
                user_id=message.from_user.id,
                chat_id=message.chat.id,
                prompt=prompt,
                advanced_params={
                    'image': image,
                    'mask': mask,
                    'seed': seed,
                    'resolution': resolution,
                    'style_type': style_type,
                    'aspect_ratio': aspect_ratio,
                    'magic_prompt_option': magic_prompt_option,
                    'style_reference_images': style_reference_images
                }
            )
            
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
            
            if image_url:
                # Store the generated image info
                image_id = f"image_{message.id}_{generation_id}"
            self.pending_images[image_id] = {
                    'url': image_url,
                'prompt': prompt,
                'chat_id': message.chat.id,
                    'reply_to_message_id': message.id,
                    'generation_id': generation_id
                }
                
                # Update database with successful generation
                await self._update_generation_result(generation_id, True, image_url)
                
                console.info(f"[IMAGE:GEN] Generated image: {image_url}")
                return image_id
            else:
                console.error("[IMAGE:GEN] Failed to generate image")
                # Update database with failed generation
                await self._update_generation_result(generation_id, False, None, "Failed to generate image")
                return False
                
        except Exception as e:
            console.error(f"[IMAGE:GEN] Error: {str(e)}")
            await self._log_error("image_generation", f"Error generating image: {str(e)}")
            return False

    async def image_history(self, client, message, params):
        """Show image generation history for user"""
        try:
            console.info(f"[IMAGE:HISTORY] called for user: {message.from_user.id}")
            
            # Get user's image generation history
            history = await self._get_user_image_history(message.from_user.id, limit=10)
            
            if not history:
                await client.send_message(
                    chat_id=message.chat.id,
                    text='🎨 Anda belum pernah generate gambar.\n\nGunakan [IMAGE:GEN:prompt] untuk membuat gambar pertama!',
                    reply_to_message_id=message.id
                )
                return True
            
            # Format history
            response = f'🎨 **History Generate Gambar (10 terakhir):**\n\n'
            for i, entry in enumerate(history, 1):
                timestamp = entry.get('created_at', datetime.utcnow()).strftime('%d/%m %H:%M')
                prompt = entry.get('prompt', 'Unknown')[:50] + "..." if len(entry.get('prompt', '')) > 50 else entry.get('prompt', '')
                status = "✅ Berhasil" if entry.get('success', False) else "❌ Gagal"
                
                response += f'**{i}.** {timestamp}\n'
                response += f'📝 {prompt}\n'
                response += f'📊 {status}\n\n'
            
            await client.send_message(
                chat_id=message.chat.id,
                text=response,
                reply_to_message_id=message.id
            )
            return True
            
        except Exception as e:
            console.error(f"[IMAGE:HISTORY] Error: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f'❌ Gagal mengambil history: {str(e)}',
                reply_to_message_id=message.id
            )
            return False

    async def image_stats(self, client, message, params):
        """Show image generation statistics"""
        try:
            console.info(f"[IMAGE:STATS] called for user: {message.from_user.id}")
            
            # Get user's image generation stats
            stats = await self._get_user_image_stats(message.from_user.id)
            
            if not stats:
                await client.send_message(
                    chat_id=message.chat.id,
                    text='📊 Belum ada statistik generate gambar.',
                    reply_to_message_id=message.id
                )
                return True
            
            # Format statistics
            response = f'📊 **Statistik Generate Gambar:**\n\n'
            response += f'🎨 **Total Requests:** {stats.get("total_requests", 0)}\n'
            response += f'✅ **Successful:** {stats.get("successful", 0)}\n'
            response += f'❌ **Failed:** {stats.get("failed", 0)}\n'
            response += f'📈 **Success Rate:** {stats.get("success_rate", 0):.1f}%\n\n'
            
            if stats.get("most_recent"):
                recent = stats["most_recent"]
                response += f'🕒 **Most Recent:** {recent.get("created_at", "").strftime("%d/%m %H:%M")}\n'
                response += f'📝 {recent.get("prompt", "")[:50]}...\n'
            
            await client.send_message(
                chat_id=message.chat.id,
                text=response,
                reply_to_message_id=message.id
            )
            return True
            
        except Exception as e:
            console.error(f"[IMAGE:STATS] Error: {str(e)}")
            await client.send_message(
                chat_id=message.chat.id,
                text=f'❌ Gagal mengambil statistik: {str(e)}',
                reply_to_message_id=message.id
            )
            return False
    
    async def send_pending_images(self, client, image_ids):
        """Send pending images with delay"""
        if not image_ids:
            return
            
        sent_images = []
        
        for image_id in image_ids:
            if image_id in self.pending_images:
                image_data = self.pending_images[image_id]
                
                try:
                    await client.send_photo(
                        chat_id=image_data['chat_id'],
                        photo=image_data['url'],
                        caption=f"🎨 **Generated Image**\n\n📝 Prompt: {image_data['prompt']}\n\n🔗 [Full Resolution]({image_data['url']})",
                        reply_to_message_id=image_data['reply_to_message_id']
                    )
                    
                    # Record successful delivery
                    await self._record_image_delivery(image_data['generation_id'], True)
                    
                    sent_images.append(image_id)
                    console.info(f"[IMAGE:GEN] Sent image: {image_id}")
                    
                except Exception as e:
                    console.error(f"[IMAGE:GEN] Error sending image {image_id}: {e}")
                    # Record failed delivery
                    await self._record_image_delivery(image_data['generation_id'], False, str(e))
                    
                # Clean up
                del self.pending_images[image_id]
                
        return sent_images 

    # ==================== DATABASE OPERATIONS ====================
    
    async def _record_generation_request(self, user_id: int, chat_id: int, prompt: str, advanced_params: Dict[str, Any] = None) -> str:
        """Record image generation request to database"""
        try:
            await self._ensure_db_connection()
            
            generation_doc = {
                'user_id': user_id,
                'chat_id': chat_id,
                'prompt': prompt,
                'advanced_params': advanced_params or {},
                'created_at': datetime.utcnow(),
                'success': None,  # Will be updated later
                'image_url': None,
                'error_message': None,
                'delivered': False,
                'delivery_error': None
            }
            
            result = await self.image_generations.insert_one(generation_doc)
            generation_id = str(result.inserted_id)
            
            await self.log_system_event("info", "image_generation", f"Image generation requested by user {user_id}")
            
            return generation_id
            
        except Exception as e:
            console.error(f"Error recording generation request: {str(e)}")
            return "unknown"

    async def _update_generation_result(self, generation_id: str, success: bool, image_url: str = None, error_message: str = None):
        """Update generation result in database"""
        try:
            await self._ensure_db_connection()
            
            update_doc = {
                'success': success,
                'completed_at': datetime.utcnow()
            }
            
            if success and image_url:
                update_doc['image_url'] = image_url
            elif not success and error_message:
                update_doc['error_message'] = error_message
            
            from bson import ObjectId
            await self.image_generations.update_one(
                {'_id': ObjectId(generation_id)},
                {'$set': update_doc}
            )
            
        except Exception as e:
            console.error(f"Error updating generation result: {str(e)}")

    async def _record_image_delivery(self, generation_id: str, delivered: bool, delivery_error: str = None):
        """Record image delivery status"""
        try:
            await self._ensure_db_connection()
            
            update_doc = {
                'delivered': delivered,
                'delivered_at': datetime.utcnow()
            }
            
            if not delivered and delivery_error:
                update_doc['delivery_error'] = delivery_error
            
            from bson import ObjectId
            await self.image_generations.update_one(
                {'_id': ObjectId(generation_id)},
                {'$set': update_doc}
            )
            
        except Exception as e:
            console.error(f"Error recording image delivery: {str(e)}")

    async def _get_user_image_history(self, user_id: int, limit: int = 10) -> list:
        """Get user's image generation history"""
        try:
            await self._ensure_db_connection()
            
            history = await self.image_generations.find(
                {'user_id': user_id}
            ).sort('created_at', -1).limit(limit).to_list(length=None)
            
            return history
            
        except Exception as e:
            console.error(f"Error getting user image history: {str(e)}")
            return []

    async def _get_user_image_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user's image generation statistics"""
        try:
            await self._ensure_db_connection()
            
            # Get all generations for user
            all_generations = await self.image_generations.find(
                {'user_id': user_id}
            ).to_list(length=None)
            
            if not all_generations:
                return {}
            
            total_requests = len(all_generations)
            successful = len([g for g in all_generations if g.get('success', False)])
            failed = total_requests - successful
            success_rate = (successful / total_requests) * 100 if total_requests > 0 else 0
            
            # Get most recent generation
            most_recent = max(all_generations, key=lambda x: x.get('created_at', datetime.min))
            
            return {
                'total_requests': total_requests,
                'successful': successful,
                'failed': failed,
                'success_rate': success_rate,
                'most_recent': most_recent
            }
            
        except Exception as e:
            console.error(f"Error getting user image stats: {str(e)}")
            return {}

    async def _log_error(self, module: str, error: str):
        """Log error to database"""
        try:
            await self.log_error(module, error)
        except:
            pass

# Create instance untuk diimpor oleh __init__.py
image_shortcode = ImageGenerationShortcode() 