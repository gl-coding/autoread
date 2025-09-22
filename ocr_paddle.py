from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang='ch',                # 中文
    det_model_dir=None,       # 指定检测模型目录（可选）
    rec_model_dir=None,       # 指定识别模型目录（可选）
    use_angle_cls=False
)

img_path = '/Users/guolei/Downloads/test.jpg'
img_path = '/Users/guolei/Downloads/test2.jpg'
results = ocr.predict(img_path)

print("\n".join(results[0].get("rec_texts")))
print("\n".join(str(score) for score in results[0].get("rec_scores")))