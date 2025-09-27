import os,sys,time,multiprocessing
from llm_prompt import *

pre_dir = "prideAndPrejudice/"

def write_file(filename):
    text_path = os.path.join(pre_dir + 'ocr_results', filename)
    if not text_path.endswith('.txt'):
        return
    
    res = single_process(text_path)
    correct_dir = pre_dir + 'correct_results'
    with open(os.path.join(correct_dir, filename), 'w', encoding='utf-8') as f:
        f.write(res)
    print(f"处理完成: {filename}")

def single_process(text):
    st = time.time()
    if os.path.exists(text):
        with open(text, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = text
    
    prompt_obj = Prompt()
    res = getattr(prompt_obj, "correct_article")(text)
    #res = prompt_obj.correct_article(text)
    print(res)
    print(f"耗时: {time.time() - st}秒")
    return res

def multi_process(cpu_count=30):
    #python 多进程处理ocr_results目录下的所有txt文件,并行处理
    #cpu_count = 1
    print(f"cpu_count: {cpu_count}")
    
    # 创建输出目录
    correct_dir = pre_dir + 'correct_results'
    if os.path.exists(correct_dir):
        import shutil
        shutil.rmtree(correct_dir)  # 删除目录及其内容
    os.makedirs(correct_dir, exist_ok=True)
    
    # 只处理.txt文件
    ocr_dir = pre_dir + 'ocr_results'
    txt_files = [f for f in os.listdir(ocr_dir) if f.endswith('.txt')]
    print(f"找到 {len(txt_files)} 个txt文件")
    
    with multiprocessing.Pool(processes=cpu_count) as pool:
        pool.map(write_file, txt_files)

def merge_files():
    correct_dir = pre_dir + 'correct_results'
    files = [f for f in os.listdir(correct_dir) if f.endswith('.txt')]
    files.sort()
    merged_dir = pre_dir + 'merged_results'
    if not os.path.exists(merged_dir):
        os.makedirs(merged_dir)
    with open(os.path.join(merged_dir, 'merged_ocr_results.txt'), 'w', encoding='utf-8') as fw:
        for file in files:
            print(file)
            with open(os.path.join(correct_dir, file), 'r', encoding='utf-8') as f:
                line = f.read()
                line = line.split('==============================')[1]
                content = ""
                for l in line.split('\n'):
                    if l.strip():
                        content += l.strip() + '\n'
                line = content
                print(line)
                fw.write(line)
    print(f"合并完成！输出文件：{merged_dir}/merged_ocr_results.txt")

def process_text():
    def is_all_chinese(l):
        for char in l:
            if not (('\u4e00' <= char <= '\u9fff') or 
                    ('\u3400' <= char <= '\u4dbf') or
                    char in '，、。！？；：「」『』（）【】《》.；“”：; (){}[]'):
                return False
        return True

    def not_chinese(l):
        for char in l:
            if '\u4e00' <= char <= '\u9fff':
                return False
        return True
    
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

    idx = 0
    merged_dir = pre_dir + 'merged_results'
    with open(os.path.join(merged_dir, 'merged_ocr_results_core_words.txt'), 'w', encoding='utf-8') as fw:
        for r in res_new:
            idx += 1
            if r.endswith("eng_flag"):
                r = r.replace("eng_flag", "")
                #ch_r = func_call(r, MODEL_NAME, "translate")
                ch_r = trans_words(r)
                r = r + " " + ch_r
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