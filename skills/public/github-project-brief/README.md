# GitHub 项目技术简报技能



这是一个基于 DeerFlow 扩展的技能：读取公开 GitHub 仓库的官方资料，生成带来源链接的中文技术简报。



## 要解决的问题



分析 GitHub 仓库时，匿名 REST API 可能遇到速率限制；`main` 等分支也会持续变化，导致引用内容难以复现。



本技能会固定分析时的 commit，并记录所读取文件的快照信息，让简报中的结论能够回溯到特定版本的官方文件。



## 工作流程



1. 解析仓库地址和目标分支。

2. 解析该分支对应的 commit SHA。

3. 从官方仓库抓取需要的文件。

4. 生成 manifest，记录每个文件的路径、字节数、行数和 SHA-256。

5. 基于快照生成中文简报，并让重要结论链接到固定 commit 下的官方文件。



快照脚本还会校验仓库路径，并在抓取失败时报告错误，避免把缺失的证据当作事实。



## 在 DeerFlow 中使用



将本目录放在 DeerFlow 仓库的以下位置：



`skills/public/github-project-brief`



然后让 DeerFlow 分析一个公开仓库，例如：



> 使用 github-project-brief 技能分析 https://github.com/OWNER/REPO。请基于官方来源固定仓库快照，生成带引用链接和 manifest 的中文技术简报。



## 个人扩展内容



- 增加按固定 commit 抓取仓库文件的快照脚本。

- 为抓取文件生成带 SHA-256、行数和字节数的 manifest。

- 在技能说明和简报模板中加入固定版本引用及中文简报要求。

- 为路径校验和抓取失败处理增加保护。



DeerFlow 的 Agent 平台和基础运行能力属于上游项目；本技能是基于 DeerFlow 扩展的工作。



## 验证记录



本技能已在两种不同类型的仓库上完成验证：



- `bytedance/deer-flow`：多服务 Agent 应用，快照包含 9 个文件。

- `psf/requests`：Python 库，快照包含 21 个文件。



两份快照的文件元数据都与 manifest 核对一致；Requests 简报还抽查了 10 条跨章节引用，均能在对应快照中找到支持。



## 样例与交叉验证

以下样例来自已验收的公开仓库分析，均固定到生成时的 commit。Requests 的 manifest 公开副本仅移除了本机工作区路径字段 written_to 和 snapshot_dir；文件路径、字节数、行数及 SHA-256 保留。

- **DeerFlow 应用**：[中文技术简报](examples/deer-flow/brief.md) · [manifest](examples/deer-flow/manifest.json) · commit 40ef4f6ac1974ba3334f833c16da43b7e059ba47
- **Requests Python 库**：[中文技术简报](examples/requests/brief.md) · [manifest](examples/requests/manifest.json) · commit 3c7baaa05ab4aa49cc819ce3a819d260de19c157

Requests 样例包含 21 个文件，manifest 元数据逐项核对一致，并抽查 10 条跨章节引用；DeerFlow 样例包含 9 个文件。样例展示的是基于清单文件的技术简报，不代表对整个仓库进行完整代码审计。
## 范围与限制



- 本技能依赖 DeerFlow，不能单独作为 Web 应用运行。

- 简报依据 manifest 中列出的文件生成，不等于对整个仓库进行完整代码审计。

- 官方资料未提供依据的内容应明确标为“未确认”，不应猜测补全。



## 上游项目



本技能扩展自 [DeerFlow](https://github.com/bytedance/deer-flow)。使用或分发时，请遵循仓库根目录中的许可证和版权说明
