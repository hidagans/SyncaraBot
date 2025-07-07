from syncara.services.replicate import generate_image
from syncara.console import console

class ImageGenerationShortcode:
    def __init__(self):
        self.handlers = {
            'IMAGE:GEN': self.image_gen,
        }
        self.descriptions = {
            'IMAGE:GEN': 'Generate image from text prompt. Usage: [IMAGE:GEN:prompt]'
        }

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
                await message.reply(f"❌ Format JSON tidak valid: {e}")
                return False
        else:
            image = mask = seed = resolution = style_type = aspect_ratio = magic_prompt_option = style_reference_images = None
        if not prompt:
            await message.reply("❌ Prompt tidak boleh kosong. Contoh: [IMAGE:GEN:kucing lucu di luar angkasa]")
            return False
        try:
            await message.reply("🎨 Sedang membuat gambar... Mohon tunggu.")
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
            await message.reply_photo(image_url, caption=f"Prompt: {prompt}")
            return True
        except Exception as e:
            console.error(f"[IMAGEGEN] Error: {e}")
            await message.reply(f"❌ Gagal generate gambar: {e}")
            return False 