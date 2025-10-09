import os, sys
import multiprocessing
from llm_prompt import *
from collections import Counter

MAX_LENGTH = 1000
#MAX_LENGTH = 200
#PROMPT = "每一个句话都给出翻译，标注在原文后面括号中，给出这个段落中所有出现的固定搭配和解释，标注“固定搭配”，给出所有单词的音标和释义，标注“单词”"
PROMPT = ""

dir_name = "Jobs/"
res_dir = dir_name + "res"
file_name = dir_name + "book.txt"
file_name_res = dir_name + "book_res.txt"
# if os.path.exists(file_name_res):
#     os.remove(file_name_res)

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
    st = time.time()
    prompt = Prompt()
    res = prompt.trans_segment(line)
    append_line_tofile(res, f"{res_dir}/{line_idx}.txt")
    print(f"耗时: {time.time() - st}秒")

def process_file_with_llm(file_path):
    # 确保输出目录存在
    output_dir = res_dir
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
    
    with multiprocessing.Pool(processes=10) as pool:
        pool.map(process_line, idx_dic.items())

def split_words(words):
    if "[" not in words:
        return words, "", ""
    pre  = words.find("[")
    post = words.find("]")
    word = words[0:pre].strip()
    yinbiao = words[pre:post+1].strip()
    mean = words[post+1:].strip()
    return word, yinbiao, mean

def format_file(file_path):
    res = []
    with open(file_path, 'r') as file:
        content = file.read()
        for line in content.split("\n"):
            line = line.strip()
            if not line or line == "---":
                continue
            #print(line)
            if line.startswith("-"):
                #print(res, line)
                res[-1][0] = res[-1][0] + " " + line
            else:
                res.append([line])
    res_dic = {}
    
    src_flag = False
    for i in range(len(res)):
        line = res[i][0]
        if "【源段落】" in line and line.split("【源段落】")[1].strip() != "":
            src_line = line.split("【源段落】")[1].strip()
            res[i].append("segs")
            res[i].append(src_line)
            res_dic["src"] = src_line
        elif "【源段落】" in line and line.split("【源段落】")[1].strip() == "":
            src_flag = True
            continue
        if src_flag:
            res[i-1].append("segs")
            res[i-1].append(line)
            src_flag = False
            res_dic["src"] = line
        if "原文:" in line and line.split("原文:")[1].strip() != "":
            num = line.split("原文:")[0].strip()
            src_line = line.split("原文:")[1].strip()
            res[i].append("text")
            res[i].append(num.strip("."))
            #res[i].append("原文")
            res[i].append(src_line)
        if "翻译:" in line and line.split("翻译:")[1].strip() != "":
            src_line = line.split("翻译:")[1].strip()
            res[i].append("trans")
            res[i].append(src_line)
        if "语法:" in line and line.split("语法:")[1].strip() != "":
            src_line = line.split("语法:")[1].strip()
            res[i].append("gram")
            res[i].append(src_line)
        if "固定搭配:" in line and line.split("固定搭配:")[1].strip() != "":
            src_line = line.split("固定搭配:")[1].strip()
            res[i].append("phrase")
            res[i].extend([it.strip() for it in src_line.split("-")[1:] if it.strip() != ""])
        if "单词:" in line and line.split("单词:")[1].strip() != "":
            src_line = line.split("单词:")[1].strip()
            res[i].append("word")
            res[i].extend([it.strip() for it in src_line.split("-")[1:] if it.strip() != ""])

    res_dict_total = []
    res_dict_local = {}
    for item in res: 
        #print(len(item))
        if len(item) < 2:
            continue
        #print("item-----", item)
        data_type = item[1]
        if data_type == "text":
            res_dict_local[data_type] = " ".join(item[3:])
        elif data_type in ["trans", "gram"]:
            res_dict_local[data_type] = " ".join(item[2:])
        else:
            content = item[2:]
            res_dict_local[data_type] = content
        if data_type == "word" or data_type == "segs":
            print(res_dict_local)
            res_dict_total.append(res_dict_local)
            res_dict_local = {}
    #print(res_dict_total)

        #print(item, data_type, content)
    #print(res_dic)
    #print(len(res_dict_total))
    words_all = []
    text_all = []
    for item in res_dict_total:
        text = item.get("text", "")
        if text != "": text_all.append(text)
        #if text != "": print(text)
        trans = item.get("trans", "")
        if trans != "": print(trans)
        gram = item.get("gram", "")
        if gram != "": print(gram)
        phrase = item.get("phrase", "")
        if phrase != "": print(phrase)
        word = item.get("word", [])
        if word: 
            print(word)
            for w in word:
                word, yinbiao, mean = split_words(w)
                print(word, yinbiao, mean)
                if yinbiao != "":
                    words_all.append(word)
    return text_all, words_all

def format_files(file_path):
    all_words = []
    all_text = []
    #遍历文件夹下的所有文件，按照序号大小排序，然后依次处理
    files = [f for f in os.listdir(file_path) if f.endswith(".txt")]
    files.sort(key=lambda x: int(x.split(".")[0]))
    for file in files:
        if file.endswith(".txt"):
            text_in_file, words_in_file = format_file(os.path.join(file_path, file))
            print(text_in_file)
            print(words_in_file)
            all_words.extend(words_in_file)
            all_text.extend(text_in_file)
    print(len(all_words))
    print(len(all_text))
    print(all_text[:10])
    #统计每个单词出现的次数，并按照出现次数降序排序，并打印前100个单词
    word_count = Counter(all_words)
    word_count = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    print(word_count)

if __name__ == "__main__":
    arg = sys.argv[1]
    #process_file("book_tmp.txt")
    if arg == "1":
        process_file(file_name)
        process_file_with_llm(file_name_res)
    elif arg == "2":
        format_files(res_dir)