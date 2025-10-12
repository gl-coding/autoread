import os,sys,time,multiprocessing
from llm_prompt import *
from llm_utils import *

class ProcessZhuan8(ProcessClass):
    def __init__(self, pre_dir):
        super().__init__(pre_dir)

    def process(self):
        self.process_text()
        self.res_final = self.res_fromfile
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