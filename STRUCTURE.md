# DDLManager 项目结构与说明

下面是为 `DDLManager` 推荐的文件和模块组织方式，适合从单文件原型过渡到可维护的小型 Python 项目。

## 推荐目录（最小可用）

- DDLManager/
  - README.md
  - STRUCTURE.md        # 本文件
  - .gitignore
  - .env.example        # 示例环境变量（例如 DEEPSEEK_API_KEY）
  - requirements.txt    # 或者使用 pyproject.toml
  - apikey.txt          # （可选，本地开发用）
  - src/

    # 推荐项目结构与迁移指南（基于 `main.py` 分析）

    下面是针对当前 `DDLManager/main.py` 的分析结论与一个更清晰、可扩展的项目结构（包含 QCE 接口 和 GUI(Electron+FastAPI) 路线）。

    ## 基于 `main.py` 的主要发现
    - **敏感信息**：明文出现 `API_KEY`、邮件账号密码，应立即移入环境变量或安全存储并从仓库移除。
    - **明显错误**：`event.add('discription', ...)` 拼写错误，应为 `description`；`events` 可能在无日历时未定义。
    - **网络配置**：DAV URL 没有 scheme（建议使用 `https://...`）。
    - **依赖**：使用到 `icalendar`, `caldav`, `openai`/DeepSeek SDK，应列入 `requirements.txt`。

    ## 设计目标（迁移后）
    - 将单体脚本拆为可测试、可复用的模块；
    - 增加 `QCE`（QQ 消息读取）模块，作为可插拔的消息源；
    - 提供一个本地 HTTP 后端（FastAPI），供 GUI（Electron/Vue）调用；
    - 把凭据与配置从代码中抽离，使用环境变量与 `.env`。

    ## 推荐目录（包含 GUI 与 QCE）

    - DDLManager/
      - README.md
      - STRUCTURE.md        # 本文件
      - .gitignore
      - .env.example        # 列出 DEEPSEEK_API_KEY、QCE credentials 等
      - requirements.txt    # Python 依赖
      - package.json        # Electron 前端依赖（若使用 Electron）
      - pyproject.toml      # 可选，用于 Poetry
      - src/
        - ddlmanager/
          - __init__.py
          - cli.py              # CLI 入口（轻量）
          - core.py             # 把 `main.py` 的核心逻辑封装为函数（解析、构建 event、调用 AI）
          - config.py           # 从环境变量或 .env 读取配置
          - client.py           # 封装 DeepSeek/OpenAI 的调用（重试、错误处理）
          - qce.py              # QCE（QQ）接口：读取消息导出或直接调用 QQ API（可选实现）
          - parser/
            - __init__.py
            - chat_parser.py     # 聊天导出解析逻辑（来自现有 `main.py` 的解析）
          - extractor/
            - deadline_extractor.py
          - calendar_utils.py    # 封装 icalendar/caldav 交互（保存 event、读取 calendars）
          - server.py           # FastAPI 后端：将功能以 REST API 暴露给 GUI
      - electron/              # （可选）Electron 前端工程
        - package.json
        - main.js               # Electron 主进程，负责启动 `server.py` 子进程
        - renderer/             # 前端源码（建议用 Vite + Vue/React）
      - tests/
        - test_core.py
        - test_qce.py

    ## 将 `main.py` 内容映射到新模块（建议）
    - `main()` 中的 I/O（读取 `input_path`、命令行参数）→ `cli.py`。
    - 读取并格式化聊天记录的函数 `extract_text_from_content()`、`format_messages_for_prompt()` → `parser/chat_parser.py` 或 `core.py` 中的公共函数。
    - 调用 AI 的部分 → `client.py`（`ApiClient.chat(messages)`）；把模型名和 base_url 改为配置项。
    - caldav/icalendar 相关创建/保存 event 的逻辑 → `calendar_utils.py`（修复 `description` 拼写并处理异常）。

    ## QCE (`qce.py`) 简要说明
    - 提供两个主要接口：
      - `read_from_file(path) -> List[Message]`：解析导出的 JSON/文本（目前仓库有 `data/` 示例）。
      - `fetch_live(**credentials) -> List[Message]`：如果可行，直接从 QQ 或 QCE API 拉取（需实现认证与节流）。
    - 将 `QCE` 视为一个 `MessageSource` 抽象，以便未来加入其他来源（微信导出等）。

    ## FastAPI 后端（`server.py`）— 最小接口示例
    - 提供 `/parse`（POST，上传 messages 或指向文件） → 返回结构化 DDL JSON
    - 提供 `/calendars`、`/save_event` 等管理日历的端点

    示例运行（开发时）:

    ```bash
    # 在虚拟环境中安装依赖
    python -m venv .venv
    .venv\\Scripts\\activate
    pip install -r requirements.txt

    # 启动后端
    python -m src.ddlmanager.server

    # 在另一个终端，启动 Electron（若使用前端）
    cd electron
    npm install
    npm run dev
    ```

    ## 安全与配置（必读）
    - 把所有敏感配置（API Key、QQ 密码）放到环境变量或 `secrets` 文件，并加入 `.gitignore`。
    - 建议添加 `DEEPSEEK_API_KEY`、`DEESEEK_BASE_URL`、`QCE_USER`、`QCE_PASS` 到 `.env.example`。

    ## 迁移步骤（短期可交付清单）
    1. 新增 `src/ddlmanager/core.py`，把 `main.py` 的可复用函数搬入并改为无副作用的函数。  
    2. 新增 `src/ddlmanager/config.py` 与 `src/ddlmanager/client.py`，把 API 调用与配置抽离。  
    3. 新增 `src/ddlmanager/qce.py`（从 `data/` 示例先实现 `read_from_file()`）。  
    4. 新增 `src/ddlmanager/server.py`（FastAPI minimal，暴露 `/parse`）并在 `electron/main.js` 中通过 `child_process.spawn` 启动它。  
    5. 修复 `main.py` 中的拼写与硬编码，并把它作为 `examples/` 或删除（迁移后留存历史）。

    ## 我可以帮你做的事（请选择）
    - A) 生成完整的 scaffold（`src/ddlmanager/*`、`requirements.txt`、最小 `electron/` 项目）。
    - B) 仅实现 `qce.py`（读取 `data/` 的示例文件），并把 `main.py` 的函数重构到 `core.py`。  
    - C) 仅生成 FastAPI `server.py` 和 minimal 前端调用示例（不含 Electron）。

    回复你要的选项，我会立刻开始并把变更提交到仓库。

    ---
    (已基于 `main.py` 分析并更新。若需我马上 scaffold，请回复选项 A、B、或 C。)


