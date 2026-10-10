# 离线最小执行循环

这个练习使用确定性策略模拟决策：请求 calculator，根据工具观察生成结果。它展示 Harness 的执行机制，没有接入 LLM，也没有使用外部项目代码。

Python 3.10+，标准库，无 API Key、网络或第三方依赖。从仓库根目录运行：

```bash
python agent-knowledge-base/examples/minimal-agent/demo.py --expression "(12 + 8) * 3"
python agent-knowledge-base/examples/minimal-agent/demo.py --expression "12 / 3" --fail-first
python agent-knowledge-base/examples/minimal-agent/run_eval.py
python -m unittest discover -s agent-knowledge-base/examples/minimal-agent -p "test_*.py"
```

正常演示的 output 为 `result=60`。首次失败演示先记录一个 `temporary_unavailable` 事件，再用一次重试得到 `result=4`。

## 读代码的顺序

| 位置 | 职责 |
| --- | --- |
| [demo.py](demo.py) 的 Action、scripted_policy | 将观察转换为结构化动作 |
| calculator_tool、calculate | 参数契约与算术 AST 白名单 |
| run_agent | 工具注册、决策/调用预算、有限重试与停止 |
| run_expression | 注入一次确定性的暂时失败 |
| [cases.json](cases.json) | 8 个预期状态、原因和数值用例 |
| [run_eval.py](run_eval.py) | 比较实际行为与用例预期，失败返回非零退出码 |
| [test_demo.py](test_demo.py) | 验证错误输入、预算、重试、轨迹和评分 |

## 执行边界

表达式只允许数字、括号、正负号及加减乘除。使用 AST 白名单，**没有 eval/exec**；限制输入为 200 字符、64 个 AST 节点，数值及中间结果绝对值不超过 1e12。函数、名字、属性、容器、布尔值和幂运算均不允许。

max_steps 计决策次数；max_tool_calls 计实际执行尝试，包含失败和重试；max_retries 是一次动作的额外重试次数。默认分别为 4、3、1。失败类型是否允许重试由工具错误明确标记。

## 看一次轨迹

```text
decision → tool_call → tool_error（可重试）
         → tool_call → tool_result → decision → stop（completed）
```

输出包含 status、reason、output、tool_calls 和 events。停止状态只有 completed、failed、budget_exceeded。演示没有真实用户数据；扩展工具后应对事件参数与结果脱敏。

## 主动触发边界

以下命令预期返回退出码 1，并输出明确原因：

```bash
python agent-knowledge-base/examples/minimal-agent/demo.py --expression "1 / 0"
python agent-knowledge-base/examples/minimal-agent/demo.py --expression "abs(-1)"
python agent-knowledge-base/examples/minimal-agent/demo.py --expression "1 + 1" --fail-first --max-tool-calls 1
python agent-knowledge-base/examples/minimal-agent/demo.py --expression "1 + 1" --max-steps 1
```

工具成功后仍需一次决策来结束，所以 max_steps=1 会在得到工具结果后因决策额度耗尽而停止。这是显式选择的演示语义。

## 如何解释评测结果

8 个用例包含 3 个完成任务、3 个预期失败和 2 个预算停止。behavior_passed 表示行为符合各自预期；completed_count 表示实际完成数量。全部用例通过，不代表 8 个任务都被完成，也不能衡量真实 LLM 能力或安全性。

演示检查 finish 有观察且输出非空，但不独立判断策略最终答案的真实性。评测器另核对数值与最终输出；真实任务需要独立的产物、来源或业务状态验收。

## 尚未实现的工程机制

未实现模型调用、真实超时/退避、token/费用预算、持久检查点、文件与网络权限、人工审批及外部副作用。自定义 policy 和工具应是本地可信代码；这个循环不是可运行任意插件的安全边界，也不会中止阻塞函数。

后续按[实践项目](../../docs/practice-projects.md)接入模型与真实工具，保留[Harness](../../docs/harness-engineering.md)的预算、错误与权限控制，再建立独立验收集。
