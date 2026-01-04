from bedrock_agentcore.tools.code_interpreter_client import CodeInterpreter
from strands import Agent, tool
from strands.models import BedrockModel
import json
import pandas as pd
from typing import Dict, Any, List

# Initialize the Code Interpreter within a supported AWS region.
code_client = CodeInterpreter('ap-northeast-1')
code_client.start(session_timeout_seconds=1200)

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


def read_file(file_path: str) -> str:
    """Helper function to read file content with error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

data_file_content = read_file("data/data.csv")

files_to_create = [
                {
                    "path": "data.csv",
                    "text": data_file_content
                }]

def call_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to invoke sandbox tools

    Args:
        tool_name (str): Name of the tool to invoke
        arguments (Dict[str, Any]): Arguments to pass to the tool

    Returns:
        Dict[str, Any]: JSON formatted result
    """
    response = code_client.invoke(tool_name, arguments)
    for event in response["stream"]:
        return json.dumps(event["result"])

# Write files to sandbox
writing_files = call_tool("writeFiles", {"content": files_to_create})
print("Writing files result:")
print(writing_files)

# Verify files were created
listing_files = call_tool("listFiles", {"path": ""})
print("\nFiles in sandbox:")
print(listing_files)

SYSTEM_PROMPT = """You are a helpful AI assistant that validates all answers through code execution using the tools provided. DO NOT Answer questions without using the tools

VALIDATION PRINCIPLES:
1. When making claims about code, algorithms, or calculations - write code to verify them
2. Use execute_python to test mathematical calculations, algorithms, and logic
3. Create test scripts to validate your understanding before giving answers
4. Always show your work with actual code execution
5. If uncertain, explicitly state limitations and validate what you can

APPROACH:
- If asked about a programming concept, implement it in code to demonstrate
- If asked for calculations, compute them programmatically AND show the code
- If implementing algorithms, include test cases to prove correctness
- Document your validation process for transparency
- The sandbox maintains state between executions, so you can refer to previous results

TOOL AVAILABLE:
- execute_python: Run Python code and see output

RESPONSE FORMAT: The execute_python tool returns a JSON response with:
- sessionId: The sandbox session ID
- id: Request ID
- isError: Boolean indicating if there was an error
- content: Array of content objects with type and text/data
- structuredContent: For code execution, includes stdout, stderr, exitCode, executionTime

For successful code execution, the output will be in content[0].text and also in structuredContent.stdout.
Check isError field to see if there was an error.

Be thorough, accurate, and always validate your answers when possible."""


#Define and configure the code interpreter tool
@tool
def execute_python(code: str, description: str = "") -> str:
    """Execute Python code in the sandbox."""

    if description:
        code = f"# {description}\n{code}"

    #Print generated Code to be executed
    print(f"\n Generated Code: {code}")


    # Call the Invoke method and execute the generated code, within the initialized code interpreter session
    response = code_client.invoke("executeCode", {
        "code": code,
        "language": "python",
        "clearContext": False
    })
    for event in response["stream"]:
        return json.dumps(event["result"])


model_id="global.anthropic.claude-haiku-4-5-20251001-v1:0"
model= BedrockModel(model_id=model_id)

#configure the strands agent including the model and tool(s)
agent=Agent(
    model=model,
        tools=[execute_python],
        system_prompt=SYSTEM_PROMPT,
        callback_handler=None)

query = "Load the file 'data.csv' and perform exploratory data analysis(EDA) on it. Tell me about distributions and outlier values."

response_text = ""
r1 = agent(query)
print(r1)
print("Token 消耗情况：\n" + json.dumps(get_token_stats_from_trace(r1)))
    

query = "Within the file 'data.csv', how many individuals with the first name 'Kimberly' have 'Crocodile' as their favourite animal?"

response_text = ""
r2 = agent(query)
print(r2)
print("Token 消耗情况：\n" + json.dumps(get_token_stats_from_trace(r2)))