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

from gc import disable as gc_disable, enable as gc_enable,collect as gc_collect

from json import loads as json_loads
from subprocess import Popen, STDOUT,DEVNULL,PIPE, run as subprocess_run

from time import sleep, perf_counter,time,strftime,localtime,mktime
from threading import Thread
from os import cpu_count,scandir,stat,sep,name as os_name,remove as os_remove,kill,rename

from tempfile import mkdtemp
windows = bool(os_name=='nt')

if windows:
    from subprocess import CREATE_NO_WINDOW
else:
    from os import getpgid, killpg

from os.path import abspath,normpath,basename,dirname,join as path_join

from zipfile import ZipFile
from platform import system as platform_system,release as platform_release,node as platform_node

from ciso8601 import parse_datetime
from fnmatch import fnmatch
from re import search as re_search
import sys
from collections import defaultdict
from pathlib import Path as pathlib_Path
from signal import SIGTERM,SIGINT,SIGABRT
if windows:
    from signal import CTRL_C_EVENT

from re import compile as re_compile

from pickle import dumps,loads
from zstandard import ZstdCompressor,ZstdDecompressor
from pympler.asizeof import asizeof
from send2trash import send2trash as send2trash_delete
from psutil import Process

from copy import deepcopy

PARAM_INDICATOR_SIGN = '%'

DATA_FORMAT_VERSION='0019'

VERSION_FILE='version.txt'

SCAN_DAT_FILE = 'scaninfo'
SEARCH_DAT_FILE = 'searchinfo'
SIGNAL_FILE = 'signal'

def get_dev_labes_dict():
    lsblk = subprocess_run(['lsblk','-fJ'],capture_output = True,text = True)
    lsblk.dict = json_loads(lsblk.stdout)

    res_map = {}
    def dict_parse(src_dict,res_map):
        if 'children' in src_dict:
            for l_elem in src_dict['children']:
                d_l_elem = dict(l_elem)
                dict_parse(d_l_elem,res_map)

        for mountpoint in src_dict['mountpoints']:
            res_map[mountpoint] = src_dict['label']

    for l_elem in lsblk.dict['blockdevices']:
        d_l_elem = dict(l_elem)
        dict_parse(d_l_elem,res_map)

    return res_map

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
    try:
        string = string.replace(' ','').lower().rstrip('b')
        string_endswith = string.endswith
        for suffix,weight in ( ('k',1024),('m',1024*1024),('g',1024*1024*1024),('t',1024*1024*1024*1024) ):
            if string_endswith(suffix):
                return int(string[0:-1]) * weight #no decimal point

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

def byte_to_bools(byte, num_bools=10):
    bool_list = [False]*num_bools

    for i in range(num_bools):
        if byte & (1 << i):
            bool_list[num_bools-1-i]=True

    return tuple(bool_list)

def test_regexp(expr):
    teststring='abc'
    try:
        re_search(expr,teststring)
    except Exception as e:
        return e

    return None

LUT_encode={}
LUT_decode={}

def prepare_LUTs():
    #global LUT_decode,LUT_encode
    for i in range(1024):
        temp_tuple = LUT_decode[i]=byte_to_bools(i)
        LUT_encode[temp_tuple]=i

prepare_LUTs()

def get_command(executable,parameters,full_file_path,shell):
    if shell:
        if PARAM_INDICATOR_SIGN in executable:
            res = executable.replace(f'"{PARAM_INDICATOR_SIGN}"',PARAM_INDICATOR_SIGN).replace(f"'{PARAM_INDICATOR_SIGN}'",PARAM_INDICATOR_SIGN).replace(PARAM_INDICATOR_SIGN,f'"{full_file_path}"')
        else:
            res = executable + ' ' + f'"{full_file_path}"'

        return res,res
    else:
        if not parameters:
            res = [executable.strip()] + [full_file_path]
        elif PARAM_INDICATOR_SIGN not in parameters:
            res = [executable.strip()] + parameters.strip().split() + [full_file_path]
        else:
            res = [executable.strip()] + [p_elem.replace(PARAM_INDICATOR_SIGN,full_file_path) for p_elem in parameters.replace(f'"{PARAM_INDICATOR_SIGN}"',PARAM_INDICATOR_SIGN).replace(f"'{PARAM_INDICATOR_SIGN}'",PARAM_INDICATOR_SIGN).strip().split() if p_elem]

    return res,' '.join(res)

#'ignore','replace','backslashreplace'
def popen_win(command,shell,stdin=DEVNULL):
    return Popen(command, stdout=PIPE, stderr=STDOUT,stdin=stdin,shell=shell,text=True,universal_newlines=True,bufsize=-1,errors='ignore',creationflags=CREATE_NO_WINDOW)
    #,close_fds=False

def popen_lin(command,shell,stdin=DEVNULL):
    return Popen(command, stdout=PIPE, stderr=STDOUT,stdin=stdin,shell=shell,text=True,universal_newlines=True,bufsize=-1,errors='ignore',start_new_session=True)

uni_popen = (lambda command,shell=False,stdin=DEVNULL : popen_win(command,shell,stdin)) if windows else (lambda command,shell=False,stdin=DEVNULL : popen_lin(command,shell,stdin))

def send_signal(subproc,temp_dir,kind=0):
    try:
        signal_file = sep.join([temp_dir,SIGNAL_FILE])

        temp_signal_file = signal_file+ '_temp'
        with open(temp_signal_file,'w') as tsf:
            tsf.write(str(kind))

        rename(temp_signal_file, signal_file)

    except Exception as se:
        print(f'subprocess signal error: {se}')

def kill_subprocess(subproc,print_func=print):
    try:
        pid = subproc.pid

        if windows:
            kill_cmd = ['taskkill', '/F', '/T', '/PID', str(pid)]
            print_func( ('info',f'killing pid: {pid}') )
            subprocess_run(kill_cmd)
        else:
            print_func( ('info',f'killing process group of pid {pid}') )
            killpg(getpgid(pid), SIGTERM)

    except Exception as ke:
        print_func( ('error',f'kill_subprocess error: {ke}') )

def compress_with_header_update(header,data,compression,datalabel,zip_file):
    t0 = perf_counter()
    data_ser = dumps(data)
    data_ser_compr = ZstdCompressor(level=compression,threads=-1).compress(data_ser)
    t1 = perf_counter()
    tdiff=t1-t0

    header.zipinfo[datalabel]=(asizeof(data_ser_compr),asizeof(data_ser),asizeof(data))
    header.compression_time[datalabel] = tdiff
    zip_file.writestr(datalabel,data_ser_compr)

CREATION_CODE = 0
EXPORT_CODE = 1
IMPORT_CODE = 2
REPACK_CODE = 3

hist_code_2_str={CREATION_CODE:'creation ',EXPORT_CODE:'export   ',IMPORT_CODE:'import   ',REPACK_CODE:'repack   '}

#######################################################################
class Header :
    def __init__(self,label='',scan_path=''):
        self.label=label
        self.scan_path = scan_path
        self.creation_time = int(time())
        self.rid = self.creation_time #record id

        self.quant_files = 0
        self.quant_folders = 0
        self.sum_size = 0
        self.data_format_version=DATA_FORMAT_VERSION

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

        self.scanning_time=0

        self.compression_level=0

        self.creation_os,self.creation_host = f'{platform_system()} {platform_release()}',platform_node()

        self.compression_time = {}
        self.compression_time['filestructure']=0
        self.compression_time['filenames']=0
        self.compression_time['customdata']=0

        self.history_stack=[ (CREATION_CODE,int(time())) ]

#######################################################################
class LibrerRecord:
    def __init__(self,label=None,scan_path=None,file_path=None):
        self.header = Header(label,scan_path)

        self.filestructure = ()
        self.customdata = []
        self.filenames = []

        self.find_results = []
        self.find_results_tuples_set=set()

        self.abort_action = False

        self.file_name = ''
        self.file_path = ''

    def find_results_clean(self):
        self.find_results = []

    def new_file_name(self):
        return f'{self.header.rid}.dat'

    def abort(self):
        self.abort_action = True

    def load(self,file_path):
        self.file_path = file_path
        self.file_name = basename(normpath(file_path))

        try:
            with ZipFile(file_path, "r") as zip_file:
                header_ser_compr = zip_file.read('header')
                header_ser = ZstdDecompressor().decompress(header_ser_compr)
                self.header = loads( header_ser )
                self.header.zipinfo["header"]=(asizeof(header_ser_compr),asizeof(header_ser),asizeof(self.header))

            if self.header.data_format_version != DATA_FORMAT_VERSION:
                return f'loading "{file_path}" error: incompatible data format version: {self.header.data_format_version} vs {DATA_FORMAT_VERSION}'

            self.prepare_info()

        except Exception as e:
            return f'loading "{file_path}" error: "{e}"'

        return False

    def save(self,print_func,file_path=None,compression_level=9):
        if file_path:
            filename = basename(normpath(file_path))
        else:
            filename = self.file_name = self.new_file_name()
            file_path = sep.join([self.db_dir,filename])

        self.file_path = file_path

        self_header = self.header

        self.header.compression_level = compression_level

        with ZipFile(file_path, "w") as zip_file:
            def compress_with_header_update_wrapp(data,datalabel):
                print_func(['save',f'compressing {datalabel}'],True)
                compress_with_header_update(self.header,data,compression_level,datalabel,zip_file)

            compress_with_header_update_wrapp(self.filestructure,'filestructure')

            compress_with_header_update_wrapp(self.filenames,'filenames')

            if self.customdata:
                compress_with_header_update_wrapp(self.customdata,'customdata')
            else:
                self_header.zipinfo['customdata'] = (0,0,0)

            compress_with_header_update_wrapp(self.header,'header')

        if False:
            with open(file_path+'.debug.txt', "w") as txt_file:
                #txt_file.write(str(self.header) + '\n')

                txt_file.write('-------------------------------\nheader:\n\n')
                for k,v in vars(self.header).items():
                    txt_file.write(f'  {k}:{v}\n')

                txt_file.write('\n\n-------------------------------\nfilestructure:\n\n')
                txt_file.write(str(self.filestructure))
                txt_file.write('\n\n-------------------------------\nfilenames:\n\n')
                txt_file.write(str(self.filenames))
                if self.customdata:
                    txt_file.write('\n-------------------------------\ncustomdata\n')
                    txt_file.write(self.customdata)

        self.prepare_info()

        print_func(['save','finished'],True)

    def scan_rec(self,print_func,abort_list,path, scan_like_data,filenames_set,check_dev=True,dev_call=None) :
        if any(abort_list) :
            return True

        path_join_loc = path_join

        local_folder_size_with_subtree=0
        local_folder_size = 0
        subitems=0

        self_scan_rec = self.scan_rec

        filenames_set_add = filenames_set.add
        self_header_ext_stats = self.header.ext_stats
        self_header_ext_stats_size = self.header.ext_stats_size
        try:
            with scandir(path) as res:

                local_folder_files_count = 0
                local_folder_folders_count = 0

                for entry in res:
                    subitems+=1
                    if any(abort_list) :
                        break

                    entry_name = entry.name
                    filenames_set_add(entry_name)

                    is_dir,is_file,is_symlink = entry.is_dir(),entry.is_file(),entry.is_symlink()

                    ext=pathlib_Path(entry).suffix

                    if is_file:
                        self_header_ext_stats[ext]+=1

                    try:
                        stat_res = stat(entry)
                        mtime = int(stat_res.st_mtime)
                        dev=stat_res.st_dev
                    except Exception as e:
                        print_func( ('error',f'stat {entry_name} error:{e}') )
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
                                    #self.log.info('devices mismatch:%s %s %s %s' % (path,entry_name,dev_call,dev) )
                                    print_func( ('info',f'devices mismatch:{path},{entry_name},{dev_call},{dev}') )
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
                                size,sub_sub_items = self_scan_rec(print_func,abort_list,path_join_loc(path,entry_name),dict_entry,filenames_set,check_dev,dev)
                                has_files = bool(sub_sub_items)

                                local_folder_size_with_subtree += size

                            local_folder_folders_count += 1
                        else:
                            if is_symlink :
                                has_files = False
                                size = 0
                            else:
                                has_files = False
                                size = int(stat_res.st_size)
                                self_header_ext_stats_size[ext]+=size

                                local_folder_size += size

                            local_folder_files_count += 1

                        temp_list_ref = scan_like_data[entry_name]=[size,is_dir,is_file,is_symlink,is_bind,has_files,mtime]

                        if dict_entry:
                            temp_list_ref.append(dict_entry)

                self_header = self.header
                self_header.sum_size += local_folder_size
                self_header.quant_files += local_folder_files_count
                self_header.quant_folders += local_folder_folders_count

                print_func( ('scan',self_header.sum_size,self_header.quant_files,self_header.quant_folders,path) )

        except Exception as e:
            print_func( ('error', f'scandir {path} error:{e}') )

        return (local_folder_size_with_subtree+local_folder_size,subitems)

    def scan(self,print_func,abort_list,cde_list,check_dev=True):
        self.header.sum_size = 0

        self.header.ext_stats=defaultdict(int)
        self.header.ext_stats_size=defaultdict(int)
        self.scan_data={}

        #########################
        time_start = perf_counter()
        filenames_set=set()
        self.scan_rec(print_func,abort_list,self.header.scan_path,self.scan_data,filenames_set,check_dev=check_dev)
        time_end = perf_counter()

        self.header.scanning_time = time_end-time_start

        self.filenames = tuple(sorted(list(filenames_set)))

        self.filenames_helper = {fsname:fsname_index for fsname_index,fsname in enumerate(self.filenames)}

        self.header.cde_list = cde_list
        self.cd_stat=[0]*len(cde_list)

        self.customdata_pool = {}
        self.customdata_pool_index = 0

        if cde_list:
            print_func( ('info','estimating files pool for custom data extraction') )
            self.prepare_customdata_pool_rec(print_func,abort_list,self.scan_data,[])

    def prepare_customdata_pool_rec(self,print_func,abort_list,scan_like_data,parent_path):
        self_header = self.header
        scan_path = self_header.scan_path
        self_prepare_customdata_pool_rec = self.prepare_customdata_pool_rec

        cde_list = self_header.cde_list
        self_customdata_pool = self.customdata_pool

        for entry_name,items_list in scan_like_data.items():
            size,is_dir,is_file,is_symlink,is_bind,has_files,mtime = items_list[0:7]

            if any(abort_list) :
                break
            try:
                subpath_list = parent_path + [entry_name]

                if not is_symlink and not is_bind:
                    if is_dir:
                        if has_files:
                            self_prepare_customdata_pool_rec(print_func,abort_list,items_list[7],subpath_list)
                    else:
                        subpath=sep.join(subpath_list)
                        ############################

                        full_file_path = normpath(abspath(sep.join([scan_path,subpath])))

                        matched = False

                        rule_nr=-1
                        for expressions,use_smin,smin_int,use_smax,smax_int,executable,parameters,shell,timeout,crc in cde_list:
                            if any(abort_list) :
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
                                if any(abort_list) :
                                    break
                                if matched:
                                    break

                                if fnmatch(full_file_path,expr):
                                    self_customdata_pool[self.customdata_pool_index]=(items_list,subpath,rule_nr,size)
                                    self.customdata_pool_index += 1
                                    self.cd_stat[rule_nr]+=1
                                    self_header.files_cde_size_sum += size
                                    matched = True

            except Exception as e:
                #self.log.error('prepare_customdata_pool_rec error::%s',e )
                #print('prepare_customdata_pool_rec',e,entry_name,size,is_dir,is_file,is_symlink,is_bind,has_files,mtime)
                print_func( ('error','prepare_customdata_pool_rec:{e},{entry_name},{size},{is_dir},{is_file},{is_symlink},{is_bind},{has_files},{mtime}') )

    def extract_customdata(self,print_func,abort_list):
        self_header = self.header
        scan_path = self_header.scan_path

        print_func( ('info','custom data extraction ...'),True)

        self_header.files_cde_quant = 0
        self_header.files_cde_size = 0
        self_header.files_cde_size_extracted = 0
        self_header.files_cde_errors_quant = defaultdict(int)
        self_header.files_cde_errors_quant_all = 0
        files_cde_quant_sum = self_header.files_cde_quant_sum = len(self.customdata_pool)
        files_cde_size_sum = self_header.files_cde_size_sum
        cde_list = self.header.cde_list

        print_func( ('cdeinit',files_cde_quant_sum,files_cde_size_sum),True)

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

            aborted_string = 'Custom data extraction was aborted.'

            files_cde_errors_quant = defaultdict(int)

            files_cde_quant = 0
            files_cde_size = 0
            files_cde_size_extracted = 0

            files_cde_errors_quant_all = 0
            for (scan_like_list,subpath,rule_nr,size) in self.customdata_pool.values():

                self.killed=False

                time_start = perf_counter()
                if abort_list[0] : #wszystko
                    returncode=200
                    output = aborted_string
                    aborted = True
                else:
                    aborted = False

                    returncode=202
                    expressions,use_smin,smin_int,use_smax,smax_int,executable,parameters,shell,timeout,do_crc = cde_list[rule_nr]
                    full_file_path = normpath(abspath(sep.join([scan_path,subpath]))).replace('/',sep)
                    command,command_info = get_command(executable,parameters,full_file_path,shell)

                    #print_func( ('cde',f'{full_file_path} ({bytes_to_str(size)})',size,files_cde_size_extracted,files_cde_errors_quant_all,files_cde_quant,files_cde_quant_sum,files_cde_size,files_cde_size_sum) )
                    print_func( ('cde',f'{full_file_path} ({bytes_to_str(size)})',size,files_cde_size_extracted,files_cde_errors_quant_all,files_cde_quant,files_cde_size) )

                    timeout_val=time()+timeout if timeout else None
                    #####################################

                    try:
                        subprocess = uni_popen(command,shell)
                        timeout_semi_list[0]=(timeout_val,subprocess)
                    except Exception as re:
                        timeout_semi_list[0]=None
                        returncode=201
                        output = f'Exception: {re}'
                    else:
                        subprocess_stdout_readline = subprocess.stdout.readline
                        subprocess_poll = subprocess.poll

                        output_list = []
                        output_list_append = output_list.append

                        while True:
                            line = subprocess_stdout_readline()

                            output_list_append(line.rstrip())

                            if not line and subprocess_poll() is not None:
                                returncode=subprocess.returncode
                                timeout_semi_list[0] = None
                                break

                        if self.killed:
                            output_list_append('Killed.')

                        output = '\n'.join(output_list).strip()
                        if not output:
                            output = 'No output collected.'
                            returncode=203

                    #####################################

                time_end = perf_counter()
                customdata_stats_time[rule_nr]+=time_end-time_start

                if returncode or self.killed or aborted:
                    files_cde_errors_quant[rule_nr]+=1
                    files_cde_errors_quant_all+=1

                if not aborted:
                    files_cde_quant += 1
                    files_cde_size += size
                    files_cde_size_extracted += asizeof(output)

                new_elem={}
                new_elem['cd_ok']= bool(returncode==0 and not self.killed and not aborted)

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

            self_header.files_cde_errors_quant=files_cde_errors_quant
            self_header.files_cde_errors_quant_all = files_cde_errors_quant_all

            self_header.files_cde_quant = files_cde_quant
            self_header.files_cde_size = files_cde_size
            self_header.files_cde_size_extracted = files_cde_size_extracted

            customdata_stats_time_all[0]=time_end_all-time_start_all
            sys.exit() #thread

        timeout_semi_list = [None]

        cde_thread = Thread(target = lambda : threaded_cde(timeout_semi_list),daemon=True)
        cde_thread.start()
        cde_thread_is_alive = cde_thread.is_alive

        while cde_thread_is_alive():
            if timeout_semi_list[0]:
                timeout_val,subprocess = timeout_semi_list[0]
                if any(abort_list) or (timeout_val and time()>timeout_val):
                    kill_subprocess(subprocess,print_func)
                    self.killed=True
                    abort_list[1]=False
                sleep(0.2)
            else:
                sleep(0.4)

        print_func( ('info','custom data extraction finished.'),True)

        cde_thread.join()

        del self.customdata_pool
        del customdata_helper

        self.header.cde_stats_size=customdata_stats_size
        self.header.cde_stats_uniq=customdata_stats_uniq
        self.header.cde_stats_refs=customdata_stats_refs
        self.header.cde_stats_time=customdata_stats_time
        self.header.cde_stats_time_all=customdata_stats_time_all[0]

    #############################################################
    def sld_recalc_rec(self,scan_like_data):
        new_size_on_this_level = 0
        new_files_quant_on_this_level = 0
        new_folders_quant_on_this_level = 0

        for entry_name,items_list in scan_like_data.items():
            (size,is_dir,is_file,is_symlink,is_bind,has_files,mtime) = items_list[0:7]

            elem_index = 7
            if has_files:
                sub_dict = items_list[elem_index]
                elem_index+=1

                sub_size,sub_quant,sub_folders_quant = self.sld_recalc_rec(sub_dict)
                new_size_on_this_level+=sub_size
                new_files_quant_on_this_level+=sub_quant
                new_folders_quant_on_this_level+=sub_folders_quant+1

                if size==0:
                    items_list[0]=sub_size
            elif is_file:
                new_files_quant_on_this_level+=1
                new_size_on_this_level+=size
            else:
                new_folders_quant_on_this_level+=1

        #scan_like_data[0]=new_size_on_this_level
        return new_size_on_this_level,new_files_quant_on_this_level,new_folders_quant_on_this_level

    #############################################################
    def tupelize_rec(self,scan_like_data,results_queue_put):
        LUT_encode_loc = LUT_encode

        self_tupelize_rec = self.tupelize_rec

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

                    try:
                        elem_index = 7
                        if has_files:
                            sub_dict = items_list[elem_index]
                            elem_index+=1
                    except:
                        #print('f1 error')
                        sub_dict={}

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

                    code_new = LUT_encode_loc[ (is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc,False,False) ]

                    sub_list_elem=[entry_name_index,code_new,size,mtime]

                    if has_files:
                        sub_list_elem.append(self_tupelize_rec(sub_dict,results_queue_put))

                    if has_cd: #only files
                        self.header.references_cd+=1
                        sub_list_elem.append( cd_index )
                    if has_crc: #only files
                        sub_list_elem.append( crc_val )

                    sub_list.append( tuple(sub_list_elem) )

                except Exception as e:
                    #self.log.error('tupelize_rec error:%s',e )
                    results_queue_put(f'tupelize_rec error:{e}' )
                    #print('tupelize_rec error:',e,' entry_name:',entry_name)

        return tuple(sorted(sub_list,key = lambda x : x[1:4]))
    #############################################################

    def pack_data(self,results_queue_put):
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

        code = LUT_encode[ (is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc,False,False) ]
        self.filestructure = ('',code,size,mtime,self.tupelize_rec(self.scan_data,results_queue_put))

        self.header.items_names=len(self.filenames)
        self.header.items_cd=len(self.customdata)

        del self.filenames_helper
        del self.scan_data

    def remove_cd_rec(self,tuple_like_data):
        LUT_decode_loc = LUT_decode

        self_remove_cd_rec = self.remove_cd_rec

        is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc,aux1,aux2 = LUT_decode_loc[tuple_like_data[1]]

        has_cd=False
        cd_ok=False

        code = LUT_encode[ (is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc,aux1,aux2) ]

        new_list = [tuple_like_data[0],code,tuple_like_data[2],tuple_like_data[3]]

        elem_index=4
        if has_files:
            sub_new_list=[]
            for sub_structure in tuple_like_data[elem_index]:
                sub_new_list.append(self_remove_cd_rec(sub_structure))
            elem_index+=1
            new_list.append(tuple(sorted( sub_new_list,key = lambda x : x[1:4] )))

        for elem in tuple_like_data[elem_index:]:
            new_list.append(elem)

        return tuple(new_list)

    ########################################################################################
    def find_items(self,
            print_func,abort_list,
            size_min,size_max,
            timestamp_min,timestamp_max,
            name_search_kind,name_func_to_call,
            cd_search_kind,cd_func_to_call,
            print_info_fn):

        self.decompress_filestructure()

        filenames_loc = self.filenames
        filestructure = self.filestructure

        search_progress = 0

        if cd_search_kind!='dont':
            self.decompress_customdata()

        LUT_decode_loc = LUT_decode

        use_size = bool(size_min or size_max)
        use_timestamp = bool(timestamp_min or timestamp_max)

        search_list = [ (filestructure[4],[]) ]
        search_list_pop = search_list.pop
        search_list_append = search_list.append

        cd_search_kind_is_regexp_glob_or_fuzzy = bool(cd_search_kind in ('regexp','glob','fuzzy'))
        cd_search_kind_is_dont_or_without = bool(cd_search_kind in ('dont','without'))

        when_folder_may_apply = bool(cd_search_kind_is_dont_or_without and not use_size and not use_timestamp)
        cd_search_kind_is_any = bool(cd_search_kind=='any')
        cd_search_kind_is_without = bool(cd_search_kind=='without')
        cd_search_kind_is_error = bool(cd_search_kind=='error')

        name_search_kind_is_error = bool(name_search_kind=='error')

        self_customdata = self.customdata

        while search_list:
            filestructure,parent_path_components = search_list_pop()

            for data_entry in filestructure:
                search_progress +=1

                name_nr,code,size,mtime = data_entry[0:4]

                name = filenames_loc[name_nr]

                is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc,aux1,aux2 = LUT_decode_loc[code]

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
                                print_func( (search_progress,size,mtime,*next_level) )

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
                            print_info_fn(f'find_items(1):{e}' )
                            continue

                    #oczywistosc
                    #if cd_search_kind=='dont':
                    #    pass

                    if cd_search_kind_is_any:
                        if not has_cd or not cd_ok:
                            continue
                    elif cd_search_kind_is_regexp_glob_or_fuzzy:
                        if has_cd and cd_ok:
                            cd_data = self_customdata[cd_nr][2]
                        else:
                            continue

                        if cd_func_to_call:
                            try:
                                if not cd_func_to_call(cd_data):
                                    continue
                            except Exception as e:
                                print_info_fn(f'find_items(2):{e}' )
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

                    print_func( (search_progress,size,mtime,*next_level) )

        print_func( [search_progress] )

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
            file_size = stat(self.file_path).st_size
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
            info_list.append(f'record file     : {self.file_name} ({bytes_to_str(file_size)}, compression level:{self.header.compression_level})')
            info_list.append('')
            info_list.append( 'data collection times:')
            info_list.append(f'filesystem      : {str(round(self_header.scanning_time,2))}s')
            if self_header.cde_stats_time_all:
                info_list.append(f'custom data     : {str(round(self_header.cde_stats_time_all,2))}s')

            info_list.append('')
            info_list.append( 'serializing and compression times:')

            filestructure_time = self.header.compression_time['filestructure']
            filenames_time = self.header.compression_time['filenames']
            customdata_time = self.header.compression_time['customdata']

            info_list.append(f'file structure  : {str(round(filestructure_time,2))}s')
            info_list.append(f'file names      : {str(round(filenames_time,2))}s')
            info_list.append(f'custom data     : {str(round(customdata_time,2))}s')
            info_list.append('')
            info_list.append(f'custom data extraction errors : {fnumber(self_header.files_cde_errors_quant_all)}')

            info_list.append('')
            info_list.append( 'internal sizes  :  compressed  serialized    original       items  references    CDE time  CDE errors')
            info_list.append('')

            h_data = self_header.zipinfo["header"]
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

                        expressions_expanded = ','.join(list(expressions))
                        info_list.append(f'files      : {expressions_expanded}')
                        if use_smin:
                            info_list.append(f'min size   : {bytes_to_str(smin_int)}')
                        if use_smax:
                            info_list.append(f'max size   : {bytes_to_str(smax_int)}')

                        in_shell_string = '(in shell)' if shell else ''
                        info_list.append(f'command    : {executable} {parameters} {in_shell_string}')
                        if timeout:
                            info_list.append(f'timeout    : {timeout}s')


            except Exception as EE:
                info_list.append(str(EE))

            info_list.append('')

            loaded_fs_info = 'filesystem  - ' + ('loaded' if self.decompressed_filestructure else 'not loaded yet')
            loaded_cd_info = 'custom data - ' + ('not present' if not bool(cd_data[0]) else 'loaded' if self.decompressed_customdata else 'not loaded yet')
            info_list.append(loaded_fs_info)
            info_list.append(loaded_cd_info)

            info_list.append('')
            info_list.append('history:')
            for hist_entry in self_header.history_stack:
                line_list = []

                try:
                    hist_code = hist_entry[0]
                    hist_time = hist_entry[1]

                    line_list.extend( [hist_code_2_str[hist_code],strftime('%Y/%m/%d %H:%M:%S',localtime_catched(hist_time))] )

                    if hist_code==CREATION_CODE:
                        pass
                    elif hist_code==EXPORT_CODE:
                        line_list.append(hist_entry[2])
                    elif hist_code==IMPORT_CODE:
                        line_list.append(hist_entry[2])
                    elif hist_code==REPACK_CODE:
                        line_list.append(f'lab:{hist_entry[2]}')
                        line_list.append(f'compr:{hist_entry[3]}')
                        line_list.append(f'cd:{"Yes" if hist_entry[4] else "No"}')
                    else:
                        line_list.append(f'unknown code:{hist_code}')

                except Exception as he:
                    line_list.append(str(he))

                info_list.append('  ' + ' '.join(line_list))
            self.txtinfo_basic = self.txtinfo_basic + f'\n\n{loaded_fs_info}\n{loaded_cd_info}'

            try:
                longest = max({len(ext) for ext in self.header.ext_stats})+2

                sublist=[]
                for ext,ext_stat in sorted(self.header.ext_stats.items(),key = lambda x : x[1],reverse=True):
                    sublist.append(f'{bytes_to_str(self.header.ext_stats_size[ext]).rjust(12)}  {fnumber(ext_stat).rjust(12)}      {ext}')
                info_list.append('')
                info_list.append('Files extensions statistics by quantity:')
                info_list.append('========================================')
                info_list.extend(sublist)

                sublist_size=[]
                for ext,ext_stat in sorted(self.header.ext_stats_size.items(),key = lambda x : x[1],reverse=True):
                    sublist_size.append(f'{bytes_to_str(self.header.ext_stats_size[ext]).rjust(12)}   {fnumber(self.header.ext_stats[ext]).rjust(12)}      {ext}')
                info_list.append('')
                info_list.append('Files extensions statistics by space:')
                info_list.append('========================================')
                info_list.extend(sublist_size)
            except Exception as se:
                #print(se)
                pass

        self.txtinfo = '\n'.join(info_list)

    def has_cd(self):
        return bool(self.header.zipinfo["customdata"][0])

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

    def __init__(self,db_dir,log):
        self.records = set()
        self.db_dir = db_dir
        self.log=log
        self.info_line = 'init'

        self.records_to_show=[]
        self.abort_action=False
        self.abort_action_single=False
        self.search_record_nr=0

        self.find_res_quant = 0
        self.records_perc_info = 0

        self.records_sorted = []

    def update_sorted(self):
        self.records_sorted = sorted(self.records,key = lambda x : x.header.creation_time)

    def create(self,label='',scan_path=''):
        new_record = LibrerRecord(label=label,scan_path=scan_path)
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

    def get_wii_files_dict(self,import_filenames):
        #<?xml version="1.0" encoding="UTF-8"?>
        re_obj_header_search = re_compile(r'.*<\?(.*)\?>.*').search

        #<!-- Generated by WhereIsIt Report Generator 3.93 -->
        re_obj_comment_search = re_compile(r'.*<!--(.*)-->.*').search

        re_obj_report_search = re_compile(r'.*<REPORT Title="([^"]+)">').search

        re_obj_report_end_search = re_compile(r'.*</REPORT>').search

        re_obj_item_search = re_compile(r'.*<ITEM ItemType="([^"]+)">').search
        re_obj_item_end_search = re_compile(r'.*/ITEM>.*').search

        re_obj_desc_search = re_compile(r'.*<DESCRIPTION>(.+)</DESCRIPTION>.*').search
        re_obj_desc_begin_search = re_compile(r'.*<DESCRIPTION>(.*)').search
        re_obj_desc_end_search = re_compile(r'(.*)</DESCRIPTION>.*').search

        re_obj_name_search = re_compile(r'.*<NAME>(.+)</NAME>.*').search
        re_obj_ext_search = re_compile(r'.*<EXT>(.+)</EXT>.*').search
        re_obj_size_search = re_compile(r'.*<SIZE>(.+)</SIZE>.*').search
        re_obj_date_search = re_compile(r'.*<DATE>(.+)</DATE>.*').search
        re_obj_disk_name_search = re_compile(r'.*<DISK_NAME>(.+)</DISK_NAME>.*').search
        re_obj_disk_type_search = re_compile(r'.*<DISK_TYPE>(.+)</DISK_TYPE>.*').search
        re_obj_disk_num_search = re_compile(r'.*<DISK_NUM>(.+)</DISK_NUM>.*').search
        re_obj_disk_location_search = re_compile(r'.*<DISK_LOCATION>(.+)</DISK_LOCATION>.*').search
        re_obj_path_search = re_compile(r'.*<PATH>(.+)</PATH>.*').search
        re_obj_time_search = re_compile(r'.*<TIME>(.+)</TIME>.*').search
        re_obj_crc_search = re_compile(r'.*<CRC>(.+)</CRC>.*').search
        re_obj_category_search = re_compile(r'.*<CATEGORY>(.+)</CATEGORY>.*').search
        re_obj_flag_search = re_compile(r'.*<FLAG>(.+)</FLAG>.*').search

        #######################################################################

        #l=0
        in_report=False
        in_item=False
        in_description=False

        demo_str = '*** DEMO ***'

        wii_paths_dict = {}
        wii_paths_dict_per_disk = defaultdict(dict)

        wii_path_tuple_to_data = {}
        wii_path_tuple_to_data_per_disk = defaultdict(dict)

        filenames_set=set()
        filenames_set_per_disk=defaultdict(set)

        filenames_set_add = filenames_set.add

        cd_set=set()
        cd_set_per_disk=defaultdict(set)

        cd_set_add = cd_set.add

        try:
            for import_filename in import_filenames:
                with open(import_filename,"rt", encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        try:
                            if in_report:
                                if in_item:
                                    if in_description:
                                        if match := re_obj_desc_end_search(line):
                                            item['description'].append(match.group(1))
                                            item['description'] = tuple(item['description'])
                                            in_description=False
                                        else:
                                            item['description'].append(line)

                                        continue

                                    elif not item['description']:
                                        if match := re_obj_desc_search(line):
                                            item['description']=match.group(1)
                                            continue

                                    elif match := re_obj_desc_begin_search(line):
                                        in_description=True
                                        item['description'].append(match.group(1))
                                        continue

                                    if not item['name']:
                                        if match := re_obj_name_search(line):
                                            item['name']=match.group(1)
                                            continue

                                    if not item['ext']:
                                        if match := re_obj_ext_search(line):
                                            item['ext'] = match.group(1)
                                            continue

                                    if not item['size']:
                                        if match := re_obj_size_search(line):
                                            try:
                                                item['size']=int(match.group(1))
                                            except:
                                                item['size']=0
                                            continue

                                    if not item['date']:
                                        if match := re_obj_date_search(line):
                                            item['date']=match.group(1)
                                            continue

                                    if not item['disk_name']:
                                        if match := re_obj_disk_name_search(line):
                                            item['disk_name']=match.group(1)
                                            continue

                                    if not item['disk_type']:
                                        if match := re_obj_disk_type_search(line):
                                            item['disk_type']=match.group(1)
                                            continue

                                    if not item['disk_num']:
                                        if match := re_obj_disk_num_search(line):
                                            item['disk_num']=match.group(1)
                                            continue

                                    if not item['disk_loc']:
                                        if match := re_obj_disk_location_search(line):
                                            item['disk_loc']=match.group(1)
                                            continue

                                    if not item['path']:
                                        if match := re_obj_path_search(line):
                                            item['path']=match.group(1)
                                            continue

                                    if not item['time']:
                                        if match := re_obj_time_search(line):
                                            item['time']=match.group(1)
                                            continue

                                    if not item['crc']:
                                        if match := re_obj_crc_search(line):
                                            item['crc']=match.group(1)
                                            continue

                                    if not item['category']:
                                        if match := re_obj_category_search(line):
                                            item['category']=match.group(1)
                                            continue

                                    if not item['flag']:
                                        if match := re_obj_flag_search(line):
                                            item['flag']=match.group(1)
                                            continue

                                    if re_obj_item_end_search(line):
                                        in_item=False
                                        in_description=False

                                        if item['type']=="Disk":
                                            print(f'disk found :{item} -> incompatible kind of report:{import_filename}')
                                            return [None,f'incompatible kind of report:{import_filename}']

                                        elif item['type']=="File" or item['type']=="Folder":
                                            if item['disk_name']!=demo_str and item['path']!=demo_str and item['name'] and item['name']!=demo_str and item['ext']!=demo_str and item['size']!=demo_str:
                                                disk_name = item['disk_name']
                                                path = item['path'].strip('\\').split('\\')

                                                fileame = item['name']
                                                if item['ext']:
                                                    fileame+='.' + item['ext']

                                                size = item['size']
                                                is_dir = bool(item['type']=="Folder")
                                                is_file = bool(item['type']=="File")
                                                is_symlink=False
                                                is_bind=False
                                                has_files=False

                                                if item['date'] and item['date']!=demo_str:
                                                    time_str=item['date']
                                                    if item['time']!=demo_str:
                                                        time_str += ' ' +  item['time']
                                                    try:
                                                        mtime=int(mktime(parse_datetime(time_str).timetuple()))
                                                    except Exception as te:
                                                        print(f'time conv {time_str} error: {te}')
                                                        mtime=0
                                                else:
                                                    mtime=0

                                                #scan_like_data

                                                if description:=item['description']:
                                                    description = description.lstrip('<![CDATA[').rstrip(']]>')
                                                    cd_set_add(description)
                                                    cd_set_per_disk[disk_name].add(description)
                                                    sld_tuple = tuple([size,is_dir,is_file,is_symlink,is_bind,has_files,mtime,description])
                                                else:
                                                    sld_tuple = tuple([size,is_dir,is_file,is_symlink,is_bind,has_files,mtime,''])

                                                #print('description',item['description'])
                                                ############################################################

                                                path_splitted = [disk_name] + path + [fileame]
                                                path_splitted = [path_elem for path_elem in path_splitted if path_elem]

                                                next_dict = wii_paths_dict
                                                for filename in path_splitted:
                                                    filenames_set_add(filename)

                                                    if filename not in next_dict:
                                                        next_dict[filename] = {}
                                                    next_dict = next_dict[filename]

                                                wii_path_tuple_to_data[tuple(path_splitted)] = sld_tuple

                                                ############################################################
                                                path_splitted = path + [fileame]
                                                path_splitted = [path_elem for path_elem in path_splitted if path_elem]

                                                next_dict = wii_paths_dict_per_disk[disk_name]
                                                for filename in path_splitted:
                                                    filenames_set_per_disk[disk_name].add(filename)

                                                    if filename not in next_dict:
                                                        next_dict[filename] = {}
                                                    next_dict = next_dict[filename]

                                                wii_path_tuple_to_data_per_disk[disk_name][tuple(path_splitted)] = sld_tuple
                                                ############################################################
                                            else:
                                                pass
                                                #print(f'another item:{item}')

                                elif match := re_obj_item_search(line):
                                    in_item=True
                                    in_description=False

                                    item = { 'ext':None,'date':None,'time':None,'path':None,'name':None,'disk_name':None,'disk_type':None,'disk_loc':None,'disk_num':None,'category':None,'crc':None,'flag':None,'size':0,'description':[],'type':match.group(1)}

                                elif re_obj_report_end_search(line):
                                    in_report=False
                                    in_item=False
                                    in_description=False
                                else:
                                    print('parse problem 1')
                            elif re_obj_header_search(line) or re_obj_comment_search(line):
                                #print(f'recognize and ignored:{line}')
                                pass
                            else:
                                if match := re_obj_report_search(line):
                                    #print(f'report :"{match.group(1)}"')
                                    in_report=True
                                    in_item=False
                                    in_description=False
                                else:
                                    print('IGNORING:',line)

                        except Exception as le:
                            print(f'line exception: "{line}" exception: {le}')

                    #<ITEM ItemType="Folder">
                    #    <NAME>$Recycle.Bin</NAME>
                    #    <SIZE>1918697428</SIZE>
                    #    <DATE>2023-04-27</DATE>
                    #    <DISK_NAME>c</DISK_NAME>
                    #    <DISK_TYPE>Hard disk</DISK_TYPE>
                    #    <PATH>\</PATH>
                    #    <DESCRIPTION><![CDATA[*** DEMO ***]]></DESCRIPTION>
                    #    <DISK_NUM>1</DISK_NUM>
                    #    <TIME>12:55:08</TIME>
                    #    <CRC>0</CRC>
                    #</ITEM>

            return filenames_set,filenames_set_per_disk,wii_path_tuple_to_data,wii_path_tuple_to_data_per_disk,wii_paths_dict,wii_paths_dict_per_disk,cd_set,cd_set_per_disk
        except Exception as ie:
            return [None,str(ie)]

    def wii_data_to_scan_like_data(self,path_list,curr_dict_ref,scan_like_data,customdata_helper):
        path_list_tuple = tuple(path_list)

        anything = False
        try:
            for name,val in curr_dict_ref.items():

                anything = True

                dict_entry={}

                sub_path_list = path_list + [name]
                sub_path_list_tuple = tuple(sub_path_list)

                try:
                    size,is_dir,is_file,is_symlink,is_bind,has_files,mtime,cd = self.wii_path_tuple_to_data[sub_path_list_tuple]
                    if cd:
                        cd_field=(0,0,cd)

                        try:
                            cd_index=customdata_helper[cd_field]
                        except Exception as cd_e:
                            print(f'{cd_e=}')

                except Exception as e1:
                    #print(f'{e1=}')
                    #tylko topowy albo niekompletny ?
                    cd=None
                    cd_index=0
                    size=0
                    is_dir = True
                    is_file = False
                    is_symlink = False
                    is_bind = False
                    mtime = 0

                if is_dir:
                    self.wii_data_to_scan_like_data(sub_path_list,val,dict_entry,customdata_helper)

                if dict_entry:
                    has_files = True
                else:
                    has_files = False

                if is_dir and not has_files and size>0:
                    is_dir=False
                    is_file=True

                temp_list_ref = scan_like_data[name] = [size,is_dir,is_file,is_symlink,is_bind,has_files,mtime]

                if dict_entry:
                    temp_list_ref.append(dict_entry)

                if cd:
                    new_elem={}
                    new_elem['cd_index']=cd_index
                    new_elem['cd_ok']=True

                    temp_list_ref.append(new_elem)

        except Exception as e:
            print('wii_data_to_scan_like_data error:',e)

        return anything

    def import_records_wii_scan(self,import_filenames):
        self.log.info(f'import_records_wii:{",".join(import_filenames)}')

        gc_disable()
        res = self.get_wii_files_dict(import_filenames)
        gc_collect()
        gc_enable()

        if len(res)==8:
            filenames_set,filenames_set_per_disk,wii_path_tuple_to_data,wii_path_tuple_to_data_per_disk,wii_paths_dict,wii_paths_dict_per_disk,cd_set,cd_set_per_disk = res

            quant_disks = len(wii_path_tuple_to_data_per_disk)

            quant_files,quant_folders = 0,0
            for k,v in wii_path_tuple_to_data.items():
                size,is_dir,is_file,is_symlink,is_bind,has_files,mtime,cd = v
                if is_dir:
                    quant_folders+=1
                elif is_file:
                    quant_files+=1

            return quant_disks,quant_files,quant_folders,filenames_set,filenames_set_per_disk,wii_path_tuple_to_data,wii_path_tuple_to_data_per_disk,wii_paths_dict,wii_paths_dict_per_disk,cd_set,cd_set_per_disk
        else:
            return res

    def import_records_wii_do(self,compr,postfix,label,quant_files,quant_folders,filenames_set,wii_path_tuple_to_data,wii_paths_dict,cd_set,update_callback):
        import_res=[]

        self.wii_path_tuple_to_data = wii_path_tuple_to_data
        self.wii_paths_dict=wii_paths_dict

        new_record = self.create()

        expressions='WII_import'
        use_smin=False
        smin_int=0
        use_smax=False
        smax_int=0
        executable='WII_import'
        parameters=''
        shell=False
        timeout=0
        crc=False

        new_record.header.cde_list = [ [expressions,use_smin,smin_int,use_smax,smax_int,executable,parameters,shell,timeout,crc] ]

        new_record.header.scan_path = 'WII_import'

        new_record.customdata = [(0,0,cd_elem) for cd_elem in cd_set]

        customdata_helper={cd_elem_tuple:index for index,cd_elem_tuple in enumerate(new_record.customdata)}

        scan_like_data={}
        self.wii_data_to_scan_like_data([],self.wii_paths_dict,scan_like_data,customdata_helper)

        del customdata_helper

        new_record.filenames = tuple(sorted(list(filenames_set)))
        new_record.header.label = label
        new_record.header.scan_path = 'WII import'
        new_record.filenames_helper = {fsname:fsname_index for fsname_index,fsname in enumerate(new_record.filenames)}

        new_record.header.quant_files = quant_files
        new_record.header.quant_folders = quant_folders

        ##################################
        #size,mtime = 0,0
        mtime = 0
        is_dir = True
        is_file = False
        is_symlink = False
        is_bind = False
        has_cd = bool(new_record.customdata)
        has_files = True
        cd_ok = False
        has_crc = False


        new_record.header.references_names=0
        new_record.header.references_cd=0

        sub_size,sub_quant,sub_folders_quant = new_record.sld_recalc_rec(scan_like_data)
        #print('ccc',sub_size,sub_quant,sub_folders_quant,flush=True)

        code = LUT_encode[ (is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc,False,False) ]

        new_record.header.sum_size = sub_size
        new_record.header.quant_files = sub_quant
        new_record.header.quant_folders = sub_folders_quant

        new_record.header.items_names=len(new_record.filenames)

        new_record.filestructure = ('',code,sub_size,mtime,new_record.tupelize_rec(scan_like_data,print))

        new_file_path = sep.join([self.db_dir,f'wii.{int(time())}.{postfix}.dat'])
        #print(f'{new_file_path=}')

        new_record.save(print,file_path=new_file_path,compression_level=compr)

        update_callback(new_record)

        if import_res:
            return '\n'.join(import_res)
        else:
            return None

    def import_records(self,import_filenames,update_callback):
        self.log.info(f"import {','.join(import_filenames)}")

        import_res=[]
        import_index=0
        for import_file in import_filenames:
            try:
                new_file_path = sep.join([self.db_dir,f'imp.{int(time())}.{import_index}.dat'])
                with ZipFile(import_file, "r") as src_zip_file:

                    decompressor = ZstdDecompressor()

                    header_ser_compr = src_zip_file.read('header')
                    header_ser = decompressor.decompress(header_ser_compr)
                    header = loads( header_ser )

                    with ZipFile(new_file_path, "w") as zip_file:
                        compressor = ZstdCompressor(level=header.compression_level,threads=-1)
                        compressor_compress = compressor.compress

                        temp_new_header = deepcopy(header)
                        temp_new_header.history_stack.append( (IMPORT_CODE,int(time()),import_file) )
                        header_ser = dumps(temp_new_header)
                        header_ser_compr = compressor_compress(header_ser)
                        zip_file.writestr('header',header_ser_compr)

                        zip_file.writestr('filestructure',src_zip_file.read('filestructure'))
                        zip_file.writestr('filenames',src_zip_file.read('filenames'))

                        if header.items_cd:
                            zip_file.writestr('customdata',src_zip_file.read('customdata'))

                    new_record = self.create()
                    if res:=new_record.load(new_file_path) :
                        #self.log.warning('removing:%s',file_name)
                        self.records.remove(new_record)
                        #load_errors.append(res)
                        send2trash_delete(new_file_path)
                        import_res.append(str(res))
                    else:
                        #self.records_to_show.append( (new_record,info_curr_quant,info_curr_size) )
                        update_callback(new_record)

            except Exception as ex_in:
                message = f"import of '{import_file}' error : {ex_in}"
                self.log.error(message)
                import_res.append(message)

                try:
                    self.log.info('removing:new_file_path')
                    send2trash_delete(new_file_path)
                except Exception as ex_de:
                    print(ex_de)

            import_index+=1

        if import_res:
            return '\n'.join(import_res)
        else:
            return None

    def export_record(self,record,new_file_path):
        self.log.info(f'export {record.header.label} -> {new_file_path}')

        try:
            with ZipFile(record.file_path, "r") as src_zip_file:
                with ZipFile(new_file_path, "w") as zip_file:

                    temp_new_header = deepcopy(record.header)
                    temp_new_header.history_stack.append( (EXPORT_CODE,int(time()),new_file_path) )
                    header_ser = dumps(temp_new_header)
                    header_ser_compr = ZstdCompressor(level=record.header.compression_level,threads=-1).compress(header_ser)
                    zip_file.writestr('header',header_ser_compr)

                    zip_file.writestr('filestructure',src_zip_file.read('filestructure'))
                    zip_file.writestr('filenames',src_zip_file.read('filenames'))

                    if record.header.items_cd:
                        zip_file.writestr('customdata',src_zip_file.read('customdata'))
        except Exception as ex_ex:
            self.log.error(f'export error {ex_ex}')
            return str(ex_ex)
        else:
            return None

    def repack_record(self,record,new_label,new_compression,keep_cd,update_callback):
        self.log.info(f'repack_record {record.header.label}->{new_label},{new_compression},{keep_cd}')

        messages = []

        new_file_path = sep.join([self.db_dir,f'rep.{int(time())}.dat'])

        try:
            src_file = record.file_path

            with ZipFile(src_file, "r") as src_zip_file:

                dec_dec = ZstdDecompressor().decompress

                header_ser_compr = src_zip_file.read('header')
                header_ser = dec_dec(header_ser_compr)
                header = loads( header_ser )

                with ZipFile(new_file_path, "w") as zip_file:
                    new_header = deepcopy(header)
                    new_header.label = new_label
                    new_header.compression_level = new_compression
                    new_header.history_stack.append( (REPACK_CODE,int(time()),record.header.label,record.header.compression_level,keep_cd) )

                    compression_change = bool(new_compression!=record.header.compression_level)

                    if compression_change:
                        data_filenames = loads(dec_dec(src_zip_file.read('filenames')))

                        self.info_line = f'compressing filenames'
                        compress_with_header_update(new_header,data_filenames,new_compression,'filenames',zip_file)
                    else:
                        zip_file.writestr('filenames',src_zip_file.read('filenames'))

                    if keep_cd!=bool(record.header.items_cd):
                        data_filestructure = record.remove_cd_rec(loads(dec_dec(src_zip_file.read('filestructure'))))

                        self.info_line = f'compressing filestructure'
                        compress_with_header_update(new_header,data_filestructure,new_compression,'filestructure',zip_file)

                        new_header.zipinfo["customdata"]=(0,0,0)
                        new_header.files_cde_size_extracted = 0
                        new_header.items_cd=0
                        new_header.references_cd = 0
                        new_header.cde_list = []
                        new_header.files_cde_errors_quant = {}
                        new_header.files_cde_errors_quant_all = 0
                        new_header.cde_stats_time_all = 0
                        new_header.compression_time['customdata']=0

                    elif not compression_change:
                        zip_file.writestr('filestructure',src_zip_file.read('filestructure'))

                        if header.items_cd:
                            zip_file.writestr('customdata',src_zip_file.read('customdata'))
                    else:
                        data_filestructure = loads(dec_dec(src_zip_file.read('filestructure')))

                        self.info_line = f'compressing filestructure'
                        compress_with_header_update(new_header,data_filestructure,new_compression,'filestructure',zip_file)

                        if header.items_cd:
                            data_customdata = loads(dec_dec(src_zip_file.read('customdata')))

                            self.info_line = f'compressing customdata'
                            compress_with_header_update(new_header,data_customdata,new_compression,'customdata',zip_file)

                    header_ser = dumps(new_header)
                    header_ser_compr = ZstdCompressor(level=new_compression,threads=-1).compress(header_ser)
                    zip_file.writestr('header',header_ser_compr)

                new_record = self.create()

                if res:=new_record.load(new_file_path) :
                    self.records.remove(new_record)
                    send2trash_delete(new_file_path)
                    messages.append(str(res))
                else:
                    update_callback(new_record)

        except Exception as ex_in:
            message = f"repack of '{src_file}' error : {ex_in}"
            self.log.error(message)
            messages.append(message)

            try:
                self.log.info('removing:new_file_path')
                send2trash_delete(new_file_path)
            except Exception as ex_de:
                print(ex_de)

        return messages

    def abort(self):
        #print('core abort')
        self.abort_action = True

    def abort_single(self):
        #print('core abort single')
        self.abort_action_single = True

    def threaded_read_records(self,load_errors):
        self.log.info('read_records: %s',self.db_dir)
        self.records_to_show=[]

        info_curr_quant = 0
        info_curr_size = 0

        for file_name,size in sorted(self.record_files_list):
            if self.abort_action:
                break

            self.log.info('db:%s',file_name)
            self.info_line = f'loading {file_name}'

            info_curr_quant+=1
            info_curr_size+=size
            new_record = self.create()

            if res:=new_record.load(sep.join([self.db_dir,file_name])) :
                self.log.warning('removing:%s',file_name)
                self.records.remove(new_record)
                load_errors.append(res)
            else:
                self.records_to_show.append( (new_record,info_curr_quant,info_curr_size) )
        self.update_sorted()

    def find_results_clean(self):
        for record in self.records:
            record.find_results_clean()

    stage = 0

    stdout_sum_size = 0
    stdout_quant_files = 0
    stdout_quant_folders = 0
    stdout_info_line_current = ''
    stdout_cde_size = 0

    stdout_files_cde_size_extracted=0
    stdout_files_cde_errors_quant_all=0
    stdout_files_cde_quant=0
    stdout_files_cde_quant_sum=0
    stdout_files_cde_size=0
    stdout_files_cde_size_sum=0

    ########################################################################################################################

    def create_new_record(self,temp_dir,update_callback):
        self.log.info(f'create_new_record')
        self_log_info = self.log.info

        new_file_path = sep.join([self.db_dir,f'rep.{int(time())}.dat'])

        command = self.record_exe()
        command.append('create')
        command.append(new_file_path)
        command.append(temp_dir)

        self.abort_action=False
        self.abort_action_single=False

        self.stdout_sum_size = 0
        self.stdout_quant_files = 0
        self.stdout_quant_folders = 0
        self.stdout_info_line_current = ''
        self.stdout_cde_size = 0

        self.stage = 0

        self.stdout_files_cde_size_extracted=0
        self.stdout_files_cde_errors_quant_all=0
        self.stdout_files_cde_quant=0
        self.stdout_files_cde_quant_sum=0
        self.stdout_files_cde_size=0
        self.stdout_files_cde_size_sum=0

        def threaded_run(command,results_semi_list,info_semi_list,processes_semi_list):
            try:
                subprocess = uni_popen(command,stdin=PIPE)
            except Exception as re:
                print('threaded_run run error',re)
                info_semi_list[0].append(f'threaded_run run error: {re}')
                sys.exit() #thread

            processes_semi_list[0]=subprocess
            subprocess_stdout_readline = subprocess.stdout.readline
            subprocess_poll = subprocess.poll

            while True:
                if line := subprocess_stdout_readline():
                    line_strip = line.strip()
                    self_log_info(f'rec:{line_strip}')
                    try:
                        if line[0]!='#':
                            val = json_loads(line_strip)

                            kind = val[0]
                            if kind == 'stage':
                                self.stage = val[1]
                            elif kind == 'error':
                                self.stdout_info_line_current = val[1]
                            elif kind == 'info':
                                self.stdout_info_line_current = val[1]
                            elif kind == 'scan-line':
                                self.stdout_info_line_current = val[1]
                            else:
                                if self.stage==0: #scan
                                    self.stdout_sum_size,self.stdout_quant_files,self.stdout_quant_folders,self.stdout_info_line_current = val[1:5]

                                elif self.stage==1: #cde
                                    if val[0]=='cdeinit':
                                        #files_cde_quant_sum,files_cde_size_sum
                                        self.stdout_files_cde_quant_sum = val[1]
                                        self.stdout_files_cde_size_sum = val[2]
                                    elif val[0]=='cde':
                                        self.stdout_info_line_current = val[1]
                                        self.stdout_cde_size = val[2]

                                        self.stdout_files_cde_size_extracted=val[3]
                                        self.stdout_files_cde_errors_quant_all=val[4]
                                        self.stdout_files_cde_quant=val[5]
                                        self.stdout_files_cde_size=val[6]
                                    else:
                                        self_log_info('ERROR UNRECOGNIZED LINE')

                                elif self.stage==2: #pack
                                    self.stdout_info_line_current = val[1]

                                elif self.stage==3: #save
                                    self.stdout_info_line_current = val[1]

                                elif self.stage==4: #end
                                    pass
                        else:
                            info_semi_list[0]=line_strip
                    except Exception as e:
                        info_semi_list[0]=f'threaded_run work error:{e} line:{line}'
                        self_log_info(f'threaded_run work error:{e} line:{line}')
                else:
                    if subprocess_poll() is not None:
                        break
                    sleep(0.001)
            sys.exit() #thread

        results_semi_list=[None]
        info_semi_list=[None]
        processes_semi_list=[None]
        job = Thread(target=lambda : threaded_run(command,results_semi_list,info_semi_list,processes_semi_list),daemon=True)
        job.start()
        job_is_alive = job.is_alive

        ###########################################
        while job_is_alive():
            subprocess=processes_semi_list[0]
            if subprocess:
                if self.abort_action:
                    send_signal(subprocess,temp_dir,0)
                    self.abort_action=False
                if self.abort_action_single:
                    send_signal(subprocess,temp_dir,1)
                    self.abort_action_single=False
            sleep(0.1)

        job.join()
        ###########################################

        #nie wiadomo czy przerwano na skanie czy cde
        new_record = self.create()

        if res:=new_record.load(new_file_path) :
            self.log.warning('removing:%s',new_file_path)
            self.records.remove(new_record)
            self_log_info(res)
        else:
            update_callback(new_record)

        return True

    def record_exe(self):
        is_frozen = bool(getattr(sys, 'frozen', False))
        if windows:
            if is_frozen:
               return(['record.exe'])
            else:
                return(['python','src\\record.py'])
        else:
            if is_frozen:
                return(['./record'])
            else:
                return(['python3','./src/record.py'])

    def find_items_in_records(self,
            temp_dir,
            range_par,
            size_min,size_max,
            t_min,t_max,
            find_filename_search_kind,name_expr,name_case_sens,
            find_cd_search_kind,cd_expr,cd_case_sens,
            filename_fuzzy_threshold,cd_fuzzy_threshold):

        self.log.info(f'find_items_in_records:{size_min},{size_max},{find_filename_search_kind},{name_expr},{name_case_sens},{find_cd_search_kind},{cd_expr},{cd_case_sens},{filename_fuzzy_threshold},{cd_fuzzy_threshold}')

        self.find_results_clean()

        records_to_process = [range_par] if range_par else list(self.records)

        records_to_process.sort(reverse = True,key = lambda x : x.header.quant_files)

        params = (size_min,size_max,
            t_min,t_max,
            find_filename_search_kind,name_expr,name_case_sens,
            find_cd_search_kind,cd_expr,cd_case_sens,
            filename_fuzzy_threshold,cd_fuzzy_threshold)

        searchinfofile = sep.join([temp_dir,SEARCH_DAT_FILE])
        try:
            with open(searchinfofile, "wb") as f:
                f.write(ZstdCompressor(level=8,threads=1).compress(dumps(params)))
        except Exception as e:
            print(e)

        record_command_list={}

        for record_nr,record in enumerate(records_to_process):
            curr_command_list = record_command_list[record_nr] = self.record_exe()
            curr_command_list.extend(['search',record.file_path,temp_dir])
            self.log.info(f'curr_command_list: {curr_command_list}')

        self.find_res_quant = 0

        self.total_search_progress = 0

        self.search_record_nr=0

        self.abort_action = False
        for record in records_to_process:
            record.abort_action = False

        ############################################################

        max_processes = cpu_count()

        records_to_process_len = len(records_to_process)

        #####################################################
        def threaded_run(record_nr,commands_list,results_list,progress_list,info_list,processes_list):
            results_list_append = results_list[record_nr].find_results.append

            try:
                subprocess = uni_popen(commands_list[record_nr])
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
                        print(f'threaded_run work error:{e} line:{line}')
                        info_list[record_nr].append(f'threaded_run work error:{e} line:{line}')
                else:
                    if subprocess_poll() is not None:
                        break
                    sleep(0.001)
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

            self.records_perc_info = (self.search_record_nr+0.5) * 100.0 / records_to_process_len

            self.info_line = f'Threads: waiting:{waiting}, running:{running}, finished:{finished}'

            if waiting:
                if running<max_processes:
                    record_nr = waiting_list[0]
                    job = jobs[record_nr]
                    job[1] = Thread(target=lambda : threaded_run(record_nr,record_command_list,records_to_process,total_progress,info_list,processes_list),daemon=True)
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
        for record in records_to_process:
            record.find_results_tuples_set = {result[0] for result in record.find_results}

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
        file_path = record.file_path
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
        return file_path
