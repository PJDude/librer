#!/usr/bin/python3

####################################################################################
#
#  Copyright (c) 2023 Piotr Jochymek
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

import json

from subprocess import Popen, STDOUT, PIPE,TimeoutExpired

from time import sleep, perf_counter,time,strftime,localtime

from signal import SIGTERM,SIGKILL

from threading import Thread

from multiprocessing import Process, Queue
from queue import Empty

from os import scandir,stat,sep
from os import remove as os_remove
from os import cpu_count
#from os import set_blocking

from os.path import abspath,normpath,basename
from os.path import join as path_join

from zipfile import ZipFile

from platform import system as platform_system
from platform import release as platform_release
from platform import node as platform_node

from fnmatch import fnmatch,translate

from re import compile as re_compile
from re import search,IGNORECASE

from sys import getsizeof
import sys

from collections import defaultdict

from pickle import dumps,loads,load

from difflib import SequenceMatcher

from pathlib import Path as pathlib_Path

from zstandard import ZstdCompressor,ZstdDecompressor

from executor import Executor

from record import LibrerRecordHeader,LibrerRecord

from func import *

from os import name as os_name
windows = bool(os_name=='nt')


#######################################################################

class LibrerCore:
    records = set()
    db_dir=''

    def __init__(self,db_dir,log):
        self.records = set()
        self.db_dir = db_dir
        self.log=log
        self.info_line = 'init'
        #self.info_line_current = ''

        self.records_to_show=[]
        self.abort_action=False
        self.search_record_nr=0

        self.find_res_quant = 0
        self.records_perc_info = 0

        self.records_sorted = []

    def update_sorted(self):
        self.records_sorted = sorted(self.records,key = lambda x : x.header.creation_time)

    def create(self,label='',path=''):
        new_record = LibrerRecord(label,path,self.log)
        new_record.db_dir = self.db_dir

        self.records.add(new_record)
        self.update_sorted()
        return new_record

    def read_records_pre(self):
        try:
            with scandir(self.db_dir) as res:
                size_sum=0
                self.record_files_list=[]
                for entry in res:
                    filename = entry.name
                    if filename.endswith('.dat'):
                        try:
                            stat_res = stat(entry)
                            size = int(stat_res.st_size)
                        except Exception as e:
                            print('record stat error:%s' % e )
                            continue

                        size_sum+=size
                        self.record_files_list.append( (filename,size) )
                quant_sum=len(self.record_files_list)
            return (quant_sum,size_sum)
        except Exception as e:
            self.log.error('list read error:%s' % e )
            return (0,0)

    def abort(self):
        #print('core abort')
        self.abort_action = True

    def read_records(self):
        self.log.info('read_records: %s',self.db_dir)
        self.records_to_show=[]

        info_curr_quant = 0
        info_curr_size = 0

        for filename,size in sorted(self.record_files_list):
            if self.abort_action:
                break

            self.log.info('db:%s',filename)
            new_record = self.create()

            self.info_line = f'loading {filename}'

            info_curr_quant+=1
            info_curr_size+=size

            if new_record.load_wrap(self.db_dir,filename) :
                self.log.warning('removing:%s',filename)
                self.records.remove(new_record)
            else:
                self.records_to_show.append( (new_record,info_curr_quant,info_curr_size) )
        self.update_sorted()

    def find_items_in_records_check(self,
            range_par,
            size_min,size_max,
            find_filename_search_kind,name_expr,name_case_sens,
            find_cd_search_kind,cd_expr,cd_case_sens,
            filename_fuzzy_threshold,cd_fuzzy_threshold):

        sel_range = [range_par] if range_par else self.records
        self.files_search_quant = sum([record.header.quant_files for record in sel_range])

        if self.files_search_quant==0:
            return 1

        #name_regexp
        #cd_regexp
        if name_expr and find_filename_search_kind == 'regexp':
            if res := test_regexp(name_expr):
                return res

        if cd_expr and find_cd_search_kind == 'regexp':
            if res := test_regexp(cd_expr):
                return res

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

    def find_results_clean(self):
        for record in self.records:
            record.find_results_clean()

    ########################################################################################################################
    def find_items_in_records(self,
            range_par,
            size_min,size_max,
            find_filename_search_kind,name_expr,name_case_sens,
            find_cd_search_kind,cd_expr,cd_case_sens,
            filename_fuzzy_threshold,cd_fuzzy_threshold):

        print('find_items_in_records',size_min,size_max,
            find_filename_search_kind,name_expr,name_case_sens,
            find_cd_search_kind,cd_expr,cd_case_sens,
            filename_fuzzy_threshold,cd_fuzzy_threshold)

        self.find_results_clean()

        records_to_process = [range_par] if range_par else list(self.records)

        records_to_process.sort(reverse = True,key = lambda x : x.header.quant_files)

        record_commnad_list={}
        for record_nr,record in enumerate(records_to_process):
            if windows:
                if getattr(sys, 'frozen', False):
                    curr_command_list = record_commnad_list[record_nr] = ['record.exe', 'load',record.file_path]
                else:
                    #curr_command_list = record_commnad_list[record_nr] = ['cmd','/c','record.bat', 'load',record.file_path]
                    curr_command_list = record_commnad_list[record_nr] = ['python','src\\record_console.py', 'load',record.file_path]
            else:
                if getattr(sys, 'frozen', False):
                    curr_command_list = record_commnad_list[record_nr] = ['./record', 'load',record.file_path]
                else:
                    #curr_command_list = record_commnad_list[record_nr] = ['bash','./record.sh', 'load',record.file_path]
                    curr_command_list = record_commnad_list[record_nr] = ['python3','./src/record_console.py', 'load',record.file_path]

            if size_min:
                curr_command_list.append(str(size_min))

            if size_max:
                curr_command_list.append(str(size_max))

            find_filename_search_kind
            if name_expr:
                filename_fuzzy_threshold_float=float(filename_fuzzy_threshold) if find_filename_search_kind == 'fuzzy' else 0

                if find_filename_search_kind == 'regexp':
                    #name_func_to_call = lambda x : search(name_expr,x)
                    curr_command_list.append('--file_regexp')
                    curr_command_list.append(name_expr)
                elif find_filename_search_kind == 'glob':
                    curr_command_list.append('--file_glob')
                    curr_command_list.append(name_expr)

                    if name_case_sens:
                        #name_func_to_call = lambda x : fnmatch(x,name_expr)
                        #name_func_to_call = lambda x : re_compile(translate(name_expr)).match(x)
                        curr_command_list.append('--file_case_sensitive')
                    #else:

                        #name_func_to_call = lambda x : re_compile(translate(name_expr), IGNORECASE).match(x)
                elif find_filename_search_kind == 'fuzzy':
                    #name_func_to_call = lambda x : bool(SequenceMatcher(None, name_expr, x).ratio()>filename_fuzzy_threshold_float)

                    curr_command_list.append('--file_fuzzy')
                    curr_command_list.append(name_expr)

                else:
                    #name_func_to_call = None
                    pass
            else:
                #name_func_to_call = None
                pass

            if cd_expr:
                cd_fuzzy_threshold_float = float(cd_fuzzy_threshold) if find_cd_search_kind == 'fuzzy' else 0

                if find_cd_search_kind == 'regexp':
                    #cd_func_to_call = lambda x : search(cd_expr,x)
                    curr_command_list.append('--cd_regexp')
                    curr_command_list.append(cd_expr)
                elif find_cd_search_kind == 'glob':
                    curr_command_list.append('--cd_glob')
                    curr_command_list.append(cd_expr)
                    if cd_case_sens:
                        curr_command_list.append('--cd_case_sensitive')
                        #cd_func_to_call = lambda x : fnmatch(x,cd_expr)
                        #cd_func_to_call = lambda x : re_compile(translate(cd_expr)).match(x)

                        #cd_func_to_call = lambda x : re_compile(translate(cd_expr), IGNORECASE).match(x)
                elif find_cd_search_kind == 'fuzzy':
                    #cd_func_to_call = lambda x : bool(SequenceMatcher(None, cd_expr, x).ratio()>cd_fuzzy_threshold_float)
                    curr_command_list.append('--cd_fuzzy')
                    curr_command_list.append(cd_expr)
            elif find_cd_search_kind == 'without':
                curr_command_list.append('--cd_without')
                #cd_func_to_call = None
            elif find_cd_search_kind == 'any':
                curr_command_list.append('--cd_ok')
                #cd_func_to_call = None
            elif find_cd_search_kind == 'error':
                curr_command_list.append('--cd_error')
                #cd_func_to_call = None
            else:
                #cd_func_to_call = None
                pass

            print('curr_command_list:',curr_command_list,' '.join(curr_command_list))

        self.find_res_quant = 0

        self.total_search_progress = 0

        self.search_record_nr=0

        self.abort_action = False
        for record in records_to_process:
            record.abort_action = False

        ############################################################

        max_processes = cpu_count()
        #max_processes = 1

        records_to_process_len = len(records_to_process)

        results_queues=[]
        abort_queues=[]

        #####################################################
        def threaded_run(command_list,results_queue,abort_queue):
            subprocess = Popen(command_list, stdout=PIPE, stderr=STDOUT,shell=False,text=True)
            subprocess_stdout_readline = subprocess.stdout.readline
            subprocess_poll = subprocess.poll
            results_queue_put = results_queue.put

            abort_queue_get = abort_queue.get
            while True:
                try:
                    if abort_queue_get(False):
                        while subprocess_poll() is None:
                            #subprocess.send_signal(SIGTERM)
                            try:
                                #subprocess.send_signal(SIGKILL)
                                #print('killing ',subprocess)
                                subprocess.kill()
                                #print('killing 2',subprocess)
                            except Exception as ke:
                                print(ke)

                            sleep(0.2)
                            #print('killing 3',subprocess)

                        #print('killing 4',subprocess)
                        break
                except Empty:
                    if line := subprocess_stdout_readline():
                        try:
                            if line[0]!='#':
                                results_queue_put(json.loads(line.strip()))
                        except Exception as e:
                            print('threaded_run error:',e,line)
                    else:
                        if subprocess_poll() is not None:
                            break
                        sleep(0.01)
            sys.exit() #thread

        #####################################################
        def suck_queue(results_queue,results_list,get_all=False):
            progress=0
            counter=0
            try:
                results_queue_get = results_queue.get
                results_list_append = results_list.append
                while val := results_queue_get(False): #progress,found_data
                    try:
                        progress = int(val[0])
                        if len(val)>1:
                            results_list_append( tuple([tuple(val[3:]),int(val[1]),int(val[2])]) )

                    except Exception as ie:
                        print('suck_queue error - ie',ie)
                        print('suck_queue error - progress',progress)
                        print('suck_queue error - val',val)

                    if get_all:
                        continue

                    counter+=1
                    if counter>128:
                        return progress
            except Empty:
                sleep(0.01)

            return progress

        #####################################################
        self.info_line = 'Initializing subprocesses ...'
        jobs = {}

        total_progress=[]

        for record_nr,record in enumerate(records_to_process):
            total_progress.append(0)

            results_queues.append(Queue())
            abort_queues.append(Queue())

            #jobs[record_nr] = [0,Thread(target=lambda : threaded_run(record_commnad_list[record_nr],results_queues[record_nr],abort_queues[record_nr]),daemon=True)]
            jobs[record_nr] = [0,None]

            record.find_results=[]

        self.info_line = 'subprocesses run.'

        print('stage 2')

        ############################################################
        #jobs[0] CODES
        #0 - waiting
        #1 - started and alive
        #2 - started and !alive
        #3 - !alive and empty queue

        while True:
            if self.abort_action:
                self.info_line = 'Aborting ...'
                _ = [abort_queues[record_nr].put(True) for record_nr in range(records_to_process_len)]
                break

            waiting_list = [ record_nr for record_nr in range(records_to_process_len) if jobs[record_nr][0]==0 ]
            waiting = len(waiting_list)

            running = len([record_nr for record_nr in range(records_to_process_len) if jobs[record_nr][0]==1 and jobs[record_nr][1].is_alive() ])
            finished = len([record_nr for record_nr in range(records_to_process_len) if jobs[record_nr][0]==2])

            self.search_record_nr = records_to_process_len-running-waiting
            self.records_perc_info = self.search_record_nr * 100.0 / records_to_process_len

            self.info_line = f'Threads: waiting:{waiting}, running:{running}, finished:{finished}'

            if waiting:
                if running<max_processes:
                    record_nr = waiting_list[0]
                    job = jobs[record_nr]

                    #print('starting:',record_commnad_list[record_nr])

                    job[0] = 1
                    job[1] = Thread(target=lambda : threaded_run(record_commnad_list[record_nr],results_queues[record_nr],abort_queues[record_nr]),daemon=True)
                    job[1].start()
                    sleep(0.01)
                    continue

            no_progress=True
            for record_nr in range(records_to_process_len):
                job = jobs[record_nr]
                if job[0]==1:
                    if not job[1].is_alive():
                        job[1].join()
                        job[0] = 2

                if job[0] in (1,2):
                    get_all=bool(job[0]==2)

                    if progress := int(suck_queue(results_queues[record_nr],records_to_process[record_nr].find_results,get_all)):
                        #print(record_nr,'\t',progress)
                        total_progress[record_nr] = progress
                        #if progress>total_progress[record_nr]:
                        no_progress = False

                if job[0]==2 and results_queues[record_nr].empty():
                    job[0]==3

            #print(total_progress)
            self.total_search_progress = sum(total_progress)
            self.find_res_quant = sum([len(record.find_results) for record in records_to_process])

            if running==0 and waiting==0 and all(results_queues[record_nr].empty() for record_nr in range(records_to_process_len)):
                break

            if no_progress:
                sleep(0.1)

        print('stage 3')

        #####################################################

        for subprocess_combo in jobs.values():
            if subprocess_combo[0]==1:
                subprocess_combo[1].join()

        print('stage 4')

        return True

    ########################################################################################################################

    def delete_record_by_id(self,rid):
        for record in self.records:
            if record.header.rid == rid:
                file_path = sep.join([self.db_dir,record.FILE_NAME])
                self.log.info('deleting file:%s',file_path)
                try:
                    os_remove(file_path)
                except Exception as e:
                    self.log.error(e)

        self.update_sorted()
