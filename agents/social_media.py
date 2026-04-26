"""
AI员工：新媒体运营
职责：内容创作、多平台分发、选题策划、直播话术、SEO、数据复盘、运营日历
岗位说明书：prompts/social_media/role-card.md
能力清单：SM-01~SM-14（14个模板）
"""

AGENT_NAME = "social_media"
AGENT_ROLE = "新媒体运营"
AGENT_DESC = "24小时在线，不发朋友圈，不摸鱼"
AGENT_ICON = "📱"
AGENT_ROLE_CARD = "prompts/social_media/role-card.md"

# 能力模块
CAPABILITIES = [
    {"id": "SM-01", "name": "爆款标题生成", "template": "爆款标题制造机"},
    {"id": "SM-02", "name": "一文多平台适配", "template": "一键多平台适配器"},
    {"id": "SM-03", "name": "小红书种草文案", "template": "小红书种草文案生成器"},
    {"id": "SM-04", "name": "短视频脚本", "template": "短视频脚本模板"},
    {"id": "SM-05", "name": "竞品内容拆解", "template": "竞品内容拆解器"},
    {"id": "SM-06", "name": "评论区话术", "template": "评论互动话术库"},
    {"id": "SM-07", "name": "直播间话术", "template": "直播间话术生成器"},
    {"id": "SM-08", "name": "运营数据复盘", "template": "运营数据复盘生成器"},
    {"id": "SM-09", "name": "SEO关键词规划", "template": "SEO关键词自动规划"},
    {"id": "SM-10", "name": "月度内容日历", "template": "月度内容运营日历"},
    {"id": "SM-11", "name": "一文多发", "template": "一文多发（含竞品分析）"},
    {"id": "SM-12", "name": "用户调研问卷", "template": "用户调研问卷设计器"},
    {"id": "SM-13", "name": "直播话术脚本", "template": "直播话术脚本"},
    {"id": "SM-14", "name": "品牌文案", "template": "品牌文案/故事"},
]
