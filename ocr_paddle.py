from paddleocr import PaddleOCR
from PIL import Image
import os

ocr = PaddleOCR(
    lang='ch',                # 中文
    det_model_dir=None,       # 指定检测模型目录（可选）
    rec_model_dir=None,       # 指定识别模型目录（可选）
    use_angle_cls=False
)

def ocr_predict(img_path):
    # img_path = '/Users/guolei/Downloads/test.jpg'
    # img_path = '/Users/guolei/Downloads/test2.jpg'
    #img_path = 'split_results/cropped_screenshot_20250923_103002_left.png'
    results = ocr.predict(img_path)

    print("\n".join(results[0].get("rec_texts")))
    print("\n".join(str(score) for score in results[0].get("rec_scores")))

def png_to_jpg(img_path, output_path, quality=95):
    with Image.open(img_path) as img:
        # 转换为RGB模式（JPEG不支持RGBA）
        if img.mode in ('RGBA', 'LA'):
            # 创建白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])  # 使用alpha通道作为mask
            else:
                background.paste(img)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 保存为JPEG
        img.save(output_path, 'JPEG', quality=quality, optimize=True)

if __name__ == "__main__":
    img_path = 'split_results/cropped_screenshot_20250923_103002_left.png'
    output_path = 'split_results/cropped_screenshot_20250923_103002_left.jpg'
    png_to_jpg(img_path, output_path)
    ocr_predict(output_path)