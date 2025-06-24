rm -rf cropped
rm -rf split_results
#rm -rf ocr_results

# 裁剪图片
python batch_crop.py

# 分割图片
python image_split.py --batch cropped split_results

# 识别图片
python images_to_pdf.py