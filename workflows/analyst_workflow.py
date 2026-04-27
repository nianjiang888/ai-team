"""
数据分析师工作流 — 数据输入→清洗→分析→可视化→报告
T08: workflows/analyst_workflow.py

完整链路：
1. 接收数据文件（CSV/Excel），自动检测格式和数据质量
2. 数据清洗（去重、补缺、格式统一）
3. 生成分析报告（趋势/对比/异常检测）
4. 推荐并生成可视化图表
5. 输出分析报告（Markdown + 图表文件）
"""

import os
import json
import csv
from datetime import datetime
from typing import Optional


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
CONTENT_DIR = os.path.join(OUTPUTS_DIR, "content")
REVIEWS_DIR = os.path.join(OUTPUTS_DIR, "reviews")


# =============================================
# T08-1: 数据文件检测
# =============================================

def detect_file_format(filepath: str) -> dict:
    """
    检测数据文件格式和数据质量。
    
    Args:
        filepath: 数据文件路径
        
    Returns:
        dict: {"format", "rows", "cols", "columns", "quality_issues", "encoding"}
    """
    result = {
        "filepath": filepath,
        "format": None,
        "rows": 0,
        "cols": 0,
        "columns": [],
        "quality_issues": [],
        "encoding": "utf-8",
    }
    
    if not os.path.exists(filepath):
        result["quality_issues"].append("文件不存在")
        return result
    
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == ".csv":
        result["format"] = "csv"
        return _analyze_csv(filepath, result)
    elif ext in (".xlsx", ".xls"):
        result["format"] = "excel"
        return _analyze_excel(filepath, result)
    elif ext == ".json":
        result["format"] = "json"
        return _analyze_json(filepath, result)
    else:
        result["format"] = ext
        result["quality_issues"].append(f"不支持的格式: {ext}")
        return result


def _analyze_csv(filepath: str, result: dict) -> dict:
    """分析CSV文件"""
    # 检测编码
    for enc in ["utf-8", "utf-8-sig", "gbk", "gb2312", "latin1"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                reader = csv.reader(f)
                rows = list(reader)
            result["encoding"] = enc
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    else:
        result["quality_issues"].append("无法识别文件编码")
        return result
    
    if len(rows) < 2:
        result["quality_issues"].append("文件内容不足2行")
        return result
    
    result["columns"] = rows[0]
    result["rows"] = len(rows) - 1
    result["cols"] = len(rows[0])
    
    # 数据质量检查
    for col_idx, col_name in enumerate(rows[0]):
        col_values = [row[col_idx] if col_idx < len(row) else "" for row in rows[1:]]
        empty_count = sum(1 for v in col_values if not v.strip())
        if empty_count > len(col_values) * 0.5:
            result["quality_issues"].append(f"列'{col_name}'空值超过50%")
    
    # 检查重复行
    data_rows = [tuple(row) for row in rows[1:] if row]
    unique_rows = set(data_rows)
    if len(data_rows) - len(unique_rows) > 0:
        dup_count = len(data_rows) - len(unique_rows)
        result["quality_issues"].append(f"发现{dup_count}行重复数据")
    
    return result


def _analyze_excel(filepath: str, result: dict) -> dict:
    """分析Excel文件"""
    try:
        import openpyxl
        wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        wb.close()
    except ImportError:
        result["quality_issues"].append("需要安装openpyxl: pip install openpyxl")
        return result
    except Exception as e:
        result["quality_issues"].append(f"Excel读取失败: {e}")
        return result
    
    if len(rows) < 2:
        result["quality_issues"].append("文件内容不足2行")
        return result
    
    result["columns"] = [str(c) if c else f"col_{i}" for i, c in enumerate(rows[0])]
    result["rows"] = len(rows) - 1
    result["cols"] = len(rows[0])
    
    # 质量检查
    for col_idx, col_name in enumerate(result["columns"]):
        col_values = [row[col_idx] if col_idx < len(row) else None for row in rows[1:]]
        empty_count = sum(1 for v in col_values if v is None or str(v).strip() == "")
        if empty_count > len(col_values) * 0.5:
            result["quality_issues"].append(f"列'{col_name}'空值超过50%")
    
    return result


def _analyze_json(filepath: str, result: dict) -> dict:
    """分析JSON文件"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        result["quality_issues"].append(f"JSON解析失败: {e}")
        return result
    
    if isinstance(data, list) and len(data) > 0:
        result["rows"] = len(data)
        result["columns"] = list(data[0].keys()) if isinstance(data[0], dict) else []
        result["cols"] = len(result["columns"])
    elif isinstance(data, dict):
        result["rows"] = 1
        result["columns"] = list(data.keys())
        result["cols"] = len(result["columns"])
    else:
        result["quality_issues"].append("JSON格式不符合预期（需要数组或对象）")
    
    return result


# =============================================
# T08-2: 数据清洗
# =============================================

def generate_cleaning_plan(analysis: dict, user_desc: str = "") -> dict:
    """
    根据数据质量分析生成清洗方案。
    
    Args:
        analysis: detect_file_format() 的返回值
        user_desc: 用户描述的额外问题
        
    Returns:
        dict: 清洗方案
    """
    steps = []
    
    # 列名清洗
    steps.append({
        "step": 1,
        "action": "规范列名",
        "description": "去除列名前后空格和特殊字符",
        "type": "column_name",
        "auto": True,
    })
    
    # 去重
    has_dup = any("重复" in issue for issue in analysis.get("quality_issues", []))
    if has_dup or analysis.get("rows", 0) > 100:
        steps.append({
            "step": 2,
            "action": "去除重复行",
            "description": "基于所有列进行去重",
            "type": "dedup",
            "auto": True,
        })
    
    # 空值处理
    has_empty = any("空值" in issue for issue in analysis.get("quality_issues", []))
    if has_empty:
        steps.append({
            "step": 3,
            "action": "处理空值",
            "description": "数值列用中位数填充，文本列用N/A填充",
            "type": "fill_null",
            "auto": True,
        })
    
    # 格式统一
    steps.append({
        "step": len(steps) + 1,
        "action": "统一数据格式",
        "description": "日期列统一为YYYY-MM-DD，手机号统一为11位，去除前后空格",
        "type": "format",
        "auto": True,
    })
    
    # 用户描述的额外问题
    if user_desc:
        steps.append({
            "step": len(steps) + 1,
            "action": "用户自定义清洗",
            "description": user_desc,
            "type": "custom",
            "auto": False,
        })
    
    # 验证
    steps.append({
        "step": len(steps) + 1,
        "action": "清洗后验证",
        "description": "检查是否还有空值、重复、格式异常",
        "type": "verify",
        "auto": True,
    })
    
    return {
        "file": analysis.get("filepath", ""),
        "total_steps": len(steps),
        "steps": steps,
        "original_rows": analysis.get("rows", 0),
        "original_cols": analysis.get("cols", 0),
    }


def clean_data_csv(filepath: str, output_path: str = None, plan: dict = None) -> dict:
    """
    执行CSV数据清洗。
    
    Args:
        filepath: 原始文件路径
        output_path: 输出路径，None则自动生成
        plan: 清洗方案，None则自动分析
        
    Returns:
        dict: 清洗结果
    """
    if plan is None:
        analysis = detect_file_format(filepath)
        plan = generate_cleaning_plan(analysis)
    
    if output_path is None:
        base, ext = os.path.splitext(filepath)
        output_path = f"{base}_cleaned{ext}"
    
    # 读取数据
    rows = []
    encoding = "utf-8"
    for enc in ["utf-8", "utf-8-sig", "gbk", "gb2312", "latin1"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                reader = csv.reader(f)
                rows = list(reader)
            encoding = enc
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    if not rows:
        return {"success": False, "error": "无法读取文件"}
    
    original_count = len(rows) - 1
    headers = [h.strip() for h in rows[0]]
    data = rows[1:]
    
    # 执行清洗步骤
    log = []
    
    for step_info in plan.get("steps", []):
        if step_info["type"] == "column_name":
            log.append(f"[步骤{step_info['step']}] 列名已规范: {headers}")
        
        elif step_info["type"] == "dedup":
            seen = set()
            unique_data = []
            for row in data:
                key = tuple(row)
                if key not in seen:
                    seen.add(key)
                    unique_data.append(row)
            removed = len(data) - len(unique_data)
            data = unique_data
            log.append(f"[步骤{step_info['step']}] 去重: 删除{removed}行, 剩余{len(data)}行")
        
        elif step_info["type"] == "fill_null":
            filled = 0
            for row in data:
                for i in range(len(row)):
                    if i < len(row) and not row[i].strip():
                        row[i] = "N/A"
                        filled += 1
            log.append(f"[步骤{step_info['step']}] 空值填充: 填充{filled}个空值")
        
        elif step_info["type"] == "format":
            # 去前后空格
            trimmed = 0
            for row in data:
                for i in range(len(row)):
                    old = row[i]
                    row[i] = row[i].strip()
                    if old != row[i]:
                        trimmed += 1
            log.append(f"[步骤{step_info['step']}] 格式统一: 修剪{trimmed}个单元格")
        
        elif step_info["type"] == "verify":
            empty_count = sum(1 for row in data for cell in row if not cell.strip())
            log.append(f"[步骤{step_info['step']}] 验证完成: 剩余空值{empty_count}个")
    
    # 写出清洗后数据
    with open(output_path, "w", encoding=encoding, newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
    
    return {
        "success": True,
        "output_path": output_path,
        "original_rows": original_count,
        "cleaned_rows": len(data),
        "columns": len(headers),
        "steps_executed": len(log),
        "log": log,
    }


# =============================================
# T08-3: 分析报告生成
# =============================================

ANALYSIS_PROMPT = """你是一个数据分析师。请根据以下数据生成一份分析报告。

【数据概览】
文件: {filename}
行数: {rows}
列数: {cols}
列名: {columns}

【数据样本（前10行）】
{sample}

【用户需求】
{requirement}

【输出格式】
# 数据分析报告

## 1. 数据概览
- 总记录数、字段数、数据时间范围

## 2. 关键指标
- 核心指标的统计摘要（均值、最大、最小、中位数）

## 3. 趋势分析
- 如果有时间维度，分析变化趋势
- 环比/同比变化

## 4. 异常检测
- 标注异常数据点（🔴严重/🟡关注）
- 分析可能原因

## 5. 洞察与建议
- 3-5条可执行的业务建议
- 每条建议说明预期效果

注意：用数据说话，不要空话。"""


def generate_analysis_report(
    filepath: str,
    requirement: str = "全面分析数据趋势和异常点",
    llm_client=None,
) -> dict:
    """
    生成数据分析报告。
    
    Args:
        filepath: 数据文件路径
        requirement: 分析需求
        llm_client: LLM客户端
        
    Returns:
        dict: 报告结果
    """
    analysis = detect_file_format(filepath)
    
    # 读取数据样本
    sample = ""
    if analysis["format"] == "csv":
        try:
            with open(filepath, "r", encoding=analysis.get("encoding", "utf-8")) as f:
                reader = csv.reader(f)
                rows = list(reader)
            for row in rows[:11]:
                sample += " | ".join(str(c)[:30] for c in row) + "\n"
        except Exception:
            sample = "[无法读取样本数据]"
    else:
        sample = f"[{analysis['format']}格式，请在LLM中直接分析文件]"
    
    prompt = ANALYSIS_PROMPT.format(
        filename=os.path.basename(filepath),
        rows=analysis["rows"],
        cols=analysis["cols"],
        columns=", ".join(analysis["columns"][:10]),
        sample=sample[:2000],
        requirement=requirement,
    )
    
    report = ""
    if llm_client:
        try:
            report = llm_client.chat(prompt)
        except Exception:
            report = "[LLM生成失败]"
    else:
        report = f"[需调用LLM生成]\n\n{prompt}"
    
    return {
        "analysis": analysis,
        "requirement": requirement,
        "report": report,
        "prompt": prompt,
    }


# =============================================
# T08-4: 图表推荐
# =============================================

CHART_RECOMMENDATIONS = {
    "trend": {"name": "折线图", "best_for": "时间序列趋势分析", "lib": "matplotlib"},
    "comparison": {"name": "柱状图", "best_for": "类别对比", "lib": "matplotlib"},
    "proportion": {"name": "饼图", "best_for": "占比分析", "lib": "matplotlib"},
    "distribution": {"name": "直方图", "best_for": "数据分布", "lib": "matplotlib"},
    "correlation": {"name": "散点图", "best_for": "相关性分析", "lib": "matplotlib"},
    "heatmap": {"name": "热力图", "best_for": "多维数据对比", "lib": "seaborn"},
}


def recommend_charts(analysis: dict, requirement: str = "") -> list:
    """
    根据数据特征推荐合适的图表类型。
    
    Args:
        analysis: detect_file_format() 的结果
        requirement: 分析需求
        
    Returns:
        list[dict]: 推荐的图表列表
    """
    recommendations = []
    columns_lower = [c.lower() for c in analysis.get("columns", [])]
    
    # 检查是否有时间维度
    has_time = any(kw in " ".join(columns_lower) for kw in ["日期", "时间", "date", "time", "月", "年"])
    if has_time:
        recommendations.append({
            "chart_type": "trend",
            **CHART_RECOMMENDATIONS["trend"],
            "x_axis": "时间列",
            "y_axis": "数值列",
            "reason": "数据包含时间维度，适合展示趋势变化",
        })
    
    # 检查是否有分类维度
    has_category = any(kw in " ".join(columns_lower) for kw in ["类别", "类型", "平台", "地区", "城市", "分类"])
    if has_category:
        recommendations.append({
            "chart_type": "comparison",
            **CHART_RECOMMENDATIONS["comparison"],
            "x_axis": "类别列",
            "y_axis": "数值列",
            "reason": "数据包含分类维度，适合展示类别对比",
        })
    
    # 检查是否有占比相关需求
    has_proportion = any(kw in requirement for kw in ["占比", "比例", "分布", "构成"])
    if has_proportion:
        recommendations.append({
            "chart_type": "proportion",
            **CHART_RECOMMENDATIONS["proportion"],
            "x_axis": "类别列",
            "reason": "需求涉及占比分析，饼图最直观",
        })
    
    # 兜底：至少推荐一种
    if not recommendations:
        recommendations.append({
            "chart_type": "comparison",
            **CHART_RECOMMENDATIONS["comparison"],
            "x_axis": "类别列",
            "y_axis": "数值列",
            "reason": "默认推荐柱状图，适合大多数对比场景",
        })
    
    return recommendations


def generate_chart_code(recommendation: dict, filepath: str) -> str:
    """
    生成图表的Python代码。
    
    Returns:
        str: 可执行的Python代码
    """
    chart_type = recommendation.get("chart_type", "comparison")
    x_axis = recommendation.get("x_axis", "A")
    y_axis = recommendation.get("y_axis", "B")
    
    if chart_type == "trend":
        code = f"""import matplotlib.pyplot as plt
import pandas as pd

# 读取数据
df = pd.read_csv("{filepath}")

# 绘制折线图
plt.figure(figsize=(12, 6))
plt.plot(df.index, df.iloc[:, 1], marker='o', linewidth=2)
plt.title("趋势分析图")
plt.xlabel("{x_axis}")
plt.ylabel("{y_axis}")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("outputs/content/trend_chart.png", dpi=150)
plt.close()
print("图表已保存: outputs/content/trend_chart.png")
"""
    else:
        code = f"""import matplotlib.pyplot as plt
import pandas as pd

# 读取数据
df = pd.read_csv("{filepath}")

# 绘制柱状图
plt.figure(figsize=(10, 6))
bars = plt.bar(df.index, df.iloc[:, 1], color='#4A90D9')
plt.title("对比分析图")
plt.xlabel("{x_axis}")
plt.ylabel("{y_axis}")
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig("outputs/content/comparison_chart.png", dpi=150)
plt.close()
print("图表已保存: outputs/content/comparison_chart.png")
"""
    
    return code


# =============================================
# T08-5: 输出报告
# =============================================

def save_analysis_report(
    filepath: str,
    report_result: dict,
    chart_recommendations: list = None,
) -> str:
    """
    保存分析报告到 outputs/content/。
    使用 output_utils 统一格式。
    """
    from workflows.output_utils import (
        build_filename, build_markdown_doc,
        create_review, save_review,
    )

    os.makedirs(CONTENT_DIR, exist_ok=True)
    os.makedirs(REVIEWS_DIR, exist_ok=True)

    analysis = report_result.get("analysis", {})

    # 构建正文
    body = ""
    body += "## 数据概览\n\n"
    body += f"- 格式: {analysis.get('format', '未知')}\n"
    body += f"- 行数: {analysis.get('rows', 0)}\n"
    body += f"- 列数: {analysis.get('cols', 0)}\n"
    body += f"- 字段: {', '.join(analysis.get('columns', [])[:10])}\n"

    issues = analysis.get("quality_issues", [])
    if issues:
        body += f"- 质量问题: {', '.join(issues)}\n"

    body += "\n---\n\n"
    body += report_result.get("report", "[未生成]")

    if chart_recommendations:
        body += "\n\n---\n\n## 推荐图表\n\n"
        for rec in chart_recommendations:
            body += f"- **{rec['name']}**: {rec['reason']}\n"
            code_block = generate_chart_code(rec, filepath)
            body += f"\n  ```python\n{code_block}\n  ```\n"

    # 使用统一命名和结构
    filename = build_filename("analyst", "analysis_report")
    report_path = os.path.join(CONTENT_DIR, filename)

    doc = build_markdown_doc(
        employee="analyst",
        task_type="analysis_report",
        title=f"数据分析报告 - {os.path.basename(filepath)}",
        body=body,
        extra_meta={
            "data_file": os.path.basename(filepath),
            "requirement": report_result.get("requirement", "全面分析"),
            "data_rows": analysis.get("rows", 0),
            "data_cols": analysis.get("cols", 0),
        },
    )

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(doc)

    # 使用统一审批记录
    review_data = create_review(
        employee="analyst",
        task_type="analysis_report",
        title=f"分析报告 - {os.path.basename(filepath)}",
        content=body,
        filepath=filename,
    )
    review_data["data_file"] = os.path.basename(filepath)
    save_review(review_data, REVIEWS_DIR)

    return report_path


# =============================================
# 完整工作流
# =============================================

def run_full_workflow(
    filepath: str,
    requirement: str = "全面分析数据趋势和异常点",
    auto_clean: bool = True,
    llm_client=None,
) -> dict:
    """执行完整的数据分析工作流"""
    result = {
        "workflow": "analyst",
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "steps": {},
    }
    
    # Step 1: 检测文件
    print("Step 1/5: 检测数据文件...")
    analysis = detect_file_format(filepath)
    result["steps"]["detect"] = analysis
    print(f"  格式: {analysis['format']}, {analysis['rows']}行 × {analysis['cols']}列")
    if analysis["quality_issues"]:
        print(f"  问题: {analysis['quality_issues']}")
    
    # Step 2: 清洗
    print("Step 2/5: 数据清洗...")
    if auto_clean and analysis["format"] in ("csv", "excel"):
        plan = generate_cleaning_plan(analysis)
        if analysis["format"] == "csv":
            clean_result = clean_data_csv(filepath, plan=plan)
            result["steps"]["clean"] = clean_result
            print(f"  清洗: {clean_result.get('log', [])}")
        else:
            result["steps"]["clean"] = {"plan": plan}
            print(f"  清洗方案: {len(plan['steps'])}步")
    else:
        print("  跳过清洗")
    
    # Step 3: 生成报告
    print("Step 3/5: 生成分析报告...")
    report = generate_analysis_report(filepath, requirement, llm_client=llm_client)
    result["steps"]["report"] = {"length": len(report["report"])}
    
    # Step 4: 推荐图表
    print("Step 4/5: 推荐图表...")
    charts = recommend_charts(analysis, requirement)
    result["steps"]["charts"] = charts
    print(f"  推荐: {', '.join(c['name'] for c in charts)}")
    
    # Step 5: 输出
    print("Step 5/5: 保存报告...")
    report_path = save_analysis_report(filepath, report, charts)
    result["steps"]["output"] = {"file": report_path}
    result["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    print(f"\n  报告已保存: {report_path}")
    
    return result
