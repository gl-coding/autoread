import os,sys,time,multiprocessing
from llm_prompt import *
from llm_utils import *

def process_text():
    res = []
    merged_dir = pre_dir + 'merged_results'
    with open(os.path.join(merged_dir, 'merged_ocr_results.txt'), 'r', encoding='utf-8') as f:
        text = f.read()
        print_flag = False
        for l in text.split('\n'):
            if l.startswith("Sentence"):
                print_flag = False
            if l.startswith("核心词表"):
                print_flag = True
                continue
            if print_flag:
                if l.strip("=") == "":
                    continue
                if l.startswith("主题归纳") or l.startswith("修改后的内容") or l.startswith("Review"):
                    continue
                if len(res) > 0 and l == res[-1]:
                    continue
                if l.startswith("n.") or l.startswith("v.") or l.startswith("adj.") or l.startswith("adv.") or l.startswith("pron.") \
                    or l.startswith("vi.") or l.startswith("vt.") or l.startswith("abbr.") or l.startswith("abbrv.") or l.startswith("prep.") \
                    or l.startswith("【搭配】") or l.startswith("【同根】") or l.startswith("【同义】") \
                    or l.startswith("【参考】") or l.startswith("【反义】"):
                    res[-1] = res[-1] + " " + l
                    continue
                if "【记忆】" not in l:
                    res.append(l)
                #print(res[-1])
    
    res_new = []
    line_tp = ""
    for r in res:
        if not_chinese(r):
            line_tp = "en"
            r += " eng_flag"
        elif line_tp == "en" and is_all_chinese(r):
            res_new[-1] = res_new[-1].replace("eng_flag", "")
            res_new[-1] = res_new[-1] + " " + r
            line_tp = ""
            continue
        if len(res_new) > 0 and r in res_new[-1]:
            continue
        res_new.append(r)

    res_new_new = []
    word_pre = ""
    for r in res_new:
        if r.endswith("eng_flag"): r = r.replace("eng_flag", "")
        word = ""
        if "/" in r: 
            word = r.split("/")[0]
            word_pre = word
        else:
            # 判断r中是否全部都是中文
            if is_all_chinese(r):
                continue
                print(r)
            if not_chinese(r):
                continue
                print(r)
            else:
                #print(r)
                continue
                pass
        res_new_new.append(r)

    idx = 0
    merged_dir = pre_dir + 'merged_results'
    with open(os.path.join(merged_dir, 'merged_ocr_results_core_words.txt'), 'w', encoding='utf-8') as fw:
        for r in res_new_new:
            idx += 1
            print(f"{idx}: {r}")
            fw.write(r)
            fw.write('\n')

if __name__ == "__main__":
    if sys.argv[1] == "multi":
        multi_process()
    elif sys.argv[1] == "single":
        multi_process(1)
    elif sys.argv[1] == "merge":
        merge_files()
    elif sys.argv[1] == "process":
        process_text()