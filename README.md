# 鼠标自动点击器

这是一个基于PyQt5开发的鼠标自动点击工具，可以实现自动点击指定位置并截图的功能。

## 功能特点

- 图形化界面，操作简单直观
- 支持手动输入或保存坐标点
- 自动循环点击指定位置
- 每次点击后自动截图
- 智能检测鼠标移动，自动停止循环
- 截图自动保存至screenshots目录
- OCR结果文件合并功能

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用说明

### 1. 鼠标自动点击

1. 运行程序：
   ```bash
   python mouse_tracker.py
   ```

2. 主要功能：
   - **保存编辑的坐标**：手动输入X和Y坐标，并可添加描述
   - **点击保存的坐标**：单次点击保存的坐标位置
   - **开始循环点击**：开始自动循环操作
   
3. 循环点击流程：
   - 每2秒执行一次点击操作
   - 移动到目标位置（耗时0.1秒）
   - 执行点击
   - 等待0.5秒
   - 自动截图保存
   - 返回原位置（耗时0.1秒）

4. 停止条件：
   - 检测到鼠标被手动移动时自动停止
   - 检测频率为每0.1秒一次

5. 截图存储：
   - 所有截图自动保存在程序目录下的screenshots文件夹中
   - 文件名格式：screenshot_年月日_时分秒.png
   - 示例：screenshot_20240101_120000.png

### 2. OCR结果合并

使用 `merge_ocr_results.py` 脚本可以将OCR结果文件按顺序合并：

1. 基本用法：
   ```bash
   python merge_ocr_results.py
   ```
   - 默认从 `ocr_results` 目录读取所有txt文件
   - 按文件名字母顺序合并
   - 输出到 `merged_results/merged_ocr_results.txt`

2. 调试模式：
   ```bash
   python merge_ocr_results.py -d
   ```
   - 显示处理进度
   - 在输出文件中添加文件信息

3. 自定义路径：
   ```bash
   python merge_ocr_results.py --input-dir 自定义输入目录 --output-file 自定义输出文件路径
   ```

## 注意事项

1. 程序运行时会自动创建必要的目录（screenshots、merged_results等）
2. 在循环过程中移动鼠标将自动停止循环
3. 循环开始后所有按钮会被禁用，直到循环停止
4. 坐标输入框只接受数字输入

## 配置文件

程序会自动保存最后使用的坐标到config.json文件中，包含：
- X坐标
- Y坐标
- 描述信息

## 系统要求

- Python 3.6+
- 依赖包：见 requirements.txt
- 支持的操作系统：Windows/MacOS/Linux
