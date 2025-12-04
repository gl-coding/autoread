#!/usr/bin/env python3
"""
图片转PDF工具
将指定目录下的所有图片按文件名排序后合并成一个PDF文件
"""

import os
import sys
import json
from PIL import Image

# 从config.json读取配置
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def resize_image(img, width):
    """调整图片大小"""
    w_percent = (width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    return img.resize((width, h_size), Image.LANCZOS)

def images_to_pdf(input_dir='split_results', output_pdf='output/output.pdf'):
    """
    将目录下的所有图片转换为PDF
    :param input_dir: 输入图片目录
    :param output_pdf: 输出PDF文件路径
    """
    # 检查输入目录是否存在
    if not os.path.exists(input_dir):
        print(f'错误：找不到输入目录 {input_dir}')
        return False
    
    # 读取配置
    config = load_config()
    TARGET_WIDTH = config.get('target_width', 800)
    
    # 获取所有图片文件名，并按文件名排序
    image_files = sorted([
        f for f in os.listdir(input_dir)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
    ])
    
    # 检查是否有图片
    if not image_files:
        print(f'错误：在 {input_dir} 目录下未找到图片文件')
        return False
    
    print(f'找到 {len(image_files)} 张图片')
    print(f'目标宽度: {TARGET_WIDTH} 像素')
    
    # 打开所有图片，转换为RGB并缩放
    print('正在处理图片...')
    images = []
    for f in image_files:
        img_path = os.path.join(input_dir, f)
        try:
            img = Image.open(img_path).convert('RGB')
            img_resized = resize_image(img, TARGET_WIDTH)
            images.append(img_resized)
            print(f'  ✓ {f}')
        except Exception as e:
            print(f'  ✗ {f}: {str(e)}')
    
    if not images:
        print('错误：没有成功加载任何图片')
        return False
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_pdf)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 保存为PDF
    print(f'\n正在生成PDF...')
    images[0].save(output_pdf, save_all=True, append_images=images[1:])
    print(f'✅ 已生成PDF文件: {output_pdf}')
    return True

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("用法：")
        print("python images_to_pdf.py [输入目录] [输出PDF路径]")
        print("\n参数：")
        print("  输入目录      要处理的图片所在目录（默认: split_results）")
        print("  输出PDF路径   生成的PDF文件路径（默认: output/output.pdf）")
        print("\n示例：")
        print("python images_to_pdf.py")
        print("python images_to_pdf.py split_results output/output.pdf")
        print("python images_to_pdf.py my_images my_output.pdf")
        return
    
    # 获取输入输出路径
    input_dir = sys.argv[1] if len(sys.argv) > 1 else 'split_results'
    output_pdf = sys.argv[2] if len(sys.argv) > 2 else 'output/output.pdf'
    
    images_to_pdf(input_dir, output_pdf)

if __name__ == "__main__":
    main()