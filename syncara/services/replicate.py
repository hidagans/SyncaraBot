# services/replicate.py
import json
import requests
from config.config import API_KEY
import asyncio

class ReplicateAPI:
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = "https://api.replicate.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def generate_response(self, prompt, system_prompt=None, temperature=1, top_p=1, max_tokens=4096):
        url = f"{self.base_url}/models/openai/gpt-4o/predictions"
        payload = {
            "stream": False,
            "input": {
                "prompt": prompt,
                "temperature": temperature,
                "top_p": top_p,
                "max_completion_tokens": max_tokens
            }
        }
        if system_prompt:
            payload["input"]["system_prompt"] = system_prompt
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            result = response.json()
            if result.get("status") == "succeeded":
                output = result.get("output", [""])[0]
                return str(output) if output is not None else ""
            elif result.get("urls", {}).get("get"):
                return str(await self._poll_for_result(result["urls"]["get"]))
            else:
                return "Error: Unexpected response format"
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"

    async def _poll_for_result(self, url, max_retries=10, delay=2):
        for i in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                result = response.json()

                if result.get("status") == "succeeded":
                    return result.get("output", [""])[0]
                elif result.get("status") in ["failed", "canceled"]:
                    return f"Error: Prediction {result.get('status')}"

                await asyncio.sleep(delay)

            except requests.exceptions.RequestException as e:
                return f"Error polling for result: {str(e)}"

        return "Error: Maximum polling retries reached"
