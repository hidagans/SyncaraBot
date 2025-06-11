import replicate
import asyncio
from config.config import API_KEY
import base64
import requests
from io import BytesIO

class ReplicateAPI:
    def __init__(self):
        replicate.api_token = API_KEY

    async def download_image_as_base64(self, file_id, client):
        try:
            # Download the file
            file_path = await client.download_media(file_id, in_memory=True)
            
            # Convert to base64
            if isinstance(file_path, BytesIO):
                base64_image = base64.b64encode(file_path.getvalue()).decode('utf-8')
                return f"data:image/jpeg;base64,{base64_image}"
            return None
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            return None

    async def generate_response(self, prompt, system_prompt=None, temperature=1, top_p=1, max_tokens=4096, image_file_id=None, client=None):
        try:
            # Prepare input parameters
            input_params = {
                "prompt": prompt,
                "temperature": temperature,
                "top_p": top_p,
                "max_completion_tokens": max_tokens
            }
            
            # If image is provided, download and add to input
            if image_file_id and client:
                image_data = await self.download_image_as_base64(image_file_id, client)
                if image_data:
                    input_params["image_input"] = [image_data]
            
            # Add system prompt if provided
            if system_prompt:
                input_params["system_prompt"] = system_prompt

            # Run the model using the official client
            output = replicate.run(
                "openai/gpt-4o",  # Changed to vision model
                input=input_params
            )

            # Since output is an iterator, we need to join the chunks
            result = ""
            for item in output:
                result += str(item)

            return result if result.strip() else "No valid response generated"

        except Exception as e:
            return f"Error: {str(e)}"

    async def generate_response_stream(self, prompt, system_prompt=None, temperature=1, top_p=1, max_tokens=4096, image_file_id=None, client=None):
        try:
            # Prepare input parameters
            input_params = {
                "prompt": prompt,
                "temperature": temperature,
                "top_p": top_p,
                "max_completion_tokens": max_tokens
            }
            
            # If image is provided, download and add to input
            if image_file_id and client:
                image_data = await self.download_image_as_base64(image_file_id, client)
                if image_data:
                    input_params["image_input"] = [image_data]
            
            # Add system prompt if provided
            if system_prompt:
                input_params["system_prompt"] = system_prompt

            # Stream the output
            for event in replicate.stream(
                "openai/gpt-4-vision-preview",  # Changed to vision model
                input=input_params
            ):
                yield str(event)

        except Exception as e:
            yield f"Error: {str(e)}"
