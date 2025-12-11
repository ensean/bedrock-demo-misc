#!/usr/bin/env python3
"""
使用 S3 引用方式分析视频 - AWS Bedrock Nova 模型
"""

import boto3
import json
from pathlib import Path
import time


class VideoAnalyzerS3:
    def __init__(self, region_name="us-east-1", model_id="amazon.nova-lite-v1:0", bucket_name=None):
        """
        初始化分析器
        
        Args:
            region_name: AWS 区域
            model_id: 模型 ID
            bucket_name: S3 bucket 名称
        """
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name
        )
        self.s3_client = boto3.client('s3', region_name=region_name)
        self.model_id = model_id
        self.bucket_name = bucket_name
        self.region_name = region_name
    
    def upload_video_to_s3(self, video_path, s3_key=None):
        """
        上传视频到 S3
        
        Args:
            video_path: 本地视频文件路径
            s3_key: S3 对象键（可选，默认使用文件名）
            
        Returns:
            S3 URI
        """
        if not self.bucket_name:
            raise ValueError("需要指定 bucket_name")
        
        if s3_key is None:
            s3_key = f"videos/{Path(video_path).name}"
        
        print(f"正在上传视频到 S3...")
        print(f"  Bucket: {self.bucket_name}")
        print(f"  Key: {s3_key}")
        
        self.s3_client.upload_file(video_path, self.bucket_name, s3_key)
        
        s3_uri = f"s3://{self.bucket_name}/{s3_key}"
        print(f"✅ 上传成功: {s3_uri}")
        
        return s3_uri
    
    def analyze_video_from_s3(self, s3_uri, prompt="请详细描述这个视频的内容", max_tokens=2048, temperature=0.7, top_p=0.9):
        """
        使用 S3 URI 分析视频
        
        Args:
            s3_uri: S3 URI (s3://bucket/key)
            prompt: 分析提示词
            max_tokens: 最大生成 token 数
            temperature: 温度参数
            top_p: Top-p 采样参数
            
        Returns:
            模型的分析结果
        """
        print(f"\n正在分析视频: {s3_uri}")
        print(f"使用模型: {self.model_id}")
        
        # 从 S3 URI 提取格式
        video_format = Path(s3_uri).suffix.lstrip(".").lower()
        if not video_format:
            video_format = "mp4"
        
        # 构建消息
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "video": {
                            "format": video_format,
                            "source": {
                                "s3Location": {
                                    "uri": s3_uri
                                }
                            }
                        }
                    },
                    {
                        "text": prompt
                    }
                ]
            }
        ]
        
        # 推理配置
        inference_config = {
            "maxTokens": max_tokens,
            "temperature": temperature,
            "topP": top_p
        }
        
        try:
            response = self.bedrock_runtime.converse(
                modelId=self.model_id,
                messages=messages,
                inferenceConfig=inference_config
            )
            return response
        except Exception as e:
            print(f"❌ 调用失败: {e}")
            raise
    
    def analyze_video(self, video_path, prompt="请详细描述这个视频的内容", max_tokens=2048, temperature=0.7, top_p=0.9, cleanup=True):
        """
        分析本地视频文件（自动上传到 S3）
        
        Args:
            video_path: 本地视频文件路径
            prompt: 分析提示词
            max_tokens: 最大生成 token 数
            temperature: 温度参数
            top_p: Top-p 采样参数
            cleanup: 分析后是否删除 S3 上的视频
            
        Returns:
            模型的分析结果
        """
        # 上传到 S3
        s3_key = f"temp-videos/{int(time.time())}-{Path(video_path).name}"
        s3_uri = self.upload_video_to_s3(video_path, s3_key)
        
        try:
            # 分析视频
            response = self.analyze_video_from_s3(
                s3_uri=s3_uri,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )
            
            return response
        finally:
            # 清理 S3 文件
            if cleanup:
                try:
                    self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
                    print(f"✅ 已清理 S3 临时文件")
                except Exception as e:
                    print(f"⚠️  清理 S3 文件失败: {e}")
    
    def extract_text_response(self, response):
        """提取响应文本"""
        try:
            return response["output"]["message"]["content"][0]["text"]
        except (KeyError, IndexError, TypeError) as e:
            print(f"解析响应时出错: {e}")
            return None
    
    def get_usage_info(self, response):
        """获取 token 使用信息"""
        try:
            usage = response.get("usage", {})
            return {
                "input_tokens": usage.get("inputTokens", 0),
                "output_tokens": usage.get("outputTokens", 0),
                "total_tokens": usage.get("totalTokens", 0)
            }
        except Exception as e:
            print(f"获取使用信息时出错: {e}")
            return None


def main():
    """
    主函数示例
    """
    import sys
    
    # 检查参数
    if len(sys.argv) < 3:
        print("用法: python analyze_video_s3.py <bucket_name> <video_path>")
        print("示例: python analyze_video_s3.py my-bucket /path/to/video.mp4")
        sys.exit(1)
    
    bucket_name = sys.argv[1]
    video_path = sys.argv[2]
    
    # 初始化分析器
    analyzer = VideoAnalyzerS3(
        region_name="us-east-1",
        model_id="us.amazon.nova-2-lite-v1:0",
        bucket_name=bucket_name
    )
    
    # 自定义提示词
    prompt = "请详细分析这个视频的内容，包括场景、人物、动作和主要事件。"
    
    try:
        print("="*60)
        print("AWS Bedrock 视频分析 (S3 方式)")
        print("="*60)
        
        # 分析视频
        response = analyzer.analyze_video(
            video_path=video_path,
            prompt=prompt,
            max_tokens=2048,
            temperature=0.7,
            top_p=0.9,
            cleanup=True  # 分析后删除 S3 文件
        )
        
        # 提取并打印结果
        result_text = analyzer.extract_text_response(response)
        
        if result_text:
            print("\n" + "="*60)
            print("分析结果:")
            print("="*60)
            print(result_text)
            
            # 打印使用信息
            usage_info = analyzer.get_usage_info(response)
            if usage_info:
                print("\n" + "="*60)
                print("Token 使用情况:")
                print(f"  输入 tokens: {usage_info['input_tokens']}")
                print(f"  输出 tokens: {usage_info['output_tokens']}")
                print(f"  总计 tokens: {usage_info['total_tokens']}")
                print("="*60)
        else:
            print("\n❌ 无法提取文本结果")
            
    except FileNotFoundError:
        print(f"❌ 错误: 找不到视频文件 '{video_path}'")
    except Exception as e:
        print(f"❌ 分析视频时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
