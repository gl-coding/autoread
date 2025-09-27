from openai import OpenAI
from dotenv import load_dotenv
import os,sys,time,multiprocessing
load_dotenv()

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


def write_article(topic):
    completion = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=[
            {
                    "role": "system",
                    "content": "你是一位文本大纲生成专家，擅长根据用户的需求创建一个有条理且易于扩展成完整文章的大纲，你拥有强大的主题分析能力，能准确提取关键信息和核心要点。具备丰富的文案写作知识储备，熟悉各种文体和题材的文案大纲构建方法。可根据不同的主题需求，如商业文案、文学创作、学术论文等，生成具有针对性、逻辑性和条理性的文案大纲，并且能确保大纲结构合理、逻辑通顺。该大纲应该包含以下部分：\n引言：介绍主题背景，阐述撰写目的，并吸引读者兴趣。\n主体部分：第一段落：详细说明第一个关键点或论据，支持观点并引用相关数据或案例。\n第二段落：深入探讨第二个重点，继续论证或展开叙述，保持内容的连贯性和深度。\n第三段落：如果有必要，进一步讨论其他重要方面，或者提供不同的视角和证据。\n结论：总结所有要点，重申主要观点，并给出有力的结尾陈述，可以是呼吁行动、提出展望或其他形式的收尾。\n创意性标题：为文章构思一个引人注目的标题，确保它既反映了文章的核心内容又能激发读者的好奇心。"
            },
            {
                    "role": "user",
                    "content": "请帮我生成“" + topic + "”这篇文章的大纲"
            }
        ]
    )

    res = completion.choices[0].message.content
    return res

def write_file(filename):
    text_path = os.path.join('ocr_results', filename)
    if not text_path.endswith('.txt'):
        return
    
    res = single_process(text_path)
    correct_dir = 'correct_results'
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
    cpu_count = os.cpu_count()
    cpu_count = 20
    print(f"cpu_count: {cpu_count}")
    
    # 创建输出目录
    correct_dir = 'correct_results'
    if os.path.exists(correct_dir):
        import shutil
        shutil.rmtree(correct_dir)  # 删除目录及其内容
    os.makedirs(correct_dir, exist_ok=True)
    
    # 只处理.txt文件
    txt_files = [f for f in os.listdir('ocr_results') if f.endswith('.txt')]
    print(f"找到 {len(txt_files)} 个txt文件")
    
    with multiprocessing.Pool(processes=cpu_count) as pool:
        pool.map(write_file, txt_files)

def merge_files():
    correct_dir = 'correct_results'
    files = [f for f in os.listdir(correct_dir) if f.endswith('.txt')]
    files.sort()
    if not os.path.exists('merged_results'):
        os.makedirs('merged_results')
    with open('merged_results/merged_ocr_results.txt', 'w', encoding='utf-8') as fw:
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
    print(f"合并完成！输出文件：{correct_dir}/merged_ocr_results.txt")

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
    with open('merged_results/merged_ocr_results.txt', 'r', encoding='utf-8') as f:
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
            res_new[-1] = res_new[-1] + " " + r
            line_tp = ""
            continue
        if len(res_new) > 0 and r in res_new[-1]:
            continue
        res_new.append(r)

    idx = 0
    with open('merged_results/merged_ocr_results_core_words.txt', 'w', encoding='utf-8') as fw:
        for r in res_new:
            idx += 1
            print(f"{idx}: {r}")
            fw.write(r)
            fw.write('\n')

if __name__ == "__main__":
    #multi_process()
    #merge_files()
    process_text()