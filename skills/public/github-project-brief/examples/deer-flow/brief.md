# DeerFlow 技术简报

> 本报告基于 DeerFlow 仓库的实际快照生成，所有事实均引用固定 commit SHA 链接，逐条可溯源。

## 快照元数据

| 项目 | 值 |
| --- | --- |
| 仓库 | `bytedance/deer-flow` |
| 分支 | `main` |
| Commit SHA | `40ef4f6ac1974ba3334f833c16da43b7e059ba47` |
| SHA 来源 | `git-refs refs/heads/main`（git smart-HTTP refs 解析） |
| 是否固定 | `pinned = true` |
| 抓取时间（UTC） | `2026-11-21T03:42:51.417756+00:00` |
| Manifest 路径 | `snapshots/bytedance__deer-flow__40ef4f6ac197/manifest.json` |

### 已检查文件清单

| 文件 | bytes | 行数 | SHA-256 |
| --- | --- | --- | --- |
| `README.md` | 11294 | 186 | `c3fd49e14561d8b3599b90d285f6ff899b2f1149f567fa7f8cf0f5217709922b` |
| `Install.md` | 4706 | 87 | `4d84cda8985620d76d12449cfd2276cef66f6fd9d797079310f8c0febb4937cb` |
| `Makefile` | 11177 | 246 | `089edee59f03da881fdd4f176d0cc3089b92f700bd763d036db8309b42a0f3e4` |
| `backend/pyproject.toml` | 5757 | 121 | `c7a5cc17351472d802d44d907a3a26abcf59b44c4aa452f748ae207da560b11a` |
| `frontend/package.json` | 4500 | 138 | `93f969b4f099b15c337401fb29eb69b65b9a68d29448825e838390f335150440` |
| `docs/ARCHITECTURE.md` | 11249 | 197 | `1d726e92bd0241fde81b3be0da8a272ca78b22d946c85585657b61729f157c95` |
| `docs/guide/deployment.md` | 41985 | 490 | `f1b8d7757106f9d4ea057d8f07df2868ba86dbbe97d617a89de0861610de33f7` |
| `backend/README.md` | 30397 | 620 | `bb2e95972ab58ae7224e18f7ceb62ffa84994d42991ee77e3b0ec331fc1b3f9d` |
| `docker/docker-compose-dev.yaml` | 14425 | 296 | `a2f84479a52a91c0da0e8d656222d74d2842a7d470b997a79bc87ca708475cad` |

---

## 1. 项目定位

DeerFlow（**D**eep **E**xploration and **E**fficient **R**esearch **Flow**）是一个开源的「超级智能体框架」（super agent harness），它编排**子智能体（sub-agents）**、**记忆（memory）** 与**沙箱（sandboxes）** 来执行几乎任意任务，并由**可扩展技能（extensible skills）** 驱动 [citation:README.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/README.md#L10)。

在架构上，DeerFlow 被定义为一个基于 LangGraph 构建的开源 super-agent harness，由一个「lead agent」编排整个流程 [citation:ARCHITECTURE.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docs/ARCHITECTURE.md#L18)。项目自述称其「不再是需要你自己拼装的框架，而是一个开箱即用、完全可扩展的超级智能体框架」，基于 LangGraph 与 LangChain，内置文件系统、记忆、技能、沙箱感知执行，以及为复杂多步任务规划与派生子智能体的能力 [citation:README.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/README.md#L101)。

当前后端元数据版本为 `2.3.0-dev`，包描述为「LangGraph-based AI agent system with sandbox execution capabilities」 [citation:backend/pyproject.toml](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/backend/pyproject.toml#L2-L5)。

## 2. 主要模块

### 2.1 服务拓扑

`docs/ARCHITECTURE.md` 描述的是**四项逻辑服务**，Nginx 是唯一公开入口 [citation:ARCHITECTURE.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docs/ARCHITECTURE.md#L26-L28)：

| 逻辑服务 | 端口 | 角色 |
| --- | --- | --- |
| **Nginx** | `2026` | 统一反向代理，浏览器访问入口 |
| **Gateway API** | `8001` | FastAPI REST API + 内嵌 LangGraph 兼容运行时 |
| **Frontend** | `3000` | Next.js Web 界面 |
| **Provisioner** | `8002` | 可选沙箱 provisioner，仅在 provisioner/K8s 模式启用 |

[citation:ARCHITECTURE.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docs/ARCHITECTURE.md#L32-L36)

而 `docker/docker-compose-dev.yaml` 定义的**默认 Docker 栈**在此之外还包含 **Redis**，且 **Provisioner 仅在 `provisioner` profile 下启用**（默认栈不需要 Kubernetes，需显式加 `--profile provisioner`） [citation:docker-compose-dev.yaml](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docker/docker-compose-dev.yaml#L21-L23) [citation:docker-compose-dev.yaml](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docker/docker-compose-dev.yaml#L28-L33)：

- **Redis**：`redis:7-alpine`，作为 Redis Streams 后端，用于跨 worker 的 SSE stream bridge [citation:docker-compose-dev.yaml](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docker/docker-compose-dev.yaml#L42-L43)。
- **Provisioner**：`profiles: [provisioner]`，仅在 `--profile provisioner` 时启用，负责在宿主机 Kubernetes 中创建沙箱 Pod [citation:docker-compose-dev.yaml](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docker/docker-compose-dev.yaml#L61-L63)。

Nginx 路由契约：`/api/langgraph/*` → Gateway 的 LangGraph 兼容运行时（重写为原生 `/api/*`）；其余 `/api/*` → Gateway REST 路由；`/*`（非 API）→ Frontend。这使得标准 LangGraph SDK 客户端无需单独 LangGraph server 即可与 DeerFlow 通信 [citation:ARCHITECTURE.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docs/ARCHITECTURE.md#L41-L46)。

### 2.2 后端：Harness / App 分层

后端为两层，具有**严格的单向依赖** [citation:ARCHITECTURE.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docs/ARCHITECTURE.md#L53-L54)：

- **Harness**（`backend/packages/harness/deerflow/`，导入前缀 `deerflow.*`）：可发布的智能体框架，包含编排、工具、沙箱、模型、MCP、技能、记忆、配置——构建与运行智能体所需的全部能力。
- **App**（`backend/app/`，导入前缀 `app.*`）：未发布的应用代码，即 FastAPI Gateway 与 IM 渠道集成。

**规则**：App 导入 `deerflow`，但 `deerflow` 从不导入 `app`；该边界由 CI 中的 `backend/tests/test_harness_boundary.py` 强制。第三个薄包 `deerflow-extension-api`（`backend/packages/extension-api/`）定义了与宿主无关的扩展契约，供插件实现 [citation:ARCHITECTURE.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docs/ARCHITECTURE.md#L60-L64)。

### 2.3 Harness 子模块

Harness 包结构包含以下子模块 [citation:backend/README.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/backend/README.md#L297-L340)：

- `agents/`：Agent 系统（`lead_agent/` 主智能体、`middlewares/` 中间件、`memory/` 记忆提取与存储、`thread_state.py` 线程状态 schema）
- `sandbox/`：沙箱执行（`local/` 本地文件系统提供者、`sandbox.py` 抽象接口、`tools.py` 提供 bash/ls/read/write/str_replace、`middleware.py` 沙箱生命周期）
- `subagents/`：子智能体委派（`builtins/`、`executor.py` 后台执行引擎、`registry.py` 注册表）
- `tools/builtins/`：内置工具
- `mcp/`：MCP 协议集成
- `models/`：模型工厂
- `skills/`：技能发现与加载
- `config/`：配置系统
- `runtime/`：内嵌运行执行（RunManager、StreamBridge）
- `persistence/`：checkpointer/store 引擎与 schema 迁移
- `guardrails/`：工具调用前授权提供者
- `tracing/`：追踪器工厂与追踪元数据
- `uploads/`、`tui/`、`community/`、`reflection/`、`utils/`

### 2.4 前端

前端为基于 LangGraph SDK 的有状态聊天界面，技术栈为 Next.js 16 / React 19 / TypeScript / Tailwind v4，使用 `@langchain/langgraph-sdk` [citation:ARCHITECTURE.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docs/ARCHITECTURE.md#L107-L109)。

### 2.5 核心组件

后端 README 列出以下核心组件：Lead Agent、Middleware Chain、Sandbox System、Subagent System、Memory System、Tool Ecosystem、Run Event Storage、Gateway API、IM Channels [citation:backend/README.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/backend/README.md#L41-L198)。

## 3. 启动流程

### 3.1 快速开始

`make setup` 运行交互式向导，写入 `config.yaml` 与 `.env`（约 2 分钟）。随后两条路径任选其一 [citation:README.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/README.md#L56-L76)：

- **Docker 路径**：`make docker-init`（拉取沙箱镜像，一次性或镜像更新时）→ `make docker-start`（启动服务）
- **本地路径**：`make check`（校验 Node.js 22+、pnpm、uv、nginx）→ `make install` → `make dev`

最后打开 `http://localhost:2026` [citation:README.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/README.md#L87)。

### 3.2 面向 coding agent 的引导

`Install.md` 明确：若当前目录不是仓库根，先克隆 `https://github.com/bytedance/deer-flow.git` 并进入仓库根；若 `config.yaml` 不存在则运行 `make config`；随后用 `docker info` 探测 Docker 是否可用——可用则 `make docker-init`（仅视为前置准备，不视为服务已启动，下一步是 `make docker-start`）；不可用则 `make check`，若缺 `node`/`pnpm`/`uv`/`nginx` 就停止并报告缺失项，若满足则 `make install`，下一步是 `make dev` [citation:Install.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/Install.md#L41-L52)。

### 3.3 Docker 启动细节

Docker 部署要求 **Docker Compose v2.24+**；`make docker-start` 仅在 `config.yaml` 使用 provisioner 模式时启动 `provisioner`，默认栈不需要 Kubernetes [citation:deployment.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docs/guide/deployment.md#L19-L31)。

## 4. 核心依赖

### 4.1 后端（Python）

后端要求 Python `>=3.12`，核心直接依赖包括 [citation:backend/pyproject.toml](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/backend/pyproject.toml#L6-L42)：

- **自有包**：`deerflow-harness`、`deerflow-extension-api`
- **Web/运行时**：`fastapi>=0.115.0`、`starlette>=1.3.1,<2`、`uvicorn[standard]>=0.34.0`、`httpx>=0.28.0`、`sse-starlette>=2.1.0`、`websockets>=16.0,<17`、`python-multipart>=0.0.31`
- **LangGraph**：`langgraph-sdk>=0.1.51`
- **沙箱**：`e2b-code-interpreter>=2.8.1`
- **IM 渠道**：`lark-oapi>=1.4.0`、`slack-sdk>=3.33.0`、`python-telegram-bot>=21.0`、`dingtalk-stream>=0.24.3`、`wecom-aibot-python-sdk>=0.1.6`
- **认证/安全**：`bcrypt>=4.0.0`、`pyjwt>=2.13.0`、`email-validator>=2.0.0`

另有可选依赖组（postgres、redis、discord、ollama、browser、memory-zh 等）与 `websockets==16.0` 的 override 锁定 [citation:backend/pyproject.toml](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/backend/pyproject.toml#L44-L102)。

### 4.2 前端（Node.js）

前端关键依赖包括 `next@^16.4.5`、`react@^19.0.0`、`@langchain/core@^1.1.15`、`@langchain/langgraph-sdk@^1.5.3`、`@tanstack/react-query`、`zod`、`tailwindcss@^4` 等 [citation:frontend/package.json](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/frontend/package.json#L24-L102)。

## 5. 运行要求

### 5.1 部署规格

官方给出部署规模参考表 [citation:deployment.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docs/guide/deployment.md#L7-L11)：

| 部署目标 | 起步 | 推荐 | 备注 |
| --- | --- | --- | --- |
| 本地评估 / `make dev` | 4 vCPU、8 GB RAM、20 GB 空闲 SSD | 8 vCPU、16 GB RAM | 单个开发者或轻量会话；`2 vCPU / 4 GB` 通常不够 |
| Docker 开发 / `make docker-start` | 4 vCPU、8 GB RAM、25 GB 空闲 SSD | 8 vCPU、16 GB RAM | 镜像构建、bind mount 与沙箱容器需要更多余量 |
| 长期服务器 / `make up` | 8 vCPU、16 GB RAM、40 GB 空闲 SSD | 16 vCPU、32 GB RAM | 推荐用于共享、多智能体运行、报告生成或较重沙箱负载 |

对持久化服务器，推荐 **Linux + Docker** 作为部署目标，macOS 与 Windows 更适合作为开发/评估环境 [citation:deployment.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docs/guide/deployment.md#L13-L14)。

### 5.2 运行时与工具链要求

- **Python**：`>=3.12`（README 徽章与后端 `pyproject.toml` 一致） [citation:README.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/README.md#L3) [citation:backend/pyproject.toml](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/backend/pyproject.toml#L6)
- **Node.js**：`>=22` [citation:README.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/README.md#L4)
- **pnpm**：`>=10.26.2`（`packageManager` 锁定 `pnpm@10.26.2`） [citation:frontend/package.json](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/frontend/package.json#L134-L138)
- **uv** 与 **nginx**：由 `make check` 校验（Node.js 22+、pnpm、uv、nginx） [citation:README.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/README.md#L74)
- **Docker Compose**：`v2.24+`（较旧客户端无法解析可选的 `env_file` 语法） [citation:deployment.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docs/guide/deployment.md#L19-L21)

---

## 资料范围与未确认项

**资料范围**：本报告仅基于上述 9 个快照文件的事实，所有引用均指向本次快照对应的 commit SHA 固定链接（`blob/40ef4f6ac197...`）。快照 commit 为 `40ef4f6ac1974ba3334f833c16da43b7e059ba47`，`pinned = true`，SHA 来源为 git smart-HTTP refs 解析（`refs/heads/main`）。文件清单（含 bytes、行数、SHA-256）来自 manifest `snapshots/bytedance__deer-flow__40ef4f6ac197/manifest.json`。

**未确认项**：
- 本报告未覆盖 `README.md` 中提到的具体「推荐模型」清单、许可证类型细节、Star 历史等（未在本轮已检查文件范围内逐一展开，相关事实可从对应文件进一步核实）。
- 沙箱 provisioner/K8s 模式的完整配置项、IM 渠道的具体接入凭证要求等实现细节，未在本报告展开。

## Sources

- [README.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/README.md) — 项目定位、快速开始、运行时徽章（Python/Node）
- [docs/ARCHITECTURE.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docs/ARCHITECTURE.md) — 服务拓扑、Harness/App 分层、前端技术栈
- [docker/docker-compose-dev.yaml](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docker/docker-compose-dev.yaml) — 默认 Docker 栈服务清单（含 Redis）、Provisioner profile 启用条件
- [backend/README.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/backend/README.md) — Harness 子模块结构与核心组件
- [backend/pyproject.toml](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/backend/pyproject.toml) — 版本、Python 要求与后端依赖
- [frontend/package.json](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/frontend/package.json) — 前端依赖、Node/pnpm engines
- [docs/guide/deployment.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/docs/guide/deployment.md) — 部署规格、Docker Compose 要求
- [Makefile](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/Makefile) — 开发命令入口
- [Install.md](https://github.com/bytedance/deer-flow/blob/40ef4f6ac1974ba3334f833c16da43b7e059ba47/Install.md) — coding agent 引导与启动决策流程

---

## 本次修订项（v2 相对 v1）

1. **保留 commit**：继续使用固定 commit `40ef4f6ac1974ba3334f833c16da43b7e059ba47`，未更换、未重新抓取仓库。
2. **补充快照元数据**：在「快照元数据」表新增 `Manifest 路径` 行（`snapshots/bytedance__deer-flow__40ef4f6ac197/manifest.json`）；「已检查文件清单」表新增 `bytes` 列，逐文件填入 manifest 中的 bytes、lines、SHA-256 实际值（无编造）。
3. **修正服务拓扑表述**：将 2.1 节改为明确区分——`docs/ARCHITECTURE.md` 描述**四项逻辑服务**；`docker/docker-compose-dev.yaml` 的**默认 Docker 栈**还包含 **Redis**，且 **Provisioner 仅在 `provisioner` profile 下启用**（默认栈不需要 Kubernetes）。
4. **补充引用**：将 `docker/docker-compose-dev.yaml` 加入 Sources；为 Redis 与 Provisioner 说明添加固定 SHA 行号引用（`#L42-L43`、`#L61-L63`，以及 `#L21-L23`、`#L28-L33`）。
5. 其余正文与引用保持不变，仅输出至 `github_project_brief_snapshot_v2.md`。
