from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')
result = ocr.ocr('./screenshots/screenshot_20250605_231224.png', cls=True)
for line in result:
    print(line[0][1])  # 打印识别结果