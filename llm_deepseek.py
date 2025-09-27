from openai import OpenAI
from dotenv import load_dotenv
import os,sys,time,multiprocessing
from llm_ollama import *
load_dotenv()

pre_dir = "prideAndPrejudice/"

client = OpenAI(
    base_url="https://api.deepseek.com/",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

def correct_article(topic):
    completion = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=[
            {
                    "role": "system",
                    "content": "你是一个英文专业词汇书文本校对助手。输入文本是《傲慢与偏见》的英文原著识别结果，请严格按照以下要求处理文本：\
                        1. 任务要求：\
                            - 逐行修改原文内容\
                            - 修正错误单词，确保每个单词都是正确的\
                            - 修正错误标点符号，确保标点符号正确\
                            - 修正错误语法，确保语法正确\
                            - 删除与上下文没有联系的识别结果\
                        2. 输入文本： {text}\
                        3. 输出格式要求：\
                            - 原文内容\
                            - ==============================\
                            - 修改后的内容\
                        4. 注意：\
                            - 必须严格按照上述格式输出\
                            - 原文部分必须完全复制输入文本\
                            - 不要添加任何额外的解释或说明，包括额外的[原文内容]、[修改后的内容]\
                ".format(text=topic)
            },
            {
                    "role": "user",
                    "content": "请帮我校对“" + topic + "”这篇文章的识别结果"
            }
        ]
    )

    res = completion.choices[0].message.content
    return res

def correct_words_book(topic):
    completion = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=[
            {
                    "role": "system",
                    "content": "你是一个英文专业词汇书文本校对助手。输入文本是一个英文专业词汇书的识别结果，请严格按照以下要求处理文本：\
                        1. 任务要求：\
                            - 逐行修改原文内容\
                            - 修正错误单词，确保每个单词都是正确的\
                            - 添加或修正标点符号，单词和词性都正确\
                            - 针对单词的音标修正音标，确保音标正确\
                            - 去掉一些内容，如：”随时阅读“、”review“、”加入书架“等\
                        2. 输入文本： {text}\
                        3. 输出格式要求：\
                            - 原文内容\
                            - ==============================\
                            - 修改后的内容\
                        4. 注意：\
                            - 必须严格按照上述格式输出\
                            - 原文部分必须完全复制输入文本\
                            - 不要添加任何额外的解释或说明，包括额外的[原文内容]、[修改后的内容]\
                ".format(text=topic)
            },
            {
                    "role": "user",
                    "content": "请帮我校对“" + topic + "”这篇文章的识别结果"
            }
        ]
    )

    res = completion.choices[0].message.content
    return res

def trans_words(topic):
    completion = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=[
            {
                    "role": "system",
                    "content": "你是一位英文翻译助手，擅长将英文单词、短语或句子翻译成中文，如果有多个意思，请用“，”分割。\
                    1. 输入文本： {text}\
                    2. 输出格式要求：\
                        - 只输出翻译后的文本，不要添加任何额外的解释或说明/no_think\
                    ".format(text=topic)
            },
            {
                    "role": "user",
                    "content": "请帮我翻译“" + topic + "”"
            }
        ]
    )

    res = completion.choices[0].message.content
    return res

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
    
    res = correct_article(text)
    print(res)
    print(f"耗时: {time.time() - st}秒")
    return res

def multi_process():
    #python 多进程处理ocr_results目录下的所有txt文件,并行处理
    cpu_count = 30
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
    if sys.argv[1] == "mult":
        multi_process()
    elif sys.argv[1] == "merge":
        merge_files()
    elif sys.argv[1] == "process":
        process_text()