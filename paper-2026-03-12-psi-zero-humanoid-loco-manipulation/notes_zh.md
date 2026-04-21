# Quick View

**Title**: Ψ0: An Open Foundation Model Towards Universal Humanoid Loco-Manipulation  
**Authors**: Songlin Wei, Hongyi Jing, Boqian Li, Zhenyu Zhao, Jiageng Mao, Zhenhao Ni, Sicheng He, Jie Liu, Xiawei Liu, Kaidi Kang, Sheng Zang, Weiduo Yuan, Marco Pavone, Di Huang, Yue Wang  
**arXiv**: [2603.12263v1](https://arxiv.org/abs/2603.12263v1)  
**Year**: 2026  

# Question

如何在**仅少量昂贵的真实人形机器人数据**下，把**大量可扩展的人类第一视角操作视频**中的世界知识与动作先验，高效迁移到**人形机器人长时程（>2000 steps）全身行走+灵巧操作（loco-manipulation）**控制上？

# Task

给定语言指令 \(\\ell\) 与当前观测 \(o_t=(I_t, q_t)\)（头部相机图像 + 本体感觉状态），预测未来动作 chunk \(a_{t:t+H}\) 并在真实人形（Unitree G1 + Dex3-1）上稳定执行 8 个长时程任务（推车、擦拭、开水龙头、倒水、下蹲放置、拉出薯片罐托盘并投掷等）。

# Challenge

- **跨形体差异（embodiment gap）**：人类与人形机器人在 DoF、动力学、动作频率等方面差异巨大，把两种动作分布硬塞进一个统一端到端策略往往是次优甚至不稳定。  
- **数据与成本矛盾**：真实人形遥操作昂贵且难扩展；纯依赖互联网视频/异构机器人混合数据噪声大、对全身控制帮助有限。  
- **推理延迟导致抖动**：VLA 往往是十亿级模型，真实部署存在 160ms 量级延迟，产生“停-想-动”的 chunk 切换抖动，长时程任务更易失败。  

# Insight

不要用单一策略去同时拟合“人类视频动作分布 + 机器人关节控制分布”。将学习过程**解耦并分阶段优化目标**：  
先用高质量人类第一视角视频让 VLM 学到“看懂任务/动作语义”的表征，再用少量高质量人形机器人数据把“语义→关节控制”的映射学精，并用训练时 RTC 解决推理延迟带来的动作抖动。

![Humanoid loco-manipulation overview](figures/fig-000.png)  
*Figure (Paper Fig. 1): Ψ0 在真实环境完成多种 pantry 场景的全身移动+操作任务，体现长时程与多技能组合的目标。*  

# Contribution

1. **三系统（System-2/1/0）人形 VLA 架构**
   - **Approach**:  
     - **System-2**：Qwen3-VL-2B-Instruct 作为视觉-语言骨干，输出 VL 特征。  
     - **System-1**：基于 flow-matching 的 **MM-DiT** 动作专家（约 500M），条件于 VL 特征预测未来关节空间动作 chunk \(a_{t:t+H}\)。  
     - **System-0**：下肢/躯干由 RL tracking policy（AMO）把高层 8-DoF lower-body action 映射到 15-DoF 下肢关节 \(q_{lower}\)。  
   - **Technical Advantage**: 将“任务语义理解”和“具身动力学/关节控制”拆开，避免共训两种异构分布导致的次优解；MM-DiT 的 joint attention + dual modulation 比 naive DiT 更好融合 VL 与动作 token。

2. **分阶段训练配方：VLM 预训练 + 动作专家后训练 + 小样本任务微调**
   - **Approach**:  
     - **Stage 1（预训练）**：在 EgoDex（约 829h）+ 少量 Humanoid Everyday（31h）上，把连续 48-DoF task-space 动作用 FAST tokenization 离散化，仅做**下一步动作 token**自回归预测（而非长 chunk），以更低计算成本学习表征与语义。  
     - **Stage 2（后训练）**：冻结 VLM，用 Humanoid Everyday（约 3M frames）在**关节空间**训练 flow-based 动作专家，直接建模人形关节控制分布。  
     - **Stage 3（微调）**：每个真实任务仅用 80 条遥操作轨迹，微调动作专家 40k steps。  
   - **Technical Advantage**: 用“高质量人类操作视频”提供可扩展的语义/动作先验，用“少量高质量人形关节轨迹”补齐具身动力学细节，实现高数据效率。

3. **训练时 Real-Time Chunking（RTC）与异步部署系统**
   - **Approach**:  
     - 训练时随机 mask chunk 前 \(d\\sim U(0,d_{max})\) 的 token 并不计入损失，让模型学会在已有“已提交动作”约束下生成后续动作，抑制 chunk 切换的发散。  
     - 部署端采用 client/server 两线程：30Hz Control Loop 驱动观测-动作闭环；Inference Loop 异步生成下一 chunk，达到阈值 \(t\\ge s_{min}\) 时无缝切换。  
   - **Technical Advantage**: 在十亿级推理延迟下仍保持连续控制，减少抖动与碰撞，提高长时程 rollout 稳定性。

![Real-time chunking system](figures/fig-018.jpeg)  
*Figure (Paper Fig. 9): 客户端执行与服务端推理异步并行，通过共享状态与触发条件实现无中断 chunk 切换。*  

4. **面向 loco-manipulation 的单人遥操作数据采集管线**
   - **Approach**: PICO 头显+腕部 tracker 做上肢多目标 IK；MANUS 手套做灵巧手 retargeting；腰/脚 tracker 提供高层速度与朝向命令，下肢由 RL policy 跟踪。  
   - **Technical Advantage**: 将操控拆成“上肢姿态 + 手指灵巧 + 下肢行走指令”，在单操作者条件下提升下肢稳定性与手部表达能力，提升 in-domain 数据质量。

![Teleoperation decomposition](figures/fig-010.png)  
*Figure (Paper Fig. 10, 抽取到单张子图): 将手指/腕/头姿等信号分别映射到 retargeting、multi-target IK 与噪声滤波，并把高层指令交给 RL 下肢控制器。*  

# Experiments

## Real-World Benchmark（8 个真实长时程任务）

- **设置**：每个任务 10 次 rollout；允许人工介入跳过失败子任务以统计子技能成功率；统一观测/动作表示与相同部署代码。  
- **结果要点**：Ψ0 在 8 个任务上整体显著优于对比方法（π0.5、GR00T N1.6、InternVLA-M1、EgoVLA、H-RDT、DP、ACT 等），论文报告整体成功率相比次优基线提升 **40%+**；并强调仅用约 **800h 人类视频 + 30h 真实机器人数据**即可达到最优。  

![Task montage](figures/fig-009.png)  
*Figure (Paper Fig. 6): 八个真实任务与关键子步骤示意，覆盖开水龙头、推车、擦拭、倒水、下蹲、投递等长时程技能组合。*  

## Core Contribution Impact（消融）

论文在一个双臂长时程任务上做消融（Table I），核心趋势：
- **无预训练/无后训练/无 RTC**：整体成功率极低。  
- **加入 EgoDex 预训练**：显著提升（即便预训练动作表示与下游关节空间不同）。  
- **加入后训练（HE）与 RTC**：进一步提升并改善执行稳定性。  
- **MM-DiT > naive DiT**：joint attention + dual modulation 的条件融合更有效。  

# Limitation

- **规模受限**：作者承认计算与时间限制，尚未进一步扩展到更大规模的人类视频与真实机器人数据。  
- **硬件负载限制**：平台 payload 限制会束缚更强操作策略的可实现性。  
- **RTC 形式**：作者指出 test-time guidance 不稳定，因此选择 training-time RTC；这暗示对特定推理/部署形态有依赖。  

