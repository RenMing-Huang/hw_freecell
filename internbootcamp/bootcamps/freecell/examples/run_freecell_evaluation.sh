#!/bin/bash

# Freecell 评测脚本
# 使用框架标准的 run_evaluation 工具

# 评测数据集路径
DATASET_PATH="${DATASET_PATH:-Game-RL/src/freecell/freecell_dataset_example/data.json}"

# 评测输出目录
OUTPUT_DIR="${OUTPUT_DIR:-outputs/freecell}"

# API 配置 (可通过环境变量覆盖)
API_KEY="${API_KEY:-EMPTY}"
API_URL="${API_URL:-http://localhost:8000/v1}"
API_MODEL="${API_MODEL:-Qwen/Qwen3-VL-2B-Instruct}"
# 设置 API 超时时间 (秒)
export API_TIMEOUT="${API_TIMEOUT:-30}"

# 评测器类 (使用框架的 BaseEvaluator)
# 评测器类 (使用自定义的 FreecellEvaluator 以支持超时配置)
EVALUATOR_CLASS="internbootcamp.bootcamps.freecell.freecell_evaluator.FreecellEvaluator"

# 奖励计算器类
REWARD_CALCULATOR_CLASS="internbootcamp.bootcamps.freecell.freecell_reward_manager.FreecellRewardManager"

# 交互配置文件路径
INTERACTION_CONFIG="internbootcamp/bootcamps/freecell/config/freecell_interaction_config.yaml"

# 最大轮数
MAX_ASSISTANT_TURNS=${MAX_ASSISTANT_TURNS:-1}
MAX_USER_TURNS=${MAX_USER_TURNS:-1}

# 最大并发数
MAX_CONCURRENT=${MAX_CONCURRENT:-5}

# Preprocess data if needed
PROCESSED_DATA="/tmp/freecell_processed_$(date +%s).jsonl"

echo "📊 Preprocessing dataset..."
python3 -c "
from internbootcamp.bootcamps.freecell.freecell_instruction_generator import FreecellInstructionGenerator
FreecellInstructionGenerator.batch_process('$DATASET_PATH', '$PROCESSED_DATA')
"

if [ $? -ne 0 ]; then
    echo "❌ Data preprocessing failed!"
    exit 1
fi

echo "🚀 Starting evaluation..."

# 执行评测命令
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
    --verbose

# Clean up temporary file
rm -f "$PROCESSED_DATA"
echo "✅ Evaluation complete!"
