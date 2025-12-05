#!/usr/bin/env python3
"""
Tesseract OCR 图片识别工具
使用 Tesseract 对指定目录下的图片进行 OCR 识别
"""

import pytesseract, os, sys
from PIL import Image

def test():
    # 识别图片文字
    text = pytesseract.image_to_string(Image.open('split_results/cropped_screenshot_20250923_103002_left.png'), lang='chi_sim')  # 中文需下载语言包
    #text = pytesseract.image_to_string(Image.open('split_results/cropped_screenshot_20250923_103002_left.png'), lang='eng')  # 中文需下载语言包
    #text = pytesseract.image_to_string(Image.open('split_results/cropped_screenshot_20250923_103002_left.png'), lang='chi_sim+eng')  # 中文需下载语言包
    print(text)
    exit()

#test()

def batch_ocr(input_dir='split_results', output_dir='ocr_results'):
    """
    批量OCR识别图片
    :param input_dir: 输入图片目录
    :param output_dir: 输出结果目录
    """
    # 检查输入目录是否存在
    if not os.path.exists(input_dir):
        print(f'错误：找不到输入目录 {input_dir}')
        return
    
    # 遍历目录下的所有图片，进行OCR识别，并保存到输出目录
    if os.path.exists(output_dir):
        os.remove(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for file in os.listdir(input_dir):
        print(file)
        if file.endswith('.png'):
            input_path = os.path.join(input_dir, file)
            text = pytesseract.image_to_string(Image.open(input_path), lang='chi_sim')
            print(text)
            output_path = os.path.join(output_dir, file.replace('.png', '.txt'))
            with open(output_path, 'w') as f:
                f.write(text)

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("用法：")
        print("python ocr_tesseract.py [输入目录] [输出目录]")
        print("\n参数：")
        print("  输入目录    要识别的图片所在目录（默认: split_results）")
        print("  输出目录    识别结果保存目录（默认: ocr_results）")
        print("\n示例：")
        print("python ocr_tesseract.py")
        print("python ocr_tesseract.py split_results")
        print("python ocr_tesseract.py split_results ocr_results")
        print("python ocr_tesseract.py my_images my_ocr_results")
        return
    
    # 获取输入输出目录
    input_dir = sys.argv[1] if len(sys.argv) > 1 else 'split_results'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'ocr_results'
    
    batch_ocr(input_dir, output_dir)

if __name__ == "__main__":
    main()