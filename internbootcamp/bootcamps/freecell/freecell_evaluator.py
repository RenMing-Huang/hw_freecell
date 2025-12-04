import os
import httpx
import openai
from internbootcamp.src.base_evaluator import BaseEvaluator

class FreecellEvaluator(BaseEvaluator):
    def __init__(self, api_timeout: int = None, **kwargs):
        super().__init__(**kwargs)
        
        # Get timeout from env var if not provided, default to 300s
        if api_timeout is None:
            api_timeout = int(os.getenv("API_TIMEOUT", 300))
            
        # Configure timeout for httpx client to prevent indefinite hangs
        timeout = httpx.Timeout(
            connect=60.0,      # Time to establish connection
            read=float(api_timeout),  # Time to read response (configurable)
            write=60.0,        # Time to send request
            pool=60.0          # Time to acquire connection from pool
        )
        
        # Re-initialize client with timeout configuration
        self.client = openai.AsyncOpenAI(
            base_url=self.client.base_url, 
            api_key=self.client.api_key, 
            default_headers=self.api_extra_headers, 
            http_client=httpx.AsyncClient(verify=False, timeout=timeout),
            timeout=float(api_timeout)
        )
        # Vision support toggle (gpt-oss via vLLM Harmony often expects only text content)
        # Opt-in via env BOOTCAMP_SUPPORTS_VISION=true
        self.supports_vision = str(os.getenv("BOOTCAMP_SUPPORTS_VISION", "false")).lower() in ("1","true","yes")

    def _build_payload(self, input_data: dict) -> dict:
        messages = input_data["messages"]
        # If images present but vision not supported, strip image packaging and keep text-only
        if not self.supports_vision and input_data.get("image"):
            # Keep messages as provided (string content). Do not convert to multimodal content list.
            pass
        else:
            # For vision-capable models, allow BaseEvaluator to embed images
            if input_data.get("image"):
                # Defer to BaseEvaluator to handle image embedding
                return super()._build_payload({
                    "messages": self._prepare_mm_messages(input_data),
                    "tools": input_data.get("tools"),
                    "tool_choice": input_data.get("tool_choice", "auto")
                })
        return super()._build_payload(input_data)

    def _prepare_mm_messages(self, input_data: dict):
        messages = input_data["messages"].copy()
        prompt = messages[0]["content"] if messages and isinstance(messages[0], dict) else ""
        image_path_list = input_data["image"]
        content_list = [{"type": "text", "text": prompt}]
        for image_item in image_path_list:
            # Let BaseEvaluator handle base64 conversion downstream
            content_list.append({
                "type": "image_url",
                "image_url": {"url": image_item}
            })
        return [{"role": "user", "content": content_list}]
