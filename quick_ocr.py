#!/usr/bin/env python3
"""
快速OCR测试脚本
用法: python quick_ocr.py <图片路径>
"""

import sys
import os
from paddleocr import PaddleOCR
import paddle

def main():
    if len(sys.argv) != 2:
        print("用法: python quick_ocr.py <图片路径>")
        print("例如: python quick_ocr.py ./screenshots/screenshot_20250605_231224.png")
        return
    
    image_path = sys.argv[1]
    
    print(f"🔍 正在识别图片: {image_path}")
    print("=" * 60)
    
    try:
        # 为M2芯片配置Paddle
        paddle.device.set_device('cpu')
        os.environ['FLAGS_use_mkldnn'] = '0'
        os.environ['FLAGS_allocator_strategy'] = 'naive_best_fit'
        os.environ['CPU_NUM_THREADS'] = '1'  # 限制CPU线程数
        
        # 初始化OCR（使用简化配置）
        ocr = PaddleOCR(
            use_textline_orientation=True,
            lang='ch'
        )
    
        print("✅ OCR模型加载完成")
        
        # 执行识别
        result = ocr.predict(image_path)
        
        if result and len(result) > 0:
            print(f"✅ 识别完成，共找到 {len(result)} 段文字:\n")
            
            for i, line in enumerate(result, 1):
                if isinstance(line, list) and len(line) >= 2:
                text = line[1][0]
                confidence = line[1][1]
                print(f"{i}. {text} (置信度: {confidence:.2f})")
                else:
                    print(f"{i}. {line}")
        else:
            print("❌ 未检测到任何文字")
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        print("请确保图片文件存在且格式正确")

if __name__ == "__main__":
    main()