# GitHub 项目导航

按学习、编排、编码执行、协议和评测分类。项目定位来自各自 README 或官方文档；“可借鉴”与“第一步”是本库建议。核验日期：**2026-10-10**，核验范围是页面与定位，未运行全部项目，也未核实所有 Release/API。

不按 Star 排名，不把不同任务的榜单成绩放在同一张效果表中。运行前固定 tag/commit、检查许可、依赖、账号和工具权限。

## 学习与资料发现

| 项目 | 类型与定位 | 可借鉴 / 第一项练习 |
| --- | --- | --- |
| [Microsoft AI Agents for Beginners](https://github.com/microsoft/ai-agents-for-beginners) | 课程；概念、工具、规划、协作等设计模式 | 按模式学习并运行一个课程示例，记录其服务要求 |
| [Hugging Face Agents Course](https://github.com/huggingface/agents-course) | 课程源码；配套概念与工具实践 | 从基本动作和观察开始，结合[课程页面](https://huggingface.co/learn/agents-course/unit0/introduction) |
| [Awesome LLM Agents](https://github.com/kaushikb11/awesome-llm-agents) | 社区项目发现索引，属于二级线索 | 借鉴分类和维护记录；技术结论回到项目原始文档核验 |

## 编排与 Harness

| 项目 | 类型与定位 | 可借鉴 / 第一项练习 |
| --- | --- | --- |
| [LangGraph](https://github.com/langchain-ai/langgraph) | 底层状态编排框架；持久执行与人工介入 | 自定义分支与检查点；测试暂停后恢复 |
| [Deep Agents](https://github.com/langchain-ai/deepagents) | 基于 LangGraph 的 Harness；规划、上下文、委派 | 追踪文件任务的计划和工具事件，检查文件后端 |
| [OpenAI Agents Python](https://github.com/openai/openai-agents-python) | Agent、工具、handoff、guardrail、追踪 SDK | 按[官方文档](https://developers.openai.com/api/docs/guides/agents/sdk)跑单工具任务，再测试交接 |
| [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) | Python/.NET Agent 与工作流框架 | 阅读状态与协作样例，确认身份及服务依赖 |
| [CrewAI](https://github.com/crewAIInc/crewAI) | Crews 角色协作与 Flows 事件流程 | 用同一任务对比固定流程和角色委派 |
| [smolagents](https://github.com/huggingface/smolagents) | 精简工具 Agent，支持代码动作 | 跟踪动作到执行路径，确认生成代码的隔离 |
| [AutoGen](https://github.com/microsoft/autogen) | 多 Agent 消息与 AgentChat 分层；已进入维护模式 | 学习已有架构；新项目按官方建议关注 Agent Framework |

具体适用边界见[框架选型](../docs/framework-selection.md)。本库未照搬任何项目代码或性能数字。

## 编码 Agent 与工作空间

| 项目 | 类型与定位 | 可借鉴 / 第一项练习 |
| --- | --- | --- |
| [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) | 精简编码 Agent 与命令执行循环 | 从最小循环读起，在隔离测试仓库中追踪一次修改与测试 |
| [SWE-agent](https://github.com/SWE-agent/SWE-agent) | 通过工具处理仓库任务；官方主要开发投入已转向 mini-swe-agent | 学习已有环境交互与配置，注意教程版本 |
| [OpenHands](https://github.com/OpenHands/OpenHands) | 当前主仓库承载 Agent Canvas 与运行控制入口 | 学习界面与运行控制边界；执行层看下方 SDK |
| [OpenHands Software Agent SDK](https://github.com/OpenHands/software-agent-sdk) | Python SDK、Agent Server、工具、工作空间与事件 | 跑独立 SDK 示例，确认本地/远程工作空间与权限 |

上述工具可能执行代码、写文件或调用外部服务。阅读[安全指南](../docs/safety.md)，先在隔离环境中使用无敏感数据的任务。

## 协议与评测

| 项目 | 类型与定位 | 可借鉴 / 第一项练习 |
| --- | --- | --- |
| [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) | 官方协议客户端与服务端 SDK | 暴露一个只读工具，验证参数、错误和协议兼容 |
| [AgentBench](https://github.com/THUDM/AgentBench) | 多环境 Agent 评测 | 学习动作接口、任务判定与失败分析 |
| [SWE-bench](https://github.com/SWE-bench/SWE-bench) | 仓库 Issue 修复评测 | 固定子集与容器，理解补丁的测试验收 |
| [WebArena](https://github.com/web-arena-x/webarena) | 可复现网站任务环境 | 固定环境快照，确认状态重置与功能验收 |
| [τ-bench](https://github.com/sierra-research/tau-bench) | 工具、用户和业务政策交互评测 | 比较最终业务状态及重复运行可靠性 |

## 这轮具体借鉴了什么

- 课程项目：按阶段提供“概念 → 示例 → 验收产物”的学习入口。
- 项目索引：按能力定位分类，并将维护状态和核验日期写入导航。
- LangGraph、Deep Agents：把状态、恢复、预算、上下文与委派拆成可讨论的工程职责。
- 编码与评测项目：把最终产物和真实工具观察作为验收依据。
- MCP SDK：将工具接入协议与编排、权限、验收区分。

这些是本库的内容组织与工程解释，并非对上游效果的复现结论。更详细的阅读范围与状态变更见[来源核验说明](verification-notes.md)。

继续：[学习路线](../docs/learning-roadmap.md) · [项目复现卡片](../templates/project-card.md)。
