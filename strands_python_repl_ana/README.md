# Strands Python REPL 分析演示

使用 Strands Agent SDK 分析 EC2 性能数据的演示项目。

## 功能说明

本项目演示了如何使用 Strands Agent SDK 让 AI 自动分析 EC2 服务器性能监控数据，支持两种分析模式：

- `demos_strands_ana_file.py`
  - **REPL 模式**：Agent 使用 Python REPL 工具动态生成并执行代码来分析数据
  - **File 模式**：直接将 CSV 文件内容作为文档传递给 Agent 进行分析

- `demos_strands_ana_agentcore.py`
  - **AgentCore CodeInterpreter 模式**: Agent 使用 CodeInterpreter 沙箱环境运行代码分析数据

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
python demo_strands_ana_file.py --mode repl # 计算结果准确，token 消耗低

#### **【问题2】平均 CPU 使用率 Top 3 的机器**

🏆 **第1名：i-4e5f6g7h8i9j0k1l2**
- 平均CPU使用率：**59.46%**
- CPU使用率范围：20.0% - 94.6%
- 超过75%的时间占比：30.2%

🥈 **第2名：i-2c3d4e5f6g7h8i9j0**
- 平均CPU使用率：**59.45%**
- CPU使用率范围：21.3% - 94.7%
- 超过75%的时间占比：29.0%

🥉 **第3名：i-3d4e5f6g7h8i9j0k1**
- 平均CPU使用率：**58.21%**
- CPU使用率范围：20.1% - 94.6%
- 超过75%的时间占比：31.0%

Token 使用统计:{
  "input_tokens": 78929,
  "output_tokens": 6113,
  "cache_creation_tokens": 0,
  "cache_read_tokens": 0,
  "total_tokens": 85042
}

# 使用 REPL 模式，同时开启 tools cache

 python demo_strands_ana_file.py --mode repl --cache_tools
🤖 Strands Agent 结果:
## 📊 EC2 服务器性能监控分析结果

我已经完成了对EC2服务器性能监控数据的详细分析，以下是关键发现：

### 🎯 问题1：平均 CPU 使用率 > 75% 的机器

**❌ 没有找到平均CPU使用率大于75%的机器**

所有5台机器的平均CPU使用率都在 **55.1% ~ 59.46%** 之间，均未超过75%的阈值。

---

### 🏆 问题2：平均 CPU 使用率 Top 3 的机器

| 排名 | 实例 ID | 平均CPU | 最小CPU | 最大CPU | 采样次数 |
|------|---------|---------|---------|---------|----------|
| **🥇 Top 1** | i-4e5f6g7h8i9j0k1l2 | **59.46%** | 20.0% | 94.6% | 199次 |
| **🥈 Top 2** | i-2c3d4e5f6g7h8i9j0 | **59.45%** | 21.3% | 94.7% | 200次 |
| **🥉 Top 3** | i-3d4e5f6g7h8i9j0k1 | **58.21%** | 20.1% | 94.6% | 200次 |

---

### 🔍 关键发现

1. **瞬时高峰频繁**：虽然平均CPU不高，但所有5台机器都出现过瞬时CPU超过75%的情况，总共发生了 **284次** CPU峰值事件

2. **负载波动大**：所有机器的CPU使用率波动范围都很大（20% ~ 95%），说明业务负载变化较大

3. **Top 3差异小**：前三名机器的平均CPU使用率非常接近，差异小于2%

---

### 💡 专业建议

1. **监控告警**：建议设置CPU使用率告警阈值为80%，及时响应高负载情况
2. **自动扩展**：为Top 3机器配置自动扩展策略，应对负载高峰
3. **根因分析**：深入分析CPU突增的时段和原因，优化资源调度
4. **容量规划**：虽然平均值不高，但考虑到频繁的峰值，建议预留足够的容量缓冲

---

### 📈 可视化报告

我已经生成了包含以下内容的详细可视化报告（**ec2_cpu_analysis_report.png**）：
- 各实例平均CPU使用率对比图
- Top 3实例CPU使用率分布箱线图
- Top 3实例CPU使用率时间序列图
- 监控统计摘要表

分析完成！如需进一步分析其他指标（如内存、磁盘使用率）或特定时间段的数据，请随时告诉我。

📊 Token 使用统计:{
  "input_tokens": 57844,
  "output_tokens": 5449,
  "cache_write_tokens": 3441,
  "cache_read_tokens": 27528,
  "total_tokens": 94262
}


# 使用 File 模式（直接传递文件内容）
python demo_strands_ana_file.py --mode file # 计算结果不准确，token 消耗高

 排名 | 实例ID | 平均CPU使用率 | 状态评估 |
|------|--------|--------------|----------|
| 🥇 **第1名** | **i-4e5f6g7h8i9j0k1l2** | **61.27%** | ⚠️ 中等负载 |
| 🥈 **第2名** | **i-2c3d4e5f6g7h8i9j0** | **60.45%** | ⚠️ 中等负载 |
| 🥉 **第3名** | **i-0a1b2c3d4e5f6g7h8** | **59.88%** | ⚠️ 中等负载 |

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
