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

from os.path import dirname,join as path_join
from os import name as os_name

from pathlib import Path as pathlib_Path
from argparse import ArgumentParser,RawTextHelpFormatter

from time import sleep,perf_counter

from threading import Thread

from re import compile as re_compile,search as re_search,IGNORECASE
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

    parser.add_argument('command',type=str,help='command to execute',choices=('load','search','info'))

    parser.add_argument('file',type=str,help='dat file')

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

results_queue=deque()

def printer():
    results_queue_get = results_queue.popleft

    try:
        while True:
            if results_queue:
                result=results_queue_get()
                if result==True:
                    break
                print(json_dumps(result))
            else:
                sys.stdout.flush()
                sleep(0.001)

    except Exception as pe:
        print_info('printer error:{pe}')

    sys.stdout.flush()
    sys.exit(0) #thread

def print_info(*args):
    print('#',*args)

if __name__ == "__main__":
    VER_TIMESTAMP = get_ver_timestamp()

    args=parse_args(VER_TIMESTAMP)

    if args.command in ('load','search'):
        record = LibrerRecord('nowy','sciezka','./record.log')
        record.load(args.file)
        print_info(f'record label:{record.header.label}')
    else:
        print_info('parse problem')
        exit(1)

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

        name_func_to_call = lambda x : search(name_regexp,x)
        name_search_kind='regexp'
    elif name_glob:
        if name_case_sens:
            name_func_to_call = lambda x : re_compile(translate(name_glob)).match(x)
        else:
            name_func_to_call = lambda x : re_compile(translate(name_glob), IGNORECASE).match(x)
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
        cd_func_to_call = lambda x : re_search(cd_regexp,x)

    elif cd_glob:
        custom_data_needed=True
        cd_search_kind='glob'
        if cd_case_sens:
            #cd_func_to_call = lambda x : fnmatch(x,cd_regexp)
            cd_func_to_call = lambda x : re_compile(translate(cd_glob)).match(x)
        else:
            cd_func_to_call = lambda x : re_compile(translate(cd_glob), IGNORECASE).match(x)
    elif cd_fuzzy:
        custom_data_needed=True
        cd_search_kind='fuzzy'
        cd_func_to_call = lambda x : bool(SequenceMatcher(None,cd_fuzzy, x).ratio()>cd_fuzzy_threshold)
        #cd_fuzzy_threshold = float(cd_fuzzy_threshold) if find_cd_search_kind == 'fuzzy' else 0
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

    thread = Thread(target=printer,daemon=True)
    thread.start()

    record.find_items(results_queue,
            size_min,size_max,
            timestamp_min,timestamp_max,
            name_search_kind,name_func_to_call,
            cd_search_kind,cd_func_to_call)

    thread.join()

    t2 = perf_counter()
    print_info(f'finished. times:{t1-t0},{t2-t1}')

    sys.exit(0)

