# Strands Python REPL 分析演示

使用 Strands Agent SDK 分析 EC2 性能数据的演示项目。

## 功能说明

本项目演示了如何使用 Strands Agent SDK 让 AI 自动分析 EC2 服务器性能监控数据，支持两种分析模式：

- **REPL 模式**：Agent 使用 Python REPL 工具动态生成并执行代码来分析数据
- **File 模式**：直接将 CSV 文件内容作为文档传递给 Agent 进行分析

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 默认运行（REPL 模式）

```bash
python demo_strands_ana_file.py
```

### 指定运行模式

```bash
# 使用 REPL 模式（Agent 动态执行 Python 代码）
python demo_strands_ana_file.py --mode repl
Token 使用统计:{
  "input_tokens": 78929,
  "output_tokens": 6113,
  "cache_creation_tokens": 0,
  "cache_read_tokens": 0,
  "total_tokens": 85042
}


# 使用 File 模式（直接传递文件内容）
python demo_strands_ana_file.py --mode file
Token 使用统计:{
    "input_tokens": 617568,
    "output_tokens": 5344,
    "cache_creation_tokens": 0,
    "cache_read_tokens": 0,
    "total_tokens": 622912
}

```

### 查看帮助

```bash
python demo_strands_ana_file.py --help
```

## 参数说明

- `--mode`: 选择分析模式
  - `repl` (默认): 使用 Python REPL 工具，Agent 可以动态生成和执行代码
  - `file`: 直接将 CSV 文件作为文档传递给 Agent

## 数据文件

确保 `data/ec2_metrics.csv` 文件存在，该文件包含 EC2 服务器的性能监控数据。

## 工作流程

1. 用户提供分析需求（例如：找出 CPU 使用率大于 75% 的机器）
2. Strands Agent 接收请求
3. Agent 自动选择合适的工具（python_repl、file_read 等）
4. Agent 生成并执行分析代码
5. 返回分析结果和 Token 使用统计

## 环境变量

- `BYPASS_TOOL_CONSENT`: 设置为 `true` 以跳过工具使用确认

## 依赖项

- strands-agents: Strands Agent SDK
- strands-agents-tools: Strands 工具集
- pandas: 数据分析库
- python-dotenv: 环境变量管理

## 注意事项

- 需要配置 AWS Bedrock 访问权限
- 使用的模型：`global.anthropic.claude-sonnet-4-5-20250929-v1:0`
- 确保有足够的 Bedrock API 配额
