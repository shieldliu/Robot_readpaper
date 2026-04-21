# Quick View

**Title**: Qwen3 Technical Report
**Authors**: Qwen Team (An Yang, Anfeng Li, Baosong Yang 等 61 位作者)
**arXiv**: [2505.09388](https://arxiv.org/abs/2505.09388)
**Year**: 2025

# Question

如何构建一个既能进行快速响应又能进行深度推理的统一大语言模型，同时实现从旗舰模型到轻量级模型的高效知识迁移？

# Task

本文的任务是开发新一代 Qwen3 系列大语言模型，包括：
1. 支持 0.6B 到 235B 参数规模的 Dense 和 MoE 架构模型
2. 在单一模型中统一"思考模式"（复杂推理）和"非思考模式"（快速响应）
3. 支持 119 种语言和方言的多语言能力
4. 通过知识蒸馏高效构建轻量级模型

# Challenge

1. **模式切换困境**：现有方案需要在聊天模型（如 GPT-4o）和专用推理模型（如 QwQ-32B）之间切换，增加了部署复杂度
2. **推理资源分配**：难以根据任务复杂度动态分配推理计算资源，简单任务浪费算力，复杂任务资源不足
3. **小模型训练成本**：从头训练小规模模型需要大量计算资源，而直接蒸馏往往性能损失严重
4. **多语言扩展**：在保持主要语言性能的同时扩展到更多语言具有挑战性

# Insight

通过四阶段后训练流程将推理能力和快速响应能力融合到单一模型中，并利用旗舰模型的知识通过 Strong-to-Weak 蒸馏高效训练轻量级模型。

![Post-training Pipeline](figures/figure-1-pipeline.png)
*Figure 1: Qwen3 后训练流程。旗舰模型经过 4 阶段训练，轻量级模型通过 Strong-to-Weak 蒸馏获得*

# Contribution

## 1. **Thinking Mode Fusion（思考模式融合）**

- **方法**: 在 Reasoning RL 模型上进行持续 SFT，使用包含"思考"和"非思考"数据的混合数据集。通过 chat template 中的 `/think` 和 `/no_think` 标志控制模式切换
- **技术优势**:
  - 消除了部署多个模型的需求
  - 支持基于用户查询或 chat template 的动态模式切换
  - 模型自然学会处理中间状态（thinking budget 机制的基础）

## 2. **Thinking Budget 机制**

- **方法**: 当模型思考长度达到用户定义的阈值时，手动插入停止思考指令，模型基于已积累的推理生成最终响应
- **技术优势**:
  - 允许用户根据任务复杂度自适应分配计算资源
  - 在延迟和性能之间实现平衡
  - 无需显式训练，自然从 Thinking Mode Fusion 中涌现

![Thinking Budget Effect](figures/figure-2-thinking-budget.png)
*Figure 2: Qwen3-235B-A22B 在不同 thinking budget 下的性能。随着 budget 增加，性能持续提升*

## 3. **Strong-to-Weak Distillation（强到弱蒸馏）**

- **方法**: 分两阶段进行：(1) Off-policy 蒸馏 - 使用旗舰模型输出作为训练数据；(2) On-policy 蒸馏 - 学生模型采样，教师模型在线打分
- **技术优势**:
  - 显著减少训练小模型所需的计算资源（仅需 RL 的 1/10 GPU 小时）
  - 蒸馏使学生模型能够扩展探索空间并增强推理潜力
  - 轻量级模型能够达到甚至超越更大参数量的前代模型

## 4. **四阶段后训练流程**

- **Stage 1 (Long-CoT Cold Start)**: 使用多样化长 CoT 数据进行 SFT，建立推理基础
- **Stage 2 (Reasoning RL)**: 在数学、代码和通用推理任务上进行强化学习
- **Stage 3 (Thinking Mode Fusion)**: 融合思考和非思考能力
- **Stage 4 (General RL)**: 进一步增强通用能力和 agent 能力

## 5. **大规模多语言预训练**

- **方法**: 在 36 万亿 tokens 上预训练，覆盖 119 种语言和方言（相比 Qwen2.5 的 29 种语言扩展 4 倍）
- **技术优势**: 通过 GQA、QK-Norm、RMSNorm 等架构改进确保稳定训练，支持 128K 上下文长度

# Experiments

## Core Contribution Impact (Ablation Studies)

### Thinking vs Non-Thinking 模式对比

| 任务类别 | Qwen3-235B-A22B (Thinking) | Qwen3-235B-A22B (Non-thinking) |
|---------|---------------------------|-------------------------------|
| AIME'24 | 85.7 | 81.4 |
| AIME'25 | 81.5 | 72.9 |
| LiveCodeBench v5 | 70.7 | 65.7 |
| CodeForces | 2056 / 98.2% | 1977 / 97.7% |

Thinking 模式在数学和编程等复杂推理任务上显著优于 Non-thinking 模式。

### 蒸馏 vs 强化学习效率对比

| 方法 | AIME'24 | AIME'25 | MATH500 | GPU Hours |
|-----|---------|---------|---------|-----------|
| Off-policy Distillation | 74.4 (93.3) | 65.5 (86.7) | 97.0 | 1,800 |
| + Reinforcement Learning | 67.6 (90.0) | 55.5 (83.3) | 94.8 | 17,920 |
| + On-policy Distillation | **74.4 (93.3)** | **65.5 (86.7)** | **97.0** | **1,800** |

On-policy 蒸馏在仅需约 1/10 计算资源的情况下达到与 RL 相当甚至更好的性能。

### 模型规模对比

- **Qwen3-235B-A22B** (MoE, 22B 激活参数): 在大多数基准测试中达到 SOTA，与 GPT-4o、DeepSeek-V3 等竞争
- **Qwen3-32B** (Dense): 使用 32B 参数超越 Qwen2.5-72B 和 Llama-4-Scout (109B 参数)
- **Qwen3-30B-A3B** (MoE): 仅 3B 激活参数，性能媲美 Qwen3-14B

## Limitation

1. **Thinking 模式长上下文性能下降**: 在 RULER 等长上下文检索任务上，Thinking 模式性能略有下降。推测 thinking 过程可能干扰检索过程
2. **复杂任务上的 Thinking Mode Fusion 权衡**: 对于 AIME'24 和 LiveCodeBench 等挑战性任务，Thinking Mode Fusion 和 General RL 训练后，thinking 模式性能实际有所下降
3. **多语言覆盖度**: 尽管支持 119 种语言，但在低资源语言上的性能仍有提升空间
