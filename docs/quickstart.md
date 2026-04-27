# 一人公司AI团队 - 5分钟上手指南

## 第一步：安装

### 环境要求
- Python 3.10 或以上
- 一个LLM API Key（OpenAI / DeepSeek / 智谱 等均可）

### 安装步骤

1. 下载项目到本地：
```bash
git clone https://github.com/nianjiang888/ai-team.git
cd ai-team
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 第二步：配置

1. 复制配置模板：
```bash
cp config.yaml config.local.yaml
```

2. 编辑 `config.local.yaml`，填入你的API Key：
```yaml
llm:
  provider: "deepseek"       # 选你用的模型
  api_key: "sk-xxxxx"        # 填你的Key
  model: "deepseek-chat"     # 模型名称
```

3. （可选）调整员工配置：
```yaml
agents:
  copywriter:
    enabled: true
    style: "professional"     # 写作风格
  social_media:
    enabled: true
    default_platform: "xiaohongshu"  # 默认平台
```

## 第三步：启动

```bash
python start.py
```

看到以下提示后，浏览器会自动打开：
```
🚀 启动看板服务: http://localhost:5678
```

## 第四步：使用

### 派发任务
点击「快速派单」按钮 → 选择员工 → 描述任务 → 立即派发

### 审批产出
AI员工完成任务后，产出自动进入「待审批」列表：
- 点击「通过」→ 内容保存到 `outputs/content/` 目录
- 点击「打回」→ 记录修改意见

### 查看日报
系统自动汇总每日产出，包括：
- 各员工产出统计
- 任务通过率
- 完成详情

## 5个AI员工能做什么？

| 员工 | 标识 | 擅长 |
|------|------|------|
| 文案助理 | CW | 周报、邮件、公文、会议纪要、文案润色 |
| 新媒体运营 | SM | 小红书、抖音、公众号文案、选题策划、热点追踪 |
| 数据分析师 | DA | 数据清洗、趋势分析、报表制作、可视化图表 |
| 项目管家 | PM | 任务拆解、进度追踪、WBS、甘特图、风险预警 |
| 商业顾问 | BC | 商业计划书、竞品分析、副业策划、BP |

## 目录结构

```
ai-team/
├── start.py           # 一键启动
├── config.yaml        # 配置模板（复制为config.local.yaml使用）
├── agents/            # AI员工定义
├── workflows/         # 自动化工作流
├── prompts/           # Prompt模板库
├── dashboard/         # 看板前端
│   ├── index.html     # 主页面
│   ├── app.py         # Flask后端
│   └── static/app.js  # 前端逻辑
├── outputs/           # 产出文件（自动生成）
│   ├── content/       # 通过审批的内容
│   ├── reviews/       # 待审批队列
│   ├── topics/        # 选题推荐
│   └── daily-reports/ # 日报归档
└── docs/              # 文档
```

## 常见问题

**Q: 启动报错 "ModuleNotFoundError: No module named 'flask'"**
A: 运行 `pip install flask pyyaml requests`

**Q: 打开看板后数据为空？**
A: 正常，首次启动没有历史数据。派发几个任务后就会有数据。

**Q: 如何更换模型？**
A: 编辑 `config.local.yaml`，修改 `llm` 部分的 provider/model/api_key。

**Q: 端口被占用？**
A: 修改配置 `dashboard.port` 为其他端口（如 8888）。

**Q: 如何备份数据？**
A: `outputs/` 目录就是所有数据，直接复制即可。
