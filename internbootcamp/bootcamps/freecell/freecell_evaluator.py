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
