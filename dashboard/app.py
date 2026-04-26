"""
一人公司AI团队 - 看板Flask应用
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")


def create_app(config=None):
    app = Flask(__name__,
                template_folder=".",
                static_folder="static")

    # ---- 页面路由 ----

    @app.route("/")
    def index():
        return render_template("index.html")

    # ---- API: 获取AI员工状态 ----

    @app.route("/api/agents")
    def get_agents():
        agents_config = {}
        if config and "agents" in config:
            for name, cfg in config["agents"].items():
                agents_config[name] = {
                    "enabled": cfg.get("enabled", False),
                    "status": "idle",  # idle / working / offline
                }
        return jsonify(agents_config)

    # ---- API: 获取任务列表 ----

    @app.route("/api/tasks")
    def get_tasks():
        tasks_file = os.path.join(OUTPUTS_DIR, "tasks.json")
        if os.path.exists(tasks_file):
            with open(tasks_file, "r", encoding="utf-8") as f:
                return jsonify(json.load(f))
        return jsonify([])

    # ---- API: 派发任务 ----

    @app.route("/api/tasks", methods=["POST"])
    def create_task():
        data = request.get_json()
        tasks_file = os.path.join(OUTPUTS_DIR, "tasks.json")

        # 读取现有任务
        tasks = []
        if os.path.exists(tasks_file):
            with open(tasks_file, "r", encoding="utf-8") as f:
                tasks = json.load(f)

        # 新任务
        task = {
            "id": len(tasks) + 1,
            "agent": data.get("agent", "copywriter"),
            "type": data.get("type", "文案撰写"),
            "input": data.get("input", ""),
            "status": "pending",  # pending / working / review / done
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "output": "",
        }
        tasks.append(task)

        with open(tasks_file, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)

        return jsonify(task)

    # ---- API: 获取日报 ----

    @app.route("/api/reports")
    def get_reports():
        reports_dir = os.path.join(OUTPUTS_DIR, "daily-reports")
        if not os.path.exists(reports_dir):
            return jsonify([])
        reports = []
        for fname in sorted(os.listdir(reports_dir), reverse=True):
            if fname.endswith(".json"):
                fpath = os.path.join(reports_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    reports.append(json.load(f))
        return jsonify(reports[:7])  # 最近7天

    # ---- API: 待审批列表 ----

    @app.route("/api/reviews")
    def get_reviews():
        reviews_dir = os.path.join(OUTPUTS_DIR, "reviews")
        if not os.path.exists(reviews_dir):
            return jsonify([])
        reviews = []
        for fname in sorted(os.listdir(reviews_dir)):
            if fname.endswith(".json"):
                fpath = os.path.join(reviews_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    item = json.load(f)
                    if item.get("status") == "pending":
                        reviews.append(item)
        return jsonify(reviews)

    # ---- API: 审批操作 ----

    @app.route("/api/reviews/<item_id>", methods=["POST"])
    def review_action(item_id):
        action = request.json.get("action")  # approve / reject
        reviews_dir = os.path.join(OUTPUTS_DIR, "reviews")
        fpath = os.path.join(reviews_dir, f"{item_id}.json")
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                item = json.load(f)
            item["status"] = "approved" if action == "approve" else "rejected"
            item["reviewed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(item, f, ensure_ascii=False, indent=2)
            return jsonify({"ok": True})
        return jsonify({"ok": False}), 404

    # ---- API: 系统状态 ----

    @app.route("/api/status")
    def system_status():
        return jsonify({
            "version": "1.0.0",
            "uptime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "agents_count": len(config.get("agents", {})) if config else 0,
        })

    return app
