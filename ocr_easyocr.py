import easyocr

reader = easyocr.Reader(['ch_sim', 'en'])  # 支持中文+英文
results = reader.readtext('split_results/cropped_screenshot_20250923_103002_left.png')
print(results)