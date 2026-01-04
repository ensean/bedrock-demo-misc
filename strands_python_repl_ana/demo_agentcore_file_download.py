#!/usr/bin/env python3
"""
演示如何从 CodeInterpreter 沙箱下载生成的文件
"""

from bedrock_agentcore.tools.code_interpreter_client import CodeInterpreter
import json
import base64
from typing import Dict, Any, List, Optional

# 初始化 CodeInterpreter
code_client = CodeInterpreter('ap-northeast-1')
code_client.start(session_timeout_seconds=1200)


def call_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """调用沙箱工具"""
    response = code_client.invoke(tool_name, arguments)
    for event in response["stream"]:
        return event["result"]


def download_file(file_path: str, local_path: Optional[str] = None) -> Optional[bytes]:
    """
    从 CodeInterpreter 沙箱下载文件
    
    Args:
        file_path: 沙箱中的文件路径
        local_path: 本地保存路径（可选）
    
    Returns:
        文件内容（bytes），如果失败返回 None
    """
    print(f"\n📥 正在下载文件: {file_path}")
    
    # 方法 1: 使用 readFiles API
    result = call_tool("readFiles", {"paths": [file_path]})
    
    if result.get("isError"):
        print(f"❌ 读取失败: {result.get('content', [{}])[0].get('text', 'Unknown error')}")
        return None
    
    # 解析返回的内容
    content = result.get("content", [])
    if not content:
        print("❌ 文件内容为空")
        return None
    
    file_data = content[0].get("resource")
    file_type = file_data.get("mimeType")
    file_content = None
    
    # 根据内容类型处理
    if file_type == "text/csv" or file_type == "application/json":
        # 文本文件
        file_content = file_data.get("text", "").encode('utf-8')
    elif file_type == "image/png":
        # 二进制文件（base64 编码）
        file_content = file_data.get("blob", "")
    else:
        print(f"⚠️ 未知文件类型: {file_type}")
        file_content = str(file_data).encode('utf-8')
    
    # 保存到本地
    if local_path and file_content:
        with open(local_path, 'wb') as f:
            f.write(file_content)
        print(f"✅ 文件已保存到: {local_path} ({len(file_content)} bytes)")
    
    return file_content


def list_files(path: str = "") -> List[Dict[str, str]]:
    """
    列出沙箱中的文件
    
    Returns:
        List[Dict]: 文件信息列表，每个字典包含:
            - name: 文件名
            - type: 'file' 或 'directory'
            - uri: 文件 URI
            - mimeType: MIME 类型（仅文件）
    """
    result = call_tool("listFiles", {"path": path})
    
    if result.get("isError"):
        print(f"❌ 列出文件失败: {result}")
        return []
    
    content = result.get("content", [])
    files = []
    
    for item in content:
        if item.get("type") == "resource_link":
            file_info = {
                "name": item.get("name", ""),
                "uri": item.get("uri", ""),
                "description": item.get("description", ""),
                "mimeType": item.get("mimeType", "")
            }
            
            # 判断是文件还是目录
            if item.get("description") == "Directory":
                file_info["type"] = "directory"
            else:
                file_info["type"] = "file"
            
            files.append(file_info)
    
    return files


def execute_code(code: str) -> Dict[str, Any]:
    """在沙箱中执行代码"""
    print(f"\n🐍 执行代码:\n{code}\n")
    result = call_tool("executeCode", {
        "code": code,
        "language": "python",
        "clearContext": False
    })
    
    if result.get("isError"):
        print(f"❌ 执行失败: {result}")
    else:
        # 打印输出
        structured = result.get("structuredContent", {})
        stdout = structured.get("stdout", "")
        stderr = structured.get("stderr", "")
        
        if stdout:
            print(f"📤 输出:\n{stdout}")
        if stderr:
            print(f"⚠️ 错误:\n{stderr}")
    
    return result


# ============================================================
# 示例 1: 生成 CSV 文件并下载
# ============================================================
print("=" * 70)
print("示例 1: 生成 CSV 文件并下载")
print("=" * 70)

# 在沙箱中生成一个 CSV 文件
code = """
import pandas as pd

# 创建示例数据
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'Age': [25, 30, 35, 40, 45],
    'City': ['New York', 'London', 'Paris', 'Tokyo', 'Sydney'],
    'Score': [85, 92, 78, 88, 95]
}

df = pd.DataFrame(data)

# 保存为 CSV
df.to_csv('output_report.csv', index=False)
print(f"CSV 文件已生成，包含 {len(df)} 行数据")
print(df.head())
"""

execute_code(code)

# 列出文件
print("\n📁 沙箱中的文件:")
files = list_files()
for f in files:
    icon = "📁" if f["type"] == "directory" else "📄"
    mime = f" ({f['mimeType']})" if f['mimeType'] else ""
    print(f"  {icon} {f['name']}{mime}")

# 下载文件（只下载文件，不下载目录）
csv_files = [f for f in files if f["type"] == "file" and f["name"].endswith('.csv')]
if csv_files:
    download_file('output_report.csv', 'local_output_report.csv')
else:
    print("⚠️ 未找到 output_report.csv 文件")


# ============================================================
# 示例 2: 生成图表并下载
# ============================================================
print("\n" + "=" * 70)
print("示例 2: 生成图表（PNG）并下载")
print("=" * 70)

code = """
import matplotlib.pyplot as plt
import numpy as np

# 生成数据
x = np.linspace(0, 10, 100)
y = np.sin(x)

# 创建图表
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2)
plt.title('Sine Wave')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)

# 保存图表
plt.savefig('sine_wave.png', dpi=150, bbox_inches='tight')
print("图表已保存为 sine_wave.png")
"""

execute_code(code)

# 下载图表
download_file('sine_wave.png', 'local_sine_wave.png')


# ============================================================
# 示例 3: 生成 JSON 文件并下载
# ============================================================
print("\n" + "=" * 70)
print("示例 3: 生成 JSON 文件并下载")
print("=" * 70)

code = """
import json

# 创建数据
data = {
    'project': 'CodeInterpreter Demo',
    'version': '1.0',
    'features': ['file_upload', 'code_execution', 'file_download'],
    'stats': {
        'total_files': 3,
        'total_size_mb': 1.5
    }
}

# 保存为 JSON
with open('metadata.json', 'w') as f:
    json.dump(data, f, indent=2)

print("JSON 文件已生成")
print(json.dumps(data, indent=2))
"""

execute_code(code)

# 下载并显示内容
content = download_file('metadata.json', 'local_metadata.json')
if content:
    print(f"\n📄 JSON 内容:\n{content.decode('utf-8')}")


# ============================================================
# 示例 4: 批量下载文件
# ============================================================
print("\n" + "=" * 70)
print("示例 4: 批量下载所有生成的文件")
print("=" * 70)

# 列出所有文件
all_files = list_files()
print(f"\n找到 {len(all_files)} 个项目")

# 只下载文件（不下载目录）
downloadable_files = [f for f in all_files if f["type"] == "file"]
print(f"其中 {len(downloadable_files)} 个是文件\n")

# 下载所有文件
for file_info in downloadable_files:
    filename = file_info["name"]
    mime_type = file_info.get("mimeType", "")
    
    # 只下载我们生成的文件（跳过系统文件）
    if any(filename.endswith(ext) for ext in ['.csv', '.png', '.json', '.txt', '.xlsx']):
        print(f"📥 下载: {filename} ({mime_type})")
        download_file(filename, f'downloaded_{filename}')
    else:
        print(f"⏭️  跳过: {filename}")


print("\n" + "=" * 70)
print("✅ 所有示例完成！")
print("=" * 70)
