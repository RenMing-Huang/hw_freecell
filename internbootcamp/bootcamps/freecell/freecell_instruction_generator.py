import json
import os
from typing import Dict, Any, Optional, List
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from internbootcamp.utils.freecell.path_utils import resolve_image_paths


class FreecellInstructionGenerator(BaseInstructionGenerator):
    """Freecell instruction generator for transforming raw data to evaluation format."""
    
    def __init__(self, raw_data_path: str):
        """
        Initialize Freecell instruction generator.
        
        Args:
            raw_data_path: Path to the raw Freecell data file (JSON/JSONL)
        """
        super().__init__()
        self.raw_data_path = raw_data_path
        self._load_data()
    
    def _load_data(self):
        """Load raw data from file."""
        with open(self.raw_data_path, 'r', encoding='utf-8') as f:
            if self.raw_data_path.endswith('.jsonl'):
                self.raw_data = [json.loads(line) for line in f if line.strip()]
            else:
                self.raw_data = json.load(f)
        
        # Filter for freecell tasks only
        if isinstance(self.raw_data, list):
            self.raw_data = [
                item for item in self.raw_data 
                if "free_cell" in item.get("data_id", "")
            ]
    
    def case_generator(self):
        """
        Generate evaluation cases from raw data.
        
        Yields:
            Dict[str, Any]: Case with identity information
        """
        for item in self.raw_data:
            # Get question/query
            question = item.get("query") or item.get("question", "")
            if not question:
                continue
            
            # Get answer/solution
            answer = item.get("solution") or item.get("answer")
            if answer is None:
                continue
            
            # Convert to int
            try:
                answer = int(answer)
            except (ValueError, TypeError):
                continue
            
            # Yield identity for this case
            yield {
                "question": question,
                "answer": answer,
                "data_id": item.get("data_id"),
                "question_id": item.get("question_id"),
                "images": item.get("images", [])
            }
    
    def prompt_func(self, identity: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate a loop-safe prompt that allows concise CoT but enforces a strict final answer format.

        Contract:
        - Input: identity with key 'question' (str)
        - Output: single user message so image-flow keeps instructions
        - Final line must be exactly: The answer is N (N is an integer). No extra numbers after it.
        - If reasoning is needed, put it inside <think>...</think> above the final line.
        """
        question = identity["question"]
        instruction = (
            "Task: Read the question (and image if provided) and select exactly one option index.\n\n"
            "If you need to reason, put your brief reasoning inside <think>...</think> as its own block. Keep it concise.\n"
            "Then, on a new final line, output exactly: The answer is N\n\n"
            "Formatting rules (strict):\n"
            "- Output exactly one final line in the format: The answer is N\n"
            "- Do not include any other words or punctuation on the final line\n"
            "- Do not output any additional numbers outside the <think> block except N on the final line\n"
            "- Do not place any content after the final line\n"
            "- Do not ask follow-up questions or start a new conversation\n\n"
            "Examples (follow strictly):\n"
            "Correct:\n"
            "<think>We compare options 2 and 3; 3 frees a column.</think>\nThe answer is 3\n\n"
            "Also correct (no reasoning):\n"
            "The answer is 2\n\n"
            "Incorrect (extra text on final line):\n"
            "The answer is 4 because it frees a column\n\n"
            "Incorrect (two numbers after final line or extra lines after final line):\n"
            "<think>2 vs 3</think>\nThe answer is 3\n2\n"
        )
        content = f"{instruction}\n\nQuestion:\n{question}"
        return [{"role": "user", "content": content}]
    
    @classmethod
    def batch_process(cls, raw_data_path: str, output_path: Optional[str] = None):
        """
        Batch process raw data and save to output file.
        
        Args:
            raw_data_path: Path to raw data file
            output_path: Path to save processed data; if None, returns the processed list
        """
        generator = cls(raw_data_path)
        processed_data = []
        
        for identity in generator.case_generator():
            # Generate messages
            messages = generator.prompt_func(identity)

            # Ground truth for reward calculation
            ground_truth = {"answer": identity["answer"]}

            # Resolve image paths relative to dataset without hard-coding absolutes
            image_paths = resolve_image_paths(raw_data_path, identity.get("images", []))

            # Create evaluation format
            # When 'image' is present, BaseEvaluator will embed them as base64 automatically
            eval_item = {
                "messages": messages,
                "image": image_paths if image_paths else None,
                "reward_model": {
                    "ground_truth": ground_truth
                },
                "extra_info": {
                    "id": identity.get("data_id"),
                    "question_id": identity.get("question_id"),
                    "images": image_paths if image_paths else None,
                    # Useful for reporting
                    "generator_name": cls.__name__,
                    # Add interaction_kwargs for interaction instance
                    "interaction_kwargs": {
                        "identity": ground_truth
                    }
                },
                # Optional: tag this dataset source for registry-based flows
                "data_source": "freecell"
            }
            processed_data.append(eval_item)
        
        # Save or return
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                if output_path.endswith('.jsonl'):
                    for item in processed_data:
                        f.write(json.dumps(item, ensure_ascii=False) + '\n')
                else:
                    json.dump(processed_data, f, ensure_ascii=False, indent=2)
            print(f"✅ Processed {len(processed_data)} items from {raw_data_path}")
            print(f"✅ Saved to {output_path}")
            return len(processed_data)
        else:
            print(f"✅ Processed {len(processed_data)} items from {raw_data_path}")
            print(f"ℹ️ output_path is None; returning processed data list instead of writing to file")
            return processed_data
