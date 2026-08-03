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

## 运行参数

本框架支持通过 **命令行参数**、**环境变量**、**Jenkins 流水线参数** 三种方式控制运行行为，方便本地调试与 CI 集成。

### 1. `run.py` 命令行参数

`run.py` 已封装为 CLI，支持如下参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| `--env` | 指定运行环境，会覆盖 `config/environments.py` 中的默认 `ENV`，用于切换 `BASE_URL` | `--env prod` |
| `--excel-file` | 指定用例 Excel 文件名（仅传文件名，自动到 `data/` 下查找） | `--excel-file 用例集合.xlsx` |
| `--sheet-name` | 指定 Excel 中的 Sheet 名 | `--sheet-name Sheet1` |
| `--case` | 指定要执行的 pytest 测试脚本路径（默认最新版本 `testcase/test_runner_40.py`） | `--case ./testcase/test_runner_38.py` |

示例：

```bash
python3 run.py --env prod --excel-file 用例集合.xlsx --sheet-name 登录模块
```

> `--case` 一般用默认值即可，只有在需要对比跑历史脚本或新写脚本调试时再覆盖。

### 2. 环境变量

以下环境变量会被 `run.py` 读取，等价于命令行参数，**命令行参数优先级高于环境变量**：

| 变量名 | 含义 | 示例 |
|--------|------|------|
| `TEST_ENV` | 运行环境 | `export TEST_ENV=prod` |
| `TEST_EXCEL_FILE` | 用例 Excel 文件名 | `export TEST_EXCEL_FILE=用例集合.xlsx` |
| `TEST_SHEET_NAME` | Sheet 名 | `export TEST_SHEET_NAME=Sheet1` |

> 优先级：`命令行参数` > `环境变量` > `配置文件中的默认值`

Jenkinsfile 中已将这些变量声明为可配置参数，可直接在 Job 配置页修改。

### 3. 飞书推送参数（`utils/send_allure_to_feishu.py`）

单独运行飞书推送脚本时支持的参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| `--webhook` | 飞书机器人 webhook 地址 | `--webhook https://open.feishu.cn/...` |
| `--secret` | 飞书机器人加签密钥（开启签名校验时必填） | `--secret SECxxxxxx` |
| `--report-path` | Allure HTML 报告根目录 | `--report-path ./allure-results/tmp/html_report` |
| `--report-url` | 报告对外访问 URL，会以卡片链接形式发送给群 | `--report-url http://ci.xxx.com/job/test/123/allure` |
| `--at-all` | 是否 @所有人（加 `--at-all` 即开启） | `--at-all` |

示例：

```bash
python3 utils/send_allure_to_feishu.py \
  --webhook https://open.feishu.cn/open-apis/bot/v2/hook/xxxx \
  --secret SECxxxxxxxx \
  --report-path ./allure-results/tmp/html_report \
  --report-url http://ci.xxx.com/job/api-test/lastBuild/allure \
  --at-all
```

### 4. Jenkins 任务参数

项目自带 `jenkins.sh` 执行脚本，在 Jenkins Freestyle Job 中需手动在任务配置页添加以下参数（位于 `General > This project is parameterized`）：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `TEST_ENV` | Choice | 运行环境枚举（如 `dev / test / prod`），自动绑定到环境变量 |
| `TEST_EXCEL_FILE` | Choice | 用例 Excel 文件名枚举 |
| `TEST_SHEET_NAME` | Choice | Sheet 名枚举 |
| `FEISHU_WEBHOOK` | Secret text | 飞书机器人 webhook（在 Build Environment 中绑定为变量），**注意不要提交到代码仓库** |

构建时会自动：

1. Jenkins 把上述参数 export 为同名的环境变量
2. `jenkins.sh` 调用 `python3 run.py --env $TEST_ENV --excel-file $TEST_EXCEL_FILE --sheet-name $TEST_SHEET_NAME` 触发执行
3. 执行完调用 `python3 utils/send_allure_to_feishu.py` 把报告链接 @ 到飞书群

---

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
