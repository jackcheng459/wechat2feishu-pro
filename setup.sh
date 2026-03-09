#!/bin/bash
# setup.sh — 一键环境初始化脚本
# 用法：bash setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Wechat2Feishu 环境初始化"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. 检查 Python
echo "▶ 检查 Python 版本…"
if ! command -v python3 &>/dev/null; then
    echo "❌ 未找到 python3，请先安装 Python 3.10+"
    exit 1
fi
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "  ✅ Python $PYTHON_VERSION"

# 2. 创建虚拟环境
echo ""
echo "▶ 创建虚拟环境 (.venv)…"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "  ✅ 虚拟环境创建完成"
else
    echo "  ✅ 虚拟环境已存在，跳过"
fi

# 激活虚拟环境
source .venv/bin/activate

# 3. 安装依赖
echo ""
echo "▶ 安装 Python 依赖…"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "  ✅ 依赖安装完成"

# 4. 安装 Playwright 浏览器内核
echo ""
echo "▶ 安装 Playwright Chromium（约 150MB，首次安装较慢）…"
python -m playwright install chromium
echo "  ✅ Chromium 安装完成"

# 5. 初始化 .env 文件
echo ""
echo "▶ 初始化配置文件…"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  ✅ .env 文件已创建（请填入飞书应用凭证）"
else
    echo "  ✅ .env 文件已存在，跳过"
fi

# 6. 完成提示
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ 初始化完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "接下来的步骤："
echo ""
echo "  1. 编辑 .env 文件，填入飞书应用凭证："
echo "     nano .env"
echo ""
echo "  2. 完成飞书 OAuth 授权："
echo "     source .venv/bin/activate"
echo "     python main.py auth"
echo ""
echo "  3. 测试抓取一篇文章："
echo "     python main.py scrape https://mp.weixin.qq.com/s/xxx"
echo ""
echo "  飞书应用创建教程："
echo "  https://open.feishu.cn/document/home/develop-a-bot-in-5-minutes/create-an-app"
echo ""
