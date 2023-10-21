from os import scandir
from os import stat
from os import sep
from os.path import join as path_join
from time import time
#from time import localtime

import gzip
import pickle

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
        files = 0
        folders = 0
        size = 0
        self.label=label

    def get_time(self):
        return self.time/1000

class LibrerCoreElement :
    db = None
    #info_size_sum = 0
    #info_counter = 0
    info_line = ''
    file_name = ''
    #size = 0

    def __init__(self,label,path,log):
        self.db = LibrerCoreData(label,path)
        self.log = log

    def abort():
        print('abort')
        pass

    def do_scan(self, path, dictionary) :
        #print(path,type(dictionary))

        folder_size=0
        try:
            with scandir(path) as res:
                folder_counter = 0

                for entry in res:
                    try:
                        stat_res = stat(entry)
                    except Exception as e:
                        self.log.error('stat error:%s', e )
                    else:
                        is_dir = entry.is_dir()
                        is_file = entry.is_file()
                        is_symlink = entry.is_symlink()
                        size = stat_res.st_size

                        if is_dir:
                            if is_symlink :
                                new_level = (is_dir,is_file,is_symlink,0,stat_res.st_mtime_ns,None)
                                self.log.warning(f'skippping directory link: {path} / {entry.name}')
                            else:
                                new_dict=dict()
                                sub_level_size=self.do_scan(path_join(path,entry.name),new_dict)
                                new_level = (is_dir,is_file,is_symlink,sub_level_size,stat_res.st_mtime_ns,new_dict)
                                folder_size += sub_level_size
                        else:
                            if is_symlink :
                                new_level = (is_dir,is_file,is_symlink,0,stat_res.st_mtime_ns,None)
                                self.log.warning(f'skippping file link: {path} / {entry.name}')
                            else:
                                new_level = (is_dir,is_file,is_symlink,size,stat_res.st_mtime_ns,None)
                                folder_size += size

                            folder_counter += 1

                        dictionary[entry.name]=new_level

                self.db.size += folder_size
                self.db.files += folder_counter

        except Exception as e:
            self.log.error('scandir error:%s',e )

        return folder_size

    def get_file_name(self):
        return f'{self.db.time}.dat'

    def scan (self,db_dir):
        self.db.size=self.do_scan(self.db.path,self.db.data)
        self.save(db_dir)

    def save(self,db_dir) :
        self.file_name=self.get_file_name()
        file_path=sep.join([db_dir,self.file_name])
        print('saving %s' % file_path)

        with gzip.open(file_path, "wb") as gzip_file:
            pickle.dump(self.db, gzip_file)

        #return file_path

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

    #import json  # Do ładnego wyświetlenia struktury
    #print(json.dumps(loaded_data, indent=2))

class LibrerCore:
    records = set()
    db_dir=''
    info_line = ''

    def __init__(self,db_dir,log):
        self.records = set()
        self.db_dir = db_dir
        self.log=log

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

                    #try:
                    #    stat_res = stat(entry)
                    #    #print(type(stat_res))
                    #except Exception as e:
                    #    print('scandir(stat):%s error:%s',entry.name,e )
                    #else:
        except Exception as e:
            self.log.error('list read error:%s' % e )
        else:
            pass

    #def set_path_to_scan(self, path):
    #    self.new_path = path

    #def scan(self):
    #    print('pre-self.cores:',len(self.records))
    #    self.info_size_sum = self.new_core.info_size_sum
    #    self.info_counter = self.new_core.info_counter
    #    self.info_line = self.new_core.info_line

    #    self.new_element.scan(self.new_path)
    #    new_core=None
    #    print('post-self.cores:',len(self.cores))



#    main_dict=dict()
#    do_scan('.',main_dict)

#kor = core()
#kor.scan('.')
#kor.save('test1.dat')
#kor.load('test1.dat')
