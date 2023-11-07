from os import scandir
from os import stat
from os import sep
from os.path import join as path_join
from os.path import abspath
from os.path import normpath
from os import remove as os_remove

from fnmatch import fnmatch
from re import search

from collections import defaultdict

import re
import fnmatch

from time import time

import gzip
import zlib
import pickle

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
    units = {'kb': 1024,'mb': 1024*1024,'gb': 1024*1024*1024,'tb': 1024*1024*1024*1024}
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
    sum_size = 0
    data_format_version=''
    files_cde_size = 1

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
    db = None

    def __init__(self,label,path,log):
        self.db = LibrerCoreData(label,path)
        self.log = log
        self.find_results = []
        self.info_line = ''

        self.files_cde = 0 #custom data extracted info
        self.files_cde_not = 0
        self.abort_action = False

    def file_name(self):
        return f'{self.db.rid}.dat'

    def abort(self):
        self.abort_action = True

    def do_scan(self, path, dictionary) :
        if self.abort_action:
            return True

        entry_LUT_code_loc = entry_LUT_code
        path_join_loc = path_join

        local_folder_files_size_sum=0
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
                                size_entry = self.do_scan(path_join_loc(path,entry_name),dict_entry)

                                local_folder_files_size_sum += size_entry

                            local_folder_folders_count += 1
                        else:
                            if is_symlink :
                                dict_entry = None
                                size_entry = 0
                            else:
                                dict_entry = None
                                size_entry = int(stat_res.st_size)

                                local_folder_files_size_sum += size_entry
                                self.db.sum_size += size_entry

                            local_folder_files_count += 1

                        dictionary[entry_name]=[code,size_entry,mtime_ns,dict_entry]

                self.db.quant_files += local_folder_files_count
                self.db.quant_folders += local_folder_folders_count

        except Exception as e:
            self.log.error('scandir error:%s',e )

        return local_folder_files_size_sum

    def scan (self,db_dir):
        self.abort_action=False
        self.db_dir = db_dir
        self.db.sum_size = 0
        self.do_scan(self.db.scan_path,self.db.data)
        self.save(db_dir)
        self.prepare_custom_data_pool()

        self.db.cde_list = []
        self.db.cd_stat=[]

    def do_prepare_custom_data_pool(self,dictionary,parent_path):
        entry_LUT_decode_loc = entry_LUT_decode
        for entry_name,items_list in dictionary.items():
            try:
                (code,size,mtime,sub_dict) = items_list
                is_dir,is_file,is_symlink = entry_LUT_decode_loc[code]
                subpath = parent_path.copy() + [entry_name]

                if not is_symlink:
                    if is_dir:
                        self.do_prepare_custom_data_pool(sub_dict,subpath)
                    else:
                        self.custom_data_pool[self.custom_data_pool_index]=[items_list,sep.join(subpath)]
                        self.custom_data_pool_index += 1
            except Exception as e:
                self.log.error('do_prepare_custom_data_pool error::%s',e )
                print(e,items_list)

    def prepare_custom_data_pool(self):
        self.custom_data_pool = {}
        self.custom_data_pool_index = 0
        self.do_prepare_custom_data_pool(self.db.data,[])

    def extract_custom_data(self,cde_list):
        scan_path = self.db.scan_path

        self.files_cde = 0 #custom data extracted info
        self.files_cde_not = 0
        self.files_cde_size = 0

        self.db.cde_list = cde_list
        self.db.cd_stat=[0]*len(self.db.cde_list)

        for key,[list_ref,subpath] in self.custom_data_pool.items():
            if self.abort_action:
                break

            #print(key,list_ref,subpath)
            full_file_path = normpath(abspath(sep.join([scan_path,subpath])))
            #full_file_path_protected = f'"{full_file_path}"'
            #print(full_file_path_protected)

            size = list_ref[1]
            matched = False

            rule_nr=-1
            for expressions,use_smin,smin_int,use_smax,smax_int,executable in cde_list:
                rule_nr+=1

                if self.abort_action:
                    break

                if matched:
                    break

                if use_smin:
                    if size<smin_int:
                        self.files_cde_not += 1
                        #print('min skipped',size,smin_int,subpath)
                        continue
                if use_smax:
                    if size>smax_int:
                        self.files_cde_not += 1
                        #print('max skipped',size,smax_int,subpath)
                        continue

                for expr in expressions.split(','):
                    if matched:
                        break

                    #print(full_file_path,expr)
                    if fnmatch.fnmatch(full_file_path,expr):
                        try:
                            cde_run_list = executable.split() + [full_file_path]
                            #print(cde_run_list)
                            result = subprocess.run(cde_run_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)
                            #text=True,
                            #, encoding="ISO-8859-1"
                        except Exception as e:
                            print(full_file_path,e)
                            self.log.error('Custom Data Extraction subprocess error:%s\n%s',cde_run_list,e )
                            list_ref.append(e)
                        else:

                            result1 = str(result.stdout).strip()
                            result2 = str(result.stderr).strip()

                            #print(result1)
                            #print(result2)
                            #result1_compressed = zlib.compress(bytes(result1,"utf-8"))
                            #print(f'compare:{len(result1)} vs {len(result1_compressed)}')
                            #result1 = result1_compressed

                            if result1!='':
                                if result2!='':
                                    list_ref.append(result1 + '\n' + result2)
                                else:
                                    list_ref.append(result1)

                            matched = True
                            #list_ref.append(rule_nr)
                            self.db.cd_stat[rule_nr]+=1

            if matched:
                self.files_cde += 1
            else:
                self.files_cde_not += 1

            self.files_cde_size += size

        del self.custom_data_pool

        file_path=sep.join([self.db_dir,self.file_name()])
        self.log.info('saving %s' % file_path)

        with gzip.open(file_path, "wb") as gzip_file:
            pickle.dump(self.db, gzip_file)

        for rule,stat in zip(self.db.cde_list,self.db.cd_stat):
            print(rule,stat)

    def find_items_rec(self,
            size_min,size_max,name_func_to_call,cd_func_to_call,
            local_dict,parent_path_components=[]):

        entry_LUT_decode_loc = entry_LUT_decode

        #print('  find_items_rec',func_to_call,parent_path_components)
        for name,val in local_dict.items():
            len_val = len(val)
            if len_val==4:
                code,size,mtime,sub_dict=val
                cd=None
            elif len_val==5:
                code,size,mtime,sub_dict,cd=val
            else:
                self.log.error('find_items_rec error:%s',val )
                return

            is_dir,is_file,is_symlink = entry_LUT_decode_loc[code]

            if is_file:
                if size_min:
                    if size<size_min:
                        continue
                if size_max:
                    if size>size_max:
                        continue

            if is_dir :
                #katalog moze spelniac kryteria naazwy pliku, nie ma rozmiaru i custom data
                if name_func_to_call:
                    if name_func_to_call(name):
                        self.find_results.append(single_res)

                if sub_dict:
                    self.find_items_rec(
                        size_min,size_max,name_func_to_call,cd_func_to_call,
                        sub_dict,parent_path_components + [name])

            else:
                if name_func_to_call:
                    if not name_func_to_call(name):
                        continue

                if cd_func_to_call:
                    if cd:
                        try:
                            if not cd_func_to_call(cd):
                                continue
                        except Exception as e:
                            self.log.error('find_items_rec:%s on:\n%s',e,cd )
                            continue
                    else:
                        continue

                single_res = parent_path_components.copy() + [name]
                self.find_results.append(single_res)

    def find_items(self,
            size_min,size_max,
            name_func_to_call,cd_func_to_call):

        self.find_results = []

        local_dict = self.db.data
        parent_path_components = []

        self.find_items_rec(size_min,size_max,name_func_to_call,cd_func_to_call,local_dict,parent_path_components)

        return self.find_results

    def save(self,db_dir) :
        file_name=self.file_name()
        file_path=sep.join([db_dir,file_name])
        self.log.info('saving %s' % file_path)

        with gzip.open(file_path, "wb") as gzip_file:
            pickle.dump(self.db, gzip_file)

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

        #self.info_max_quant = 0
        #self.info_max_size = 0
        #self.info_curr_quant = 0
        #self.info_curr_size = 0

        self.records_to_show=[]
        self.abort_action=False

    def create(self,label='',path=''):
        new_record = LibrerCoreRecord(label,path,self.log)

        self.records.add(new_record)
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

        #self.info_max_quant = 0
        #self.info_max_size = 0
        info_curr_quant = 0
        info_curr_size = 0

        for ename,size in sorted(self.record_files_list):
            if self.abort_action:
                break

            self.log.info('db:%s',ename)
            new_record = self.create()

            self.info_line = f'loading {ename} ...'

            info_curr_quant+=1
            info_curr_size+=size

            if new_record.load(self.db_dir,ename) :
                self.log.warning('removing:%s',ename)
                self.records.remove(new_record)
            else:
                self.records_to_show.append( (new_record,info_curr_quant,info_curr_size) )


    def find_items_in_all_records_check(self,
            size_min,size_max,
            name_expr,name_regexp,name_case_sens,
            cd_expr,cd_regexp,cd_case_sens):

        if name_expr and name_regexp:
            if res := test_regexp(name_expr):
                return res

        if cd_expr and cd_regexp:
            if res := test_regexp(cd_expr):
                return res

        return None

    def find_items_in_all_records(self,
            range_par,
            size_min,size_max,
            name_expr,name_regexp,name_case_sens,
            cd_expr,cd_regexp,cd_case_sens):

        #print('find_items_in_all_records:',size_min,size_max,name_expr,name_regexp,name_case_sens,cd_expr,cd_regexp,cd_case_sens)
        if name_expr:
            if name_case_sens:
                if name_regexp:
                    name_func_to_call = lambda x : search(name_expr,x)
                else:
                    name_func_to_call = lambda x : fnmatch.fnmatch(x,name_expr)
            else:
                if name_regexp:
                    name_func_to_call = lambda x : search(name_expr,x,re.IGNORECASE)
                else:
                    name_func_to_call = lambda x : re.compile(fnmatch.translate(name_expr), re.IGNORECASE).match(x)


        else:
            name_func_to_call = None

        if cd_expr:
            if cd_case_sens:
                if cd_regexp:
                    cd_func_to_call = lambda x : search(cd_expr,x)
                else:
                    cd_func_to_call = lambda x : fnmatch.fnmatch(x,cd_expr)
            else:
                if cd_regexp:
                    cd_func_to_call = lambda x : search(cd_expr,x,re.IGNORECASE)
                else:
                    cd_func_to_call = lambda x : re.compile(fnmatch.translate(cd_expr), re.IGNORECASE).match(x)
        else:
            cd_func_to_call = None


        #re.IGNORECASE


        #name_expr_used = name_expr if name_case_sens else name_expr.lower()

        ##name_func_to_call = None if not name_expr else ( lambda x : search(name_expr_used,x) ) if name_regexp else ( lambda x : fnmatch(x,name_expr) )
        #name_func_to_call_case = if name_case_sens else name_func_to_call

        #cd_func_to_call = None if not cd_expr else ( lambda x : search(cd_expr,x) ) if cd_regexp else ( lambda x : fnmatch(x,cd_expr) )

        #self.find_res = defaultdict(set)
        self.find_res = []
        sel_range = [range_par] if range_par else self.records

        for record in sel_range:
            sub_res = record.find_items(
                size_min,size_max,
                name_func_to_call,
                cd_func_to_call)
            if sub_res:
                for single_res in sub_res:
                    #self.find_res[record].add( single_res )
                    self.find_res.append( (record,single_res) )

        #self.find_res
        #return tuple(res)
        return None

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



