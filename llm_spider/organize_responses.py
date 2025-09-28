import os
import shutil
from pathlib import Path
import re

def extract_title_from_markdown(content):
    """从markdown内容中提取标题
    
    Args:
        content (str): markdown文件内容
        
    Returns:
        str: 提取的标题
    """
    # 按行分割内容
    lines = content.split('\n')
    
    # 查找第一个非空行
    for line in lines:
        line = line.strip()
        if line:
            # 如果是markdown标题（以#开头），去除#号和空格
            if line.startswith('#'):
                return line.lstrip('#').strip()
            # 如果不是标题格式，直接返回该行
            return line
    
    return ""

def process_markdown_content(content):
    """处理markdown内容
    
    Args:
        content (str): markdown文件内容
        
    Returns:
        str: 处理后的内容
    """
    # TODO: 在此处添加具体的处理逻辑
    res_content = ""
    null_flag = False
    for line in content.split("\n"):
        if line.strip() == "":
            null_flag = True
        else:
            null_flag = False
        if line.strip() == "---" and null_flag == False:
            line = "\r" + line 
        elif line.strip().startswith("##") and null_flag == False:
            line = "\r" + line
        #elif line.strip().startswith("| ") and line.strip().endswith("|") and null_flag == False:
        #    line = "\r" + line
        elif line.strip() == "下载":
            continue
        new_line = line
        res_content += new_line + "\n"

    return res_content + "<br><br><br>"

def create_honkit_structure():
    """创建Honkit文档结构并整理文件"""
    # 定义基础目录
    base_dir = Path("ai_responses")
    honkit_dir = Path("honkit_docs")
    chapters_dir = honkit_dir / "chapters"
    
    # 创建必要的目录
    honkit_dir.mkdir(exist_ok=True)
    chapters_dir.mkdir(exist_ok=True)
    
    # 获取所有markdown文件
    md_files = list(base_dir.glob("*.md"))
    
    # 用于存储章节信息的字典
    chapters = {}
    
    # 处理每个文件
    for md_file in md_files:
        # 获取文件名（不含扩展名）并分割
        filename = md_file.stem
        parts = filename.split('_')
        
        if len(parts) > 1:
            chapter = parts[0]
            
            # 创建章节目录
            chapter_dir = chapters_dir / chapter
            chapter_dir.mkdir(exist_ok=True)
            
            # 读取并处理文件内容
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 处理markdown内容
                processed_content = process_markdown_content(content)
                # 从内容中提取标题
                title = extract_title_from_markdown(processed_content)
                if not title:
                    title = filename
            
            # 创建新文件并写入处理后的内容
            new_file_path = chapter_dir / md_file.name
            with open(new_file_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            
            # 存储章节信息
            if chapter not in chapters:
                chapters[chapter] = []
            chapters[chapter].append({
                'title': title,
                'file': f"chapters/{chapter}/{md_file.name}"
            })
    
    # 生成SUMMARY.md
    generate_summary(chapters)
    
    # 生成README.md
    generate_readme()

def generate_summary(chapters):
    """生成SUMMARY.md文件"""
    summary_path = Path("honkit_docs/SUMMARY.md")
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# Summary\n\n")
        
        # 添加首页链接
        f.write("* [首页](README.md)\n\n")
        
        # 按章节组织内容
        for chapter in sorted(chapters.keys()):
            # 添加章节标题
            f.write(f"## {chapter}\n\n")
            
            # 添加该章节下的所有文档
            for doc in chapters[chapter]:
                f.write(f"* [{doc['title']}]({doc['file']})\n")
            f.write("\n")

def generate_readme():
    """生成README.md文件"""
    readme_path = Path("honkit_docs/README.md")
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("# Honkit 文档\n\n")
        f.write("本文档包含以下主要内容：\n\n")
        
        # 获取所有章节目录
        chapters_dir = Path("honkit_docs/chapters")
        if chapters_dir.exists():
            for chapter_dir in sorted(chapters_dir.iterdir()):
                if chapter_dir.is_dir():
                    f.write(f"* {chapter_dir.name}\n")

def main():
    print("开始整理文档结构...")
    create_honkit_structure()
    print("文档结构整理完成！")
    print("\n目录结构：")
    print_directory_structure()

def print_directory_structure():
    """打印目录结构"""
    def print_tree(path, prefix=""):
        if path.is_file():
            print(f"{prefix}└── {path.name}")
        else:
            print(f"{prefix}├── {path.name}")
            for item in sorted(path.iterdir()):
                print_tree(item, prefix + "│   ")
    
    print_tree(Path("honkit_docs"))

if __name__ == "__main__":
    main() 