import replicate
import asyncio
from config.config import API_KEY
import base64
import requests
from io import BytesIO
import httpx
import os
from syncara import console

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

REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
REPLICATE_API_URL = "https://api.replicate.com/v1/predictions"

HEADERS = {
    "Authorization": f"Token {REPLICATE_API_TOKEN}",
    "Content-Type": "application/json"
}

async def run_replicate_model(model: str, version: str, input_data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        payload = {
            "version": version,
            "input": input_data
        }
        response = await client.post(REPLICATE_API_URL, headers=HEADERS, json=payload, timeout=120)
        response.raise_for_status()
        prediction = response.json()
        # Poll for result
        prediction_id = prediction["id"]
        status = prediction["status"]
        while status not in ("succeeded", "failed", "canceled"):
            await asyncio.sleep(2)
            poll = await client.get(f"{REPLICATE_API_URL}/{prediction_id}", headers=HEADERS)
            poll.raise_for_status()
            prediction = poll.json()
            status = prediction["status"]
        return prediction

# Image generation (inpainting & text2img) dengan model ideogram-ai/ideogram-v3-balanced
async def generate_image(
    prompt: str,
    image: str = None,
    mask: str = None,
    seed: int = None,
    resolution: str = None,
    style_type: str = None,
    aspect_ratio: str = None,
    magic_prompt_option: str = None,
    style_reference_images: list = None
) -> str:
    """
    Generate image using Replicate model (ideogram-ai/ideogram-v3-balanced)
    Returns: URL hasil gambar
    """
    model = "ideogram-ai/ideogram-v3-balanced"
    version = None  # Gunakan versi default terbaru
    input_data = {
        "prompt": prompt
    }
    if image:
        input_data["image"] = image
    if mask:
        input_data["mask"] = mask
    if seed is not None:
        input_data["seed"] = seed
    if resolution:
        input_data["resolution"] = resolution
    if style_type:
        input_data["style_type"] = style_type
    if aspect_ratio:
        input_data["aspect_ratio"] = aspect_ratio
    if magic_prompt_option:
        input_data["magic_prompt_option"] = magic_prompt_option
    if style_reference_images:
        input_data["style_reference_images"] = style_reference_images

    console.info(f"[IMAGEGEN] Request: {input_data}")
    result = await run_replicate_model(model, version, input_data)
    if result["status"] == "succeeded":
        output = result.get("output")
        if isinstance(output, list) and output:
            return output[0]  # URL gambar
        elif isinstance(output, str):
            return output
        else:
            raise Exception("No image output from model")
    else:
        raise Exception(f"Image generation failed: {result.get('error', result['status'])}")
