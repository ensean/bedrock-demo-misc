# AWS Bedrock 多媒体分析脚本

使用 AWS Bedrock 上的 Nova 模型分析视频和图片内容。

## ⚠️ 重要提示

**视频分析当前状态**：
- ✅ **图片分析**：完全可用，支持单张和多张图片
- ⚠️ **视频分析**：需要使用 S3 引用方式（见下方说明）

直接传递视频字节数据到 Converse API 会返回 `ValidationException` 错误。请使用 `analyze_video_s3.py` 脚本通过 S3 引用方式分析视频。

详细信息请查看 [VIDEO_ANALYSIS_STATUS.md](VIDEO_ANALYSIS_STATUS.md)

## 安装依赖

```bash
pip install -r requirements.txt
```

## AWS 配置

确保已配置 AWS 凭证，可以通过以下方式之一：

1. AWS CLI 配置：
```bash
aws configure
```

2. 环境变量：
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

3. IAM 角色（如果在 EC2 或 Lambda 上运行）

## 使用方法

### 基本使用

#### 分析视频

```python
from analyze_video import MediaAnalyzer

# 初始化分析器（使用 Converse API）
# 支持视频的模型: amazon.nova-lite-v1:0, amazon.nova-pro-v1:0
analyzer = MediaAnalyzer(
    region_name="us-east-1",
    model_id="amazon.nova-lite-v1:0"
)

# 分析视频
response = analyzer.analyze_video(
    video_path="your_video.mp4",
    prompt="请描述视频内容",
    max_tokens=2048,
    temperature=0.7,
    top_p=0.9
)

# 获取结果
result = analyzer.extract_text_response(response)
print(result)

# 获取 token 使用信息
usage = analyzer.get_usage_info(response)
print(f"使用了 {usage['total_tokens']} tokens")
```

#### 分析单张图片

```python
from analyze_video import MediaAnalyzer

# 可以使用任何支持图片的模型
analyzer = MediaAnalyzer(
    region_name="us-east-1",
    model_id="amazon.nova-lite-v1:0"
)

# 分析图片
response = analyzer.analyze_image(
    image_path="your_image.jpg",
    prompt="请描述这张图片的内容"
)

result = analyzer.extract_text_response(response)
print(result)
```

#### 分析多张图片

```python
from analyze_video import MediaAnalyzer

analyzer = MediaAnalyzer(region_name="us-east-1")

# 分析多张图片
response = analyzer.analyze_multiple_images(
    image_paths=["image1.jpg", "image2.jpg", "image3.jpg"],
    prompt="请比较这些图片的异同"
)

result = analyzer.extract_text_response(response)
print(result)
```

### 运行示例脚本

#### 图片分析（推荐，完全可用）

```bash
# 分析单张图片
python analyze_video.py image

# 分析多张图片
python analyze_video.py images
```

#### 视频分析（需要 S3）

```bash
# 使用 S3 引用方式分析视频
python analyze_video_s3.py <bucket_name> <video_path>

# 示例
python analyze_video_s3.py my-bedrock-bucket /path/to/video.mp4
```

**前提条件**：
1. 创建一个 S3 bucket
2. 确保 IAM 角色有 S3 和 Bedrock 权限
3. 视频会自动上传到 S3，分析后自动删除

注意：需要修改脚本中的文件路径为实际的图片或视频文件路径。

## 支持的格式

### 视频格式
- MP4
- MOV
- AVI
- MKV
- WebM

### 图片格式
- JPEG / JPG
- PNG
- GIF
- WebP
- BMP

## 自定义提示词示例

### 视频分析

```python
# 场景识别
prompt = "识别视频中的主要场景和环境"

# 动作检测
prompt = "描述视频中人物的动作和行为"

# 物体识别
prompt = "列出视频中出现的所有物体"

# 综合分析
prompt = "详细分析视频内容，包括场景、人物、动作、情感和关键事件"
```

### 图片分析

```python
# 物体识别
prompt = "识别图片中的所有物体并标注位置"

# 场景理解
prompt = "描述图片的场景、氛围和情感"

# OCR 文字识别
prompt = "提取图片中的所有文字内容"

# 图片比较
prompt = "比较这些图片的相似之处和不同之处"

# 详细描述
prompt = "详细描述图片内容，包括前景、背景、颜色、光线和构图"
```

## 支持的模型

### 视频分析模型
- `amazon.nova-lite-v1:0` - 轻量级，快速，成本低
- `amazon.nova-pro-v1:0` - 专业级，更高精度
- `amazon.nova-micro-v1:0` - 微型模型，超快速

### 图片分析模型
- 所有 Nova 系列模型
- `anthropic.claude-3-*` 系列
- `us.anthropic.claude-3-*` 系列

## API 说明

脚本使用 AWS Bedrock 的 **Converse API**，这是推荐的多模态内容处理方式：

- 统一的 API 接口，支持文本、图像和视频
- 自动处理不同模型的格式差异
- 更好的错误处理和响应结构
- 支持流式和非流式响应

**重要提示**: 
- 视频分析需要使用支持视频的模型（如 Nova 系列）
- 消息格式：文本提示在前，媒体内容在后

## 注意事项

- 确保有足够的 AWS Bedrock 访问权限
- 视频文件大小限制：最大 25MB
- 图片文件大小限制：建议小于 5MB
- 较大的视频文件可能需要较长的处理时间
- 确保在支持相应模型的 AWS 区域运行（如 us-east-1）
- Converse API 需要 boto3 版本 >= 1.34.0
- 多图片分析时，建议不超过 10 张图片以获得最佳性能
- 视频分析仅支持 Nova 系列模型
- 消息格式很重要：文本提示必须在媒体内容之前

## 常见问题

### ValidationException: Malformed input request

如果遇到此错误：

**对于视频分析**：
- ❌ 直接传递视频字节数据当前不可用
- ✅ 使用 `analyze_video_s3.py` 脚本通过 S3 引用
- ✅ 或者提取视频帧作为图片分析

**对于图片分析**：
1. 检查图片格式是否支持（jpeg, png, gif, webp）
2. 检查图片大小是否小于 5MB
3. 确保使用正确的模型 ID

### 如何选择模型

- **快速测试**: `amazon.nova-lite-v1:0` ✅
- **高精度**: `amazon.nova-pro-v1:0` ✅
- **图片专用**: `anthropic.claude-3-sonnet-20240229-v1:0` ✅

### 视频分析替代方案

1. **S3 引用方式**（推荐）：
   ```bash
   python analyze_video_s3.py my-bucket video.mp4
   ```

2. **视频帧提取**：
   ```python
   # 提取关键帧作为图片分析
   import cv2
   # ... 提取帧代码
   analyzer.analyze_multiple_images(frames, "分析这些视频帧")
   ```

3. **使用 Amazon Rekognition Video**：
   专门的视频分析服务
