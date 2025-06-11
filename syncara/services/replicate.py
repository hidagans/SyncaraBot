import replicate
import asyncio
from config.config import API_KEY

class ReplicateAPI:
    def __init__(self):
        # Set the REPLICATE_API_TOKEN environment variable
        replicate.api_token = API_KEY

    async def generate_response(self, prompt, system_prompt=None, temperature=1, top_p=1, max_tokens=4096):
        try:
            # Prepare input parameters
            input_params = {
                "prompt": prompt,
                "temperature": temperature,
                "top_p": top_p,
                "max_completion_tokens": max_tokens
            }
            
            # Add system prompt if provided
            if system_prompt:
                input_params["system_prompt"] = system_prompt

            # Run the model using the official client
            output = replicate.run(
                "openai/gpt-4o",
                input=input_params
            )

            # Since output is an iterator, we need to join the chunks
            result = ""
            for item in output:
                result += str(item)

            return result if result.strip() else "No valid response generated"

        except Exception as e:
            return f"Error: {str(e)}"

    async def generate_response_stream(self, prompt, system_prompt=None, temperature=1, top_p=1, max_tokens=4096):
        try:
            # Prepare input parameters
            input_params = {
                "prompt": prompt,
                "temperature": temperature,
                "top_p": top_p,
                "max_completion_tokens": max_tokens
            }
            
            # Add system prompt if provided
            if system_prompt:
                input_params["system_prompt"] = system_prompt

            # Stream the output
            for event in replicate.stream(
                "openai/gpt-4o",
                input=input_params
            ):
                yield str(event)

        except Exception as e:
            yield f"Error: {str(e)}"
