#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

class FileProcessor:
    def __init__(self, input_file, output_file):
        """
        初始化文件处理器
        :param input_file: 输入文件路径
        :param output_file: 输出文件路径
        """
        self.input_file = input_file
        self.output_file = output_file
        
    def process_line(self, line):
        """
        处理单行文本的方法
        :param line: 输入的文本行
        :return: 处理后的文本行
        """
        # 这里可以添加自定义的行处理逻辑
        # 默认实现：去除行首尾的空白字符
        return line.strip()
    
    def process_file(self):
        """
        处理整个文件
        """
        try:
            with open(self.input_file, 'r', encoding='utf-8') as infile:
                print(f"正在读取文件：{self.input_file}")
                # 读取所有行并处理
                processed_lines = []
                br_line = False
                for line in infile:
                    if line.strip() == "<br>" and not br_line:
                        br_line = True
                        processed_lines.append(line.rstrip('\n'))
                    elif line.strip() == "<br>" and br_line:
                        continue
                    else:
                        br_line = False
                        processed_lines.append(line.rstrip('\n'))
                    if line.strip() != "":
                        print(f"处理行: {line.rstrip()}")  # 添加调试输出
            
            print(f"总共处理了 {len(processed_lines)} 行")
            
            # 写入处理后的内容到输出文件
            with open(self.output_file, 'a', encoding='utf-8') as outfile:
                for line in processed_lines:
                    outfile.write(line + '\n')
                
            print(f"文件处理完成！")
            print(f"输入文件：{self.input_file}")
            print(f"输出文件：{self.output_file}")
            
        except FileNotFoundError:
            print(f"错误：找不到输入文件 {self.input_file}")
        except Exception as e:
            print(f"处理文件时发生错误：{str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用方法: python file_processor.py 输入文件 输出文件")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # 创建处理器实例
    processor = FileProcessor(input_file, output_file)
    
    # 处理文件
    processor.process_file()
