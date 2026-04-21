# Quick View

**Title**: FastUMI: A Scalable and Hardware-Independent Universal Manipulation Interface with Dataset  
**Authors**: Zhaxizhuoma, Kehui Liu, Chuyue Guan, Zhongjie Jia, Ziniu Wu, Xin Liu, Tianyu Wang, Shuai Liang, Pengan Chen, Pingrui Zhang, Haoming Song, Delin Qu, Dong Wang, Zhigang Wang, Nieqing Cao, Yan Ding, Bin Zhao, Xuelong Li  
**arXiv**: [2409.19499v2](https://arxiv.org/abs/2409.19499v2)  
**Year**: 2025  

# Question

如何把“手持式、传感器增强”的示教接口做成**低成本、硬件无关、可快速部署**的数据采集系统，并且在**遮挡/铰链操作**等真实场景下保持稳定追踪与高数据质量，从而支撑通用操作策略学习？

# Task

构建 FastUMI：用手持设备采集 FPV（第一视角）视频 + 末端位姿/夹爪开合等多模态数据，并能在多种机械臂/夹爪上快速部署一致的观测视角，最终开源一个覆盖 22 个日常任务、>10,000 条轨迹的真实数据集，并验证其对 ACT/DP 等模仿学习算法的有效性。

# Challenge

- **硬件强耦合**：原 UMI 与特定夹爪（如 WSG-50）等组件绑定，换平台需要机械改造、传感器重标定、代码参数调整，推广成本高。  
- **追踪链路复杂且脆弱**：原 UMI 依赖 GoPro VIO + SLAM，遇到长时间遮挡（如开柜门/抽屉）容易失稳；同时校准与坐标变换复杂、复现门槛高。  
- **FPV 数据分布对策略学习不友好**：近端第一视角导致机械臂本体不可见、场景/几何变化大、单目缺少显式深度，ACT/DP 容易出现不可达/非法姿态或深度误差导致失败。  

# Insight

把“可扩展数据采集”当成一个端到端工程问题：  
**硬件层做解耦与标准化视角对齐**，**软件层用现成可靠的追踪模块替换复杂 VIO/SLAM**，再配套**数据验证与算法适配**（对 FPV、无深度、非平行夹爪等现实因素做针对性改造），才能同时降低部署门槛与提高学习效果。

![FastUMI tasks benchmark montage](figures/fig-056.png)  
*Figure (Paper Fig. 9): 论文用于策略评测的 12 个任务集合，覆盖铰链类、抓放类、推扫类与按压类操作。*  

# Contribution

1. **硬件解耦：手持端与上机端的“同视角”可迁移设计**
   - **Approach**:  
     - 手持端：GoPro 鱼眼用于宽视角观测；RealSense T265 用于末端位姿追踪；夹爪开合用指尖 marker/ArUco 测量。  
     - 上机端：提供 ISO 标准法兰板、可串联的延长臂与相机支架、可插拔指尖模块，使 GoPro 视角能对齐到与手持端一致。  
   - **Technical Advantage**: 不绑定特定机械臂/夹爪几何，依靠模块化结构快速适配；通过统一视角标准实现“手持示教→机器人执行”的直接迁移。

![Robot-mounted deployment example](figures/fig-002.jpeg)  
*Figure (Paper Fig. 1 子图示例): FastUMI 可快速部署到不同机械臂/夹爪，保持相机相对指尖的近似一致视角。*  

2. **软件即插即用：用 T265 追踪替代 GoPro VIO/SLAM**
   - **Approach**:  
     - 以 ROS 节点采集多模态流；用统一时钟做同步，下采样到 20Hz，并对 T265 漂移用“回到桌面蓝色槽位”触发 loop-closure/必要时重启重置。  
     - 不再让 GoPro 承担定位追踪，只负责高分辨率视频记录与观测一致性。  
   - **Technical Advantage**: 大幅减少标定与参数调优，遮挡场景下更稳健，部署成本与复现难度显著降低。

![T265 APE over time](figures/fig-059.png)  
*Figure (Paper Fig. 11): 轨迹 APE 随时间变化，靠近桌面导致可见特征减少会出现误差峰值，回到初始视角后 loop-closure 可恢复。*  

3. **数据生态：质量验证 + 多算法兼容的数据格式**
   - **Approach**:  
     - 质量门控：要求采样 pose 的 High confidence 占比 ≥95%，对低置信度片段插值、对速度/加速度/姿态突变做阈值筛除。  
     - 同时产出 TCP 轨迹（绝对/相对）与关节轨迹（IK 解算），并以 HDF5（可转 Zarr）统一存储，适配 ACT/DP 等不同范式。  
   - **Technical Advantage**: 降低“采到的数据不可用”的风险，让数据直接进入训练流水线并便于复用/扩展模态。

4. **面向 FastUMI 数据分布的算法适配**
   - **Approach**:  
     - **Smooth-ACT**：在 Transformer decoder 上加 GRU 做局部时间平滑，减少非法关节跳变。  
     - **PoseACT**：预测末端位姿（可用相对 TCP），提升跨平台鲁棒性并减少极端关节角。  
     - **Depth-Enhanced DP**：用 Depth Anything V2 为数据离线/在线补深度图，显著改善需要精确深度的任务。  
     - **动态误差补偿**：针对非平行夹爪闭合导致 TCP 沿局部 Z 轴漂移，按夹爪开合宽度实时补偿并再 IK。  
   - **Technical Advantage**: 直接对准 FPV 的关键痛点（不可见机械臂、深度不足、夹爪几何差异），把“能学会”转化为“能稳定执行”。

# Experiments

## Data Quality（T265 vs MINI）

论文用光学动捕提供 GT，对不同任务下的 pose 误差做统计（TABLE I），并指出：低遮挡时 T265 精度更好；遮挡更严重时 MINI 更稳定，但频率更低（附录 TABLE VII）。

## Baselines（ACT vs DP，12 任务）

在每个任务 200 条示教训练、每任务 15 次测试（TABLE II）：
- 多数任务 ACT/DP 都能达到较高成功率，说明数据集足够多样。  
- 需要精确深度的任务（如 Open Drawer / Pick Lid / Open Ricecooker）里，**原始 DP 更易失败**；而 ACT 在某些任务会出现未见过的极端关节姿态（FPV 下机械臂不可见导致）。  

## Ablation / Core Contribution Impact（算法增强）

- **Depth-Enhanced DP（TABLE III）**：  
  - Pick Lid：53.33% → 80.00%（+26.67%）  
  - Open Ricecooker：20.00% → 93.33%（+73.33%）  
- **ACT 变体（TABLE IV）**：Smooth-ACT、PoseACT 在 Pick Bear / Sweep Trash 等任务上显著提升；相对 TCP 表示对长轨迹任务更有利，但对“高度精确”任务可能有权衡。  

# Limitation

- **模态受限**：主要依赖视觉，缺少力/触觉，难覆盖易碎/精细力控任务。  
- **平台范围**：当前覆盖单臂/双臂，尚未扩展到移动操作等更复杂形态。  
- **连线与便携性**：依赖有线传输，野外/移动部署受限，未来需无线与边缘算力方案。  

