 #!/usr/bin/env python3
"""
批量OCR文字识别工具
遍历 cropped 目录中的所有图片，进行OCR识别并将结果保存到 ocr_results 目录
"""

import os
import pytesseract
from PIL import Image
from datetime import datetime

def save_text_result(text, output_path):
    """
    保存OCR识别结果到文本文件
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"保存文件失败 {output_path}: {str(e)}")
        return False

def process_image(image_path, output_dir):
    """
    处理单个图片的OCR识别
    """
    try:
        # 获取不带扩展名的文件名
        filename = os.path.splitext(os.path.basename(image_path))[0]
        
        # 生成输出文件路径
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(output_dir, f"{filename}_{timestamp}.txt")
        
        # OCR识别
        text = pytesseract.image_to_string(
            Image.open(image_path), 
            lang='chi_sim'  # 使用中文识别
        )
        
        # 保存结果
        if save_text_result(text, output_path):
            print(f"✅ OCR识别成功: {os.path.basename(image_path)}")
            print(f"   结果保存至: {output_path}")
            return True
        return False
        
    except Exception as e:
        print(f"❌ OCR识别失败 {os.path.basename(image_path)}: {str(e)}")
        return False

def batch_process_ocr():
    """
    批量处理OCR识别
    """
    # 创建输出目录
    output_dir = 'ocr_results'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")

    # 确保cropped目录存在
    input_dir = 'split_results'
    if not os.path.exists(input_dir):
        print(f"错误：找不到cropped目录")
        return

    # 支持的图片格式
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    
    # 遍历cropped目录
    processed = 0
    failed = 0
    
    print("\n开始批量OCR处理...")
    print("=" * 50)
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(image_extensions):
            input_path = os.path.join(input_dir, filename)
            
            if process_image(input_path, output_dir):
                processed += 1
            else:
                failed += 1
    
    print("\n" + "=" * 50)
    print(f"处理完成！")
    print(f"成功处理: {processed} 张图片")
    print(f"处理失败: {failed} 张图片")
    print(f"OCR结果保存在: {output_dir} 目录")

if __name__ == "__main__":
    batch_process_ocr()