# Agent 资料索引

先读基础论文，再看评测基准；每篇记录后续可迁移到 Harness、工具调用和 Agent 质量评审的思路。论文原文优先使用 arXiv 或会议论文页。

本轮核验日期：2026-10-10。论文的标题、首版日期与摘要已核对；本页简述不代表全文方法审查或复现。阅读范围与来源边界见[核验说明](verification-notes.md)。

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

## 记忆、反思与更多任务环境

以下日期为 arXiv 首次提交日期；条目类型均为论文，阅读范围为摘要核对。局限与工程问题是本库的阅读建议。

| 资料与日期 | 摘要中的核心内容 | 阅读时要验证的边界 |
| --- | --- | --- |
| [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) · 2023-03-20 | 用语言反馈与 episodic memory 影响后续尝试，不更新模型权重 | 反馈来自哪里？哪些任务受益？错误反思是否被保留？ |
| [WebArena: A Realistic Web Environment for Building Autonomous Agents](https://arxiv.org/abs/2307.13854) · 2023-07-25 | 提供可复现的网站交互环境，按任务功能完成判定 | 环境怎样重置？动作与最终网站状态是否一致？ |
| [GAIA: a benchmark for General AI Assistants](https://arxiv.org/abs/2311.12983) · 2023-11-21 | 问题涉及推理、多模态、浏览与工具使用 | 文件、网络与答案判定影响了哪些结果？ |
| [τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains](https://arxiv.org/abs/2406.12045) · 2024-06-17 | 模拟用户与业务工具交互，核对最终数据库状态并衡量多次运行可靠性 | 模拟器与业务政策如何影响评分？可靠性指标与 pass@k 有何不同？ |

前四篇的首版日期依次为 ReAct 2022-10-06、Toolformer 2023-02-09、AgentBench 2023-08-07、SWE-bench 2023-10-10；表中的 ICLR 年份是发表信息，不是首版日期。

## 官方工程资料

类型均为官方文档或作者项目 README；本轮核验日期为 2026-10-10，未固定软件 Release。运行前按[复现卡片](../templates/project-card.md)记录实际版本。

| 来源与维护方 | 主题 | 适合带着什么问题阅读 |
| --- | --- | --- |
| [LangGraph](https://github.com/langchain-ai/langgraph) · LangChain | 状态编排、持久执行、人工介入 | 恢复时哪些动作会再次执行？ |
| [Deep Agents](https://github.com/langchain-ai/deepagents) · LangChain | 规划、上下文、文件与委派 Harness | 如何管理计划、上下文和文件后端？ |
| [Agents SDK](https://developers.openai.com/api/docs/guides/agents/sdk) · OpenAI | 应用内循环、工具、交接、校验与追踪 | 哪些控制由 SDK 提供，哪些归应用负责？ |
| [追踪与集成](https://developers.openai.com/api/docs/guides/agents/integrations-observability) · OpenAI | 运行、模型与工具事件 | 会记录和传出什么数据？ |
| [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) · Microsoft | Python/.NET Agent 与工作流 | 协作、身份和状态如何结合？ |
| [MCP 架构](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture) · MCP | Host/Client/Server、工具、资源、提示模板 | 协议接入与业务授权的边界在哪里？ |
| [MCP 安全实践（draft）](https://modelcontextprotocol.io/docs/draft/tutorials/security/security_best_practices) · MCP | 协议接入的安全设计 | 草案与实际实现版本是否一致？ |

## 扩展主题入口

- 记忆与反思：先读 Reflexion，再区分反馈证据与模型自评。
- Harness：[工程指南](../docs/harness-engineering.md)。
- 框架：[选型指南](../docs/framework-selection.md)与[项目导航](github-projects.md)。
- 多 Agent：[协作模式与对照实验](../docs/multi-agent.md)。
- 评测：[任务集、指标与失败分类](../docs/evaluation.md)。

## 新增资料记录格式

每项至少填写：标题、来源链接、资料类型、主题、发布日期或版本、阅读状态。分析性笔记补充核心贡献、局限、证据和对目标项目的启发。
