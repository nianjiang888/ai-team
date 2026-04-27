"""
项目管家工作流 — 目标→拆解→分配→追踪→汇报
T09: workflows/project_manager_workflow.py

完整链路：
1. 接收项目目标，AI自动拆解为WBS任务列表
2. 生成里程碑时间表
3. 每日自动汇总进度（读取任务状态文件）
4. 生成项目日报/周报
5. 逾期/风险自动告警
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
CONTENT_DIR = os.path.join(OUTPUTS_DIR, "content")
DAILY_REPORTS_DIR = os.path.join(OUTPUTS_DIR, "daily-reports")
REVIEWS_DIR = os.path.join(OUTPUTS_DIR, "reviews")


# =============================================
# T09-1: 任务拆解（WBS）
# =============================================

WBS_PROMPT = """你是一个资深项目经理。请将以下项目目标拆解为WBS任务列表。

【项目信息】
- 项目名称: {project_name}
- 项目目标: {goal}
- 项目周期: {duration}
- 团队规模: {team_size}

【拆解要求】
1. 拆解为3-5个大阶段，每个阶段包含具体任务
2. 每个任务标注：预估工时、依赖关系、是否可并行
3. 标注关键路径（🔴标记）
4. 标注可自动化的任务（🤖标记）

【输出格式（JSON）】
{{
  "project_name": "...",
  "total_duration": "...",
  "phases": [
    {{
      "id": 1,
      "name": "阶段名称",
      "duration": "1周",
      "tasks": [
        {{
          "id": "1.1",
          "name": "任务名称",
          "hours": 8,
          "depends_on": [],
          "parallel": false,
          "critical": true,
          "automatable": false
        }}
      ]
    }}
  ],
  "milestones": [
    {{"name": "里程碑", "date": "目标日期"}}
  ]
}}"""


def create_wbs(
    project_name: str,
    goal: str,
    duration: str = "4周",
    team_size: str = "1人+AI",
    llm_client=None,
) -> dict:
    """创建WBS任务拆解"""
    prompt = WBS_PROMPT.format(
        project_name=project_name,
        goal=goal,
        duration=duration,
        team_size=team_size,
    )
    
    if llm_client:
        try:
            response = llm_client.chat(prompt)
            wbs = _parse_json(response)
            if wbs:
                return wbs
        except Exception:
            pass
    
    # 无LLM时生成基础结构
    return {
        "project_name": project_name,
        "total_duration": duration,
        "phases": [
            {
                "id": 1,
                "name": "阶段一：规划",
                "duration": duration,
                "tasks": [{
                    "id": "1.1",
                    "name": f"确定{project_name}需求范围",
                    "hours": 4,
                    "depends_on": [],
                    "parallel": False,
                    "critical": True,
                    "automatable": False,
                }],
            }
        ],
        "milestones": [],
        "_prompt": prompt,
    }


def _parse_json(text: str) -> dict:
    import re
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}


# =============================================
# T09-2: 里程碑时间表
# =============================================

def generate_milestones(wbs: dict, start_date: str = None) -> list:
    """根据WBS生成里程碑时间表"""
    if start_date is None:
        start_date = datetime.now().strftime("%Y-%m-%d")
    
    milestones = wbs.get("milestones", [])
    
    # 如果WBS有阶段信息，自动生成里程碑
    phases = wbs.get("phases", [])
    if not milestones and phases:
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        for phase in phases:
            milestones.append({
                "name": f"✅ {phase['name']}完成",
                "date": current_date.strftime("%Y-%m-%d"),
                "phase": phase["id"],
            })
            # 简单推算日期（假设每阶段1-2周）
            days = 7 * len(phase.get("tasks", [{}]))
            current_date += timedelta(days=min(days, 14))
    
    # 补充项目起止里程碑
    if milestones:
        milestones.insert(0, {
            "name": "🚀 项目启动",
            "date": start_date,
            "phase": 0,
        })
        milestones.append({
            "name": "🏁 项目交付",
            "date": milestones[-1]["date"] if len(milestones) > 1 else start_date,
            "phase": 999,
        })
    
    return milestones


# =============================================
# T09-3: 进度汇总
# =============================================

def save_tasks_state(wbs: dict, status_file: str = None) -> str:
    """保存任务状态文件"""
    if status_file is None:
        status_file = os.path.join(OUTPUTS_DIR, "tasks.json")
    
    os.makedirs(os.path.dirname(status_file), exist_ok=True)
    
    # 从WBS展开为扁平任务列表
    tasks = []
    for phase in wbs.get("phases", []):
        for task in phase.get("tasks", []):
            tasks.append({
                "id": task["id"],
                "name": task["name"],
                "phase": phase["name"],
                "phase_id": phase["id"],
                "status": "pending",  # pending / in_progress / done / blocked
                "hours": task.get("hours", 0),
                "critical": task.get("critical", False),
                "automatable": task.get("automatable", False),
                "started_at": None,
                "completed_at": None,
            })
    
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    
    return status_file


def load_tasks_state(status_file: str = None) -> list:
    """加载任务状态"""
    if status_file is None:
        status_file = os.path.join(OUTPUTS_DIR, "tasks.json")
    
    if os.path.exists(status_file):
        with open(status_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def summarize_progress(tasks: list = None) -> dict:
    """汇总项目进度"""
    if tasks is None:
        tasks = load_tasks_state()
    
    if not tasks:
        return {"total": 0, "done": 0, "progress": 0, "status": "empty"}
    
    total = len(tasks)
    done = sum(1 for t in tasks if t["status"] == "done")
    in_progress = sum(1 for t in tasks if t["status"] == "in_progress")
    blocked = sum(1 for t in tasks if t["status"] == "blocked")
    pending = sum(1 for t in tasks if t["status"] == "pending")
    progress = round(done / total * 100, 1) if total > 0 else 0
    
    return {
        "total": total,
        "done": done,
        "in_progress": in_progress,
        "blocked": blocked,
        "pending": pending,
        "progress": progress,
        "status": "on_track" if progress >= 20 else "behind",
    }


# =============================================
# T09-4: 日报/周报生成
# =============================================

DAILY_REPORT_PROMPT = """根据以下任务进度信息，生成今日项目日报。

【项目信息】
项目名称: {project_name}
当前进度: {progress}%

【今日完成】
{completed}

【进行中】
{in_progress}

【被阻塞】
{blocked}

【明日计划】
{tomorrow}

【输出格式】
# 项目日报 | {project_name} | {date}

【今日完成】
（列表格式）

【明日计划】
（基于未完成任务自动推导）

【风险/卡点】
（如有阻塞任务，分析原因和建议）

【整体进度】{progress}%"""


def generate_daily_report(project_name: str = "项目", tasks: list = None, llm_client=None) -> str:
    """生成项目日报"""
    if tasks is None:
        tasks = load_tasks_state()
    
    progress = summarize_progress(tasks)
    
    completed = "\n".join(f"✅ {t['name']}" for t in tasks if t["status"] == "done") or "（无）"
    in_progress = "\n".join(f"🔄 {t['name']}" for t in tasks if t["status"] == "in_progress") or "（无）"
    blocked = "\n".join(f"🚫 {t['name']}" for t in tasks if t["status"] == "blocked") or "（无）"
    tomorrow = "\n".join(f"1. {t['name']}" for t in tasks if t["status"] == "pending")[:200] or "（无）"
    
    prompt = DAILY_REPORT_PROMPT.format(
        project_name=project_name,
        progress=progress["progress"],
        completed=completed,
        in_progress=in_progress,
        blocked=blocked,
        tomorrow=tomorrow,
        date=datetime.now().strftime("%Y-%m-%d"),
    )
    
    if llm_client:
        try:
            return llm_client.chat(prompt)
        except Exception:
            pass
    
    return prompt


def save_daily_report(project_name: str, tasks: list = None, llm_client=None) -> str:
    """保存日报到文件，使用 output_utils 统一格式。"""
    from workflows.output_utils import (
        build_filename, build_markdown_doc,
        create_review, save_review,
    )

    os.makedirs(DAILY_REPORTS_DIR, exist_ok=True)
    os.makedirs(CONTENT_DIR, exist_ok=True)
    os.makedirs(REVIEWS_DIR, exist_ok=True)

    report = generate_daily_report(project_name, tasks, llm_client)

    # 日报同时保存为JSON（数据用）和Markdown（展示用）
    date_str = datetime.now().strftime("%Y-%m-%d")
    json_filepath = os.path.join(DAILY_REPORTS_DIR, f"report_{date_str}.json")

    progress = summarize_progress(tasks).get("progress", 0)
    data = {
        "project": project_name,
        "date": date_str,
        "progress": progress,
        "report": report,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    with open(json_filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 生成Markdown版本
    md_filename = build_filename("pm", "daily_report")
    md_filepath = os.path.join(CONTENT_DIR, md_filename)

    doc = build_markdown_doc(
        employee="pm",
        task_type="daily_report",
        title=f"项目日报 - {project_name}",
        body=report,
        extra_meta={
            "project": project_name,
            "progress": progress,
        },
    )

    with open(md_filepath, "w", encoding="utf-8") as f:
        f.write(doc)

    # 审批记录
    review_data = create_review(
        employee="pm",
        task_type="daily_report",
        title=f"日报 - {project_name}",
        content=report,
        filepath=md_filename,
    )
    save_review(review_data, REVIEWS_DIR)

    return md_filepath


# =============================================
# T09-5: 风险告警
# =============================================

def check_risks(tasks: list = None, wbs: dict = None) -> list:
    """检查项目风险"""
    if tasks is None:
        tasks = load_tasks_state()
    
    risks = []
    
    # 风险1: 关键路径任务被阻塞
    critical_blocked = [t for t in tasks if t.get("critical") and t.get("status") == "blocked"]
    if critical_blocked:
        risks.append({
            "level": "high",
            "type": "关键路径阻塞",
            "tasks": [t["name"] for t in critical_blocked],
            "suggestion": "关键路径任务被阻塞会直接影响交付时间，建议立即协调解决",
        })
    
    # 风险2: 进度落后
    progress = summarize_progress(tasks)
    if progress["progress"] < 15 and progress["total"] > 0:
        risks.append({
            "level": "medium",
            "type": "进度落后",
            "detail": f"当前进度仅{progress['progress']}%",
            "suggestion": "检查任务优先级，聚焦关键路径任务",
        })
    
    # 风险3: 有阻塞任务
    if progress.get("blocked", 0) > 0:
        risks.append({
            "level": "medium",
            "type": "任务阻塞",
            "count": progress.get("blocked", 0),
            "tasks": [t["name"] for t in tasks if t.get("status") == "blocked"],
            "suggestion": "排查阻塞原因，必要时调整依赖关系",
        })
    
    return risks


# =============================================
# 完整工作流
# =============================================

def run_full_workflow(
    project_name: str,
    goal: str,
    duration: str = "4周",
    team_size: str = "1人+AI",
    llm_client=None,
) -> dict:
    """执行完整的项目管家工作流"""
    result = {
        "workflow": "project_manager",
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    
    # Step 1: WBS拆解
    print("Step 1/5: 生成WBS...")
    wbs = create_wbs(project_name, goal, duration, team_size, llm_client)
    phase_count = len(wbs.get("phases", []))
    task_count = sum(len(p.get("tasks", [])) for p in wbs.get("phases", []))
    print(f"  {phase_count}个阶段, {task_count}个任务")
    
    # Step 2: 里程碑
    print("Step 2/5: 生成里程碑...")
    milestones = generate_milestones(wbs)
    print(f"  {len(milestones)}个里程碑")
    
    # Step 3: 保存任务状态
    print("Step 3/5: 初始化任务状态...")
    status_file = save_tasks_state(wbs)
    tasks = load_tasks_state()
    print(f"  {len(tasks)}个任务已初始化: {status_file}")
    
    # Step 4: 日报
    print("Step 4/5: 生成首日日报...")
    report_file = save_daily_report(project_name, tasks, llm_client)
    print(f"  日报: {report_file}")
    
    # Step 5: 风险检查
    print("Step 5/5: 风险检查...")
    risks = check_risks(tasks, wbs)
    if risks:
        print(f"  发现{len(risks)}个风险:")
        for r in risks:
            print(f"    [{r['level']}] {r['type']}: {r.get('suggestion', '')}")
    else:
        print("  未发现风险")
    
    # 保存WBS到文件（使用统一命名）
    from workflows.output_utils import build_filename
    os.makedirs(CONTENT_DIR, exist_ok=True)
    wbs_filename = build_filename("pm", "wbs", ext="json")
    wbs_file = os.path.join(CONTENT_DIR, wbs_filename)
    with open(wbs_file, "w", encoding="utf-8") as f:
        json.dump(wbs, f, ensure_ascii=False, indent=2)
    
    result["wbs_file"] = wbs_file
    result["milestones"] = milestones
    result["task_count"] = len(tasks)
    result["risks"] = risks
    result["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    print(f"\n  WBS已保存: {wbs_file}")
    
    return result
