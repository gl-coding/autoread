import os,sys,time,multiprocessing
from llm_prompt import *
from llm_utils import *

pre_dir = os.path.basename(sys.argv[0]).split(".")[0].split("_")[1] + "/"
print("pre_dir:", pre_dir)

class ProcessZhuan8(ProcessClass):
    def __init__(self, pre_dir):
        super().__init__(pre_dir)
    
    #处理音标部分，音标和单词在同一行
    def process_yinbiao(self):
        res_in = self.res_all[-1]
        pre_line = ""
        res_out = []
        for r in res_in:
            #音标部分合并上一行
            if r.startswith("[") and "]" in r and len(res_out) > 0:
                res_out[-1] = res_out[-1] + " " + r
            else:
                res_out.append(r)
            pre_line = r
        #for item in res_out[:10]: print(item)
        self.res_all.append(res_out)
    
    #合并当前行数据到上一行
    def process_phrase(self):
        res_in = self.res_all[-1]
        pre_line = ""
        res_out = []
        for r in res_in:
            if r and r[0].isupper():
                r_list = list(r)
                r_list[0] = r_list[0].lower()
                r = "".join(r_list)
            #取第一个单词，进行后续的逻辑判断
            first_word = r.split(" ")[0].strip()
            #if first_word.endswith(".") and not first_word.endswith("..") and not_chinese(first_word): print(r)
            if len(r) > 2 and r[1] == ' ' and (is_all_chinese(r[0]) or r[0] == '□'): 
                r = r[1:].strip()
            if r.startswith("[") and "]" in r and len(res_out) > 0:
                res_out[-1] = res_out[-1] + " " + r
                continue
            flag = False
            for key in ["词根记忆", "联想记忆", "词源记忆", "组合词:", "例", "相关词", "记忆", "来自", "构词", "例", \
                "短语", "词根", "派生", "相关词", "记忆", "衍生词", "习语", "短语", "派生", "本身为词根"]:
                for sep in ["", ":", "："]:
                    new_key = key + sep
                    if r.startswith(new_key):
                        flag = True
                        idx = r.find(new_key)
                        r = r[idx:]
                        res_out[-1] = res_out[-1] + "; " + r
                        break
                if flag: break
            if flag: continue
            if r.startswith("/"): #//音标上移
                res_out[-1] = res_out[-1] + " " + r
                continue
            if first_word.endswith(".") and not first_word.endswith("..") and not_chinese(first_word):
                res_out[-1] = res_out[-1] + " " + r
                continue
            res_out.append(r)
            pre_line = r
        self.res_all.append(res_out)

    def process(self):
        self.process_text()
        #self.process_yinbiao()
        self.process_phrase()
        self.write_to_file()

if __name__ == "__main__":
    if sys.argv[1] == "multi":
        multi_process()
    elif sys.argv[1] == "single":
        multi_process(1)
    elif sys.argv[1] == "merge":
        merge_files()
    elif sys.argv[1] == "process":
        process_class = ProcessZhuan8(pre_dir)
        process_class.process()