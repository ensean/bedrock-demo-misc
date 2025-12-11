#!/usr/bin/env python3
"""
Word文档内容审核和总结工具
使用 AWS Bedrock Converse API 调用 Claude Sonnet 3.5 模型
支持直接传递 DOCX 文档格式
"""

import boto3
import json
import logging
import base64
from pathlib import Path
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentReviewer:
    def __init__(self, region_name: str = 'us-east-1', prompt_file: str = 'prompt.txt'):
        """
        初始化文档审核器
        
        Args:
            region_name: AWS区域名称
            prompt_file: 系统提示词文件路径
        """
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=region_name)
        self.model_id = 'us.anthropic.claude-sonnet-4-5-20250929-v1:0'
        self.prompt_file = prompt_file
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        """
        从文件加载系统提示词
        
        Returns:
            系统提示词内容
        """
        try:
            prompt_path = Path(__file__).parent / self.prompt_file
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"加载提示词文件失败: {e}")
            # 返回默认提示词
            return "请对提供的文档进行全面审核和分析，包括内容总结、结构分析、质量审核等方面。"
    
    def _read_document(self, file_path: str) -> str:
        """
        读取文档文件
        
        Args:
            file_path: 文档文件路径
            
        Returns:
            文档内容
        """
        try:
            with open(file_path, 'rb') as f:
                document_bytes = f.read()
            return document_bytes
        except Exception as e:
            logger.error(f"读取文档文件失败: {e}")
            raise

    def review_document(self, file_path: str) -> Dict[str, Any]:
        """
        审核Word文档
        
        Args:
            file_path: Word文档路径
            
        Returns:
            审核结果字典
        """
        try:
            # 检查文件格式
            if not file_path.lower().endswith('.docx'):
                raise ValueError("仅支持 .docx 格式的文档")
            
            # 读取文档并转换为base64
            logger.info(f"正在读取文档: {file_path}")
            document_bytes = self._read_document(file_path)
            
            # 获取文件大小信息
            file_size = Path(file_path).stat().st_size
            logger.info(f"文档大小: {file_size} 字节")
            
            # 调用Bedrock Converse API，直接传递文档
            logger.info("正在调用Claude Sonnet 4.5进行文档审核...")
            response = self.bedrock_client.converse(
                modelId=self.model_id,
                messages=[
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "text": self.system_prompt
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "document": {
                                    "format": "docx",
                                    "name": "prd_document",
                                    "source": {
                                        "bytes": document_bytes
                                    }
                                }
                            },
                            {
                                "text": "分析下这个文档"
                            }
                        ]
                    }
                ],
                inferenceConfig={
                    "maxTokens": 8000,
                    "temperature": 0.6
                }
            )
            
            # 提取响应内容
            review_result = response['output']['message']['content'][0]['text']
            
            return {
                "status": "success",
                "file_path": file_path,
                "file_size": file_size,
                "review_result": review_result,
                "model_used": self.model_id
            }
            
        except Exception as e:
            logger.error(f"文档审核失败: {e}")
            return {
                "status": "error",
                "file_path": file_path,
                "error": str(e)
            }

    def save_review_result(self, result: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        保存审核结果到文件
        
        Args:
            result: 审核结果
            output_path: 输出文件路径，如果为None则自动生成
            
        Returns:
            输出文件路径
        """
        if output_path is None:
            file_name = Path(result['file_path']).stem
            output_path = f"{file_name}_review_result.txt"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("文档审核报告\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"原文档: {result['file_path']}\n")
                f.write(f"审核时间: {result.get('timestamp', 'N/A')}\n")
                f.write(f"使用模型: {result.get('model_used', 'N/A')}\n")
                
                if result['status'] == 'success':
                    f.write(f"文档大小: {result['file_size']} 字节\n\n")
                    f.write("审核结果:\n")
                    f.write("-" * 40 + "\n")
                    f.write(result['review_result'])
                else:
                    f.write(f"审核失败: {result['error']}\n")
            
            logger.info(f"审核结果已保存到: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"保存审核结果失败: {e}")
            raise


def main():
    """主函数"""
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='Word文档内容审核工具')
    parser.add_argument('file_path', help='Word文档路径 (.docx格式)')
    parser.add_argument('--region', default='us-east-1', help='AWS区域 (默认: us-east-1)')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--prompt', default='prompt.txt', help='系统提示词文件路径 (默认: prompt.txt)')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not Path(args.file_path).exists():
        logger.error(f"文件不存在: {args.file_path}")
        return
    
    # 创建审核器
    reviewer = DocumentReviewer(region_name=args.region, prompt_file=args.prompt)
    
    # 执行审核
    result = reviewer.review_document(args.file_path)
    result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 保存结果
    output_path = reviewer.save_review_result(result, args.output)
    
    # 打印结果摘要
    if result['status'] == 'success':
        print(f"\n✅ 文档审核完成!")
        print(f"📄 原文档: {args.file_path}")
        print(f"📊 文档大小: {result['file_size']} 字节")
        print(f"💾 结果保存至: {output_path}")
    else:
        print(f"\n❌ 审核失败: {result['error']}")


if __name__ == "__main__":
    main()