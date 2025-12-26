#!/usr/bin/env python3
"""
使用 Strands Agent SDK 分析 EC2 性能数据
演示：大模型生成代码 -> python_repl 运行 -> 大模型分析结果
"""

import os
from strands import Agent
from strands_tools import calculator, file_read, shell, python_repl
from strands.models import BedrockModel

os.environ["BYPASS_TOOL_CONSENT"] = "true"

bedrock_model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    temperature=0.3)

system_prompt = """你是一个数据分析专家，擅长使用 Python 和 pandas 分析数据。
当需要分析数据时，你会：
1. 读取部分文件，分析文件数据结构
2. 根据分析任务生成 python 代码，如有必要可使用 pandas 库，使用 python_repl 工具执行代码获取结果
2. 分析执行结果
3. 提供清晰的数据洞察和建议"""


def analyze_ec2_metrics():
    """使用 Strands Agent 分析 EC2 性能数据"""
    
    print("=" * 70)
    print("Strands Agent Python REPL 演示")
    print("分析 EC2 服务器性能数据")
    print("=" * 70)
    print()

    # 创建 Strands Agent（自动包含 python_repl tool）
    agent = Agent(
        model=bedrock_model,
        system_prompt=system_prompt,
        tools=[python_repl, file_read, shell, calculator]
    )

    # 构建分析请求
    csv_file_name = 'data/ec2_metrics.csv'
    analysis_request = f"""
我有一份 EC2 服务器的性能监控数据（CSV 格式），存储在{csv_file_name}：
请执行以下分析：
1. 使用 pandas 加载数据
2. 显示数据的基本信息（行数、列数、数据类型）
3. 计算每个实例的平均 CPU、内存、磁盘使用率
4. 找出资源使用率最高的 TOP 3 实例
5. 识别存在性能风险的实例（CPU > 90% 或 内存 > 85%）
6. 生成分析报告和优化建议
"""
    print("👤 用户请求:")
    print("-" * 70)
    print("分析 EC2 服务器性能数据...")
    print()
    
    print("🤖 Strands Agent 开始工作...\n")
    
    # 运行 Agent（自动处理工具调用循环）
    agent(analysis_request)
    


if __name__ == "__main__":
    try:
        analyze_ec2_metrics()
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("\n请确保：")
        print("1. 已安装 Strands Agent SDK: pip install anthropic-strands")
        import traceback
        traceback.print_exc()
