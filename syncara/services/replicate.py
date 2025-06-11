# services/replicate.py
import json
import requests
from config.config import API_KEY

class ReplicateAPI:
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = "https://api.replicate.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_response(self, prompt, system_prompt=None, temperature=1, top_p=1, max_tokens=4096):
        """
        Generate response using Replicate's GPT-4o model
        """
        url = f"{self.base_url}/models/openai/gpt-4o/predictions"
        
        payload = {
            "stream": False,  # Set to False for simplicity, can be changed to True with proper handling
            "input": {
                "prompt": prompt,
                "temperature": temperature,
                "top_p": top_p,
                "max_completion_tokens": max_tokens
            }
        }
        
        # Add system prompt if provided
        if system_prompt:
            payload["input"]["system_prompt"] = system_prompt
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            # For non-streaming response
            result = response.json()
            
            # Check if prediction is completed or needs to be polled
            if result.get("status") == "succeeded":
                return result.get("output", [""])[0]
            elif result.get("urls", {}).get("get"):
                # Poll for result
                return await self._poll_for_result(result["urls"]["get"])
            else:
                return "Error: Unexpected response format"
                
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"
    
    async def _poll_for_result(self, url, max_retries=10, delay=2):
        """
        Poll for result when the prediction is not immediately available
        """
        import asyncio
        
        for i in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                result = response.json()
                
                if result.get("status") == "succeeded":
                    return result.get("output", [""])[0]
                elif result.get("status") in ["failed", "canceled"]:
                    return f"Error: Prediction {result.get('status')}"
                
                # Wait before polling again
                await asyncio.sleep(delay)
                
            except requests.exceptions.RequestException as e:
                return f"Error polling for result: {str(e)}"
        
        return "Error: Maximum polling retries reached"
