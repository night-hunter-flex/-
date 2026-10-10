# 工具调用与 MCP

工具让执行系统获取观察或改变外部状态。模型提出调用，应用负责校验和执行。本文的工具契约是工程建议；MCP 概念依据[官方架构说明](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)与[官方 Python SDK](https://github.com/modelcontextprotocol/python-sdk)。核验日期：2026-10-10。

## 一份可实现的工具契约

| 字段 | 要说明什么 | 只读资料搜索示例 |
| --- | --- | --- |
| 名称与用途 | 何时应使用此工具 | search_notes：搜索授权资料 |
| 输入 schema | 字段、类型、长度、必填与范围 | query：非空字符串；limit：1–10 |
| 输出 schema | 结果和错误的稳定结构 | 命中项包含路径、片段与版本 |
| 权限与副作用 | 身份、授权范围、是否写入 | 只读指定目录，不访问其他用户 |
| 执行约束 | 超时、大小上限与调用额度 | 单次限时，结果截断有标记 |
| 错误语义 | 可重试错误与终止错误 | 暂时失败可重试；无权限终止 |
| 提交语义 | 重试是否会重复副作用 | 查询可重试；写入需幂等键 |

模型可能生成格式正确但越权的参数；schema 校验通过后仍须执行身份、路径、对象归属和业务权限检查。

示例动作与观察使用应用自定义格式，**不是 MCP 报文**：

```json
{
  "action": {"tool": "search_notes", "arguments": {"query": "checkpoint", "limit": 3}},
  "observation": {
    "ok": true,
    "items": [{"path": "notes/state.md", "excerpt": "检查点记录……", "version": "v1"}],
    "truncated": false
  }
}
```

## MCP 的角色与边界

| 概念 | 职责 |
| --- | --- |
| Host | 承载应用、管理一个或多个客户端 |
| Client | 与服务端交换协议消息 |
| Server | 暴露工具、资源和提示模板 |
| Tools | 可执行能力，如查询或文件操作 |
| Resources | 可供读取的上下文数据 |
| Prompts | 可复用的交互模板 |

官方架构说明列出本地 stdio 和远程 Streamable HTTP 两类传输。协议解决交换方式，不规定应用如何规划任务或管理模型上下文。

SDK 与服务端可能支持不同协议版本。使用教程时同时记录 SDK 版本、服务端版本和协议版本；不能只因包名相同就假定兼容。本页固定链接到 2026-07-28 架构说明，不复述旧教程中的连接握手细节。

## 接入顺序

1. 先用普通函数实现工具，并验证输入、错误与权限。
2. 将工具暴露给 MCP Server，用客户端验证列表、调用和错误返回。
3. 只把当前任务允许使用的工具交给模型，限制结果大小。
4. 通过 Host 执行权限、审批和预算；保留实际工具观察。
5. 测试断连、错误参数、越权请求和协议版本不匹配。

工具描述和远程结果也属于外部数据。新增服务时审查它实际提供的能力，不因名称或“只读”提示就默认信任它。

## 从函数到真实服务

[离线计算工具](../examples/minimal-agent/demo.py)演示严格的工具名和参数校验。升级到真实服务时，进一步实现超时、认证、秘密管理、服务端授权、输出长度控制和持久运行记录。

安全设计可参考 [MCP 官方安全实践](https://modelcontextprotocol.io/docs/draft/tutorials/security/security_best_practices)；这是 draft 链接，实施时再次核对对应版本。项目接入见[GitHub 导航](../resources/github-projects.md)，系统边界见[安全指南](safety.md)。
