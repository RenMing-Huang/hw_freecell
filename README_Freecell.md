# Freecell RLVR Task

This directory contains the Freecell task implementation for the RLVR framework.

## Structure

- `internbootcamp/bootcamps/freecell/`: Contains the core logic.
  - `freecell_reward_manager.py`: Handles answer extraction and scoring.
  - `freecell_interaction.py`: Handles the interaction loop (single-turn QA).
  - `config/freecell_interaction_config.yaml`: Configuration for the interaction class.
  - `examples/run_freecell_evaluation.sh`: Standard evaluation script.

> [!NOTE]
> The evaluation script automatically handles both data formats:
> - Original format: `question` and `answer` fields
> - GameQA-5K format: `query` and `solution` fields

## Usage

### Quick Start

Run the evaluation using the provided shell script:

```bash
# Set environment variables (optional)
export DATASET_PATH="path/to/your/data.json"
export API_KEY="your-api-key"
export API_URL="https://api.openai.com/v1"
export API_MODEL="gpt-4"

# Run evaluation
bash internbootcamp/bootcamps/freecell/examples/run_freecell_evaluation.sh
```

### Using Local Models

For locally deployed models:

```bash
export API_KEY="EMPTY"
export API_URL="http://localhost:8000/v1"
export API_MODEL="Qwen/Qwen3-VL-2B-Instruct"
export DATASET_PATH="/path/to/GameQA_RL_5k.json"

bash internbootcamp/bootcamps/freecell/examples/run_freecell_evaluation.sh
```

### Advanced Usage

You can also call the evaluation utility directly:

```bash
python -m internbootcamp.utils.run_evaluation \
    --dataset-path "Game-RL/src/freecell/freecell_dataset_example/data.json" \
    --output-dir "outputs/freecell" \
    --api-key "your-api-key" \
    --api-url "https://api.openai.com/v1" \
    --api-model "gpt-4" \
    --evaluator-class "internbootcamp.src.base_evaluator.BaseEvaluator" \
    --reward-calculator-class "internbootcamp.bootcamps.freecell.freecell_reward_manager.FreecellRewardManager" \
    --interaction-config "internbootcamp/bootcamps/freecell/config/freecell_interaction_config.yaml" \
    --max-concurrent 5
```

## Scoring Logic

The reward is calculated as follows:
- **Format Score (0.1)**: Awarded if the model output is valid and an answer can be extracted.
- **Answer Score (0.9)**: Awarded if the extracted answer matches the ground truth.
- **Total Score**: Sum of Format Score and Answer Score (max 1.0).

## Implementation Details

The implementation follows the `internbootcamp` framework patterns:
- **Reward Manager**: Uses regex to extract the answer index from the model's response.
- **Interaction**: Simulates a single-turn interaction where the environment provides the question and the model provides the answer.
- **Evaluation**: Uses the framework's standard `BaseEvaluator` with configuration files.

