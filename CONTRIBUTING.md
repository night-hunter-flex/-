# 贡献指南

欢迎补充原始资料、项目复现、失败案例、工程指南和文档修正。仓库以中文讲解为主，保留英文技术名称和论文原题。

## 资料放在哪里

| 内容 | 位置 |
| --- | --- |
| 原始论文与官方文档 | [资料索引](agent-knowledge-base/resources/reading-list.md) |
| 项目入口、定位与维护状态 | [GitHub 导航](agent-knowledge-base/resources/github-projects.md) |
| 概念、选型或工程指南 | agent-knowledge-base/docs/ |
| 可运行的独立练习 | agent-knowledge-base/examples/ |
| 深入阅读与复现记录 | 使用[分析卡片](agent-knowledge-base/resources/template.md)或[复现卡片](agent-knowledge-base/templates/project-card.md)，保存到相应主题目录 |

## 新条目的最低要求

- 可访问的原始来源、完整标题、类型、作者/维护方。
- 首次发布日期、文档版本或代码提交；另记核验日期。
- 阅读范围：仅摘要、指定章节、全文或仅 README。
- 要解决的问题、核心设计、适用范围与局限。
- 分开写“来源声明”“本库分析”和“实际复现”。
- 不用 Star 或宣传数字代替质量评价；不写未经核实的“最好”“生产可用”。

摘要阅读不能标记为全文审查。评测结论记录数据、模型、环境、预算、判定与失败。只修文档时无需伪造实验结果。

## 版权与引用

优先链接并用自己的语言概括。复制代码、图片或数据前检查对应许可并保留其要求的声明；不能因仓库公开就假定可任意复用。不要自行更改本仓库整体许可。

## 提交前检查

从仓库根目录执行，Python 3.10+，不需要第三方依赖：

```bash
python scripts/check_docs.py
python -m unittest discover -s scripts -p "test_*.py"
python -m unittest discover -s agent-knowledge-base/examples/minimal-agent -p "test_*.py"
python agent-knowledge-base/examples/minimal-agent/run_eval.py
```

链接检查器只覆盖普通 Markdown 内联链接指向的本地文件，跳过 fenced code 和行内代码；不验证外部 URL、锚点、HTML 或 reference-style 链接。新文档请使用本库现有内联链接格式。

提交说明写清问题、改动、来源核验日期与验证结果；新增页面补齐导航。不要提交 API Key、真实用户资料或含秘密的日志。内容提议和纠错可使用 Issue 模板。
