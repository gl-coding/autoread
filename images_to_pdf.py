import os
import json
from PIL import Image

# 从config.json读取配置
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
TARGET_WIDTH = config.get('target_width', 800)

# 图片文件夹路径
dir_path = 'split_results'
# 获取所有图片文件名，并按文件名排序
image_files = sorted([
    f for f in os.listdir(dir_path)
    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
])

# 检查是否有图片
if not image_files:
    print('未找到图片文件')
    exit(1)

def resize_image(img, width):
    w_percent = (width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    return img.resize((width, h_size), Image.LANCZOS)

# 打开所有图片，转换为RGB并缩放
images = [resize_image(Image.open(os.path.join(dir_path, f)).convert('RGB'), TARGET_WIDTH) for f in image_files]

# 确保输出目录存在
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)
output_pdf = os.path.join(output_dir, 'output.pdf')

# 保存为PDF
images[0].save(output_pdf, save_all=True, append_images=images[1:])
print(f'已生成PDF文件: {output_pdf}')