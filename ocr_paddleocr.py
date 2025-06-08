#!/usr/bin/env python3
"""
使用EasyOCR进行文字识别
支持单个文件和批量处理
"""

import os
import sys
import easyocr

def init_ocr():
    """
    初始化EasyOCR
    """
    try:
        # 初始化中文和英文识别
        reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
        return reader
    except Exception as e:
        print(f"初始化OCR失败: {str(e)}")
        return None

def process_image(reader, image_path, output_dir=None):
    """
    处理单个图片
    :param reader: EasyOCR实例
    :param image_path: 图片路径
    :param output_dir: 输出目录（可选）
    :return: 是否处理成功
    """
    try:
        print(f"\n处理图片: {image_path}")

        # 执行OCR识别
        result = reader.readtext(image_path)
        
        if not result:
            print("未检测到文字")
            return False
            
        # 准备输出
        output = []
        for idx, (bbox, text, confidence) in enumerate(result, 1):
            output.append(f"{idx}. {text} (置信度: {confidence:.2f})")
        
        # 如果指定了输出目录，保存到文件
        if output_dir:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            filename = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join(output_dir, f"{filename}_ocr.txt")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(output))
            print(f"结果已保存到: {output_path}")
        
        # 打印结果
        print("\n识别结果:")
        print("\n".join(output))
        return True
        
    except Exception as e:
        print(f"处理失败: {str(e)}")
        return False

def batch_process(input_dir='screenshots', output_dir='ocr_results'):
    """
    批量处理图片
    :param input_dir: 输入目录
    :param output_dir: 输出目录
    """
    # 初始化OCR
    reader = init_ocr()
    if not reader:
        return
    
    # 检查输入目录
    if not os.path.exists(input_dir):
        print(f"错误：找不到输入目录 {input_dir}")
        return
    
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 支持的图片格式
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp')
    
    # 统计
    processed = 0
    failed = 0
    
    # 处理所有图片
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(image_extensions):
            image_path = os.path.join(input_dir, filename)
            if process_image(reader, image_path, output_dir):
                processed += 1
            else:
                failed += 1
    
    # 打印统计信息
    print(f"\n处理完成！")
    print(f"成功: {processed} 张")
    print(f"失败: {failed} 张")

def main():
    if len(sys.argv) < 2:
        print("用法：")
        print("1. 处理单个文件：python ocr_paddleocr.py <图片路径> [输出目录]")
        print("2. 批量处理：python ocr_paddleocr.py --batch [输入目录] [输出目录]")
        return
    
    if sys.argv[1] == '--batch':
        # 批量处理模式
        input_dir = sys.argv[2] if len(sys.argv) > 2 else 'screenshots'
        output_dir = sys.argv[3] if len(sys.argv) > 3 else 'ocr_results'
        batch_process(input_dir, output_dir)
    else:
        # 单文件处理模式
        image_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not os.path.exists(image_path):
            print(f"错误：找不到图片文件 {image_path}")
            return
            
        reader = init_ocr()
        if reader:
            process_image(reader, image_path, output_dir)

if __name__ == "__main__":
    main()