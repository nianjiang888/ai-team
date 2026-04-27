"""
新媒体运营工作流 — 选题→写稿→润色→排版→审批
T06: workflows/social_media_workflow.py

完整链路：
1. 抓取热搜/榜单数据（web_search 或 预设来源）
2. LLM分析热搜，生成5个选题建议
3. 选题格式化输出到 outputs/topics/
4. 用户选择选题后，调用对应平台文案模板
5. 自动润色去AI腔
6. 输出排版好的文件到 outputs/content/，进入"待审批"状态
7. APScheduler定时任务（每天8:00触发选题抓取）
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional


# =============================================
# 配置
# =============================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
TOPICS_DIR = os.path.join(OUTPUTS_DIR, "topics")
CONTENT_DIR = os.path.join(OUTPUTS_DIR, "content")
REVIEWS_DIR = os.path.join(OUTPUTS_DIR, "reviews")

# 平台配置
PLATFORMS = {
    "xiaohongshu": {
        "name": "小红书",
        "style": "种草风、emoji丰富、分段短句、互动引导",
        "max_title_len": 20,
        "max_body_len": 1000,
        "tags_required": True,
    },
    "wechat": {
        "name": "公众号",
        "style": "深度长文、结构清晰、专业但不生硬",
        "max_title_len": 30,
        "max_body_len": 3000,
        "tags_required": False,
    },
    "douyin": {
        "name": "抖音",
        "style": "口语化、短句为主、前3秒抓人",
        "max_title_len": 25,
        "max_body_len": 500,
        "tags_required": True,
    },
    "toutiao": {
        "name": "今日头条",
        "style": "资讯风、标题抓眼球、内容有信息量",
        "max_title_len": 30,
        "max_body_len": 2000,
        "tags_required": False,
    },
}

# 默认热搜关键词（按行业分类，可由config.yaml扩展）
DEFAULT_KEYWORDS = [
    "AI工具", "提效", "一人公司", "副业", "自媒体",
    "AI写作", "ChatGPT", "小红书运营", "短视频", "创业",
]


# =============================================
# T06-1: 热搜数据抓取
# =============================================

def fetch_trending(keywords: list = None) -> list:
    """
    抓取热搜/榜单数据。
    
    在WorkBuddy环境下，通过调用web_search抓取。
    独立运行时，通过公开API（如百度热搜、微博热搜）获取。
    
    Args:
        keywords: 搜索关键词列表，None则使用默认关键词
        
    Returns:
        list[dict]: 热搜条目列表，每条包含 title, source, hot_score, url
    """
    if keywords is None:
        keywords = DEFAULT_KEYWORDS
    
    trending_items = []
    
    # 方式1: 微博热搜API（免费、无需key）
    try:
        resp = requests.get(
            "https://weibo.com/ajax/side/hotSearch",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("data", {}).get("realtime"):
                for item in data["data"]["realtime"][:15]:
                    trending_items.append({
                        "title": item.get("word", ""),
                        "source": "微博热搜",
                        "hot_score": item.get("num", 0),
                        "url": f"https://s.weibo.com/weibo?q={item.get('word', '')}",
                        "category": "general",
                    })
    except Exception:
        pass
    
    # 方式2: 百度热搜（通过RSS）
    try:
        resp = requests.get(
            "https://top.baidu.com/board?tab=realtime",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        # 百度热搜需要解析HTML，这里简化为提示
        if resp.status_code == 200:
            trending_items.append({
                "title": "[百度热搜] 抓取成功，需在WorkBuddy中调用web_search解析",
                "source": "百度热搜",
                "hot_score": 0,
                "url": "https://top.baidu.com/board?tab=realtime",
                "category": "general",
            })
    except Exception:
        pass
    
    # 方式3: 基于关键词的搜索建议（兜底）
    if len(trending_items) < 5:
        for kw in keywords[:5]:
            trending_items.append({
                "title": kw,
                "source": "关键词搜索",
                "hot_score": 0,
                "url": "",
                "category": "行业相关",
            })
    
    return trending_items


# =============================================
# T06-2: LLM分析热搜，生成选题建议
# =============================================

def generate_topics(
    trending_items: list,
    niche: str = "AI效率工具/一人公司运营",
    count: int = 5,
    llm_client=None,
) -> list:
    """
    分析热搜数据，生成选题建议。
    
    在WorkBuddy环境下，由AI agent直接调用。
    独立运行时，使用传入的llm_client或返回结构化提示词。
    
    Args:
        trending_items: 热搜条目列表
        niche: 你的内容定位/垂直领域
        count: 生成选题数量
        llm_client: 可选的LLM客户端（需支持 .chat() 方法）
        
    Returns:
        list[dict]: 选题建议列表
    """
    # 构造热搜摘要
    hot_summary = "\n".join([
        f"- {item['title']}（{item['source']}，热度{item['hot_score']}）"
        for item in trending_items[:15]
    ])
    
    # 选题生成提示词
    topic_prompt = f"""你是一个资深新媒体运营，擅长从热点中找到与以下领域结合的选题机会。

【我的内容定位】{niche}

【今日热搜/热点】
{hot_summary}

【任务】
从以上热点中，找出与我的领域相关的选题机会，生成{count}个选题建议。

【输出格式（JSON数组）】
[
  {{
    "id": 1,
    "title": "选题标题（吸引眼球但不是标题党）",
    "angle": "切入角度（一句话说明怎么蹭热点）",
    "platform": "推荐首发平台（xiaohongshu/wechat/douyin/toutiao）",
    "reason": "推荐理由（为什么这个选题有流量）",
    "urgency": "时效性（immediate=今天必须发/today=今天发最好/week=本周内可发）",
    "keywords": ["关键词1", "关键词2"]
  }}
]

要求：
1. 选题必须与我的领域有真实关联，不要硬蹭
2. 标题控制在20字以内
3. 优先选择时效性高的话题
4. 覆盖不同平台"""

    # 如果有LLM客户端，直接调用
    if llm_client:
        try:
            response = llm_client.chat(topic_prompt)
            topics = _parse_json_response(response)
            if topics:
                return topics[:count]
        except Exception:
            pass
    
    # 没有LLM时，返回结构化提示词（供手动使用或WorkBuddy调用）
    return [{
        "id": i + 1,
        "title": f"[待AI生成] 基于热搜选题{i+1}",
        "angle": "由AI根据热搜分析生成",
        "platform": "xiaohongshu",
        "reason": "需要LLM分析热搜后生成",
        "urgency": "today",
        "keywords": [],
        "_prompt": topic_prompt,  # 供WorkBuddy使用
    } for i in range(count)]


def _parse_json_response(text: str) -> list:
    """从LLM响应中提取JSON数组"""
    import re
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 提取JSON块
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return []


# =============================================
# T06-3: 选题格式化输出
# =============================================

def save_topics(topics: list, date_str: str = None) -> str:
    """
    将选题保存到 outputs/topics/ 目录。
    
    Args:
        topics: 选题列表
        date_str: 日期字符串，None则使用今天
        
    Returns:
        str: 保存的文件路径
    """
    os.makedirs(TOPICS_DIR, exist_ok=True)
    
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    filepath = os.path.join(TOPICS_DIR, f"topics_{date_str}.json")
    
    data = {
        "date": date_str,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "topic_count": len(topics),
        "topics": topics,
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filepath


def load_today_topics() -> list:
    """加载今天的选题"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(TOPICS_DIR, f"topics_{date_str}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("topics", [])
    return []


# =============================================
# T06-4: 文案生成（多平台适配）
# =============================================

PLATFORM_TEMPLATES = {
    "xiaohongshu": """你是一个小红书爆款文案写手。根据以下信息写一篇种草笔记。

【产品/主题】{product}
【卖点】{selling_points}
【目标受众】{audience}
【切入角度】{angle}
【参考关键词】{keywords}

【输出要求】
1. 标题：20字以内，带情绪或数字，吸引点击
2. 正文：分段短句，每段2-4行，适当用emoji（每段1-2个）
3. 风格：像朋友推荐朋友，不要官方广告腔
4. 结构：开头抓人 → 产品介绍 → 使用场景 → 个人感受 → 互动引导
5. 结尾：提问引导评论 + 话题标签（至少5个）
6. 总字数：400-800字""",

    "wechat": """你是一个公众号深度内容写手。根据以下信息写一篇文章。

【产品/主题】{product}
【卖点】{selling_points}
【目标受众】{audience}
【切入角度】{angle}
【参考关键词】{keywords}

【输出要求】
1. 标题：30字以内，有信息量，让读者想点开
2. 正文：2000-3000字，结构清晰，有深度
3. 风格：专业但不生硬，有观点有数据
4. 结构：开头抛问题 → 分析原因 → 给出方案 → 案例佐证 → 总结行动建议
5. 小标题用3-5个，每个小标题下至少300字""",

    "douyin": """你是一个抖音短视频脚本写手。根据以下信息写一个60秒短视频脚本。

【产品/主题】{product}
【卖点】{selling_points}
【目标受众】{audience}
【切入角度】{angle}
【参考关键词】{keywords}

【输出要求】
1. 格式：分镜头脚本（画面|旁白|字幕|时长）
2. 前3秒必须抓人（抛痛点/反常识/提问）
3. 总时长60秒，旁白字数200字以内
4. 口语化，不要书面语
5. 结尾有CTA（关注/点赞/评论区见）""",

    "toutiao": """你是一个今日头条资讯类写手。根据以下信息写一篇文章。

【产品/主题】{product}
【卖点】{selling_points}
【目标受众】{audience}
【切入角度】{angle}
【参考关键词】{keywords}

【输出要求】
1. 标题：25字以内，有信息量，适合资讯流
2. 正文：1500-2500字，有信息密度
3. 风格：客观分析+观点输出，不要标题党
4. 结构：新闻引入 → 现状分析 → 深度解读 → 行业观点 → 未来展望
5. 引用至少2个数据或案例""",
}


def generate_content(
    topic: dict,
    product: str = "AI效率全能助手",
    selling_points: str = "5个AI员工、58个模板、覆盖80%办公场景、提效4x-20x",
    audience: str = "一人公司创始人、自由职业者、小团队",
    platform: str = None,
    llm_client=None,
) -> dict:
    """
    根据选题生成多平台文案。
    
    Args:
        topic: 选题字典
        product: 产品名称
        selling_points: 卖点描述
        audience: 目标受众
        platform: 指定平台，None则用选题推荐的
        llm_client: LLM客户端
        
    Returns:
        dict: 生成的文案内容
    """
    platform = platform or topic.get("platform", "xiaohongshu")
    config = PLATFORMS.get(platform, PLATFORMS["xiaohongshu"])
    
    template = PLATFORM_TEMPLATES.get(platform, PLATFORM_TEMPLATES["xiaohongshu"])
    prompt = template.format(
        product=product,
        selling_points=selling_points,
        audience=audience,
        angle=topic.get("angle", ""),
        keywords=", ".join(topic.get("keywords", [])),
    )
    
    # 如果有LLM，直接生成
    content_text = ""
    if llm_client:
        try:
            content_text = llm_client.chat(prompt)
        except Exception:
            content_text = "[LLM生成失败，请手动使用Prompt]"
    else:
        content_text = f"[需调用LLM生成]\n\n{prompt}"
    
    return {
        "topic_id": topic.get("id", 0),
        "topic_title": topic.get("title", ""),
        "platform": platform,
        "platform_name": config["name"],
        "content": content_text,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


# =============================================
# T06-5: 自动润色去AI腔
# =============================================

REFINEMENT_PROMPT = """你是一个文案审稿人，负责润色以下内容，去除AI味。

【润色规则】
1. 去掉"首先、其次、最后、综上所述"等AI常用连接词
2. 去掉过度排比（连续3个以上相同句式）
3. 删除空洞的形容词和副词（"令人瞩目的"、"毋庸置疑的"）
4. 把长句拆成短句（超过30字的句子必须拆）
5. 加入1-2个口语化表达（"说实话"、"讲真"、"不瞒你说"等，但不要过度）
6. 检查是否有煽情/鸡汤/空话，删除或改为具体内容
7. 保持原意不变，不要添加原文没有的信息
8. 不要改变文章结构

【原文】
{content}

【输出】
直接输出润色后的全文，不要加任何解释。"""


def refine_content(content: str, llm_client=None) -> str:
    """
    润色内容，去除AI腔。
    
    Args:
        content: 原始内容
        llm_client: LLM客户端
        
    Returns:
        str: 润色后的内容
    """
    prompt = REFINEMENT_PROMPT.format(content=content)
    
    if llm_client:
        try:
            refined = llm_client.chat(prompt)
            return refined.strip()
        except Exception:
            return content
    
    # 没有LLM时返回原文+提示
    return f"{content}\n\n---\n[润色提示] 需调用LLM执行去AI腔润色，参考上述规则"


def quality_check(content: str) -> dict:
    """
    质量检查（不依赖LLM的规则检查）。
    
    Returns:
        dict: { score: 0-100, issues: list }
    """
    issues = []
    score = 100
    
    # 检查1: AI腔关键词
    ai_keywords = [
        "首先", "其次", "最后", "综上所述", "总而言之",
        "令人瞩目", "毋庸置疑", "不可否认", "众所周知",
        "在这个快速发展的时代", "随着科技的不断进步",
        "值得一提的是", "需要注意的是",
    ]
    found_ai = [kw for kw in ai_keywords if kw in content]
    if found_ai:
        issues.append(f"AI腔关键词: {', '.join(found_ai)}")
        score -= len(found_ai) * 3
    
    # 检查2: 过长句子（>40字）
    sentences = content.replace("。", "。\n").replace("！", "！\n").replace("？", "？\n").split("\n")
    long_sentences = [s.strip() for s in sentences if len(s.strip()) > 40]
    if long_sentences:
        issues.append(f"过长句子({len(long_sentences)}句，建议<30字)")
        score -= len(long_sentences) * 2
    
    # 检查3: 过度排比（连续3+个相同开头的句子）
    lines = [l.strip() for l in content.split("\n") if l.strip()]
    consecutive_count = 0
    for i in range(1, len(lines)):
        if lines[i].startswith(("1.", "2.", "3.", "一、", "二、", "三、")):
            consecutive_count += 1
        else:
            consecutive_count = 0
        if consecutive_count >= 3:
            issues.append("可能存在过度排比")
            score -= 5
            break
    
    # 检查4: 字数
    char_count = len(content)
    if char_count < 50:
        issues.append(f"内容过短({char_count}字，建议>200字)")
        score -= 10
    
    score = max(0, min(100, score))
    
    return {
        "score": score,
        "issues": issues,
        "char_count": char_count,
        "passed": score >= 70,
    }


# =============================================
# T06-6: 输出文件 + 审批状态
# =============================================

def save_content(content_data: dict, auto_refine: bool = True, llm_client=None) -> str:
    """
    将内容保存到 outputs/content/ 并创建审批记录到 outputs/reviews/。
    使用 output_utils 统一格式。
    """
    from workflows.output_utils import (
        build_filename, build_markdown_doc,
        create_review, save_review,
    )

    os.makedirs(CONTENT_DIR, exist_ok=True)
    os.makedirs(REVIEWS_DIR, exist_ok=True)

    platform = content_data.get("platform", "xiaohongshu")
    task_type = platform if platform in ["xiaohongshu", "douyin", "wechat", "weibo"] else "content"

    # 润色
    raw_content = content_data.get("content", "")
    if auto_refine:
        refined_content = refine_content(raw_content, llm_client=llm_client)
    else:
        refined_content = raw_content

    # 质量检查
    qc = quality_check(refined_content)

    # 使用统一命名
    filename = build_filename("social_media", task_type)
    filepath = os.path.join(CONTENT_DIR, filename)

    # 使用统一文件结构
    doc = build_markdown_doc(
        employee="social_media",
        task_type=task_type,
        title=content_data.get("topic_title", "未命名"),
        body=refined_content,
        quality_info=qc,
        extra_meta={
            "platform": content_data.get("platform_name", platform),
            "topic_id": content_data.get("topic_id", 0),
        },
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(doc)

    # 使用统一审批记录
    review_data = create_review(
        employee="social_media",
        task_type=task_type,
        title=content_data.get("topic_title", ""),
        content=refined_content,
        filepath=filename,
    )
    save_review(review_data, REVIEWS_DIR)

    return filepath


# =============================================
# T06-7: 定时任务调度
# =============================================

def setup_scheduler(trigger_time: str = "08:00", callback=None):
    """
    配置定时任务，每天自动执行选题抓取+生成。
    
    Args:
        trigger_time: 触发时间，格式 "HH:MM"
        callback: 选题生成完成后的回调函数
        
    Returns:
        APScheduler BackgroundScheduler 实例
    """
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    
    scheduler = BackgroundScheduler()
    
    hour, minute = map(int, trigger_time.split(":"))
    
    def daily_topic_job():
        """每日选题抓取任务"""
        print(f"[{datetime.now()}] 开始执行每日选题抓取...")
        try:
            # Step 1: 抓取热搜
            trending = fetch_trending()
            print(f"  抓取到 {len(trending)} 条热搜")
            
            # Step 2: 生成选题（需要LLM，这里先保存热搜）
            if callback:
                callback(trending)
            else:
                # 保存热搜数据，等待LLM处理
                filepath = save_topics([{
                    "id": i + 1,
                    "title": item["title"],
                    "angle": f"[待分析] {item['source']}",
                    "platform": "xiaohongshu",
                    "reason": f"来源: {item['source']}",
                    "urgency": "today",
                    "keywords": [],
                } for i, item in enumerate(trending[:5])])
                print(f"  选题已保存到 {filepath}")
            
            print(f"[{datetime.now()}] 每日选题抓取完成")
        except Exception as e:
            print(f"[{datetime.now()}] 选题抓取失败: {e}")
    
    scheduler.add_job(
        daily_topic_job,
        trigger=CronTrigger(hour=hour, minute=minute),
        id="daily_topic_generation",
        name="每日选题生成",
        replace_existing=True,
    )
    
    return scheduler


# =============================================
# 完整工作流：一键执行
# =============================================

def run_full_workflow(
    product: str = "AI效率全能助手",
    selling_points: str = None,
    audience: str = None,
    platform: str = None,
    auto_refine: bool = True,
    llm_client=None,
) -> dict:
    """
    执行完整的新媒体运营工作流。
    
    流程：抓热搜 → 生成选题 → 保存选题 → 等用户选择 → 生成文案 → 润色 → 输出审批
    
    Args:
        product: 产品名称
        selling_points: 卖点
        audience: 目标受众
        platform: 指定平台
        auto_refine: 是否自动润色
        llm_client: LLM客户端
        
    Returns:
        dict: 工作流执行结果
    """
    if selling_points is None:
        selling_points = "5个AI员工、58个模板、覆盖80%办公场景、提效4x-20x"
    if audience is None:
        audience = "一人公司创始人、自由职业者、小团队"
    
    result = {
        "workflow": "social_media",
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "steps": {},
    }
    
    # Step 1-2: 抓热搜 + 生成选题
    print("Step 1/5: 抓取热搜数据...")
    trending = fetch_trending()
    result["steps"]["trending"] = {"count": len(trending), "sources": list(set(i["source"] for i in trending))}
    
    print("Step 2/5: 生成选题建议...")
    topics = generate_topics(trending, llm_client=llm_client)
    
    print("Step 3/5: 保存选题...")
    topics_file = save_topics(topics)
    result["steps"]["topics"] = {"count": len(topics), "file": topics_file}
    
    # 打印选题供用户选择
    print(f"\n{'='*60}")
    print("📋 今日选题建议（共{0}个）".format(len(topics)))
    print(f"{'='*60}")
    for t in topics:
        print(f"  [{t.get('id')}] {t.get('title')}")
        print(f"      平台: {PLATFORMS.get(t.get('platform','xiaohongshu'),{}).get('name','未知')}")
        print(f"      角度: {t.get('angle','')}")
        print(f"      时效: {t.get('urgency','')}")
        print()
    
    # Step 4: 对每个选题生成文案
    print("Step 4/5: 生成文案...")
    content_files = []
    for topic in topics:
        pf = platform or topic.get("platform", "xiaohongshu")
        content_data = generate_content(
            topic=topic,
            product=product,
            selling_points=selling_points,
            audience=audience,
            platform=pf,
            llm_client=llm_client,
        )
        filepath = save_content(content_data, auto_refine=auto_refine, llm_client=llm_client)
        content_files.append(filepath)
    
    result["steps"]["content"] = {"count": len(content_files), "files": content_files}
    
    # Step 5: 汇总
    result["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    result["summary"] = (
        f"抓取{len(trending)}条热搜 → 生成{len(topics)}个选题 → "
        f"输出{len(content_files)}篇文案 → 待审批"
    )
    
    print("Step 5/5: 工作流完成！")
    print(f"\n📊 结果汇总：{result['summary']}")
    print(f"📂 选题文件: {topics_file}")
    print(f"📂 文案文件: {', '.join(content_files)}")
    print("\n✅ 所有文案已进入「待审批」状态，请到 reviews/ 目录查看。")
    
    return result


# =============================================
# CLI入口
# =============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="新媒体运营工作流")
    parser.add_argument("--step", choices=["fetch", "topics", "generate", "refine", "full"],
                       default="full", help="执行步骤")
    parser.add_argument("--product", default="AI效率全能助手", help="产品名称")
    parser.add_argument("--platform", default=None, help="指定平台")
    parser.add_argument("--no-refine", action="store_true", help="跳过润色")
    
    args = parser.parse_args()
    
    if args.step == "fetch":
        items = fetch_trending()
        for i, item in enumerate(items[:10]):
            print(f"  {i+1}. {item['title']} ({item['source']})")
    
    elif args.step == "topics":
        trending = fetch_trending()
        topics = generate_topics(trending)
        for t in topics:
            print(f"  [{t['id']}] {t['title']} → {t['platform']}")
        filepath = save_topics(topics)
        print(f"\n  选题已保存: {filepath}")
    
    elif args.step == "generate":
        topics = load_today_topics()
        if not topics:
            print("  今天没有选题，请先执行 --step topics")
        else:
            for topic in topics:
                content = generate_content(topic, platform=args.platform)
                print(f"  [{topic['id']}] {topic['title']}")
                print(f"  平台: {content['platform_name']}")
                print(f"  预览: {content['content'][:100]}...\n")
    
    elif args.step == "refine":
        import glob
        md_files = glob.glob(os.path.join(CONTENT_DIR, "*.md"))
        for f in md_files[:3]:
            with open(f, "r", encoding="utf-8") as fh:
                content = fh.read()
            qc = quality_check(content)
            print(f"  {os.path.basename(f)}: {qc['score']}/100", end="")
            if qc["issues"]:
                print(f" ({', '.join(qc['issues'][:2])})")
            else:
                print(" ✅")
    
    elif args.step == "full":
        run_full_workflow(
            product=args.product,
            platform=args.platform,
            auto_refine=not args.no_refine,
        )
