 #!/usr/bin/env python3
"""
批量图片裁剪工具
遍历 screenshots 目录中的所有图片，进行裁剪并保存到 cropped 目录
"""

import os
from image_crop import crop_image

def batch_crop_images():
    """
    批量处理图片
    """
    # 创建输出目录
    output_dir = 'cropped'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")

    # 确保screenshots目录存在
    screenshots_dir = 'screenshots'
    if not os.path.exists(screenshots_dir):
        print(f"错误：找不到screenshots目录")
        return

    # 支持的图片格式
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    
    # 遍历screenshots目录
    processed = 0
    failed = 0
    
    print("\n开始批量处理图片...")
    print("=" * 50)
    
    for filename in os.listdir(screenshots_dir):
        if filename.lower().endswith(image_extensions):
            input_path = os.path.join(screenshots_dir, filename)
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

if __name__ == "__main__":
    batch_crop_images()