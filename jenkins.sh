#!/bin/bash
set -e

cd /Users/yefenglei/.jenkins/workspace/test_pytest

# ★ 新增：定位 Python 3.14 解释器（按优先级找）
PY314=""
for p in \
    /opt/homebrew/bin/python3.14 \
    /usr/local/bin/python3.14 \
    /Users/yefenglei/.pyenv/versions/3.14.0/bin/python3.14 \
    /Users/yefenglei/.pyenv/versions/3.14*/bin/python3.14 ; do
    if [ -x "$p" ]; then PY314="$p"; break; fi
done

if [ -z "$PY314" ]; then
    echo "❌ 没找到 python3.14，请先安装（brew install python@3.14 或 pyenv install 3.14.0）"
    exit 1
fi
echo ">>> 使用解释器: $PY314 ($($PY314 --version))"

echo "========== 1. 创建/激活虚拟环境 =========="
# ★ 改动1：每次重建 venv，避免旧 3.9 venv 被复用
rm -rf venv
"$PY314" -m venv venv
source venv/bin/activate

echo "========== 2. 升级 pip =========="
pip install --upgrade pip

echo "========== 3. 安装依赖 =========="
pip install -r requirements.txt

echo "========== 4. 验证 pytest 已安装 =========="
pytest --version
echo "=== PATH ==="
echo $PATH

echo "=== which allure ==="
# ★ 改动2：把 allure 2.44.0 加到 PATH 前面
export PATH=/usr/local/allure-2.44.0/bin:$PATH
which allure || echo "allure not in PATH"

echo "=== ls /usr/local/allure-2.44.0/bin/ ==="
ls -la /usr/local/allure-2.44.0/bin/

echo "========== 5. 运行测试 =========="
python3 run.py

# 验证结果
echo "=== allure-results 内容 ==="
ls -la allure-results/

echo "=== allure-history 内容 ==="
ls -la allure-history/ | tail -5

# 只保留最近 10 次历史
cd ${WORKSPACE}/allure-history
ls -t | tail -n +11 | xargs rm -rf 2>/dev/null || true

echo "========== 构建结束 =========="