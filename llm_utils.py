import os,time,multiprocessing
from llm_prompt import *

prompt_dict = {
    "100words/": "correct_words_book",
    "zhuan8/": "correct_words_book",
    "prideAndPrejudice/": "correct_article"
}

#pre_dir = "prideAndPrejudice/"
#pre_dir = "100words/"
pre_dir = "zhuan8/"
prompt_name = prompt_dict[pre_dir]

def is_all_chinese(l):
    for char in l:
        if not (('\u4e00' <= char <= '\u9fff') or 
                ('\u3400' <= char <= '\u4dbf') or
                char in '，、。！？；：「」『』（）【】《》.；“”：; (){}[]":，'):
            return False
    return True

def not_chinese(l):
    for char in l:
        if '\u4e00' <= char <= '\u9fff':
            return False
    return True

def write_file(filename):
    text_path = os.path.join(pre_dir + 'ocr_results', filename)
    if not text_path.endswith('.txt'):
        return
    
    res = single_process(text_path)
    correct_dir = pre_dir + 'correct_results'
    with open(os.path.join(correct_dir, filename), 'w', encoding='utf-8') as f:
        f.write(res)
    print(f"处理完成------: {filename}")

def single_process(text):
    st = time.time()
    if os.path.exists(text):
        with open(text, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = text
    
    prompt_obj = Prompt()
    res = getattr(prompt_obj, prompt_name)(text)
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