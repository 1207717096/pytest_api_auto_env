# python-test-api

基于 **pytest + Excel + requests + Allure** 的接口自动化测试框架。  
用例维护在 Excel 中，支持 HTTP 断言、数据库断言、JSON/SQL 变量提取与用例间传参。

## 功能特性

- Excel 驱动：在表格中维护用例，无需改代码即可扩展场景
- 数据驱动执行：`pytest.mark.parametrize` 参数化运行
- 请求封装：统一解析 method / path / headers / params / data / json / files
- 断言能力：HTTP 响应断言、MySQL 数据库断言
- 变量提取：JSONPath 提取、SQL 提取，支持 Jinja2 模板跨用例传参（如 `{{TOKEN}}`）
- 报告与日志：pytest-html、Allure HTML、按时间戳落盘的运行日志

## 技术栈

| 类型 | 依赖 |
|------|------|
| 测试框架 | pytest、pytest-html、pytest-ordering、pytest-rerunfailures |
| 请求 / 解析 | requests、jsonpath |
| 数据源 | openpyxl（Excel）、pymysql（MySQL） |
| 报告 | allure-pytest + Allure 命令行 |
| 模板 | Jinja2 |

## 项目结构

```text
python-test-api/
├── config/
│   └── config.py              # 环境地址、Excel 路径、数据库配置
├── data/
│   └── 测试用例.xlsx           # 接口测试用例
├── files/                     # 上传文件等测试资源
├── testcase/
│   └── test_runner_*.py       # 测试执行入口（推荐最新版本）
├── utils/
│   ├── excel_utils.py         # 读取 Excel 用例
│   ├── analyse_case.py        # 解析用例为 requests 参数
│   ├── send_request.py        # HTTP / JDBC 请求
│   ├── asserts.py             # HTTP / 数据库断言
│   ├── extractor.py           # JSON / SQL 变量提取
│   └── allure_utils.py        # Allure 动态标题等
├── report/                    # pytest-html 报告
├── allure-results/            # Allure 原始结果与 HTML 报告
├── log/                       # 运行日志
├── conftest.py                # pytest 钩子与日志配置
├── run.py                     # 一键执行并生成报告
├── pytest.ini
└── install_package.sh         # 依赖安装脚本
```

## 环境准备

### 1. Python 依赖

```bash
# 方式一：使用项目脚本
bash install_package.sh

# 方式二：手动安装
pip3 install requests pytest pytest-html pytest-ordering allure-pytest \
  pymysql openpyxl jinja2 jsonpath pytest-rerunfailures
```

### 2. Allure 命令行（生成 HTML 报告）

1. 解压 Allure 到本地，例如：`/usr/local/allure-2.44.0`
2. 配置环境变量（`~/.zshrc`）：

```bash
export ALLURE_HOME=/usr/local/allure-2.44.0
export PATH=$PATH:$ALLURE_HOME/bin
```

3. 终端验证：

```bash
allure --version
```

> 说明：IDE 运行 Python 时通常不会加载 `~/.zshrc`。  
> 因此 `run.py` 中默认使用 Allure 完整路径：`/usr/local/allure-2.44.0/bin/allure`。  
> 若本机安装路径不同，请同步修改 `run.py`。

### 3. 被测服务与数据库

在 `config/config.py` 中按实际环境修改：

```python
BASE_URL = 'http://127.0.0.1:8888/api/private/v1'

EXCEL_FILE = './data/测试用例.xlsx'
SHEET_NAME = 'Sheet1'

DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_NAME = 'mydb'
DB_PORT = 3306
```

请确认：

- 接口服务已启动（默认 `127.0.0.1:8888`）
- 如用例含数据库断言 / SQL 提取，MySQL 可连通且库表数据正确

## Excel 用例说明

文件路径：`data/测试用例.xlsx`  
第 2 行为表头，第 3 行起为用例数据。仅当 `is_True` 为真时才会执行。

| 字段 | 说明 |
|------|------|
| id | 用例编号 |
| feature / story / title | Allure 模块、场景、标题 |
| method | 请求方法，如 get / post |
| path | 接口路径，会拼到 `BASE_URL` 后 |
| headers / params / data / json / files | 请求参数（字符串写字典，运行时 `eval`） |
| check | JsonPath，用于定位响应字段；为空则用 `expected in 响应文本` |
| expected | HTTP 断言期望值 |
| sql_check / sql_expectted | 数据库断言 SQL 与期望值 |
| jsonExdata | JSON 提取，如 `{"TOKEN":"$..token"}` |
| sqlExdata | SQL 提取字段 |
| is_True | 是否执行该用例 |

跨用例传参示例：

1. 登录用例通过 `jsonExdata` 提取 `TOKEN`
2. 后续用例 headers 中写：`{"Authorization":"{{TOKEN}}"}`
3. 执行前用 Jinja2 渲染全局变量 `all`

## 快速开始

### 方式一：使用 run.py（推荐）

```bash
python3 run.py
```

会自动：

1. 执行指定测试文件（当前为 `testcase/test_runner_38.py`，可按需改成最新脚本）
2. 生成 pytest-html 报告到 `report/`
3. 生成 Allure 结果到 `allure-results/`，并输出 HTML 到对应目录下的 `html_report/`

### 方式二：直接用 pytest

```bash
# 执行某个测试文件
pytest -vs ./testcase/test_runner_40.py

# 同时生成 HTML + Allure 原始结果
pytest -vs ./testcase/test_runner_40.py \
  --html=./report/report.html \
  --alluredir=./allure-results/tmp
```

查看 Allure 报告：

```bash
allure open ./allure-results/<某次运行目录>/html_report
# 或
allure serve ./allure-results/<某次运行目录>
```

## 执行流程

以最新用例脚本为例（如 `testcase/test_runner_40.py`）：

```text
读取 Excel
  → Jinja2 渲染变量（all）
  → Allure 动态标注（feature / story / title）
  → 解析请求参数（analyse_case）
  → 发送 HTTP 请求（send_http_request）
  → HTTP 断言 / 数据库断言
  → JSON 提取 / SQL 提取，写回 all
```

## 常见问题

### 1. `sh: allure: command not found`

- 原因：Python 进程未继承 `.zshrc` 中的 PATH
- 处理：使用完整路径调用 Allure，或在 IDE Run Configuration 中配置 `PATH` / `ALLURE_HOME`

### 2. 读 Excel 得到 `{None: None}` 或字段为空

- 确认打开的是 `data/测试用例.xlsx`
- 确认第 2 行是表头、第 3 行起有数据且已保存
- 确认 `is_True` 列已勾选需要执行的用例

### 3. `KeyError` / 变量被覆盖

- 不要复用参数名覆盖整行用例字典（例如先 `data = case`，再 `data = eval(case["data"])`）
- 建议：Excel 行用 `case`，请求体用 `body`

### 4. 接口返回非 JSON 导致 `JSONDecodeError`

- 先确认服务是否启动、路径是否正确、鉴权是否有效
- 必要时先打印 `res.status_code` 与 `res.text` 排查

## 作者

@叶风磊
