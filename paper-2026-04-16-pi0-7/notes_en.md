# Quick View

**Title**: $π_{0.7}$: a Steerable Generalist Robotic Foundation Model with Emergent Capabilities
**Authors**: Physical Intelligence Team
**arXiv**: [2604.15483](https://arxiv.org/abs/2604.15483)
**Year**: 2026

# Question

How can we build a generalist robotic foundation model that can achieve strong out-of-the-box performance across diverse tasks and robot embodiments without task-specific fine-tuning?

# Task

Develop a model that can follow diverse language instructions in unseen environments, perform multi-stage tasks with various kitchen appliances, enable zero-shot cross-embodiment generalization (e.g., folding laundry without prior demonstration), and perform challenging tasks like operating an espresso machine at performance levels matching specialized RL-finetuned models.

# Challenge

Previous robotic foundation models often require task-specific fine-tuning to achieve good performance, limiting their generality. Robot learning faces challenges including data inefficiency, large embodiment gaps, limited language understanding, and difficulty in task compositional generalization.

# Insight

By using diverse context conditioning during training—including language commands, subgoal images, and episode metadata—the model can be precisely steered to perform many tasks with different strategies, enabling it to learn from diverse data sources and distill specialist performance into a generalist model.

![Overview Figure](figures/fig-076.png)
*Figure 1: Prompt overview. π0.7 uses diverse modalities of context in the prompt, including: subtask instructions, subgoal images, and episode metadata.*

# Contribution

1. **Diverse Context Conditioning Training**
   - **Method**: Combining language instructions, subgoal images, and episode metadata (such as task performance and subgoal images) as conditioning during training
   - **Technical Advantage**: Enables learning from diverse data sources including suboptimal (autonomous) data and failures, and allows precise behavior control at inference time by adjusting the context

2. **Subgoal Image Generation with World Model Integration**
   - **Method**: Using a lightweight world model to generate subgoal images as context, supplementing real future images to mitigate train-test mismatch
   - **Technical Advantage**: Improves language following capabilities, especially for complex instructions and dataset bias cases, by introducing semantic understanding from the world model

3. **Episode Metadata for Behavior Steering**
   - **Method**: Incorporating episode metadata (such as speed, quality, mistake flags) into the prompt to steer the model toward desired behavior modes
   - **Technical Advantage**: Enables distilling expert behavior from suboptimal data during training and allows trading off speed vs. quality at inference time by adjusting metadata

![Method Figure](figures/fig-006.png)
*Figure 2: Model architecture showing history vision encoder, subgoal image processing, and action expert components.*

# Experiments

## Core Contribution Impact (Ablation Studies)

On challenging tasks such as laundry folding, espresso making, and box building, π0.7 achieves out-of-the-box performance competitive with specialized RL-finetuned models, and even exceeds them in some tasks.

![Results Figure](figures/fig-017.png)
*Figure/Table 3: Performance comparison on dexterous tasks showing π0.7's success rate and throughput compared to specialist models.*

Removing either episode metadata or evaluation data leads to significant performance drops, indicating these components are crucial for the model's ability to learn from diverse data and generalize effectively.

![Ablation Figure](figures/fig-074.png)
*Figure 4: Ablation study removing metadata or evaluation data, showing performance degradation when these components are missing.*

## Limitation

While π0.7 shows strong generalization capabilities, success rates for completely unseen tasks and robot embodiment combinations typically range from 60-80%, lower than the 90%+ success rates on seen tasks. Additionally, it's practically difficult to definitively determine which tasks are truly "unseen" due to the diversity of the dataset potentially containing related skills with different labels or incidentally as part of other tasks.

![Limitation Figure](figures/fig-112.png)
*Figure 5: Examples of world model generated subgoal images, showing how visual analogies are constructed from text instructions.*