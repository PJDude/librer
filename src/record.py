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

#from signal import signal,SIGINT,CTRL_C_EVENT,SIGTERM,SIGABRT

from core import *

#if windows:
#    from signal import SIGBREAK

import logging

l_info = logging.info
l_warning = logging.warning
l_error = logging.error

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

    file_group = parser.add_argument_group()

    file_group.add_argument('-fre'  ,'--file_regexp',type=str,help='serch files by regular expression')

    #file_glob_group = file_group.add_argument_group('file name glob matching')
    file_group.add_argument('-fg'   ,'--file_glob',type=str,help='serch files by glob expression')
    file_group.add_argument('-fgcs' ,'--file_case_sensitive',action='store_true',help='serch files by case sensitive glob expression')

    #file_fuzzy_group = file_group.add_argument_group('file name fuzzy matching')
    file_group.add_argument('-ff'   ,'--file_fuzzy',type=str,help='serch files by fuzzy match with threshold')
    file_group.add_argument('-fft'  ,'--file_fuzzy_threshold', type=float,help='threshold value')

    file_group.add_argument('-fe'   ,'--file_error',action='store_true',help='serch files with error on access')

    cd_group = parser.add_argument_group()
    cd_group.add_argument('-cdw','--cd_without',action='store_true',help='serch for riles without custom data')
    cd_group.add_argument('-cdok','--cd_ok',action='store_true',help='serch for riles with correct custom data')
    cd_group.add_argument('-cderror','--cd_error',action='store_true',help='serch for riles with error status on custom data extraction')

    cd_group.add_argument('-cdre'   ,'--cd_regexp',type=str,help='serch by regular expression on custom data')

    #cd_glob_group = file_group.add_argument_group('Custom data glob matching')
    cd_group.add_argument('-cdg'    ,'--cd_glob',type=str,help='serch by glob expression on custom data')
    cd_group.add_argument('-cdgcs'  ,'--cd_case_sensitive',action='store_true',help='serch by case sensitive glob expression on custom data')

    #cd_fuzzy_group = cd_group.add_argument_group('Custom data fuzzy matching')
    cd_group.add_argument('-cdf'    ,'--cd_fuzzy',type=str,help='serch by fuzzy match with threshold on custom data')
    cd_group.add_argument('-cdft'   ,'--cd_fuzzy_threshold',type=float,help='threshold value on custom data')

    parser.add_argument('-min','--size_min',type=str,help='minimum size')
    parser.add_argument('-max','--size_max',type=str,help='maximum size')

    parser.add_argument('-tmin','--timestamp_min',type=str,help='minimum modification timestamp')
    parser.add_argument('-tmax','--timestamp_max',type=str,help='maximum modification timestamp')

    return parser.parse_args()

def find_params_check(self,
        size_min,size_max,
        find_filename_search_kind,name_expr,name_case_sens,
        find_cd_search_kind,cd_expr,cd_case_sens,
        file_fuzzy_threshold,cd_fuzzy_threshold):


    if find_filename_search_kind == 'fuzzy':
        if name_expr:
            try:
                float(file_fuzzy_threshold)
            except ValueError:
                return f"wrong threshold value:{file_fuzzy_threshold}"
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
stdout_data_last_not_printed=None
stdout_data_queue_print_time=0

def print_func(data,always=False):
    now=perf_counter()
    global stdout_data_queue_print_time
    global stdout_data_last_not_printed
    if now>stdout_data_queue_print_time or always:
        stdout_data_queue.append(data)
        stdout_data_queue_print_time=now+0.1
        stdout_data_last_not_printed=None
    else:
        stdout_data_last_not_printed=data

def print_func_always(data):
    stdout_data_queue.append(data)

def printer_stop():
    stdout_data_queue.append(True)

def printer():
    stdout_data_queue_get = stdout_data_queue.popleft

    last_print_time=0
    global stdout_data_last_not_printed
    try:
        while True:
            if stdout_data_queue:
                result=stdout_data_queue_get()
                if result==True:
                    break
                print(json_dumps(result),flush=True)
                last_print_time=time()
            else:
                sleep(0.01)
                if stdout_data_last_not_printed:
                    if time()>last_print_time+0.5:
                        print(json_dumps(stdout_data_last_not_printed),flush=True)
                        stdout_data_last_not_printed=None
    except Exception as pe:
        print_info(f'printer error:{pe}')

    sys.exit(0) #thread

abort_list=[False,False]

def check_abort(signal_file):
    while True:
        if path_exists(signal_file):
            try:
                with open(signal_file,'r') as sf:
                    got_int = int(sf.read().strip())

                    print_info(f'got abort int:{got_int}')

                    global abort_list
                    abort_list[got_int]=True

                remove(signal_file)

            except Exception as pe:
                print_info(f'check_abort error:{pe}')
        else:
            sleep(0.1)

    sys.exit(0) #thread

def print_info(*args):
    print('#',*args)

if __name__ == "__main__":
    VER_TIMESTAMP = get_ver_timestamp()

    args=parse_args(VER_TIMESTAMP)
    comm_dir=args.comm_dir

    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s', filename='record-temp.log',filemode='w')

    gc_disable()

    printer_thread = Thread(target=printer,daemon=True)
    printer_thread.start()

    signal_file = sep.join([comm_dir,SIGINT_FILE])

    abort_thread = Thread(target=lambda : check_abort(signal_file),daemon=True)
    abort_thread.start()

    if args.command == 'search':
        #####################################################################
        record = LibrerRecord('nowy','sciezka','./record.log')
        record.load(args.file)
        print_info(f'record label:{record.header.label}')
        print_info(f'{comm_dir=}')
        if comm_dir:
            try:
                with open(sep.join([comm_dir,SEARCH_DAT_FILE]),"rb") as f:
                    params = loads(ZstdDecompressor().decompress(f.read()))
                    print_info(f'{params=}')
            except Exception as e:
                print_info(e)
                exit(2)
            else:
                (size_min,size_max,t_min,t_max,find_filename_search_kind,name_expr,name_case_sens,find_cd_search_kind,cd_expr,cd_case_sens,filename_fuzzy_threshold,cd_fuzzy_threshold) = params

        name_case_sens=args.file_case_sensitive
        cd_case_sens=args.cd_case_sensitive

        name_regexp=args.file_regexp
        name_glob=args.file_glob
        name_fuzzy=args.file_fuzzy
        file_error=args.file_error

        file_fuzzy_threshold = args.file_fuzzy_threshold
        cd_fuzzy_threshold = args.cd_fuzzy_threshold

        if name_regexp:
            if res := test_regexp(name_regexp):
                exit(res)

            re_obj_name=re_compile(name_regexp)
            name_func_to_call = lambda x : re_obj_name.match(x)
            name_search_kind='regexp'
        elif name_glob:
            if name_case_sens:
                re_obj_name=re_compile(translate(name_glob))
                name_func_to_call = lambda x : re_obj_name.match(x)
            else:
                re_obj_name=re_compile(translate(name_glob), IGNORECASE)
                name_func_to_call = lambda x : re_obj_name.match(x)
            name_search_kind='glob'
        elif name_fuzzy:
            name_func_to_call = lambda x : bool(SequenceMatcher(None, name_fuzzy, x).ratio()>file_fuzzy_threshold)
            name_search_kind='fuzzy'
        elif file_error:
            name_func_to_call = None
            name_search_kind='error'

        else:
            name_func_to_call = None
            name_search_kind='dont'

        custom_data_needed=False

        cd_without=args.cd_without
        cd_error=args.cd_error
        cd_ok=args.cd_ok

        cd_regexp=args.cd_regexp
        cd_glob=args.cd_glob
        cd_fuzzy=args.cd_fuzzy

        if cd_regexp:
            custom_data_needed=True
            cd_search_kind='regexp'
            if res := test_regexp(cd_regexp):
                exit(res)
            re_obj_cd=re_compile(cd_regexp, MULTILINE | DOTALL)
            cd_func_to_call = lambda x : re_obj_cd.match(x)

        elif cd_glob:
            custom_data_needed=True
            cd_search_kind='glob'
            if cd_case_sens:
                re_obj_cd=re_compile(translate(cd_glob), MULTILINE | DOTALL)
                cd_func_to_call = lambda x : re_obj_cd.match(x)
            else:
                re_obj_cd=re_compile(translate(cd_glob), MULTILINE | DOTALL | IGNORECASE)
                cd_func_to_call = lambda x : re_obj_cd.match(x)
        elif cd_fuzzy:
            custom_data_needed=True
            cd_search_kind='fuzzy'
            cd_func_to_call = lambda x : bool(SequenceMatcher(None,cd_fuzzy, x).ratio()>cd_fuzzy_threshold)
        elif cd_without:
            cd_search_kind='without'
            cd_func_to_call = None
        elif cd_error:
            cd_search_kind='error'
            cd_func_to_call = None
        elif cd_ok:
            cd_search_kind='any'
            cd_func_to_call = None
        else:
            cd_search_kind='dont'
            cd_func_to_call = None

        #####################################################################
        t0 = perf_counter()
        record.decompress_filestructure()

        if custom_data_needed:
            record.decompress_customdata()

        print_info('search start')
        t1 = perf_counter()

        size_min=str_to_bytes(args.size_min) if args.size_min else None
        size_max=str_to_bytes(args.size_max) if args.size_max else None

        timestamp_min=int(args.timestamp_min) if args.timestamp_min else None
        timestamp_max=int(args.timestamp_max) if args.timestamp_max else None

        print_info(f'args:{args}')

        try:
            record.find_items(print_func_always,abort_list,
                    size_min,size_max,
                    timestamp_min,timestamp_max,
                    name_search_kind,name_func_to_call,
                    cd_search_kind,cd_func_to_call,
                    print_info)
        except Exception as fe:
            print_info('find_items error:' + str(fe))

        t2 = perf_counter()
        print_info(f'finished. times:{t1-t0},{t2-t1}')
        ###################################################################
    elif args.command == 'create':
        if comm_dir:
            try:
                with open(sep.join([comm_dir,SCAN_DAT_FILE]),"rb") as f:
                    create_list = loads(ZstdDecompressor().decompress(f.read()))

                label,path_to_scan,check_dev,cde_list = create_list
            except Exception as e:
                print_info(e)
                exit(2)
            else:
                new_record = LibrerRecord(logging,label=label,scan_path=path_to_scan)

                try:
                    print_func(['stage',0],True)
                    new_record.scan(print_func,abort_list,tuple(cde_list),check_dev)
                except Exception as fe:
                    print_info(f'scan error:{fe}')
                else:
                    if not abort_list[0]:
                        if cde_list :
                            try:
                                print_func(['stage',1],True)
                                new_record.extract_customdata(print_func,abort_list)
                            except Exception as cde:
                                print_info(f'cde error:{cde}')

                        print_func(['stage',2],True)
                        new_record.pack_data(print_func)
                        print_func(['stage',3],True)
                        new_record.save(print_func,file_path=args.file,compression_level=9)
                        print_func(['stage',4],True)

        #####################################################################
    else:
        print_info(f'parse problem. command:{args.command}')
        exit(1)

    printer_stop()
    printer_thread.join()
    sys.exit(0)

