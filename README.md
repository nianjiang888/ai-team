# 一人公司AI团队

> 5个AI员工，帮你管文案、管数据、管运营、管项目、管生意。
> 从"50个独立模板"升级为**自动运转的AI团队系统**。

不是让你学prompt，而是**替你干活**。

---

## 产品介绍

你是一个人，但要干一整个团队的活——写文案、发内容、分析数据、管项目、想策略。

**一人公司AI团队**给你配了5个AI员工，每人有明确的岗位、专业的工作流、可追踪的产出。你只需要在看板上派单，他们自动干活，产出文件直接送到你面前。

## AI员工一览

| 员工 | 代号 | 职责 | 典型产出 |
|------|------|------|---------|
| 文案助理 | CW | 公文、周报、邮件、文案润色 | 排版好的文档文件 |
| 新媒体运营 | SM | 小红书/抖音/公众号/头条内容 | 选题、文案、发布计划 |
| 数据分析师 | DA | 数据整理、报表、趋势分析 | 图表 + 分析报告 |
| 项目管家 | PM | 任务拆解、进度追踪、汇报 | 甘特图、任务看板 |
| 商业顾问 | BC | 创业规划、副业分析、商业计划 | 商业方案文档 |

## 版本说明

| | 免费版 | 专业版 |
|---|---|---|
| AI员工 | 文案助理（1个） | 全部5个 |
| 模板数量 | 10个 | 58个 |
| 看板功能 | 基础版 | 完整版（图表+审批+日报） |
| 获取方式 | GitHub下载 | 付费社群 |
| 价格 | 免费 | 见社群公告 |

> 免费版适合体验核心功能，专业版解锁全部5个员工的协作工作流。

---

## 快速开始（3步）

### 环境要求

- Python 3.10 或以上（[下载地址](https://www.python.org/downloads/)）
- 一个 LLM API Key（OpenAI / DeepSeek / 智谱等均可）

### Windows 用户（推荐）

1. 下载 Release 中的 `ai-team-v1.0.zip`，解压
2. 双击 `start.bat`，首次运行会自动提示配置 API Key
3. 填好 Key 后再次双击，浏览器自动打开看板

### macOS / Linux 用户

```bash
# 1. 克隆仓库
git clone https://github.com/nianjiang888/ai-team.git
cd ai-team

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Key
cp config.free.yaml config.local.yaml
# 编辑 config.local.yaml，填入你的 API Key

# 4. 一键启动
python start.py
```

启动后浏览器会自动打开看板：http://localhost:5678

## 配置说明

编辑 `config.local.yaml`：

```yaml
llm:
  provider: "openai"           # openai / claude / deepseek / zhipu
  api_key: "your-api-key"      # 你的API Key
  model: "gpt-4o-mini"         # 模型名

agents:
  copywriter:
    enabled: true               # 免费版默认只开文案助理
  social_media:
    enabled: false              # 专业版解锁
  analyst:
    enabled: false              # 专业版解锁
  project_manager:
    enabled: false              # 专业版解锁
  consultant:
    enabled: false              # 专业版解锁
```

支持多种 LLM：OpenAI、Claude、DeepSeek、智谱、或任何兼容 OpenAI 接口的模型。

## 目录结构

```
ai-team/
├── start.bat             # Windows一键启动
├── start.py              # Python启动脚本
├── config.yaml           # 完整配置模板
├── config.free.yaml      # 免费版配置
├── requirements.txt      # Python依赖
├── agents/               # AI员工定义
├── prompts/              # Prompt模板库（58个）
│   ├── copywriter/       # 文案类（10个）
│   ├── social_media/     # 运营类（14个）
│   ├── analyst/          # 分析类（14个）
│   ├── project_manager/  # 管理类（10个）
│   └── consultant/       # 商业类（10个）
├── workflows/            # 自动化工作流
├── dashboard/            # 看板（前端+Flask后端）
├── outputs/              # 输出文件
└── docs/                 # 使用文档
```

## 如何升级到专业版

免费版体验满意后，解锁全部5个AI员工：

1. 将 `config.yaml`（完整配置）复制为 `config.local.yaml`
2. 填入你的 API Key
3. 将其他4个员工的 `enabled` 改为 `true`
4. 重启即可

## 许可证

MIT License

---

**一人公司AI团队** — 一个人，一个团队，无限可能。
