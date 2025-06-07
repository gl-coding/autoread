#!/usr/bin/env python3
"""
图片横向切分工具
将一张图片横向切分为左右两张图片
"""

from PIL import Image
import os
import sys

def split_image(image_path, output_dir=None):
    """
    将图片横向切分为两张图片
    :param image_path: 输入图片路径
    :param output_dir: 输出目录（可选）
    :return: 切分后的两个图片路径
    """
    try:
        # 打开图片
        with Image.open(image_path) as img:
            # 获取原始图片尺寸
            width, height = img.size
            print(f"原始图片尺寸: {width} x {height}")

            # 计算切分点（中点）
            mid_point = width // 2

            # 切分图片
            left_img = img.crop((0, 0, mid_point, height))
            right_img = img.crop((mid_point, 0, width, height))

            # 准备输出路径
            if output_dir is None:
                output_dir = 'split_results'
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 生成输出文件名
            filename = os.path.splitext(os.path.basename(image_path))[0]
            left_path = os.path.join(output_dir, f"{filename}_left.png")
            right_path = os.path.join(output_dir, f"{filename}_right.png")

            # 保存切分后的图片
            left_img.save(left_path)
            right_img.save(right_path)

            print(f"\n✅ 切分成功！")
            print(f"左半部分保存至：{left_path}")
            print(f"右半部分保存至：{right_path}")
            print(f"切分后尺寸: {mid_point} x {height} (每张)")

            return left_path, right_path

    except Exception as e:
        print(f"\n❌ 切分失败：{str(e)}")
        return None, None

def batch_split_images(input_dir='screenshots', output_dir='split_results'):
    """
    批量处理图片切分
    :param input_dir: 输入目录
    :param output_dir: 输出目录
    """
    if not os.path.exists(input_dir):
        print(f"错误：找不到输入目录 {input_dir}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")

    # 支持的图片格式
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    
    # 遍历目录
    processed = 0
    failed = 0
    
    print("\n开始批量切分图片...")
    print("=" * 50)
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(image_extensions):
            input_path = os.path.join(input_dir, filename)
            
            print(f"\n处理图片: {filename}")
            left, right = split_image(input_path, output_dir)
            
            if left and right:
                processed += 1
            else:
                failed += 1
    
    print("\n" + "=" * 50)
    print(f"处理完成！")
    print(f"成功处理: {processed} 张图片")
    print(f"处理失败: {failed} 张图片")
    print(f"切分结果保存在: {output_dir} 目录")

def main():
    if len(sys.argv) < 2:
        print("用法：")
        print("1. 处理单张图片：python image_split.py <图片路径> [输出目录]")
        print("2. 批量处理目录：python image_split.py --batch [输入目录] [输出目录]")
        print("\n示例：")
        print("python image_split.py input.jpg split_results")
        print("python image_split.py --batch screenshots split_results")
        return

    if sys.argv[1] == '--batch':
        # 批量处理模式
        input_dir = sys.argv[2] if len(sys.argv) > 2 else 'screenshots'
        output_dir = sys.argv[3] if len(sys.argv) > 3 else 'split_results'
        batch_split_images(input_dir, output_dir)
    else:
        # 单文件处理模式
        image_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not os.path.exists(image_path):
            print(f"错误：找不到图片文件 {image_path}")
            return

        split_image(image_path, output_dir)

if __name__ == "__main__":
    main() 