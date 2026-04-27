# 一人公司AI团队 — 20任务流水线（含子任务明细）

> 按依赖关系排列，5个阶段，线性推进。
> 每个任务完成后确认再进下一个。
> 创建日期：2026-04-26

---

## 阶段一：重新包装（T01~T05）

**目标**：不写新代码，把50个模板重新组织为5个AI员工的产品形态。

### ✅ T01 搭建GitHub仓库骨架

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T01-1 创建GitHub仓库 | https://github.com/nianjiang888/ai-team | ✅ |
| T01-2 创建目录结构（agents/ prompts/ workflows/ dashboard/ outputs/ docs/） | 完整目录树 | ✅ |
| T01-3 编写 config.yaml（LLM API、5员工开关、风格偏好、端口） | config.yaml | ✅ |
| T01-4 编写 requirements.txt（Flask、requests、pyyaml、openai） | requirements.txt | ✅ |
| T01-5 编写 start.py（检查环境→装依赖→启动Flask→打开浏览器） | start.py | ✅ |
| T01-6 编写 .gitignore（排除 outputs/、config.local.yaml、__pycache__） | .gitignore | ✅ |
| T01-7 编写 README.md（产品介绍、快速开始、目录说明、配置说明） | README.md | ✅ |
| T01-8 编写 dashboard/app.py（Flask后端，8个API路由） | app.py | ✅ |
| T01-9 编写 dashboard/index.html（看板占位页面） | index.html | ✅ |
| T01-10 编写 agents/*.py（5个员工占位模块） | 5个py文件 | ✅ |
| T01-11 编写 docs/quickstart.md（快速上手指南） | quickstart.md | ✅ |
| T01-12 首次提交推送到GitHub | git commit + push | ✅ |
| T01-BugFix 补充 dashboard/static/ 目录 | 目录修复 | ✅ |

**T01 验证结果**：Flask应用创建成功，8个API路由全部正常，无遗留BUG。

---

### ✅ T02 梳理50+模板，按5个员工角色重新分类

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T02-1 读取ai-efficiency-booster技能包全部模板（SKILL.md + references/） | 模板原始清单 | ✅ |
| T02-2 文案助理归类（CW-01~CW-10，10个模板） | prompts/copywriter/ 映射 | ✅ |
| T02-3 新媒体运营归类（SM-01~SM-14，14个模板） | prompts/social_media/ 映射 | ✅ |
| T02-4 数据分析师归类（DA-01~DA-14，14个模板） | prompts/analyst/ 映射 | ✅ |
| T02-5 项目管家归类（PM-01~PM-10，10个模板） | prompts/project_manager/ 映射 | ✅ |
| T02-6 商业顾问归类（BC-01~BC-10，10个模板） | prompts/consultant/ 映射 | ✅ |
| T02-7 标注跨员工协作模板（竞品分析、数据复盘、日报、用户调研、Excel公式） | 协作关系表 | ✅ |
| T02-8 输出完整映射表 | docs/template-mapping.md | ✅ |

---

### ✅ T03 为5个员工编写岗位说明书

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T03-1 文案助理岗位说明书（人设+10个能力模块+使用场景+不擅长声明+示例输入输出） | prompts/copywriter/role-card.md | ✅ |
| T03-2 新媒体运营岗位说明书（人设+14个能力模块+使用场景+不擅长声明+示例输入输出） | prompts/social_media/role-card.md | ✅ |
| T03-3 数据分析师岗位说明书（人设+14个能力模块+使用场景+不擅长声明+示例输入输出） | prompts/analyst/role-card.md | ✅ |
| T03-4 项目管家岗位说明书（人设+10个能力模块+使用场景+不擅长声明+示例输入输出） | prompts/project_manager/role-card.md | ✅ |
| T03-5 商业顾问岗位说明书（人设+10个能力模块+使用场景+不擅长声明+示例输入输出） | prompts/consultant/role-card.md | ✅ |
| T03-6 更新 agents/*.py 中的员工信息（引用岗位说明书） | agents/copywriter.py 等5个文件 | ✅ |

---

### ✅ T04 每个员工选1-2个模板做明星工作流演示

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T04-1 文案助理演示案例：周报自动生成（输入原始材料→输出排版好的周报） | docs/demos/demo-01-copywriter-weekly-report.md | ✅ |
| T04-2 文案助理演示案例：商务邮件生成（输入场景→输出正式邮件） | docs/demos/demo-02-copywriter-business-email.md | ✅ |
| T04-3 新媒体运营演示案例：小红书种草文案（输入产品→输出完整笔记） | docs/demos/demo-03-social-media-xiaohongshu.md | ✅ |
| T04-4 新媒体运营演示案例：爆款标题生成（输入主题→输出10个标题） | docs/demos/demo-04-social-media-viral-titles.md | ✅ |
| T04-5 数据分析师演示案例：Excel数据清洗（输入脏数据→输出清洗后数据） | docs/demos/demo-05-analyst-data-cleaning.md | ✅ |
| T04-6 数据分析师演示案例：数据趋势分析（输入销售数据→输出趋势报告） | docs/demos/demo-06-analyst-trend-analysis.md | ✅ |
| T04-7 项目管家演示案例：任务拆解WBS（输入项目目标→输出WBS表格） | docs/demos/demo-07-pm-wbs.md | ✅ |
| T04-8 项目管家演示案例：项目日报生成（输入今日工作→输出格式化日报） | docs/demos/demo-08-pm-daily-report.md | ✅ |
| T04-9 商业顾问演示案例：商业计划书（输入创业想法→输出BP大纲） | docs/demos/demo-09-consultant-bp.md | ✅ |
| T04-10 商业顾问演示案例：竞品分析报告（输入行业→输出竞品对比） | docs/demos/demo-10-consultant-competitor.md | ✅ |

---

### ✅ T05 重新设计SkillHub上架页面文案

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T05-1 撰写产品标题和一句话简介（突出"5个AI员工"概念） | docs/skillhub-listing/product-copy.md | ✅ |
| T05-2 撰写产品详细描述（目标用户、核心卖点、使用场景、定价） | docs/skillhub-listing/product-copy.md | ✅ |
| T05-3 设计产品宣传图（1页介绍图，用AI生图） | 待补充（图片服务限流） | ⚠️ |
| T05-4 编写短视频脚本（30~60秒产品介绍） | docs/skillhub-listing/video-script.md | ✅ |
| T05-5 更新SkillHub SKILL.md描述和触发词 | SKILL.md已更新 | ✅ |

---

## 阶段二：工作流化（T06~T12）

**目标**：把独立模板串成5条自动化工作流。

### ✅ T06 新媒体运营工作流：选题→写稿→配图→排版

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T06-1 每日自动抓取热搜/榜单（web_search API） | workflows/social_media_workflow.py → fetch_trending() | ✅ |
| T06-2 LLM分析热搜，生成5个选题建议（Prompt链） | workflows/social_media_workflow.py → generate_topics() | ✅ |
| T06-3 选题格式化输出到看板（写入outputs/topics.json） | workflows/social_media_workflow.py → save_topics() | ✅ |
| T06-4 用户选择选题后调用对应平台文案模板 | workflows/social_media_workflow.py → generate_content() | ✅ |
| T06-5 自动润色去AI腔 | workflows/social_media_workflow.py → refine_content() + quality_check() | ✅ |
| T06-6 输出排版好的文件到outputs/，进入"待审批"状态 | workflows/social_media_workflow.py → save_content() | ✅ |
| T06-7 APScheduler定时任务（每天8:00触发） | workflows/social_media_workflow.py → setup_scheduler() | ✅ |

---

### ✅ T07 文案助理工作流：输入→生成→润色→质检

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T07-1 接收用户输入（文字/文件），识别文档类型 | workflows/copywriter_workflow.py → identify_doc_type() | ✅ |
| T07-2 匹配对应模板（周报/邮件/汇报/翻译等） | workflows/copywriter_workflow.py → get_template_prompt() | ✅ |
| T07-3 调用LLM生成初稿 | workflows/copywriter_workflow.py → generate_draft() | ✅ |
| T07-4 自动润色（去AI腔、口语化、专业度检查） | workflows/copywriter_workflow.py → refine_draft() + professionalism_check() | ✅ |
| T07-5 输出Markdown文件，附带修改说明 | workflows/copywriter_workflow.py → save_draft() | ✅ |

---

### ✅ T08 数据分析师工作流：数据输入→清洗→分析→可视化

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T08-1 接收数据文件（CSV/Excel），自动检测格式和数据质量 | workflows/analyst_workflow.py → detect_file_format() | ✅ |
| T08-2 数据清洗（去重、补缺、格式统一） | workflows/analyst_workflow.py → clean_data_csv() | ✅ |
| T08-3 生成分析报告（趋势/对比/异常检测） | workflows/analyst_workflow.py → generate_analysis_report() | ✅ |
| T08-4 推荐并生成可视化图表 | workflows/analyst_workflow.py → recommend_charts() + generate_chart_code() | ✅ |
| T08-5 输出分析报告（Markdown + 图表文件） | workflows/analyst_workflow.py → save_analysis_report() | ✅ |

---

### ✅ T09 项目管家工作流：目标→拆解→分配→追踪→汇报

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T09-1 接收项目目标，AI自动拆解为WBS任务列表 | workflows/project_manager_workflow.py → create_wbs() | ✅ |
| T09-2 生成甘特图/里程碑时间表 | workflows/project_manager_workflow.py → generate_milestones() | ✅ |
| T09-3 每日自动汇总进度（读取任务状态文件） | workflows/project_manager_workflow.py → summarize_progress() | ✅ |
| T09-4 生成项目日报/周报 | workflows/project_manager_workflow.py → generate_daily_report() | ✅ |
| T09-5 逾期/风险自动告警 | workflows/project_manager_workflow.py → check_risks() | ✅ |

---

### ✅ T10 商业顾问工作流：需求诊断→方案生成→执行计划

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T10-1 问卷式引导用户描述需求 | workflows/consultant_workflow.py → get_needs_questions() + parse_needs_input() | ✅ |
| T10-2 自动匹配分析维度 | workflows/consultant_workflow.py → match_dimensions() | ✅ |
| T10-3 生成结构化方案文档（BP/竞品报告/市场调研） | workflows/consultant_workflow.py → generate_solution() | ✅ |
| T10-4 生成30天冷启动执行计划 | workflows/consultant_workflow.py → generate_launch_plan() | ✅ |
| T10-5 方案评分和风险提示 | workflows/consultant_workflow.py → score_solution() + generate_risks() | ✅ |

---

### ✅ T11 统一每个工作流的结果交付格式

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T11-1 定义统一输出文件命名规范（日期_员工_任务类型.格式） | workflows/output_utils.py → build_filename() | ✅ |
| T11-2 定义统一输出文件结构（YAML front matter + Markdown正文） | workflows/output_utils.py → build_markdown_doc() | ✅ |
| T11-3 定义审批状态流转（draft→pending→approved/rejected→revised） | workflows/output_utils.py → transition_status() + review CRUD | ✅ |
| T11-4 各工作流输出函数统一改造 | 5个工作流save函数全部改用output_utils | ✅ |

---

### ✅ T12 测试所有工作流，修复断点

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T12-1 T06新媒体运营工作流端到端测试 | 6/6 PASS | ✅ |
| T12-2 T07文案助理工作流端到端测试 | 5/5 PASS | ✅ |
| T12-3 T08数据分析师工作流端到端测试 | 4/4 PASS | ✅ |
| T12-4 T09项目管家工作流端到端测试 | 4/4 PASS (修复2个BUG) | ✅ |
| T12-5 T10商业顾问工作流端到端测试 | 4/4 PASS (修复1个BUG) | ✅ |
| T12-6 修复发现的BUG和断点 | 3个BUG已修复 | ✅ |
| T12-7 输出测试报告 | docs/test-report.md + test-report.json | ✅ |

---

## 阶段三：看板与交付体系（T13~T17）

**目标**：开发看板界面，让用户感知"有团队在干活"。

### ✅ T13 开发HTML看板主界面

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T13-1 看板页面框架（顶部导航+主体布局+底部状态栏） | index.html 骨架 | ✅ |
| T13-2 员工状态卡片区域（5个员工+状态指示+快捷操作） | 员工面板组件 | ✅ |
| T13-3 工作台区域（今日任务+选题推荐+快捷派单入口） | 工作台组件 | ✅ |
| T13-4 日报展示区域（今日完成+待审批+风险提示） | 日报组件 | ✅ |
| T13-5 审批面板（待审批列表+通过/打回按钮+修改意见输入） | 审批组件 | ✅ |
| T13-6 CSS样式开发（Tailwind CSS CDN+自定义主题色） | index.html 内联样式 | ✅ |
| T13-7 前端JS交互（API调用+动态渲染+30秒自动刷新） | static/app.js（约400行） | ✅ |
| T13.1 视觉升级：Chart.js动态图表（状态饼图+产出柱状图+完成率图） | 3个图表组件 | ✅ |
| T13.2 视觉升级：去Emoji，改用色块字母标识（CW/SM/DA/PM/BC） | 全局图标替换 | ✅ |

---

### ✅ T14 开发Flask后端API（完整版）

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T14-1 GET /api/agents/status — 返回5个员工状态（在线/忙碌/待命） | API实现 | ✅ |
| T14-2 GET /api/tasks — 返回今日任务列表（含状态筛选） | API实现 | ✅ |
| T14-3 GET /api/stats — 返回统计卡片数据（总产出/通过率/待审批/活跃员工） | API实现 | ✅ |
| T14-4 GET /api/reviews — 返回待审批列表 | API实现 | ✅ |
| T14-5 POST /api/reviews/<id> — 审批操作（approve/reject+意见） | API实现 | ✅ |
| T14-6 GET /api/timeline — 返回协作动态时间线 | API实现 | ✅ |
| T14-7 GET /api/report/today — 返回今日日报 | API实现 | ✅ |
| T14-8 POST /api/report/generate — 手动触发日报生成 | API实现 | ✅ |
| T14-9 GET /api/topics — 返回选题推荐列表 | API实现 | ✅ |

---

### ✅ T15 实现日报自动生成 + 审批机制

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T15-1 日报生成逻辑（扫描outputs目录按日期聚合+任务完成情况） | workflows/report_gen.py | ✅ |
| T15-2 日报输出JSON+Markdown双格式 | outputs/reports/目录 | ✅ |
| T15-3 审批队列数据结构（outputs/reviews/JSON存储审批状态） | 数据结构设计 | ✅ |
| T15-4 审批通过后自动归档到outputs/ + 更新统计和时间线 | 归档逻辑 | ✅ |
| T15-5 打回后附带意见重新进入工作流 | 重做逻辑 | ✅ |
| T15-6 审批机制端到端联调（13条待审批→审批1条→统计实时更新） | 联调通过 | ✅ |

---

### ✅ T16 start.py一键启动 + config.yaml配置模板完善

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T16-1 start.py 一键启动脚本（检查环境→装依赖→启动Flask→打开浏览器） | start.py | ✅ |
| T16-2 config.yaml 增加完整注释（每个字段说明+示例值） | config.yaml | ✅ |
| T16-3 支持config.local.yaml（本地配置覆盖，不提交到git） | 配置加载逻辑 | ✅ |
| T16-4 Python版本检查（≥3.8） | start.py 内置 | ✅ |
| T16-5 自动安装依赖（pip install -r requirements.txt） | start.py 内置 | ✅ |
| T16-6 自动打开浏览器 | start.py 内置 | ✅ |

---

### ✅ T17 编写用户引导文档 + 全流程联调测试

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T17-1 quickstart.md（5分钟上手指南：安装→配置→启动→派第一个任务） | docs/quickstart.md | ✅ |
| T17-2 全流程联调测试（API连通性+数据格式+审批流程+日报生成） | 14/14 PASS | ✅ |
| T17-3 agent-guide.md（5个员工详细使用说明+示例） | 待补充（非阻塞） | ⬜ |
| T17-4 faq.md（常见问题：安装失败/API key配置/工作流报错等） | 待补充（非阻塞） | ⬜ |
| T17-5 changelog.md（版本更新日志） | 待补充（非阻塞） | ⬜ |

---

## 阶段四：商业化推广（T18~T20）

**目标**：推向市场，建立付费模型。

### ⬜ T18 GitHub仓库整理

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T18-1 README.md完善（产品介绍+功能截图+安装说明+使用示例） | README.md | ⬜ |
| T18-2 产品截图（看板界面+日报+审批流程） | screenshots/目录 | ⬜ |
| T18-3 LICENSE文件（MIT或自定义） | LICENSE | ⬜ |
| T18-4 GitHub Topics/Tags设置 | GitHub仓库设置 | ⬜ |
| T18-5 创建Release v1.0 | GitHub Release | ⬜ |

---

### ⬜ T19 SkillHub上架更新版 + 推广内容制作

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T19-1 SkillHub上架免费体验版（1个员工+基础模板） | 上架完成 | ⬜ |
| T19-2 体验帖：从ChatGPT到AI团队，我的效率翻了5倍 | 推广文章1 | ⬜ |
| T19-3 对比帖：50个prompt模板 vs 5个AI员工，差别在哪 | 推广文章2 | ⬜ |
| T19-4 使用案例帖：我用AI员工7天搞定了一人公司全部运营 | 推广文章3 | ⬜ |

---

### ⬜ T20 发布推广内容 + 开设付费社群

| 子任务 | 产出物 | 状态 |
|--------|--------|------|
| T20-1 小红书发布推广内容（至少3条） | 小红书发布 | ⬜ |
| T20-2 今日头条发布推广内容（至少3条） | 今日头条发布 | ⬜ |
| T20-3 选择付费社群平台（知识星球/微信群） | 平台选择 | ⬜ |
| T20-4 创建付费社群（定价+规则+首批内容） | 社群建立 | ⬜ |
| T20-5 收集首批用户反馈，建立反馈跟踪表 | 反馈记录 | ⬜ |

---

## 阶段五：持续迭代（长期）

| 编号 | 任务 | 说明 | 状态 |
|------|------|------|------|
| 持续-1 | 收集用户反馈，制定迭代计划 | 反馈记录 + 迭代roadmap | ⬜ 长期 |
| 持续-2 | 每月新增1-2条工作流 | 按用户需求优先排序 | ⬜ 长期 |
| 持续-3 | 每月直播答疑 + 实操演示 | 建立用户粘性 | ⬜ 长期 |

---

## 当前进度

- ✅ **阶段一**（T01~T05）重新包装 — 全部完成
- ✅ **阶段二**（T06~T12）工作流化 — 全部完成，25/25测试通过，修复3个BUG
- ✅ **阶段三**（T13~T17）看板与交付体系 — 全部完成
  - T13+T14: 前后端联调完成，9个REST API，Chart.js动态图表，色块字母标识
  - T15: 日报自动生成+审批机制端到端联调通过
  - T16: start.py一键启动+config配置完善
  - T17: 全流程联调测试14/14 PASS，quickstart.md用户文档
  - 关键文件：dashboard/app.py(重构), dashboard/static/app.js(新), workflows/report_gen.py(新)
- ⬜ **阶段四**（T18~T20）商业化推广 — **下一步**
- ⬜ **阶段五** 持续迭代 — 长期

---

## 依赖关系图

```
T01 ──→ T02 ──→ T03 ──┬──→ T04 ──→ T05
                        │
                        ├──→ T06 ──┐
                        ├──→ T07 ──┤
                        ├──→ T08 ──┼──→ T11 ──→ T12 ──┬──→ T13 ──→ T14 ──┬──→ T16 ──→ T17 ──→ T18 ──→ T19 ──→ T20
                        ├──→ T09 ──┤                   └──────────────────────→ T15 ──┘
                        └──→ T10 ──┘
```
