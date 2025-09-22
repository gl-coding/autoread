import pytesseract
from PIL import Image

# 识别图片文字
text = pytesseract.image_to_string(Image.open('/Users/guolei/Downloads/test2.jpg'), lang='chi_sim')  # 中文需下载语言包
print(text)
