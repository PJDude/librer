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

from time import  perf_counter,time,strftime,localtime

from threading import Thread

from os import scandir,stat,sep

from os.path import abspath,normpath,basename
from os.path import join as path_join

from zipfile import ZipFile

from platform import system as platform_system
from platform import release as platform_release
from platform import node as platform_node

from fnmatch import fnmatch,translate

from re import search,IGNORECASE
from re import compile as re_compile

from sys import getsizeof

from collections import defaultdict

from pickle import dumps,loads

from difflib import SequenceMatcher

from pathlib import Path as pathlib_Path

from zstandard import ZstdCompressor,ZstdDecompressor

from executor import Executor

from func import *

data_format_version='1.0010'

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
        self.files_cde_errors_quant = 0

        self.cde_list = []

        self.creation_os,self.creation_host = f'{platform_system()} {platform_release()}',platform_node()

#######################################################################
class LibrerRecord:
    def __init__(self,label,scan_path,log):
        self.header = LibrerRecordHeader(label,scan_path)

        self.filestructure = ()
        self.customdata = []

        self.log = log
        self.find_results = []

        self.info_line = ''
        self.info_line_current = ''

        self.abort_action = False

        #self.crc_progress_info=0

        self.FILE_NAME = ''
        self.FILE_SIZE = 0
        self.file_path = ''

        self.zipinfo={'header':'?','filestructure':'?','filenames':'?','customdata':'?'}
        self.exe = None

    def find_results_clean(self):
        self.find_results = []

    def new_file_name(self):
        return f'{self.header.rid}.dat'

    def abort(self):
        if self.exe:
            self.exe.abort_now()

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
        filenames_set=set()
        self.scan_rec(self.header.scan_path,self.scan_data,filenames_set,check_dev=check_dev)

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

    def extract_customdata_update(self):
        self.info_line_current = self.exe.info
        self_header = self.header

        self_header.files_cde_errors_quant = self.exe.files_cde_errors_quant

        self_header.files_cde_quant = self.exe.files_cde_quant
        self_header.files_cde_size = self.exe.files_cde_size
        self_header.files_cde_size_extracted = self.exe.files_cde_size_extracted

    def extract_customdata(self):
        self_header = self.header
        scan_path = self_header.scan_path

        self.info_line = 'custom data extraction ...'

        self_header.files_cde_quant = 0
        self_header.files_cde_size = 0
        self_header.files_cde_size_extracted = 0
        self_header.files_cde_errors_quant = 0
        self_header.files_cde_quant_sum = len(self.customdata_pool)

        cde_list = self.header.cde_list

        customdata_helper={}

        cd_index=0
        self_customdata_append = self.customdata.append

        io_list=[]

        #############################################################
        for (scan_like_list,subpath,rule_nr,size) in self.customdata_pool.values():
            if self.abort_action:
                break
            expressions,use_smin,smin_int,use_smax,smax_int,executable,parameters,shell,timeout,do_crc = cde_list[rule_nr]

            full_file_path = normpath(abspath(sep.join([scan_path,subpath]))).replace('/',sep)

            io_list.append( [ executable,parameters,full_file_path,timeout,shell,do_crc,size,scan_like_list,rule_nr ] )

        #############################################################
        self.exe=Executor(io_list,self.extract_customdata_update)

        self.exe.run()
        #############################################################
        for io_list_elem in io_list:
            executable,parameters,full_file_path,timeout,shell,do_crc,size,scan_like_list,rule_nr,result_tuple = io_list_elem
            if do_crc:
                returncode,output,crc_val = result_tuple
            else:
                returncode,output = result_tuple

            new_elem={}
            new_elem['cd_ok']= bool(returncode==0)

            if output not in customdata_helper:
                customdata_helper[output]=cd_index
                new_elem['cd_index']=cd_index
                cd_index+=1

                self_customdata_append(output)
            else:
                new_elem['cd_index']=customdata_helper[output]

            if do_crc:
                new_elem['crc_val']=crc_val

            scan_like_list.append(new_elem)

        #############################################################

        del self.customdata_pool
        del customdata_helper

        self.exe = None

    #############################################################
    def tupelize_rec(self,scan_like_data):
        LUT_encode_loc = LUT_encode

        self_tupelize_rec = self.tupelize_rec

        self_customdata = self.customdata
        sub_list = []
        for entry_name,items_list in scan_like_data.items():

            try:
                entry_name_index = self.filenames_helper[entry_name]
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

        code = LUT_encode[ (is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc) ]
        self.filestructure = ('',code,size,mtime,self.tupelize_rec(self.scan_data))

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
            name_func_to_call,cd_search_kind,cd_func_to_call):

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

        search_list = [ (filestructure[4],[]) ]
        search_list_pop = search_list.pop
        search_list_append = search_list.append

        cd_search_kind_is_regezp_glob_or_fuzzy = bool(cd_search_kind in ('regexp','glob','fuzzy'))
        cd_search_kind_is_dont_or_without = bool(cd_search_kind in ('dont','without'))

        when_folder_may_apply = bool(cd_search_kind_is_dont_or_without and not use_size)
        cd_search_kind_is_any = bool(cd_search_kind=='any')
        cd_search_kind_is_without = bool(cd_search_kind=='without')
        cd_search_kind_is_error = bool(cd_search_kind=='error')

        self_customdata = self.customdata

        results_queue_put = results_queue.put

        while search_list:
            filestructure,parent_path_components = search_list_pop()

            for data_entry in filestructure:
                #if check_abort():
                #    break

                search_progress_update_quant+=1
                if search_progress_update_quant>1024:
                    #yield (search_progress,None) #just update progress bar
                    #yield [search_progress] #just update progress bar
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
                if is_dir :
                    if when_folder_may_apply:
                        #katalog moze spelniac kryteria naazwy pliku ale nie ma rozmiaru i custom data
                        if name_func_to_call:
                            if name_func_to_call(name):
                                #yield (search_progress,tuple([tuple(next_level),size,mtime]))
                                #yield [search_progress,size,mtime,*next_level]
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
                            cd_data = self_customdata[cd_nr]
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

                    #yield (search_progress,tuple([tuple(next_level),size,mtime ]))
                    #yield (search_progress,tuple([tuple(next_level),size,mtime ]))
                    #yield [search_progress,size,mtime,*next_level]
                    results_queue_put([search_progress,size,mtime,*next_level])
                    search_progress_update_quant=0

        #yield [search_progress]
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

    def prepare_info(self):
        bytes_to_str_mod = lambda x : bytes_to_str(x) if isinstance(x,int) else x

        info_list = []

        self.txtinfo = 'init'
        self.txtinfo_basic = 'init-basic'

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
            info_list.append(f'record label    : {self_header.label}')
            info_list.append('')
            info_list.append(f'scanned path    : {self_header.scan_path}')
            info_list.append(f'scanned space   : {bytes_to_str(self_header.sum_size)}')
            info_list.append(f'scanned files   : {fnumber(self_header.quant_files)}')
            info_list.append(f'scanned folders : {fnumber(self_header.quant_folders)}')
            info_list.append('')
            info_list.append(f'creation host   : {self_header.creation_host} ({self_header.creation_os})')
            info_list.append(f'creation time   : {local_time}')

            self.txtinfo_basic = '\n'.join(info_list)

            info_list.append('')
            info_list.append(f'database file   : {self.FILE_NAME} ({bytes_to_str(self.FILE_SIZE)})')
            info_list.append('')
            info_list.append('internal sizes  :   compressed  decompressed')
            info_list.append('')

            info_list.append(f'header          :{bytes_to_str_mod(zip_file_info["header"]).rjust(14)}{bytes_to_str_mod(self.zipinfo["header"]).rjust(14)}')
            info_list.append(f'filestructure   :{bytes_to_str_mod(zip_file_info["filestructure"]).rjust(14)}{bytes_to_str_mod(self.zipinfo["filestructure"]).rjust(14)}')
            info_list.append(f'file names      :{bytes_to_str_mod(zip_file_info["filenames"]).rjust(14)}{bytes_to_str_mod(self.zipinfo["filenames"]).rjust(14)}')

            if zip_file_info["customdata"]:
                info_list.append(f'custom data     :{bytes_to_str_mod(zip_file_info["customdata"]).rjust(14)}{bytes_to_str_mod(self.zipinfo["customdata"]).rjust(14)}')

            try:
                if self_header.cde_list:
                    info_list.append('\nCDE rules (draft):')
                    for nr,single_cde in enumerate(self_header.cde_list):
                        info_list.append(str(nr) + ':' + str(single_cde))
            except:
                pass

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
            compressor = ZstdCompressor(level=compression_level,threads=-1)

            header_ser = dumps(self.header)
            self.zipinfo['header'] = len(header_ser)
            zip_file.writestr('header',compressor.compress(header_ser))

            self.info_line = f'saving {filename} (File stucture)'
            filestructure_ser = dumps(self.filestructure)
            self.zipinfo['filestructure'] = len(filestructure_ser)
            zip_file.writestr('filestructure',compressor.compress(filestructure_ser))

            self.info_line = f'saving {filename} (File names)'
            filenames_ser = dumps(self.filenames)
            self.zipinfo['filenames'] = len(filenames_ser)
            zip_file.writestr('filenames',compressor.compress(filenames_ser))

            if self.customdata:
                self.info_line = f'saving {filename} (Custom Data)'
                customdata_ser = dumps(self.customdata)
                self.zipinfo['customdata'] = len(customdata_ser)
                zip_file.writestr('customdata',compressor.compress(customdata_ser))
            else:
                self.zipinfo['customdata'] = 0

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
                header_ser = ZstdDecompressor().decompress(zip_file.read('header'))
                self.header = loads( header_ser )
                self.zipinfo['header'] = len(header_ser)

            self.prepare_info()

            if self.header.data_format_version != data_format_version:
                self.log.error(f'incompatible data format version error: {self.header.data_format_version} vs {data_format_version}')
                return True

        except Exception as e:
            print('loading error:%s' % e )
            return True

        return False

    decompressed_filestructure = False
    def decompress_filestructure(self):
        if not self.decompressed_filestructure:
            with ZipFile(self.file_path, "r") as zip_file:
                decompressor = ZstdDecompressor()

                filestructure_ser = decompressor.decompress(zip_file.read('filestructure'))
                self.filestructure = loads( filestructure_ser )
                self.zipinfo['filestructure'] = len(filestructure_ser)

                filenames_ser = decompressor.decompress(zip_file.read('filenames'))
                self.filenames = loads(filenames_ser)
                self.zipinfo['filenames'] = len(filenames_ser)

            self.decompressed_filestructure = True

            self.prepare_info()

            return True

        return False

    decompressed_customdata = False
    def decompress_customdata(self):
        if not self.decompressed_customdata:
            with ZipFile(self.file_path, "r") as zip_file:
                try:
                    customdata_ser_comp = zip_file.read('customdata')
                    customdata_ser = ZstdDecompressor().decompress(customdata_ser_comp)
                    self.customdata = loads( customdata_ser )
                    self.zipinfo['customdata'] = len(customdata_ser)
                except:
                    self.customdata = []
                    self.zipinfo['customdata'] = 0

            self.decompressed_customdata = True

            self.prepare_info()
            return True

        return False

