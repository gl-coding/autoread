import os,sys,time,multiprocessing
from llm_prompt import *
from llm_utils import *

class ProcessZhuan8(ProcessClass):
    def __init__(self, pre_dir):
        super().__init__(pre_dir)
    
    #处理音标部分
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

    def process(self):
        self.process_text()
        self.process_yinbiao()
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