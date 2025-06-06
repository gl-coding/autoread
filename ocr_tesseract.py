import pytesseract
from PIL import Image

# 识别图片文字
text = pytesseract.image_to_string(Image.open('./screenshots/screenshot_20250605_231226.png'), lang='chi_sim')  # 中文需下载语言包
print(text)
