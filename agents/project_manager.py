"""
AI员工：项目管家
职责：项目规划、任务拆解、日报生成、风险评估、PRD、会议设计、里程碑、复盘、资源分配
岗位说明书：prompts/project_manager/role-card.md
能力清单：PM-01~PM-10（10个模板）
"""

AGENT_NAME = "project_manager"
AGENT_ROLE = "项目管家"
AGENT_DESC = "事无巨细，件件有回音"
AGENT_ICON = "📋"
AGENT_ROLE_CARD = "prompts/project_manager/role-card.md"

# 能力模块
CAPABILITIES = [
    {"id": "PM-01", "name": "项目计划书", "template": "项目计划书一键生成"},
    {"id": "PM-02", "name": "任务拆解（WBS）", "template": "任务拆分生成器"},
    {"id": "PM-03", "name": "项目日报生成", "template": "项目日报自动生成"},
    {"id": "PM-04", "name": "风险评估", "template": "项目风险评估矩阵"},
    {"id": "PM-05", "name": "PRD文档", "template": "PRD文档生成器"},
    {"id": "PM-06", "name": "会议议程设计", "template": "高效会议设计器"},
    {"id": "PM-07", "name": "里程碑规划", "template": "项目里程碑规划器"},
    {"id": "PM-08", "name": "跨部门沟通", "template": "跨部门协作沟通生成器"},
    {"id": "PM-09", "name": "项目复盘", "template": "项目复盘报告生成器"},
    {"id": "PM-10", "name": "资源分配", "template": "项目资源分配规划器"},
]
