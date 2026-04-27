"""
商业顾问工作流 — 需求诊断→方案生成→执行计划
T10: workflows/consultant_workflow.py

完整链路：
1. 问卷式引导用户描述需求
2. 自动匹配分析维度
3. 生成结构化方案文档（BP/竞品报告/市场调研）
4. 生成30天冷启动执行计划
5. 方案评分和风险提示
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
CONTENT_DIR = os.path.join(OUTPUTS_DIR, "content")
REVIEWS_DIR = os.path.join(OUTPUTS_DIR, "reviews")


# =============================================
# T10-1: 需求收集
# =============================================

NEEDS_QUESTIONS = [
    {
        "id": "industry",
        "question": "你所在的行业是什么？",
        "type": "text",
        "example": "AI效率工具 / 新媒体 / 电商 / 教育",
    },
    {
        "id": "stage",
        "question": "你的项目目前处于哪个阶段？",
        "type": "select",
        "options": ["想法阶段", "验证阶段", "MVP开发中", "已上线运营", "寻求融资"],
    },
    {
        "id": "goal",
        "question": "你最想解决的核心问题是什么？",
        "type": "text",
        "example": "如何获取第一批用户 / 如何提高付费转化 / 如何做竞品差异化",
    },
    {
        "id": "budget",
        "question": "目前的预算情况？",
        "type": "select",
        "options": ["零成本启动", "1万以内", "1-5万", "5-20万", "20万以上"],
    },
    {
        "id": "resources",
        "question": "你目前有哪些资源？",
        "type": "text",
        "example": "1人团队 + AI工具 / 已有种子用户200人 / 有技术背景",
    },
    {
        "id": "timeline",
        "question": "期望什么时候看到成果？",
        "type": "select",
        "options": ["1个月内", "3个月内", "半年内", "1年内", "没有明确时间线"],
    },
]


def get_needs_questions() -> list:
    """获取需求收集问卷"""
    return NEEDS_QUESTIONS


def parse_needs_input(user_input: str) -> dict:
    """
    从用户的自由输入中提取需求信息。
    
    Args:
        user_input: 用户描述的需求（可以是结构化的也可以是自由文本）
        
    Returns:
        dict: 提取的需求信息
    """
    needs = {
        "industry": "",
        "stage": "",
        "goal": "",
        "budget": "",
        "resources": "",
        "timeline": "",
        "raw_input": user_input,
    }
    
    # 尝试从自由文本中提取
    stage_keywords = {
        "想法阶段": ["想法", "构思", "想做", "计划", "打算"],
        "验证阶段": ["验证", "调研", "测试", "探索"],
        "MVP开发中": ["开发", "MVP", "做产品", "写代码"],
        "已上线运营": ["运营", "上线", "已发布", "有用户"],
        "寻求融资": ["融资", "投资", "BP", "路演"],
    }
    
    budget_keywords = {
        "零成本启动": ["零成本", "没钱", "免费", "不花钱"],
        "1万以内": ["几千", "1万", "预算有限"],
        "1-5万": ["几万", "3万", "5万"],
        "5-20万": ["10万", "十几万"],
        "20万以上": ["50万", "百万"],
    }
    
    for stage, keywords in stage_keywords.items():
        if any(kw in user_input for kw in keywords):
            needs["stage"] = stage
            break
    
    for budget, keywords in budget_keywords.items():
        if any(kw in user_input for kw in keywords):
            needs["budget"] = budget
            break
    
    # 尝试JSON解析
    try:
        data = json.loads(user_input)
        for key in needs:
            if key in data:
                needs[key] = data[key]
    except (json.JSONDecodeError, TypeError):
        pass
    
    return needs


# =============================================
# T10-2: 分析维度匹配
# =============================================

ANALYSIS_DIMENSIONS = {
    "competitive": {
        "name": "竞品分析",
        "description": "分析竞争对手的产品、定价、差异化策略",
        "triggers": ["竞品", "竞争对手", "市场", "差异化", "竞争"],
        "weight": 0.3,
    },
    "market": {
        "name": "市场调研",
        "description": "市场规模、用户画像、增长趋势",
        "triggers": ["市场", "用户", "需求", "规模", "调研"],
        "weight": 0.25,
    },
    "financial": {
        "name": "财务模型",
        "description": "收入预测、成本结构、盈亏平衡点",
        "triggers": ["收入", "成本", "利润", "财务", "预算", "变现"],
        "weight": 0.2,
    },
    "brand": {
        "name": "品牌定位",
        "description": "品牌故事、Slogan、传播策略",
        "triggers": ["品牌", "定位", "传播", "营销", "推广"],
        "weight": 0.15,
    },
    "operations": {
        "name": "运营策略",
        "description": "获客渠道、用户留存、增长策略",
        "triggers": ["运营", "获客", "增长", "渠道", "推广"],
        "weight": 0.1,
    },
}


def match_dimensions(needs: dict) -> list:
    """
    根据用户需求匹配分析维度。
    
    Returns:
        list[dict]: 按权重排序的分析维度列表
    """
    text = needs.get("raw_input", "") + " " + needs.get("goal", "")
    
    scored = []
    for dim_id, dim in ANALYSIS_DIMENSIONS.items():
        score = 0
        for trigger in dim["triggers"]:
            if trigger in text:
                score += 2
        scored.append({
            "id": dim_id,
            "name": dim["name"],
            "description": dim["description"],
            "score": score + dim["weight"] * 10,  # 基础分 + 触发分
            "weight": dim["weight"],
        })
    
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


# =============================================
# T10-3: 方案文档生成
# =============================================

SOLUTION_TEMPLATES = {
    "bp": """你是一个商业顾问。请根据以下信息生成一份商业计划书（BP）。

【项目信息】
- 行业: {industry}
- 阶段: {stage}
- 目标: {goal}
- 预算: {budget}
- 资源: {resources}

【输出格式（10章）】
一、执行摘要（200字以内，3分钟看懂）
二、问题与机会（用户痛点 + 市场机会）
三、解决方案（产品/服务描述）
四、市场分析（TAM/SAM/SOM + 增长趋势）
五、商业模式（收入来源 + 定价策略）
六、财务预测（12个月收入/成本预测表）
七、竞品分析（对比矩阵 + 差异化策略）
八、运营策略（获客 + 留存 + 增长）
九、里程碑（按月的关键目标）
十、团队与需求""",

    "competitor": """你是一个商业顾问。请根据以下信息生成一份竞品分析报告。

【项目信息】
- 我的业务: {business_desc}
- 行业: {industry}
- 已知竞品: {known_competitors}

【输出格式（5章）】
一、竞品全景图（直接竞品 + 间接竞品 + 潜在进入者）
二、对比分析矩阵（9维度打分）
三、逐个竞品详细分析（定位/定价/优势/劣势/用户评价）
四、差异化策略建议（市场空白点 + 我们的定位）
五、风险提示""",

    "market_research": """你是一个商业顾问。请根据以下信息生成一份市场调研报告。

【项目信息】
- 行业: {industry}
- 关注点: {focus}

【输出格式（5章）】
一、行业概况（市场规模、增速、格局）
二、用户画像（目标用户特征、需求、行为习惯）
三、趋势分析（3-5个关键趋势）
四、机会窗口（市场空白 + 进入时机）
五、行动建议（3-5条具体建议）""",
}


def generate_solution(
    needs: dict,
    dimensions: list,
    solution_type: str = "bp",
    llm_client=None,
) -> dict:
    """
    生成方案文档。
    
    Args:
        needs: 用户需求
        dimensions: 分析维度
        solution_type: 方案类型 (bp/competitor/market_research)
        llm_client: LLM客户端
        
    Returns:
        dict: 方案结果
    """
    template = SOLUTION_TEMPLATES.get(solution_type, SOLUTION_TEMPLATES["bp"])
    
    prompt = template.format(
        industry=needs.get("industry", "未指定"),
        stage=needs.get("stage", "想法阶段"),
        goal=needs.get("goal", "未明确"),
        budget=needs.get("budget", "未指定"),
        resources=needs.get("resources", "未指定"),
        business_desc=needs.get("raw_input", ""),
        known_competitors="用户未提供具体竞品",
        focus=needs.get("goal", ""),
    )
    
    # 追加分析维度
    dim_text = "\n【重点分析维度】\n" + "\n".join(
        f"- {d['name']}: {d.get('description', '')}" for d in dimensions[:3]
    )
    prompt = prompt.replace("【输出", dim_text + "\n\n【输出")
    
    solution = ""
    if llm_client:
        try:
            solution = llm_client.chat(prompt)
        except Exception:
            solution = "[LLM生成失败]"
    else:
        solution = f"[需调用LLM生成]\n\n{prompt}"
    
    return {
        "type": solution_type,
        "dimensions": [d["name"] for d in dimensions[:3]],
        "solution": solution,
        "prompt": prompt,
    }


# =============================================
# T10-4: 30天冷启动执行计划
# =============================================

LAUNCH_PLAN_PROMPT = """基于以下方案，生成一份30天冷启动执行计划。

【项目信息】
{needs}

【方案摘要】
{solution_summary}

【输出格式】
# 30天冷启动计划

## 第一周：基础搭建（Day 1-7）
每天1-2个具体任务，包含：
- [ ] Day X: 任务描述（预估X小时）
  → 交付物: XXX

## 第二周：内容+种子用户（Day 8-14）
...

## 第三周：渠道拓展（Day 15-21）
...

## 第四周：数据复盘+优化（Day 22-30）
...

【要求】
1. 每天任务具体可执行，不要写"研究""思考"这种模糊动词
2. 标注交付物（具体到文件名或产出形式）
3. 标注关键里程碑
4. 如果预算有限，标注哪些任务零成本"""


def generate_launch_plan(needs: dict, solution: str, llm_client=None) -> str:
    """生成30天冷启动计划"""
    prompt = LAUNCH_PLAN_PROMPT.format(
        needs=json.dumps(needs, ensure_ascii=False, indent=2),
        solution_summary=solution[:1000] if len(solution) > 1000 else solution,
    )
    
    if llm_client:
        try:
            return llm_client.chat(prompt)
        except Exception:
            pass
    
    return f"[需调用LLM生成]\n\n{prompt}"


# =============================================
# T10-5: 方案评分和风险提示
# =============================================

def score_solution(needs: dict) -> dict:
    """
    对方案可行性进行评分（基于规则，不依赖LLM）。
    
    Returns:
        dict: 评分结果
    """
    scores = {}
    total = 0
    
    # 1. 市场清晰度
    if needs.get("industry"):
        scores["市场清晰度"] = 20
    else:
        scores["市场清晰度"] = 5
    total += scores["市场清晰度"]
    
    # 2. 目标明确度
    goal = needs.get("goal", "")
    if len(goal) > 10:
        scores["目标明确度"] = 20
    elif len(goal) > 0:
        scores["目标明确度"] = 10
    else:
        scores["目标明确度"] = 5
    total += scores["目标明确度"]
    
    # 3. 资源匹配度
    resources = needs.get("resources", "")
    if resources and len(resources) > 5:
        scores["资源匹配度"] = 20
    else:
        scores["资源匹配度"] = 10
    total += scores["资源匹配度"]
    
    # 4. 时间合理性
    timeline = needs.get("timeline", "")
    if "1个月" in timeline:
        scores["时间合理性"] = 10  # 太短
    elif "3个月" in timeline or "半年" in timeline:
        scores["时间合理性"] = 20
    else:
        scores["时间合理性"] = 15
    total += scores["时间合理性"]
    
    # 5. 预算匹配度
    budget = needs.get("budget", "")
    if "零成本" in budget:
        scores["预算可行性"] = 15  # 零成本可行但受限
    elif "1万" in budget or "5万" in budget:
        scores["预算可行性"] = 20
    else:
        scores["预算可行性"] = 10
    total += scores["预算可行性"]
    
    return {
        "total": total,
        "max": 100,
        "percentage": total,
        "details": scores,
        "level": "优秀" if total >= 80 else "良好" if total >= 60 else "需要补充信息",
    }


def generate_risks(needs: dict) -> list:
    """生成风险提示"""
    risks = []
    
    if not needs.get("industry"):
        risks.append({
            "level": "high",
            "risk": "行业不明确",
            "suggestion": "建议先做1天行业调研，确定目标市场",
        })
    
    if not needs.get("goal"):
        risks.append({
            "level": "high",
            "risk": "目标不清晰",
            "suggestion": "建议用一句话描述你想在3个月内达成什么",
        })
    
    if "零成本" in needs.get("budget", ""):
        risks.append({
            "level": "medium",
            "risk": "零成本启动资源有限",
            "suggestion": "优先利用免费渠道（小红书/知乎/社群），避免付费投放",
        })
    
    if "1个月" in needs.get("timeline", ""):
        risks.append({
            "level": "medium",
            "risk": "时间线过于激进",
            "suggestion": "建议预留2周缓冲期，MVP先上线再迭代",
        })
    
    return risks


# =============================================
# 完整工作流
# =============================================

def run_full_workflow(
    user_input: str,
    solution_type: str = "bp",
    llm_client=None,
) -> dict:
    """执行完整的商业顾问工作流"""
    result = {
        "workflow": "consultant",
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    
    # Step 1: 解析需求
    print("Step 1/5: 解析用户需求...")
    needs = parse_needs_input(user_input)
    print(f"  行业: {needs.get('industry', '未指定')}")
    print(f"  阶段: {needs.get('stage', '未指定')}")
    print(f"  目标: {needs.get('goal', '未指定')}")
    
    # Step 2: 匹配分析维度
    print("\nStep 2/5: 匹配分析维度...")
    dimensions = match_dimensions(needs)
    print(f"  推荐: {', '.join(d['name'] for d in dimensions[:3])}")
    
    # Step 3: 生成方案
    print("\nStep 3/5: 生成方案文档...")
    solution = generate_solution(needs, dimensions, solution_type, llm_client)
    print(f"  类型: {solution_type}, 长度: {len(solution['solution'])}字")
    
    # Step 4: 冷启动计划
    print("\nStep 4/5: 生成30天冷启动计划...")
    launch_plan = generate_launch_plan(needs, solution["solution"], llm_client)
    print(f"  计划长度: {len(launch_plan)}字")
    
    # Step 5: 评分和风险
    print("\nStep 5/5: 方案评分和风险提示...")
    score = score_solution(needs)
    risks = generate_risks(needs)
    print(f"  评分: {score['total']}/100 ({score['level']})")
    if risks:
        print(f"  风险: {len(risks)}个")
        for r in risks:
            print(f"    [{r['level']}] {r['risk']}")
    
    # 保存结果（使用 output_utils 统一格式）
    from workflows.output_utils import (
        build_filename, build_markdown_doc,
        create_review, save_review,
    )

    os.makedirs(CONTENT_DIR, exist_ok=True)
    os.makedirs(REVIEWS_DIR, exist_ok=True)

    # 构建正文
    body = ""
    if risks:
        body += "## 风险提示\n\n"
        for r in risks:
            icon = "🔴" if r["level"] == "high" else "🟡"
            body += f"{icon} {r['risk']}: {r['suggestion']}\n"
        body += "\n---\n\n"

    body += solution["solution"]
    body += "\n\n---\n\n"
    body += "## 30天冷启动计划\n\n"
    body += launch_plan

    quality_info = {
        "score": score["total"],
        "issues": [r["risk"] for r in risks if r["level"] == "high"],
        "suggestions": [r["suggestion"] for r in risks],
    }

    filename = build_filename("consultant", solution_type)
    output_file = os.path.join(CONTENT_DIR, filename)

    doc = build_markdown_doc(
        employee="consultant",
        task_type=solution_type,
        title=f"商业方案 | {solution_type.upper()}",
        body=body,
        quality_info=quality_info,
        extra_meta={
            "score": score["total"],
            "score_level": score["level"],
            "dimensions": solution["dimensions"],
        },
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(doc)

    # 使用统一审批记录
    review_data = create_review(
        employee="consultant",
        task_type=solution_type,
        title=f"商业方案 - {solution_type}",
        content=body,
        filepath=filename,
    )
    review_data["risks"] = risks
    save_review(review_data, REVIEWS_DIR)
    
    result["score"] = score
    result["risks"] = risks
    result["output_file"] = output_file
    result["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    print(f"\n  方案已保存: {output_file}")
    
    return result
