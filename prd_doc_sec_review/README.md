# Word 文档智能审核系统

基于 AWS Bedrock 和 Claude AI 的专业文档安全审核工具，支持命令行和 Web 界面两种使用方式。

## 📋 项目简介

这是一个智能文档审核系统，专门用于从安全角度分析 PRD（产品需求文档）等 Word 文档。系统利用 AWS Bedrock 服务调用 Claude 4.5 系列模型，提供专业的文档安全分析和建议。

### 主要特性

- 🤖 **多模型支持**：支持 Claude 4.5 Opus、Sonnet、Haiku 三种模型
- 🌐 **双模式运行**：命令行工具和 Web 界面两种使用方式
- ⚡ **流式处理**：实时显示分析进度和结果
- 📊 **专业分析**：从安全角度深度分析文档内容
- 💾 **结果保存**：自动保存审核报告，支持下载
- 🎨 **友好界面**：现代化的 Web UI，支持拖拽上传

## 🚀 快速开始

### 环境要求

- Python 3.8+
- AWS 账号（需要配置 Bedrock 访问权限）
- AWS CLI 已配置凭证

### 安装依赖

```bash
cd prd_doc_sec_review
pip install -r requirements.txt
```

### AWS 配置

确保已配置 AWS 凭证，可以通过以下方式之一：

1. 使用 AWS CLI 配置：
```bash
aws configure
```

2. 设置环境变量：
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## 📖 使用方法

### 方式一：命令行工具

基本用法：

```bash
python prd_review.py <文档路径>
```

完整参数：

```bash
python prd_review.py prd_sample.docx \
  --region us-east-1 \
  --output result.txt \
  --prompt prompt2.txt
```

参数说明：
- `file_path`：Word 文档路径（必需，仅支持 .docx 格式）
- `--region`：AWS 区域（默认：us-east-1）
- `--output`：输出文件路径（可选，默认自动生成）
- `--prompt`：系统提示词文件路径（默认：prompt.txt）

### 方式二：Web 界面

1. 启动 Web 服务：

```bash
python web_app.py
```

2. 打开浏览器访问：

```
http://localhost:5000
```

3. 在 Web 界面中：
   - 选择或拖拽 Word 文档（.docx 格式）
   - 选择 AI 模型（Opus/Sonnet/Haiku）
   - 选择 AWS 区域
   - 点击"开始分析"按钮
   - 实时查看分析进度和结果
   - 下载审核报告

## 🎯 支持的模型

| 模型 | 模型 ID | 特点 | 适用场景 |
|------|---------|------|----------|
| Claude 4.5 Opus | `global.anthropic.claude-opus-4-5-20251101-v1:0` | 最强大 | 复杂文档深度分析 |
| Claude 4.5 Sonnet | `global.anthropic.claude-sonnet-4-5-20250929-v1:0` | 平衡性能 | 日常文档审核（推荐） |
| Claude 4.5 Haiku | `global.anthropic.claude-haiku-4-5-20251001-v1:0` | 快速响应 | 简单文档快速审核 |

## 📁 项目结构

```
prd_doc_sec_review/
├── prd_review.py           # 核心审核逻辑（命令行工具）
├── web_app.py              # Flask Web 应用
├── run_web.py              # Web 服务启动脚本
├── requirements.txt        # Python 依赖
├── prompt.txt              # 系统提示词（版本1）
├── prompt2.txt             # 系统提示词（版本2）
├── templates/
│   └── index.html          # Web 界面模板
├── uploads/                # 上传文件存储目录
├── results/                # 审核结果存储目录
└── prd_sample.docx         # 示例文档
```

## 🔧 配置说明

### 自定义提示词

系统提示词文件（`prompt.txt` 或 `prompt2.txt`）定义了 AI 的审核角度和输出格式。你可以根据需求修改提示词内容，例如：

- 调整审核重点（安全性、合规性、可行性等）
- 修改输出格式
- 添加特定领域的审核标准

### Web 应用配置

在 `web_app.py` 中可以修改以下配置：

```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大文件大小
app.config['UPLOAD_FOLDER'] = 'uploads'              # 上传目录
app.config['RESULTS_FOLDER'] = 'results'             # 结果目录
```

## 📊 输出示例

审核报告包含以下内容：

- 文档基本信息（文件名、大小、审核时间）
- 使用的 AI 模型信息
- 详细的安全分析结果
- 潜在风险点和建议
- 改进建议

## 🔒 安全注意事项

1. **凭证安全**：不要在代码中硬编码 AWS 凭证
2. **文件大小限制**：Web 应用默认限制 16MB，可根据需求调整
3. **数据隐私**：上传的文档会发送到 AWS Bedrock 进行处理
4. **访问控制**：生产环境建议添加身份验证机制

## 🛠️ 故障排查

### 常见问题

1. **AWS 凭证错误**
   - 检查 AWS CLI 配置：`aws configure list`
   - 确认 IAM 用户有 Bedrock 访问权限

2. **模型不可用**
   - 确认所选区域支持 Claude 4.5 模型
   - 检查 Bedrock 模型访问权限

3. **文件上传失败**
   - 确认文件格式为 .docx
   - 检查文件大小是否超过限制
   - 确保 uploads 目录有写入权限

4. **流式输出中断**
   - 检查网络连接稳定性
   - 查看服务器日志获取详细错误信息

## 📝 开发说明

### 扩展功能

1. **添加新模型**：在 `web_app.py` 的 `SUPPORTED_MODELS` 字典中添加
2. **自定义分析维度**：修改 `prompt.txt` 或 `prompt2.txt`
3. **添加新的输出格式**：修改 `DocumentReviewer.save_review_result()` 方法

### API 端点

Web 应用提供以下 API 端点：

- `POST /upload`：上传文档并开始分析
- `GET /status/<task_id>`：查询任务状态
- `GET /result/<task_id>`：获取分析结果
- `GET /download/<task_id>`：下载结果文件
- `GET /stream/<task_id>`：流式获取实时结果（SSE）

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请通过 Issue 反馈。
