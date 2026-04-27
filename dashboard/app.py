"""
一人公司AI团队 - 看板Flask应用 (v2)
T13+T14: 重构API层，从outputs目录读取真实数据

API列表:
  GET  /api/agents              → 5个AI员工状态（从配置+outputs统计数据）
  GET  /api/stats               → 统计卡片数据（总任务/已完成/进行中/待审批）
  GET  /api/tasks               → 任务列表（从reviews和content目录聚合）
  POST /api/tasks               → 派发新任务
  POST /api/tasks/<id>/execute  → 执行任务（调用工作流）
  GET  /api/reviews             → 待审批列表
  POST /api/reviews/<id>        → 审批操作（approve/reject）
  GET  /api/reports             → 日报列表
  GET  /api/topics              → 今日选题
  POST /api/topics/generate     → 生成新选题
  GET  /api/timeline            → 协作动态时间线
  GET  /api/status              → 系统状态
"""

import os
import json
import glob
from datetime import datetime, date
from flask import Flask, render_template, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
REVIEWS_DIR = os.path.join(OUTPUTS_DIR, "reviews")
CONTENT_DIR = os.path.join(OUTPUTS_DIR, "content")
TOPICS_DIR = os.path.join(OUTPUTS_DIR, "topics")
REPORTS_DIR = os.path.join(OUTPUTS_DIR, "daily-reports")
TASKS_FILE = os.path.join(OUTPUTS_DIR, "tasks.json")
TIMELINE_FILE = os.path.join(OUTPUTS_DIR, "timeline.json")

# 员工元信息
AGENT_META = {
    "copywriter":      {"name": "文案助理",   "color": "blue",   "desc": "公文 · 周报 · 邮件 · 润色",     "letter": "CW"},
    "social_media":    {"name": "新媒体运营", "color": "pink",   "desc": "小红书 · 抖音 · 公众号 · 热点",   "letter": "SM"},
    "analyst":         {"name": "数据分析师", "color": "cyan",   "desc": "报表 · 图表 · 趋势分析 · 清洗",  "letter": "DA"},
    "project_manager": {"name": "项目管家",   "color": "indigo", "desc": "任务拆解 · 进度追踪 · 日报",      "letter": "PM"},
    "consultant":      {"name": "商业顾问",   "color": "amber",  "desc": "商业计划 · 竞品分析 · BP",        "letter": "BC"},
}


def create_app(config=None):
    app = Flask(__name__,
                template_folder=".",
                static_folder="static")

    # ---- 页面路由 ----
    @app.route("/")
    def index():
        return render_template("index.html")

    # ---- 工具函数 ----

    def _load_json(filepath, default=None):
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return default if default is not None else []

    def _save_json(filepath, data):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _scan_reviews():
        """扫描reviews目录，返回所有review列表"""
        reviews = []
        if not os.path.exists(REVIEWS_DIR):
            return reviews
        for fname in sorted(os.listdir(REVIEWS_DIR)):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(REVIEWS_DIR, fname)
            try:
                item = _load_json(fpath)
                if isinstance(item, dict):
                    reviews.append(item)
            except Exception:
                continue
        return reviews

    def _scan_content():
        """扫描content目录，返回所有产出文件信息"""
        items = []
        if not os.path.exists(CONTENT_DIR):
            return items
        for fname in sorted(os.listdir(CONTENT_DIR)):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(CONTENT_DIR, fname)
            # 解析YAML front matter获取元信息
            info = {"filename": fname, "path": fpath}
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read(500)
                if content.startswith("---"):
                    end = content.find("---", 3)
                    if end > 0:
                        yaml_str = content[3:end].strip()
                        for line in yaml_str.split("\n"):
                            if ":" in line:
                                k, v = line.split(":", 1)
                                k = k.strip()
                                v = v.strip().strip('"')
                                if k == "title":
                                    info["title"] = v
                                elif k == "employee_key":
                                    info["agent"] = v
                                elif k == "task_type":
                                    info["task_type"] = v
                                elif k == "status":
                                    info["status"] = v
                                elif k == "generated_at":
                                    info["created_at"] = v
            except Exception:
                pass
            items.append(info)
        return items

    def _scan_topics():
        """扫描topics目录"""
        topics = []
        if not os.path.exists(TOPICS_DIR):
            return topics
        for fname in sorted(os.listdir(TOPICS_DIR), reverse=True):
            if fname.endswith(".json"):
                fpath = os.path.join(TOPICS_DIR, fname)
                item = _load_json(fpath)
                if isinstance(item, dict):
                    topics.append(item)
                elif isinstance(item, list):
                    topics.extend(item)
        return topics

    def _add_timeline(entry):
        """追加一条动态到时间线"""
        timeline = _load_json(TIMELINE_FILE, [])
        timeline.insert(0, entry)
        # 只保留最近50条
        timeline = timeline[:50]
        _save_json(TIMELINE_FILE, timeline)

    # ---- API: 统计数据 ----

    @app.route("/api/stats")
    def get_stats():
        reviews = _scan_reviews()
        content = _scan_content()

        # 从reviews统计
        total = len(reviews)
        approved = sum(1 for r in reviews if r.get("status") in ("approved", "done"))
        pending_review = sum(1 for r in reviews if r.get("status") in ("pending_review", "pending", "review"))
        rejected = sum(1 for r in reviews if r.get("status") == "rejected")

        # 从tasks.json也统计
        tasks = _load_json(TASKS_FILE, [])
        if isinstance(tasks, list):
            task_total = len(tasks)
            task_done = sum(1 for t in tasks if t.get("status") == "done")
            task_working = sum(1 for t in tasks if t.get("status") == "working")
            task_pending = sum(1 for t in tasks if t.get("status") in ("pending", "review"))
        else:
            task_total = task_done = task_working = task_pending = 0

        # 合并统计：以reviews为主（实际产出），tasks为辅（工作流任务）
        # 今日数据
        today = date.today().isoformat()
        today_reviews = [r for r in reviews if today in r.get("created_at", "")]
        today_done = sum(1 for r in today_reviews if r.get("status") in ("approved", "done"))
        today_total = len(today_reviews)

        # 各员工统计
        agent_stats = {}
        for key, meta in AGENT_META.items():
            agent_reviews = [r for r in reviews if r.get("employee") == key]
            agent_done = sum(1 for r in agent_reviews if r.get("status") in ("approved", "done"))
            agent_total = len(agent_reviews)
            agent_pending = sum(1 for r in agent_reviews if r.get("status") in ("pending_review", "pending", "review"))
            agent_working = sum(1 for r in agent_reviews if r.get("status") == "rejected")

            # 判断状态：有pending的=工作中，有rejected=需关注，否则=空闲
            if agent_pending > 0:
                status = "working"
            elif agent_working > 0:
                status = "attention"
            else:
                status = "idle"

            agent_stats[key] = {
                "total": agent_total,
                "done": agent_done,
                "pending": agent_pending,
                "rejected": agent_working,
                "status": status,
            }

        return jsonify({
            "total_reviews": total,
            "approved": approved,
            "pending_review": pending_review,
            "rejected": rejected,
            "total_tasks": task_total + total,
            "today_total": today_total,
            "today_done": today_done,
            "agent_stats": agent_stats,
            "content_count": len(content),
        })

    # ---- API: 获取AI员工状态 ----

    @app.route("/api/agents")
    def get_agents():
        result = {}
        for key, meta in AGENT_META.items():
            enabled = True
            if config and "agents" in config:
                agent_cfg = config["agents"].get(key, {})
                enabled = agent_cfg.get("enabled", True)

            result[key] = {
                "name": meta["name"],
                "color": meta["color"],
                "desc": meta["desc"],
                "enabled": enabled,
                "status": "idle",
            }
        return jsonify(result)

    @app.route("/api/agents/status")
    def get_agents_status():
        """返回带统计数据的员工状态"""
        stats_data = get_stats()
        stats_json = json.loads(stats_data.get_data(as_text=True))
        agent_stats = stats_json["agent_stats"]

        result = {}
        for key, meta in AGENT_META.items():
            astat = agent_stats.get(key, {"total": 0, "done": 0, "pending": 0, "rejected": 0, "status": "idle"})
            result[key] = {
                "name": meta["name"],
                "color": meta["color"],
                "desc": meta["desc"],
                "letter": meta["letter"],
                "enabled": config.get("agents", {}).get(key, {}).get("enabled", True) if config else True,
                "status": astat["status"],
                "total": astat["total"],
                "done": astat["done"],
                "pending": astat["pending"],
                "progress": int(astat["done"] / max(astat["total"], 1) * 100),
            }
        return jsonify(result)

    # ---- API: 任务列表 ----

    @app.route("/api/tasks")
    def get_tasks():
        # 聚合reviews + tasks
        reviews = _scan_reviews()
        tasks = _load_json(TASKS_FILE, [])

        # 将reviews转为任务格式
        task_list = []
        for r in reviews:
            status_map = {
                "pending_review": "review",
                "pending": "review",
                "approved": "done",
                "done": "done",
                "rejected": "rejected",
                "revised": "working",
            }
            task_list.append({
                "id": r.get("review_id", r.get("id", "")),
                "agent": r.get("employee", ""),
                "type": r.get("task_type", r.get("doc_type", "")),
                "input": r.get("title", r.get("doc_name", "")),
                "status": status_map.get(r.get("status", ""), "pending"),
                "created_at": r.get("created_at", ""),
                "score": r.get("quality_score"),
            })

        # 从tasks.json补充
        if isinstance(tasks, list):
            for t in tasks:
                if not any(tt["id"] == str(t.get("id", "")) for tt in task_list):
                    task_list.append({
                        "id": str(t.get("id", "")),
                        "agent": t.get("agent", ""),
                        "type": t.get("type", ""),
                        "input": t.get("name", t.get("input", "")),
                        "status": t.get("status", "pending"),
                        "created_at": t.get("started_at", "") or t.get("created_at", ""),
                    })

        # 按时间倒序
        task_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return jsonify(task_list)

    # ---- API: 派发任务 ----

    @app.route("/api/tasks", methods=["POST"])
    def create_task():
        data = request.get_json() or {}
        agent = data.get("agent", "copywriter")
        task_input = data.get("input", "")
        task_type = data.get("type", "general")

        if not task_input:
            return jsonify({"error": "任务描述不能为空"}), 400

        # 创建review记录
        review_id = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{agent}_{task_type}"
        review_data = {
            "review_id": review_id,
            "title": task_input,
            "employee": agent,
            "task_type": task_type,
            "filepath": "",
            "content": "",
            "status": "pending",
            "reviewer": "user",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reviewed_at": None,
            "review_comment": None,
        }

        fpath = os.path.join(REVIEWS_DIR, f"{review_id}.json")
        _save_json(fpath, review_data)

        # 添加时间线
        _add_timeline({
            "type": "task_created",
            "agent": agent,
            "message": f"收到新任务：{task_input}",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        return jsonify(review_data)

    # ---- API: 执行任务 ----

    @app.route("/api/tasks/<task_id>/execute", methods=["POST"])
    def execute_task(task_id):
        """执行任务，调用对应的工作流"""
        # 查找任务
        review = None
        for r in _scan_reviews():
            if r.get("review_id") == task_id or r.get("id") == task_id:
                review = r
                break

        if not review:
            return jsonify({"error": "任务不存在"}), 404

        agent = review.get("employee", "copywriter")
        task_type = review.get("task_type", "general")
        title = review.get("title", "")

        try:
            # 根据员工类型调用工作流
            if agent == "copywriter":
                from workflows.copywriter_workflow import run_workflow
                result = run_workflow(title)
            elif agent == "social_media":
                from workflows.social_media_workflow import generate_content
                result = generate_content(title, task_type)
            elif agent == "analyst":
                from workflows.analyst_workflow import run_workflow
                result = run_workflow(title)
            elif agent == "project_manager":
                from workflows.project_manager_workflow import run_workflow
                result = run_workflow(title)
            elif agent == "consultant":
                from workflows.consultant_workflow import run_workflow
                result = run_workflow(title)
            else:
                return jsonify({"error": f"未知员工: {agent}"}), 400

            # 更新任务状态
            review["status"] = result.get("status", "pending_review")
            if result.get("filepath"):
                review["filepath"] = result["filepath"]
            if result.get("content"):
                review["content"] = result["content"]

            review_id = review.get("review_id", task_id)
            fpath = os.path.join(REVIEWS_DIR, f"{review_id}.json")
            _save_json(fpath, review)

            # 时间线
            _add_timeline({
                "type": "task_completed",
                "agent": agent,
                "message": f"完成任务「{title}」，等待审批",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

            return jsonify({"ok": True, "task": review})

        except ImportError as e:
            return jsonify({"error": f"工作流模块未找到: {e}"}), 500
        except Exception as e:
            return jsonify({"error": f"执行失败: {e}"}), 500

    # ---- API: 审批操作 ----

    @app.route("/api/reviews")
    def get_reviews():
        reviews = _scan_reviews()
        # 只返回待审批的
        pending = [r for r in reviews if r.get("status") in ("pending_review", "pending", "review")]
        return jsonify(pending)

    @app.route("/api/reviews/<review_id>", methods=["POST"])
    def review_action(review_id):
        action = request.json.get("action")  # approve / reject
        comment = request.json.get("comment", "")

        if action not in ("approve", "reject"):
            return jsonify({"error": "action必须是approve或reject"}), 400

        # 查找review文件
        fpath = os.path.join(REVIEWS_DIR, f"{review_id}.json")
        if not os.path.exists(fpath):
            # 尝试遍历查找
            for r in _scan_reviews():
                if r.get("review_id") == review_id or r.get("id") == review_id:
                    fpath = os.path.join(REVIEWS_DIR, f"{r.get('review_id', '')}.json")
                    if not os.path.exists(fpath):
                        fpath = os.path.join(REVIEWS_DIR, f"{r.get('id', '')}.json")
                    break

        if not os.path.exists(fpath):
            return jsonify({"error": "审批记录不存在"}), 404

        review = _load_json(fpath)
        review["status"] = "approved" if action == "approve" else "rejected"
        review["reviewed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        review["review_comment"] = comment
        _save_json(fpath, review)

        # 时间线
        label = "通过" if action == "approve" else "打回"
        _add_timeline({
            "type": "review_" + action,
            "agent": review.get("employee", ""),
            "message": f"「{review.get('title', '')}」已{label}",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        return jsonify({"ok": True, "review": review})

    # ---- API: 日报 ----

    @app.route("/api/reports")
    def get_reports():
        if not os.path.exists(REPORTS_DIR):
            return jsonify([])
        reports = []
        for fname in sorted(os.listdir(REPORTS_DIR), reverse=True):
            if fname.endswith(".json"):
                item = _load_json(os.path.join(REPORTS_DIR, fname))
                if isinstance(item, dict):
                    reports.append(item)
                elif isinstance(item, list):
                    reports.extend(item)
        return jsonify(reports[:7])

    @app.route("/api/report/today")
    def get_today_report():
        today = date.today().isoformat()
        fname = f"report_{today}.json"
        fpath = os.path.join(REPORTS_DIR, fname)
        if os.path.exists(fpath):
            return jsonify(_load_json(fpath))
        return jsonify({"date": today, "empty": True})

    @app.route("/api/report/generate", methods=["POST"])
    def generate_report():
        """手动触发日报生成"""
        try:
            from workflows.report_gen import generate_daily_report
            report = generate_daily_report()
            _add_timeline({
                "type": "task_completed",
                "agent": "project_manager",
                "message": f"日报已生成：{report['summary']['total_reviews']}项产出，通过率{report['summary']['approval_rate']}%",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
            return jsonify({"ok": True, "report": report})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ---- API: 选题 ----

    @app.route("/api/topics")
    def get_topics():
        topics = _scan_topics()
        # 返回最近一组（今天的）
        if topics:
            # 如果是列表套列表，取最后一组
            if isinstance(topics[-1], list):
                return jsonify(topics[-1])
            return jsonify(topics)
        return jsonify([])

    @app.route("/api/topics/generate", methods=["POST"])
    def generate_topics():
        """触发生成新选题"""
        try:
            from workflows.social_media_workflow import generate_topics as gen_topics
            result = gen_topics()
            _add_timeline({
                "type": "topics_generated",
                "agent": "social_media",
                "message": f"生成了{len(result)}个新选题",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
            return jsonify({"ok": True, "topics": result})
        except ImportError:
            return jsonify({"error": "social_media_workflow.generate_topics 未找到"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ---- API: 时间线 ----

    @app.route("/api/timeline")
    def get_timeline():
        timeline = _load_json(TIMELINE_FILE, [])
        return jsonify(timeline[:20])

    # ---- API: 系统状态 ----

    @app.route("/api/status")
    def system_status():
        return jsonify({
            "version": "1.0.0",
            "uptime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "agents_count": len(AGENT_META),
            "outputs_count": len(_scan_reviews()) + len(_scan_content()),
        })

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
