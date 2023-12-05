#!/usr/bin/python3

####################################################################################
#
#  Copyright (c) 2022-2023 Piotr Jochymek
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

import argparse
import os
import signal
#from sys import exit
from subprocess import DEVNULL
import pathlib
import sys

from time import sleep

from threading import Thread

from re import compile as re_compile
from fnmatch import fnmatch,translate
from re import search,IGNORECASE

from pickle import dumps,loads,dump,load

from record import data_format_version,LibrerRecordHeader,LibrerRecord

from multiprocessing import Process, Queue
from queue import Empty

from func import *

VERSION_FILE='version.txt'

def get_ver_timestamp():
    try:
        timestamp=pathlib.Path(os.path.join(os.path.dirname(__file__),VERSION_FILE)).read_text(encoding='ASCII').strip()
    except Exception as e_ver:
        print(e_ver)
        timestamp=''
    return timestamp

def parse_args(ver):
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            prog = 'record.exe' if (os.name=='nt') else 'record',
            description = f"librer record version {ver}\nCopyright (c) 2023 Piotr Jochymek\n\nhttps://github.com/PJDude/librer",
            )

    #parser.add_argument('--foo', required=True)

    parser.add_argument('command',type=str,help='command to execute',choices=('load','search','info'))

    parser.add_argument('file',type=str,help='dat file')

    file_group = parser.add_mutually_exclusive_group()

    file_group.add_argument('-fre'  ,'--file_regexp',type=str,help='serch files by regular expression')
    file_group.add_argument('-fg'   ,'--file_glob',type=str,help='serch files by glob expression')
    file_group.add_argument('-fgcs' ,'--file_case_sensitive',action='store_true',help='serch files by case sensitive glob expression')
    file_group.add_argument('-ff'   ,'--file_fuzzy',type=str,help='serch files by fuzzy match with threshold')
    file_group.add_argument('-fft'  ,'--file_fuzzy_threshold', type=float,help='threshold value')

    cd_group = parser.add_mutually_exclusive_group()
    cd_group.add_argument('-cdw','--cd_without',action='store_true',help='serch for riles without custom data')
    cd_group.add_argument('-cdok','--cd_ok',action='store_true',help='serch for riles with correct custom data')
    cd_group.add_argument('-cderror','--cd_error',action='store_true',help='serch for riles with error status on custom data extraction')

    cd_group.add_argument('-cdre'   ,'--cd_regexp',type=str,help='serch by regular expression on custom data')
    cd_group.add_argument('-cdg'    ,'--cd_glob',type=str,help='serch by glob expression on custom data')
    cd_group.add_argument('-cdgcs'  ,'--cd_case_sensitive',action='store_true',help='serch by case sensitive glob expression on custom data')
    cd_group.add_argument('-cdf'    ,'--cd_fuzzy',type=str,help='serch by fuzzy match with threshold on custom data')
    cd_group.add_argument('-cdft'   ,'--cd_fuzzy_threshold',type=float,help='threshold value on custom data')

    parser.add_argument('-min','--size_min',type=str,help='minimum size')
    parser.add_argument('-max','--size_max',type=str,help='maximum size')

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

results_queue=Queue()

import base64
import codecs

import io

import json

def printer():
    results_queue_get = results_queue.get

    #sys.stdout.reconfigure(encoding='utf-8')

    #sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
    #sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='latin-1', buffering=1)

    #sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='latin-1')

    while True:
        try:
            if result:=results_queue_get(False):
                if result==True:
                    break
                try:
                    #print('/'.join(str(elem) for elem in result))
                    #sys.stdout.write('/'.join(str(elem) for elem in result).encode())
                    #str_list = [str(elem) for elem in result]
                    print(json.dumps(result))

                except Exception as e:
                    print_info(result)
                    print_info(e)
                    exit(1)

                #try:
                #    print(dumps(str_list))
                #except Exception as e:
                #    print_info(str_list)
                #    print_info(e)
                #    exit(1)

        except Empty:
            sleep(0.01)

    sys.exit() #thread

def print_info(*args):
    print('#',*args)

#windows console wrapper
if __name__ == "__main__":
    VER_TIMESTAMP = get_ver_timestamp()

    #print('rc init')
    args=parse_args(VER_TIMESTAMP)

    if args.command in ('load','search'):
        record = LibrerRecord('nowy','sciezka','./record.log')
        record.load(args.file)
        print_info(record.header.label)
    else:
        print_info('parse problem')
        exit(1)

    name_case_sens=args.file_case_sensitive
    cd_case_sens=args.file_case_sensitive

    name_regexp=args.file_regexp
    name_glob=args.file_glob
    name_fuzzy=args.file_fuzzy

    file_fuzzy_threshold = args.file_fuzzy_threshold
    cd_fuzzy_threshold = args.cd_fuzzy_threshold

    if name_regexp:
        if res := test_regexp(name_regexp):
            exit(res)

        name_func_to_call = lambda x : search(name_regexp,x)
    elif name_glob:
        if name_case_sens:
            name_func_to_call = lambda x : re_compile(translate(name_glob)).match(x)
        else:
            name_func_to_call = lambda x : re_compile(translate(name_glob), IGNORECASE).match(x)
    elif name_fuzzy:
        name_func_to_call = lambda x : bool(SequenceMatcher(None, name_fuzzy, x).ratio()>file_fuzzy_threshold)
        #TODO
    else:
        name_func_to_call = None

    cd_without=args.cd_without
    cd_error=args.cd_error
    cd_ok=args.cd_ok

    cd_regexp=args.cd_regexp
    cd_glob=args.cd_glob
    cd_fuzzy=args.cd_fuzzy

    if cd_regexp:
        cd_search_kind='regexp'
        if res := test_regexp(cd_regexp):
            exit(res)
        cd_func_to_call = lambda x : search(cd_regexp,x)
    elif cd_glob:
        cd_search_kind='glob'
        if cd_case_sens:
            #cd_func_to_call = lambda x : fnmatch(x,cd_regexp)
            cd_func_to_call = lambda x : re_compile(translate(cd_glob)).match(x)
        else:
            cd_func_to_call = lambda x : re_compile(translate(cd_glob), IGNORECASE).match(x)
    elif cd_fuzzy:
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

    #TODO itd

    #####################################################################
    print_info('decompresing filestructure')
    record.decompress_filestructure()
    print_info('decompresing customdata')
    record.decompress_customdata()
    print_info('searching')

    size_min=args.size_min if args.size_min else None
    size_max=args.size_max if args.size_max else None

    print_info(size_min,size_max,name_func_to_call,cd_search_kind,cd_func_to_call)

    thread = Thread(target=printer,daemon=True)
    thread.start()

    record.find_items(results_queue,
            size_min,size_max,
            name_func_to_call,
            cd_search_kind,cd_func_to_call)

    thread.join()
    print_info('finished.')
