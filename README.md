# 清律健康 - Python 后端

> 为清律健康 App 提供 RESTful API 服务，包含用户认证、健康数据管理、AI 健康分析。

## 技术栈

- **Python**: 3.13+
- **Web 框架**: FastAPI + Uvicorn
- **数据库**: MySQL 8.0 + SQLAlchemy ORM
- **认证**: JWT (PyJWT) + bcrypt
- **AI**: LangChain + DeepSeek / OpenAI 兼容 API（ReAct Agent + Tools）
- **定时任务**: APScheduler
- **数据校验**: Pydantic v2

## 功能模块

### 用户认证 (`/api/auth`)

- 注册 / 登录 → 返回 JWT Token
- 获取/更新个人信息（身高、体重同步到数据库）
- 密码 bcrypt 加密存储

### 健康数据 (`/api/health`)

- 健康记录 CRUD（体重、BMI、体脂、血压、心率、血糖、步数、睡眠）
- 仪表盘（综合评分 + 指标摘要）
- 趋势数据（weight / bmi / heart_rate / blood_sugar 等，支持 7-365 天）
- 饮水记录（今日杯数、打卡 +1、设定目标）
- 提醒计划 CRUD + 打卡
- 体重目标（设定/查询目标体重和日期）
- 睡眠记录（录入/查询今日/历史睡眠数据）

### 健康知识 (`/api/knowledge`)

- 文章列表（支持标签筛选、关键词搜索）
- 文章详情（带收藏状态）
- 收藏 / 取消收藏
- 收藏列表

### AI 分析 (`/api/analysis`)

- 健康报告生成（规则引擎 / LLM 双模式）
- 健康顾问对话（基础版）
- 健康 Agent（ReAct Agent + 10 个工具，自动查询数据并回答）

### AI 对话 (`/api/chat`)

- 会话管理（新建 / 列表 / 删除）
- 消息收发（保存对话历史 → Agent 回答）
- **ReAct Agent 工具调用**：LLM 自动决定调用哪个工具，执行后继续推理

## API 一览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录 |
| GET | `/api/auth/me` | 当前用户信息 |
| PUT | `/api/auth/me` | 更新个人信息 |
| POST | `/api/health/records` | 录入健康数据 |
| GET | `/api/health/records` | 查询历史记录 |
| PUT | `/api/health/records/{id}` | 更新健康记录 |
| DELETE | `/api/health/records/{id}` | 删除健康记录 |
| GET | `/api/health/dashboard` | 首页仪表盘 |
| GET | `/api/health/trends/{field}` | 趋势数据 |
| GET | `/api/health/water` | 今日饮水 |
| POST | `/api/health/water/drink` | 喝水打卡 |
| PUT | `/api/health/water/goal` | 设定饮水目标 |
| GET | `/api/health/plans` | 提醒计划列表 |
| POST | `/api/health/plans` | 创建提醒计划 |
| PUT | `/api/health/plans/{id}` | 更新提醒计划 |
| DELETE | `/api/health/plans/{id}` | 删除提醒计划 |
| POST | `/api/health/checkin/{id}` | 打卡 |
| GET | `/api/health/goal/weight` | 获取体重目标 |
| PUT | `/api/health/goal/weight` | 设置体重目标 |
| POST | `/api/health/sleep` | 录入睡眠数据 |
| GET | `/api/health/sleep/today` | 今日睡眠 |
| GET | `/api/health/sleep/history` | 睡眠历史 |
| GET | `/api/knowledge/articles` | 文章列表 |
| GET | `/api/knowledge/articles/{id}` | 文章详情 |
| POST | `/api/knowledge/favorites/{id}` | 收藏 |
| DELETE | `/api/knowledge/favorites/{id}` | 取消收藏 |
| GET | `/api/knowledge/favorites` | 收藏列表 |
| GET | `/api/analysis/report` | AI 健康报告 |
| POST | `/api/analysis/chat` | 健康顾问对话 |
| POST | `/api/analysis/agent` | 健康 Agent |
| POST | `/api/chat/sessions` | 新建会话 |
| GET | `/api/chat/sessions` | 会话列表 |
| DELETE | `/api/chat/sessions/{id}` | 删除会话 |
| GET | `/api/chat/sessions/{id}/messages` | 消息列表 |
| POST | `/api/chat/sessions/{id}/send` | 发送消息 |

## 项目结构

```
QingLvBack/
├── .env                       # 环境变量（不提交到 git）
├── .env.example               # 环境变量模板
├── .gitignore
├── requirements.txt
├── main.py                    # 启动脚本（uvicorn --reload）
├── qinglv.sql                 # 全量数据库初始化脚本（含所有表 + 测试数据）
└── app/
    ├── main.py                # FastAPI 入口 + 生命周期 + CORS
    ├── config.py              # 配置（从 .env 读取）
    ├── database.py            # SQLAlchemy 连接 + Session 依赖
    ├── models/                # ORM 模型
    │   ├── user.py            # User（身高/体重单位：cm / 公斤）
    │   ├── health.py          # HealthRecord, WaterIntake, ReminderPlan,
    │   │                      # CheckinRecord, WeightGoal, WaterGoal, SleepRecord
    │   │                      # 含唯一约束：water(user+date), checkin(user+plan+date), sleep(user+date)
    │   ├── knowledge.py       # KnowledgeArticle, KnowledgeFavorite
    │   └── chat.py            # ChatSession（cascade delete）, ChatMessage
    ├── schemas/               # Pydantic v2 请求/响应模型（含字段校验）
    │   ├── user.py            # UserProfileUpdate: gender Literal, height/weight ge/le
    │   ├── health.py          # HealthRecordCreate: 全字段 ge/le 约束
    │   │                      # SleepRecordCreate: 深睡+浅睡 ≤ 总时长校验
    │   ├── knowledge.py
    │   ├── analysis.py        # AgentRequest.history: max_length=50
    │   └── chat.py
    ├── routers/               # API 路由
    │   ├── auth.py
    │   ├── health.py
    │   ├── knowledge.py
    │   ├── analysis.py
    │   └── chat.py
    ├── services/              # 业务逻辑
    │   ├── auth_service.py    # JWT 生成/验证 + bcrypt
    │   ├── health_service.py  # 原子 drink_water, 单次查询 checkin_streak, 并发安全
    │   ├── ai_analysis.py     # ReAct Agent + 规则引擎回退
    │   ├── agent_tools.py     # Agent 工具定义（10 个工具）
    │   └── mock_generator.py  # 模拟数据生成（健康、睡眠、饮水）
    └── middleware/
        └── auth.py            # JWT Bearer 认证中间件
```

## 快速开始

### 1. 安装依赖

```bash
cd QingLvBack
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS qinglv DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 导入全量 SQL（含所有表结构 + 30 篇健康知识 + 测试数据）
mysql -u root -p qinglv < qinglv.sql
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，修改以下配置：

```env
MYSQL_PASSWORD=你的MySQL密码
SECRET_KEY=随机字符串              # 生产环境务必修改
LLM_API_KEY=sk-your-deepseek-key  # 可选，不配则使用规则引擎分析
```

### 4. 启动

```bash
# 方式一：直接运行（带热重载）
python main.py

# 方式二：命令行
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问 `http://localhost:8000/docs` 查看 Swagger 文档。

### 5. 默认账号

首次启动自动创建 demo 用户（需 `MOCK_DATA_ENABLED=true`）：

- 用户名: `demo`
- 密码: `demo123`
- 体重: 68 公斤

同时自动回填 30 天模拟健康数据（体重、血压、心率、血糖、步数、睡眠、饮水）。

## 模拟数据

- `MOCK_DATA_ENABLED=true` 时，启动自动创建 demo 用户并回填数据
- 每天凌晨 1:00 自动为所有用户生成当日健康数据（APScheduler）
- 模拟数据有合理的随机波动和长期趋势（体重缓慢下降）
- 自动生成睡眠记录（总时长、深睡、浅睡、质量评分）
- 所有体重数据单位统一为 **公斤**

## 数据完整性

| 表 | 唯一约束 | 说明 |
|---|---|---|
| `water_intake` | `(user_id, date)` | 每人每天一条饮水记录 |
| `checkin_records` | `(user_id, plan_id, checkin_date)` | 每人每天每个计划只能签到一次 |
| `sleep_records` | `(user_id, date)` | 每人每天一条睡眠记录 |
| `chat_messages` | 外键 `ON DELETE CASCADE` | 删除会话自动清理消息 |

关键业务逻辑：
- **饮水 +1**：使用 `UPDATE SET cup_count = cup_count + 1` 原子操作，避免并发竞争
- **签到**：`IntegrityError` 捕获兜底，防止唯一约束冲突
- **连续签到天数**：单次查询 + Python 端计算，避免 N+1 查询

## 字段校验（Pydantic v2）

| Schema | 校验规则 |
|---|---|
| `UserProfileUpdate.gender` | `Literal["男", "女"]` |
| `UserProfileUpdate.height` | `50 ≤ x ≤ 250` |
| `UserProfileUpdate.weight` | `10 ≤ x ≤ 300` |
| `HealthRecordCreate.*` | 所有数值字段均有 `ge/le` 上下界 |
| `SleepRecordCreate` | `深睡 + 浅睡 ≤ 总睡眠时长` |
| `AgentRequest.history` | `max_length=50` |
| `ChatSendRequest.message` | `max_length=1000` |
| `SessionCreate.title` | `max_length=128` |

## 数据完整性（v2.3 更新）

新增修复：
- **drink_water 先确保记录存在**: 原子 UPDATE 前先调用 `get_today_water()` 创建当日记录，避免喝水丢失
- **get_today_water / create_sleep_record 防并发**: 添加 `IntegrityError` 捕获，防止并发请求导致 500
- **register_user 防并发**: 同名注册的 `IntegrityError` 返回 409 而非 500
- **get_db 异常回滚**: 请求处理异常时自动 `db.rollback()`，防止脏状态残留
- **KnowledgeFavorite 唯一约束**: 新增 `(user_id, article_id)` 唯一约束
- **LLM 异常日志**: `_llm_analysis` 异常不再静默吞掉，改为 `logger.exception()` 记录
- **错误信息脱敏**: AI 对话接口不再向客户端暴露内部异常详情（API 地址、密钥等）

## AI 功能

### 无 LLM API Key

- 使用规则引擎生成健康分析报告
- 对话功能返回规则分析结果 + 提示配置 API Key

### 有 LLM API Key（推荐 DeepSeek）

- 健康报告由 LLM 生成自然语言分析
- **ReAct Agent**：LLM 自动决定调用工具 → 执行 → 继续推理 → 生成回答
- 支持多轮对话，历史消息自动传入
- 三层回退：Agent 异常 → 简单对话模式 → 规则引擎

### Agent 工具列表

| 工具 | 功能 | 触发场景 |
|------|------|---------|
| `get_user_profile` | 查询用户个人信息 | 询问身高、体重、BMI |
| `get_health_records` | 查询历史健康数据 | 询问血压、心率趋势 |
| `get_today_water_intake` | 查询今日饮水 | 询问喝水情况 |
| `get_weight_goal` | 查询体重目标 | 询问减重进度 |
| `get_checkin_streak` | 查询打卡记录 | 询问坚持天数 |
| `get_favorite_articles` | 查询收藏文章 | 询问收藏内容 |
| `analyze_nutrition` | 食物营养分析 | "吃了xxx，帮我分析" |
| `generate_exercise_plan` | 生成运动计划 | "帮我制定运动计划" |
| `predict_health_trend` | 健康趋势预测 | "一个月后体重多少" |
| `assess_health_risk` | 综合健康风险评估 | "我的健康风险" |

---

## 👥 团队协作必看配置指南
本拉取代码后，不同成员可能会因为本地环境差异（如 IP 地址、数据库账号密码、大模型 API Key 额度不同）遇到无法运行或连接超时的问题。请团队小伙伴在跑通项目前，**务必确认并修改**以下配置文件：

### 1. 前端配置：局域网 IP
- **文件路径**：`HealthManagement1.0.1/commons/common/src/main/ets/util/NetworkConfig.ets`
- **需要修改**：将 `DEFAULT_URL` 中的 `100.79.96.224` 替换为您**自己电脑在局域网内的 IPv4 地址**，否则前台发出的请求无法连接到您本地启动的 FastAPI 服务端。
- *(注：为避免代码冲突，该文件已加入 `.gitignore`)*

### 2. 后端配置：环境变量文件 (.env)
- **文件路径**：在 `HealthManagement-backened/QingLvBack/` 目录下创建一个名为 `.env` 的文件。
- **需要修改**：
  - 数据库账号密码：将 `MYSQL_USER` 和 `MYSQL_PASSWORD` 更改为您本地 MySQL 真实的用户名和密码。
  - DeepSeek API Key：将 `LLM_API_KEY` 替换成您自己的 Key 以防额度受限或冲突。
- *(注：为避免代码冲突，该文件已加入 `.gitignore`)*

### 3. 后端配置：数据库初始化
- **文件路径**：`HealthManagement-backened/QingLvBack/qinglv.sql`
- **需要修改**：在启动后端服务前，请务必先通过 Navicat 等工具在本地数据库新建名为 `qinglv` 的库，并运行此 SQL 文件导入基础结构和测试数据，否则服务无法正常启动。
