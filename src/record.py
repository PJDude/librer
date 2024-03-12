#!/usr/bin/python3

####################################################################################
#
#  Copyright (c) 2023-2024 Piotr Jochymek
#
#  MIT License
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
####################################################################################

import sys

from os.path import dirname,join as path_join,exists as path_exists
from os import name as os_name,remove

from gc import disable as gc_disable

from pathlib import Path as pathlib_Path
from argparse import ArgumentParser,RawTextHelpFormatter

from time import sleep,perf_counter,time

from threading import Thread

from re import compile as re_compile,IGNORECASE,MULTILINE,DOTALL
from fnmatch import translate
from difflib import SequenceMatcher

from json import dumps as json_dumps
from collections import deque

from core import *

VERSION_FILE='version.txt'

def get_ver_timestamp():
    try:
        timestamp=pathlib_Path(path_join(dirname(__file__),VERSION_FILE)).read_text(encoding='ASCII').strip()
    except Exception as e_ver:
        print(e_ver)
        timestamp=''
    return timestamp

def parse_args(ver):
    parser = ArgumentParser(
            formatter_class=RawTextHelpFormatter,
            prog = 'record.exe' if (os_name=='nt') else 'record',
            description = f"librer record version {ver}\nCopyright (c) 2023-2024 Piotr Jochymek\n\nhttps://github.com/PJDude/librer",
            )

    parser.add_argument('command',type=str,help='command to execute',choices=('create','search'))

    parser.add_argument('file',type=str,help='record dat file')

    parser.add_argument('comm_dir',type=str,help='internal communication dir')

    return parser.parse_args()

def find_params_check(self,
        size_min,size_max,
        find_filename_search_kind,name_expr,name_case_sens,
        find_cd_search_kind,cd_expr,cd_case_sens,
        filename_fuzzy_threshold,cd_fuzzy_threshold):

    if find_filename_search_kind == 'fuzzy':
        if name_expr:
            try:
                float(filename_fuzzy_threshold)
            except ValueError:
                return f"wrong threshold value:{filename_fuzzy_threshold}"
        else:
            return "empty file expression"

    if find_cd_search_kind == 'fuzzy':
        if cd_expr:
            try:
                float(cd_fuzzy_threshold)
            except ValueError:
                return f"wrong threshold value:{cd_fuzzy_threshold}"
        else:
            return "empty cd expression"

    return None

stdout_data_queue=deque()
stdout_data_queue_append = stdout_data_queue.append

def print_func(data,always=False):
    stdout_data_queue_append( (data,always) )

def print_func_always(data):
    print_func(data,True)

abort_list=[False,False]

def caretaker(signal_file):
    stdout_data_queue_get = stdout_data_queue.popleft

    next_signal_file_check=0
    next_time_print=0

    global abort_list

    print_min_time_period=0.1
    signal_file_check_period=0.5
    last_data_not_printed=None

    sys_stdout_flush = sys.stdout.flush
    lines_non_stop=0

    json_dumps_loc = json_dumps
    stdout_data_queue_loc = stdout_data_queue
    path_exists_loc = path_exists

    def flush_last_data_not_printed(flush):
        nonlocal last_data_not_printed
        if last_data_not_printed:
            print(json_dumps_loc(last_data_not_printed),flush=flush)
            last_data_not_printed=None

    while True:
        now=perf_counter()
        now_grater_than_next_time_print = bool(now>next_time_print)

        if stdout_data_queue_loc:
            data,always=stdout_data_queue_get()

            if data==True:
                break

            if always:
                flush_last_data_not_printed(False)

            if always or now_grater_than_next_time_print:
                print(json_dumps_loc(data),flush=True)
                next_time_print=now+print_min_time_period
                lines_non_stop+=1
                last_data_not_printed=None
            else:
                last_data_not_printed=data

            if lines_non_stop<128:
                continue

        lines_non_stop=0

        if now_grater_than_next_time_print:
            flush_last_data_not_printed(True)

        if now>next_signal_file_check:
            next_signal_file_check=now+signal_file_check_period
            if path_exists_loc(signal_file):
                try:
                    with open(signal_file,'r') as sf:
                        got_int = int(sf.read().strip())
                        print_info(f'got abort int:{got_int}')
                        abort_list[got_int]=True
                    remove(signal_file)

                except Exception as pe:
                    print_info(f'check_abort error:{pe}')

        sleep(0.001)

    sys.exit(0) #thread

def print_info(*args):
    print('#',*args)

def proper_exit(code):
    stdout_data_queue_append( (True,True) )
    caretaker_thread.join()
    sys.exit(code)

if __name__ == "__main__":
    VER_TIMESTAMP = get_ver_timestamp()

    args=parse_args(VER_TIMESTAMP)
    comm_dir=args.comm_dir

    gc_disable()

    caretaker_thread = Thread(target=lambda : caretaker(sep.join([comm_dir,SIGNAL_FILE])),daemon=False)
    caretaker_thread.start()

    if args.command == 'search':
        #####################################################################
        record = LibrerRecord()
        load_result=record.load(args.file)
        if load_result:
            print_info(f'load error:{load_result}')
            proper_exit(3)

        print_info(f'record label:{record.header.label}')
        print_info(f'{comm_dir=}')
        if comm_dir:
            try:
                with open(sep.join([comm_dir,SEARCH_DAT_FILE]),"rb") as f:
                    params = loads(ZstdDecompressor().decompress(f.read()))
                    print_info(f'{params=}')
            except Exception as e:
                print_info(f'search error:{e}')
                proper_exit(2)

            (size_min,size_max,t_min,t_max,find_filename_search_kind,name_expr,name_case_sens,find_cd_search_kind,cd_expr,cd_case_sens,filename_fuzzy_threshold_str,cd_fuzzy_threshold_str) = params

            try:
                filename_fuzzy_threshold = float(filename_fuzzy_threshold_str)
            except Exception as ce:
                filename_fuzzy_threshold = 0.0

            try:
                cd_fuzzy_threshold = float(cd_fuzzy_threshold_str)
            except Exception as ce:
                cd_fuzzy_threshold = 0.0

            name_regexp=bool(find_filename_search_kind == 'regexp')
            name_glob=bool(find_filename_search_kind == 'glob')
            name_fuzzy=bool(find_filename_search_kind == 'fuzzy')
            file_error=bool(find_filename_search_kind == 'error')

            if name_regexp:
                if res := test_regexp(name_expr):
                    proper_exit(res)

                re_obj_name=re_compile(name_expr)
                name_func_to_call = lambda x : re_obj_name.match(x)
                name_search_kind='regexp'
            elif name_glob:
                if name_case_sens:
                    re_obj_name=re_compile(translate(name_expr))
                    name_func_to_call = lambda x : re_obj_name.match(x)
                else:
                    re_obj_name=re_compile(translate(name_expr), IGNORECASE)
                    name_func_to_call = lambda x : re_obj_name.match(x)
                name_search_kind='glob'
            elif name_fuzzy:
                name_func_to_call = lambda x : bool(SequenceMatcher(None, name_expr, x).ratio()>filename_fuzzy_threshold)
                name_search_kind='fuzzy'
            elif file_error:
                name_func_to_call = None
                name_search_kind='error'

            else:
                name_func_to_call = None
                name_search_kind='dont'

            custom_data_needed=False

            cd_regexp=bool(find_cd_search_kind=='regexp')
            cd_glob=bool(find_cd_search_kind=='glob')
            cd_fuzzy=bool(find_cd_search_kind=='fuzzy')
            cd_error=bool(find_cd_search_kind=='error')
            cd_empty=bool(find_cd_search_kind=='empty')
            cd_aborted=bool(find_cd_search_kind=='aborted')
            cd_without=bool(find_cd_search_kind=='without')
            cd_ok=bool(find_cd_search_kind=='any')

            if cd_regexp:
                custom_data_needed=True
                if res := test_regexp(cd_expr):
                    proper_exit(res)
                re_obj_cd=re_compile(cd_expr, MULTILINE | DOTALL)
                cd_func_to_call = lambda x : re_obj_cd.match(x)

            elif cd_glob:
                custom_data_needed=True
                if cd_case_sens:
                    re_obj_cd=re_compile(translate(cd_expr), MULTILINE | DOTALL)
                    cd_func_to_call = lambda x : re_obj_cd.match(x)
                else:
                    re_obj_cd=re_compile(translate(cd_expr), MULTILINE | DOTALL | IGNORECASE)
                    cd_func_to_call = lambda x : re_obj_cd.match(x)
            elif cd_fuzzy:
                custom_data_needed=True
                cd_func_to_call = lambda x : bool(SequenceMatcher(None,cd_expr, x).ratio()>cd_fuzzy_threshold)
            elif cd_without:
                cd_func_to_call = None
            elif cd_empty:
                cd_func_to_call = None
            elif cd_error:
                cd_func_to_call = None
            elif cd_ok:
                cd_func_to_call = None
            else:
                #cd_search_kind='dont'
                cd_func_to_call = None

            #####################################################################
            t0 = perf_counter()
            record.decompress_filestructure()

            if custom_data_needed:
                record.decompress_customdata()

            print_info('search start')
            t1 = perf_counter()

            print_info(f'args:{args}')

            try:
                record.find_items(print_func_always,
                        size_min,size_max,
                        t_min,t_max,
                        name_search_kind,name_func_to_call,
                        find_cd_search_kind,cd_func_to_call,
                        print_info)
            except Exception as fe:
                print_info(f'find_items error:{fe}')

            t2 = perf_counter()
            print_info(f'finished. times:{t1-t0},{t2-t1}')
            ###################################################################

    elif args.command == 'create':
        if comm_dir:
            try:
                with open(sep.join([comm_dir,SCAN_DAT_FILE]),"rb") as f:
                    create_list = loads(ZstdDecompressor().decompress(f.read()))

                label,path_to_scan,check_dev,compression_level,threads,cde_list = create_list
            except Exception as e:
                print_info(f'create error:{e}')
                proper_exit(2)
            else:
                new_record = LibrerRecord(label=label,scan_path=path_to_scan)

                try:
                    print_func(('stage',0),True)
                    new_record.scan(print_func,abort_list,tuple(cde_list),check_dev)
                except Exception as fe:
                    print_info(f'scan error:{fe}')
                else:
                    if not abort_list[0]:
                        if cde_list :
                            try:
                                print_func(('stage',1),True)
                                new_record.extract_customdata(print_func,abort_list,threads=threads)
                            except Exception as cde:
                                print_info(f'cde error:{cde}')

                        print_func(('stage',2),True)
                        new_record.pack_data(print_func)
                        print_func(('stage',3),True)
                        new_record.save(print_func,file_path=args.file,compression_level=compression_level)
                        print_func(('stage',4),True)

        #####################################################################
    else:
        print_info(f'parse problem. command:{args.command}')
        proper_exit(1)

    proper_exit(0)

