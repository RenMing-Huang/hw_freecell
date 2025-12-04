import logging
import os
from typing import Any, Optional
from uuid import uuid4

from internbootcamp.bootcamps.freecell.freecell_reward_manager import FreecellRewardManager
from internbootcamp.src.base_interaction import BaseInteraction

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))

class FreecellInteraction(BaseInteraction):
    """
    Interaction class for Freecell task.
    Handles single-turn QA interaction and reward calculation.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self._instance_dict = {}

    async def start_interaction(
        self, instance_id: Optional[str] = None, identity: Optional[dict] = None, **kwargs
    ) -> str:
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "response": "",
            "identity": identity, # Contains ground truth
            "reward": 0.0,
        }
        return instance_id

    async def generate_response(
        self, instance_id: str, messages: list[dict[str, Any]], **kwargs
    ) -> tuple[bool, str, float, dict]:
        content = ""
        # Get the last assistant message
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                content = item.get("content")
                break

        self._instance_dict[instance_id]["response"] = content

        reward = await self.calculate_score(instance_id)
        
        # For single-turn QA, we terminate after one response
        should_terminate_sequence = True
        
        if reward >= 1.0:
            response = "Correct!"
        else:
            response = "Incorrect."

        return should_terminate_sequence, response, reward, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        identity = self._instance_dict[instance_id]["identity"]
        response = self._instance_dict[instance_id]["response"]
        
        # Use FreecellRewardManager to calculate score
        # We assume format_penalty might be passed in config or kwargs, 
        # but for now we rely on default behavior or what's passed.
        # The verify_score method in our manager handles the 0.1 + 0.9 logic.
        
        return FreecellRewardManager.verify_score(
            response,
            identity,
            format_score=0.1,
            format_penalty=False # Can be made configurable
        )

    async def finalize_interaction(self, instance_id: str, **kwargs) -> None:
        if instance_id in self._instance_dict:
            del self._instance_dict[instance_id]
