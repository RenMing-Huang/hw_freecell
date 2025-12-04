#!/bin/bash

# Freecell evaluation with gpt-oss served by vLLM
# Prerequisite: start vLLM server, e.g.
#   VLLM_ATTENTION_BACKEND=TRITON_ATTN_VLLM_V1 \
#   vllm serve /inspire/hdd/project/robot-decision/public/models/openai/gpt-oss-20b \
#     --served-model-name gpt-oss-20b \
#     --trust_remote_code \
#     --port 8801

set -euo pipefail

# Dataset path (text-only or multimodal). The generator will resolve images relatively.
DATASET_PATH="${DATASET_PATH:-Game-RL/src/freecell/freecell_dataset_example/data.json}"
OUTPUT_DIR="${OUTPUT_DIR:-outputs/freecell_gpt_oss}"

# vLLM OpenAI-compatible endpoint
API_KEY="${API_KEY:-EMPTY}"           # vLLM typically doesn't require a real key
API_URL="${API_URL:-http://localhost:8801/v1}"
API_MODEL="${API_MODEL:-gpt-oss-20b}" # must match --served-model-name

# Optional: model params (JSON string or @file), e.g. enable higher max tokens
API_EXTRA_PARAMS="${API_EXTRA_PARAMS:-}" 
# Example:
# API_EXTRA_PARAMS='{"temperature":0.2,"max_tokens":1024}'

# Evaluator and reward
EVALUATOR_CLASS="internbootcamp.bootcamps.freecell.freecell_evaluator.FreecellEvaluator"
REWARD_CALCULATOR_CLASS="internbootcamp.bootcamps.freecell.freecell_reward_manager.FreecellRewardManager"
INTERACTION_CONFIG="internbootcamp/bootcamps/freecell/config/freecell_interaction_config.yaml"

MAX_ASSISTANT_TURNS=${MAX_ASSISTANT_TURNS:-1}
MAX_USER_TURNS=${MAX_USER_TURNS:-1}
MAX_CONCURRENT=${MAX_CONCURRENT:-5}

# Preprocess the dataset into framework-ready format
PROCESSED_DATA="/tmp/freecell_gpt_oss_$(date +%s).jsonl"

echo "📊 Preprocessing dataset for gpt-oss..."
python3 - <<'PY'
import os, json
from internbootcamp.bootcamps.freecell.freecell_instruction_generator import FreecellInstructionGenerator

raw = os.environ.get('DATASET_PATH')
out = os.environ.get('PROCESSED_DATA')
FreecellInstructionGenerator.batch_process(raw, out)
PY

if [ ! -s "$PROCESSED_DATA" ]; then
  echo "❌ Data preprocessing failed or produced empty file: $PROCESSED_DATA"
  exit 1
fi

echo "🚀 Running evaluation on gpt-oss (${API_URL}, model=${API_MODEL})..."
python -m internbootcamp.utils.run_evaluation \
  --dataset-path "$PROCESSED_DATA" \
  --output-dir "$OUTPUT_DIR" \
  --api-key "$API_KEY" \
  --api-url "$API_URL" \
  --api-model "$API_MODEL" \
  --evaluator-class "$EVALUATOR_CLASS" \
  --reward-calculator-class "$REWARD_CALCULATOR_CLASS" \
  --interaction-config "$INTERACTION_CONFIG" \
  --max-assistant-turns $MAX_ASSISTANT_TURNS \
  --max-user-turns $MAX_USER_TURNS \
  --max-concurrent $MAX_CONCURRENT \
  ${API_EXTRA_PARAMS:+--api-extra-params "$API_EXTRA_PARAMS"} \
  --verbose

# Cleanup
rm -f "$PROCESSED_DATA"
echo "✅ Evaluation complete. Results in $OUTPUT_DIR"
