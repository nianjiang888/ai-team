"""
AI员工：商业顾问
职责：商业计划书、竞品分析、市场调研、融资路演、财务预测、品牌定位、商业模式画布、副业评估
岗位说明书：prompts/consultant/role-card.md
能力清单：BC-01~BC-10（10个模板）
"""

AGENT_NAME = "consultant"
AGENT_ROLE = "商业顾问"
AGENT_DESC = "帮你赚钱、帮你决策、帮你避坑"
AGENT_ICON = "💡"
AGENT_ROLE_CARD = "prompts/consultant/role-card.md"

# 能力模块
CAPABILITIES = [
    {"id": "BC-01", "name": "商业计划书（BP）", "template": "商业计划书生成器"},
    {"id": "BC-02", "name": "竞品深度分析", "template": "竞品深度分析报告"},
    {"id": "BC-03", "name": "市场快速调研", "template": "市场快速调研报告"},
    {"id": "BC-04", "name": "融资Pitch Deck", "template": "融资路演PPT生成器"},
    {"id": "BC-05", "name": "财务预测建模", "template": "财务预测快速建模"},
    {"id": "BC-06", "name": "品牌定位分析", "template": "品牌定位分析器"},
    {"id": "BC-07", "name": "商业模式画布", "template": "商业模式画布生成器"},
    {"id": "BC-08", "name": "副业项目评估", "template": "副业项目快速评估器"},
    {"id": "BC-09", "name": "用户访谈问卷", "template": "用户调研问卷设计器"},
    {"id": "BC-10", "name": "投资Pitch Deck", "template": "融资Pitch Deck"},
]
