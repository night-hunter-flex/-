# 来源核验与整理说明

本轮核验日期：2026-10-10。目的：为中文 Agent 学习与工程知识库补充项目入口、论文索引与实践指导。内容由 AI 辅助检索和整理，不是系统性文献综述，也不宣称覆盖所有项目。

## 方法与证据范围

从仓库现有的闭环、Harness、工具、框架、评测主题出发，查阅项目自身 README、官方文档和 arXiv 页面。收录能核对标题、定位及原始入口的资料。社区 Awesome 列表只用于发现与分类参考，不作为技术功能或效果的主要证据。

| 来源类别 | 本轮检查 | 可以支持 | 未检查或不能支持 |
| --- | --- | --- | --- |
| 论文 | arXiv 标题、首版日期、摘要与部分页面说明 | 研究问题、摘要中的方法和基准定位 | 全文方法审查、统计重算、复现实验 |
| GitHub 项目 | README、官方文档入口、显式维护提示与重定向 | 当前页面声明的定位和学习入口 | 所有代码路径、所有版本兼容、部署效果 |
| 官方文档 | 所引用页面的概念与功能说明 | 协议角色、执行职责、追踪与编排概念 | 对特定应用的安全或效果保证 |
| 本库工程建议 | 根据任务约束提出的设计与练习 | 可实施的学习步骤与验收标准 | 未运行的项目成绩或普遍性能结论 |

原论文可能报告数字，但本轮索引不转录历史榜单分数；过去的实验不能直接说明当前模型或真实业务表现。官方项目也由其维护方描述，可能含宣传性判断，本库不将其转述为独立验证。

## 核验后调整的入口

| 条目 | 观察与来源 | 本库处理 |
| --- | --- | --- |
| AutoGen | [README](https://github.com/microsoft/autogen)标明维护模式，建议新用户使用 Microsoft Agent Framework | 保留架构学习入口；补上[后继框架](https://github.com/microsoft/agent-framework) |
| SWE-agent | [README](https://github.com/SWE-agent/SWE-agent)说明主要开发转向 mini-swe-agent | 增加[精简项目](https://github.com/SWE-agent/mini-swe-agent)，不引用其宣传成绩 |
| SWE-bench | 旧 princeton-nlp 地址重定向到 [SWE-bench/SWE-bench](https://github.com/SWE-bench/SWE-bench) | 使用当前规范地址 |
| OpenHands | [主仓库](https://github.com/OpenHands/OpenHands)说明界面与 [Software Agent SDK](https://github.com/OpenHands/software-agent-sdk) 的职责 | 分别链接控制入口和执行层 |
| MCP | [架构页面](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)有明确文档版本 | 固定概念来源；接入前核对 SDK/服务端版本 |
| OpenAI Agents SDK | [官方说明](https://developers.openai.com/api/docs/guides/agents/sdk)说明循环在应用中执行 | 不与服务端托管运行方式混淆 |

## 如何解释“已核验”

“页面核验”表示读取了相应来源并核对本库写出的定位；不表示用户已读、全文已审查、项目已安装或所有链接永久有效。具体运行另用[复现卡片](../templates/project-card.md)记录。

来源失效时先查迁移、归档、Release 或原作者入口。发现功能变化时更新描述与日期；无法核实的功能不要新增为事实。不要静默把重命名项目、协议新旧版本或不同基准子集混在一起。

## 后续维护

优先补充真实任务的失败案例、带版本的复现和验收集。已有练习中只有离线计算演示提供代码与回归用例；其他项目仍是实现建议。外部页面与本地文件链接分别维护：自动检查负责本地文件链接，外部资料需要人工复核原始页面。
