# Requests 技术简报（github-project-brief 验证报告）

> 本报告由 `github-project-brief` 技能生成，仅依据 **psf/requests 官方仓库文件与文档**。所有证据均来自固定 commit 下的官方文件快照。

## 快照元数据

| 字段 | 值 |
|---|---|
| 仓库 | psf/requests |
| 固定 commit SHA | `3c7baaa05ab4aa49cc819ce3a819d260de19c157` |
| 分支来源 | `refs/heads/main`（pinned = true） |
| fetched_at_utc | `2026-11-21T11:11:45.108513+00:00` |
| 快照目录 | 本样例只分发简报与去敏后的 manifest，不分发原始快照文件。 |
| manifest 路径 | [manifest.json](manifest.json)（仓库内去敏副本） |

本报告所有引用链接均固定指向上述 commit SHA，不使用可变的 `main` 分支链接。

---

## 一、项目定位

Requests 是一个简单而优雅的 Python HTTP 库（README 原文：*"Requests is a simple, yet elegant, HTTP library."*）[README L9](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/README.md#L9)。官方口号为 **"Requests: HTTP for Humans™"** [index.rst L6](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/docs/index.rst#L6)，源码元数据中的描述为 *"Python HTTP for Humans."* [__version__.py L6](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/__version__.py#L6)。

Requests 让你能极其简单地发送 HTTP/1.1 请求 [README L26](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/README.md#L26)。它是当今下载量最大的 Python 包之一：每周约 300M 次下载，被 4,000,000+ 个仓库依赖 [README L28](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/README.md#L28)。

当前版本为 **2.34.2** [__version__.py L8](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/__version__.py#L8)，许可证为 **Apache-2.0** [__version__.py L12](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/__version__.py#L12)[pyproject.toml L9](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/pyproject.toml#L9)。原作者 Kenneth Reitz [__version__.py L10](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/__version__.py#L10)；维护者为 Ian Stapleton Cordasco 与 Nate Prewitt [pyproject.toml L13-L16](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/pyproject.toml#L13-L16)，贡献指南另提到 Seth Michael Larson 为共同维护者 [contributing.rst L14-L15](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/docs/dev/contributing.rst#L14-L15)。

README 列出的支持特性 [README L44-L56](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/README.md#L44-L56)：Keep-Alive 与连接池、国际化域名与 URL、带 Cookie 持久化的 Session、浏览器式 TLS/SSL 验证、Basic/Digest 认证、类 dict 的 Cookies、自动内容解压与解码、多部分文件上传、SOCKS 代理支持、连接超时、流式下载、自动 `.netrc`、分块 HTTP 请求。

## 二、主要模块

requests 包采用 src 布局，包位于 `src/requests` 下，通过 `[tool.setuptools.packages.find] where = ["src"]` 发现 [pyproject.toml L83-L84](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/pyproject.toml#L83-L84)。顶层 `__init__.py` 将各模块的公开 API 汇总导出：

- 顶层便捷函数 `request` / `get` / `options` / `head` / `post` / `put` / `patch` / `delete` 来自 `api` 模块 [__init__.py L171](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/__init__.py#L171)。
- `Session`、`session` 来自 `sessions` 模块 [__init__.py L185](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/__init__.py#L185)。
- `Request`、`Response`、`PreparedRequest` 来自 `models` 模块 [__init__.py L184](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/__init__.py#L184)。
- `codes`（HTTP 状态码映射）来自 `status_codes` 模块 [__init__.py L186](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/__init__.py#L186)。
- 异常集合来自 `exceptions` 模块 [__init__.py L172](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/__init__.py#L172)。

各模块职责（引自各自模块 docstring）：

- `api.py`：实现 Requests API，提供 `request()`（L24）及 `get`/`options`/`head`/`post`/`put`/`patch`/`delete` 便捷函数（L74–L171）[api.py L5](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/api.py#L5)。
- `sessions.py`：提供 `Session` 对象，用于跨请求管理和持久化设置（cookies、auth、proxies）[sessions.py L5-L6](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/sessions.py#L5-L6)。
- `models.py`：包含驱动 Requests 的核心对象 [models.py L5](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/models.py#L5)。
- `adapters.py`：包含 Requests 用于定义和维护连接的传输适配器 [adapters.py L5-L6](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/adapters.py#L5-L6)。
- `auth.py`：包含 Requests 的认证处理器 [auth.py L5](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/auth.py#L5)。
- `utils.py`：提供 Requests 内部使用、且对外可用的实用函数 [utils.py L5-L6](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/utils.py#L5-L6)。
- `status_codes.py`：定义 HTTP 状态码的通用名称到数字码的映射 [status_codes.py L2-L4](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/status_codes.py#L2-L4)。
- `exceptions.py`：包含 Requests 的异常集合 [exceptions.py L5](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/src/requests/exceptions.py#L5)。

## 三、"启动流程"说明 + 安装 / 使用 / 开发与测试入口

**说明**：Requests 是一个 **Python 库**，不是 Web 服务或独立应用，没有需要启动的服务进程或守护程序，因此 **不存在"服务端启动流程"**。下文按官方文档整理三类入口：安装、基本使用、开发与测试。

### 3.1 安装

- 从 PyPI 安装：`python -m pip install requests` [install.rst L13-L15](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/docs/user/install.rst#L13-L15)[README L35](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/README.md#L35)。
- 源码安装：克隆仓库后 `cd requests && python -m pip install .` [install.rst L35-L36](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/docs/user/install.rst#L35-L36)。
- 获取源码：`git clone https://github.com/psf/requests.git` [install.rst L25](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/docs/user/install.rst#L25)，或下载 tarball `https://github.com/psf/requests/tarball/main` [install.rst L27-L29](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/docs/user/install.rst#L27-L29)。
- 克隆注意：因历史坏 commit 时间戳（issue #2690），建议使用 `git clone -c fetch.fsck.badTimezone=ignore https://github.com/psf/requests.git`，或全局 `git config --global fetch.fsck.badTimezone ignore` [README L58-L71](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/README.md#L58-L71)。

### 3.2 基本使用

- GET：`r = requests.get('https://api.github.com/events')` [quickstart.rst L32](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/docs/user/quickstart.rst#L32)。
- POST：`r = requests.post('https://httpbin.org/post', data={'key': 'value'})` [quickstart.rst L40](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/docs/user/quickstart.rst#L40)。
- 完整示例（README）：`r = requests.get('https://httpbin.org/basic-auth/user/pass', auth=('user', 'pass'))`，随后访问 `r.status_code`、`r.headers`、`r.encoding`、`r.text`、`r.json()` [README L12-L23](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/README.md#L12-L23)。

### 3.3 开发与测试

- 安装开发依赖：`python -m pip install -r requirements-dev.txt`（Makefile `init` 目标）[Makefile L2-L3](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/Makefile#L2-L3)；`requirements-dev.txt` 内容为 `-e .[socks]` 及 pytest、pytest-cov、pytest-httpbin、httpbin、trustme、wheel [requirements-dev.txt L1-L7](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/requirements-dev.txt#L1-L7)。
- 运行测试：`python -m pytest tests`（Makefile `test` 目标）[Makefile L4-L5](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/Makefile#L4-L5)；`ci` 目标额外生成 `python -m pytest tests --junitxml=report.xml` [Makefile L7-L8](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/Makefile#L7-L8)。
- tox 环境矩阵：`py{310,311,312,313,314}-{default, use_chardet_on_py3}` [tox.ini L2](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/tox.ini#L2)，测试命令 `pytest {posargs:tests}` [tox.ini L9-L10](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/tox.ini#L9-L10)。
- pytest 配置：`testpaths = ["tests"]`，并开启 `--doctest-modules` [pyproject.toml L111-L115](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/pyproject.toml#L111-L115)。
- 代码贡献流程：Fork → 跑测试 → 写测试 → 改代码 → 重跑测试 → 向 `main` 分支发 PR [contributing.rst L70-L81](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/docs/dev/contributing.rst#L70-L81)。
- 代码风格：使用 pre-commit 编排格式工具，本地与 CI 均会运行 [contributing.rst L97-L104](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/docs/dev/contributing.rst#L97-L104)。

## 四、核心依赖

运行时依赖（`[project].dependencies`）[pyproject.toml L18-L23](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/pyproject.toml#L18-L23)：

| 依赖 | 版本约束 |
|---|---|
| charset_normalizer | `>=2, <4` |
| idna | `>=2.5, <4` |
| urllib3 | `>=1.26, <3` |
| certifi | `>=2023.5.7` |

可选依赖（`[project.optional-dependencies]`）[pyproject.toml L53-L56](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/pyproject.toml#L53-L56)：

| extra | 依赖 |
|---|---|
| security | （空列表） |
| socks | `PySocks>=1.5.6, !=1.5.7` |
| use_chardet_on_py3 | `chardet>=3.0.2, <8` |

依赖组（`[dependency-groups]`，PEP 735）：
- `test`：`requests[socks]`、`pytest-httpbin==2.1.0`、`httpbin~=0.10.0`、`pytest-cov`、`pytest-mock`、`pytest-xdist`、`pytest>=3`、`trustme` [pyproject.toml L58-L68](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/pyproject.toml#L58-L68)。
- `typecheck`：`pyright`、`typing_extensions`、`chardet`、`cryptography`、`PyOpenSSL` [pyproject.toml L69-L75](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/pyproject.toml#L69-L75)。

构建系统：`setuptools>=61.0` + build-backend `setuptools.build_meta` [pyproject.toml L1-L3](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/pyproject.toml#L1-L3)。版本号动态取自 `requests.__version__.__version__` [pyproject.toml L80-L81](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/pyproject.toml#L80-L81)。

## 五、运行要求

- Python：`requires-python = ">=3.10"` [pyproject.toml L17](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/pyproject.toml#L17)；README 声明官方支持 Python 3.10+ [README L38](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/README.md#L38)，文档同样说明支持 Python 3.10+ 并在 PyPy 上运行良好 [index.rst L79](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/docs/index.rst#L79)。
- setup.py 在 Python < 3.10 时打印 *"Requests requires Python 3.10 or later."* 并 `sys.exit(1)` [setup.py L3-L5](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/setup.py#L3-L5)。
- classifiers 声明支持 Python 3.10–3.15、CPython、PyPy，以及 Free Threading 2-Beta [pyproject.toml L26-L44](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/pyproject.toml#L26-L44)。
- 无明确操作系统限制（classifier 含 *"Operating System :: OS Independent"*）[pyproject.toml L32](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/pyproject.toml#L32)。

---

## 资料范围与未确认项

**资料范围**：本简报仅使用固定 commit `3c7baaa05ab4aa49cc819ce3a819d260de19c157` 下的官方仓库文件（README.md、setup.py、pyproject.toml、requirements-dev.txt、tox.ini、Makefile、LICENSE）、官方文档（docs/index.rst、docs/user/quickstart.rst、docs/user/install.rst、docs/dev/contributing.rst）以及 `src/requests` 下核心源码文件，共 **21 个 `ok:true`（HTTP 200）文件**，证据均来自 manifest 记录的快照。

**未确认项 / 官方资料未说明**：

1. 主要模块的逐符号清单（如各异常类、工具函数签名）本次未逐一展开，仅依据模块 docstring 与 `__init__.py` 导出关系说明职责。
2. Requests 为 Python 库，官方资料未说明任何"启动流程/服务进程"；本简报已明确该点，并用安装 / 基本使用 / 开发测试入口替代。
3. `security` extra 为空列表，官方未说明其用途 [pyproject.toml L54](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/pyproject.toml#L54)。
4. 官方声明项目处于"永久特性冻结"状态，仅 BDFL 可批准新特性 [contributing.rst L155-L157](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/docs/dev/contributing.rst#L155-L157)；具体 BDFL 是谁，官方资料未直接指名。
5. `use_chardet_on_py3` extra 的详细用途，官方元数据仅给出依赖约束、未展开说明 [pyproject.toml L56](https://github.com/psf/requests/blob/3c7baaa05ab4aa49cc819ce3a819d260de19c157/pyproject.toml#L56)。
6. 本次快照未抓取仓库中非关键文件（如 `ext/` 徽标图片、`tests/` 目录下的测试源码），相关细节不在本简报证据范围内。

---

## 附录 A：快照逐文件清单

以下清单与 manifest.json 完全一致，共 **21 个 ok:true 文件**（数据逐项取自 manifest，未经改写或推算）。仓库内的去敏 manifest 副本见 [manifest.json](manifest.json)。

| # | path | bytes | lines | sha256 |
|---|---|---|---|---|
| 1 | README.md | 2906 | 76 | `2a9268c9be5f4dc9abe9105740be7c5234babc3dd2b25eb11ca376c538a0c67b` |
| 2 | setup.py | 179 | 9 | `1728c11af4134997015ab07547544852e2f7e103c79a5b0486a8486799f50e0a` |
| 3 | pyproject.toml | 3404 | 125 | `345f26b9f691435e39d0eb6f7f4150a390f43175b22f8d61ac95e7f2827f0a77` |
| 4 | requirements-dev.txt | 93 | 7 | `aed8622c9a3d9361a9cdbe71a4643831387aff5f622ebdd68de598a8b258c841` |
| 5 | tox.ini | 285 | 18 | `65aeb46c94fc5723a9764bb029fdb448539658fe47d3a39550a829b2383804fd` |
| 6 | Makefile | 834 | 27 | `c31f5628de71af324c7db9b61579e8a287caae87f76586d70994a7dc86964ec7` |
| 7 | LICENSE | 10142 | 175 | `09e8a9bcec8067104652c168685ab0931e7868f9c8284b66f5ae6edae5f1130b` |
| 8 | src/requests/__init__.py | 5637 | 219 | `80534322a1a3167d8775829ee220a6acf4fe455f3f778c4b8e94bcf7fadfa0b5` |
| 9 | src/requests/__version__.py | 435 | 14 | `abba90670b0370a3dc40d97c2dea46a35d4bec941ff10d7c3cf3098ef04a17f9` |
| 10 | src/requests/api.py | 7152 | 180 | `4d15480ac046f089209798e8650476ef4a28ebe6f81b400758f8ef42ec6b5509` |
| 11 | src/requests/sessions.py | 34072 | 920 | `3d2089736ced93b2b405624a943f866d22652b17df06a85eb010f86272fc3e7d` |
| 12 | src/requests/models.py | 41462 | 1184 | `a3351c3c12a86bf5ed211533875350bc4791e9327a685f8c19ba54343e471e26` |
| 13 | src/requests/adapters.py | 27992 | 748 | `cc9b1b02694fee0353481fbad84fe3ddbedec4441dba54df7914c63f2aa85937` |
| 14 | src/requests/auth.py | 12107 | 354 | `fdc8bb34a8a5a088b169ca13277d107b0bc94ee63ed5e89dd4f5569d9b2bb04c` |
| 15 | src/requests/utils.py | 36061 | 1155 | `b879cb3f671cf1c28e8ff9b2b02151bcdb8974b4820a514cfdd1f5a038443cd2` |
| 16 | src/requests/status_codes.py | 4351 | 128 | `1950f47c89cf18019787e07d8ce48f66d6b38e622f7d94d70a90247fee6c040e` |
| 17 | src/requests/exceptions.py | 4564 | 162 | `c5e18f3352454968e337bb3056f0867df2f37c0a0d2c1a77dc05e7e0b3c0411b` |
| 18 | docs/index.rst | 3635 | 144 | `b9a698849d129bec56fcb19d6078f3c60c626bda6b4a4e105966ec3ceb1d1115` |
| 19 | docs/user/quickstart.rst | 19213 | 573 | `5914de6a636d91ca2ca3a0df55ef8e57359e3fe364fb7176fdee60d231fe2e9f` |
| 20 | docs/user/install.rst | 1038 | 36 | `8b70734839932fa0a53da6e1d97e9c8077fe15f6e06747f24acf154feea039db` |
| 21 | docs/dev/contributing.rst | 6584 | 165 | `37e7765220386a5f81feadf77ac676954188aa4f3371d04b7534ee8d3326ed2b` |

**一致性核对**：上表 21 个 `path` 与 `requests_snapshot_manifest.json` 中 `files[].path` 逐项一致，`bytes`、`lines`、`sha256` 均直接复制自 manifest，无推算、无改写。
