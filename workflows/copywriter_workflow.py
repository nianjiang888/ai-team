"""
文案助理工作流 — 输入→识别类型→匹配模板→生成初稿→润色→输出
T07: workflows/copywriter_workflow.py

完整链路：
1. 接收用户输入（文字/文件），识别文档类型
2. 匹配对应模板（周报/邮件/汇报/翻译等）
3. 调用LLM生成初稿
4. 自动润色（去AI腔、口语化、专业度检查）
5. 输出Markdown文件，附带修改说明
"""

import os
import json
import re
from datetime import datetime
from typing import Optional


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
CONTENT_DIR = os.path.join(OUTPUTS_DIR, "content")
REVIEWS_DIR = os.path.join(OUTPUTS_DIR, "reviews")


# =============================================
# T07-1: 文档类型识别
# =============================================

DOC_TYPE_PATTERNS = {
    "weekly_report": {
        "name": "周报/日报",
        "keywords": ["周报", "日报", "工作总结", "本周", "今天完成", "这周"],
        "template_id": "CW-01",
    },
    "meeting_notes": {
        "name": "会议纪要",
        "keywords": ["会议", "纪要", "开会", "参会", "议题", "决议", "待办"],
        "template_id": "CW-02",
    },
    "business_email": {
        "name": "商务邮件",
        "keywords": ["邮件", "发邮件", "回复", "收件人", "抄送", "主题", "催", "确认"],
        "template_id": "CW-03",
    },
    "work_report": {
        "name": "工作汇报",
        "keywords": ["汇报", "月报", "季度", "述职", "年终", "工作成果", "KPI"],
        "template_id": "CW-04",
    },
    "contract_review": {
        "name": "合同审阅",
        "keywords": ["合同", "条款", "甲方", "乙方", "违约", "法律"],
        "template_id": "CW-05",
    },
    "industry_research": {
        "name": "行业调研",
        "keywords": ["调研", "行业", "市场", "趋势", "报告", "分析"],
        "template_id": "CW-06",
    },
    "interview_prep": {
        "name": "面试准备",
        "keywords": ["面试", "笔试", "题库", "面试官", "候选人", "HR"],
        "template_id": "CW-07",
    },
    "translation": {
        "name": "文档翻译",
        "keywords": ["翻译", "英文", "中文", "translate", "中英", "英中"],
        "template_id": "CW-08",
    },
    "knowledge_base": {
        "name": "知识库整理",
        "keywords": ["知识库", "归档", "笔记", "整理", "分类", "文档管理"],
        "template_id": "CW-09",
    },
    "brand_story": {
        "name": "品牌故事",
        "keywords": ["品牌", "故事", "品牌文案", "品牌介绍", "slogan"],
        "template_id": "CW-10",
    },
}


def identify_doc_type(user_input: str) -> dict:
    """
    识别用户输入的文档类型。
    
    Args:
        user_input: 用户输入的原始文本
        
    Returns:
        dict: {"type": str, "name": str, "template_id": str, "confidence": float}
    """
    scores = {}
    
    for doc_type, config in DOC_TYPE_PATTERNS.items():
        score = 0
        for keyword in config["keywords"]:
            # 完全匹配
            if keyword in user_input:
                score += 2
            # 模糊匹配（输入包含关键词的部分）
            for word in user_input:
                if keyword in word and len(keyword) >= 2:
                    score += 1
        scores[doc_type] = score
    
    # 找最高分
    if not scores or max(scores.values()) == 0:
        return {
            "type": "general",
            "name": "通用文案",
            "template_id": None,
            "confidence": 0,
        }
    
    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]
    max_possible = len(DOC_TYPE_PATTERNS[best_type]["keywords"]) * 2
    confidence = min(1.0, best_score / max(max_possible, 1))
    
    return {
        "type": best_type,
        "name": DOC_TYPE_PATTERNS[best_type]["name"],
        "template_id": DOC_TYPE_PATTERNS[best_type]["template_id"],
        "confidence": round(confidence, 2),
    }


# =============================================
# T07-2: 模板匹配
# =============================================

TEMPLATE_PROMPTS = {
    "weekly_report": """你是文案助理，负责将用户的工作记录整理成结构化周报。

【用户工作记录】
{input}

【输出格式】
按项目分类，每个项目包含：
- 进度百分比
- 已完成事项（✅）
- 进行中事项（⏳）
- 下周计划（▶）
- 风险提示（⚠️，如有）

格式要求：
- 总字数控制在500字内
- 每个项目2-4个要点
- 不要空话，用数据说话""",

    "meeting_notes": """你是文案助理，负责将会议内容整理成结构化会议纪要。

【会议信息】
{input}

【输出格式】
1. 会议基本信息（时间、参会人、议题）
2. 核心决议（每个决议一句话）
3. 待办事项（责任人+截止时间+内容）
4. 下次会议安排（如有）

格式要求：
- 决议和待办分开列
- 每个待办必须有责任人和时间""",

    "business_email": """你是文案助理，负责撰写商务邮件。

【邮件信息】
{input}

【输出格式】
- 主题行（格式：[公司名] 项目名 — 具体事项）
- 称呼
- 正文（背景→要点→行动呼吁，3段以内）
- 落款

格式要求：
- 正文控制在200字内
- 语气：专业但不生硬
- 必须包含明确的行动呼吁（需要对方做什么）""",

    "work_report": """你是文案助理，负责撰写工作汇报材料。

【工作内容】
{input}

【输出格式】
1. 工作概述（1段，100字）
2. 核心成果（分条列，带数据）
3. 亮点/创新（1-2个）
4. 遇到的困难及解决方案
5. 下阶段计划

格式要求：
- 总字数800-1500字
- 多用数据，少用形容词
- 困难部分不要回避，展现解决问题的能力""",

    "contract_review": """你是文案助理，负责审阅合同/协议并标注风险点。

【合同内容】
{input}

【输出格式】
1. 合同基本信息（双方、标的、金额、期限）
2. 风险点清单（每条含：条款位置、风险描述、严重程度🔴/🟡/🟢、修改建议）
3. 遗漏条款检查（是否缺少必要条款）
4. 总结建议

注意：你提供的是参考意见，不构成法律建议。""",

    "industry_research": """你是文案助理，负责整理行业调研信息。

【调研需求/素材】
{input}

【输出格式】
1. 行业概况（市场规模、增速、格局）
2. 主要趋势（3-5个，每个配数据）
3. 竞争格局（头部玩家+差异化）
4. 机会与风险
5. 建议行动

格式要求：
- 2000字以内
- 每个观点配数据或案例
- 标注信息来源""",

    "interview_prep": """你是文案助理，负责准备面试题库。

【面试信息】
{input}

【输出格式】
1. 岗位分析（核心能力要求）
2. 笔试题（5道，附参考答案）
3. 技术面试题（10道，分基础/进阶/系统设计）
4. 行为面试题（5道，STAR格式）
5. 候选人追问清单

每道题附评分标准和参考答案。""",

    "translation": """你是专业翻译，负责文档翻译。

【翻译任务】
{input}

【要求】
1. 保持原文语气和风格
2. 专业术语统一翻译
3. 不要直译，符合目标语言习惯
4. 长句拆短，提高可读性
5. 数字、日期格式按目标语言规范""",

    "knowledge_base": """你是文案助理，负责整理知识库。

【素材内容】
{input}

【输出格式】
1. 分类结构（3级目录）
2. 每个条目：标题+摘要+标签+关联条目
3. 交叉引用索引
4. 维护建议（哪些需要更新）

格式要求：
- 结构清晰，便于检索
- 摘要控制在50字内
- 标签3-5个/条目""",

    "brand_story": """你是文案助理，负责撰写品牌故事/文案。

【品牌信息】
{input}

【输出格式】
1. 品牌Slogan（3个备选，每个10字内）
2. 品牌故事（500-800字，有人物有情节）
3. 品牌宣言（100字）
4. 品牌关键词（5个）

风格要求：
- 有故事感，不要广告腔
- 传递品牌价值观
- 读者看完能记住一句话""",
}


def get_template_prompt(doc_type: str, user_input: str) -> str:
    """
    根据文档类型获取对应的Prompt模板。
    
    Args:
        doc_type: 文档类型
        user_input: 用户原始输入
        
    Returns:
        str: 完整的Prompt
    """
    template = TEMPLATE_PROMPTS.get(doc_type)
    if template:
        return template.format(input=user_input)
    # 通用模板
    return f"""你是文案助理，请根据以下内容生成一篇专业的文档。

【用户需求】
{user_input}

【要求】
1. 结构清晰，逻辑通顺
2. 语言专业但不生硬
3. 适当使用数据支撑观点
4. 控制在800字以内"""


# =============================================
# T07-3: 调用LLM生成初稿
# =============================================

def generate_draft(
    user_input: str,
    doc_type: dict = None,
    llm_client=None,
) -> dict:
    """
    根据用户输入生成文档初稿。
    
    Args:
        user_input: 用户输入
        doc_type: identify_doc_type() 的结果，None则自动识别
        llm_client: LLM客户端
        
    Returns:
        dict: {"doc_type", "template_id", "draft", "prompt"}
    """
    # Step 1: 识别类型
    if doc_type is None:
        doc_type = identify_doc_type(user_input)
    
    # Step 2: 获取模板
    prompt = get_template_prompt(doc_type["type"], user_input)
    
    # Step 3: 调用LLM
    draft = ""
    if llm_client:
        try:
            draft = llm_client.chat(prompt)
        except Exception:
            draft = "[LLM生成失败]"
    else:
        draft = f"[需调用LLM生成]\n\n以下是Prompt模板，可直接复制使用：\n\n---\n{prompt}\n---"
    
    return {
        "doc_type": doc_type["type"],
        "doc_name": doc_type["name"],
        "template_id": doc_type["template_id"],
        "confidence": doc_type["confidence"],
        "draft": draft,
        "prompt": prompt,
    }


# =============================================
# T07-4: 自动润色
# =============================================

COPYWRITER_REFINE_PROMPT = """你是一个资深文案审稿人。请润色以下文档，遵循以下规则：

【润色规则】
1. 去掉AI腔连接词（"首先""其次""最后""综上所述""总而言之"）
2. 去掉空洞形容词（"令人瞩目的""毋庸置疑的""不可否认的"）
3. 长句拆短（>35字的必须拆）
4. 专业术语保留，但确保前后文有解释
5. 如果是周报/日报：确保每个项目有进度、有数据
6. 如果是邮件：确保有明确的行动呼吁
7. 如果是汇报：确保有数据支撑结论
8. 保持原文结构和字数范围

【原文】
{content}

【输出】
直接输出润色后的全文。如果有重要修改，在末尾用【修改说明】列出改动点。"""


def refine_draft(draft: str, doc_type: str = None, llm_client=None) -> dict:
    """
    润色初稿。
    
    Args:
        draft: 原始草稿
        doc_type: 文档类型（用于针对性润色）
        llm_client: LLM客户端
        
    Returns:
        dict: {"refined": str, "changes": list}
    """
    prompt = COPYWRITER_REFINE_PROMPT.format(content=draft)
    
    if llm_client:
        try:
            refined = llm_client.chat(prompt)
            changes = _extract_changes(refined)
            return {"refined": refined.strip(), "changes": changes}
        except Exception:
            pass
    
    # 无LLM时做基础规则润色
    refined = draft
    changes = []
    
    # 去AI腔
    ai_phrases = ["首先，", "其次，", "最后，", "综上所述，", "总而言之，", "不可否认"]
    for phrase in ai_phrases:
        if phrase in refined:
            refined = refined.replace(phrase, "")
            changes.append(f"删除AI腔词: {phrase.strip('，')}")
    
    return {"refined": refined.strip(), "changes": changes}


def _extract_changes(text: str) -> list:
    """从润色输出中提取修改说明"""
    changes = []
    if "【修改说明】" in text:
        section = text.split("【修改说明】")[1].strip()
        for line in section.split("\n"):
            line = line.strip("-• ").strip()
            if line and len(line) > 2:
                changes.append(line)
    return changes


def professionalism_check(content: str, doc_type: str = None) -> dict:
    """
    专业度检查。
    
    Returns:
        dict: {"score": int, "checks": list}
    """
    checks = []
    score = 100
    
    # 通用检查
    # 1. 数据使用
    has_numbers = bool(re.search(r'\d+', content))
    checks.append({"item": "包含数据/数字", "passed": has_numbers})
    if not has_numbers:
        score -= 10
    
    # 2. 段落结构
    paragraphs = [p for p in content.split("\n\n") if p.strip()]
    checks.append({"item": "分段合理", "passed": 2 <= len(paragraphs) <= 15})
    if not (2 <= len(paragraphs) <= 15):
        score -= 5
    
    # 3. 字数
    char_count = len(content)
    checks.append({"item": f"字数合理({char_count}字)", "passed": 50 <= char_count <= 3000})
    if not (50 <= char_count <= 3000):
        score -= 10
    
    # 4. AI腔检查
    ai_count = sum(1 for kw in ["首先", "其次", "综上所述", "令人瞩目"] if kw in content)
    checks.append({"item": "无AI腔", "passed": ai_count == 0})
    score -= ai_count * 3
    
    # 5. 针对性检查
    if doc_type == "business_email":
        has_cta = any(w in content for w in ["请", "烦请", "望", "期待", "确认", "回复"])
        checks.append({"item": "邮件有行动呼吁", "passed": has_cta})
        if not has_cta:
            score -= 15
    
    elif doc_type == "weekly_report":
        has_progress = any(w in content for w in ["%", "完成", "进度", "✅"])
        checks.append({"item": "周报有进度标识", "passed": has_progress})
        if not has_progress:
            score -= 10
    
    score = max(0, min(100, score))
    
    return {"score": score, "checks": checks, "passed": score >= 70}


# =============================================
# T07-5: 输出文件
# =============================================

def save_draft(
    result: dict,
    refined_result: dict = None,
    auto_save: bool = True,
) -> str:
    """
    输出Markdown文件到 outputs/content/，并创建审批记录。
    使用 output_utils 统一格式。
    """
    from workflows.output_utils import (
        build_filename, build_markdown_doc,
        create_review, save_review,
    )

    os.makedirs(CONTENT_DIR, exist_ok=True)
    os.makedirs(REVIEWS_DIR, exist_ok=True)

    doc_type = result.get("doc_type", "general")

    # 使用润色后的内容，或原始草稿
    content = refined_result["refined"] if refined_result else result["draft"]
    changes = refined_result.get("changes", []) if refined_result else []

    # 专业度检查
    prof = professionalism_check(content, doc_type)
    quality_info = {
        "score": prof["score"],
        "issues": [c["item"] for c in prof["checks"] if not c["passed"]],
        "suggestions": [f"建议改进: {c['item']}" for c in prof["checks"] if not c["passed"]],
    }

    # 如果有修改说明，追加到正文
    body = content
    if changes:
        body += "\n\n---\n\n## 修改说明\n\n"
        for change in changes:
            body += f"- {change}\n"

    # 使用统一命名和结构
    filename = build_filename("copywriter", doc_type)
    filepath = os.path.join(CONTENT_DIR, filename)

    doc = build_markdown_doc(
        employee="copywriter",
        task_type=doc_type,
        title=result.get("doc_name", "文档"),
        body=body,
        quality_info=quality_info,
        extra_meta={
            "template_id": result.get("template_id", "通用"),
            "confidence": result.get("confidence", 0),
        },
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(doc)

    # 使用统一审批记录
    review_data = create_review(
        employee="copywriter",
        task_type=doc_type,
        title=result.get("doc_name", ""),
        content=content,
        filepath=filename,
    )
    review_data["refinement_changes"] = changes
    save_review(review_data, REVIEWS_DIR)

    return filepath


# =============================================
# 完整工作流
# =============================================

def run_full_workflow(
    user_input: str,
    doc_type: str = None,
    auto_refine: bool = True,
    llm_client=None,
) -> dict:
    """
    执行完整的文案助理工作流。
    
    Args:
        user_input: 用户输入（工作记录/邮件信息/会议内容等）
        doc_type: 指定文档类型，None则自动识别
        auto_refine: 是否自动润色
        llm_client: LLM客户端
        
    Returns:
        dict: 工作流结果
    """
    result = {
        "workflow": "copywriter",
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "steps": {},
    }
    
    # Step 1: 识别文档类型
    print("Step 1/5: 识别文档类型...")
    if doc_type:
        type_info = DOC_TYPE_PATTERNS.get(doc_type, {
            "name": "自定义", "template_id": None, "keywords": []
        })
        identified = {"type": doc_type, "name": type_info["name"],
                     "template_id": type_info.get("template_id"), "confidence": 1.0}
    else:
        identified = identify_doc_type(user_input)
    
    result["steps"]["identify"] = {
        "type": identified["type"],
        "name": identified["name"],
        "confidence": identified["confidence"],
    }
    print(f"  识别结果: {identified['name']} (置信度: {identified['confidence']})")
    
    # Step 2: 匹配模板
    print("Step 2/5: 匹配模板...")
    prompt = get_template_prompt(identified["type"], user_input)
    result["steps"]["template"] = {
        "template_id": identified.get("template_id"),
        "prompt_length": len(prompt),
    }
    print(f"  模板: {identified.get('template_id', '通用')}")
    
    # Step 3: 生成初稿
    print("Step 3/5: 生成初稿...")
    draft_result = generate_draft(user_input, identified, llm_client=llm_client)
    result["steps"]["draft"] = {
        "char_count": len(draft_result["draft"]),
        "has_llm": llm_client is not None,
    }
    print(f"  初稿: {len(draft_result['draft'])} 字")
    
    # Step 4: 润色
    print("Step 4/5: 润色文档...")
    if auto_refine:
        refined = refine_draft(draft_result["draft"], identified["type"], llm_client=llm_client)
        result["steps"]["refine"] = {"changes": len(refined["changes"])}
        print(f"  修改: {len(refined['changes'])} 处")
    else:
        refined = None
        result["steps"]["refine"] = {"changes": 0}
        print("  跳过润色")
    
    # Step 5: 输出文件
    print("Step 5/5: 输出文件...")
    filepath = save_draft(draft_result, refined)
    result["steps"]["output"] = {"file": filepath}
    result["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    print(f"\n  文件已保存: {filepath}")
    print("  已进入「待审批」状态")
    
    return result


# =============================================
# CLI入口
# =============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="文案助理工作流")
    parser.add_argument("--step", choices=["identify", "generate", "refine", "full"],
                       default="full", help="执行步骤")
    parser.add_argument("--input", "-i", type=str, help="用户输入内容")
    parser.add_argument("--type", "-t", type=str, help="指定文档类型")
    parser.add_argument("--no-refine", action="store_true", help="跳过润色")
    
    args = parser.parse_args()
    
    if args.step == "identify" and args.input:
        result = identify_doc_type(args.input)
        print(f"  类型: {result['name']} (置信度: {result['confidence']})")
    
    elif args.step == "generate" and args.input:
        result = generate_draft(args.input)
        print(f"  类型: {result['doc_name']}")
        print(f"  初稿:\n{result['draft'][:500]}")
    
    elif args.step == "refine" and args.input:
        refined = refine_draft(args.input)
        print(f"  修改: {refined['changes']}")
        print(f"  润色后:\n{refined['refined'][:500]}")
    
    elif args.step == "full":
        if not args.input:
            # 交互模式
            print("请输入内容（Ctrl+Z结束）：")
            user_input = ""
            try:
                for line in sys.stdin:
                    user_input += line
            except EOFError:
                pass
        else:
            user_input = args.input
        
        if user_input.strip():
            run_full_workflow(user_input, args.type, not args.no_refine)
        else:
            print("  错误：请提供输入内容")
    
    else:
        parser.print_help()
