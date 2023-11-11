from os import scandir
from os import stat
from os import sep
from os.path import join as path_join
from os.path import abspath
from os.path import normpath
from os import remove as os_remove

from fnmatch import fnmatch
from fnmatch import translate
from re import search
from sys import getsizeof

from collections import defaultdict

import re
from re import IGNORECASE

from time import time

import gzip
import zlib
import pickle

import difflib

import subprocess

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
    units = {'b':1, 'kb': 1024,'mb': 1024*1024,'gb': 1024*1024*1024,'tb': 1024*1024*1024*1024}
    try:
        string = string.replace(' ','')
        for suffix in units:
            if string.lower().endswith(suffix):
                return int(string[0:-len(suffix)]) * units[suffix]

        return int(string)
    except:
        return -1

def test_regexp(expr):
    teststring='abc'
    try:
        search(expr,teststring)
    except Exception as e:
        return e
    else:
        return None

#######################################################################
data_format_version='1.0001'

class LibrerCoreData :
    label = ""
    creation_time = None
    rid = None #data record id
    scan_path = None
    data = None
    quant_files = 0
    quant_folders = 0
    data_format_version=''

    def __init__(self,label,path):
        self.label=label
        self.scan_path = path
        self.creation_time = int(1000*time())
        self.rid = self.creation_time
        self.data = {}
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

    def get_time(self):
        return self.creation_time/1000

entry_LUT_code={
    (True,True,True):7,
    (True,True,False):6,
    (True,False,True):5,
    (True,False,False):4,
    (False,True,True):3,
    (False,True,False):2,
    (False,False,True):1,
    (False,False,False):0
}

entry_LUT_decode={
    7:(True,True,True),
    6:(True,True,False),
    5:(True,False,True),
    4:(True,False,False),
    3:(False,True,True),
    2:(False,True,False),
    1:(False,False,True),
    0:(False,False,False)
}
#######################################################################
class LibrerCoreRecord :
    def __init__(self,label,path,log):
        self.db = LibrerCoreData(label,path)
        self.log = log
        self.find_results = set()
        self.find_results_list = []
        self.info_line = ''

        self.abort_action = False
        self.files_search_progress = 0

    def file_name(self):
        return f'{self.db.rid}.dat'

    def abort(self):
        self.abort_action = True

    def scan_rec(self, path, dictionary) :
        if self.abort_action:
            return True

        entry_LUT_code_loc = entry_LUT_code
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

                    is_dir,is_file,is_symlink = entry.is_dir(),entry.is_file(),entry.is_symlink()
                    code = entry_LUT_code_loc[ (is_dir,is_file,is_symlink) ]

                    try:
                        stat_res = stat(entry)

                        mtime_ns = stat_res.st_mtime_ns
                    except Exception as e:
                        self.log.error('stat error:%s', e )
                        #size -1 <=> error, dev,in ==0
                        dictionary[entry_name] = [code,-1,0,None]
                    else:

                        if is_dir:
                            if is_symlink :
                                dict_entry = None
                                size_entry = 0
                            else:
                                dict_entry={}
                                size_entry = self.scan_rec(path_join_loc(path,entry_name),dict_entry)

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

                        dictionary[entry_name]=[code,size_entry,mtime_ns,dict_entry]

                self_db = self.db
                self_db.sum_size += local_folder_size
                self_db.quant_files += local_folder_files_count
                self_db.quant_folders += local_folder_folders_count

        except Exception as e:
            self.log.error('scandir error:%s',e )

        return local_folder_size_with_subtree+local_folder_size

    def scan (self,db_dir,cde_list):
        self.info_line = 'Scanning filesystem'
        self.abort_action=False
        self.db_dir = db_dir
        self.db.sum_size = 0
        self.scan_rec(self.db.scan_path,self.db.data)
        self.save()

        self.db.cde_list = cde_list
        self.db.cd_stat=[0]*len(cde_list)

        self.custom_data_pool = {}
        self.custom_data_pool_index = 0

        self.info_line = f'estimating files pool for custom data extraction'
        self.prepare_custom_data_pool_rec(self.db.data,[])
        self.info_line = ''

    def prepare_custom_data_pool_rec(self,dictionary,parent_path):
        entry_LUT_decode_loc = entry_LUT_decode
        scan_path = self.db.scan_path
        self_prepare_custom_data_pool_rec = self.prepare_custom_data_pool_rec

        self_db_cde_list = self.db.cde_list
        self_custom_data_pool = self.custom_data_pool
        for entry_name,items_list in dictionary.items():
            try:
                (code,size,mtime,sub_dict) = items_list
                is_dir,is_file,is_symlink = entry_LUT_decode_loc[code]
                subpath_list = parent_path.copy() + [entry_name]

                if not is_symlink:
                    if is_dir:
                        self_prepare_custom_data_pool_rec(sub_dict,subpath_list)
                    else:
                        #self.custom_data_pool[self.custom_data_pool_index]=[items_list,sep.join(subpath_list)]
                        subpath=sep.join(subpath_list)
                        ############################
                        #for key,[items_list,subpath] in self.custom_data_pool.items():
                        if self.abort_action:
                            break

                        #print(key,items_list,subpath)
                        full_file_path = normpath(abspath(sep.join([scan_path,subpath])))
                        #full_file_path_protected = f'"{full_file_path}"'
                        #print(full_file_path_protected)

                        size = items_list[1]
                        matched = False

                        rule_nr=-1
                        for expressions,use_smin,smin_int,use_smax,smax_int,executable in self_db_cde_list:
                            if self.abort_action:
                                break

                            if matched:
                                break

                            rule_nr+=1

                            if use_smin:
                                if size<smin_int:
                                    #print('min skipped',size,smin_int,subpath)
                                    continue
                            if use_smax:
                                if size>smax_int:
                                    #print('max skipped',size,smax_int,subpath)
                                    continue

                            for expr in expressions:
                                if matched:
                                    break

                                #print(full_file_path,expr)
                                if fnmatch(full_file_path,expr):
                                    self_custom_data_pool[self.custom_data_pool_index]=[items_list,subpath,rule_nr]
                                    self.custom_data_pool_index += 1
                                    self.db.cd_stat[rule_nr]+=1
                                    self.db.files_cde_size_sum += size
                                    matched = True

            except Exception as e:
                self.log.error('prepare_custom_data_pool_rec error::%s',e )
                print(e,items_list)

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
        for [list_ref,subpath,rule_nr] in self.custom_data_pool.values():
            if self.abort_action:
                break

            expressions,use_smin,smin_int,use_smax,smax_int,executable = self_db_cde_list[rule_nr]

            #print(key,list_ref,subpath)
            full_file_path = normpath(abspath(sep.join([scan_path,subpath])))
            #full_file_path_protected = f'"{full_file_path}"'
            #print(full_file_path_protected)

            size = list_ref[1]

            cde_run_list = executable + [full_file_path]

            try:
                #print(cde_run_list)
                result = subprocess.run(cde_run_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True,encoding="ISO-8859-1")
                #text=True,
                #, encoding="ISO-8859-1"
            except Exception as e:
                self.log.error('Custom Data Extraction subprocess error:%s\n%s',cde_run_list,e )
                cd_code=1
                e_str = str(e)
                e_size = getsizeof(e_str)
                list_ref.append( (cd_code,'',str(e)) )
                self_db.files_cde_errors_quant +=1

                self_db.files_cde_size += e_size
            else:

                result1 = str(result.stdout).strip()
                result2 = str(result.stderr).strip()


                #print(result1)
                #print(result2)
                #result1_compressed = zlib.compress(bytes(result1,"utf-8"))
                #print(f'compare:{len(result1)} vs {len(result1_compressed)}')
                #result1 = result1_compressed

                #res_tuple_list =

                #if result2!='':
                #    res_tuple_list.append(result2)

                cd_code=0
                list_ref.append( (cd_code,result1,result2) )

                self_db.files_cde_quant += 1
                self_db.files_cde_size += size
                self_db.files_cde_size_extracted += getsizeof(result1) + getsizeof(result2)


        del self.custom_data_pool

        self.save()

        #file_path=sep.join([self_db_dir,self.file_name()])
        #self.log.info('saving %s' % file_path)

        #with gzip.open(file_path, "wb") as gzip_file:
        #    pickle.dump(self_db, gzip_file)

        for rule,stat in zip(self_db.cde_list,self_db.cd_stat):
            print('cd_stat',rule,stat)

    search_kind_code_tab={'dont':0,'without':1,'error':2,'regexp':3,'glob':4,'fuzzy':5}
    def find_items(self,
            size_min,size_max,
            filename_search_kind,name_func_to_call,cd_search_kind,cd_func_to_call):

        dont_kind_code = self.search_kind_code_tab['dont']
        regexp_kind_code = self.search_kind_code_tab['regexp']
        glob_kind_code = self.search_kind_code_tab['glob']
        without_kind_code = self.search_kind_code_tab['without']
        error_kind_code = self.search_kind_code_tab['error']
        fuzzy_kind_code = self.search_kind_code_tab['fuzzy']

        find_results = self.find_results = set()
        find_results_add = find_results.add

        local_dict = self.db.data
        parent_path_components = []
        self.files_search_progress = 0

        filename_search_kind_code = self.search_kind_code_tab[filename_search_kind]
        cd_search_kind_code = self.search_kind_code_tab[cd_search_kind]

        entry_LUT_decode_loc = entry_LUT_decode

        if size_min or size_max:
            use_size= True
        else:
            use_size= False

        search_list = [ (local_dict,parent_path_components)]
        search_list_pop = search_list.pop
        search_list_append = search_list.append

        best_fuzzy_match=0
        while search_list:
            local_dict,parent_path_components = search_list_pop()

            for name,val in sorted(local_dict.items()):
                if self.abort_action:
                    break

                try:
                    code,size,mtime,sub_dict,cd=val
                except:
                    code,size,mtime,sub_dict=val
                    cd=None

                is_dir,is_file,is_symlink = entry_LUT_decode_loc[code]
                self.files_search_progress +=1

                if is_file:
                    if use_size:
                        if size_min:
                            if size<size_min:
                                continue
                        if size_max:
                            if size>size_max:
                                continue

                if is_dir :
                    if cd_search_kind_code==dont_kind_code:
                        #katalog moze spelniac kryteria naazwy pliku, nie ma rozmiaru i custom data
                        if name_func_to_call:
                            if name_func_to_call(name):
                                single_res = parent_path_components + [name]
                                find_results_add( tuple(single_res) )

                    if sub_dict:
                        search_list_append( (sub_dict,parent_path_components + [name]) )

                else:
                    if name_func_to_call:
                        func_res_code = name_func_to_call(name)
                        if filename_search_kind_code==fuzzy_kind_code:
                            if func_res_code>best_fuzzy_match:
                                best_fuzzy_match = func_res_code
                                find_results={ tuple(parent_path_components + [name]) }
                                print(func_res_code)

                            continue
                            #if func_res_code<0.6:
                            #    continue
                        elif filename_search_kind_code in (regexp_kind_code,glob_kind_code):
                            if not func_res_code:
                                continue
                        else:
                            pass
                    if cd_search_kind_code==dont_kind_code:
                        pass
                    if cd_search_kind_code in (regexp_kind_code,glob_kind_code):
                        if cd_func_to_call:
                            if cd:
                                if len(cd)==3:
                                    cd_code = cd[0]
                                    if cd_code==0:
                                        try:
                                            if not cd_func_to_call(cd[1]):
                                                continue
                                        except Exception as e:
                                            self.log.error('find_items_rec:%s on:\n%s',str(e),str(cd) )
                                            continue
                                    else:
                                        continue
                                else:
                                    print('find problem 1:',cd)
                                    continue
                            else:
                                continue
                    elif cd_search_kind_code==without_kind_code:
                        if cd:
                            continue
                    elif cd_search_kind_code==error_kind_code:
                        if cd:
                            cd_code = cd[0]
                            if cd_code==0:
                                continue
                        else:
                            continue
                    elif cd_search_kind_code==fuzzy_kind_code:
                        if cd_func_to_call:
                            if cd:
                                if len(cd)==3:
                                    cd_code = cd[0]
                                    if cd_code==0:
                                        try:
                                            fuzzy_result = cd_func_to_call(cd[1])
                                            print(fuzzy_result)
                                        except Exception as e:
                                            self.log.error('find_items_rec:%s on:\n%s',str(e),str(cd) )
                                            continue
                                        else:
                                            if fuzzy_result<0.6:
                                                continue
                                    else:
                                        continue
                                else:
                                    print('find problem 1:',cd)
                                    continue
                            else:
                                continue
                    else:
                        print('to check')

                    #single_res = parent_path_components + [name]
                    find_results_add( tuple(parent_path_components + [name]) )

        self.find_results_list = list(find_results)

    def save(self) :
        file_name=self.file_name()
        self.info_line = f'saving {file_name}'
        file_path=sep.join([self.db_dir,file_name])
        self.log.info('saving %s' % file_path)

        with gzip.open(file_path, "wb") as gzip_file:
            pickle.dump(self.db, gzip_file)

        self.info_line = ''

    def load(self,db_dir,file_name):
        self.log.info('loading %s' % file_name)
        try:
            full_file_path = sep.join([db_dir,file_name])
            with gzip.open(full_file_path, "rb") as gzip_file:
                self.db = pickle.load(gzip_file)

        except Exception as e:
            print('loading error:%s' % e )
            return True
        else:
            return False

#######################################################################
class LibrerCore:
    records = set()
    db_dir=''

    def __init__(self,db_dir,log):
        self.records = set()
        self.db_dir = db_dir
        self.log=log
        self.info_line = 'init'

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
            find_cd_search_kind,cd_expr,cd_case_sens):

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

        return None

    def find_items_in_all_records(self,
            range_par,
            size_min,size_max,
            find_filename_search_kind,name_expr,name_case_sens,
            find_cd_search_kind,cd_expr,cd_case_sens):

        print('find_items_in_all_records',range_par,
                size_min,size_max,
                find_filename_search_kind,name_expr,name_case_sens,
                find_cd_search_kind,cd_expr,cd_case_sens)

        if name_expr:
            if find_filename_search_kind == 'regexp':
                name_func_to_call = lambda x : search(name_expr,x)
            elif find_filename_search_kind == 'glob':
                if name_case_sens:
                    #name_func_to_call = lambda x : fnmatch(x,name_expr)
                    name_func_to_call = lambda x : re.compile(translate(name_expr)).match(x)
                else:
                    name_func_to_call = lambda x : re.compile(translate(name_expr), IGNORECASE).match(x)
            elif find_filename_search_kind == 'fuzzy':
                name_func_to_call = lambda x : difflib.SequenceMatcher(None, name_expr, x).ratio()
            else:
                name_func_to_call = None
        else:
            name_func_to_call = None

        if cd_expr:
            if find_cd_search_kind == 'regexp':
                cd_func_to_call = lambda x : search(cd_expr,x)
            elif find_cd_search_kind == 'glob':
                if cd_case_sens:
                    #cd_func_to_call = lambda x : fnmatch(x,cd_expr)
                    cd_func_to_call = lambda x : re.compile(translate(cd_expr)).match(x)
                else:
                    cd_func_to_call = lambda x : re.compile(translate(cd_expr), IGNORECASE).match(x)
            elif find_cd_search_kind == 'fuzzy':
                cd_func_to_call = lambda x : difflib.SequenceMatcher(None, name_expr, x).ratio()
            else:
                cd_func_to_call = None
        else:
            cd_func_to_call = None

        #print('fuzz:',difflib.SequenceMatcher(None, 'hello world', 'hello').ratio())

        self.find_res_quant = 0
        sel_range = [range_par] if range_par else self.records

        self.files_search_progress = 0

        self.search_record_nr=0
        self.search_record_ref=None

        records_len = len(self.records)
        ############################################################
        for record in sel_range:
            self.search_record_ref = record

            self.search_record_nr+=1
            self.records_perc_info = self.search_record_nr * 100.0 / records_len

            self.info_line = f'searching in record: {record.db.label}'

            if self.abort_action:
                break

            try:
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
                print('found record to delete:',rid)

                file_path = sep.join([self.db_dir,record.file_name()])
                self.log.info('deleting file:%s',file_path)
                try:
                    os_remove(file_path)
                except Exception as e:
                    self.log.error(e)

        self.update_sorted()

