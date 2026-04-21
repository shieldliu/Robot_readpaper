# Robot_readpaper

本仓库用于整理机器人/具身智能相关论文的 PDF、抽取图与中英笔记。

## Papers

- **[π₀.7: a Steerable Generalist Robotic Foundation Model with Emergent Capabilities](paper-2026-04-16-pi0-7/)**
  - **简介**：提出一种通过多样化上下文条件训练的通用机器人基础模型，能够在无需任务特定微调的情况下实现跨任务、跨机器人具身的强泛化能力。模型能够遵循多样化语言指令、在未见环境中执行多阶段任务、实现零样本跨具身泛化，并在具有挑战性的任务上达到与专用RL微调模型相当性能。

- **[Ψ0: An Open Foundation Model Towards Universal Humanoid Loco-Manipulation](paper-2026-03-12-psi-zero-humanoid-loco-manipulation/)**
  - **简介**：提出分阶段训练的人形 VLA（人类第一视角视频预训练 VLM + 关节空间动作专家后训练 + 训练时 RTC），用较少真实人形数据实现长时程全身行走+灵巧操作。

- **[FastUMI: A Scalable and Hardware-Independent Universal Manipulation Interface with Dataset](paper-2025-02-01-fastumi/)**
  - **简介**：重构 UMI 为可快速部署、硬件解耦的数据采集接口（T265 追踪替代复杂 VIO/SLAM），并开源 10k+ 真实示教数据集与面向 FPV 的 ACT/DP 算法适配。