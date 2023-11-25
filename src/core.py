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

from zstandard import ZstdCompressor
from zstandard import ZstdDecompressor

from zipfile import ZipFile

from os import scandir
from os import stat
from os import sep

from os.path import join as path_join
from os.path import abspath
from os.path import normpath
from os.path import basename

from platform import system as platform_system
from platform import release as platform_release
from platform import node as platform_node

from os import remove as os_remove

from fnmatch import fnmatch
from fnmatch import translate
from re import search
from sys import getsizeof

from shutil import copy as shutil_copy

from hashlib import sha1

from collections import defaultdict

from re import compile as re_compile
from re import IGNORECASE

from signal import SIGTERM

from time import time
from time import strftime
from time import localtime

from pickle import dumps
from pickle import loads

from difflib import SequenceMatcher

from executor import Executor

from pathlib import Path as pathlib_Path

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

def str_to_bytes(string):
    units = {'kb': 1024,'mb': 1024*1024,'gb': 1024*1024*1024,'tb': 1024*1024*1024*1024, 'b':1}
    try:
        string = string.replace(' ','')
        for suffix in units:
            if string.lower().endswith(suffix):
                return int(string[0:-len(suffix)]) * units[suffix]

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
        if (byte & (1 << i)):
            bool_list[num_bools-1-i]=True

    return tuple(bool_list)

def test_regexp(expr):
    teststring='abc'
    try:
        search(expr,teststring)
    except Exception as e:
        return e
    else:
        return None

entry_LUT_encode={}
entry_LUT_decode={}

for i in range(256):
    temp_tuple = entry_LUT_decode[i]=byte_to_bools(i)
    entry_LUT_encode[temp_tuple]=i
    #print(i, temp_tuple)

#######################################################################
data_format_version='1.0009'

class LibrerRecordHeader :
    def __init__(self,label='',path=''):
        self.label=label
        self.scan_path = path
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
        self.files_cde_errors_quant = 0

        self.creation_os,self.creation_host = f'{platform_system()} {platform_release()}',platform_node()

#######################################################################
class LibrerRecord:
    def __init__(self,label,path,log):
        self.header = LibrerRecordHeader(label,path)

        #self.filenames = ()
        self.filestructure = ()
        self.custom_data = []

        self.log = log
        self.find_results = []

        self.info_line = ''
        self.info_line_current = ''

        self.abort_action = False
        self.files_search_progress = 0

        self.crc_progress_info=0

        self.FILE_NAME = ''
        self.FILE_SIZE = 0
        self.file_path = ''

        self.zipinfo={'header':'?','filestructure':'?','filenames':'?','customdata':'?'}

    def new_file_name(self):
        return f'{self.header.rid}.dat'

    def abort(self):
        self.abort_action = True

    def calc_crc(self,fullpath,size):
        CRC_BUFFER_SIZE=4*1024*1024
        buf = bytearray(CRC_BUFFER_SIZE)
        view = memoryview(buf)

        self.crc_progress_info=0

        try:
            file_handle=open(fullpath,'rb')
            file_handle_readinto=file_handle.readinto
        except Exception as e:
            self.log.error(e)
            return None
        else:
            hasher = sha1()
            hasher_update=hasher.update

            #faster for smaller files
            if size<CRC_BUFFER_SIZE:
                hasher_update(view[:file_handle_readinto(buf)])
            else:
                while rsize := file_handle_readinto(buf):
                    hasher_update(view[:rsize])

                    if rsize==CRC_BUFFER_SIZE:
                        #still reading
                        self.crc_progress_info+=rsize

                    if self.abort_action:
                        break

                self.crc_progress_info=0

            file_handle.close()

            if self.abort_action:
                return None

            #only complete result
            #return hasher.hexdigest()
            return hasher.digest()

    def scan_rec(self, path, scan_like_data,file_names_set,check_dev=True,dev_call=None) :
        if self.abort_action:
            return True

        path_join_loc = path_join

        local_folder_size_with_subtree=0
        local_folder_size = 0

        self_scan_rec = self.scan_rec

        file_names_set_add = file_names_set.add
        try:
            with scandir(path) as res:
                local_folder_files_count = 0
                local_folder_folders_count = 0

                for entry in res:
                    if self.abort_action:
                        break

                    entry_name = entry.name
                    file_names_set_add(entry_name)

                    is_dir,is_file,is_symlink = entry.is_dir(),entry.is_file(),entry.is_symlink()

                    self.ext_statistics[pathlib_Path(entry).suffix]+=1

                    self.info_line_current = entry_name
                    try:
                        stat_res = stat(entry)

                        #mtime_ns = stat_res.st_mtime_ns
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
                                size = self_scan_rec(path_join_loc(path,entry_name),dict_entry,file_names_set,check_dev,dev)
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
        return self.FILE_NAMES[nr]

    def scan(self,cde_list,check_dev=True):
        self.info_line = 'Scanning filesystem'
        self.abort_action=False

        self.header.sum_size = 0

        self.ext_statistics=defaultdict(int)
        self.scan_data={}

        #########################
        file_names_set=set()
        self.scan_rec(self.header.scan_path,self.scan_data,file_names_set)

        self.FILE_NAMES = tuple(sorted(list(file_names_set)))
        #########################
        self.info_line = 'indexing filesystem names'

        self.FILE_NAMES_helper = {fsname:fsname_index for fsname_index,fsname in enumerate(self.FILE_NAMES)}

        self.cde_list = cde_list
        self.cd_stat=[0]*len(cde_list)

        self.custom_data_pool = {}
        self.custom_data_pool_index = 0

        #if cde_list:
        self.info_line = f'estimating files pool for custom data extraction'
        self.prepare_custom_data_pool_rec(self.scan_data,[])

        self.info_line = ''

        #for ext,stat in sorted(self.ext_statistics.items(),key = lambda x : x[1],reverse=True):
        #    print(ext,stat)

    def prepare_custom_data_pool_rec(self,scan_like_data,parent_path):
        scan_path = self.header.scan_path
        self_prepare_custom_data_pool_rec = self.prepare_custom_data_pool_rec

        self_cde_list = self.cde_list
        self_custom_data_pool = self.custom_data_pool

        for entry_name,items_list in scan_like_data.items():
            if self.abort_action:
                break
            try:
                #is_dir,is_file,is_symlink,is_bind,has_files,size,mtime = items_list
                size,is_dir,is_file,is_symlink,is_bind,has_files,mtime = items_list[0:7]
                subpath_list = parent_path.copy() + [entry_name]

                if not is_symlink and not is_bind:
                    if is_dir:
                        if has_files:
                            self_prepare_custom_data_pool_rec(items_list[7],subpath_list)
                    else:
                        subpath=sep.join(subpath_list)
                        ############################

                        full_file_path = normpath(abspath(sep.join([scan_path,subpath])))

                        matched = False

                        rule_nr=-1
                        for expressions,use_smin,smin_int,use_smax,smax_int,executable,timeout,crc in self_cde_list:
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
                                    self_custom_data_pool[self.custom_data_pool_index]=(items_list,subpath,rule_nr)
                                    self.custom_data_pool_index += 1
                                    self.cd_stat[rule_nr]+=1
                                    self.header.files_cde_size_sum += size
                                    matched = True

            except Exception as e:
                self.log.error('prepare_custom_data_pool_rec error::%s',e )
                print('prepare_custom_data_pool_rec',e,entry_name,size,is_dir,is_file,is_symlink,is_bind,has_files,mtime)

    def extract_custom_data(self):
        self_header = self.header
        scan_path = self_header.scan_path

        self.info_line = f'custom data extraction ...'

        self_header.files_cde_quant = 0
        self_header.files_cde_size = 0
        self_header.files_cde_size_extracted = 0
        self_header.files_cde_errors_quant = 0
        self_header.files_cde_quant_sum = len(self.custom_data_pool)

        self_cde_list = self.cde_list

        exe = Executor()

        custom_data_helper={}

        cd_index=0
        self_custom_data_append = self.custom_data.append
        self_calc_crc = self.calc_crc
        exe_run = exe.run

        for (scan_like_list,subpath,rule_nr) in self.custom_data_pool.values():
            if self.abort_action:
                break

            expressions,use_smin,smin_int,use_smax,smax_int,executable,timeout,crc = self_cde_list[rule_nr]

            full_file_path = normpath(abspath(sep.join([scan_path,subpath]))).replace('/',sep)

            size = scan_like_list[0]

            cde_run_list = executable + [full_file_path]

            if crc:
                self.info_line_current = f'{subpath} CRC calculation ({bytes_to_str(size)})'
                crc_val = self_calc_crc(full_file_path,size)

            self.info_line_current = f'{subpath} ({bytes_to_str(size)})'

            cd_ok,output = exe_run(cde_run_list,timeout)

            if not cd_ok:
                self_header.files_cde_errors_quant +=1

            new_elem={}
            new_elem['cd_ok']=cd_ok

            if output not in custom_data_helper:
                custom_data_helper[output]=cd_index
                new_elem['cd_index']=cd_index
                cd_index+=1

                self_custom_data_append(output)
            else:
                new_elem['cd_index']=custom_data_helper[output]

            if crc:
                new_elem['crc_val']=crc_val

            scan_like_list.append(new_elem)

            self_header.files_cde_quant += 1
            self_header.files_cde_size += size
            self_header.files_cde_size_extracted += getsizeof(output)

            self.info_line_current = ''

        del self.custom_data_pool
        del custom_data_helper

        exe.end()

    search_kind_code_tab={'dont':0,'without':1,'any':2,'error':3,'regexp':4,'glob':5,'fuzzy':6}

    #############################################################
    def tupelize_rec(self,scan_like_data):
        entry_LUT_encode_loc = entry_LUT_encode

        self_tupelize_rec = self.tupelize_rec

        self_custom_data = self.custom_data
        sub_list = []
        for entry_name,items_list in scan_like_data.items():

            try:
                entry_name_index = self.FILE_NAMES_helper[entry_name]
            except Exception as VE:
                print('FILE_NAMES error:',entry_name,VE)
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

                    code_new = entry_LUT_encode_loc[ (is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc) ]

                    sub_list_elem=[entry_name_index,code_new,size,mtime]

                    if has_files:
                        sub_list_elem.append(self_tupelize_rec(sub_dict))
                    else:
                        if has_cd: #only files
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

        code = entry_LUT_encode[ (is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc) ]
        self.filestructure = ('',code,size,mtime,self.tupelize_rec(self.scan_data))

        del self.FILE_NAMES_helper
        del self.scan_data

    def clone_record_rec(self,cd_org,FILE_NAMES_org,tuple_like_data,keep_cd,keep_crc):
        entry_LUT_decode_loc = entry_LUT_decode
        self_get_file_name = self.get_file_name
        self_clone_record_rec = self.clone_record_rec

        name_index,code,size,mtime = tuple_like_data[0:4]
        if name_index:
            name = FILE_NAMES_org[name_index]
        else:
            name=''

        is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc = entry_LUT_decode_loc[code]
        if not keep_cd or not keep_crc:
            has_cd = has_cd and keep_cd
            has_crc = has_crc and keep_crc
            if not has_crc:
                cd_ok=False

            code = entry_LUT_encode[ (is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc) ]

        new_list = [name_index,code,size,mtime]

        elem_index=4
        if has_files:
            sub_new_list=[]
            for sub_structure in tuple_like_data[elem_index]:
                sub_new_list.append(self_clone_record_rec(cd_org,FILE_NAMES_org,sub_structure,keep_cd,keep_crc))
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
        self.decompress_custom_data()

        new_record = LibrerRecord(self.header.label,file_path,self.log)

        new_record.header = self.header
        new_record.FILE_NAMES = self.FILE_NAMES
        if keep_cd:
            new_record.custom_data = self.custom_data

        new_record.filestructure = self.clone_record_rec(self.custom_data,self.FILE_NAMES,self.filestructure,keep_cd,keep_crc)
        new_record.save(file_path,compression_level)

    def find_items(self,
            size_min,size_max,
            filename_search_kind,name_func_to_call,cd_search_kind,cd_func_to_call):

        self.decompress_filestructure()

        dont_kind_code = self.search_kind_code_tab['dont']
        regexp_kind_code = self.search_kind_code_tab['regexp']
        glob_kind_code = self.search_kind_code_tab['glob']
        without_kind_code = self.search_kind_code_tab['without']
        any_kind_code = self.search_kind_code_tab['any']
        error_kind_code = self.search_kind_code_tab['error']
        fuzzy_kind_code = self.search_kind_code_tab['fuzzy']

        find_results = self.find_results = []
        find_results_add = find_results.append

        file_names_loc = self.FILE_NAMES
        filestructure = self.filestructure

        self.files_search_progress = 0

        filename_search_kind_code = self.search_kind_code_tab[filename_search_kind]
        cd_search_kind_code = self.search_kind_code_tab[cd_search_kind]

        if cd_search_kind_code!=dont_kind_code:
            self.decompress_custom_data()

        entry_LUT_decode_loc = entry_LUT_decode

        use_size = True if size_min or size_max else False

        search_list = [ (filestructure[4],[]) ]
        search_list_pop = search_list.pop
        search_list_append = search_list.append

        rgf_group = (regexp_kind_code,glob_kind_code,fuzzy_kind_code)

        self_custom_data = self.custom_data
        while search_list:
            if self.abort_action:
                break

            filestructure,parent_path_components = search_list_pop()

            for data_entry in filestructure:
                if self.abort_action:
                    break

                self.files_search_progress +=1

                name_nr,code,size,mtime = data_entry[0:4]

                #data_entry_len = len(data_entry)
                #if data_entry_len==5:
                #elif data_entry_len==4:
                #    name_nr,code,size,mtime = data_entry
                #else:
                #    print('format error:',data_entry_len,data_entry[0])
                #    continue

                name = file_names_loc[name_nr]

                is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc = entry_LUT_decode_loc[code]

                elem_index=4
                if has_files:
                    sub_data = data_entry[elem_index]
                    elem_index+=1
                else:
                    sub_data = None

                if has_cd:
                    cd_nr = data_entry[elem_index]
                    elem_index+=1

                if has_crc:
                    crc = data_entry[elem_index]

                cd_search_kind_code_is_rgf = True if cd_search_kind_code in rgf_group else False

                next_level = parent_path_components + [name]
                if is_dir :
                    if cd_search_kind_code==dont_kind_code and not use_size:
                        #katalog moze spelniac kryteria naazwy pliku ale nie ma rozmiaru i custom data
                        if name_func_to_call:
                            if name_func_to_call(name):
                                find_results_add( tuple([tuple(next_level),size,mtime]) )

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

                    if name_func_to_call:
                        func_res_code = name_func_to_call(name)
                        if not func_res_code:
                            continue

                    #oczywistosc
                    #if cd_search_kind_code==dont_kind_code:
                    #    pass

                    if cd_search_kind_code==any_kind_code:
                        if not has_cd or not cd_ok:
                            continue
                    elif cd_search_kind_code_is_rgf:
                        if has_cd and cd_ok:
                            cd_data = self_custom_data[cd_nr]
                        else:
                            continue

                        if cd_func_to_call:
                            try:
                                #cd_txt = cd_data
                                #self.get_cd_text(cd_data)

                                if not cd_func_to_call(cd_data):
                                    continue
                            except Exception as e:
                                self.log.error('find_items_rec:%s',str(e) )
                                continue

                        else:
                            continue
                    elif cd_search_kind_code==without_kind_code:
                        if has_cd:
                            continue
                    elif cd_search_kind_code==error_kind_code:
                        if has_cd:
                            if cd_ok:
                                continue
                        else:
                            continue

                    find_results_add( tuple([tuple(next_level),size,mtime ]) )

    def find_items_sort(self,what,reverse):
        if what=='data':
            self.find_results.sort(key = lambda x : x[0],reverse=reverse)
        elif what=='size':
            self.find_results.sort(key = lambda x : (x[0][0:-1],x[1]),reverse=reverse)
        elif what=='ctime':
            self.find_results.sort(key = lambda x : (x[0][0:-1],x[2]),reverse=reverse)
        else:
            print('unknown sorting',what,mod)

    def prepare_info(self):
        info_list = []

        try:
             self.FILE_SIZE = stat(self.file_path).st_size
        except Exception as e:
            print('prepare_info stat error:%s' % e )
        else:
            zip_file_info = {'header':0,'filestructure':0,'filenames':0,'customdata':0}
            with ZipFile(self.file_path, "r") as zip_file:
                for info in zip_file.infolist():
                    zip_file_info[info.filename] = info.compress_size

            self_header = self.header

            local_time = strftime('%Y/%m/%d %H:%M:%S',localtime(self.header.creation_time))
            info_list.append(f'name: {self_header.label}')
            info_list.append(f'scan path: {self_header.scan_path}')
            info_list.append(f'size: {bytes_to_str(self_header.sum_size)}')
            info_list.append(f'host: {self_header.creation_host}')
            info_list.append(f'OS: {self_header.creation_os}')
            info_list.append(f'creation time: {local_time}')
            info_list.append(f'file: {self.FILE_NAME}')
            info_list.append(f'')
            info_list.append(f'file size: {bytes_to_str(self.FILE_SIZE)}')
            info_list.append(f'')
            info_list.append(f'internal sizes:')
            info_list.append(f'')
            info_list.append( '                   compressed  decompressed')

            bytes_to_str_mod = lambda x : bytes_to_str(x) if type(x) == int else x

            info_list.append(f'header        :{bytes_to_str_mod(zip_file_info["header"]).rjust(14)}{bytes_to_str_mod(self.zipinfo["header"]).rjust(14)}')
            info_list.append(f'filestructure :{bytes_to_str_mod(zip_file_info["filestructure"]).rjust(14)}{bytes_to_str_mod(self.zipinfo["filestructure"]).rjust(14)}')
            info_list.append(f'file names    :{bytes_to_str_mod(zip_file_info["filenames"]).rjust(14)}{bytes_to_str_mod(self.zipinfo["filenames"]).rjust(14)}')
            info_list.append(f'custom data   :{bytes_to_str_mod(zip_file_info["customdata"]).rjust(14)}{bytes_to_str_mod(self.zipinfo["customdata"]).rjust(14)}')

        self.txtinfo = '\n'.join(info_list)

    def save(self,file_path=None,compression_level=16):
        if file_path:
            filename = basename(normpath(file_path))
        else:
            filename = self.FILE_NAME = self.new_file_name()
            self.file_path = file_path = sep.join([self.db_dir,filename])

        self.info_line = f'saving {filename}'

        self.log.info('saving %s' % file_path)

        with ZipFile(file_path, "w") as zip_file:
            cctx = ZstdCompressor(level=compression_level,threads=-1)

            header_ser = dumps(self.header)
            self.zipinfo['header'] = len(header_ser)
            zip_file.writestr('header',cctx.compress(header_ser))

            self.info_line = f'saving {filename} (File stucture)'
            filestructure_ser = dumps(self.filestructure)
            self.zipinfo['filestructure'] = len(filestructure_ser)
            zip_file.writestr('filestructure',cctx.compress(filestructure_ser))

            self.info_line = f'saving {filename} (File names)'
            filenames_ser = dumps(self.FILE_NAMES)
            self.zipinfo['filenames'] = len(filenames_ser)
            zip_file.writestr('filenames',cctx.compress(filenames_ser))

            self.info_line = f'saving {filename} (Custom Data)'
            custom_data_ser = dumps(self.custom_data)
            self.zipinfo['customdata'] = len(custom_data_ser)
            zip_file.writestr('customdata',cctx.compress(custom_data_ser))

        self.prepare_info()

        self.info_line = ''

    def load_wrap(self,db_dir,file_name):
        self.FILE_NAME = file_name
        file_path = sep.join([db_dir,self.FILE_NAME])

        return self.load(file_path)

    def load(self,file_path):
        self.file_path = file_path
        file_name = basename(normpath(file_path))
        self.log.info('loading %s' % file_name)

        dctx = ZstdDecompressor()

        try:
            with ZipFile(file_path, "r") as zip_file:
                header_ser = dctx.decompress(zip_file.read('header'))
                self.header = loads( header_ser )
                self.zipinfo['header'] = len(header_ser)

            self.prepare_info()

            global data_format_version
            if self.header.data_format_version != data_format_version:
                self.log.error(f'incompatible data format version error: {self.header.data_format_version} vs {data_format_version}')
                return True

        except Exception as e:
            print('loading error:%s' % e )
            return True
        else:
            return False

    decompressed_filestructure = False
    def decompress_filestructure(self):
        if not self.decompressed_filestructure:
            dctx = ZstdDecompressor()

            with ZipFile(self.file_path, "r") as zip_file:
                filestructure_ser = dctx.decompress(zip_file.read('filestructure'))
                self.filestructure = loads( filestructure_ser )
                self.zipinfo['filestructure'] = len(filestructure_ser)

                filenames_ser = dctx.decompress(zip_file.read('filenames'))
                self.FILE_NAMES = loads(filenames_ser)
                self.zipinfo['filenames'] = len(filenames_ser)

            self.decompressed_filestructure = True

            self.prepare_info()

            return True
        else:
            return False

    decompressed_custom_data = False
    def decompress_custom_data(self):
        if not self.decompressed_custom_data:
            dctx = ZstdDecompressor()
            with ZipFile(self.file_path, "r") as zip_file:

                customdata_ser_comp = zip_file.read('customdata')
                customdata_ser = dctx.decompress(customdata_ser_comp)
                self.custom_data = loads( customdata_ser )
                self.zipinfo['customdata'] = len(customdata_ser)

            self.decompressed_custom_data = True

            self.prepare_info()
            return True
        else:
            return False

#######################################################################
class LibrerCore:
    records = set()
    db_dir=''

    def test_cde(self,executable,timeout,file_to_test):
        exe = Executor()
        cde_run_list = executable + [file_to_test]

        cd_ok,output = exe.run(cde_run_list,timeout)
        exe.end()

        return cd_ok,output

    def __init__(self,db_dir,log):
        self.records = set()
        self.db_dir = db_dir
        self.log=log
        self.info_line = 'init'
        #self.info_line_current = ''

        self.records_to_show=[]
        self.abort_action=False
        self.search_record_nr=0
        self.search_record_ref=None

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
                    ename = entry.name
                    if ename.endswith('.dat'):
                        try:
                            stat_res = stat(entry)
                            size = int(stat_res.st_size)
                        except Exception as e:
                            print('record stat error:%s' % e )
                            continue

                        size_sum+=size
                        self.record_files_list.append( (ename,size) )
                quant_sum=len(self.record_files_list)
            return (quant_sum,size_sum)
        except Exception as e:
            self.log.error('list read error:%s' % e )
            return (0,0)

    def abort(self):
        self.abort_action = True

    def import_record(self,file_path):
        new_record = self.create()
        if new_record.load(file_path): #tylko dla testu
            self.log.warning('import failed :%s',file_path)
            self.records.remove(new_record)
            return None
        else:
            new_file_tail = 'imported' + str(new_record.header.rid) + '.' + str(time()) + '.dat'
            file_path_loc = sep.join([self.db_dir,new_file_tail])
            try:
                shutil_copy(file_path,file_path_loc)
            except Exception as e:
                print(e)
                return None
            else:
                new_record = self.create()
                if new_record.load_wrap(self.db_dir,new_file_tail):
                    return None
                else:
                    return new_record

            #self.records_to_show.append( (new_record,info_curr_quant,info_curr_size) )

    def read_records(self):
        self.log.info('read_records: %s',self.db_dir)
        self.records_to_show=[]

        info_curr_quant = 0
        info_curr_size = 0

        for ename,size in sorted(self.record_files_list):
            if self.abort_action:
                break

            self.log.info('db:%s',ename)
            new_record = self.create()

            self.info_line = f'loading {ename}'

            info_curr_quant+=1
            info_curr_size+=size

            if new_record.load_wrap(self.db_dir,ename) :
                self.log.warning('removing:%s',ename)
                self.records.remove(new_record)
            else:
                self.records_to_show.append( (new_record,info_curr_quant,info_curr_size) )
        self.update_sorted()

    def find_items_in_all_records_check(self,
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

    def find_items_in_all_records(self,
            range_par,
            size_min,size_max,
            find_filename_search_kind,name_expr,name_case_sens,
            find_cd_search_kind,cd_expr,cd_case_sens,
            filename_fuzzy_threshold,cd_fuzzy_threshold):

        if name_expr:
            filename_fuzzy_threshold_float=float(filename_fuzzy_threshold) if find_filename_search_kind == 'fuzzy' else 0

            if find_filename_search_kind == 'regexp':
                name_func_to_call = lambda x : search(name_expr,x)
            elif find_filename_search_kind == 'glob':
                if name_case_sens:
                    #name_func_to_call = lambda x : fnmatch(x,name_expr)
                    name_func_to_call = lambda x : re_compile(translate(name_expr)).match(x)
                else:
                    name_func_to_call = lambda x : re_compile(translate(name_expr), IGNORECASE).match(x)
            elif find_filename_search_kind == 'fuzzy':
                name_func_to_call = lambda x : True if SequenceMatcher(None, name_expr, x).ratio()>filename_fuzzy_threshold_float else False
            else:
                name_func_to_call = None
        else:
            name_func_to_call = None

        if cd_expr:
            cd_fuzzy_threshold_float = float(cd_fuzzy_threshold) if find_cd_search_kind == 'fuzzy' else 0

            if find_cd_search_kind == 'regexp':
                cd_func_to_call = lambda x : search(cd_expr,x)
            elif find_cd_search_kind == 'glob':
                if cd_case_sens:
                    #cd_func_to_call = lambda x : fnmatch(x,cd_expr)
                    cd_func_to_call = lambda x : re_compile(translate(cd_expr)).match(x)
                else:
                    cd_func_to_call = lambda x : re_compile(translate(cd_expr), IGNORECASE).match(x)
            elif find_cd_search_kind == 'fuzzy':
                cd_func_to_call = lambda x : True if SequenceMatcher(None, name_expr, x).ratio()>cd_fuzzy_threshold_float else False
            else:
                cd_func_to_call = None
        else:
            cd_func_to_call = None

        self.find_res_quant = 0
        sel_range = [range_par] if range_par else self.records

        self.files_search_progress = 0

        self.search_record_nr=0
        self.search_record_ref=None

        records_len = len(self.records)

        ############################################################
        self.abort_action = False
        ############################################################
        for record in sel_range:
            self.search_record_ref = record

            self.search_record_nr+=1
            self.records_perc_info = self.search_record_nr * 100.0 / records_len

            self.info_line = f'searching in record: {record.header.label}'

            if self.abort_action:
                break

            try:
                record.abort_action = False
                record.find_items(
                    size_min,size_max,
                    find_filename_search_kind,name_func_to_call,
                    find_cd_search_kind,cd_func_to_call)
            except Exception as e:
                print(e)

            self.files_search_progress += record.header.quant_files
            self.find_res_quant = len(record.find_results)
        ############################################################


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

