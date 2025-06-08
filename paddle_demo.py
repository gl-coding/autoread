from paddleocr import PaddleOCR
import os
from PIL import Image
import matplotlib.pyplot as plt

def recognize_text(image_path, lang='ch'):
    """
    使用PaddleOCR识别图片中的文字
    
    Args:
        image_path: 图片路径
        lang: 识别语言，默认为中文('ch')
        
    Returns:
        识别结果列表，每个元素为 (文本, 置信度) 的元组
    """
    # 初始化PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang=lang)
    
    # 确保图片文件存在
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"找不到图片文件：{image_path}")
    
    # 执行文字识别
    result = ocr.ocr(image_path, cls=True)
    
    # 提取识别结果
    texts = []
    if result:
        for line in result[0]:
            text = line[1][0]  # 识别的文本
            confidence = line[1][1]  # 置信度
            texts.append((text, confidence))
    
    return texts

def visualize_result(image_path, result):
    """
    可视化识别结果
    
    Args:
        image_path: 原始图片路径
        result: OCR识别结果
    """
    # 读取原始图片
    img = Image.open(image_path)
    plt.figure(figsize=(15, 10))
    plt.imshow(img)
    
    # 在图片上标注识别的文字
    for text, conf in result:
        plt.text(10, 10, f"{text} ({conf:.2f})", 
                bbox=dict(facecolor='white', alpha=0.7))
    
    plt.axis('off')
    plt.show()

def main():
    # 使用screenshots文件夹中的第一张图片作为测试
    image_path = "screenshots/screenshot_20250607_161930.png"
    
    try:
        # 执行文字识别
        results = recognize_text(image_path)
        
        # 打印识别结果
        print("识别结果：")
        for text, confidence in results:
            print(f"文本：{text}，置信度：{confidence:.2f}")
        
        # 可视化结果
        visualize_result(image_path, results)
        
    except Exception as e:
        print(f"发生错误：{str(e)}")

if __name__ == "__main__":
    main() 