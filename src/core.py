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

from send2trash import send2trash as send2trash_delete
from pympler.asizeof import asizeof
 
from json import loads as json_loads

from subprocess import Popen, STDOUT, PIPE
#TimeoutExpired
#from subprocess import call as subprocess_call

from time import sleep, perf_counter,time,strftime,localtime

from threading import Thread

#from multiprocessing import Queue
#from queue import Empty

from os import scandir,stat,sep
from os import name as os_name
from os import remove as os_remove
from os import cpu_count
#from os import kill as os_kill

from os.path import abspath,normpath,basename,dirname
from os.path import join as path_join

from zipfile import ZipFile

from platform import system as platform_system
from platform import release as platform_release
from platform import node as platform_node

from fnmatch import fnmatch
#translate

#from re import compile as re_compile
from re import search
#IGNORECASE

from sys import getsizeof
import sys

from collections import defaultdict

from pathlib import Path as pathlib_Path

from zstandard import ZstdCompressor,ZstdDecompressor

from signal import SIGTERM

from psutil import Process

from pickle import dumps,loads

windows = bool(os_name=='nt')

PARAM_INDICATOR_SIGN = '%'

data_format_version='0017'

VERSION_FILE='version.txt'

def localtime_catched(t):
    try:
        #mtime sometimes happens to be negative (Virtual box ?)
        return localtime(t)
    except:
        return localtime(0)
        
def get_ver_timestamp():
    try:
        timestamp=pathlib_Path(path_join(dirname(__file__),VERSION_FILE)).read_text(encoding='ASCII').strip()
    except Exception as e_ver:
        print(e_ver)
        timestamp=''
    return timestamp

def bytes_to_str(num):
    if num < 1024:
        return "%s B" % num

    numx100=num*100

    for unit in ('kB','MB','GB','TB'):
        numx100 //= 1024
        if numx100 < 102400:
            s=str(numx100)
            s_main,s_frac=s[:-2],s[-2:]

            if s_frac_strip := s_frac.rstrip('0'):
                return "%s.%s %s" % (s_main,s_frac_strip,unit)

            return "%s %s" % (s_main,unit)

    return "BIG"

def fnumber(num):
    return str(format(num,',d').replace(',',' '))

def str_to_bytes(string):
    units = {'kb': 1024,'mb': 1024*1024,'gb': 1024*1024*1024,'tb': 1024*1024*1024*1024, 'b':1}
    try:
        string = string.replace(' ','')
        for suffix,weight in units.items():
            if string.lower().endswith(suffix):
                return int(string[0:-len(suffix)]) * weight #no decimal point

        return int(string)
    except:
        return -1

def bools_to_byte(bool_values):
    byte = 0

    for value in bool_values:
        byte <<= 1
        if value:
            byte |= 1

    return byte

def byte_to_bools(byte, num_bools=8):
    bool_list = [False]*num_bools

    for i in range(num_bools):
        if byte & (1 << i):
            bool_list[num_bools-1-i]=True

    return tuple(bool_list)

def test_regexp(expr):
    teststring='abc'
    try:
        search(expr,teststring)
    except Exception as e:
        return e

    return None

LUT_encode={}
LUT_decode={}

def prepare_LUTs():
    #global LUT_decode,LUT_encode
    for i in range(256):
        temp_tuple = LUT_decode[i]=byte_to_bools(i)
        LUT_encode[temp_tuple]=i

prepare_LUTs()

def get_command_list(executable,parameters,full_file_path,shell=False):
    if windows:
        full_file_path = full_file_path.replace('/',sep)

    if shell:
        if ' ' in executable:
            executable=f'"{executable}"'
            
        if ' ' in full_file_path:
            full_file_path = f'"{full_file_path}"'
    
    parameters = parameters.strip()
    
    if parameters:
        if PARAM_INDICATOR_SIGN not in parameters:
            parameters = parameters + ' ' + PARAM_INDICATOR_SIGN
            
        parameters = parameters.replace(f'"{PARAM_INDICATOR_SIGN}"',PARAM_INDICATOR_SIGN)
    else:
        parameters=PARAM_INDICATOR_SIGN

    parameters_list = [p_elem.replace(PARAM_INDICATOR_SIGN,full_file_path) for p_elem in parameters.split() if p_elem]

    single_command_list = [executable] + parameters_list

    return single_command_list

def rec_kill(pid):
    proc = Process(pid)

    #proc.send_signal(SIGSTOP)
    #proc.send_signal(SIGINT)

    for child in proc.children():
        rec_kill(child.pid)

    try:
        #proc.send_signal(SIGTERM)
        proc.send_signal(SIGTERM)
        #print('SIGTERM send to',pid)

    except Exception as e:
        print('rec_kill error',e)


#######################################################################
class LibrerRecordHeader :
    def __init__(self,label='',scan_path=''):
        self.label=label
        self.scan_path = scan_path
        self.creation_time = int(time())
        self.rid = self.creation_time #record id

        self.quant_files = 0
        self.quant_folders = 0
        self.sum_size = 0
        self.data_format_version=data_format_version

        self.files_cde_size = 0
        self.files_cde_size_sum = 0
        self.files_cde_quant = 0
        self.files_cde_quant_sum = 0

        self.files_cde_size_extracted = 0

        self.items_names=0
        self.items_cd=0
        
        self.references_names = 0
        self.references_cd = 0
        
        self.cde_list = []
        self.files_cde_errors_quant = {}
        self.files_cde_errors_quant_all = 0
        self.cde_stats_time_all = 0
        
        self.zipinfo = {}
        
        self.compression_level=0
        
        self.creation_os,self.creation_host = f'{platform_system()} {platform_release()}',platform_node()

#######################################################################
class LibrerRecord:
    def __init__(self,label,scan_path,log):
        self.header = LibrerRecordHeader(label,scan_path)

        self.filestructure = ()
        self.customdata = []
        self.filenames = []

        self.log = log
        self.find_results = []

        self.info_line = ''
        self.info_line_current = ''

        self.abort_action = False

        #self.crc_progress_info=0

        self.FILE_NAME = ''
        self.FILE_SIZE = 0
        self.file_path = ''

        #self.quantinfo={'header':'','filestructure':'','filenames':'?','customdata':'?'}
        
    def find_results_clean(self):
        self.find_results = []

    def new_file_name(self):
        return f'{self.header.rid}.dat'

    def abort(self):
        self.abort_action = True

    def scan_rec(self, path, scan_like_data,filenames_set,check_dev=True,dev_call=None) :
        if self.abort_action:
            return True

        path_join_loc = path_join

        local_folder_size_with_subtree=0
        local_folder_size = 0

        self_scan_rec = self.scan_rec

        filenames_set_add = filenames_set.add
        try:
            with scandir(path) as res:
                local_folder_files_count = 0
                local_folder_folders_count = 0

                for entry in res:
                    if self.abort_action:
                        break

                    entry_name = entry.name
                    filenames_set_add(entry_name)

                    is_dir,is_file,is_symlink = entry.is_dir(),entry.is_file(),entry.is_symlink()

                    self.ext_statistics[pathlib_Path(entry).suffix]+=1

                    self.info_line_current = entry_name
                    try:
                        stat_res = stat(entry)

                        mtime = int(stat_res.st_mtime)
                        dev=stat_res.st_dev
                    except Exception as e:
                        self.log.error('stat error:%s', e )
                        #size -1 <=> error, dev,in ==0
                        is_bind = False
                        size=-1
                        mtime=0
                        has_files = False
                        scan_like_data[entry_name] = [size,is_dir,is_file,is_symlink,is_bind,has_files,mtime]
                    else:
                        dict_entry={}
                        is_bind=False
                        if check_dev:
                            if dev_call:
                                if dev_call!=dev:
                                    self.log.info('devices mismatch:%s %s %s %s' % (path,entry_name,dev_call,dev) )
                                    is_bind=True
                            else:
                                dev_call=dev

                        if is_dir:
                            if is_symlink :
                                has_files = False
                                size = 0
                            elif is_bind:
                                has_files = False
                                size = 0
                            else:
                                size = self_scan_rec(path_join_loc(path,entry_name),dict_entry,filenames_set,check_dev,dev)
                                has_files = bool(size)

                                local_folder_size_with_subtree += size

                            local_folder_folders_count += 1
                        else:
                            if is_symlink :
                                has_files = False
                                size = 0
                            else:
                                has_files = False
                                size = int(stat_res.st_size)

                                local_folder_size += size

                            local_folder_files_count += 1

                        temp_list_ref = scan_like_data[entry_name]=[size,is_dir,is_file,is_symlink,is_bind,has_files,mtime]
                        if has_files:
                            temp_list_ref.append(dict_entry)

                self_header = self.header
                self_header.sum_size += local_folder_size
                self_header.quant_files += local_folder_files_count
                self_header.quant_folders += local_folder_folders_count

        except Exception as e:
            self.log.error('scandir error:%s',e )

        self.info_line_current = ''

        return local_folder_size_with_subtree+local_folder_size

    def get_file_name(self,nr):
        return self.filenames[nr]

    def scan(self,cde_list,check_dev=True):
        self.info_line = 'Scanning filesystem'
        self.abort_action=False

        self.header.sum_size = 0

        self.ext_statistics=defaultdict(int)
        self.scan_data={}

        #########################
        time_start = perf_counter()
        filenames_set=set()
        self.scan_rec(self.header.scan_path,self.scan_data,filenames_set,check_dev=check_dev)
        time_end = perf_counter()
        
        self.header.scanning_time = time_end-time_start
        
        self.filenames = tuple(sorted(list(filenames_set)))
        #########################
        self.info_line = 'indexing filesystem names'

        self.filenames_helper = {fsname:fsname_index for fsname_index,fsname in enumerate(self.filenames)}

        self.header.cde_list = cde_list
        self.cd_stat=[0]*len(cde_list)

        self.customdata_pool = {}
        self.customdata_pool_index = 0

        if cde_list:
            self.log.info('estimating CD pool')
            self.info_line = 'estimating files pool for custom data extraction'
            self.prepare_customdata_pool_rec(self.scan_data,[])

        self.info_line = ''

        #for ext,stat in sorted(self.ext_statistics.items(),key = lambda x : x[1],reverse=True):
        #    print(ext,stat)

    def prepare_customdata_pool_rec(self,scan_like_data,parent_path):
        scan_path = self.header.scan_path
        self_prepare_customdata_pool_rec = self.prepare_customdata_pool_rec

        cde_list = self.header.cde_list
        self_customdata_pool = self.customdata_pool

        for entry_name,items_list in scan_like_data.items():
            size,is_dir,is_file,is_symlink,is_bind,has_files,mtime = items_list[0:7]

            if self.abort_action:
                break
            try:
                subpath_list = parent_path + [entry_name]

                if not is_symlink and not is_bind:
                    if is_dir:
                        if has_files:
                            self_prepare_customdata_pool_rec(items_list[7],subpath_list)
                    else:
                        subpath=sep.join(subpath_list)
                        ############################

                        full_file_path = normpath(abspath(sep.join([scan_path,subpath])))

                        matched = False

                        rule_nr=-1
                        for expressions,use_smin,smin_int,use_smax,smax_int,executable,parameters,shell,timeout,crc in cde_list:
                            if self.abort_action:
                                break
                            if matched:
                                break

                            rule_nr+=1

                            if use_smin:
                                if size<smin_int:
                                    continue
                            if use_smax:
                                if size>smax_int:
                                    continue

                            for expr in expressions:
                                if self.abort_action:
                                    break
                                if matched:
                                    break

                                if fnmatch(full_file_path,expr):
                                    self_customdata_pool[self.customdata_pool_index]=(items_list,subpath,rule_nr,size)
                                    self.customdata_pool_index += 1
                                    self.cd_stat[rule_nr]+=1
                                    self.header.files_cde_size_sum += size
                                    matched = True

            except Exception as e:
                self.log.error('prepare_customdata_pool_rec error::%s',e )
                print('prepare_customdata_pool_rec',e,entry_name,size,is_dir,is_file,is_symlink,is_bind,has_files,mtime)

    def extract_customdata_threaded(self):
        self_header = self.header
        scan_path = self_header.scan_path

        self.info_line = 'custom data extraction ...'

        self_header.files_cde_quant = 0
        self_header.files_cde_size = 0
        self_header.files_cde_size_extracted = 0
        self_header.files_cde_errors_quant = defaultdict(int)
        self_header.files_cde_errors_quant_all = 0
        self_header.files_cde_quant_sum = len(self.customdata_pool)

        cde_list = self.header.cde_list
    
        customdata_helper={}
        
        customdata_stats_size=defaultdict(int)
        customdata_stats_uniq=defaultdict(int)
        customdata_stats_refs=defaultdict(int)
        customdata_stats_time=defaultdict(float)
        
        customdata_stats_time_all=[0]
        #############################################################
        def threaded_cde(timeout_semi_list):
            cd_index=0
            self_customdata_append = self.customdata.append
            
            time_start_all = perf_counter()
            for (scan_like_list,subpath,rule_nr,size) in self.customdata_pool.values():
                decoding_error=False
                self.killed=False
                self.abort_single_file_cde=False

                time_start = perf_counter()
                if self.abort_action:
                    returncode=200
                    output = 'Custom data extraction was aborted.'
                    aborted = True
                else:
                    aborted = False

                    returncode=202
                    expressions,use_smin,smin_int,use_smax,smax_int,executable,parameters,shell,timeout,do_crc = cde_list[rule_nr]
                    full_file_path = normpath(abspath(sep.join([scan_path,subpath]))).replace('/',sep)
                    single_command_list = get_command_list(executable,parameters,full_file_path,shell)
                    single_command_list_joined = ' '.join(single_command_list)
                    command = single_command_list_joined if shell else single_command_list

                    self.info_line_current = f'{single_command_list_joined} ({bytes_to_str(size)})'

                    timeout_val=time()+timeout if timeout else None
                    #####################################
                    
                    try:
                        subprocess = Popen(command, stdout=PIPE, stderr=STDOUT,shell=shell,text=True)
                        timeout_semi_list[0]=(timeout_val,subprocess)
                    except Exception as re:
                        print('threaded_cde error:',re)
                        subprocess = None
                        timeout_semi_list[0]=(timeout_val,subprocess)
                        returncode=201
                        output = str(re)
                    else:

                        subprocess_stdout_readline = subprocess.stdout.readline
                        subprocess_poll = subprocess.poll

                        output_list = []
                        output_list_append = output_list.append

                        while True:
                            try:
                                line = subprocess_stdout_readline()
                            except Exception as le:
                                #print(command,le)
                                line = str(le)
                                decoding_error = True

                            output_list_append(line.rstrip('\n\r'))

                            if not line and subprocess_poll() is not None:
                                returncode=subprocess.returncode
                                timeout_semi_list[0] = None
                                break

                        if self.killed:
                            output_list.append('Killed.')

                        output = '\n'.join(output_list)
                    
                    #####################################

                time_end = perf_counter()
                customdata_stats_time[rule_nr]+=time_end-time_start
                
                if returncode or decoding_error or self.killed or aborted:
                    self_header.files_cde_errors_quant[rule_nr]+=1
                    self_header.files_cde_errors_quant_all+=1

                if not aborted:
                    self_header.files_cde_quant += 1
                    self_header.files_cde_size += size
                    self_header.files_cde_size_extracted += getsizeof(output)

                new_elem={}
                new_elem['cd_ok']= bool(returncode==0 and not decoding_error and not self.killed and not aborted)
                
                cd_field=(rule_nr,returncode,output)
                if cd_field not in customdata_helper:
                    customdata_helper[cd_field]=cd_index
                    new_elem['cd_index']=cd_index
                    cd_index+=1

                    self_customdata_append(cd_field)
                    
                    customdata_stats_size[rule_nr]+=asizeof(cd_field)
                    customdata_stats_uniq[rule_nr]+=1
                    customdata_stats_refs[rule_nr]+=1
                else:
                    new_elem['cd_index']=customdata_helper[cd_field]
                    customdata_stats_refs[rule_nr]+=1

                #if do_crc:
                #    new_elem['crc_val']=crc_val
                scan_like_list.append(new_elem)
            
            time_end_all = perf_counter()
            
            customdata_stats_time_all[0]=time_end_all-time_start_all
            sys.exit() #thread

        timeout_semi_list = [None]

        cde_thread = Thread(target = lambda : threaded_cde(timeout_semi_list),daemon=True)
        cde_thread.start()

        while cde_thread.is_alive():
            if timeout_semi_list[0]:
                timeout_val,subprocess = timeout_semi_list[0]
                if self.abort_action or (timeout_val and time()>timeout_val):
                    try:
                        self.killed=True
                        rec_kill(subprocess.pid)
                        #if windows:
                        #    subprocess_call(['taskkill', '/F', '/T', '/PID', str(subprocess.pid)])
                        #else:
                        #    rec_kill(subprocess.pid)
                            #subprocess.kill()
                            #os_kill(subprocess.pid, -9)

                    except Exception as ke:
                        print('killing error:',subprocess.pid,ke)
                
                if self.abort_single_file_cde:
                    try:
                        self.killed=True
                        rec_kill(subprocess.pid)
                        #if windows:
                        #    subprocess_call(['taskkill', '/F', '/T', '/PID', str(subprocess.pid)])
                        #else:
                        #    rec_kill(subprocess.pid)
                            #subprocess.kill()
                            #os_kill(subprocess.pid, -9)

                    except Exception as ke:
                        print('killing error:',subprocess.pid,ke)
            else:
                sleep(0.01)

        cde_thread.join()

        del self.customdata_pool
        del customdata_helper
        
        self.header.cde_stats_size=customdata_stats_size
        self.header.cde_stats_uniq=customdata_stats_uniq
        self.header.cde_stats_refs=customdata_stats_refs
        self.header.cde_stats_time=customdata_stats_time
        self.header.cde_stats_time_all=customdata_stats_time_all[0]
        
    #############################################################
    def tupelize_rec(self,scan_like_data):
        LUT_encode_loc = LUT_encode

        self_tupelize_rec = self.tupelize_rec

        #self_customdata = self.customdata
        sub_list = []
        for entry_name,items_list in scan_like_data.items():
            try:
                entry_name_index = self.filenames_helper[entry_name]
                self.header.references_names+=1
            except Exception as VE:
                print('filenames error:',entry_name,VE)
            else:
                try:
                    (size,is_dir,is_file,is_symlink,is_bind,has_files,mtime) = items_list[0:7]

                    elem_index = 7
                    if has_files:
                        sub_dict = items_list[elem_index]
                        elem_index+=1

                    try:
                        info_dict = items_list[elem_index]
                    except:
                        has_cd = False
                        cd_ok = False
                        has_crc = False
                    else:
                        if 'cd_ok' in info_dict:
                            cd_ok = info_dict['cd_ok']
                            cd_index = info_dict['cd_index']
                            has_cd = True
                        else:
                            cd_ok = False
                            has_cd = False

                        if 'crc_val' in info_dict:
                            crc_val = info_dict['crc_val']
                            has_crc = True
                        else:
                            has_crc = False

                    code_new = LUT_encode_loc[ (is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc) ]

                    sub_list_elem=[entry_name_index,code_new,size,mtime]

                    if has_files:
                        sub_list_elem.append(self_tupelize_rec(sub_dict))
                    else:
                        if has_cd: #only files
                            self.header.references_cd+=1
                            sub_list_elem.append( cd_index )
                        if has_crc: #only files
                            sub_list_elem.append( crc_val )

                    sub_list.append( tuple(sub_list_elem) )

                except Exception as e:
                    self.log.error('tupelize_rec error::%s',e )
                    print('tupelize_rec error:',e,' entry_name:',entry_name,' items_list:',items_list)
        
        
        return tuple(sorted(sub_list,key = lambda x : x[1:4]))
    #############################################################

    def pack_data(self):
        size,mtime = 0,0
        is_dir = True
        is_file = False
        is_symlink = False
        is_bind = False
        has_cd = False
        has_files = True
        cd_ok = False
        has_crc = False
                
        self.header.references_names=0
        self.header.references_cd=0
        
        code = LUT_encode[ (is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc) ]
        self.filestructure = ('',code,size,mtime,self.tupelize_rec(self.scan_data))
                
        self.header.items_names=len(self.filenames)
        self.header.items_cd=len(self.customdata)
        
        del self.filenames_helper
        del self.scan_data

    def clone_record_rec(self,cd_org,filenames_org,tuple_like_data,keep_cd,keep_crc):
        LUT_decode_loc = LUT_decode
        self_get_file_name = self.get_file_name
        self_clone_record_rec = self.clone_record_rec

        name_index,code,size,mtime = tuple_like_data[0:4]
        if name_index:
            name = filenames_org[name_index]
        else:
            name=''

        is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc = LUT_decode_loc[code]
        if not keep_cd or not keep_crc:
            has_cd = has_cd and keep_cd
            if not has_cd:
                cd_ok=False

            has_crc = has_crc and keep_crc

            code = LUT_encode[ (is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc) ]

        new_list = [name_index,code,size,mtime]

        elem_index=4
        if has_files:
            sub_new_list=[]
            for sub_structure in tuple_like_data[elem_index]:
                sub_new_list.append(self_clone_record_rec(cd_org,filenames_org,sub_structure,keep_cd,keep_crc))
            elem_index+=1
            new_list.append(tuple(sorted( sub_new_list,key = lambda x : x[1:4] )))

        if has_cd:
            cd_index = tuple_like_data[elem_index]
            elem_index+=1
            if keep_cd:
                new_list.append(cd_index)

        if has_crc:
            crc = tuple_like_data[elem_index]
            if keep_crc:
                new_list.append(crc)

        return tuple(new_list)

    def clone_record(self,file_path,keep_cd=True,keep_crc=True,compression_level=16):
        self.decompress_filestructure()
        self.decompress_customdata()

        new_record = LibrerRecord(self.header.label,file_path,self.log)

        new_record.header = self.header
        new_record.filenames = self.filenames
        
        if keep_cd:
            new_record.customdata = self.customdata

        new_record.filestructure = self.clone_record_rec(self.customdata,self.filenames,self.filestructure,keep_cd,keep_crc)
        new_record.save(file_path,compression_level)

    ########################################################################################
    def find_items(self,
            results_queue,
            size_min,size_max,
            timestamp_min,timestamp_max,
            name_search_kind,name_func_to_call,
            cd_search_kind,cd_func_to_call):

        self.find_results = []

        self.decompress_filestructure()

        filenames_loc = self.filenames
        filestructure = self.filestructure

        search_progress = 0
        search_progress_update_quant = 0

        if cd_search_kind!='dont':
            self.decompress_customdata()

        LUT_decode_loc = LUT_decode

        use_size = bool(size_min or size_max)
        use_timestamp = bool(timestamp_min or timestamp_max)

        search_list = [ (filestructure[4],[]) ]
        search_list_pop = search_list.pop
        search_list_append = search_list.append

        cd_search_kind_is_regezp_glob_or_fuzzy = bool(cd_search_kind in ('regexp','glob','fuzzy'))
        cd_search_kind_is_dont_or_without = bool(cd_search_kind in ('dont','without'))

        when_folder_may_apply = bool(cd_search_kind_is_dont_or_without and not use_size and not use_timestamp)
        cd_search_kind_is_any = bool(cd_search_kind=='any')
        cd_search_kind_is_without = bool(cd_search_kind=='without')
        cd_search_kind_is_error = bool(cd_search_kind=='error')
            
        name_search_kind_is_error = bool(name_search_kind=='error')
        
        self_customdata = self.customdata

        results_queue_put = results_queue.append

        while search_list:
            filestructure,parent_path_components = search_list_pop()

            for data_entry in filestructure:
                #if check_abort():
                #    break

                search_progress_update_quant+=1
                if search_progress_update_quant>1024:
                    results_queue_put([search_progress])
                    search_progress_update_quant=0

                search_progress +=1

                name_nr,code,size,mtime = data_entry[0:4]

                name = filenames_loc[name_nr]

                is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc = LUT_decode_loc[code]

                elem_index=4
                if has_files:
                    sub_data = data_entry[elem_index]
                    elem_index+=1
                else:
                    sub_data = None

                if has_cd:
                    cd_nr = data_entry[elem_index]
                    elem_index+=1

                #if has_crc:
                #    crc = data_entry[elem_index]

                next_level = parent_path_components + [name]
                if name_search_kind_is_error:
                    if size>-1:
                        continue
                    
                if is_dir :
                    if when_folder_may_apply:
                        #katalog moze spelniac kryteria naazwy pliku ale nie ma rozmiaru i custom data
                        if name_func_to_call:
                            if name_func_to_call(name):
                                results_queue_put([search_progress,size,mtime,*next_level])
                                search_progress_update_quant=0

                    if sub_data:
                        search_list_append( (sub_data,next_level) )

                elif is_file:
                    
                    if use_size:
                        if size<0:
                            continue

                        if size_min:
                            if size<size_min:
                                continue
                        if size_max:
                            if size>size_max:
                                continue
                    if use_timestamp:
                        if timestamp_min:
                            if mtime<timestamp_min:
                                continue
                        if timestamp_max:
                            if mtime>timestamp_max:
                                continue
                            
                    if name_func_to_call:
                        try:
                            if not name_func_to_call(name):
                                continue
                        except Exception as e:
                            self.log.error('find_items(1):%s',str(e) )
                            continue

                    #oczywistosc
                    #if cd_search_kind=='dont':
                    #    pass

                    if cd_search_kind_is_any:
                        if not has_cd or not cd_ok:
                            continue
                    elif cd_search_kind_is_regezp_glob_or_fuzzy:
                        if has_cd and cd_ok:
                            cd_data = self_customdata[cd_nr][2]
                        else:
                            continue

                        if cd_func_to_call:
                            try:
                                if not cd_func_to_call(cd_data):
                                    continue
                            except Exception as e:
                                self.log.error('find_items(2):%s',str(e) )
                                continue

                        else:
                            continue
                    elif cd_search_kind_is_without:
                        if has_cd:
                            continue
                    elif cd_search_kind_is_error:
                        if has_cd:
                            if cd_ok:
                                continue
                        else:
                            continue

                    results_queue_put([search_progress,size,mtime,*next_level])
                    search_progress_update_quant=0

        results_queue_put([search_progress])
        results_queue_put(True)

    def find_items_sort(self,what,reverse):
        if what=='data':
            self.find_results.sort(key = lambda x : x[0],reverse=reverse)
        elif what=='size':
            self.find_results.sort(key = lambda x : (x[0][0:-1],x[1]),reverse=reverse)
        elif what=='ctime':
            self.find_results.sort(key = lambda x : (x[0][0:-1],x[2]),reverse=reverse)
        else:
            print('error unknown sorting',what,reverse)

    #############################################################
    def prepare_info(self):
        bytes_to_str_mod = lambda x : bytes_to_str(x) if isinstance(x,int) else x

        info_list = []

        self.txtinfo = 'init'
        self.txtinfo_basic = 'init-basic'
        self.txtinfo_short = 'init-short'

        try:
            self.FILE_SIZE = stat(self.file_path).st_size
        except Exception as e:
            print('prepare_info stat error:%s' % e )
        else:
            self_header = self.header

            local_time = strftime('%Y/%m/%d %H:%M:%S',localtime_catched(self_header.creation_time))
            info_list.append(f'record label    : {self_header.label}')
            info_list.append('')
            info_list.append(f'scanned path    : {self_header.scan_path}')
            info_list.append(f'scanned space   : {bytes_to_str(self_header.sum_size)}')
            info_list.append(f'scanned files   : {fnumber(self_header.quant_files)}')
            info_list.append(f'scanned folders : {fnumber(self_header.quant_folders)}')
            
            info_list.append('')
            info_list.append(f'creation host   : {self_header.creation_host} ({self_header.creation_os})')
            info_list.append(f'creation time   : {local_time}')
            
            self.txtinfo_short = '\n'.join(info_list)
            self.txtinfo_basic = '\n'.join(info_list)

            info_list.append('')
            info_list.append(f'record file     : {self.FILE_NAME} ({bytes_to_str(self.FILE_SIZE)}, compression level:{self.header.compression_level})')
            info_list.append('')
            info_list.append( 'data collection times:')
            info_list.append(f'filesystem      : {str(round(self_header.scanning_time,2))}s')
            if self_header.cde_stats_time_all:
                info_list.append(f'custom data     : {str(round(self_header.cde_stats_time_all,2))}s')
                
            info_list.append('')
            info_list.append( 'serializing and compression times:')
            info_list.append(f'file structure  : {str(round(self_header.filestructure_time,2))}s')
            info_list.append(f'file names      : {str(round(self_header.filenames_time,2))}s')
            info_list.append(f'custom data     : {str(round(self_header.customdata_time,2))}s')
            info_list.append('')
            info_list.append(f'custom data extraction errors : {fnumber(self_header.files_cde_errors_quant_all)}')
                
            info_list.append('')
            info_list.append( 'internal sizes  :  compressed  serialized    original       items  references    CDE time  CDE errors')
            info_list.append('')
            
            h_data = self.header_sizes
            fs_data = self_header.zipinfo["filestructure"]
            fn_data = self_header.zipinfo["filenames"]
            cd_data = self_header.zipinfo["customdata"]

            info_list.append(f'header          :{bytes_to_str_mod(h_data[0]).rjust(12)          }{bytes_to_str_mod(h_data[1]).rjust(12)     }{bytes_to_str_mod(h_data[2]).rjust(12)    }')
            info_list.append(f'filestructure   :{bytes_to_str_mod(fs_data[0]).rjust(12)         }{bytes_to_str_mod(fs_data[1]).rjust(12)    }{bytes_to_str_mod(fs_data[2]).rjust(12)   }')
            info_list.append(f'file names      :{bytes_to_str_mod(fn_data[0]).rjust(12)         }{bytes_to_str_mod(fn_data[1]).rjust(12)    }{bytes_to_str_mod(fn_data[2]).rjust(12)   }{fnumber(self_header.items_names).rjust(12)    }{fnumber(self_header.references_names).rjust(12)}')
            
            if cd_data[0]:
                info_list.append(f'custom data     :{bytes_to_str_mod(cd_data[0]).rjust(12)     }{bytes_to_str_mod(cd_data[1]).rjust(12)     }{bytes_to_str_mod(cd_data[2]).rjust(12)  }{fnumber(self_header.items_cd).rjust(12)       }{fnumber(self_header.references_cd).rjust(12)}')
            
            info_list.append('')
            
            try:
                if self_header.cde_list:
                    info_list.append('\nCustom data with details about the rules:')
                    for nr,(expressions,use_smin,smin_int,use_smax,smax_int,executable,parameters,shell,timeout,crc) in enumerate(self_header.cde_list):
                        info_list.append(f'\nrule nr    : {nr}                           {bytes_to_str(self_header.cde_stats_size[nr]).rjust(12)}{fnumber(self_header.cde_stats_uniq[nr]).rjust(12)}{fnumber(self_header.cde_stats_refs[nr]).rjust(12)}{str(round(self_header.cde_stats_time[nr],2)).rjust(12)}s{fnumber(self_header.files_cde_errors_quant[nr]).rjust(11)}')
                        
                        info_list.append(f'files      : {expressions}')
                        if use_smin:
                            info_list.append(f'min size   : {bytes_to_str(smin_int)}')
                        if use_smax:
                            info_list.append(f'max size   : {bytes_to_str(smax_int)}')
                        
                        in_shell_string = '(in shell)' if shell else ''
                        info_list.append(f'command    : {executable} {parameters} {in_shell_string}')
                        if timeout:
                            info_list.append(f'timeout    : {timeout}s')
                        

            except Exception as EE:
                print(EE)
                pass

            info_list.append('')
            
            loaded_fs_info = 'filesystem  - ' + ('loaded' if self.decompressed_filestructure else 'not loaded yet')
            loaded_cd_info = 'custom data - ' + ('not present' if not bool(cd_data[0]) else 'loaded' if self.decompressed_customdata else 'not loaded yet')
            info_list.append(loaded_fs_info)
            info_list.append(loaded_cd_info)
            
            self.txtinfo_basic = self.txtinfo_basic + f'\n\n{loaded_fs_info}\n{loaded_cd_info}'

        self.txtinfo = '\n'.join(info_list)
    
    def has_cd(self):
        return bool(self.header.zipinfo["customdata"][0])
        
    def save(self,file_path=None,compression_level=16):
        if file_path:
            filename = basename(normpath(file_path))
        else:
            filename = self.FILE_NAME = self.new_file_name()
            file_path = sep.join([self.db_dir,filename])
        
        self.file_path = file_path
        
        self.info_line = f'saving {filename}'

        self.log.info('saving %s' % file_path)
        
        self_header = self.header
        
        with ZipFile(file_path, "w") as zip_file:
            compressor = ZstdCompressor(level=compression_level,threads=-1)
            compressor_compress = compressor.compress
            
            t0 = perf_counter()
            self.info_line = f'serializing file stucture'
            filestructure_ser = dumps(self.filestructure)
            self.info_line = f'compressing file stucture'
            filestructure_ser_compr = compressor_compress(filestructure_ser)
            self_header.zipinfo['filestructure'] = (asizeof(filestructure_ser_compr),asizeof(filestructure_ser),asizeof(self.filestructure))

            t1 = perf_counter()
            self.info_line = f'serializing file names'
            filenames_ser = dumps(self.filenames)
            self.info_line = f'compressing file names'
            filenames_ser_comp = compressor_compress(filenames_ser)
            self_header.zipinfo['filenames'] = (asizeof(filenames_ser_comp),asizeof(filenames_ser),asizeof(self.filenames))
            
            t2 = perf_counter()
            if self.customdata:
                self.info_line = f'serializing custom data'
                customdata_ser = dumps(self.customdata)
                self.info_line = f'compressing custom data'
                customdata_ser_compr = compressor_compress(customdata_ser)
                self_header.zipinfo['customdata'] = (asizeof(customdata_ser_compr),asizeof(customdata_ser),asizeof(self.customdata))
            else:
                self_header.zipinfo['customdata'] = (0,0,0)
            
            t3 = perf_counter()
        
            self.header.compression_level = compression_level
            
            self.header.filestructure_time = t1-t0
            self.header.filenames_time = t2-t1
            self.header.customdata_time = t3-t2
        
            ###########
            header_ser = dumps(self_header)
            header_ser_compr = compressor_compress(header_ser)
            self.header_sizes=(asizeof(header_ser_compr),asizeof(header_ser),asizeof(self_header))
            
            zip_file.writestr('header',header_ser_compr)
            ###########
            self.info_line = f'saving {filename} (File stucture)'
            zip_file.writestr('filestructure',filestructure_ser_compr)

            self.info_line = f'saving {filename} (File names)'
            zip_file.writestr('filenames',filenames_ser_comp)

            if self.customdata:
                self.info_line = f'saving {filename} (Custom Data)'
                zip_file.writestr('customdata',customdata_ser_compr)

        self.prepare_info()

        self.info_line = ''

    def load_wrap(self,db_dir,file_name):
        self.FILE_NAME = file_name
        file_path = sep.join([db_dir,self.FILE_NAME])

        return self.load(file_path)

    def load(self,file_path):
        self.file_path = file_path
        file_name = basename(normpath(file_path))
        
        #self.log.info('loading %s' % file_name)
        #TODO - problem w podprocesie

        try:
            with ZipFile(file_path, "r") as zip_file:
                header_ser_compr = zip_file.read('header')
                header_ser = ZstdDecompressor().decompress(header_ser_compr)
                self.header = loads( header_ser )
                self.header_sizes=(asizeof(header_ser_compr),asizeof(header_ser),asizeof(self.header))

            if self.header.data_format_version != data_format_version:
                message = f'loading "{file_path}" error: incompatible data format version: {self.header.data_format_version} vs {data_format_version}'
                self.log.error(message)
                return message
            
            self.prepare_info()

        except Exception as e:
            message = f'loading "{file_path}" error: "{e}"'
            #self.log.error(message)
            return message

        return False

    decompressed_filestructure = False
    def decompress_filestructure(self):
        if not self.decompressed_filestructure:
            with ZipFile(self.file_path, "r") as zip_file:
                decompressor = ZstdDecompressor()

                filestructure_ser = decompressor.decompress(zip_file.read('filestructure'))
                self.filestructure = loads( filestructure_ser )

                filenames_ser = decompressor.decompress(zip_file.read('filenames'))
                self.filenames = loads(filenames_ser)

            self.decompressed_filestructure = True
            self.prepare_info()

            return True

        return False
    
    def unload_filestructure(self):
        self.decompressed_filestructure = False
        self.filestructure = ()
        self.prepare_info()
            
    decompressed_customdata = False
    def decompress_customdata(self):
        if not self.decompressed_customdata:
            with ZipFile(self.file_path, "r") as zip_file:
                try:
                    customdata_ser_comp = zip_file.read('customdata')
                    customdata_ser = ZstdDecompressor().decompress(customdata_ser_comp)
                    self.customdata = loads( customdata_ser )
                except:
                    self.customdata = []

            self.decompressed_customdata = True
            self.prepare_info()
            
            return True

        return False
    
    def unload_customdata(self):
        self.decompressed_customdata = False
        self.customdata = []
        self.prepare_info()
    
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

    def threaded_read_records(self,load_errors):
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
            
            
            if res:=new_record.load_wrap(self.db_dir,filename) :
                self.log.warning('removing:%s',filename)
                self.records.remove(new_record)
                load_errors.append(res)
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
            t_min,t_max,
            find_filename_search_kind,name_expr,name_case_sens,
            find_cd_search_kind,cd_expr,cd_case_sens,
            filename_fuzzy_threshold,cd_fuzzy_threshold):

        self.log.info(f'find_items_in_records {size_min},{size_max},\
            {find_filename_search_kind},{name_expr},{name_case_sens},\
            {find_cd_search_kind},{cd_expr},{cd_case_sens},\
            {filename_fuzzy_threshold},{cd_fuzzy_threshold}')

        self.find_results_clean()

        records_to_process = [range_par] if range_par else list(self.records)

        records_to_process.sort(reverse = True,key = lambda x : x.header.quant_files)

        record_commnad_list={}
        for record_nr,record in enumerate(records_to_process):
            if windows:
                if getattr(sys, 'frozen', False):
                    curr_command_list = record_commnad_list[record_nr] = ['record.exe', 'load',record.file_path]
                else:
                    curr_command_list = record_commnad_list[record_nr] = ['python','src\\record.py', 'load',record.file_path]
            else:
                if getattr(sys, 'frozen', False):
                    curr_command_list = record_commnad_list[record_nr] = ['./record', 'load',record.file_path]
                else:
                    curr_command_list = record_commnad_list[record_nr] = ['python3','./src/record.py', 'load',record.file_path]
            
            if t_min:
                curr_command_list.extend( ['--timestamp_min',str(t_min) ] )
                
            if t_max:
                curr_command_list.extend( ['--timestamp_max',str(t_max)] )
            
            if size_min:
                curr_command_list.extend( ['--size_min',str(size_min).replace(' ','') ] )

            if size_max:
                curr_command_list.extend( ['--size_max',str(size_max).replace(' ','')] )

            if name_expr:
                if find_filename_search_kind == 'regexp':
                    curr_command_list.extend(['--file_regexp',name_expr])
                elif find_filename_search_kind == 'glob':
                    curr_command_list.extend(['--file_glob',name_expr])
                    if name_case_sens:
                        curr_command_list.append('--file_case_sensitive')
                elif find_filename_search_kind == 'fuzzy':
                    curr_command_list.extend(['--file_fuzzy',name_expr,'--file_fuzzy_threshold',filename_fuzzy_threshold])
            elif find_filename_search_kind == 'error':
                    curr_command_list.append('--file_error')

            if cd_expr:
                if find_cd_search_kind == 'regexp':
                    curr_command_list.extend( ['--cd_regexp',cd_expr] )
                elif find_cd_search_kind == 'glob':
                    curr_command_list.extend( ['--cd_glob',cd_expr] )
                    if cd_case_sens:
                        curr_command_list.append('--cd_case_sensitive')
                elif find_cd_search_kind == 'fuzzy':
                    curr_command_list.extend( ['--cd_fuzzy',cd_expr,'--cd_fuzzy_threshold',cd_fuzzy_threshold] )
            elif find_cd_search_kind == 'without':
                curr_command_list.append('--cd_without')
            elif find_cd_search_kind == 'any':
                curr_command_list.append('--cd_ok')
            elif find_cd_search_kind == 'error':
                curr_command_list.append('--cd_error')

            self.log.info(f'curr_command_list: {curr_command_list}')

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

        #####################################################
        def threaded_run(record_nr,commands_list,results_list,progress_list,info_list,processes_list):
            results_list_append = results_list[record_nr].find_results.append

            try:
                subprocess = Popen(commands_list[record_nr], stdout=PIPE, stderr=STDOUT,shell=False,text=True)
            except Exception as re:
                print('threaded_run run error',re)
                info_list[record_nr].append(f'threaded_run run error: {re}')
                sys.exit() #thread

            processes_list[record_nr]=subprocess
            subprocess_stdout_readline = subprocess.stdout.readline
            subprocess_poll = subprocess.poll

            while True:
                if line := subprocess_stdout_readline():
                    try:
                        if line[0]!='#':
                            val = json_loads(line.strip())

                            progress_list[record_nr]=int(val[0])
                            if len(val)>1:
                                results_list_append( tuple([tuple(val[3:]),int(val[1]),int(val[2])]) )
                        else:
                            info_list[record_nr].append(line.strip())
                    except Exception as e:
                        print('threaded_run work error:',e,line)
                        info_list[record_nr].append(f'threaded_run work error: {e} line: {line}')
                else:
                    if subprocess_poll() is not None:
                        break
                    sleep(0.01)
            sys.exit() #thread

        #####################################################
        self.info_line = 'Initializing subprocesses ...'
        jobs = {}

        total_progress=[]
        info_list=[]
        processes_list=[]

        for record_nr,record in enumerate(records_to_process):
            total_progress.append(0)
            info_list.append([])
            processes_list.append(None)

            #abort_queues.append(Queue())

            jobs[record_nr] = [0,None]

            record.find_results=[]

        self.info_line = 'subprocesses run.'

        ############################################################
        #jobs[0] CODES
        #0 - waiting
        #1 - started and alive
        #2 - started and !alive

        while True:
            if self.abort_action:
                self.info_line = 'Aborting ...'

                for record_nr,subprocess in enumerate(processes_list):
                    if subprocess:
                        try:
                            subprocess.kill()
                        except Exception as ke:
                            print('killing error:',ke)

                break

            waiting_list = [ record_nr for record_nr in range(records_to_process_len) if jobs[record_nr][0]==0 ]
            waiting = len(waiting_list)
            running = len([record_nr for record_nr in range(records_to_process_len) if jobs[record_nr][0]==1 and jobs[record_nr][1].is_alive() ])
            finished = self.search_record_nr = records_to_process_len-running-waiting
            
            self.records_perc_info = self.search_record_nr * 100.0 / records_to_process_len

            self.info_line = f'Threads: waiting:{waiting}, running:{running}, finished:{finished}'

            if waiting:
                if running<max_processes:
                    record_nr = waiting_list[0]
                    job = jobs[record_nr]
                    job[1] = Thread(target=lambda : threaded_run(record_nr,record_commnad_list,records_to_process,total_progress,info_list,processes_list),daemon=True)
                    job[1].start()
                    job[0] = 1
                    sleep(0.01)
                    continue

            self.total_search_progress = sum(total_progress)
            self.find_res_quant = sum([len(record.find_results) for record in records_to_process])

            if running==0 and waiting==0:
                break

            sleep(0.1)
        #####################################################
        for record_nr,info in enumerate(info_list):
            self.log.info(f'got info for record:{record_nr}')
            for info_line in info:
                self.log.info(info_line)
            self.log.info('')

        for subprocess_combo in jobs.values():
            if subprocess_combo[0]==1:
                subprocess_combo[1].join()

        return True

    ########################################################################################################################

    def delete_record(self,record):
        file_path = sep.join([self.db_dir,record.FILE_NAME])
        
        self.records.remove(record)
        
        self.log.info('removing file to trash:%s',file_path)
        try:
            send2trash_delete(file_path)
        except Exception as e:
            self.log.error(f'removing file to trash failed:{e}. Deleting permanently.')
            try:
                os_remove(file_path)
            except Exception as e2:
                self.log.error(f'deleting permanently failed:{e2}.')
        
        
        del record
        self.update_sorted()
