"""
日报自动生成脚本 — T15
每天定时汇总各工作流产出，生成结构化日报。

触发方式：
  1. APScheduler定时（config.yaml中daily_report_time配置）
  2. 手动调用 generate_daily_report()
  3. Flask API: POST /api/report/generate

输出：outputs/daily-reports/YYYY-MM-DD.json + YYYY-MM-DD.md
"""

import os
import json
from datetime import datetime, date, timedelta
from typing import Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
REVIEWS_DIR = os.path.join(OUTPUTS_DIR, "reviews")
CONTENT_DIR = os.path.join(OUTPUTS_DIR, "content")
TOPICS_DIR = os.path.join(OUTPUTS_DIR, "topics")
REPORTS_DIR = os.path.join(OUTPUTS_DIR, "daily-reports")

# 员工映射
EMPLOYEE_MAP = {
    "copywriter": "文案助理",
    "social_media": "新媒体运营",
    "analyst": "数据分析师",
    "project_manager": "项目管家",
    "consultant": "商业顾问",
}


def _load_json(filepath, default=None):
    """安全读取JSON"""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default if default is not None else []


def _scan_directory(dirpath, ext=".json"):
    """扫描目录返回文件列表"""
    if not os.path.exists(dirpath):
        return []
    return [f for f in os.listdir(dirpath) if f.endswith(ext)]


def _today_str():
    return date.today().isoformat()


def generate_daily_report(target_date: Optional[str] = None) -> dict:
    """
    生成指定日期的日报。
    
    Args:
        target_date: 日期字符串 YYYY-MM-DD，默认今天
    
    Returns:
        日报数据字典
    """
    if target_date is None:
        target_date = _today_str()

    # 扫描各目录，筛选目标日期的文件
    review_files = _scan_directory(REVIEWS_DIR)
    content_files = _scan_directory(CONTENT_DIR, ".md")
    topic_files = _scan_directory(TOPICS_DIR)

    # 按员工统计
    agent_summary = {}
    for key, name in EMPLOYEE_MAP.items():
        agent_summary[key] = {
            "name": name,
            "reviews": 0,
            "approved": 0,
            "rejected": 0,
            "pending": 0,
            "content_files": 0,
            "items": [],  # 详细条目
        }

    # 处理reviews
    for fname in review_files:
        fpath = os.path.join(REVIEWS_DIR, fname)
        item = _load_json(fpath)
        if not isinstance(item, dict):
            continue
        
        # 检查日期匹配
        created = item.get("created_at", "")
        if target_date not in created:
            continue

        agent = item.get("employee", "")
        if agent in agent_summary:
            agent_summary[agent]["reviews"] += 1
            status = item.get("status", "")
            if status in ("approved", "done"):
                agent_summary[agent]["approved"] += 1
            elif status == "rejected":
                agent_summary[agent]["rejected"] += 1
            else:
                agent_summary[agent]["pending"] += 1
            
            agent_summary[agent]["items"].append({
                "title": item.get("title", ""),
                "task_type": item.get("task_type", ""),
                "status": status,
                "time": created[-8:] if len(created) > 8 else created,
            })

    # 处理content
    for fname in content_files:
        if target_date not in fname:
            continue
        agent = "copywriter"  # 默认
        for key in EMPLOYEE_MAP:
            if key in fname:
                agent = key
                break
        if agent in agent_summary:
            agent_summary[agent]["content_files"] += 1

    # 汇总统计
    total_reviews = sum(a["reviews"] for a in agent_summary.values())
    total_approved = sum(a["approved"] for a in agent_summary.values())
    total_rejected = sum(a["rejected"] for a in agent_summary.values())
    total_pending = sum(a["pending"] for a in agent_summary.values())
    total_content = sum(a["content_files"] for a in agent_summary.values())

    report = {
        "date": target_date,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_reviews": total_reviews,
            "approved": total_approved,
            "rejected": total_rejected,
            "pending_review": total_pending,
            "total_content": total_content,
            "approval_rate": round(total_approved / max(total_reviews, 1) * 100, 1),
        },
        "agents": agent_summary,
        "highlights": _extract_highlights(agent_summary, target_date),
    }

    # 保存
    _save_report(report)
    return report


def _extract_highlights(agent_summary: dict, target_date: str) -> list:
    """提取今日亮点"""
    highlights = []
    for key, a in agent_summary.items():
        if a["reviews"] > 0:
            if a["approved"] > 0:
                highlights.append({
                    "type": "success",
                    "agent": a["name"],
                    "message": f"{a['name']}完成 {a['approved']} 项任务",
                })
            if a["pending"] > 0:
                highlights.append({
                    "type": "pending",
                    "agent": a["name"],
                    "message": f"{a['name']}有 {a['pending']} 项待审批",
                })
    if not highlights:
        highlights.append({
            "type": "info",
            "agent": "系统",
            "message": "今日暂无工作记录",
        })
    return highlights


def _save_report(report: dict):
    """保存日报（JSON + Markdown双格式）"""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    date_str = report["date"]

    # JSON
    json_path = os.path.join(REPORTS_DIR, f"report_{date_str}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Markdown
    md_path = os.path.join(REPORTS_DIR, f"report_{date_str}.md")
    md_lines = [
        f"# 日报 - {date_str}",
        "",
        f"> 生成时间：{report['generated_at']}",
        "",
        "## 今日概览",
        "",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| 总产出 | {report['summary']['total_reviews']} |",
        f"| 已通过 | {report['summary']['approved']} |",
        f"| 待审批 | {report['summary']['pending_review']} |",
        f"| 已打回 | {report['summary']['rejected']} |",
        f"| 通过率 | {report['summary']['approval_rate']}% |",
        "",
        "## 各员工详情",
        "",
    ]

    for key, a in report["agents"].items():
        md_lines.append(f"### {a['name']}")
        md_lines.append(f"- 产出：{a['reviews']} 项")
        md_lines.append(f"- 通过：{a['approved']} 项")
        md_lines.append(f"- 待审：{a['pending']} 项")
        if a["items"]:
            md_lines.append("")
            md_lines.append("**任务清单：**")
            for item in a["items"]:
                status_label = {"approved": "通过", "done": "完成", "rejected": "打回"}.get(item["status"], item["status"])
                md_lines.append(f"- [{status_label}] {item['title']} ({item['time']})")
        md_lines.append("")

    md_lines.append("---")
    md_lines.append("")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))


def get_latest_reports(days=7) -> list:
    """获取最近N天的日报"""
    reports = []
    for i in range(days):
        d = (date.today() - timedelta(days=i)).isoformat()
        json_path = os.path.join(REPORTS_DIR, f"report_{d}.json")
        report = _load_json(json_path)
        if report:
            reports.append(report)
    return reports


if __name__ == "__main__":
    report = generate_daily_report()
    print(f"日报生成完成：{report['date']}")
    print(f"总产出：{report['summary']['total_reviews']}，通过率：{report['summary']['approval_rate']}%")
