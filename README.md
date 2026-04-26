# 一人公司AI团队

> 5个AI员工，帮你管文案、管数据、管运营、管项目、管生意。

## 这是什么？

把你的AI技能包从"50个独立模板"升级为一套**自动运转的AI团队系统**。每个AI员工有明确的岗位职责、专业的工作流程、可追踪的输出成果。

不是让你学prompt，而是**替你干活**。

## AI员工一览

| 员工 | 职责 | 典型产出 |
|------|------|---------|
| ✍️ 文案助理 | 公文、周报、邮件、文案润色 | 排版好的文档文件 |
| 📱 新媒体运营 | 小红书/抖音/公众号/头条内容 | 选题、文案、发布计划 |
| 📊 数据分析师 | 数据整理、报表、趋势分析 | 图表 + 分析报告 |
| 📋 项目管家 | 任务拆解、进度追踪、汇报 | 甘特图、任务看板 |
| 💡 商业顾问 | 创业规划、副业分析、商业计划 | 商业方案文档 |

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/nianjiang888/ai-team.git
cd ai-team

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置你的API Key
cp config.yaml config.local.yaml
# 编辑 config.local.yaml，填入你的 API Key

# 4. 一键启动
python start.py
```

启动后浏览器会自动打开看板页面：http://localhost:5678

## 目录结构

```
ai-team/
├── start.py              # 一键启动脚本
├── config.yaml           # 默认配置模板
├── requirements.txt      # Python依赖
├── agents/               # AI员工定义（核心逻辑）
│   ├── copywriter.py     # 文案助理
│   ├── social_media.py   # 新媒体运营
│   ├── analyst.py        # 数据分析师
│   ├── project_manager.py# 项目管家
│   └── consultant.py     # 商业顾问
├── prompts/              # Prompt模板库
│   ├── copywriter/       # 文案类prompt
│   ├── social_media/     # 运营类prompt
│   ├── analyst/          # 分析类prompt
│   ├── project_manager/  # 管理类prompt
│   └── consultant/       # 商业类prompt
├── workflows/            # 自动化工作流
├── dashboard/            # 看板前端 + Flask后端
│   ├── app.py            # Flask应用
│   ├── index.html        # 主页面
│   └── static/           # 静态资源
├── outputs/              # 输出文件（.gitignore）
│   ├── daily-reports/    # 日报
│   ├── content/          # 内容产出
│   └── reviews/          # 审批队列
└── docs/                 # 使用文档
    └── quickstart.md     # 快速上手指南
```

## 配置说明

编辑 `config.local.yaml`：

```yaml
llm:
  provider: "openai"           # openai / claude / deepseek / zhipu
  api_key: "your-api-key"      # 你的API Key
  model: "gpt-4o-mini"         # 模型名

agents:
  copywriter:
    enabled: true               # 开关
    style: "professional"       # 写作风格
```

## 许可证

MIT License
