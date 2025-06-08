import os
import argparse
from datetime import datetime

def merge_ocr_results(input_dir, output_file, debug=False):
    """
    合并OCR结果文件
    
    Args:
        input_dir: OCR结果文件所在目录
        output_file: 输出的合并文件路径
        debug: 是否显示调试信息
    """
    # 获取所有.txt文件并按文件名排序
    files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
    files.sort()
    
    # 创建输出目录（如果不存在）
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 合并文件内容
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for i, filename in enumerate(files, 1):
            file_path = os.path.join(input_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read().strip()
                    if content:  # 只写入非空内容
                        if debug:
                            outfile.write(f"### 文件 {i}/{len(files)}: {filename} ###\n")
                        outfile.write(content)
                        if i < len(files):  # 如果不是最后一个文件，添加换行
                            outfile.write("\n")
                if debug:
                    print(f"处理文件 ({i}/{len(files)}): {filename}")
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='合并OCR结果文件')
    parser.add_argument('--input-dir', default='ocr_results',
                      help='输入目录路径 (默认: ocr_results)')
    parser.add_argument('--output-file', default='merged_results/merged_ocr_results.txt',
                      help='输出文件路径 (默认: merged_results/merged_ocr_results.txt)')
    parser.add_argument('-d', '--debug', action='store_true',
                      help='显示调试信息')
    
    args = parser.parse_args()
    
    try:
        merge_ocr_results(args.input_dir, args.output_file, debug=args.debug)
        
        print(f"合并完成！输出文件：{args.output_file}")
        if args.verbose:
            files_count = len([f for f in os.listdir(args.input_dir) if f.endswith('.txt')])
            print(f"共合并了 {files_count} 个文件")
            
    except Exception as e:
        print(f"发生错误：{str(e)}")

if __name__ == "__main__":
    main() 