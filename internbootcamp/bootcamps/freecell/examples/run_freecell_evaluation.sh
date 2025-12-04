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
# 设置 API 超时时间 (秒) - 增加到 120s 以支持多模态处理
export API_TIMEOUT="${API_TIMEOUT:-120}"
# 限制图片大小 (bytes) - 5MB
export MAX_IMAGE_SIZE="${MAX_IMAGE_SIZE:-5000000}"

# 图片目录
IMAGE_DIR="/inspire/hdd/project/robot-decision/huangrenming-253108120148/project/hw_freecell/GameQA-5K/"
IMAGE_PORT=8082
export IMAGE_SERVER_URL="http://localhost:${IMAGE_PORT}"

# 检查图片目录是否存在
if [ ! -d "$IMAGE_DIR" ]; then
    echo "Error: Image directory not found: $IMAGE_DIR"
    exit 1
fi

# 启动 HTTP 服务器提供图片访问
echo "Starting image server on port ${IMAGE_PORT}..."
python3 -m http.server ${IMAGE_PORT} --directory "${IMAGE_DIR}" > /tmp/img_server.log 2>&1 &
IMAGE_SERVER_PID=$!

# 确保脚本退出时关闭服务器
cleanup() {
    if ps -p ${IMAGE_SERVER_PID} > /dev/null; then
        echo "Stopping image server (PID: ${IMAGE_SERVER_PID})..."
        kill ${IMAGE_SERVER_PID}
    fi
}
trap cleanup EXIT

# 检查服务器是否启动
sleep 2
if ! ps -p ${IMAGE_SERVER_PID} > /dev/null; then
    echo "Failed to start image server!"
    echo "Server log:"
    cat /tmp/img_server.log
    exit 1
fi
echo "Image server running at ${IMAGE_SERVER_URL}"

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
