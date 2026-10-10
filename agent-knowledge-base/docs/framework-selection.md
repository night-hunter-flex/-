# Agent 框架选型

先写任务约束，再选执行方式。下表中的能力描述来自项目 README 或官方文档；“适合验证什么”是本库建议，不能代替实际对照实验。核验日期：2026-10-10。

## 项目定位与学习入口

| 项目 | 核心抽象与已说明的能力 | 适合验证什么 | 需要自行确认 |
| --- | --- | --- | --- |
| [LangGraph](https://github.com/langchain-ai/langgraph) | 状态图、持久执行、人工介入 | 自定义分支、检查点和长任务恢复 | 状态存储、部署环境、恢复时副作用处理 |
| [Deep Agents](https://github.com/langchain-ai/deepagents) | 建于 LangGraph 之上的 Harness，提供规划、上下文管理与委派 | 文件任务和多步骤计划 | 文件后端、隔离范围、中间件及预算 |
| [OpenAI Agents SDK](https://developers.openai.com/api/docs/guides/agents/sdk) | Agent、工具、handoff、guardrail、追踪；循环在应用中执行 | 工具调用、专长交接和运行记录 | 模型/工具兼容性、追踪数据处理、应用的权限与状态存储 |
| [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) | Python/.NET Agent 与多 Agent 工作流，提供可观测性集成 | 跨运行时应用、已有 Microsoft 技术栈集成 | 实际使用的连接器、身份体系及服务依赖 |
| [CrewAI](https://github.com/crewAIInc/crewAI) | Crews 表达角色协作，Flows 表达事件驱动流程 | 角色任务与业务流程的组合 | 汇总质量、共享状态、重试和成本 |
| [smolagents](https://github.com/huggingface/smolagents) | 精简 Agent 抽象，支持用代码表达动作及工具调用 | 理解动作如何转换为工具执行 | 生成代码的执行隔离、模型适配和工具权限 |

不同项目可能实现重叠能力；此表不做速度、成本、效果或“生产可用性”排名，也不表示未列出的能力不存在。安装命令和 API 以选定版本的官方文档为准。

## 维护状态会影响选择

[AutoGen 当前 README](https://github.com/microsoft/autogen)说明项目进入维护模式，不再增加新功能，并建议新项目使用 Microsoft Agent Framework。可以继续用 AutoGen 学习消息传递与 AgentChat 分层，但复现旧教程时要确认版本，迁移时参考官方入口。

同样，[SWE-agent](https://github.com/SWE-agent/SWE-agent)说明主要开发投入已转向 [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)。前者适合研究已有设计，后者适合从更小的编码 Agent 执行循环入手。

## 用需求缩小候选

| 需求 | 首先做的验证 | 可考虑的入口 |
| --- | --- | --- |
| 规则稳定的结构化处理 | 固定流程是否已能通过验收？ | 普通程序 + 少量模型调用 |
| 严格控制状态和分支 | 暂停、修改状态、恢复同一任务 | LangGraph |
| 需要现成的计划和文件 Harness | 限定目录内完成多步任务并追踪 | Deep Agents |
| 工具调用与专长交接 | 单 Agent、handoff 两种模式对照 | Agents SDK、Microsoft Agent Framework |
| 角色协作型流程 | 两个专长角色与单 Agent 对照 | CrewAI |
| 学习精简代码动作 | 检查输入到执行的路径和隔离 | smolagents、mini-swe-agent |
| 接入不同工具服务 | 明确协议版本与客户端兼容性 | MCP SDK；再选择编排层 |

这些是试验起点，不是唯一推荐。MCP SDK 负责协议接入，不能直接替代任务状态管理和评测。

## 一次公平的选型实验

从自己的任务中选 10–20 个开发样例，再保留独立验收样例；数量是入门建议，不足以支持一般化性能结论。

1. 固定任务、模型、工具、外部数据快照与验收条件。
2. 统一总工具调用、模型调用、时间与成本上限；记录并行度。
3. 每个候选都测试成功、工具错误、数据缺失、权限拒绝和预算停止。
4. 比较任务成功率、成本、延迟、恢复行为和维护工作量。
5. 保存失败案例与原始事件；不要只保留最终输出或截图。

框架升级后重新跑验收集。若版本迁移改变了工具或评测数据，单独记录这些变化。

下一步：[项目导航](../resources/github-projects.md) · [评测报告模板](../templates/evaluation-report.md)。
