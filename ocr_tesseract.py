import pytesseract, os
from PIL import Image

def test():
    # 识别图片文字
    text = pytesseract.image_to_string(Image.open('split_results/cropped_screenshot_20250923_103002_left.png'), lang='chi_sim')  # 中文需下载语言包
    #text = pytesseract.image_to_string(Image.open('split_results/cropped_screenshot_20250923_103002_left.png'), lang='eng')  # 中文需下载语言包
    #text = pytesseract.image_to_string(Image.open('split_results/cropped_screenshot_20250923_103002_left.png'), lang='chi_sim+eng')  # 中文需下载语言包
    print(text)
    exit()

test()

def main():
    #遍历split_results目录下的所有图片，进行OCR识别，并保存到ocr_results目录
    if os.path.exists('ocr_results'):
        os.remove('ocr_results')
    if not os.path.exists('ocr_results'):
        os.makedirs('ocr_results')
    for file in os.listdir('split_results'):
        print(file)
        if file.endswith('.png'):
            text = pytesseract.image_to_string(Image.open('split_results/' + file), lang='eng')
            print(text)
            with open('ocr_results/' + file.replace('.png', '.txt'), 'w') as f:
                f.write(text)

if __name__ == "__main__":
    main()