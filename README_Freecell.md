# Freecell RLVR Task

This directory contains the implementation of the Freecell task for the RLVR framework.

## Structure

- `internbootcamp/bootcamps/freecell/`: Contains the core logic.
  - `freecell_reward_manager.py`: Handles answer extraction and scoring.
  - `freecell_interaction.py`: Handles the interaction loop (single-turn QA).
  - `freecell_evaluator.py`: Configures the evaluator.
  - `config/freecell_interaction_config.yaml`: Configuration for the interaction class.
- `scripts/run_freecell_eval.py`: Script to run the evaluation.

> [!NOTE]
> The evaluation script automatically handles both data formats:
> - Original format: `question` and `answer` fields
> - GameQA-5K format: `query` and `solution` fields

## Usage

To run the evaluation, use the following command:

```bash
python3 scripts/run_freecell_eval.py \
    --api_key YOUR_API_KEY \
    --api_url YOUR_API_URL \
    --model YOUR_MODEL_NAME \
    --data_path Game-RL/src/freecell/freecell_dataset_example/data.json \
    --output_dir outputs/freecell
```

## Using Local Models

If you are using a locally deployed model (e.g., via vLLM or LMDeploy) that provides an OpenAI-compatible API, you can run the evaluation as follows:

```bash
python3 scripts/run_freecell_eval.py \
    --api_key "EMPTY" \
    --api_url "http://localhost:8000/v1" \
    --model "your-local-model-name" \
    --data_path Game-RL/src/freecell/freecell_dataset_example/data.json \
    --output_dir outputs/freecell
```

Note:
- Set `--api_key` to "EMPTY" or any string if your local server doesn't require authentication.
- Set `--api_url` to your local server's endpoint (usually ending in `/v1`).
- Set `--model` to the model name served by your local server.

## Scoring Logic

The reward is calculated as follows:
- **Format Score (0.1)**: Awarded if the model output is valid (non-empty, or follows format if strict mode is on).
- **Answer Score (0.9)**: Awarded if the extracted answer matches the ground truth.
- **Total Score**: Sum of Format Score and Answer Score (max 1.0).

## Implementation Details

The implementation follows the `internbootcamp` framework patterns.
- **Reward Manager**: Uses regex to extract the answer index from the model's response. It supports patterns like "The answer is X" or simply finding the last number.
- **Interaction**: Simulates a single-turn interaction where the user (environment) provides the question and the assistant (model) provides the answer.
