from typing import Any, Dict, Optional, Tuple, Union, List, Callable

from internbootcamp.src.base_evaluator import BaseEvaluator
from internbootcamp.bootcamps.freecell.freecell_reward_manager import FreecellRewardManager

class FreecellEvaluator(BaseEvaluator):
    def __init__(self, api_url: str, api_key: str, api_model: str, reward_manager=FreecellRewardManager, max_turns: int = 5, **kwargs):
        super().__init__(api_url=api_url, api_key=api_key, api_model=api_model, reward_manager=reward_manager, max_turns=max_turns, **kwargs)
    
    def run_evaluation(self, dataset: Optional[List[dict]] = None, dataset_path: Optional[str] = None, output_path: Optional[str] = None, yaml_tool_path: Optional[str] = None, yaml_interaction_path: Optional[str] = 'internbootcamp/bootcamps/freecell/config/freecell_interaction_config.yaml', max_concurrent: int = 1):
        super().run_evaluation(dataset=dataset, dataset_path=dataset_path, output_path=output_path, yaml_tool_path=yaml_tool_path, yaml_interaction_path=yaml_interaction_path, max_concurrent=max_concurrent)
