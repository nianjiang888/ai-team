#!/usr/bin/env python3
"""
一人公司AI团队 - 一键启动脚本
"""

import sys
import os
import subprocess
import webbrowser
import threading
import time

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


def check_python_version():
    """检查Python版本 >= 3.10"""
    if sys.version_info < (3, 10):
        print("❌ Python版本过低，需要 3.10 或以上")
        print(f"   当前版本: {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


def check_config():
    """检查配置文件"""
    local_config = os.path.join(BASE_DIR, "config.local.yaml")
    default_config = os.path.join(BASE_DIR, "config.yaml")

    if os.path.exists(local_config):
        print("✅ 找到配置文件: config.local.yaml")
        return local_config
    elif os.path.exists(default_config):
        print("⚠️  使用默认配置（请复制 config.yaml 为 config.local.yaml 并填入你的API Key）")
        return default_config
    else:
        print("❌ 找不到配置文件 config.yaml")
        sys.exit(1)


def install_dependencies():
    """检查并安装依赖"""
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError:
        print("📦 正在安装依赖...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r",
            os.path.join(BASE_DIR, "requirements.txt"),
            "--quiet"
        ])
        print("✅ 依赖安装完成")


def ensure_dirs():
    """确保输出目录存在"""
    dirs = [
        os.path.join(BASE_DIR, "outputs", "daily-reports"),
        os.path.join(BASE_DIR, "outputs", "content"),
        os.path.join(BASE_DIR, "outputs", "reviews"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def load_config():
    """加载配置"""
    config_path = check_config()
    try:
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        print("📦 安装 PyYAML...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "--quiet"])
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)


def open_browser(port, delay=2):
    """延迟打开浏览器"""
    time.sleep(delay)
    webbrowser.open(f"http://localhost:{port}")


def main():
    print("=" * 50)
    print("  一人公司AI团队  v1.0")
    print("=" * 50)
    print()

    # 1. 环境检查
    check_python_version()

    # 2. 检查配置
    config = load_config()

    # 3. 安装依赖
    install_dependencies()

    # 4. 确保目录
    ensure_dirs()

    # 5. 读取看板配置
    port = config.get("dashboard", {}).get("port", 5678)
    auto_open = config.get("dashboard", {}).get("auto_open_browser", True)

    print(f"\n🚀 启动看板服务: http://localhost:{port}")

    if auto_open:
        threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # 6. 启动Flask服务
    from dashboard.app import create_app
    app = create_app(config)
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
