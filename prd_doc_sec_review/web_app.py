#!/usr/bin/env python3
"""
Word文档审核Web应用
基于Flask提供Web界面，支持模型选择和文档上传
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, Response
from werkzeug.utils import secure_filename
import threading
import queue
import time

from prd_review import DocumentReviewer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保上传和结果目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# 支持的模型列表
SUPPORTED_MODELS = {
    'claude-4-5-opus': {
        'id': 'global.anthropic.claude-opus-4-5-20251101-v1:0',
        'name': 'Claude 4.5 Opus',
        'description': '最强大的Claude 4.5 Opus模型，适合最复杂的文档分析任务'
    },
    'claude-4-5-sonnet': {
        'id': 'global.anthropic.claude-sonnet-4-5-20250929-v1:0',
        'name': 'Claude 4.5 Sonnet',
        'description': 'Claude 4.5 Sonnet模型，平衡性能、速度和成本的最佳选择'
    },
    'claude-4-5-haiku': {
        'id': 'global.anthropic.claude-haiku-4-5-20251001-v1:0',
        'name': 'Claude 4.5 Haiku',
        'description': 'Claude 4.5 Haiku模型，快速响应，适合简单文档分析'
    }
}

# 全局任务状态存储
task_status = {}
task_results = {}

class StreamingDocumentReviewer(DocumentReviewer):
    """扩展DocumentReviewer以支持Web流式输出"""
    
    def __init__(self, region_name: str = 'us-east-1', prompt_file: str = 'prompt.txt', model_id: str = None):
        super().__init__(region_name, prompt_file)
        if model_id:
            self.model_id = model_id
    
    def review_document_streaming(self, file_path: str, task_id: str):
        """
        流式审核文档，更新任务状态
        """
        try:
            task_status[task_id] = {'status': 'processing', 'progress': 0, 'message': '正在读取文档...'}
            
            # 检查文件格式
            if not file_path.lower().endswith('.docx'):
                raise ValueError("仅支持 .docx 格式的文档")
            
            # 读取文档
            document_bytes = self._read_document(file_path)
            file_size = Path(file_path).stat().st_size
            
            task_status[task_id] = {'status': 'processing', 'progress': 20, 'message': '正在调用AI模型...'}
            
            # 调用流式API
            response = self.bedrock_client.converse_stream(
                modelId=self.model_id,
                messages=[
                    {
                        "role": "assistant",
                        "content": [{"text": self.system_prompt}]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "document": {
                                    "format": "docx",
                                    "name": "document",
                                    "source": {"bytes": document_bytes}
                                }
                            },
                            {"text": "从安全角度分析下这个需求文档"}
                        ]
                    }
                ],
                inferenceConfig={
                    "maxTokens": 8000,
                    "temperature": 0.6
                }
            )
            
            # 处理流式响应
            full_response = ""
            task_status[task_id] = {'status': 'processing', 'progress': 40, 'message': '正在生成分析报告...'}
            
            for event in response['stream']:
                if 'contentBlockDelta' in event:
                    delta = event['contentBlockDelta']['delta']
                    if 'text' in delta:
                        chunk = delta['text']
                        full_response += chunk
                        # 更新进度
                        progress = min(90, 40 + len(full_response) // 50)
                        task_status[task_id] = {
                            'status': 'processing', 
                            'progress': progress, 
                            'message': '正在生成分析报告...',
                            'partial_result': full_response
                        }
                elif 'messageStop' in event:
                    break
            
            # 保存结果
            result = {
                "status": "success",
                "file_path": file_path,
                "file_size": file_size,
                "review_result": full_response,
                "model_used": self.model_id,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 保存到文件
            result_file = os.path.join(app.config['RESULTS_FOLDER'], f"{task_id}_result.txt")
            self.save_review_result(result, result_file)
            
            task_status[task_id] = {'status': 'completed', 'progress': 100, 'message': '分析完成'}
            task_results[task_id] = result
            
        except Exception as e:
            task_status[task_id] = {'status': 'error', 'progress': 0, 'message': str(e)}
            task_results[task_id] = {"status": "error", "error": str(e)}

@app.route('/')
def index():
    """主页"""
    return render_template('index.html', models=SUPPORTED_MODELS)

@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if not file.filename.lower().endswith('.docx'):
            return jsonify({'error': '仅支持.docx格式文件'}), 400
        
        # 获取其他参数
        model_key = request.form.get('model', 'claude-4-5-sonnet')
        region = request.form.get('region', 'us-east-1')
        
        if model_key not in SUPPORTED_MODELS:
            return jsonify({'error': '不支持的模型'}), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        task_id = str(uuid.uuid4())
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{task_id}_{filename}")
        file.save(file_path)
        
        # 创建审核器
        model_id = SUPPORTED_MODELS[model_key]['id']
        reviewer = StreamingDocumentReviewer(region_name=region, model_id=model_id, prompt_file="prompt2.txt")
        
        # 启动后台任务
        thread = threading.Thread(
            target=reviewer.review_document_streaming,
            args=(file_path, task_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'filename': filename,
            'model': SUPPORTED_MODELS[model_key]['name']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status/<task_id>')
def get_status(task_id):
    """获取任务状态"""
    if task_id not in task_status:
        return jsonify({'error': '任务不存在'}), 404
    
    return jsonify(task_status[task_id])

@app.route('/result/<task_id>')
def get_result(task_id):
    """获取任务结果"""
    if task_id not in task_results:
        return jsonify({'error': '结果不存在'}), 404
    
    return jsonify(task_results[task_id])

@app.route('/download/<task_id>')
def download_result(task_id):
    """下载结果文件"""
    result_file = os.path.join(app.config['RESULTS_FOLDER'], f"{task_id}_result.txt")
    if not os.path.exists(result_file):
        return jsonify({'error': '文件不存在'}), 404
    
    return send_file(result_file, as_attachment=True, download_name=f"review_result_{task_id}.txt")

@app.route('/stream/<task_id>')
def stream_result(task_id):
    """流式获取结果"""
    def generate():
        last_length = 0
        while task_id in task_status:
            status = task_status[task_id]
            if 'partial_result' in status:
                current_result = status['partial_result']
                if len(current_result) > last_length:
                    new_content = current_result[last_length:]
                    yield f"data: {json.dumps({'type': 'content', 'data': new_content})}\n\n"
                    last_length = len(current_result)
            
            if status['status'] in ['completed', 'error']:
                yield f"data: {json.dumps({'type': 'status', 'data': status})}\n\n"
                break
            
            time.sleep(1)
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)