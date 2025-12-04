# RLVR 作业详解 (Assignment Explanation)

## 1. 作业背景与目标 (Background & Objective)

这份作业的核心目标是让你熟悉 **RLVR (Reinforcement Learning with Verifiable Rewards)** 的工作流程。在训练或评估大语言模型（LLM）解决复杂问题（如数学、代码、游戏逻辑）时，我们需要一个自动化的方式来判断模型的回答是否正确，并给出相应的奖励（Reward）。

**简单来说，你需要搭建一套流水线：**
1.  **出题**：把数据（如 Freecell 游戏的局面）变成模型能看懂的 Prompt。
2.  **做题**：让模型回答问题。
3.  **判卷**：自动判断模型答对没，并打分（0~1分）。

## 2. 核心组件 (Key Components)

为了实现这个目标，我们需要实现以下几个模块（对应代码中的类）：

### A. 数据 (Data)
- **来源**：`Game-RL` 目录下的各种游戏数据。
- **我们选的任务**：**Freecell (空当接龙)**。
- **形式**：给出一个牌局状态，问你“第X列第Y张牌是什么？”或者“这一步移动合不合法？”。

### B. 交互 (Interaction) - `FreecellInteraction`
- **作用**：管理“出题”和“做题”的流程。
- **逻辑**：
    - 读取题目（Prompt）。
    - 发送给模型。
    - 接收模型的回复。
    - 调用“判卷”模块打分。

### C. 奖励计算 (Reward Calculator) - `FreecellRewardManager`
- **作用**：负责“判卷”。
- **逻辑**：
    - **提取 (Extract)**：从模型的一大段回复中，提取出核心答案（比如选项 "2"）。
    - **验证 (Verify)**：把提取的答案和标准答案（Ground Truth）对比。
    - **打分 (Score)**：
        - **格式分 (Format Score)**：只要模型回复了且能提取出答案，给 0.1 分（鼓励模型开口说话且格式正确）。
        - **答案分 (Answer Score)**：如果答对了，再加 0.9 分。
        - **总分**：满分 1.0 分。

### D. 评测器 (Evaluator) - `FreecellEvaluator`
- **作用**：把上面所有东西串起来，批量跑测试数据，最后算出一个平均准确率。

## 3. 我们做了什么？ (What We Implemented)

针对 Freecell 任务，我们完成了以下工作：

1.  **创建了 `internbootcamp/bootcamps/freecell/` 目录**：
    - `freecell_reward_manager.py`: 实现了如何从回复中找数字，以及如何打分。
    - `freecell_interaction.py`: 实现了简单的一问一答流程。
    - `freecell_evaluator.py`: 配置了评测器。

2.  **编写了运行脚本 `scripts/run_freecell_eval.py`**：
    - 这个脚本会自动读取 `Game-RL` 里的 Freecell 数据。
    - 把它转换成评测器需要的格式。
    - 调用模型（可以是 API 也可以是本地模型）进行测试。
    - 输出结果到 `outputs/freecell`。

## 4. 如何理解“验证”？ (Verification)

作业要求“代码形式需要能够提交到 bootcamp 代码中并进行验证”。这意味着：
- 你的代码结构必须符合 `internbootcamp` 的框架规范（我们已经做到了，放在了 `bootcamps` 目录下）。
- 你的评分逻辑必须是客观的、可执行的（我们用了正则提取+数值比对，非常客观）。
- 你需要能跑通一个评测流程，证明你的代码是工作的（我们提供了 `run_freecell_eval.py` 和 `test_freecell_task.py`）。

## 5. 总结

这个作业本质上就是让你**写一个自动判题机**。
- **输入**：题目 + 标准答案。
- **黑盒**：大模型。
- **输出**：模型得分。

你现在可以直接运行 `scripts/run_freecell_eval.py` 来体验这个“自动判题”的过程。
