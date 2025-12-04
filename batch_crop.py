 #!/usr/bin/env python3
"""
批量图片裁剪工具
遍历指定目录中的所有图片，进行裁剪并保存到输出目录
"""

import os
import sys
from image_crop import crop_image

def batch_crop_images(input_dir='screenshots', output_dir='cropped'):
    """
    批量处理图片
    :param input_dir: 输入目录
    :param output_dir: 输出目录
    """
    # 确保输入目录存在
    if not os.path.exists(input_dir):
        print(f"错误：找不到输入目录 {input_dir}")
        return
    
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")

    # 支持的图片格式
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    
    # 遍历输入目录
    processed = 0
    failed = 0
    
    print("\n开始批量处理图片...")
    print("=" * 50)
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(image_extensions):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"cropped_{filename}")
            
            print(f"\n处理图片: {filename}")
            result = crop_image(input_path, output_path)
            
            if result:
                processed += 1
            else:
                failed += 1
    
    print("\n" + "=" * 50)
    print(f"处理完成！")
    print(f"成功处理: {processed} 张图片")
    print(f"处理失败: {failed} 张图片")
    print(f"裁剪后的图片保存在: {output_dir} 目录")

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("用法：")
        print("python batch_crop.py [输入目录] [输出目录]")
        print("\n参数：")
        print("  输入目录    要处理的图片所在目录（默认: screenshots）")
        print("  输出目录    裁剪后图片保存目录（默认: cropped）")
        print("\n示例：")
        print("python batch_crop.py")
        print("python batch_crop.py screenshots cropped")
        print("python batch_crop.py my_images my_output")
        return
    
    # 获取输入输出目录
    input_dir = sys.argv[1] if len(sys.argv) > 1 else 'screenshots'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'cropped'
    
    batch_crop_images(input_dir, output_dir)

if __name__ == "__main__":
    main()