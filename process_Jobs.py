import os, sys
import multiprocessing
from llm_prompt import *
from collections import Counter
from rapidfuzz.distance import Levenshtein
from rapidfuzz.distance import DamerauLevenshtein
import numpy as np
import hashlib

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

def words_cluster(words_all):
    def get_ngrams(text: str, n: int = 2) -> set:
        if n < 1: return set()
        ngrams = set(text[i:i+n] for i in range(len(text) - n + 1))
        return ngrams
    #two-gram dice similarity
    def two_gram_dice_similarity(s1: str, s2: str) -> float:
        g1, g2 = get_ngrams(s1, n=2), get_ngrams(s2, n=2)
        if not g1 and not g2: return 1.0
        intersection_size = len(g1.intersection(g2))
        size_g1, size_g2 = len(g1), len(g2)
        denominator = size_g1 + size_g2
        if denominator == 0: return 0.0 # 理论上上面已处理两个空集的情况
        similarity = (2 * intersection_size) / denominator
        return similarity

    print("聚类开始")
    word_count = Counter(words_all)
    word_sort = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    print(len(words_all), len(word_sort))
    word_list = [it[0] for it in word_sort]
    n = len(word_list)
    dist_mat = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            dist_mat[i, j] = two_gram_dice_similarity(word_list[i], word_list[j])
            #dist_mat[i, j] = Levenshtein.normalized_similarity(word_list[i], word_list[j])
            #dist_mat[i, j] = DamerauLevenshtein.normalized_similarity(word_list[i], word_list[j])
    print("聚类结束")
    topk = 5 # 对每个词找出最相似的 top-k
    similar_words = {}
    for i in range(n):
        idx_sorted = np.argsort(-dist_mat[i]) # 对第 i 行的相似度排序（从高到低），argsort 默认升序，所以要加负号
        idx_sorted = [j for j in idx_sorted if j != i] # 跳过自己（相似度=100）
        top_indices = idx_sorted[:topk] # 取 top-k 相似词
        top_pairs = [(word_list[j], dist_mat[i, j]) for j in top_indices]
        similar_words[word_list[i]] = top_pairs

    # 输出结果
    for w, sims in similar_words.items():
        result = [(sw, round(sim, 2)) for sw, sim in sims if sim > 0.6]
        print(w, result)

def format_single_file(file_path):
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

    words_all  = []
    phrase_all = []
    text_all   = []
    words_info_all = {}
    phrase_info_file = {}
    sentence_info = {}
    word_sentence = {}
    for item in res_dict_total:
        key = ""
        text = item.get("text", "")
        if text != "": 
            text_all.append(text)
            key = hashlib.md5(text.encode()).hexdigest()
            sentence_info[key] = {"text": text}
        else:
            continue
        print(text)
        trans = item.get("trans", "")
        if trans != "": 
            sentence_info[key]["trans"] = trans
        gram = item.get("gram", "")
        if gram != "": 
            sentence_info[key]["gram"] = gram
        phrase = item.get("phrase", "")
        if phrase: 
            #print(phrase)
            phrase_info = {}
            for p in phrase:
                sps = p.split(":")
                if len(sps) != 2: continue
                phrase_info[sps[0]] = sps[1]
                phrase_all.append(sps[0])
            sentence_info[key]["phrase"] = phrase_info
            phrase_info_file.update(phrase_info)
        word = item.get("word", [])
        if word: 
            #print(word)
            words_info = {}
            for w in word:
                word, yinbiao, mean = split_words(w)
                #print(word, yinbiao, mean)
                if yinbiao != "":
                    words_all.append(word)
                    words_info[word] = (yinbiao, mean)
                    word_sentence.setdefault(word, []).append(text)
            sentence_info[key]["word"] = words_info
            words_info_all.update(words_info)
    return text_all, words_all, words_info_all, sentence_info, word_sentence, phrase_all, phrase_info_file

def format_files(file_path):
    all_text  = []
    all_text_idmap = {}

    all_words = []
    all_words_info = {}

    all_phrase = []
    all_phrase_info = {}

    all_sentence_info = {}
    all_word_sentence = {}
    #遍历文件夹下的所有文件，按照序号大小排序，然后依次处理
    files = [f for f in os.listdir(file_path) if f.endswith(".txt")]
    files.sort(key=lambda x: int(x.split(".")[0]))
    for file in files:
        if file.endswith(".txt"):
            text_in_file, words_in_file, words_info, sentence_info, word_sentence, phrase_all, phrase_info_file = format_single_file(os.path.join(file_path, file))
            # print(text_in_file)
            # print(words_in_file)
            all_text.extend(text_in_file)
            all_words.extend(words_in_file)
            all_words_info.update(words_info)
            all_phrase.extend(phrase_all)
            all_phrase_info.update(phrase_info_file)
            all_sentence_info.update(sentence_info)
            for word, sentences in word_sentence.items():
                all_word_sentence.setdefault(word, []).extend(sentences)
    #处理句子，得到整片文章的序列
    if False:
        print(len(all_text))
        #print(all_text[:10])
        #for item in all_text[:10]:
        cnt = -1
        for item in all_text:
            cnt += 1
            print(item)
            key = hashlib.md5(item.encode()).hexdigest()
            all_text_idmap[key] = cnt
            sentence_info = all_sentence_info[key]
            print(sentence_info)
    #处理单词聚类
    if True:
        #统计每个单词出现的次数，并按照出现次数降序排序，并打印前100个单词
        word_count = Counter(all_words)
        word_sort = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        print(len(all_words), len(word_sort))
        #print(all_text[:100])
        words_cluster(all_words)
    #处理单词倒排索引
    if False:
        for word, sentences in all_word_sentence.items():
            print(word, sentences)
    #处理短语倒排索引
    if False:
        for phrase, mean in all_phrase_info.items(): print(phrase, mean)
        #for phrase in all_phrase: print(phrase)
        print(len(all_phrase))

if __name__ == "__main__":
    arg = sys.argv[1]
    #process_file("book_tmp.txt")
    if arg == "1":
        process_file(file_name)
        process_file_with_llm(file_name_res)
    elif arg == "2":
        format_files(res_dir)