#!/usr/bin/env python3
"""
使用 Strands Agent SDK 分析 EC2 性能数据
演示：大模型生成代码 -> python_repl 运行 -> 大模型分析结果
"""

import os
import json
from strands import Agent
from strands_tools import calculator, file_read, shell, python_repl
from strands.models import BedrockModel

from strands.agent.conversation_manager import (
    NullConversationManager,
    SlidingWindowConversationManager,
    SummarizingConversationManager
)

sum_manager = SummarizingConversationManager(
    summary_ratio=0.3,
    preserve_recent_messages=2
)

slide_manager = SlidingWindowConversationManager(
    window_size=2
)

def event_loop_tracker(**kwargs):
    # Track event loop lifecycle
    complete = kwargs.get("complete", False)


    if "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
        print(f"\nUSING TOOL: {kwargs['current_tool_use']['name']}")
        print("type: ", kwargs.get("type"))
        print("request_state: ", kwargs.get("request_state"))
        


os.environ["BYPASS_TOOL_CONSENT"] = "true"

bedrock_model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    temperature=0.3)

system_prompt = """作为监控系统专家，仔细分析监控指标"""


def get_token_stats_from_trace(trace):
    """Extract token usage statistics from trace result."""
    stats = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_tokens": 0,
        "cache_read_tokens": 0,
        "total_tokens": 0
    }
    
    # Get metrics from trace
    if hasattr(trace, 'metrics'):
        metrics_summary = trace.metrics.get_summary()
        accumulated_usage = metrics_summary.get("accumulated_usage", {})
        
        stats["input_tokens"] = accumulated_usage.get("inputTokens", 0)
        stats["output_tokens"] = accumulated_usage.get("outputTokens", 0)
        stats["total_tokens"] = accumulated_usage.get("totalTokens", 0)
        
        # Check for cache tokens in the usage details
        if "cacheCreationInputTokens" in accumulated_usage:
            stats["cache_creation_tokens"] = accumulated_usage.get("cacheCreationInputTokens", 0)
        if "cacheReadInputTokens" in accumulated_usage:
            stats["cache_read_tokens"] = accumulated_usage.get("cacheReadInputTokens", 0)
    
    return stats


def analyze_ec2_metrics_file():
    """使用 Strands Agent 分析 EC2 性能数据"""
    
    print("=" * 70)
    print("Strands Agent File content 演示")
    print("分析 EC2 服务器性能数据")
    print("=" * 70)
    print()

    # 创建 Strands Agent（自动包含 python_repl tool）
    agent = Agent(
        model=bedrock_model,
        system_prompt=system_prompt,
        tools=[file_read, calculator],
        callback_handler=None
    )

    # 构建分析请求
    csv_file_name = 'data/ec2_metrics.csv'

    with open(csv_file_name, "rb") as fp:
        csv_bytes = fp.read()

    user_prompt = f"""
我有一份 EC2 服务器的性能监控数据（CSV 格式），请找出平均 CPU 使用率大于 75% 的机器
"""
    analysis_request = [
        {"text": user_prompt},
        {
            "document": {
                "format": "csv",
                "name": "ec2_metrics",
                "source": {
                    "bytes": csv_bytes
                }
            }
        }
    ]
    print("👤 用户请求:")
    print("-" * 70)
    print("分析 EC2 服务器性能数据...")
    print()
    
    print("🤖 Strands Agent 开始工作...\n")
    
    # 运行 Agent（自动处理工具调用循环）
    trace = agent(analysis_request)
    print("\n------------------\n🤖 Strands Agent 结果:")
    print(trace)
    stats = get_token_stats_from_trace(trace)
    print("------------------\n 📊 Token 使用统计:" + json.dumps(stats, indent=4))



def analyze_ec2_metrics_repl():
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
        tools=[python_repl, file_read, shell, calculator],
        callback_handler=None
    )

    # 构建分析请求
    csv_file_name = 'data/ec2_metrics.csv'
    analysis_request = f"""
我有一份 EC2 服务器的性能监控数据（CSV 格式），存储在{csv_file_name}，请找出平均 CPU 使用率大于 75% 的机器
"""
    print("👤 用户请求:")
    print("-" * 70)
    print("分析 EC2 服务器性能数据...")
    print()
    
    print("🤖 Strands Agent 开始工作...\n")
    
    # 运行 Agent（自动处理工具调用循环）
    trace = agent(analysis_request)
    

    print("\n------------------\n🤖 Strands Agent 结果:")
    print(trace)

    stats = get_token_stats_from_trace(trace)
    print("\n------------------\n📊 Token 使用统计:" + json.dumps(stats, indent=2))


if __name__ == "__main__":
    try:
        # analyze_ec2_metrics_repl()
        analyze_ec2_metrics_file()
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("\n请确保：")
        print("1. 已安装 Strands Agent SDK: pip install anthropic-strands")
        import traceback
        traceback.print_exc()
