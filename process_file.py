import os
import multiprocessing
from llm_prompt import *

MAX_LENGTH = 1000
#MAX_LENGTH = 200
#PROMPT = "每一个句话都给出翻译，标注在原文后面括号中，给出这个段落中所有出现的固定搭配和解释，标注“固定搭配”，给出所有单词的音标和释义，标注“单词”"
PROMPT = ""

file_name_res = "Jobs/book_res.txt"
if os.path.exists(file_name_res):
    os.remove(file_name_res)

def append_line_tofile(line, file_name=file_name_res):
    with open(file_name, 'a') as file:
        file.write(line + "\n")

def process_file(file_path):
    res = []
    max_length, min_length = 0, 10000
    max_line, min_line = "", ""
    max_single_line = 0
    with open(file_path, 'r') as file:
        content = file.read()
        for line in content.split("\n"):
            line = line.strip()
            if line == "":
                continue
            res.append(line)

    print(len(res))
    for item in res: print(item)

    print("*"*100)
    local_res = []
    total_res = []
    for line in res: 
        local_res.append(line)
        if line[-1] == "." or line[-2] == ".":
            #print(res)
            total_line = " ".join(local_res)
            total_res.append(total_line)
            local_res = []
    if len(local_res) > 0:
        total_res.append(" ".join(local_res))
    print(len(total_res))

    segment_res = []
    cnt = 0
    max_length = 0
    max_line = ""
    for item in total_res:
        #print(item)
        #print("-"*100)
        segment_res.append(item)
        cnt += len(item)
        # if cnt == 3626:
        #     print(item)
        #     print(len(item))
        #     print("-"*100)
        #     break
        max_length = max(max_length, cnt)
        if cnt > MAX_LENGTH:
            seg_line = " ".join(segment_res)
            print(seg_line, len(seg_line))
            append_line_tofile(seg_line + PROMPT)
            #append_line_tofile(str(len(seg_line)))
            segment_res = []
            cnt = 0
    if len(segment_res) > 0:
        seg_line = " ".join(segment_res)
        append_line_tofile(seg_line + PROMPT)
        #append_line_tofile(str(len(seg_line)))
        print(seg_line, len(seg_line))
    print(max_length)

def process_line(line_item):
    """全局函数，用于多进程处理"""
    line_idx, line = line_item
    print(f"{line_idx}: {line}")
    prompt = Prompt()
    res = prompt.trans_segment(line)
    append_line_tofile(res, f"Jobs/res/{line_idx}.txt")

def process_file_with_llm(file_path):
    # 确保输出目录存在
    output_dir = "Jobs/res"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    line_idx = 0
    idx_dic = {}
    with open(file_path, 'r') as file:
        content = file.read()
        for line in content.split("\n"):
            line = line.strip()
            if line == "":
                continue
            line_idx += 1
            idx_dic[line_idx] = line
    
    with multiprocessing.Pool(processes=1) as pool:
        pool.map(process_line, idx_dic.items())

if __name__ == "__main__":
    #process_file("book_tmp.txt")
    process_file("Jobs/book.txt")
    process_file_with_llm("Jobs/book_res.txt")