# Quick View

**Title**: AgentIR: Reasoning-Aware Retrieval for Deep Research Agents
**Authors**: Zijian Chen, Xueguang Ma, Shengyao Zhuang, Jimmy Lin, Akari Asai, Victor Zhong
**arXiv**: [2603.04384](https://arxiv.org/abs/2603.04384)
**Year**: 2026

# Question

Deep Research agent 在多轮搜索中产生的推理链（reasoning trace）包含丰富的意图和上下文信息，现有检索器完全忽略了这些信号——如何让检索器利用这些"免费"的推理信号来提升检索质量？

# Task

为 Deep Research agent 构建专用检索器：agent 在每轮搜索前会生成自然语言推理，检索器需要联合编码推理链和查询，在多轮复杂信息检索任务（如 BrowseComp-Plus）中提升端到端准确率。

# Challenge

1. **查询歧义性**：agent 发出的子查询（如 "backroom studio early 2010s euphoric"）本身高度模糊，传统检索器仅基于查询文本无法理解真实意图
2. **多轮上下文缺失**：传统检索将每次查询视为独立的人类搜索，完全丢失了 agent 前几轮积累的搜索上下文
3. **训练数据缺失**：不存在针对 Deep Research agent 子查询的检索训练数据——现有 QA 数据集只有全局问题-答案对，没有多轮子查询级别的相关性标注

# Insight

Deep Research agent 的推理链是一个"免费的"、经过隐式策展的检索信号：它不仅包含任务意图、先前结果的反思和假设推测，还会自动过滤掉过时的错误假设，比天真地嵌入完整历史更干净。

![Overview Figure](figures/fig-000.png)
*Figure 1: Reasoning-Aware Retrieval（AgentIR）vs 传统检索的对比。左侧传统检索器仅基于模糊查询返回不相关结果；右侧 AgentIR 联合编码推理链，利用其中的意图澄清、先前结果反思和假设推测，成功检索到相关文档。*

# Contribution

1. **Reasoning-Aware Retrieval（推理感知检索范式）**
   - **方法**：将 agent 当前轮的推理链 τ_t 与查询 q_t 拼接后联合编码为检索输入（o_t ← R(τ_t, q_t)），使用模板 "Reasoning: {reasoning} Query: {query}" 嵌入
   - **技术优势**：推理链提供三重信号增益——(1) 任务意图澄清（类似 task-aware retrieval 中的人工指令，但无需人工）；(2) 先前结果反思（纳入多轮搜索历史的关键发现）；(3) 假设搜索目标（类似 HyDE 但基于完整交互历史，更加 grounded）。最关键的是，这些信号完全"免费"——agent 本身就会生成推理链，无需额外 LLM 调用

2. **DR-Synth（Deep Research 检索训练数据合成流水线）**
   - **方法**：从标准 QA 数据集的 (Q, A, P) 三元组出发，(1) 使用 agent + 传统检索器在 Q 上进行 rollout 生成多轮子查询 (τ_t, q_t)；(2) 对每轮检索结果进行 oracle reranking——将 ground truth 正例文档 P 注入候选池，使用 LLM 进行 listwise reranking（同时考虑子查询相关性和全局问题对齐）；(3) 取 top-1 为正例、bottom-7 为硬负例；(4) 仅保留成功回答 Q 的 trajectory（rejection sampling）
   - **技术优势**：解决了 Deep Research 场景下缺乏子查询级训练数据的核心瓶颈；oracle reranking 机制确保标注同时满足局部相关性和全局一致性；从 500 个 WebShaper 问题生成 5,238 条训练数据即可获得显著提升

![DR-Synth Pipeline](figures/fig-001.png)
*Figure 2: DR-Synth 的 oracle reranking 流程。对每轮子查询检索 top-50 文档，注入全局正例文档，使用 LLM（结合全局问题 Q 和答案 A）进行 listwise reranking，top-1 标为正例，bottom-7 标为硬负例。*

# Experiments

## 主实验结果

在 BrowseComp-Plus 上的端到端评估（Table 1）：

| Agent | 检索器 | Accuracy | Recall | Search Calls |
|-------|--------|----------|--------|-------------|
| Tongyi-DR | BM25 | 33.98 | 46.83 | 32.92 |
| Tongyi-DR | Qwen3-Embed-4B | 48.67 | 59.90 | 31.02 |
| Tongyi-DR | Qwen3-Embed-8B | 50.72 | 61.78 | 30.43 |
| Tongyi-DR | ReasonIR-8B | 51.03 | 63.62 | 31.15 |
| Tongyi-DR | LLM Rerank | 55.66 | 68.35 | 28.85 |
| Tongyi-DR | **AgentIR-4B** | **66.27** | **78.86** | **25.91** |
| oss-120b-high | **AgentIR-4B** | **66.99** | **78.13** | **24.08** |
| GLM-4.7 | **AgentIR-4B** | **64.66** | **79.21** | **29.85** |

关键发现：
- AgentIR-4B 比同 backbone（Qwen3-Embed-4B）提升 **+17.6%** 绝对准确率
- 比两倍大小的 Qwen3-Embed-8B 高 **~15%**
- 比计算昂贵的 LLM Rerank 高 **~10%**，且无需额外重排推理开销
- 搜索次数从 32.92（BM25）降至 25.91，效率显著提升

## Core Contribution Impact (Ablation Studies)

**组件消融（Table 2）**：

| 方法 | Tongyi-DR Acc | oss-120b Acc | GLM-4.7 Acc |
|------|--------------|-------------|-------------|
| Qwen3-Embed-4B (baseline) | 48.67 | 47.59 | 50.48 |
| + Reasoning（无训练） | 55.54 | 51.33 | 50.90 |
| + DR-Synth 训练（无 Reasoning） | 59.40 | 59.16 | 57.47 |
| + 两者结合（AgentIR-4B） | **66.27** | **66.99** | **64.66** |

两个组件独立有效，组合效果最佳。

**替代信号消融（Table 3）**：仅用当前轮推理链（AgentIR-4B）始终优于使用全局问题、历史查询、历史查询+推理、完整 trajectory 等所有替代方案。

**历史轮数分析**：

![History Turns Analysis](figures/fig-002.png)
*Figure 3: (a) 嵌入不同数量历史轮数 k 的准确率——仅用当前轮（k=1）即达到最佳；(b) 最近 k 轮推理的线索覆盖率——仅当前轮已覆盖 >40% 的所有历史线索，说明当前推理会自动总结先前发现。*

## Limitation

**"遗忘即特性"分析**：

![Noise Analysis](figures/fig-003.png)
*Figure 4(b): 最近 k 轮推理中正确 vs 错误声明的平均数量。错误声明（红线）随轮数线性增长，而正确声明（绿线）基本保持平稳。这解释了为什么加入更多历史反而有害——噪声增长远快于有效信号。*

当前推理链的优势在于它隐式地"策展"了历史：确认的发现被总结保留，错误的假设（如 "Jesper Kyd"、"Finland"）被自然遗忘。天真地嵌入完整历史会引入大量过时噪声，在极端情况下（Prior Queries & Reasonings & Docs）导致 11.45% 的 run 零召回。

此外，论文未探讨的局限包括：
- 仅在 BrowseComp-Plus 单一基准上评估
- 训练依赖特定 agent（Tongyi-DR）的 rollout，尽管泛化性良好
- 推理链质量高度依赖 agent 本身的推理能力
