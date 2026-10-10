# Agent 资料索引

先读基础论文，再看评测基准；每篇记录后续可迁移到 Harness、工具调用和 Agent 质量评审的思路。论文原文优先使用 arXiv 或会议论文页。

## 基础原理与工具使用

| 资料 | 主题与核心贡献 | 阅读时关注 |
| --- | --- | --- |
| [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)（2022） | 将推理轨迹与任务动作交替生成；行动结果提供外部观察，帮助更新计划和处理异常。 | ReAct 如何利用 observation 更新下一步；它与仅生成计划的方式有何不同。 |
| [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761)（2023） | 研究模型如何学习决定何时调用 API、传入什么参数，以及如何把工具结果用于后续生成。 | 工具调用的触发、参数生成、结果整合分别由什么机制支持。 |

## 评测与真实任务

| 资料 | 主题与核心贡献 | 阅读时关注 |
| --- | --- | --- |
| [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688)（ICLR 2024） | 在多个交互环境中评估 LLM Agent，并分析长程推理、决策和指令遵循等失败来源。 | 环境覆盖、任务成功条件、失败分类；单一最终分数遗漏了什么过程信息。 |
| [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770)（ICLR 2024） | 给模型真实代码仓库和 Issue，要求生成解决问题的代码补丁。 | 任务如何复现和验证；代码定位、修改、测试各环节如何影响最终成功率。 |

## 建议阅读顺序

1. **ReAct**：理解 Agent 的“观察—行动”循环。
2. **Toolformer**：聚焦模型如何学会使用工具。
3. **AgentBench**：从交互环境角度学习 Agent 评测。
4. **SWE-bench**：观察真实工程任务中的端到端验收。

## 后续待补充

- 记忆、反思与自我修正：记录方法是否使用外部状态、何时更新，以及反思是否有可验证收益。
- Harness 工程：补充长任务状态管理、检查点、恢复、预算和人工接管的研究或工程报告。
- Agent 框架：按官方文档、执行模型、工具生态、限制和版本记录，避免只比较 API 表面。
- 多 Agent：记录协作收益是否超过通信、协调和错误传播成本。

## 新增资料记录格式

每项至少填写：标题、来源链接、资料类型、主题、发布日期或版本、阅读状态。分析性笔记补充核心贡献、局限、证据和对目标项目的启发。