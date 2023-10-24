from os import scandir
from os import stat
from os import sep
from os.path import join as path_join
from time import time

import gzip
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

class LibrerCoreData :
    time = None
    path = None
    data = None
    scanned = False
    files = 0
    folders = 0
    size = 0
    label = ""

    def __init__(self,label,path):
        self.time = int(1000*time())
        self.path = path
        self.scanned = False
        self.data = {}
        self.files = 0
        self.files_cde = 0
        self.folders = 0
        self.size = 0
        self.label=label

    def get_time(self):
        return self.time/1000

class LibrerCoreElement :
    db = None
    file_name = ''

    def __init__(self,label,path,log):
        self.db = LibrerCoreData(label,path)
        self.log = log
        self.find_results = []
        self.info_line = ''

    def abort():
        print('abort')
        pass

    def do_scan(self, path, dictionary) :
        folder_size=0
        try:
            with scandir(path) as res:
                folder_counter = 0

                for entry in res:
                    entry_name = entry.name

                    is_dir,is_file,is_symlink = entry.is_dir(),entry.is_file(),entry.is_symlink()

                    try:
                        stat_res = stat(entry)
                    except Exception as e:
                        self.log.error('stat error:%s', e )
                        #size -1 <=> error, dev,in ==0
                        dictionary[entry_name] = (is_dir,is_file,is_symlink,-1,0,None,None,None)
                    else:
                        dev = stat_res.st_dev
                        ino = stat_res.st_ino

                        if is_dir:
                            if is_symlink :
                                new_level = (is_dir,is_file,is_symlink,0,stat_res.st_mtime_ns,None,ino,dev)
                                #self.log.warning(f'skippping directory link: {path} / {entry_name}')
                            else:
                                new_dict={}
                                sub_level_size=self.do_scan(path_join(path,entry_name),new_dict)
                                new_level = (is_dir,is_file,is_symlink,sub_level_size,stat_res.st_mtime_ns,new_dict,ino,dev)
                                folder_size += sub_level_size
                        else:
                            if is_symlink :
                                new_level = (is_dir,is_file,is_symlink,0,stat_res.st_mtime_ns,None,ino,dev)
                                #self.log.warning(f'skippping file link: {path} / {entry_name}')
                            else:
                                size = stat_res.st_size
                                new_level = (is_dir,is_file,is_symlink,size,stat_res.st_mtime_ns,None,ino,dev)
                                folder_size += size

                            folder_counter += 1

                        dictionary[entry_name]=new_level

                self.db.size += folder_size
                #print(f'self.db.size:{bytes_to_str(self.db.size)}')
                self.db.files += folder_counter

        except Exception as e:
            self.log.error('scandir error:%s',e )

        return folder_size

    def scan (self,db_dir):
        self.db.size=self.do_scan(self.db.path,self.db.data)
        self.db_dir = db_dir
        self.save(db_dir)
        self.prepare_custom_info_pool()

    def do_prepare_custom_info_pool(self,dictionary,parent_path):
        #print('do_prepare_custom_info_pool',parent_path,dictionary.items())
        for entry_name,(is_dir,is_file,is_symlink,size,mtime,sub_dictionary,inode,dev) in dictionary.items():
            subpath = parent_path.copy() + [entry_name]

            if not is_symlink:
                if is_dir:
                    self.do_prepare_custom_info_pool(sub_dictionary,subpath)
                else:
                    self.custom_info_pool[(inode,dev)] = sep.join(subpath)

    def prepare_custom_info_pool(self):
        self.custom_info_pool = {}
        self.do_prepare_custom_info_pool(self.db.data,[])

    def processs_custom_info(self,script):
        self.cimax = len(self.custom_info_pool)
        print('processs_custom_info',script,self.cimax)

        self.custom_info = {}
        for key,val in self.custom_info_pool.items():
            self.db.files_cde += 1
            #print(key,val)
            result = subprocess.run([script,val], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            result1 = result.stdout
            result2 = result.stderr

            if result1!='':
                if result2!='':
                    self.custom_info[key] = (result1,result2)
                else:
                    self.custom_info[key] = (result1)

                #print(key,self.custom_info[key],'\n')


        file_name=self.get_cd_file_name()
        file_path=sep.join([self.db_dir,file_name])
        print('saving %s' % file_path)

        with gzip.open(file_path, "wb") as gzip_file:
            pickle.dump(self.custom_info, gzip_file)

        print(self.custom_info)

    def find_items_rec(self,func_to_call,local_dict,parent_path_components=[]):
        for name,(is_dir,is_file,is_symlink,size,mtime,sub_dictionary) in local_dict.items():
            if func_to_call(name):
                single_res = parent_path_components.copy()
                single_res.append(name)

                self.find_results.append(single_res)
            elif is_dir and sub_dictionary:
                self.find_items_rec(func_to_call,sub_dictionary,parent_path_components + [name])

    def find_items(self,func_to_call):
        self.find_results = []

        local_dict = self.db.data
        parent_path_components = []

        self.find_items_rec(func_to_call,local_dict,parent_path_components)

        return self.find_results

    def get_cd_file_name(self):
        return f'{self.db.time}.cd.dat'

    def get_file_name(self):
        return f'{self.db.time}.dat'


    def save(self,db_dir) :
        self.file_name=self.get_file_name()
        file_path=sep.join([db_dir,self.file_name])
        print('saving %s' % file_path)

        with gzip.open(file_path, "wb") as gzip_file:
            pickle.dump(self.db, gzip_file)

    def load(self,db_dir,file_name="data.gz"):
        self.log.info('loading %s' % file_name)
        try:
            full_file_path = sep.join([db_dir,file_name])
            with gzip.open(full_file_path, "rb") as gzip_file:
                self.db = pickle.load(gzip_file)

            self.file_name = file_name
        except Exception as e:
            print('loading error:%s' % e )
            return True
        else:
            return False

class LibrerCore:
    records = set()
    db_dir=''

    def __init__(self,db_dir,log):
        self.records = set()
        self.db_dir = db_dir
        self.log=log
        self.info_line = ''

    def create(self,label='',path=''):
        new_element = LibrerCoreElement(label,path,self.log)
        self.records.add(new_element)
        return new_element

    def read_list(self,callback=None):

        self.log.info('read_list: %s',self.db_dir)
        try:
            with scandir(self.db_dir) as res:
                for entry in res:
                    self.log.info('db:%s',entry.name)
                    new_element = self.create()

                    if new_element.load(self.db_dir,entry.name) :
                        self.log.warning('removing:%s',entry.name)
                        self.records.remove(new_element)
                    else:
                        callback(new_element)

        except Exception as e:
            self.log.error('list read error:%s' % e )
        else:
            pass

    def find_items_in_all_records(self,func_to_call):
        res = []
        for record in self.records:
            sub_res = record.find_items(func_to_call)
            if sub_res:
                for single_res in sub_res:
                    res.append( (record,single_res) )

        return tuple(res)

