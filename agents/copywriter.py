"""
AI员工：文案助理
职责：公文写作、周报、邮件、汇报、翻译、审阅、面试、知识库、品牌故事
岗位说明书：prompts/copywriter/role-card.md
能力清单：CW-01~CW-10（10个模板）
"""

AGENT_NAME = "copywriter"
AGENT_ROLE = "文案助理"
AGENT_DESC = "写得好、写得快、不带AI腔"
AGENT_ICON = "✍️"
AGENT_ROLE_CARD = "prompts/copywriter/role-card.md"

# 能力模块
CAPABILITIES = [
    {"id": "CW-01", "name": "周报/日报自动生成", "template": "周报自动生成器"},
    {"id": "CW-02", "name": "会议纪要整理", "template": "会议纪要秒整理"},
    {"id": "CW-03", "name": "商务邮件撰写", "template": "商务邮件万能生成器"},
    {"id": "CW-04", "name": "向上汇报材料", "template": "向上汇报材料生成器"},
    {"id": "CW-05", "name": "合同风险审阅", "template": "合同风险快审"},
    {"id": "CW-06", "name": "行业信息调研", "template": "行业信息快速调研"},
    {"id": "CW-07", "name": "面试准备", "template": "面试模拟器"},
    {"id": "CW-08", "name": "专业文档翻译", "template": "专业文档翻译器"},
    {"id": "CW-09", "name": "知识库整理", "template": "知识库自动整理"},
    {"id": "CW-10", "name": "品牌故事撰写", "template": "品牌故事生成器"},
]
