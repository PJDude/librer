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

from os import scandir
from os import stat
from os import sep

from os.path import join as path_join
from os.path import abspath
from os.path import normpath

from platform import system as platform_system
from platform import release as platform_release
from platform import node as platform_node

from os import remove as os_remove

from fnmatch import fnmatch
from fnmatch import translate
from re import search
from sys import getsizeof

from hashlib import sha1

from collections import defaultdict

from re import compile as re_compile
from re import IGNORECASE

from signal import SIGTERM

from time import time
from time import strftime
from time import localtime

#from gzip import open as gzip_open
from gzip import decompress as gzip_decompress
from gzip import compress as gzip_compress

#from bz2 import open as bz2_open
from bz2 import decompress as bz2_decompress
from bz2 import compress as bz2_compress

from pickle import dumps as dumps
from pickle import loads as loads

from pickle import dump as pickle_dump
from pickle import load as pickle_load

from difflib import SequenceMatcher
from subprocess import STDOUT, TimeoutExpired, PIPE, check_output

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

def byte_to_bools(byte, num_bools=7):
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

for i in range(128):
    temp_tuple = entry_LUT_decode[i]=byte_to_bools(i)
    entry_LUT_encode[temp_tuple]=i
    #print(i, temp_tuple)

#######################################################################
data_format_version='1.0004'

class LibrerCoreData :
    def __init__(self,label='',path=''):
        self.label=label
        self.scan_path = path
        self.creation_time = int(1000*time())
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

        self.pack_filestructure = None
        self.pack_filenames = None
        self.pack_custom_data = None

#######################################################################
class LibrerCoreRecord :
    def __init__(self,label,path,log):

        self.db = LibrerCoreData(label,path)

        #tylko w ramie
        self.filenames = ()
        self.filestructure = ()
        self.custom_data = ()

        self.log = log
        self.find_results = []

        self.info_line = ''
        self.info_line_current = ''

        self.abort_action = False
        self.files_search_progress = 0

        self.crc_progress_info=0
        self.FILE_NAME = ''
        self.FILE_SIZE = 0

    def get_time(self):
        return self.db.creation_time/1000

    def new_file_name(self):
        return f'{self.db.rid}.dat'

    def abort(self):
        self.abort_action = True

    def get_info(self):
        local_time = strftime('%Y/%m/%d %H:%M:%S',localtime(self.get_time()))
        return f'name: {self.db.label}\nscan path: {self.db.scan_path}\nsize: {bytes_to_str(self.db.sum_size)}\nhost: {self.db.creation_host}\nOS: {self.db.creation_os}\ncreation time: {local_time}\nfile: {self.FILE_NAME}\nfile size: {bytes_to_str(self.FILE_SIZE)}\n\nfilestructure size:{bytes_to_str(len(self.db.pack_filestructure))}\nfile names size:{bytes_to_str(len(self.db.pack_filenames))}\ncustom data size:{bytes_to_str(len(self.db.pack_custom_data))}'

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

        try:
            with scandir(path) as res:
                local_folder_files_count = 0
                local_folder_folders_count = 0

                for entry in res:
                    if self.abort_action:
                        break

                    entry_name = entry.name
                    file_names_set.add(entry_name)

                    is_dir,is_file,is_symlink = entry.is_dir(),entry.is_file(),entry.is_symlink()

                    self.ext_statistics[pathlib_Path(entry).suffix]+=1

                    self.info_line_current = entry_name
                    try:
                        stat_res = stat(entry)

                        mtime_ns = stat_res.st_mtime_ns
                        dev=stat_res.st_dev
                    except Exception as e:
                        self.log.error('stat error:%s', e )
                        #size -1 <=> error, dev,in ==0
                        is_bind = False
                        scan_like_data[entry_name] = [is_dir,is_file,is_symlink,is_bind,-1,0,None]
                    else:
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
                                dict_entry = None
                                size_entry = 0
                            elif is_bind:
                                dict_entry = None
                                size_entry = 0
                            else:
                                dict_entry={}
                                size_entry = self.scan_rec(path_join_loc(path,entry_name),dict_entry,file_names_set,check_dev,dev)

                                local_folder_size_with_subtree += size_entry

                            local_folder_folders_count += 1
                        else:
                            if is_symlink :
                                dict_entry = None
                                size_entry = 0
                            else:
                                dict_entry = None
                                size_entry = int(stat_res.st_size)

                                local_folder_size += size_entry

                            local_folder_files_count += 1

                        scan_like_data[entry_name]=[is_dir,is_file,is_symlink,is_bind,size_entry,mtime_ns,dict_entry]

                self_db = self.db
                self_db.sum_size += local_folder_size
                self_db.quant_files += local_folder_files_count
                self_db.quant_folders += local_folder_folders_count

        except Exception as e:
            self.log.error('scandir error:%s',e )

        self.info_line_current = ''

        return local_folder_size_with_subtree+local_folder_size

    def get_file_name(self,nr):
        return self.FILE_NAMES[nr]

    def scan(self,db_dir,cde_list,check_dev=True):
        self.info_line = 'Scanning filesystem'
        self.abort_action=False
        self.db_dir = db_dir
        self.db.sum_size = 0

        self.ext_statistics=defaultdict(int)
        self.scan_data={}

        #########################
        file_names_set=set()
        self.scan_rec(self.db.scan_path,self.scan_data,file_names_set)

        self.FILE_NAMES = tuple(sorted(list(file_names_set)))
        #########################
        self.info_line = 'indexing filesystem names'

        self.FILE_NAMES_helper = {fsname:fsname_index for fsname_index,fsname in enumerate(self.FILE_NAMES)}

        #dopiero na czas zapisu ?
        self.info_line = 'serializing file names'
        serialized_filenames = dumps(self.FILE_NAMES)

        self.info_line = 'compressing filesystem names'
        self.db.pack_filenames = bz2_compress(serialized_filenames)

        self.info_line = 'Processing filesystem data'
        self.set_data()

        self.db.cde_list = cde_list
        self.db.cd_stat=[0]*len(cde_list)

        self.custom_data_pool = {}
        self.custom_data_pool_index = 0

        #if cde_list:
        self.info_line = f'estimating files pool for custom data extraction'
        self.prepare_custom_data_pool_rec(self.scan_data,[])

        self.save()

        self.info_line = ''

        #for ext,stat in sorted(self.ext_statistics.items(),key = lambda x : x[1],reverse=True):
        #    print(ext,stat)

    #def data_group_test_rec(self,scan_like_data):
    #    list_flat = []
    #    for entry_name,items_list in scan_like_data.items():

    #        list_flat.append(entry_name)

    #        (is_dir,is_file,is_symlink,is_bind,size,mtime,sub_dict) = items_list[0:7]

    #        if is_dir:
    #            if not is_symlink and not is_bind:
    #                list_flat.extend(self.data_group_test_rec(sub_dict))

    #    return list_flat


    #############################################################
    def tupelize_rec(self,scan_like_data):
        entry_LUT_encode_loc = entry_LUT_encode

        self_tupelize_rec = self.tupelize_rec

        sub_list = []
        for entry_name,items_list in scan_like_data.items():

            try:
                #entry_name_index = self.FILE_NAMES.index(entry_name)
                entry_name_index = self.FILE_NAMES_helper[entry_name]
            except Exception as VE:
                print('FILE_NAMES error:',entry_name,VE)
            else:
                #print('entry_name_index:',entry_name_index)

                sub_list_elem=[entry_name_index]
                try:
                    len_items_list = len(items_list)
                    #print('items_list:',items_list,'len_items_list:',len_items_list)

                    (is_dir,is_file,is_symlink,is_bind,size,mtime,sub_dict) = items_list[0:7]

                    if len_items_list==7:
                        has_cd = False
                        has_files = True if bool(sub_dict) else  False

                        cd_ok=False
                        output = None

                    elif len_items_list==8:
                        cd_nr = items_list[7]

                        cd = self.custom_data[cd_nr]
                        #print('cd:',cd)

                        cd_len = len(cd)
                        if cd_len==2:
                            cd_ok,output = cd
                        elif cd_len==3:
                            cd_ok,output,crc = cd
                        else:
                            print('lewizna crc:')
                            continue

                        has_cd = True

                        has_files = False
                    else:
                        print('lewizna:',items_list)
                        continue

                    code_new = entry_LUT_encode_loc[ (is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok) ]

                    sub_list_elem.extend( [code_new,size,mtime] )

                    if has_cd: #only files
                        sub_list_elem.append( cd_nr )
                    elif is_dir:
                        if not is_symlink and not is_bind:
                            sub_tuple = self_tupelize_rec(sub_dict)
                            sub_list_elem.append(sub_tuple)

                except Exception as e:
                    self.log.error('tupelize_rec error::%s',e )
                    print('tupelize_rec error:',e,' items_list:',items_list)

                sub_list.append( tuple(sub_list_elem) )

        #return tuple( sorted(sub_list,key=lambda x : x[0]) )
        return tuple(sub_list)
    #############################################################

    def prepare_custom_data_pool_rec(self,scan_like_data,parent_path):
        scan_path = self.db.scan_path
        self_prepare_custom_data_pool_rec = self.prepare_custom_data_pool_rec

        self_db_cde_list = self.db.cde_list
        self_custom_data_pool = self.custom_data_pool

        for entry_name,items_list in scan_like_data.items():
            if self.abort_action:
                break
            try:
                is_dir,is_file,is_symlink,is_bind,size,mtime,sub_dict = items_list
                subpath_list = parent_path.copy() + [entry_name]

                if not is_symlink and not is_bind:
                    if is_dir:
                        self_prepare_custom_data_pool_rec(sub_dict,subpath_list)
                    else:
                        subpath=sep.join(subpath_list)
                        ############################

                        full_file_path = normpath(abspath(sep.join([scan_path,subpath])))

                        matched = False

                        rule_nr=-1
                        for expressions,use_smin,smin_int,use_smax,smax_int,executable,timeout,crc in self_db_cde_list:
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
                                    self.db.cd_stat[rule_nr]+=1
                                    self.db.files_cde_size_sum += size
                                    matched = True

            except Exception as e:
                self.log.error('prepare_custom_data_pool_rec error::%s',e )
                print('prepare_custom_data_pool_rec',e,entry_name,is_dir,is_file,is_symlink,is_bind,size,mtime)

    #def get_cd_text(self,cd_data,is_compressed):
        #'utf-8'
        #return gzip_decompress(cd_data).decode("ISO-8859-1") if is_compressed else cd_data
    #    return gzip_decompress(cd_data).decode("ISO-8859-1") if is_compressed else cd_data

    def extract_custom_data(self):
        scan_path = self.db.scan_path

        self.info_line = f'custom data extraction ...'
        self_db = self.db

        self_db.files_cde_quant = 0
        self_db.files_cde_size = 0
        self_db.files_cde_size_extracted = 0
        self_db.files_cde_errors_quant = 0
        self_db.files_cde_quant_sum = len(self.custom_data_pool)

        self_db_cde_list = self_db.cde_list

        exe = Executor()

        custom_data_helper={}
        custom_data_list=[]
        custom_data_index=0

        for (list_ref,subpath,rule_nr) in self.custom_data_pool.values():
            if self.abort_action:
                break

            expressions,use_smin,smin_int,use_smax,smax_int,executable,timeout,crc = self_db_cde_list[rule_nr]

            full_file_path = normpath(abspath(sep.join([scan_path,subpath]))).replace('/',sep)

            size = list_ref[4]

            cde_run_list = executable + [full_file_path]

            if crc:
                self.info_line_current = f'{subpath} CRC calculation ({bytes_to_str(size)})'
                crc_val = self.calc_crc(full_file_path,size)
                #print(crc_val)

            self.info_line_current = f'{subpath} ({bytes_to_str(size)})'

            cd_ok,output = exe.run(cde_run_list,timeout)

            new_list_ref_elem = [cd_ok,output]

            if not cd_ok:
                self_db.files_cde_errors_quant +=1

            if crc:
                new_list_ref_elem.append(crc_val)

            new_list_ref_elem_tuple = tuple(new_list_ref_elem)

            if new_list_ref_elem_tuple not in custom_data_helper:
                custom_data_helper[new_list_ref_elem_tuple]=custom_data_index
                custom_data_index+=1
                custom_data_list.append(new_list_ref_elem_tuple)

            #list_ref.append( tuple(new_list_ref_elem) )
            list_ref.append( custom_data_helper[new_list_ref_elem_tuple] )
            #self.custom_data

            self_db.files_cde_quant += 1
            self_db.files_cde_size += size
            self_db.files_cde_size_extracted += getsizeof(output)

            self.info_line_current = ''

        del self.custom_data_pool
        self.custom_data = tuple(custom_data_list)
        #print('self.custom_data:',len(self.custom_data),'vs',custom_data_index,'\n',self.custom_data)

        exe.end()

        self.set_data()

        self.scan_data={}

        self.save()

    search_kind_code_tab={'dont':0,'without':1,'any':2,'error':3,'regexp':4,'glob':5,'fuzzy':6}

    def set_data(self):
        size,mtime = 0,0
        is_dir = True
        is_file = False
        is_symlink = False
        is_bind = False
        has_cd = False
        has_files = True
        cd_ok = False

        code = entry_LUT_encode[ (is_dir,is_file,is_symlink,is_bind, has_cd,has_files,cd_ok) ]
        self.filestructure = ('',code,size,mtime,self.tupelize_rec(self.scan_data))

        #del self.FILE_NAMES_helper

        self.info_line = 'serializing filesystem structure'
        serialized_filestructure = dumps(self.filestructure)

        self.info_line = 'compressing filesystem structure'
        self.db.pack_filestructure = bz2_compress(serialized_filestructure)

        self.info_line = 'serializing custom data'
        serialized_custom_data = dumps(self.custom_data)

        self.info_line = 'compressing custom data'
        self.db.pack_custom_data = bz2_compress(serialized_custom_data)

    def find_items(self,
            size_min,size_max,
            filename_search_kind,name_func_to_call,cd_search_kind,cd_func_to_call):

        self.decompress()

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

        entry_LUT_decode_loc = entry_LUT_decode

        use_size = True if size_min or size_max else False

        search_list = [ (filestructure[4],[]) ]
        search_list_pop = search_list.pop
        search_list_append = search_list.append

        rgf_group = (regexp_kind_code,glob_kind_code,fuzzy_kind_code)

        while search_list:
            if self.abort_action:
                break

            filestructure,parent_path_components = search_list_pop()

            for data_entry in filestructure:
                if self.abort_action:
                    break

                data_entry_len = len(data_entry)
                if data_entry_len==5:
                    name_nr,code,size,mtime,fifth_field = data_entry
                elif data_entry_len==4:
                    name_nr,code,size,mtime = data_entry
                else:
                    print('format error:',data_entry_len,data_entry[0])
                    continue
                name = file_names_loc[name_nr]

                next_level = parent_path_components + [name]

                is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok = entry_LUT_decode_loc[code]

                sub_data = fifth_field if is_dir and has_files else None

                self.files_search_progress +=1

                cd_search_kind_code_is_rgf = True if cd_search_kind_code in rgf_group else False

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
                            cd_nr = fifth_field
                            cd_data = self.custom_data[cd_nr]
                            #cd_data = fifth_field
                        else:
                            continue

                        if cd_func_to_call:
                            try:
                                cd_txt = cd_data
                                #self.get_cd_text(cd_data)

                                if not cd_func_to_call(cd_txt):
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

    def save(self) :
        file_name=self.new_file_name()
        self.info_line = f'saving {file_name}'
        file_path=sep.join([self.db_dir,file_name])
        self.log.info('saving %s' % file_path)

        #print(dir(self.db))
        #with gzip_open(file_path, "wb") as gzip_file:
        #    pickle_dump(self.db, gzip_file)

        with open(file_path, "wb") as raw_file:
            pickle_dump(self.db, raw_file)

        #with bz2_open(file_path + '.bz2', "wb") as bz2_file:
        #    pickle_dump(self.db, bz2_file)

        try:
            self.FILE_NAME = file_name
            self.FILE_SIZE = stat(file_path).st_size
        except Exception as e:
            print('stat error:%s' % e )

        self.info_line = ''

    def load(self,db_dir,file_name):
        self.log.info('loading %s' % file_name)
        self.FILE_NAME = file_name

        try:
            full_file_path = sep.join([db_dir,file_name])
            stat_res = stat(full_file_path)
            self.FILE_SIZE = stat_res.st_size
            with open(full_file_path, "rb") as raw_file:
                self.db = pickle_load(raw_file)

            global data_format_version
            if self.db.data_format_version != data_format_version:
                self.log.error(f'incompatible data format version error: {self.db.data_format_version} vs {data_format_version}')
                return True

        except Exception as e:
            print('loading error:%s' % e )
            return True
        else:
            return False

    decompressed = False
    def decompress(self):
        if not self.decompressed:
            self.FILE_NAMES = loads(bz2_decompress(self.db.pack_filenames))
            self.filestructure = loads(bz2_decompress(self.db.pack_filestructure))
            self.custom_data = loads(bz2_decompress(self.db.pack_custom_data))
            self.decompressed = True
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
        self.records_sorted = sorted(self.records,key = lambda x : x.db.creation_time)

    def create(self,label='',path=''):
        new_record = LibrerCoreRecord(label,path,self.log)

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

            if new_record.load(self.db_dir,ename) :
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
        self.files_search_quant = sum([record.db.quant_files for record in sel_range])

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

            self.info_line = f'searching in record: {record.db.label}'

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

            self.files_search_progress += record.db.quant_files
            self.find_res_quant = len(record.find_results)
        ############################################################


    def delete_record_by_id(self,rid):
        for record in self.records:
            if record.db.rid == rid:
                file_path = sep.join([self.db_dir,record.FILE_NAME])
                self.log.info('deleting file:%s',file_path)
                try:
                    os_remove(file_path)
                except Exception as e:
                    self.log.error(e)

        self.update_sorted()

