import argparse
import os
import asyncio
from internbootcamp.bootcamps.freecell.freecell_evaluator import FreecellEvaluator
from internbootcamp.src.base_evaluator import load_dataset

def main():
    parser = argparse.ArgumentParser(description="Run Freecell Evaluation")
    parser.add_argument("--api_key", type=str, required=True, help="API Key for the model")
    parser.add_argument("--api_url", type=str, required=True, help="API URL for the model")
    parser.add_argument("--model", type=str, required=True, help="Model name")
    parser.add_argument("--data_path", type=str, default="Game-RL/src/freecell/freecell_dataset_example/data.json", help="Path to data.json")
    parser.add_argument("--output_dir", type=str, default="outputs/freecell", help="Output directory")
    parser.add_argument("--max_concurrent", type=int, default=5, help="Max concurrent requests")
    
    args = parser.parse_args()

    # Load dataset
    if not os.path.exists(args.data_path):
        print(f"Error: Data path {args.data_path} does not exist.")
        return

    raw_dataset = load_dataset(args.data_path)
    
    # Transform dataset to the format expected by BaseEvaluator
    # BaseEvaluator expects "messages" or "prompt" and "reward_model" -> "ground_truth"
    
    eval_dataset = []
    for item in raw_dataset:
        # Filter for free_cell tasks
        if "free_cell" not in item.get("data_id", ""):
            continue

        # Construct the prompt
        # Support both "question" and "query" fields
        prompt_content = item.get("query") or item.get("question", "")
        
        if not prompt_content:
            print(f"Warning: Skipping item {item.get('data_id')} - no question/query field")
            continue
        
        messages = [
            {"role": "user", "content": prompt_content}
        ]
        
        # Ground truth - support both "answer" and "solution" fields
        answer = item.get("solution") or item.get("answer")
        if answer is None:
            print(f"Warning: Skipping item {item.get('data_id')} - no answer/solution field")
            continue
            
        # Convert to int if it's a string
        try:
            answer = int(answer)
        except (ValueError, TypeError):
            print(f"Warning: Could not convert answer to int for {item.get('data_id')}: {answer}")
            continue
        
        ground_truth = {"answer": answer}
        
        # Handle images if present
        images = item.get("images", [])
        if images:
            # Note: Image handling might need to be added to the evaluator
            # For now, we'll store it in extra_info
            pass
        
        eval_dataset.append({
            "messages": messages,
            "reward_model": {
                "ground_truth": ground_truth
            },
            "extra_info": {
                "id": item.get("data_id"),
                "question_id": item.get("question_id"),
                "images": images if images else None
            }
        })

    evaluator = FreecellEvaluator(
        api_url=args.api_url,
        api_key=args.api_key,
        api_model=args.model,
    )

    asyncio.run(evaluator.run_evaluation(
        dataset=eval_dataset,
        output_dir=args.output_dir,
        max_concurrent=args.max_concurrent
    ))

if __name__ == "__main__":
    main()
