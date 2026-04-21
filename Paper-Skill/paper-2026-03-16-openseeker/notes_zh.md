# Quick View

**Title**: OpenSeeker: Democratizing Frontier Search Agents by Fully Open-Sourcing Training Data
**Authors**: Yuwen Du, Rui Ye, Shuo Tang, Xinyu Zhu, Yijun Lu, Yuzhu Cai, Siheng Chen
**arXiv**: [2603.15594](https://arxiv.org/abs/2603.15594)
**Year**: 2026
**机构**: 上海交通大学

# Question

如何让学术界也能训练出与工业界媲美的高性能搜索智能体（Search Agent），打破大公司对高质量训练数据的垄断？

# Task

构建一个完全开源的搜索智能体训练方案，包括：
1. 高难度的问答对（QA pairs）合成方法
2. 高质量的搜索轨迹（trajectory）生成方法
3. 完整开源训练数据、模型权重和合成流程

# Challenge

1. **数据垄断**：高性能搜索智能体的训练一直是大公司的"闭门游戏"，高质量训练数据是他们的核心护城河。OpenAI、Google、阿里等公司虽然开源了部分模型权重，但都没有公开训练数据。

2. **现有开源数据质量低**：学术界现有的开源数据集往往质量差、推理复杂度不足。例如 MiroThinker 使用 147k 样本训练，效果仍远不如商业模型。

3. **QA 难度不足**：简单的 QA 对无法迫使模型进行多轮工具调用和深度推理，容易被模型通过参数记忆直接回答。

4. **轨迹噪声问题**：原始网页内容包含大量无关噪声，干扰教师模型生成高质量的推理和动作。

# Insight

通过"逆向工程"网页图谱来构建问题（先找到推理路径，再构造必须遍历该路径的问题），并通过"生成时去噪、训练时保留噪声"的不对称策略来合成高质量轨迹，可以用极少的高保真数据（11.7k 样本）超越使用复杂训练流程的工业级模型。

# Contribution

1. **基于事实的可扩展可控 QA 合成（Fact-grounded Scalable Controllable QA Synthesis）**
   - **方法**: 从网页语料库随机采样种子节点，通过拓扑图扩展收集相连网页形成子图；提取实体构建实体子图；基于实体子图结构生成初始问题；对实体进行模糊化处理（entity obfuscation）使问题更难；最后通过双重验证（难度检验 + 可解性检验）过滤样本
   - **技术优势**:
     - 事实锚定：基于真实网页拓扑而非 LLM 生成，消除幻觉
     - 可扩展：TB 级网页存档可作为无限数据源
     - 可控：通过子图大小调节推理复杂度

2. **去噪轨迹合成（Denoised Trajectory Synthesis）**
   - **方法**: 采用回顾式摘要机制：每次工具调用后，将上一轮的原始工具响应压缩为摘要替换到历史窗口中。教师模型基于"清洁"的摘要上下文生成高质量推理和动作。但训练时，学生模型需要基于原始噪声历史来预测这些专家级动作
   - **技术优势**: 这种不对称设计迫使学生模型内化去噪和信息提取能力，学会从噪声中"看穿"找到关键信号

3. **完全开源的数据集和模型**
   - **方法**: 合成 10.3k 英文 + 1.4k 中文样本，基于 Qwen3-30B-A3B 进行 SFT 训练
   - **技术优势**: 首个由纯学术团队实现 SOTA 并完全开源训练数据的搜索智能体

# Experiments

## Core Contribution Impact (Ablation Studies)

### 主要结果对比

| 模型 | 训练方式 | BrowseComp | BC-ZH | xbench | WideSearch |
|------|---------|------------|-------|--------|------------|
| OpenSeeker-v1-30B-SFT | SFT | **29.5%** | **48.4%** | **74.0%** | **59.4%** |
| Tongyi DeepResearch | CPT+SFT+RL | 43.4% | 46.7% | 75.0% | - |
| WebSailor-V2-30B (SFT) | SFT | 24.4% | 28.3% | 61.7% | - |
| DeepDive-32B | SFT+RL | 15.3% | 29.7% | 51.8% | - |
| MiroThinker-32B-v0.1 | SFT | 10.6% | 13.8% | - | - |

**关键发现**：
- 仅用 SFT，OpenSeeker 在 BrowseComp-ZH 上超越了使用 CPT+SFT+RL 的通义 DeepResearch（48.4% vs 46.7%）
- 数据质量远比数量重要：11.7k 样本 > 147k 样本（MiroThinker）

### 数据难度分析

![数据难度对比（中文）](figures/fig-011.png)
*图：OpenSeeker-v1-Data-ZH 与 BrowseComp-ZH 的难度对比。OpenSeeker 数据平均 46.35 次工具调用、76.1k tokens，而 BrowseComp-ZH 仅 26.98 次调用、15.1k tokens。*

![数据难度对比（英文）](figures/fig-012.png)
*图：OpenSeeker-v1-Data-EN 与 BrowseComp-EN 的难度对比。英文数据难度与基准相当。*

### 与同类开源工作对比

![工具调用分布对比](figures/fig-013.png)
*图：与 REDSearcher 的工具调用次数对比。OpenSeeker 数据的平均工具调用次数显著更高（EN: 45.92 vs 36.91, ZH: 46.35 vs 20.02），证明数据更具挑战性。*

### 相同数据量下的对比

| 数据 | 样本数 | BrowseComp | xbench | WideSearch |
|------|--------|------------|--------|------------|
| WebSailor-V2-10k | 10k | 24.50% | 62.67% | 38.91% |
| WebSailor-V2-5k + WebLeaper-5k | 10k | 27.50% | 62.33% | 41.70% |
| **OpenSeeker-v1-Data** | **11.7k** | **29.50%** | **74.00%** | **59.40%** |

## Limitation

1. **单次训练运行**：由于资源限制，结果仅基于单次训练运行、默认超参数，无任何数据筛选或超参优化

2. **英文数据尚未更新**：英文数据尚未更新到最新 QA 标准，难度略低于中文数据

3. **工具集限制**：目前仅支持纯网页搜索，未集成更多样化的工具和数据源

4. **上下文窗口约束**：需要平衡信息保留与上下文窗口限制
