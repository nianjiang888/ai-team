"""
统一输出格式工具模块 — T11
所有工作流共用此模块，确保输出一致。

规范：
  文件命名：YYYY-MM-DD_HHMMSS_{employee}_{task_type}.{ext}
  文件结构：头部元信息( YAML front matter ) + 正文( Markdown )
  审批状态：draft → pending_review → approved / rejected → revised → pending_review
"""

import os
import json
from datetime import datetime
from typing import Optional


# =============================================
# T11-1: 统一文件命名规范
# =============================================

# 5个AI员工的英文标识
EMPLOYEE_MAP = {
    "copywriter": "文案助理",
    "social_media": "新媒体运营",
    "analyst": "数据分析师",
    "pm": "项目管家",
    "consultant": "商业顾问",
}

# 各员工对应的任务类型
TASK_TYPES = {
    "copywriter": ["weekly_report", "email", "meeting_minutes", "translation", "presentation", "general"],
    "social_media": ["topics", "xiaohongshu", "douyin", "wechat", "weibo", "viral_titles"],
    "analyst": ["analysis_report", "data_cleaning", "trend", "comparison", "anomaly"],
    "pm": ["wbs", "daily_report", "weekly_report", "milestone", "risk_alert"],
    "consultant": ["bp", "competitor", "market_research", "launch_plan", "needs"],
}


def build_filename(
    employee: str,
    task_type: str,
    ext: str = "md",
    timestamp: Optional[datetime] = None,
) -> str:
    """
    生成统一格式的文件名。
    格式: YYYY-MM-DD_HHMMSS_{employee}_{task_type}.{ext}
    示例: 2026-04-27_083000_copywriter_weekly_report.md
    """
    if timestamp is None:
        timestamp = datetime.now()
    ts = timestamp.strftime("%Y-%m-%d_%H%M%S")
    return f"{ts}_{employee}_{task_type}.{ext}"


# =============================================
# T11-2: 统一文件结构
# =============================================

def build_header(
    employee: str,
    task_type: str,
    title: str,
    extra_meta: Optional[dict] = None,
) -> str:
    """
    生成 YAML front matter 格式的头部元信息。
    所有输出的 Markdown 文件都以 --- 包裹的 YAML 头开始。
    """
    if extra_meta is None:
        extra_meta = {}

    employee_cn = EMPLOYEE_MAP.get(employee, employee)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = ["---"]
    lines.append(f"title: \"{title}\"")
    lines.append(f"employee: \"{employee_cn}\"")
    lines.append(f"employee_key: \"{employee}\"")
    lines.append(f"task_type: \"{task_type}\"")
    lines.append(f"generated_at: \"{ts}\"")
    lines.append(f"status: \"draft\"")

    # 额外元信息
    for k, v in extra_meta.items():
        if isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        elif isinstance(v, list):
            safe = ", ".join(str(x) for x in v)
            lines.append(f"{k}: [{safe}]")
        else:
            lines.append(f'{k}: "{v}"')

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def build_quality_footer(quality_info: dict) -> str:
    """
    生成质量检查脚注。
    quality_info: {"score": 85, "issues": [...], "suggestions": [...]}
    """
    lines = []
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"**质量评分**: {quality_info.get('score', 'N/A')}/100")
    if quality_info.get("issues"):
        lines.append(f"**检测到的问题**: {', '.join(quality_info['issues'])}")
    if quality_info.get("suggestions"):
        lines.append("**优化建议**:")
        for s in quality_info["suggestions"]:
            lines.append(f"- {s}")
    lines.append("")
    return "\n".join(lines)


def build_markdown_doc(
    employee: str,
    task_type: str,
    title: str,
    body: str,
    quality_info: Optional[dict] = None,
    extra_meta: Optional[dict] = None,
) -> str:
    """
    组装完整的 Markdown 文档：头部元信息 + 正文 + 质量脚注。
    """
    header = build_header(employee, task_type, title, extra_meta)
    doc = header + body
    if quality_info:
        doc += build_quality_footer(quality_info)
    return doc


# =============================================
# T11-3: 审批状态流转
# =============================================

STATUS_FLOW = {
    "draft": {"next": ["pending_review"], "label": "草稿"},
    "pending_review": {"next": ["approved", "rejected"], "label": "待审批"},
    "approved": {"next": [], "label": "已通过"},
    "rejected": {"next": ["revised"], "label": "已打回"},
    "revised": {"next": ["pending_review"], "label": "已修改"},
}


def transition_status(current: str, target: str) -> dict:
    """
    检查状态流转是否合法，返回操作结果。
    """
    if current not in STATUS_FLOW:
        return {"ok": False, "error": f"未知状态: {current}"}
    if target not in STATUS_FLOW[current]["next"]:
        return {
            "ok": False,
            "error": f"不允许从 '{STATUS_FLOW[current]['label']}' 转到 '{STATUS_FLOW.get(target, {}).get('label', target)}'",
            "allowed": [STATUS_FLOW[s]["label"] for s in STATUS_FLOW[current]["next"]],
        }
    return {"ok": True, "new_status": target}


def create_review(
    employee: str,
    task_type: str,
    title: str,
    content: str,
    filepath: str,
    reviewer: str = "user",
) -> dict:
    """
    创建审批记录，保存到 outputs/reviews/ 目录。
    返回包含 review_id 的字典。
    """
    review_id = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{employee}_{task_type}"
    review_data = {
        "review_id": review_id,
        "title": title,
        "employee": employee,
        "task_type": task_type,
        "filepath": filepath,
        "content": content,
        "status": "pending_review",
        "reviewer": reviewer,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reviewed_at": None,
        "review_comment": None,
    }
    return review_data


def save_review(review_data: dict, reviews_dir: str) -> str:
    """
    将审批记录保存为 JSON 文件。
    """
    os.makedirs(reviews_dir, exist_ok=True)
    filepath = os.path.join(reviews_dir, f"{review_data['review_id']}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(review_data, f, ensure_ascii=False, indent=2)
    return filepath


def load_review(review_id: str, reviews_dir: str) -> Optional[dict]:
    """
    读取审批记录。
    """
    filepath = os.path.join(reviews_dir, f"{review_id}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def update_review_status(
    review_id: str,
    reviews_dir: str,
    new_status: str,
    comment: Optional[str] = None,
) -> dict:
    """
    更新审批记录的状态。
    """
    review = load_review(review_id, reviews_dir)
    if review is None:
        return {"ok": False, "error": "审批记录不存在"}

    result = transition_status(review["status"], new_status)
    if not result["ok"]:
        return result

    review["status"] = new_status
    review["reviewed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if comment:
        review["review_comment"] = comment

    save_review(review, reviews_dir)
    return {"ok": True, "review": review}
