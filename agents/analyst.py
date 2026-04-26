"""
AI员工：数据分析师
职责：数据清洗、图表推荐、SQL生成、Python脚本、趋势分析、看板设计、A/B测试、用户画像
岗位说明书：prompts/analyst/role-card.md
能力清单：DA-01~DA-14（14个模板）
"""

AGENT_NAME = "analyst"
AGENT_ROLE = "数据分析师"
AGENT_DESC = "数字不会说谎，但需要人来翻译"
AGENT_ICON = "📊"
AGENT_ROLE_CARD = "prompts/analyst/role-card.md"

# 能力模块
CAPABILITIES = [
    {"id": "DA-01", "name": "Excel数据清洗", "template": "Excel数据清洗助手"},
    {"id": "DA-02", "name": "图表类型推荐", "template": "数据可视化图表推荐器"},
    {"id": "DA-03", "name": "SQL语句生成", "template": "SQL语句生成器"},
    {"id": "DA-04", "name": "Python分析脚本", "template": "Python数据分析脚本生成器"},
    {"id": "DA-05", "name": "数据趋势分析", "template": "数据趋势分析报告生成器"},
    {"id": "DA-06", "name": "数据看板设计", "template": "数据看板设计方案"},
    {"id": "DA-07", "name": "A/B测试方案", "template": "A/B测试方案生成器"},
    {"id": "DA-08", "name": "用户画像分析", "template": "用户画像自动生成器"},
    {"id": "DA-09", "name": "日报/周报数据汇总", "template": "数据汇报自动汇总"},
    {"id": "DA-10", "name": "数据需求文档", "template": "数据需求文档（DRD）生成器"},
    {"id": "DA-11", "name": "Excel公式生成", "template": "Excel公式生成器"},
    {"id": "DA-12", "name": "数据可视化看板", "template": "数据可视化看板"},
    {"id": "DA-13", "name": "日报数据汇总", "template": "日报/周报数据汇总"},
    {"id": "DA-14", "name": "数据需求文档", "template": "数据需求文档"},
]
