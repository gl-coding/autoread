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
    
    def process_phrase(self):
        res_in = self.res_all[-1]
        pre_line = ""
        res_out = []
        for r in res_in:
            if len(r) > 2 and r[1] == ' ' and (is_all_chinese(r[0]) or r[0] == '□'): 
                r = r[1:].strip()
            if "词根记忆" in r:
                idx = r.find("词根记忆")
                r = r[idx:]
                res_out[-1] = res_out[-1] + "; " + r
            elif "联想记忆" in r:
                idx = r.find("联想记忆")
                r = r[idx:]
                res_out[-1] = res_out[-1] + "; " + r
            elif r.startswith("/"): #//音标上移
                res_out[-1] = res_out[-1] + " " + r
            else:
                res_out.append(r)
            pre_line = r
        self.res_all.append(res_out)

    def process(self):
        self.process_text()
        self.process_yinbiao()
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