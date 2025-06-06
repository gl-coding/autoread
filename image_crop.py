#!/usr/bin/env python3
"""
图片裁剪工具
支持从配置文件读取裁剪区域或手动指定裁剪区域
"""

from PIL import Image
import sys
import os
import json

CONFIG_FILE = 'config.json'

def load_config():
    """
    加载配置文件，如果不存在则创建默认配置
    """
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            default_config = {
                "crop": {
                    "left": 0,
                    "top": 0,
                    "right": 1920,
                    "bottom": 1080,
                    "description": "默认裁剪边界"
                }
            }
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)
            return default_config
    except Exception as e:
        print(f'加载配置文件失败: {str(e)}')
        return {"crop": {"left": 0, "top": 0, "right": 1920, "bottom": 1080, "description": "默认裁剪边界"}}

def crop_image(image_path, output_path=None, box=None):
    """
    裁剪图片
    :param image_path: 输入图片路径
    :param output_path: 输出图片路径（可选）
    :param box: 裁剪区域 (left, top, right, bottom)，如果为None则从配置文件读取
    :return: 裁剪后的图片路径
    """
    try:
        # 打开图片
        with Image.open(image_path) as img:
            # 获取原始图片尺寸
            width, height = img.size
            print(f"原始图片尺寸: {width} x {height}")

            if box is None:
                # 从配置文件读取裁剪区域
                config = load_config()
                crop_config = config.get('crop', {})
                box = (
                    crop_config.get('left', 0),
                    crop_config.get('top', 0),
                    crop_config.get('right', width),
                    crop_config.get('bottom', height)
                )
                print(f"\n使用配置文件中的裁剪区域: {box}")
                print(f"描述: {crop_config.get('description', '无描述')}")
            
            # 验证裁剪区域是否有效
            left, top, right, bottom = box
            if left < 0 or top < 0 or right > width or bottom > height:
                raise ValueError("裁剪区域超出图片范围！")
            if left >= right or top >= bottom:
                raise ValueError("裁剪区域无效！左上角坐标必须小于右下角坐标。")

            # 执行裁剪
            cropped_img = img.crop(box)
            
            # 如果没有指定输出路径，在原文件名基础上添加后缀
            if output_path is None:
                filename, ext = os.path.splitext(image_path)
                output_path = f"{filename}_cropped{ext}"
            
            # 保存裁剪后的图片
            cropped_img.save(output_path)
            print(f"\n✅ 裁剪成功！已保存到：{output_path}")
            print(f"裁剪后尺寸: {cropped_img.size[0]} x {cropped_img.size[1]}")
            
            return output_path

    except Exception as e:
        print(f"\n❌ 裁剪失败：{str(e)}")
        return None

def main():
    if len(sys.argv) < 2:
        print("用法：python image_crop.py <图片路径> [输出路径]")
        print("示例：python image_crop.py input.jpg output.jpg")
        return

    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(image_path):
        print(f"错误：找不到图片文件 {image_path}")
        return

    crop_image(image_path, output_path)

if __name__ == "__main__":
    main() 