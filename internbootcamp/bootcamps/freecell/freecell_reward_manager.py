from internbootcamp.src.base_reward_calculator import BaseRewardCalculator
import re

class FreecellRewardManager(BaseRewardCalculator):

    @staticmethod
    def extract_output(output_str: str):
        """
        Extract the selected option index from the model output.
        Prefers parsing the segment after the last </think> (answer section),
        then falls back to the whole output. Assumes the answer is an integer index.
        """
        if not output_str:
            return None
        text = output_str
        # 1) Prefer only the segment after the last </think>
        if "</think>" in output_str:
            try:
                text = output_str.rsplit("</think>", 1)[1]
            except Exception:
                text = output_str
        
        # Look for patterns like "The answer is X", "Option X", or just the last number
        # We prioritize explicit statements
        explicit_patterns = [
            r"answer is (\d+)",
            r"option (\d+)",
            r"choose (\d+)",
            r"select (\d+)"
        ]
        # 2) Try explicit patterns in answer segment first
        for pattern in explicit_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return int(matches[-1])
        # 3) Fallback: explicit patterns anywhere
        for pattern in explicit_patterns:
            matches = re.findall(pattern, output_str, re.IGNORECASE)
            if matches:
                return int(matches[-1])
        # 4) If no explicit pattern, find the last integer in answer segment
        matches = re.findall(r"\d+", text)
        if matches:
            return int(matches[-1])
        # 5) Final fallback: last integer anywhere
        matches = re.findall(r"\d+", output_str)
        if matches:
            return int(matches[-1])
            
        return None

    @classmethod
    def _verify_correction(cls, extract_solution, identity: dict, **kwargs) -> float:
        """
        Verify if the extracted solution matches the ground truth.
        identity: {"answer": 1}
        """
        if extract_solution is None:
            return 0.0
            
        try:
            # Ground truth answer is an integer index
            gold = int(identity.get("answer"))
            pred = int(extract_solution)
            return 1.0 if pred == gold else 0.0
        except (ValueError, TypeError):
            return 0.0

    @classmethod
    def verify_score(cls, model_output, identity: dict, format_score=0.1, **kwargs) -> float:
        """
        Calculate the total score: format_score (0.1) + answer_score (0.9).
        """
        # Base verification for format (checks <think> tags if format_penalty is True)
        # We assume format_score is passed as 0.1 by default or from config
        
        # We can reuse the base class logic but we need to customize the scoring weights
        # The base class returns `format_score` if extraction succeeds but answer is wrong.
        # If answer is correct, it returns 1.0 (or whatever _verify_correction returns if not bool).
        
        # Let's manually implement the logic to ensure the 0.1 + 0.9 split
        
        score = 0.0
        
        # Check format (simple check for now, or rely on base class if we call super)
        # The requirement says "format score 取 0, 0.1". 
        # Let's assume presence of <think> tags is the format requirement if we want to be strict,
        # or just "valid output" (not empty).
        # Given the base class logic:
        # if format_penalty is True, it checks <think> tags.
        # Let's assume we want to give 0.1 if we can at least extract an answer, or just for non-empty?
        # The prompt says "format score 取 0, 0.1".
        
        # Let's use the base class verify_score but tweak the parameters?
        # Base class:
        # if extracted: score = format_score
        # if correct: score = 1.0 (if _verify_correction returns True)
        
        # If we want 0.1 + 0.9:
        # If correct: 0.1 + 0.9 = 1.0
        # If incorrect but formatted: 0.1
        
        # So if we pass format_score=0.1 to base verify_score,
        # and _verify_correction returns 0.9 (float) instead of True?
        # Base class line 94: if isinstance(judge, (bool, int, float)): score = float(judge)
        # But wait, base class line 88: score = format_score.
        # Then line 89: judge = _verify_correction(...)
        # If judge is True -> score = 1.0.
        # If judge is float -> score = float(judge).
        # So if _verify_correction returns 1.0, score becomes 1.0.
        # If _verify_correction returns 0.0, score becomes 0.0 (overwriting format_score!).
        
        # Ah, looking at base_reward_calculator.py:
        # line 88: score = format_score
        # line 89: judge = _verify_correction(...)
        # line 90: if type(judge) == bool and judge: score = 1.
        # line 94: elif isinstance(judge, ...): score = float(judge)
        
        # So if _verify_correction returns 0.0 (float), score becomes 0.0.
        # This means we lose the format_score!
        
        # To preserve format_score + answer_score logic, we should probably override verify_score completely
        # or make _verify_correction return the *total* score?
        # If _verify_correction returns 0.1 (format only) or 1.0 (format + answer)?
        # But _verify_correction is supposed to verify *correction*.
        
        # Let's override verify_score to be safe and explicit.
        
        format_penalty = kwargs.get("format_penalty", False)
        
        # 1. Format Check
        has_valid_format = True
        if format_penalty:
            if "<think>" not in model_output or "</think>" not in model_output:
                has_valid_format = False
            if model_output.count("<think>") > 1 or model_output.count("</think>") > 1:
                has_valid_format = False
        
        if not has_valid_format:
            return 0.0
            
        current_score = format_score # 0.1
        
        # 2. Extraction
        extracted = cls.extract_output(model_output)
        if extracted is None:
            return 0.0 # Or should it be 0? If we can't extract, maybe format is bad too?
                       # Requirement: "format score 取 0, 0.1". 
                       # If we can't extract, let's say 0.
        
        # 3. Verification
        is_correct = cls._verify_correction(extracted, identity)
        
        if is_correct:
            current_score += 0.9
            
        return min(current_score, 1.0)

