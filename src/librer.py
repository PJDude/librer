#!/usr/bin/python3

####################################################################################
#
#  Copyright (c) 2023-2025 Piotr Jochymek
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

from os import sep,system,getcwd,name as os_name,cpu_count
from os.path import abspath,normpath,basename,splitext as path_splitext,dirname,join as path_join,isfile as path_isfile,exists as path_exists,isdir
from gc import disable as gc_disable, enable as gc_enable,collect as gc_collect,set_threshold as gc_set_threshold, get_threshold as gc_get_threshold

from pathlib import Path
from time import strftime,time,mktime
from signal import signal,SIGINT

from tkinter import Toplevel,PhotoImage,Menu,Label,LabelFrame,Frame,StringVar,BooleanVar,IntVar
from tkinter.ttk import Treeview,Checkbutton,Radiobutton,Scrollbar,Button,Menubutton,Entry,Scale,Style,Combobox
from tkinter.filedialog import askdirectory,asksaveasfilename,askopenfilename,askopenfilenames

from tkinterdnd2 import DND_FILES, TkinterDnD

from threading import Thread
from traceback import format_stack
import sys
import logging
from shutil import rmtree
from collections import defaultdict

from pickle import dumps, loads
from dateparser import parse as parse_datetime

from zstandard import ZstdCompressor,ZstdDecompressor
from psutil import disk_partitions
from librer_images import librer_image

from dialogs import *
from core import *
from text import LANGUAGES

from tempfile import mkdtemp

windows = bool(os_name=='nt')

langs=LANGUAGES()

STR=langs.STR

if windows:
    from os import startfile
    from win32api import GetVolumeInformation

l_info = logging.info
l_warning = logging.warning
l_error = logging.error

###########################################################################################################################################

CFG_THEME='theme'

CFG_KEY_CDE_SETTINGS = 'cde_settings'
CFG_KEY_SINGLE_DEVICE = 'single_device'

CFG_KEY_SINGLE_DEVICE = 'single_device'

CFG_KEY_find_size_min = 'find_size_min'
CFG_KEY_find_size_max = 'find_size_max'

CFG_KEY_find_modtime_min = 'find_modtime_min'
CFG_KEY_find_modtime_max = 'find_modtime_max'

CFG_KEY_find_range_all = 'find_range_all'
CFG_KEY_type_folders = 'find_type_folders'
CFG_KEY_type_files = 'find_type_files'
CFG_KEY_find_cd_search_kind = 'find_cd_search_kind'
CFG_KEY_find_filename_search_kind = 'find_filename_search_kind'

CFG_KEY_find_name_regexp = 'find_name_regexp'
CFG_KEY_find_name_glob = 'find_name_glob'
CFG_KEY_find_name_fuzz = 'find_name_fuzz'
#CFG_KEY_find_name_regexp = 'name_regexp'
CFG_KEY_find_name_case_sens = 'name_case_sens'

CFG_KEY_find_cd_regexp = 'find_cd_regexp'
CFG_KEY_find_cd_glob = 'find_cd_glob'
CFG_KEY_find_cd_fuzz = 'find_cd_fuzz'
CFG_KEY_find_cd_case_sens = 'cd_case_sens'

CFG_KEY_filename_fuzzy_threshold = 'filename_fuzzy_threshold'
CFG_KEY_cd_fuzzy_threshold = 'cd_fuzzy_threshold'

CFG_KEY_SEARCH_TXT_STRING = 'search_txt_string'
CFG_KEY_SEARCH_TXT_CS = 'search_txt_cs'

CFG_LANG = 'lang'

CFG_last_dir = 'last_dir'
CFG_geometry = 'geometry'
CFG_geometry_search = 'geometry_search'
CFG_SORTING = 'sorting'
CFG_SORTING_RESULTS = 'sorting_results'
CFG_KEY_show_popups = 'show_popups'
CFG_KEY_groups_collapse = 'groups_collapse'
CFG_KEY_include_hidden = 'include_hidden'
CFG_KEY_select_found = 'select_found'
CFG_KEY_after_action = 'after_search'
CFG_KEY_expand_search_results = 'expand_search_results'

cfg_defaults={
    CFG_THEME:'Vista' if windows else 'Clam',
    CFG_KEY_SINGLE_DEVICE:True,
    CFG_KEY_CDE_SETTINGS:[],

    CFG_KEY_find_range_all:False,
    CFG_KEY_type_folders:True,
    CFG_KEY_type_files:True,
    CFG_KEY_find_filename_search_kind:'dont',
    CFG_KEY_find_cd_search_kind:'dont',

    CFG_KEY_find_size_min:'',
    CFG_KEY_find_size_max:'',

    CFG_KEY_find_modtime_min:'',
    CFG_KEY_find_modtime_max:'',

    CFG_KEY_find_name_regexp:'',
    CFG_KEY_find_name_glob:'',
    CFG_KEY_find_name_fuzz:'',
    CFG_KEY_find_name_case_sens:not windows,

    CFG_KEY_find_cd_regexp:'',
    CFG_KEY_find_cd_glob:'',
    CFG_KEY_find_cd_fuzz:'',
    CFG_KEY_find_cd_case_sens:False,

    CFG_KEY_filename_fuzzy_threshold:'0.95',
    CFG_KEY_cd_fuzzy_threshold:'0.95',

    CFG_KEY_SEARCH_TXT_STRING:'',
    CFG_KEY_SEARCH_TXT_CS:False,
    CFG_LANG:'English',

    CFG_last_dir:'.',
    CFG_geometry:'',
    CFG_geometry_search:'',
    CFG_KEY_show_popups:True,
    CFG_KEY_groups_collapse:True,
    CFG_KEY_include_hidden:False,
    CFG_KEY_select_found:False,
    CFG_KEY_after_action:1,
    CFG_KEY_expand_search_results:False
}

HOMEPAGE='https://github.com/PJDude/librer'

class Config:
    def __init__(self,config_dir):
        self.cfg = {}

        self.path = config_dir
        self.file = self.path + '/cfg'

    def write(self):
        l_info('writing config')
        Path(self.path).mkdir(parents=True,exist_ok=True)

        with open(self.file, "wb") as f:
            f.write(ZstdCompressor(level=8,threads=1).compress(dumps(self.cfg)))

    def read(self):
        l_info('reading config')
        if path_isfile(self.file):
            try:
                with open(self.file, "rb") as f:
                    self.cfg = loads(ZstdDecompressor().decompress(f.read()))

            except Exception as e:
                l_error(e)
        else:
            l_warning('no config file: %s',self.file)
            l_info('setting defaults')
            #use,mask,smin,smax,exe,pars,shell,timeout,crc

            if windows:
                line_list1  = ['0','*.7z,*.zip,*.bz2,*.xz,*.z,*.gzip,*.iso,*.rar,*.arj,*.lzh,*.lzma,*.vdi,*.vhd','','','C:\\Program Files\\7-Zip\\7z.exe','l %','0','10','0']
                line_list1a = ['0','*.rar','','','C:\\Program Files\\WinRAR\\UnRAR.exe','l %','0','10','0']
                line_list2 =  ['0','*.txt,*.nfo','1','256kB','more %','','1','5','0']
                line_list3 =  ['0','*.pls,*.m3u,*.cue,*.plp,*.m3u8,*.mpcpl','','','more %','','1','5','0']
                line_list4 =  ['0','*.aac,*.ac3,*.aiff,*.dts,*.dtshd,*.flac,*.h261,*.h263,*.h264,*.iff,*.m4v,*.matroska,*.mpc,*.mp3,*.mp4,*.mpeg,*.mkv,*.ts,*.ogg,*.wav,*.wv','','','ffprobe.exe','-hide_banner %','0','5','0']
                line_list4a = ['0','*.mp3,*.mp4,*.mpeg,*.mkv','','','MediaInfo.exe','%','0','5','0']
                line_list5 =  ['0','*.jpg','','','exiftool.exe','%','0','5','0']
                line_list5a = ['0','*.exe','','','exiftool.exe','%','0','5','0']
                line_list6 =  ['0','*.tar,*.tgz,*.tar.gz,*.tar.bz2,*.tbz,*.tar.xz','','','tar','tvf %','0','60','0']
                line_list7 =  ['0','*.pdf','','','pdftotext.exe','-f 0 -l 3 -layout % -','0','10','0']

                cde_sklejka_list=[line_list1,line_list1a,line_list2,line_list3,line_list4,line_list4a,line_list5,line_list5a,line_list6,line_list7]
            else:
                line_list1 =  ['0','*.7z,*.zip,*.bz2,*.xz,*.z,*.gzip,*.iso,*.rar,*.arj,*.lzh,*.lzma,*.vdi,*.vhd','','','7z','l %','0','10','0']
                line_list2 =  ['0','*.txt,*.nfo','1','256kB','cat','%','0','5','0']
                line_list3 =  ['0','*.pls,*.m3u,*.cue,*.plp,*.m3u8,*.mpcpl','','','cat','%','0','5','0']
                line_list4 =  ['0','*.aac,*.ac3,*.aiff,*.dts,*.dtshd,*.flac,*.h261,*.h263,*.h264,*.iff,*.m4v,*.matroska,*.mpc,*.mp3,*.mp4,*.mpeg,*.mkv,*.ts,*.ogg,*.wav,*.wv','','','ffprobe','-hide_banner %','0','5','0']
                line_list5 =  ['0','*.jpg','','','exif','%','0','5','0']
                line_list6 =  ['0','*.tar,*.tgz,*.tar.gz,*.tar.bz2,*.tbz,*.tar.xz','','','tar','tvf %','0','60','0']
                line_list7 =  ['0','*.pdf','','','pdftotext','-f 0 -l 3 -layout % -','0','10','0']

                cde_sklejka_list=[line_list1,line_list2,line_list3,line_list4,line_list5,line_list6,line_list7]
            self.set(CFG_KEY_CDE_SETTINGS,cde_sklejka_list)
            self.write()

    def set(self,key,val):
        self.cfg[key]=val
        return val

    def get(self,key):
        try:
            res=self.cfg[key]
        except Exception as e:
            l_warning('gettting config key: %s',key)
            l_warning(e)

            res=cfg_defaults[key]

            self.cfg[key]=res

        return res

###########################################################

class Gui:
    block_processing_stack=['init']

    block_processing_stack_append = block_processing_stack.append
    block_processing_stack_pop = block_processing_stack.pop

    ################################################
    def processing_off(self,caller_id=None):
        #print('processing_off',self.block_processing_stack,caller_id)
        gc_disable()
        self.block_processing_stack_append(caller_id)

        disable = lambda menu : self.menubar_entryconfig(menu, state="disabled")

        _ = {disable(menu) for menu in (STR("File"),STR("Help")) }

        self.menubar_config(cursor='watch')
        self.main_config(cursor='watch')

    ################################################
    def processing_on(self):
        #print('processing_on',self.block_processing_stack)
        self.block_processing_stack_pop()

        if not self.block_processing_stack:
            norm = lambda menu : self.menubar_entryconfig(menu, state="normal")

            _ = {norm(menu) for menu in (STR("File"),STR("Help")) }

            self.main_config(cursor='')
            self.menubar_config(cursor='')
            gc_collect()
            gc_enable()

    ################################################
    def block_and_log(func):
        def block_and_log_wrapp(self,*args,**kwargs):
            self.processing_off(f'b&l_wrapp:{func.__name__}')
            l_info("b&l '%s' start",func.__name__)

            try:
                res=func(self,*args,**kwargs)
            except Exception as e:
                self.status('block_and_log_wrapp func:%s error:%s args:%s kwargs:%s' % (func.__name__,e,args,kwargs) )
                l_error('block_and_log_wrapp func:%s error:%s args:%s kwargs: %s',func.__name__,e,args,kwargs)
                l_error(''.join(format_stack()))
                self.info_dialog_on_main.show('INTERNAL ERROR block_and_log_wrapp',f'{func.__name__}\n' + str(e))
                res=None

            self.processing_on()

            l_info("b&l '%s' end",func.__name__)
            return res
        return block_and_log_wrapp
    ################################################
    def block(func):
        def block_wrapp(self,*args,**kwargs):
            self.processing_off(f'block_wrapp:{func.__name__}')

            try:
                res=func(self,*args,**kwargs)
            except Exception as e:
                self.status('block_wrapp func:%s error:%s args:%s kwargs:%s' % (func.__name__,e,args,kwargs) )
                l_error('block_wrapp func:%s error:%s args:%s kwargs: %s',func.__name__,e,args,kwargs)
                l_error(''.join(format_stack()))
                self.info_dialog_on_main.show('INTERNAL ERROR block_wrapp',f'{func.__name__}\n' + str(e))
                res=None

            self.processing_on()

            return res
        return block_wrapp
    ################################################

    def catched(func):
        def catched_wrapp(self,*args,**kwargs):
            try:
                res=func(self,*args,**kwargs)
            except Exception as e:
                self.status('catched_wrapp func:%s error:%s args:%s kwargs:%s' % (func.__name__,e,args,kwargs) )
                l_error('catched_wrapp func:%s error:%s args:%s kwargs: %s',func.__name__,e,args,kwargs)
                l_error(''.join(format_stack()))
                self.info_dialog_on_main.show('INTERNAL ERROR catched_wrapp','%s %s' % (func.__name__,str(e)) )
                res=None
            return res
        return catched_wrapp

    def logwrapper(func):
        def logwrapper_wrapp(self,*args,**kwargs):
            l_info("logwrapper '%s' start",func.__name__)
            start = time()
            try:
                res=func(self,*args,**kwargs)
            except Exception as e:
                self.status('logwrapper_wrapp func:%s error:%s args:%s kwargs:%s' % (func.__name__,e,args,kwargs) )
                l_error('logwrapper_wrapp func:%s error:%s args:%s kwargs: %s',func.__name__,e,args,kwargs)
                l_error(''.join(format_stack()))
                self.info_dialog_on_main.show('INTERNAL ERROR logwrapper_wrapp','%s %s' % (func.__name__,str(e)) )
                res=None

            l_info("logwrapper '%s' end. BENCHMARK TIME:%s",func.__name__,time()-start)
            return res
        return logwrapper_wrapp

    def restore_status_line(func):
        def restore_status_line_wrapp(self,*args,**kwargs):

            prev=self.status_curr_text
            try:
                res=func(self,*args,**kwargs)
            except Exception as e:
                self.status('restore_status_line_wrapp:%s:%s args:%s kwargs:%s' % (func.__name__,e,args,kwargs) )
                l_error('restore_status_line_wrapp:%s:%s args:%s kwargs:%s',func.__name__,e,args,kwargs)
                l_error(''.join(format_stack()))
                self.info_dialog_on_main.show('INTERNAL ERROR restore_status_line_wrapp',str(e))
                res=None
            else:
                self.status(prev)

            return res
        return restore_status_line_wrapp

    def __init__(self,cwd):
        gc_disable()

        self.cfg = Config(DATA_DIR)
        self.cfg.read()
        self.cfg_get=self.cfg.get
        langs.set( self.cfg_get(CFG_LANG) )

        self.cwd=cwd

        self.last_dir = self.cfg_get(CFG_last_dir).replace('/',sep)

        signal(SIGINT, lambda a, k : self.handle_sigint())

        self.main_locked_by_child=None
        ####################################################################
        self_main = self.main = TkinterDnD.Tk()

        self_main.drop_target_register(DND_FILES)
        self_main.dnd_bind('<<Drop>>', lambda e: self.main_drop(e.data) )

        self.main_config = self.main.config

        self_main.title(f'Librer {VER_TIMESTAMP}')
        self_main.protocol("WM_DELETE_WINDOW", self.delete_window_wrapper)
        self_main.withdraw()

        self.main_update = self_main.update
        self.main_update()

        self_main.minsize(800, 600)

        if self_main.winfo_screenwidth()>=1600 and self_main.winfo_screenheight()>=1024:
            self_main.geometry('1200x800')
        elif self_main.winfo_screenwidth()>=1200 and self_main.winfo_screenheight()>=800:
            self_main.geometry('1024x768')

        self_ico = self.ico = { img:PhotoImage(data = img_data) for img,img_data in librer_image.items() }

        self.hg_index = 0
        hg_indices=('01','02','03','04','05','06','07','08', '11','12','13','14','15','16','17','18', '21','22','23','24','25','26','27','28', '31','32','33','34','35','36','37','38',)
        self.hg_ico={ i:self_ico[str('hg'+j)] for i,j in enumerate(hg_indices) }

        self.hg_ico_len = len(self.hg_ico)

        self.ico_record_new = self_ico['record_new']
        self.ico_record_delete = self_ico['record_delete']
        self.ico_record_raw = self_ico['record_raw']
        self.ico_record_pure = self_ico['record_pure']
        self.ico_record_import = self_ico['record_import']
        self.ico_record_export = self_ico['record_export']
        self.ico_record_raw_cd = self_ico['record_raw_cd']
        self.ico_record = self_ico['record']
        self.ico_records_all = self_ico['records_all']
        self.ico_record_cd = self_ico['record_cd']
        self.ico_record_cd_loaded = self_ico['record_cd_loaded']
        self.ico_cd_ok = self_ico['cd_ok']
        self.ico_cd_ok_crc = self_ico['cd_ok_crc']
        self.ico_cd_error = self_ico['cd_error']
        self.ico_cd_error_crc = self_ico['cd_error_crc']

        self.ico_cd_aborted = self_ico['cd_aborted']
        self.ico_cd_empty = self_ico['cd_empty']

        self.ico_crc = self_ico['crc']
        self.ico_license = self_ico['license']
        self.ico_timeout = self_ico['timeout']
        self.ico_smaller = self_ico['smaller']
        self.ico_bigger = self_ico['bigger']
        self.ico_test_col = self_ico['test_col']
        self.ico_shell = self_ico['shell']
        self.ico_search_text = self_ico['search_text']
        self.ico_left = self_ico['left']
        self.ico_right = self_ico['right']

        self.ico_find = self_ico['find']
        self.ico_start = self_ico['start']
        self.ico_stop = self_ico['stop']
        self.ico_abort = self_ico['abort']

        self.ico_folder = self_ico['folder']
        self.ico_folder_link = self_ico['folder_link']
        self.ico_folder_error = self_ico['folder_error']
        self.ico_warning = self_ico['warning']
        self.ico_empty = self_ico['empty']
        self.ico_cancel = self_ico['cancel']
        self.ico_open = self_ico['open']
        self.ico_drive = self_ico['drive']
        self.ico_up = self_ico['up']
        self.ico_info = self_ico['info']
        self.ico_group = self_ico['group']
        self.ico_group_new = self_ico['group_new']
        self.ico_group_remove = self_ico['group_delete']
        self.ico_group_assign = self_ico['group_assign']

        #self.ico_delete = self_ico['delete']

        self_ico_librer = self.ico_librer = self_ico['librer']
        self.ico_librer_small = self_ico['librer_small']
        self.ico_test = self_ico['test']

        #self_main.iconphoto(True, self_ico_librer,self.ico_record)
        self_main.iconphoto(True, self_ico_librer,self.ico_librer_small)

        self.main_icon_tuple = (self.ico_librer,self.ico_librer_small)

        self.RECORD_RAW='r'
        self.RECORD='R'
        self.DIR='D'
        self.DIRLINK='L'
        self.LINK='l'
        self.FILE='F'
        self.FILELINK='l'

        self.SYMLINK='S'

        self.FOUND = 'X'

        self.GROUP = 'z'

        #self.defaultFont = font.nametofont("TkDefaultFont")
        #self.defaultFont.configure(family="Monospace regular",size=8,weight=font.BOLD)
        #self.defaultFont.configure(family="Monospace regular",size=10)
        #self_main.option_add("*Font", self.defaultFont)

        self_tooltip = self.tooltip = Toplevel(self_main)
        self.tooltip_withdraw = self_tooltip.withdraw
        self.tooltip_withdraw()
        self.tooltip_deiconify = self_tooltip.deiconify
        self.tooltip_wm_geometry = self_tooltip.wm_geometry

        self.tooltip.wm_overrideredirect(True)
        self.tooltip_lab=Label(self_tooltip, justify='left', background="#ffffe0", relief='solid', borderwidth=0, wraplength = 1200)

        try:
            self.tooltip_lab.configure(font=('Courier', 10))
        except:
            try:
                self.tooltip_lab.configure(font=('TkFixedFont', 10))
            except:
                pass

        self.tooltip_lab.pack(ipadx=1)
        self.tooltip_lab_configure = self.tooltip_lab.configure

        ####################################################################
        themes_names= ['Clam', 'Alt']
        if windows:
            themes_names = ['Vista','Winnative'] + themes_names

        #print('themes_names:',themes_names)
        self.themes_combos={}

        for name in themes_names:
            for darkness,darknesscode in (('',0),('Dark',1)):
                full_name = name + ((' ' + darkness) if darknesscode else '')
                self.themes_combos[full_name]=name.lower(),darknesscode

        self.default_theme='vista' if windows else 'clam'

        theme_name,black_theme=self.themes_combos.get(self.cfg_get(CFG_THEME),(self.default_theme,0))

        if black_theme:
            bg_focus='dark green'
            bg_sel='gray30'
            self.bg_content='black'
            self.fg_content='white'
            self.col_found='tomato'
            self.col_record='azure'
            self.col_record_raw='ghost white'
        else:
            bg_focus='pale green'
            bg_sel='#AAAAAA'
            self.bg_content='white'
            self.fg_content='black'
            self.col_found='red'
            self.col_record='green4'
            self.col_record_raw='gray'

        style = Style()

        try:
            style.theme_create("dummy", parent=theme_name )
        except Exception as e:
            print("cannot set theme - setting default")
            print(e)

            self.cfg.set(CFG_THEME,self.default_theme)

            sys_exit(1)

        self.bg_color = style.lookup('TFrame', 'background')

        style.theme_use("dummy")

        style_configure = style.configure

        style_configure("TButton", anchor = "center")
        style_configure("TButton", background = self.bg_color)

        style_configure("TCheckbutton", background = self.bg_color,anchor='center',padding=(10, 0, 10, 0),)

        style_map = style.map

        style_map("TCheckbutton",indicatorbackground=[("disabled",self.bg_color),('','white')],indicatorforeground=[("disabled",'darkgray'),('','black')],relief=[('disabled',"flat"),('',"sunken")],foreground=[('disabled',"gray"),('',"black")])

        style_configure('TRadiobutton', background=self.bg_color)
        style_configure('TMenubutton', background=self.bg_color)

        style_map("TButton", relief=[('disabled',"flat"),('',"raised")],foreground=[('disabled',"gray"),('',"black")] )

        style_map("TEntry", foreground=[("disabled",'darkgray'),('','black')],relief=[("disabled",'flat'),('','sunken')],borderwidth=[("disabled",0),('',2)],fieldbackground=[("disabled",self.bg_color),('','white')])

        style_map("Treeview.Heading", relief=[('','raised')] )

        self.rowhight=18
        style_configure("Treeview",rowheight=self.rowhight)
        style_configure("Treeview", fieldbackground=self.bg_content,background = self.bg_color,borderwidth=0,foreground=self.fg_content)

        style_configure("TScale", background=self.bg_color)
        style_configure('TScale.slider', background=self.bg_color)
        style_configure('TScale.Horizontal.TScale', background=self.bg_color)

        style_map('Treeview', background=[('focus',bg_focus),('selected',bg_sel),('',self.bg_content)] )

        if windows:
            #fix border problem ...
            style_configure("TCombobox",padding=1)

        style.element_create("Treeheading.border", "from", "default")
        style.layout("Treeview.Heading", [
            ("Treeheading.cell", {'sticky': 'nswe'}),
            ("Treeheading.border", {'sticky':'nswe', 'children': [
                ("Treeheading.padding", {'sticky':'nswe', 'children': [
                    ("Treeheading.image", {'side':'right', 'sticky':''}),
                    ("Treeheading.text", {'sticky':'we'})
                ]})
            ]}),
        ])

        style_configure("Treeview.Heading",background=self.bg_color, foreground="black", relief="groove")
        style_map("Treeview.Heading",relief=[('active','raised'),('pressed','sunken')])

        style_configure("Treeview",background=self.bg_color, relief="flat",borderwidth=0)

        #######################################################################
        menubar = self.menubar = Menu(self_main,bg=self.bg_color)
        self_main.config(menu=menubar)
        #######################################################################

        self.tooltip_message={}

        self.menubar_config = menubar.config
        self.menubar_cget = menubar.cget

        self.menubar_entryconfig = menubar.entryconfig
        self.menubar_norm = lambda x : self.menubar_entryconfig(x, state="normal")
        self.menubar_disable = lambda x : self.menubar_entryconfig(x, state="disabled")

        (status_frame := Frame(self_main,bg=self.bg_color)).pack(side='bottom', fill='both')

        self.status_records_all=Label(status_frame,image=self.ico_records_all,text='--',width=200,borderwidth=2,bg=self.bg_color,relief='groove',anchor='w')
        self.status_records_all.pack(fill='x',expand=0,side='left')
        self.status_records_all_configure = lambda x : self.status_records_all.configure(image = self.ico_records_all, text = x,compound='left')
        self.widget_tooltip(self.status_records_all,STR('All records in repository'))
        self.status_records_all.bind("<ButtonPress-1>", lambda event : self.unload_record() )
        self.status_records_all.bind("<Double-Button-1>", lambda event : self.unload_all_recods() )

        self.status_record=Label(status_frame,image=self.ico_empty,text='--',width=200,borderwidth=2,bg=self.bg_color,relief='groove',anchor='w')
        self.status_record.pack(fill='x',expand=0,side='left')
        self.status_record_configure = lambda x : self.status_record.configure(image = self.ico_record, text = x,compound='left')

        self.widget_tooltip(self.status_record,'Selected record')
        self.status_record.bind("<ButtonPress-1>", lambda event : self.record_info() )

        self.status_info = Label(status_frame,text='Initializing...',relief='sunken',borderwidth=1,bg=self.bg_color,anchor='w')
        self.status_info.pack(fill='x',expand=1,side='left')
        self_status_info_configure = self.status_info.configure
        self.status= lambda x : self_status_info_configure(text = x)

        self.status_info.bind("<ButtonPress-1>", lambda event : self.clip_copy_full_path_with_file() )
        self.widget_tooltip(self.status_info,STR('Click to copy full path'))

        self.status_find = Label(status_frame,image=self.ico_find,relief='flat',state='disabled',borderwidth=1,bg=self.bg_color,width=18)
        self.status_find.pack(fill='x',expand=0,side='right')

        self.status_find.bind("<ButtonPress-1>", lambda event : self.finder_wrapper_show() )
        self.status_find_tooltip = lambda message : self.widget_tooltip(self.status_find,message)

        self.status_find_tooltip_default = STR('No search results\nClick to open find dialog.')
        self.status_find_tooltip(self.status_find_tooltip_default)

        ##############################################################################
        tree = self.tree = Treeview(self_main,takefocus=True,show=('tree','headings') )

        self.tree_set = tree.set

        self.tree_get_children = self.tree.get_children
        self.tree_focus = self.tree.focus

        self_org_label = self.org_label = {}

        self_org_label['#0']=STR('Name')
        self_org_label['size_h']=STR('Size')
        self_org_label['ctime_h']=STR('Time')

        tree["columns"]=('data','record','opened','path','size','size_h','ctime','ctime_h','kind')
        tree["displaycolumns"]=('size_h','ctime_h')
        self.real_display_columns=('#0','size_h','ctime_h')

        tree_column = tree.column

        tree_column('#0', width=120, minwidth=100, stretch='yes')
        tree_column('size_h', width=80, minwidth=80, stretch='no',anchor='e')
        tree_column('ctime_h', width=150, minwidth=100, stretch='no',anchor='e')

        tree_heading = tree.heading
        #tree_heading('#0',text='Name \u25B2',anchor='w')
        tree_heading('#0',text=STR('Name'),anchor='w')
        tree_heading('size_h',anchor='n',text=self_org_label['size_h'])
        tree_heading('ctime_h',anchor='n',text=self_org_label['ctime_h'])

        tree_yview = tree.yview
        self.tree_scrollbar = Scrollbar(self_main, orient='vertical', command=tree_yview,takefocus=False)

        tree.configure(yscrollcommand=self.tree_scrollbar_set)

        self.tree_scrollbar.pack(side='right',fill='y',expand=0)
        tree.pack(fill='both',expand=1, side='left')

        tree_tag_configure = tree.tag_configure

        tree_tag_configure(self.RECORD_RAW, foreground=self.col_record_raw)
        tree_tag_configure(self.RECORD, foreground=self.col_record)
        tree_tag_configure(self.SYMLINK, foreground='gray')
        tree_tag_configure(self.FOUND, foreground=self.col_found)

        self.biggest_file_of_path={}
        self.biggest_file_of_path_id={}

        self.iid_to_size={}

        self.popup = Menu(tree, tearoff=0,bg=self.bg_color)
        self.popup_unpost = self.popup.unpost
        self.popup.bind("<FocusOut>",lambda event : self.popup_unpost() )

        #######################################################################

        self.info_dialog_on_main = LabelDialog(self_main,self.main_icon_tuple,self.bg_color,pre_show=self.pre_show,post_close=self.post_close)

        self.progress_dialog_on_load = ProgressDialog(self_main,self.main_icon_tuple,self.bg_color,pre_show=self.pre_show,post_close=self.post_close)
        self.progress_dialog_on_load.command_on_close = self.progress_dialog_load_abort

        self.widget_tooltip(self.progress_dialog_on_load.abort_button,'')

        #######################################################################

        def file_cascade_post():
            self.file_cascade.delete(0,'end')
            if not self.block_processing_stack:
                self_file_cascade_add_command = self.file_cascade.add_command
                self_file_cascade_add_separator = self.file_cascade.add_separator

                self_file_cascade_add_command(label = STR('New record ...'),command = self.scan_dialog_show, accelerator="Ctrl+N",image = self.ico_record_new,compound='left')

                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = STR('Import record ...'), accelerator='Ctrl+I', command = self.record_import,image = self.ico_record_import,compound='left')
                self_file_cascade_add_command(label = STR('Import "Where Is It?" xml ...'), command = self.record_import_wii,image = self.ico_empty,compound='left')
                self_file_cascade_add_command(label = STR('Import "Cathy" data ...'), command = self.record_import_caf,image = self.ico_empty,compound='left')
                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = STR('Find ...'),command = self.finder_wrapper_show, accelerator="Ctrl+F",image = self.ico_find,compound='left',state = 'normal' if librer_core.records else 'disabled')
                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = STR('Settings ...'),command = self.settings_show, accelerator="F12",image = self.ico_empty,compound='left',state = 'normal')
                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = STR('Clear Search Results'),command = self.find_clear, image = self.ico_empty,compound='left',state = 'normal' if self.any_valid_find_results else 'disabled')
                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = STR('Exit'),command = self.exit,image = self_ico['exit'],compound='left')

        self.file_cascade= Menu(menubar,tearoff=0,bg=self.bg_color,postcommand=file_cascade_post)
        menubar.add_cascade(label = STR("File"),menu = self.file_cascade,accelerator="Alt+F")

        def help_cascade_post():
            self.help_cascade.delete(0,'end')
            if not self.block_processing_stack:

                self_help_cascade_add_command = self.help_cascade.add_command
                self_help_cascade_add_separator = self.help_cascade.add_separator

                self_help_cascade_add_command(label = STR('About'),command=lambda : self.get_about_dialog().show(),accelerator="F1", image = self_ico['about'],compound='left')
                self_help_cascade_add_command(label = STR('License'),command=lambda : self.get_license_dialog().show(), image = self.ico_license,compound='left')
                self_help_cascade_add_separator()
                self_help_cascade_add_command(label = STR('Open current Log'),command=self.show_log, image = self_ico['log'],compound='left')
                self_help_cascade_add_command(label = STR('Open logs directory'),command=self.show_logs_dir, image = self_ico['logs'],compound='left')
                self_help_cascade_add_separator()
                self_help_cascade_add_command(label = STR('Open homepage'),command=self.show_homepage, image = self_ico['home'],compound='left')

        self.help_cascade= Menu(menubar,tearoff=0,bg=self.bg_color,postcommand=help_cascade_post)

        menubar.add_cascade(label = STR("Help"),menu = self.help_cascade)

        #######################################################################
        self.sel_item = None

        self_REAL_SORT_COLUMN = self.REAL_SORT_COLUMN = self.REAL_SORT_COLUMN={}

        self_REAL_SORT_COLUMN['#0'] = 'data'
        self_REAL_SORT_COLUMN['size_h'] = 'size'
        self_REAL_SORT_COLUMN['ctime_h'] = 'ctime'

        self_REAL_SORT_COLUMN_INDEX = self.REAL_SORT_COLUMN_INDEX = self.REAL_SORT_COLUMN_INDEX={}

        for disply_column in self.real_display_columns:
            self_REAL_SORT_COLUMN_INDEX[disply_column] = tree["columns"].index(self_REAL_SORT_COLUMN[disply_column])

        self_REAL_SORT_COLUMN_IS_NUMERIC = self.REAL_SORT_COLUMN_IS_NUMERIC = self.REAL_SORT_COLUMN_IS_NUMERIC={}

        self_REAL_SORT_COLUMN_IS_NUMERIC['#0'] = False
        self_REAL_SORT_COLUMN_IS_NUMERIC['size_h'] = True
        self_REAL_SORT_COLUMN_IS_NUMERIC['ctime_h'] = True

        try:
            self.column_sort_last_params = self.cfg_get(CFG_SORTING)
            if len(self.column_sort_last_params)!=7:
                raise

        except:
            #colname,sort_index,is_numeric,reverse,group_code,dir_code,non_dir_code
            self.column_sort_last_params=('#0',self_REAL_SORT_COLUMN_INDEX['#0'],self_REAL_SORT_COLUMN_IS_NUMERIC['#0'],0,0,1,2)

        try:
            self.column_sort_last_params_results = self.cfg_get(CFG_SORTING_RESULTS)
            if len(self.column_sort_last_params_results)!=7:
                raise

        except:
            #colname,sort_index,is_numeric,reverse,group_code,dir_code,non_dir_code
            self.column_sort_last_params_results=('#0',self_REAL_SORT_COLUMN_INDEX['#0'],self_REAL_SORT_COLUMN_IS_NUMERIC['#0'],0,0,1,2)
            #self.column_sort_last_params_results=('#0',self_REAL_SORT_COLUMN_INDEX_RESULTS['#0'],self_REAL_SORT_COLUMN_IS_NUMERIC['#0'],0,0,1,2)


        #######################################################################

        self.main_update()
        try:
            cfg_geometry=self.cfg_get(CFG_geometry)

            if cfg_geometry:
                self_main.geometry(cfg_geometry)
            else:
                x_offset = int(0.5*(self_main.winfo_screenwidth()-self_main.winfo_width()))
                y_offset = int(0.5*(self_main.winfo_screenheight()-self_main.winfo_height()))

                self_main.geometry(f'+{x_offset}+{y_offset}')

        except Exception as e:
            self.status(str(e))
            l_error(e)
            cfg_geometry = None

        self_main.deiconify()

        #prevent displacement
        if cfg_geometry :
            self_main.geometry(cfg_geometry)

        self.menu_disable()
        self.menubar_config(cursor='watch')
        self.main_config(cursor='watch')

        self.main_update()

        self.item_to_record={}
        self.record_to_item={}
        self.record_filename_to_record={}
        self.item_to_data={}

        #############################
        self_progress_dialog_on_load = self.progress_dialog_on_load
        self_progress_dialog_on_load_lab = self_progress_dialog_on_load.lab

        self_progress_dialog_on_load_progr1var = self_progress_dialog_on_load.progr1var
        self_progress_dialog_on_load_progr2var = self_progress_dialog_on_load.progr2var

        self_progress_dialog_on_load_lab_r1_config = self_progress_dialog_on_load.lab_r1.config
        self_progress_dialog_on_load_lab_r2_config = self_progress_dialog_on_load.lab_r2.config

        str_self_progress_dialog_on_load_abort_button = str(self_progress_dialog_on_load.abort_button)

        #############################

        self.tooltip_message[str_self_progress_dialog_on_load_abort_button]=STR('Abort loading.')
        self_progress_dialog_on_load.abort_button.configure(image=self.ico_cancel,text=STR('Abort'),compound='left')
        self_progress_dialog_on_load.abort_button.pack( anchor='center',padx=5,pady=5)

        self.action_abort=False
        self.action_abort_single=False
        self_progress_dialog_on_load.abort_button.configure(state='normal')

        self.status_info.configure(image='',text = STR('Checking records to load ...'))
        records_quant,records_size = librer_core.read_records_pre()

        load_errors = []

        self.groups_show()

        if records_quant:
            self.status_info.configure(image='',text = STR('Loading records ...'))

            read_thread=Thread(target=lambda : librer_core.threaded_read_records(load_errors),daemon=True)
            read_thread_is_alive = read_thread.is_alive

            self_progress_dialog_on_load.lab_l1.configure(text=STR('Records space:'))
            self_progress_dialog_on_load.lab_l2.configure(text=STR('Records number:'))
            self_progress_dialog_on_load.show(STR('Loading records'))

            self_progress_dialog_on_load_progr1var.set(0)
            self_progress_dialog_on_load_lab_r1_config(text='- - - -')
            self_progress_dialog_on_load_progr2var.set(0)
            self_progress_dialog_on_load_lab_r2_config(text='- - - -')

            wait_var=BooleanVar()
            wait_var.set(False)

            read_thread.start()

            bytes_to_str_records_size = bytes_to_str(records_size)
            fnumber_records_quant = fnumber(records_quant)

            self_progress_dialog_on_load_lab_r1_configure = self_progress_dialog_on_load.lab_r1.configure
            self_progress_dialog_on_load_lab_r2_configure = self_progress_dialog_on_load.lab_r2.configure
            self_progress_dialog_on_load_lab_0_configure = self_progress_dialog_on_load_lab[0].configure

            self_progress_dialog_on_load_progr1var_set = self_progress_dialog_on_load_progr1var.set
            self_progress_dialog_on_load_progr2var_set = self_progress_dialog_on_load_progr2var.set

            self_main_after = self.main.after

            wait_var_set = wait_var.set
            wait_var_get = wait_var.get
            self_main_wait_variable = self.main.wait_variable

            groups_expand = not bool(self.cfg.get(CFG_KEY_groups_collapse))

            self_single_record_show = self.single_record_show

            while read_thread_is_alive() or librer_core.records_to_show :
                self_progress_dialog_on_load_lab[2].configure(image=self.get_hg_ico())

                if librer_core.records_to_show:
                    new_rec,quant,size = librer_core.records_to_show.pop(0)

                    self_progress_dialog_on_load_lab_r1_configure(text= bytes_to_str(size) + '/' + bytes_to_str_records_size)
                    self_progress_dialog_on_load_lab_r2_configure(text= fnumber(quant) + '/' + fnumber_records_quant)

                    self_progress_dialog_on_load_lab_0_configure(text=librer_core.info_line)

                    self_progress_dialog_on_load_progr1var_set(100*size/records_size)
                    self_progress_dialog_on_load_progr2var_set(100*quant/records_quant)

                    self_single_record_show(new_rec,groups_expand)
                else:
                    self_main_after(25,lambda : wait_var_set(not wait_var_get()))
                    self_main_wait_variable(wait_var)

                if self.action_abort:
                    librer_core.abort()

            self_progress_dialog_on_load.hide(True)
            read_thread.join()

            if self.action_abort:
                self.info_dialog_on_main.show(STR('Records loading aborted','Restart Librer to gain full access to the recordset.'))

        if load_errors:
            self.get_text_info_dialog().show(STR('Loading errors'),'\n\n'.join(load_errors) )
            self.store_text_dialog_fields(self.text_info_dialog)

        self.menu_enable()
        self.menubar_config(cursor='')
        self.main_config(cursor='')

        if items := self.tree.get_children():
            item = items[0]
            self.tree_focus(item)
            self.sel_item = item
            self.tree_item_focused(item)

        self.tree.focus_set()

        self.status_info.configure(image='',text = STR('Ready'))

        tree_bind = tree.bind

        tree_bind('<ButtonPress-1>', self.tree_on_mouse_button_press)
        tree_bind('<Double-Button-1>', self.double_left_button)
        tree_bind("<Motion>", self.motion_on_tree)
        tree_bind("<Leave>", lambda event : self.widget_leave())

        tree_bind('<KeyPress>', self.key_press )
        tree_bind('<<TreeviewOpen>>', lambda event : self.open_item())
        tree_bind('<<TreeviewClose>>', lambda event : self.close_item())
        tree_bind('<ButtonPress-3>', self.context_menu_show)

        #tree_bind("<<TreeviewSelect>>", lambda event : self.tree_on_select() )

        tree_bind("<Configure>", lambda event : self.tree_configure())

        self_main_bind = self_main.bind

        self.tree.bind("<FocusOut>",lambda event : self.tree_focus_out() )
        self.tree.bind("<FocusIn>",lambda event : self.tree_focus_in() )

        self_main_bind("<FocusOut>",lambda event : self.menubar_unpost() )
        self_main_bind("<FocusIn>",lambda event : self.focusin() )

        self_main_bind('<KeyPress-F1>', lambda event : self.get_about_dialog().show())
        self_main_bind('<Control-n>', lambda event : self.scan_dialog_show())
        self_main_bind('<Control-N>', lambda event : self.scan_dialog_show())

        self_main_bind('<Control-f>', lambda event : self.finder_wrapper_show())
        self_main_bind('<Control-F>', lambda event : self.finder_wrapper_show())

        self_main_bind('<Control-e>', lambda event : self.record_export())
        self_main_bind('<Control-E>', lambda event : self.record_export())

        self_main_bind('<Control-i>', lambda event : self.record_import())
        self_main_bind('<Control-I>', lambda event : self.record_import())

        self_main_bind('<Control-c>', lambda event : self.clip_copy_full_path_with_file())
        self_main_bind('<Control-C>', lambda event : self.clip_copy_full_path_with_file())

        #self_main_bind('<Alt-Return>', lambda event : self.record_info())
        #self_main_bind('<Return>', lambda event : self.show_customdata())

        self_main_bind('<KeyPress-Delete>', lambda event : self.delete_action())
        self_main_bind('<F8>', lambda event : self.delete_action() )

        self_main_bind('<F7>', lambda event : self.new_group())

        self_main_bind('<F6>', lambda event : self.assign_to_group() )
        self_main_bind('<F5>', lambda event : self.record_repack() )

        self_main_bind('<F3>', lambda event : self.find_next() )
        self_main_bind('<F12>', lambda event : self.settings_show() )

        self_main_bind('<Shift-F3>', lambda event : self.find_prev())

        self_main_bind('<F2>', lambda event : self.alias_name() )

        self_main_bind('<BackSpace>', lambda event : self.unload_record())
        self_main_bind('<Control-BackSpace>', lambda event : self.unload_all_recods())

        gc_collect()
        gc_enable()

        self.any_valid_find_results = False
        self.external_find_params_change=True

        self.temp_dir = mkdtemp()
        #print(f'{self.temp_dir=}')

        self.processing_on()

        self.tree_configure()

        self_main.mainloop()

    def main_drop(self, data):
        self.get_scan_dialog()
        self.path_to_scan_entry_var.set(data)
        self.scan_label_entry_var.set("dropped_path")

        self.main.after_idle(lambda : self.scan_dialog_show())

    def scan_dialog_drop(self, data):
        if paths := self.main.splitlist(data):
            path = paths[0]
            p_path = normpath(abspath(path))

            self.scan_label_entry_var.set("dropped_path")

            if path_exists(p_path):
                if isdir(p_path):
                    self.path_to_scan_entry_var.set(p_path)
                else:
                    self.path_to_scan_entry_var.set(dirname(p_path))
            else:
                self.get_info_dialog_on_scan().show(STR('Path does not exist'),str(p_path))

    def tree_focus_out(self):
        tree = self.tree
        item=tree.focus()
        if item:
            tree.selection_set(item)
            self.sel_item=item

    def tree_focus_in(self):
        tree = self.tree
        try:
            item=self.sel_item
            selection = tree.selection()

            if selection:
                tree.selection_remove(*selection)

                if not item:
                    item = selection[0]

            if item:
                self.select_and_focus(item)

        except Exception as e:
            l_error(f'groups_tree_focus_in:{e}')

    def tree_scrollbar_set(self,v1,v2):
        if v1=='0.0' and v2=='1.0':
            self.tree_scrollbar.pack_forget()
        else:
            self.tree_scrollbar.set(v1,v2)
            self.tree_scrollbar.pack(side='right',fill='y',expand=0)

    def results_tree_scrollbar_set(self,v1,v2):
        if v1=='0.0' and v2=='1.0':
            self.results_tree_scrollbar.pack_forget()
        else:
            self.results_tree_scrollbar.set(v1,v2)
            self.results_tree_scrollbar.pack(side='right',fill='y',expand=0)

    def item_has_cd(self,item):
        has_cd=False
        if item in self.item_to_data:
            data_tuple = self.item_to_data[item]
            code = data_tuple[1]

            is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,cd_aborted,cd_empty,aux2 = LUT_decode[code]
        return has_cd

    def widget_tooltip_cget(self,widget,tooltip):
        widget.bind("<Motion>", lambda event : self.motion_on_widget_cget(event,tooltip))
        widget.bind("<Leave>", lambda event : self.widget_leave())

    def widget_tooltip(self,widget,tooltip):
        widget.bind("<Motion>", lambda event : self.motion_on_widget(event,tooltip))
        widget.bind("<Leave>", lambda event : self.widget_leave())

    #######################################################################
    action_abort=False

    def progress_dialog_find_abort(self):
        self.status(STR("Abort pressed ..."))
        self.action_abort=True

    def progress_dialog_load_abort(self):
        self.status(STR("Abort pressed ..."))
        self.action_abort=True

    def progress_dialog_abort(self):
        self.status(STR("Abort pressed ..."))
        l_info(STR("Abort pressed ..."))
        self.action_abort=True

    def handle_sigint(self):
        self.status("Received SIGINT signal")
        l_warning("Received SIGINT signal")
        self.action_abort=True

    def get_hg_ico(self):
        self.hg_index=(self.hg_index+1) % self.hg_ico_len
        return self.hg_ico[self.hg_index]

    @restore_status_line
    def pre_show(self,on_main_window_dialog=True,new_widget=None):
        self.processing_off(f'pre_show:{new_widget}')

        #self.status("Opening dialog ...")
        self.menubar_unpost()
        self.hide_tooltip()
        self.popup_unpost()

        if on_main_window_dialog:
            if new_widget:
                self.main_locked_by_child=new_widget

    def post_close(self,on_main_window_dialog=True):
        self.main.focus_set()

        if on_main_window_dialog:
            self.main_locked_by_child=None

        self.processing_on()

    text_info_dialog_created = False
    @restore_status_line
    @block
    def get_text_info_dialog(self):
        if not self.text_info_dialog_created:
            self.status(STR("Creating dialog ..."))

            self.text_info_dialog = TextDialogInfo(self.main,self.main_icon_tuple,self.bg_color,pre_show=self.pre_show,post_close=self.post_close)
            self.fix_text_dialog(self.text_info_dialog)

            self.text_info_dialog.cancel_button.configure(text=STR('Cancel'),compound='left')
            self.text_info_dialog.copy_button.configure(text=STR('Copy'),compound='left')

            self.text_info_dialog_created = True

        return self.text_info_dialog

    simple_question_dialog_created = False
    @restore_status_line
    @block
    def get_simple_question_dialog(self):
        if not self.simple_question_dialog_created:
            self.status(STR("Creating dialog ..."))

            self.simple_question_dialog = LabelDialogQuestion(self.main,(self.ico_record_delete,self.ico_record_delete),self.bg_color,pre_show=self.pre_show,post_close=self.post_close,image=self.ico_warning)

            self.simple_question_dialog.label.configure(justify='left')
            self.simple_question_dialog.cancel_button.configure(text=STR('Cancel'),compound='left')
            try:
                self.simple_question_dialog.label.configure(font=('Courier', 10))
            except:
                try:
                    self.simple_question_dialog.label.configure(font=('TkFixedFont', 10))
                except:
                    pass

            self.simple_question_dialog_created = True

        return self.simple_question_dialog

    def configure_scan_button(self):
        self.scan_button.configure(image=self.ico_start if all(bool(self.CDE_use_var_list[e_local].get())==False for e_local in range(self.CDE_ENTRIES_MAX) ) else self.ico_warning)

    def shell_change(self,e):
        if self.CDE_shell_var_list[e].get():
            #self.open_button[e].configure(state='disabled')
            self.executable_entry[e].grid(row=self.executable_entry_row[e], column=7,sticky='news',columnspan=2)
            self.parameters_entry[e].grid_forget()
        else:
            #self.open_button[e].configure(state='normal')
            self.executable_entry[e].grid(row=self.executable_entry_row[e], column=7,sticky='news',columnspan=1)
            self.parameters_entry[e].grid(row=self.executable_entry_row[e], column=8,sticky='news')

    def use_checkbutton_mod(self,e,do_configure_scan_button=True):
        #do_crc = bool( self.CDE_crc_var_list[e].get() )
        do_crc = False
        do_cd = bool( self.CDE_use_var_list[e].get() )

        if do_cd:
            self.executable_entry[e].configure(state='normal')
            self.parameters_entry[e].configure(state='normal')
            self.shell_checkbutton[e].configure(state='normal')
            self.open_button[e].configure(state='normal')
            self.timeout_entry[e].configure(state='normal')
            self.test_button[e].configure(state='normal')

            self.shell_change(e)

            self.scan_button.configure(image=self.ico_warning)

        else:
            self.executable_entry[e].configure(state='disabled')
            self.parameters_entry[e].configure(state='disabled')
            self.shell_checkbutton[e].configure(state='disabled')
            self.open_button[e].configure(state='disabled')
            self.timeout_entry[e].configure(state='disabled')
            self.test_button[e].configure(state='disabled')

        if do_cd or do_crc:
            self.mask_entry[e].configure(state='normal')
            self.size_min_entry[e].configure(state='normal')
            self.size_max_entry[e].configure(state='normal')
        else:
            self.mask_entry[e].configure(state='disabled')
            self.size_min_entry[e].configure(state='disabled')
            self.size_max_entry[e].configure(state='disabled')

        if do_configure_scan_button:
            self.configure_scan_button()

    def scan_comp_set(self):
        self.scan_compr_var_int.set(int(self.scan_compr_var.get()))

    def scan_threads_set(self):
        self.scan_threads_var_int.set(int(self.scan_threads_var.get()))

    scan_dialog_created = False
    @restore_status_line
    @block
    def get_scan_dialog(self):
        if not self.scan_dialog_created:
            self.status(STR("Creating dialog ..."))

            self.scan_dialog=dialog=GenericDialog(self.main,(self.ico_record_new,self.ico_record_new),self.bg_color,'---',pre_show=self.pre_show,post_close=self.post_close,min_width=800,min_height=550)

            dialog.area_main.drop_target_register(DND_FILES)
            dialog.area_main.dnd_bind('<<Drop>>', lambda e: self.scan_dialog_drop(e.data) )

            dialog.area_main.grid_columnconfigure(0, weight=1)
            dialog.area_main.grid_rowconfigure(3, weight=1)

            dialog.widget.bind('<Alt_L><p>',lambda event : self.set_path_to_scan())
            dialog.widget.bind('<Alt_L><P>',lambda event : self.set_path_to_scan())
            dialog.widget.bind('<Alt_L><s>',lambda event : self.scan_wrapper())
            dialog.widget.bind('<Alt_L><S>',lambda event : self.scan_wrapper())

            self.scan_dialog_group = None
            ##############

            temp_frame = Frame(dialog.area_main,borderwidth=2,bg=self.bg_color)
            temp_frame.grid(row=0,column=0,sticky='we',padx=4,pady=4)

            ul_lab=Label(temp_frame,text=STR("Label:"),bg=self.bg_color,anchor='w')
            ul_lab.grid(row=0, column=4, sticky='news',padx=4,pady=4)\

            label_tooltip = STR("Internal Label of the record to be created")
            self.widget_tooltip(ul_lab,label_tooltip)

            self.scan_label_entry_var=StringVar(value='')
            self.scan_label_entry = Entry(temp_frame,textvariable=self.scan_label_entry_var)
            self.scan_label_entry.grid(row=0, column=5, sticky='news',padx=4,pady=4)

            self.widget_tooltip(self.scan_label_entry,label_tooltip)

            (path_to_scan_label := Label(temp_frame,text=STR("Path:"),bg=self.bg_color,anchor='w')).grid(row=0, column=0, sticky='news',padx=4,pady=4)
            self.widget_tooltip(path_to_scan_label,STR("Path to scan"))

            self.path_to_scan_entry_var=StringVar(value=self.last_dir)
            path_to_scan_entry = Entry(temp_frame,textvariable=self.path_to_scan_entry_var)
            path_to_scan_entry.grid(row=0, column=1, sticky='news',padx=4,pady=4)
            self.widget_tooltip(path_to_scan_entry,STR("Path to scan"))

            self.add_path_button = Button(temp_frame,width=18,image = self.ico_open, command=self.set_path_to_scan,underline=0)
            self.add_path_button.grid(row=0, column=2, sticky='news',padx=4,pady=4)
            self.widget_tooltip(self.add_path_button,STR("Set path to scan."))

            self.add_dev_button = Menubutton(temp_frame,width=18,image = self.ico_drive,underline=0)
            self.add_dev_button.grid(row=0, column=3, sticky='news',padx=4,pady=4)
            self.widget_tooltip(self.add_dev_button,STR("Select device to scan."))

            self.drives_menu = Menu(self.add_dev_button, tearoff=0,postcommand=self.set_dev_to_scan_menu)
            self.add_dev_button["menu"] = self.drives_menu

            temp_frame.grid_columnconfigure(1, weight=1)

            ##############
            self.scan_button = Button(dialog.area_buttons,width=12,text=STR("Scan"),compound='left',command=self.scan_wrapper,underline=0)
            self.scan_button.pack(side='right',padx=4,pady=4)
            self.widget_tooltip(self.scan_button,STR('Start scanning.\n\nIf any Custom Data Extractor is enabled it will be executed\nwith every file that meets its criteria (mask & size).'))

            self.scan_cancel_button = Button(dialog.area_buttons,width=12,text=STR("Cancel"),command=self.scan_dialog_hide_wrapper)
            #,image=self.ico_stop
            #,compound='left'
            self.scan_cancel_button.pack(side='left',padx=4,pady=4)

            (scan_options_frame := Frame(dialog.area_buttons,bg=self.bg_color)).pack(side='right',padx=4,pady=4)
            #.grid(row=1,column=0,sticky='news',padx=4,pady=4,columnspan=2)
            self.scan_compr_var = IntVar()
            self.scan_compr_var_int = IntVar()

            self.scan_threads_var = IntVar()
            self.scan_threads_var_int = IntVar()

            self.scan_compr_var.set(9)
            self.scan_compr_var_int.set(9)

            self.scan_threads_var.set(1)
            self.scan_threads_var_int.set(1)

            (compr_label := Label(scan_options_frame, text=STR('Compression:'),bg=self.bg_color,relief='flat')).pack(side='left',padx=2,pady=2)
            (compr_scale := Scale(scan_options_frame, variable=self.scan_compr_var, orient='horizontal',from_=0, to=22,command=lambda x : self.scan_comp_set(),style="TScale",length=160)).pack(fill='x',side='left',expand=1,padx=2)
            (compr_in_label := Label(scan_options_frame, textvariable=self.scan_compr_var_int,width=3,bg=self.bg_color,relief='groove',borderwidth=2)).pack(side='left',padx=2,pady=2)
            compr_tooltip = STR("Data record internal compression. A higher value\nmeans a smaller file and longer compression time.\nvalues above 20 may result in extremely long compression\nand memory consumption. The default value is 9.")
            self.widget_tooltip(compr_scale,compr_tooltip)
            self.widget_tooltip(compr_label,compr_tooltip)
            self.widget_tooltip(compr_in_label,compr_tooltip)

            (threads_in_label := Label(scan_options_frame, textvariable=self.scan_threads_var_int,width=3,bg=self.bg_color,relief='groove',borderwidth=2)).pack(side='right',padx=2,pady=2)
            (threads_scale := Scale(scan_options_frame, variable=self.scan_threads_var, orient='horizontal',from_=0, to=cpu_count(),command=lambda x : self.scan_threads_set(),style="TScale",length=160)).pack(fill='x',side='right',expand=1,padx=2)
            (threads_label := Label(scan_options_frame, text=STR('CDE Threads:'),bg=self.bg_color,relief='flat')).pack(side='left',padx=2,pady=2)
            threads_tooltip = STR("Number of threads used to extract Custom Data\n\n0 - all available CPU cores\n1 - single thread (default value)\n\nThe optimal value depends on the CPU cores performace,\nIO subsystem performance and Custom Data Extractor specifics.\n\nConsider limitations of parallel CDE execution e.g.\nnumber of licenses of used software,\nused working directory, needed memory etc.")
            self.widget_tooltip(threads_scale,threads_tooltip)
            self.widget_tooltip(threads_label,threads_tooltip)
            self.widget_tooltip(threads_in_label,threads_tooltip)

            self.single_device=BooleanVar()
            single_device_button = Checkbutton(dialog.area_buttons,text=STR('one device mode'),variable=self.single_device)
            single_device_button.pack(side='right',padx=2,pady=2)
            self.single_device.set(self.cfg_get(CFG_KEY_SINGLE_DEVICE))
            self.widget_tooltip(single_device_button,STR("Don't cross device boundaries (mount points, bindings etc.) - recommended"))

            dialog.focus=self.scan_cancel_button

            ############
            temp_frame3 = LabelFrame(dialog.area_main,text=STR('Custom Data Extractors:'),borderwidth=2,bg=self.bg_color,takefocus=False)
            temp_frame3.grid(row=3,column=0,sticky='news',padx=4,pady=4,columnspan=3,ipadx=4,ipady=4)

            sf_par3 = SFrame(temp_frame3,bg=self.bg_color)
            sf_par3.pack(fill='both',expand=True,side='top')
            self.cde_frame = cde_frame = sf_par3.frame()

            (lab_criteria := Label(cde_frame,text=STR('% File cryteria'),bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=0, column=2,sticky='news',columnspan=3)
            (lab_command := Label(cde_frame,text=STR('Custom Data extractor command'),bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=0, column=5,sticky='news',columnspan=4)
            (lab_mask := Label(cde_frame,text=STR('File Mask'),bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=1, column=2,sticky='news')
            (lab_min := Label(cde_frame,image=self.ico_bigger,bg=self.bg_color,anchor='center',relief='groove',bd=2,width=40)).grid(row=1, column=3,sticky='news')
            (lab_max := Label(cde_frame,image=self.ico_smaller,bg=self.bg_color,anchor='center',relief='groove',bd=2,width=40)).grid(row=1, column=4,sticky='news')
            (lab_shell := Label(cde_frame,image=self.ico_shell,bg=self.bg_color,anchor='center',relief='groove',bd=2)).grid(row=1, column=5,sticky='news')
            (lab_open := Label(cde_frame,text='',bg=self.bg_color,anchor='n')).grid(row=1, column=6,sticky='news')
            (lab_exec := Label(cde_frame,text=STR('Executable'),bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=1, column=7,sticky='news')
            (lab_pars  := Label(cde_frame,text=STR('Parameters'),bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=1, column=8,sticky='news')
            (lab_timeout := Label(cde_frame,image=self.ico_timeout,bg=self.bg_color,anchor='center',relief='groove',bd=2,width=3)).grid(row=1, column=9,sticky='news')
            (lab_test := Label(cde_frame,image=self.ico_test_col,bg=self.bg_color,anchor='center',relief='groove',bd=2)).grid(row=1, column=10,sticky='news')

            up_tooltip = STR('UP_TOOLTIP')
            use_tooltip = STR("Mark to use CD Extractor")
            mask_tooltip = STR('MASK_TOOLTIP')
            size_common_tooltip = STR('SIZE_TOOLTIP')
            max_tooltip = 'Maximum file size.' + '\n\n' + size_common_tooltip
            min_tooltip = 'Minimum file size.' + '\n\n'+ size_common_tooltip
            exec_tooltip = STR('EXEC_TOOLTIP')
            pars_tooltip = STR('PARS_TOOLTIP')
            shell_tooltip = STR('SHELL_TOOLTIP')
            open_tooltip = STR('OPEN_TOOLTIP')
            timeout_tooltip = STR('TIMEOUT_TOOLTIP')
            test_tooltip_common = STR('TEST_TOOLTIP_COMMOMN')
            test_tooltip = STR('TEST_TOOLTIP') + test_tooltip_common

            self_widget_tooltip = self.widget_tooltip

            #self_widget_tooltip(lab_use,use_tooltip)
            self_widget_tooltip(lab_mask,mask_tooltip)
            self_widget_tooltip(lab_min,min_tooltip)
            self_widget_tooltip(lab_max,max_tooltip)
            self_widget_tooltip(lab_exec,exec_tooltip)
            self_widget_tooltip(lab_pars,pars_tooltip)
            self_widget_tooltip(lab_shell,shell_tooltip)
            self_widget_tooltip(lab_open,open_tooltip)
            self_widget_tooltip(lab_timeout,timeout_tooltip)
            self_widget_tooltip(lab_test,test_tooltip)
            #self_widget_tooltip(lab_crc,crc_tooltip)

            self.CDE_ENTRIES_MAX = 16

            self.CDE_use_var_list = []
            self.CDE_mask_var_list=[]
            self.CDE_size_min_var_list=[]
            self.CDE_size_max_var_list=[]
            self.CDE_executable_var_list=[]
            self.CDE_parameters_var_list=[]
            self.CDE_shell_var_list=[]
            self.CDE_timeout_var_list=[]
            self.CDE_crc_var_list=[]

            self.up_button={}
            self.mask_entry={}
            self.size_min_entry={}
            self.size_max_entry={}
            self.use_checkbutton={}
            self.executable_entry={}
            self.executable_entry_row={}
            self.parameters_entry={}
            self.shell_checkbutton={}
            self.open_button={}
            self.timeout_entry={}
            self.test_button={}
            self.crc_entry={}

            for e in range(self.CDE_ENTRIES_MAX):
                self.CDE_use_var_list.append(BooleanVar())
                self.CDE_mask_var_list.append(StringVar())
                self.CDE_size_min_var_list.append(StringVar())
                self.CDE_size_max_var_list.append(StringVar())
                self.CDE_executable_var_list.append(StringVar())
                self.CDE_parameters_var_list.append(StringVar())
                self.CDE_shell_var_list.append(BooleanVar())
                self.CDE_timeout_var_list.append(StringVar())
                self.CDE_crc_var_list.append(BooleanVar())

                row = e+2

                self.up_button[e] = Button(cde_frame,image=self.ico_up,command = lambda x=e : self.cde_up(x) )

                if row>2:
                    self.up_button[e].grid(row=row,column=0,sticky='news')

                self.use_checkbutton[e] = Checkbutton(cde_frame,variable=self.CDE_use_var_list[e],command = lambda x=e : self.use_checkbutton_mod(x))
                self.use_checkbutton[e].grid(row=row,column=1,sticky='news')

                self.mask_entry[e] = Entry(cde_frame,textvariable=self.CDE_mask_var_list[e])
                self.mask_entry[e].grid(row=row, column=2,sticky='news')

                self.size_min_entry[e] = Entry(cde_frame,textvariable=self.CDE_size_min_var_list[e],width=6)
                self.size_min_entry[e].grid(row=row, column=3,sticky ='news')

                self.size_max_entry[e] = Entry(cde_frame,textvariable=self.CDE_size_max_var_list[e],width=6)
                self.size_max_entry[e].grid(row=row, column=4,sticky ='news')

                self.shell_checkbutton[e] = Checkbutton(cde_frame,variable=self.CDE_shell_var_list[e],command = lambda x=e : self.shell_change(x))
                self.shell_checkbutton[e].grid(row=row, column=5,sticky='news')

                self.open_button[e] = Button(cde_frame,image=self.ico_open,command = lambda x=e : self.cde_entry_open(x) )
                self.open_button[e].grid(row=row,column=6,sticky='news')

                self.executable_entry[e] = Entry(cde_frame,textvariable=self.CDE_executable_var_list[e])
                self.executable_entry_row[e] = row
                self.executable_entry[e].grid(row=row, column=7,sticky='news')

                self.parameters_entry[e] = Entry(cde_frame,textvariable=self.CDE_parameters_var_list[e])
                self.parameters_entry[e].grid(row=row, column=8,sticky='news')

                self.timeout_entry[e] = Entry(cde_frame,textvariable=self.CDE_timeout_var_list[e],width=3)
                self.timeout_entry[e].grid(row=row, column=9,sticky='news')

                self.test_button[e] = Button(cde_frame,image=self.ico_test,command = lambda x=e : self.cde_test(x) )
                self.test_button[e].grid(row=row,column=10,sticky='news')

                #self.crc_entry[e] = Checkbutton(cde_frame,variable=self.CDE_crc_var_list[e],command = lambda x=e : self.use_checkbutton_mod(x))
                #self.crc_entry[e].grid(row=row, column=9,sticky='news')

                self.widget_tooltip(self.up_button[e],up_tooltip)
                self.widget_tooltip(self.mask_entry[e],mask_tooltip)
                self.widget_tooltip(self.size_min_entry[e],min_tooltip)
                self.widget_tooltip(self.size_max_entry[e],max_tooltip)
                self.widget_tooltip(self.use_checkbutton[e],use_tooltip)
                self.widget_tooltip(self.executable_entry[e],exec_tooltip)
                self.widget_tooltip(self.parameters_entry[e],pars_tooltip)
                self.widget_tooltip(self.shell_checkbutton[e],shell_tooltip)
                self.widget_tooltip(self.open_button[e],open_tooltip)
                self.widget_tooltip(self.timeout_entry[e],timeout_tooltip)
                self.widget_tooltip(self.test_button[e],test_tooltip)
                #self.widget_tooltip(self.crc_entry[e],crc_tooltip)

            cde_frame.grid_columnconfigure(2, weight=2)
            cde_frame.grid_columnconfigure(7, weight=2)
            cde_frame.grid_columnconfigure(8, weight=1)

            self.scan_dialog_created = True

        return self.scan_dialog

    def fix_text_dialog(self,dialog):
        dialog.find_lab.configure(image=self.ico_search_text,text=' ' + STR('Search') + ':',compound='left',bg=self.bg_color)
        dialog.find_prev_butt.configure(image=self.ico_left)
        dialog.find_next_butt.configure(image=self.ico_right)

        dialog.text.configure(bg=self.bg_content,fg=self.fg_content)
        dialog.text.configure(bg=self.bg_content,fg=self.fg_content)

        self.widget_tooltip(dialog.find_prev_butt,STR('Select Prev') + ' (Shift+F3)')
        self.widget_tooltip(dialog.find_next_butt,STR('Select Next') + ' (F3)')
        self.widget_tooltip(dialog.find_cs,STR('Case sensitive'))
        self.widget_tooltip(dialog.find_info_lab,STR('index of the selected search result / search results total'))

        dialog.find_var.set( self.cfg_get(CFG_KEY_SEARCH_TXT_STRING) )
        dialog.find_cs_var.set( self.cfg_get(CFG_KEY_SEARCH_TXT_CS) )

    def store_text_dialog_fields(self,dialog):
        self.cfg.set(CFG_KEY_SEARCH_TXT_STRING,dialog.find_var.get())
        self.cfg.set(CFG_KEY_SEARCH_TXT_CS,dialog.find_cs_var.get())

    progress_dialog_on_scan_created = False
    @restore_status_line
    @block
    def get_progress_dialog_on_scan(self):
        if not self.progress_dialog_on_scan_created:
            self.status(STR("Creating dialog ..."))

            self.progress_dialog_on_scan = ProgressDialog(self.scan_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget : self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))

            self.progress_dialog_on_scan.command_on_close = self.progress_dialog_abort

            self.widget_tooltip(self.progress_dialog_on_scan.abort_button,'')
            self.progress_dialog_on_scan_created = True

        return self.progress_dialog_on_scan

    simple_progress_dialog_on_scan_created = False
    @restore_status_line
    @block
    def get_simple_progress_dialog_on_scan(self):
        if not self.simple_progress_dialog_on_scan_created:
            self.status(STR("Creating dialog ..."))

            self.simple_progress_dialog_on_scan = ProgressDialog(self.scan_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget : self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False),ShowProgress=False,min_width=400,min_height=200)

            self.simple_progress_dialog_on_scan.command_on_close = self.progress_dialog_abort

            self.widget_tooltip(self.simple_progress_dialog_on_scan.abort_button,'Abort test')

            str_simple_progress_dialog_scan_abort_button = str(self.simple_progress_dialog_on_scan.abort_button)
            self.tooltip_message[str_simple_progress_dialog_scan_abort_button]='Abort test.'

            self.simple_progress_dialog_on_scan_created = True

        return self.simple_progress_dialog_on_scan

    info_dialog_on_main_created = False
    @restore_status_line
    @block
    def get_info_dialog_on_main(self):
        if not self.info_dialog_on_main_created:
            self.status(STR("Creating dialog ..."))

            self.info_dialog_on_main = LabelDialog(self.main,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=True,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=True))
            self.info_dialog_on_main_created = True

        return self.info_dialog_on_main

    info_dialog_on_settings_created = False
    @restore_status_line
    @block
    def get_info_dialog_on_settings(self):
        if not self.info_dialog_on_settings_created:
            self.status(STR("Creating dialog ..."))

            self.info_dialog_on_settings = LabelDialog(self.settings_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))
            self.info_dialog_on_settings_created = True

        return self.info_dialog_on_settings

    info_dialog_on_scan_created = False
    @restore_status_line
    @block
    def get_info_dialog_on_scan(self):
        if not self.info_dialog_on_scan_created:
            self.status(STR("Creating dialog ..."))

            self.info_dialog_on_scan = LabelDialog(self.scan_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))
            self.info_dialog_on_scan_created = True

        return self.info_dialog_on_scan

    text_dialog_on_scan_created = False
    @restore_status_line
    @block
    def get_text_dialog_on_scan(self):
        if not self.text_dialog_on_scan_created:
            self.status(STR("Creating dialog ..."))

            self.text_dialog_on_scan = TextDialogInfo(self.scan_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget : self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))
            self.fix_text_dialog(self.text_dialog_on_scan)
            self.text_dialog_on_scan.cancel_button.configure(text=STR('Close'))
            self.text_dialog_on_scan.copy_button.configure(text=STR('Copy'),compound='left')

            self.text_dialog_on_scan_created = True

        return self.text_dialog_on_scan

    text_ask_dialog_on_scan_created = False
    @restore_status_line
    @block
    def get_text_ask_dialog_on_scan(self):
        if not self.text_ask_dialog_on_scan_created:
            self.status(STR("Creating dialog ..."))

            self.text_ask_dialog_on_scan = TextDialogQuestion(self.scan_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False),image=self.ico_warning)
            self.fix_text_dialog(self.text_ask_dialog_on_scan)
            self.text_ask_dialog_on_scan.cancel_button.configure(text=STR('Cancel'))
            self.text_ask_dialog_on_scan.copy_button.configure(text=STR('Copy'),compound='left')

            self.text_ask_dialog_on_scan_created = True

        return self.text_ask_dialog_on_scan

    ask_dialog_on_scan_created = False
    @restore_status_line
    @block
    def get_ask_dialog_on_scan(self):
        if not self.ask_dialog_on_scan_created:
            self.status(STR("Creating dialog ..."))

            self.ask_dialog_on_scan = LabelDialogQuestion(self.scan_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False),image=self.ico_warning)
            self.ask_dialog_on_scan_created = True

        return self.ask_dialog_on_scan

    progress_dialog_on_main_created = False
    @restore_status_line
    @block
    def get_progress_dialog_on_main(self):
        if not self.progress_dialog_on_main_created:
            self.status(STR("Creating dialog ..."))

            self.progress_dialog_on_main = ProgressDialog(self.main,self.main_icon_tuple,self.bg_color,pre_show=self.pre_show,post_close=self.post_close)
            self.progress_dialog_on_main.set_mins(300, 100)
            self.progress_dialog_on_main.command_on_close = self.progress_dialog_abort

            self.progress_dialog_on_main.abort_button.configure(command=librer_core.abort)

            self.progress_dialog_on_main.progr1.grid_forget()
            self.progress_dialog_on_main.progr2.grid_forget()

            self.progress_dialog_on_main.lab_l1.grid_forget()
            self.progress_dialog_on_main.lab_l2.grid_forget()

            self.progress_dialog_on_main.lab_r1.grid_forget()
            self.progress_dialog_on_main.lab_r2.grid_forget()

            self.progress_dialog_on_main.progr1.grid_forget()
            self.progress_dialog_on_main.progr2.grid_forget()

            self.progress_dialog_on_main_created = True

        return self.progress_dialog_on_main

    progress_dialog_on_find_created = False
    @restore_status_line
    @block
    def get_progress_dialog_on_find(self):
        if not self.progress_dialog_on_find_created:
            self.status(STR("Creating dialog ..."))

            self.progress_dialog_on_find = ProgressDialog(self.find_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))
            self.progress_dialog_on_find.command_on_close = self.progress_dialog_find_abort
            self.widget_tooltip(self.progress_dialog_on_find.abort_button,STR('Abort searching.'))

            self.progress_dialog_on_find_created = True

        return self.progress_dialog_on_find

    def repack_to_local(self):
        self.repack_dialog_do_it = True
        self.repack_dialog.hide()

    def repack_comp_set(self):
        self.repack_compr_var_int.set(int(self.repack_compr_var.get()))

    def wii_import_comp_set(self):
        self.wii_import_compr_var_int.set(int(self.wii_import_compr_var.get()))

    repack_dialog_created = False
    @restore_status_line
    @block
    def get_repack_dialog(self):
        self.repack_dialog_do_it=False

        if not self.repack_dialog_created:

            self.repack_dialog=GenericDialog(self.main,self.main_icon_tuple,self.bg_color,STR('Rename / Repack record'),pre_show=self.pre_show,post_close=self.post_close,min_width=400,min_height=200)
            self.repack_cd_var = BooleanVar()
            #self.repack_crc_var = BooleanVar()
            self.repack_compr_var = IntVar()
            self.repack_compr_var_int = IntVar()
            self.repack_label_var = StringVar()

            #self.repack_cd_var.set(self.cfg.get(CFG_KEY_repack_cd))
            #self.repack_crc_var.set(self.cfg.get(CFG_KEY_repack_crc))

            self.repack_compr_var.set(9)
            self.repack_compr_var_int.set(9)
            self.repack_label_var.set('')

            (label_frame := LabelFrame(self.repack_dialog.area_main,text=STR('Record Label'),bd=2,bg=self.bg_color,takefocus=False)).grid(row=0,column=0,sticky='news',padx=4,pady=4,columnspan=2)
            Entry(label_frame,textvariable=self.repack_label_var).pack(expand='yes',fill='x',padx=2,pady=2)

            (repack_frame := LabelFrame(self.repack_dialog.area_main,text=STR('Data options'),bd=2,bg=self.bg_color,takefocus=False)).grid(row=1,column=0,sticky='news',padx=4,pady=4,columnspan=2)
            self.repack_dialog.area_main.grid_columnconfigure( 0, weight=1)
            self.repack_dialog.area_main.grid_columnconfigure( 1, weight=1)

            self.repack_dialog.area_main.grid_rowconfigure( 2, weight=1)

            self.repack_cd_cb = Checkbutton(repack_frame,text=STR("Keep 'Custom Data'"),variable=self.repack_cd_var)

            self.repack_cd_cb.grid(row=0, column=0, sticky='wens',padx=4,pady=4)

            repack_frame.grid_columnconfigure( 0, weight=1)

            (repack_frame_compr := LabelFrame(self.repack_dialog.area_main,text=STR('Compression (0-22)'),bd=2,bg=self.bg_color,takefocus=False)).grid(row=2,column=0,sticky='news',padx=4,pady=4,columnspan=2)

            Scale(repack_frame_compr, variable=self.repack_compr_var, orient='horizontal',from_=0, to=22,command=lambda x : self.repack_comp_set(),style="TScale").pack(fill='x',side='left',expand=1,padx=2)
            Label(repack_frame_compr, textvariable=self.repack_compr_var_int,width=3,bg=self.bg_color,relief='ridge').pack(side='right',padx=2,pady=2)

            Button(self.repack_dialog.area_buttons, text=STR('Proceed'), width=14 , command= self.repack_to_local).pack(side='left', anchor='n',padx=5,pady=5)
            Button(self.repack_dialog.area_buttons, text=STR('Close'), width=14, command=self.repack_dialog.hide ).pack(side='right', anchor='n',padx=5,pady=5)

            self.repack_dialog_created = True
        return self.repack_dialog

    def wii_import_dialog_name_state(self):
        self.wii_import_label_entry.configure(state='disabled' if self.wii_import_separate.get() else 'normal')

    wii_import_dialog_created = False
    @restore_status_line
    @block
    def get_wii_import_dialog(self):
        self.wii_import_dialog_do_it=False

        if not self.wii_import_dialog_created:
            self.wii_import_dialog=GenericDialog(self.main,self.main_icon_tuple,self.bg_color,STR('Where Is It ? Import Records'),pre_show=self.pre_show,post_close=self.post_close,min_width=400,min_height=200)
            self.wii_import_separate = BooleanVar()
            self.wii_import_separate.set(False)
            self.wii_import_compr_var = IntVar()
            self.wii_import_compr_var_int = IntVar()
            self.wii_import_label_var = StringVar()

            self.wii_import_compr_var.set(9)
            self.wii_import_compr_var_int.set(9)

            self.wii_import_brief_label=Label(self.wii_import_dialog.area_main,text='',bd=2,bg=self.bg_color,takefocus=False,relief='groove',anchor='w',justify='left')
            self.wii_import_brief_label.grid(row=0,column=0,sticky='news',padx=4,pady=4,columnspan=2)
            try:
                self.wii_import_brief_label.configure(font=('Courier', 10))
            except:
                try:
                    self.wii_import_brief_label.configure(font=('TkFixedFont', 10))
                except:
                    pass

            #(label_frame := LabelFrame(self.wii_import_dialog.area_main,text='Record Label',bd=2,bg=self.bg_color,takefocus=False)).grid(row=1,column=0,sticky='news',padx=4,pady=4,columnspan=2)

            (wii_import_frame := LabelFrame(self.wii_import_dialog.area_main,text=STR('Options'),bd=2,bg=self.bg_color,takefocus=False)).grid(row=2,column=0,sticky='news',padx=4,pady=4,columnspan=2)
            self.wii_import_dialog.area_main.grid_columnconfigure( 0, weight=1)
            self.wii_import_dialog.area_main.grid_columnconfigure( 1, weight=1)

            self.wii_import_dialog.area_main.grid_rowconfigure( 2, weight=1)

            self.wii_import_separate_cb = Checkbutton(wii_import_frame,text=' ' + STR('Separate record per each disk (not recommended)'),variable=self.wii_import_separate,command = self.wii_import_dialog_name_state)
            self.wii_import_separate_cb.grid(row=0, column=0, sticky='wens',padx=4,pady=4,columnspan=2)

            Label(wii_import_frame,text=STR('Common record label:'),bg=self.bg_color,anchor='w').grid(row=1, column=0, sticky='wens',padx=4,pady=4)
            self.wii_import_label_entry = Entry(wii_import_frame,textvariable=self.wii_import_label_var)
            self.wii_import_label_entry.grid(row=1, column=1, sticky='wens',padx=4,pady=4)

            wii_import_frame.grid_columnconfigure( 1, weight=1)

            (wii_import_frame_compr := LabelFrame(self.wii_import_dialog.area_main,text=STR('Compression (0-22)'),bd=2,bg=self.bg_color,takefocus=False)).grid(row=3,column=0,sticky='news',padx=4,pady=4,columnspan=2)

            Scale(wii_import_frame_compr, variable=self.wii_import_compr_var, orient='horizontal',from_=0, to=22,command=lambda x : self.wii_import_comp_set(),style="TScale").pack(fill='x',side='left',expand=1,padx=2)
            Label(wii_import_frame_compr, textvariable=self.wii_import_compr_var_int,width=3,bg=self.bg_color,relief='ridge').pack(side='right',padx=2,pady=2)

            Button(self.wii_import_dialog.area_buttons, text=STR('Proceed'), width=14 , command= self.wii_import_to_local).pack(side='left', anchor='n',padx=5,pady=5)
            Button(self.wii_import_dialog.area_buttons, text=STR('Close'), width=14, command=self.wii_import_dialog.hide ).pack(side='right', anchor='n',padx=5,pady=5)

            self.wii_import_dialog_created = True

        return self.wii_import_dialog

    entry_ask_dialog_created = False
    @restore_status_line
    @block
    def get_entry_ask_dialog(self):
        if not self.entry_ask_dialog_created:
            self.status(STR("Creating dialog ..."))
            self.entry_ask_dialog = EntryDialogQuestion(self.main,self.main_icon_tuple,self.bg_color,pre_show=self.pre_show,post_close=self.post_close)
            self.entry_ask_dialog.cancel_button.configure(text=STR('Cancel'))

            self.entry_ask_dialog_created = True
        return self.entry_ask_dialog

    assign_to_group_dialog_created = False
    @restore_status_line
    @block
    def get_assign_to_group_dialog(self):
        if not self.assign_to_group_dialog_created:
            self.status(STR("Creating dialog ..."))
            self.assign_to_group_dialog = ComboboxDialogQuestion(self.main,self.main_icon_tuple,self.bg_color,pre_show=self.pre_show,post_close=self.post_close)
            self.assign_to_group_dialog_created = True
        return self.assign_to_group_dialog

    settings_dialog_created = False
    @restore_status_line
    @block
    def get_settings_dialog(self):
        if not self.settings_dialog_created:
            self.status(STR("Creating dialog ..."))

            self.settings_dialog=GenericDialog(self.main,self.main_icon_tuple,self.bg_color,STR('Settings'),pre_show=self.pre_show,post_close=self.post_close)

            self.theme = StringVar()

            sfdma = self.settings_dialog.area_main

            lang_frame = Frame(sfdma)
            lang_frame.grid(row=0, column=0, sticky='news',padx=4,pady=4)

            Label(lang_frame,text=STR('Language:'),anchor='w').grid(row=0, column=0, sticky='wens',padx=8,pady=4)

            self.lang_var = StringVar()
            self.lang_cb = Combobox(lang_frame,values=list(langs.lang_dict.keys()),textvariable=self.lang_var,state='readonly',width=16)
            self.lang_cb.grid(row=0, column=1, sticky='news',padx=4,pady=4)

            Label(lang_frame,text=STR('Theme') + ':',anchor='w').grid(row=0, column=3, sticky='wens',padx=8,pady=4)
            self.theme_var = StringVar()

            self.theme_cb = Combobox(lang_frame,values=list(self.themes_combos.keys()),textvariable=self.theme_var,state='readonly',width=16)
            self.theme_cb.grid(row=0, column=4, sticky='news',padx=4,pady=4)

            lang_frame.grid_columnconfigure( 2, weight=1)

            #self.lang_cb.bind('<<ComboboxSelected>>', self.lang_change)

            self.show_popups_var = BooleanVar()
            self.popups_cb = Checkbutton(sfdma,text=' ' + STR('Show tooltips'),variable=self.show_popups_var)
            self.popups_cb.grid(row=1, column=0, sticky='news',padx=4,pady=4)

            self.groups_collapsed_var = BooleanVar()
            self.popups_cb = Checkbutton(sfdma,text=' ' + STR('Groups collapsed at startup'),variable=self.groups_collapsed_var)
            self.popups_cb.grid(row=2, column=0, sticky='news',padx=4,pady=4)

            self.scan_hidden_var = BooleanVar()
            self.scan_hidden_cb = Checkbutton(sfdma,text=' ' + STR('Include hidden files / folders in scan'),variable=self.scan_hidden_var)
            self.scan_hidden_cb.grid(row=3, column=0, sticky='news',padx=4,pady=4)

            find_frame=LabelFrame(sfdma, text=STR("Searching"),borderwidth=2,bg=self.bg_color)
            find_frame.grid(row=4,column=0,sticky='wens',padx=3,pady=3)

            self.search_after_action_var = BooleanVar()
            self.search_after_action0_cb = Radiobutton(find_frame,text=' ' + STR('Close dialog after searching'),variable=self.search_after_action_var,value=0)
            self.search_after_action0_cb.grid(row=0, column=0, sticky='news',padx=4,pady=4)

            self.search_after_action1_cb = Radiobutton(find_frame,text=' ' + STR('Show results dialog after searching'),variable=self.search_after_action_var,value=1)
            self.search_after_action1_cb.grid(row=1, column=0, sticky='news',padx=4,pady=4)

            self.select_found_var = BooleanVar()
            self.select_found_cb = Checkbutton(find_frame,text=' ' + STR('Select first found item after searching'),variable=self.select_found_var)
            self.select_found_cb.grid(row=2, column=0, sticky='news',padx=0,pady=4)

            self.expand_search_results_var = BooleanVar()
            self.expand_search_results_cb = Checkbutton(find_frame,text=' ' + STR('Expand record on search results dialog'),variable=self.expand_search_results_var)
            self.expand_search_results_cb.grid(row=3, column=0, sticky='news',padx=0,pady=4)

            sfdma.grid_columnconfigure( 0, weight=1)
            sfdma.grid_rowconfigure( 9, weight=1)

            bfr=Frame(self.settings_dialog.area_main,bg=self.bg_color)

            bfr.grid(row=10,column=0)

            Button(bfr, text=STR('Set defaults'),width=16, command=self.settings_reset).pack(side='left', anchor='n',padx=5,pady=5)
            Button(bfr, text='OK', width=16, command=self.settings_ok ).pack(side='left', anchor='n',padx=5,pady=5,fill='both')
            self.cancel_button=Button(bfr, text=STR('Cancel'), width=16 ,command=self.settings_dialog.hide )
            self.cancel_button.pack(side='right', anchor='n',padx=5,pady=5)

            self.settings_dialog_created = True

            self.settings = [
                (self.show_popups_var,CFG_KEY_show_popups),
                (self.groups_collapsed_var,CFG_KEY_groups_collapse),
                (self.scan_hidden_var,CFG_KEY_include_hidden),
                (self.select_found_var,CFG_KEY_select_found),
                (self.search_after_action_var,CFG_KEY_after_action),
                (self.expand_search_results_var,CFG_KEY_expand_search_results)
            ]

            self.settings_str = [
                (self.theme,CFG_THEME)
            ]

        self.show_popups_var.set(self.cfg.get(CFG_KEY_show_popups))
        self.groups_collapsed_var.set(self.cfg.get(CFG_KEY_groups_collapse))
        self.scan_hidden_var.set(self.cfg.get(CFG_KEY_include_hidden))
        self.select_found_var.set(self.cfg.get(CFG_KEY_select_found))
        self.search_after_action_var.set(self.cfg.get(CFG_KEY_after_action))
        self.expand_search_results_var.set(self.cfg.get(CFG_KEY_expand_search_results))
        self.lang_var.set(self.cfg_get(CFG_LANG))
        self.theme_var.set(self.cfg_get(CFG_THEME))

        return self.settings_dialog

    def settings_reset(self):
        _ = {var.set(cfg_defaults[key]) for var,key in self.settings}
        _ = {var.set(cfg_defaults[key]) for var,key in self.settings_str}

    def settings_ok(self):
        need_restart=False

        if self.cfg_get(CFG_LANG)!=self.lang_var.get():
            new_val = self.lang_var.get()
            self.cfg.set(CFG_LANG,new_val)
            self.get_info_dialog_on_settings().show(STR('Language Changed'),STR('Application restart required\nfor changes to take effect',new_val) + '\n\n' + STR('Translations are made using AI\nIf any corrections are necessary,\nplease contact the author.',new_val) )

            need_restart=True

        if self.cfg_get(CFG_THEME)!=self.theme_var.get():
            self.cfg.set(CFG_THEME,self.theme_var.get())

            if not need_restart:
                self.get_info_dialog_on_settings().show(STR('Theme Changed'),STR('Application restart required\nfor changes to take effect'))

        if self.cfg.get(CFG_KEY_show_popups)!=self.show_popups_var.get():
            self.cfg.set(CFG_KEY_show_popups,self.show_popups_var.get())

        if self.cfg.get(CFG_KEY_groups_collapse)!=self.groups_collapsed_var.get():
            self.cfg.set(CFG_KEY_groups_collapse,self.groups_collapsed_var.get())

        if self.cfg.get(CFG_KEY_include_hidden)!=self.scan_hidden_var.get():
            self.cfg.set(CFG_KEY_include_hidden,self.scan_hidden_var.get())

        if self.cfg.get(CFG_KEY_select_found)!=self.select_found_var.get():
            self.cfg.set(CFG_KEY_select_found,self.select_found_var.get())

        if self.cfg.get(CFG_KEY_after_action)!=self.search_after_action_var.get():
            self.cfg.set(CFG_KEY_after_action,self.search_after_action_var.get())

        if self.cfg.get(CFG_KEY_expand_search_results)!=self.expand_search_results_var.get():
            self.cfg.set(CFG_KEY_expand_search_results,self.expand_search_results_var.get())

        self.settings_dialog.hide()

    find_dialog_created = False
    @restore_status_line
    @block
    def get_find_dialog(self):
        if not self.find_dialog_created:
            self.status(STR("Creating dialog ..."))

            ###################################
            #self.find_dialog=GenericDialog(self.main,self.main_icon_tuple,self.bg_color,STR('Search records'),pre_show=self.pre_show,post_close=self.post_close)
            self.find_dialog=GenericDialog(self.main,self.main_icon_tuple,self.bg_color,STR('Search records'),pre_show=lambda new_widget : self.pre_show(on_main_window_dialog=True,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=True))

            #self.find_size_use_var = BooleanVar()
            self.find_filename_search_kind_var = StringVar()
            self.find_cd_search_kind_var = StringVar()

            self.find_range_all = BooleanVar()
            self.type_folders_var = BooleanVar()
            self.type_files_var = BooleanVar()

            self.find_size_min_var = StringVar()
            self.find_size_max_var = StringVar()

            self.find_modtime_min_var = StringVar()
            self.find_modtime_max_var = StringVar()

            self.find_name_regexp_var = StringVar()
            self.find_name_glob_var = StringVar()
            self.find_name_fuzz_var = StringVar()

            self.find_name_case_sens_var = BooleanVar()
            self.find_name_fuzzy_threshold = StringVar()

            self.find_cd_regexp_var = StringVar()
            self.find_cd_glob_var = StringVar()
            self.find_cd_fuzz_var = StringVar()

            self.find_cd_case_sens_var = BooleanVar()
            self.find_cd_fuzzy_threshold = StringVar()
            ##############

            def ver_number(var):
                temp=str_to_bytes(var)

                if temp>0:
                    return var

                return ''

            try:
                self.find_range_all.set(self.cfg.get(CFG_KEY_find_range_all))
            except Exception as d1:
                print(d1)

            try:
                self.type_folders_var.set(self.cfg.get(CFG_KEY_type_folders))
                self.type_files_var.set(self.cfg.get(CFG_KEY_type_files))
            except Exception as d2:
                print(d2)

            self.find_cd_search_kind_var.set(self.cfg.get(CFG_KEY_find_cd_search_kind))
            self.find_filename_search_kind_var.set(self.cfg.get(CFG_KEY_find_filename_search_kind))

            self.find_size_min_var.set(ver_number(self.cfg.get(CFG_KEY_find_size_min)))
            self.find_size_max_var.set(ver_number(self.cfg.get(CFG_KEY_find_size_max)))

            self.find_modtime_min_var.set(self.cfg.get(CFG_KEY_find_modtime_min))
            self.find_modtime_max_var.set(self.cfg.get(CFG_KEY_find_modtime_max))

            self.find_name_regexp_var.set(self.cfg.get(CFG_KEY_find_name_regexp))
            self.find_name_glob_var.set(self.cfg.get(CFG_KEY_find_name_glob))
            self.find_name_fuzz_var.set(self.cfg.get(CFG_KEY_find_name_fuzz))
            self.find_name_case_sens_var.set(self.cfg.get(CFG_KEY_find_name_case_sens))

            self.find_cd_regexp_var.set(self.cfg.get(CFG_KEY_find_cd_regexp))
            self.find_cd_glob_var.set(self.cfg.get(CFG_KEY_find_cd_glob))
            self.find_cd_fuzz_var.set(self.cfg.get(CFG_KEY_find_cd_fuzz))
            self.find_cd_case_sens_var.set(self.cfg.get(CFG_KEY_find_cd_case_sens))

            self.find_name_fuzzy_threshold.set(self.cfg.get(CFG_KEY_filename_fuzzy_threshold))
            self.find_cd_fuzzy_threshold.set(self.cfg.get(CFG_KEY_cd_fuzzy_threshold))

            ##############

            sfdma = self.find_dialog.area_main

            (find_range_frame := LabelFrame(sfdma,text=STR('Search range'),bd=2,bg=self.bg_color,takefocus=False)).grid(row=0,column=0,sticky='news',padx=4,pady=4)
            self.find_range_cb1 = Radiobutton(find_range_frame,text=' ' + STR('Selected record / group'),variable=self.find_range_all,value=False,command=self.find_mod)
            self.find_range_cb1.grid(row=0, column=0, sticky='news',padx=4,pady=4)
            self.find_range_cb1.bind('<Return>', lambda event : self.find_items())

            find_range_cb2 = Radiobutton(find_range_frame,text=' ' + STR('All records'),variable=self.find_range_all,value=True,command=self.find_mod)
            find_range_cb2.grid(row=0, column=1, sticky='news',padx=4,pady=4)
            find_range_cb2.bind('<Return>', lambda event : self.find_items())

            find_range_frame.grid_columnconfigure( 0, weight=1)
            find_range_frame.grid_columnconfigure( 1, weight=1)

            (type_frame := LabelFrame(sfdma,text=STR('Kind'),bd=2,bg=self.bg_color,takefocus=False)).grid(row=1,column=0,sticky='news',padx=4,pady=4)
            self.type_folder_cb = Checkbutton(type_frame,text=' ' + STR('Folders'),variable=self.type_folders_var,command=lambda : self.find_mod('folders'))
            self.type_folder_cb.grid(row=0, column=0, sticky='news',padx=4,pady=4)
            self.type_folder_cb.bind('<Return>', lambda event : self.find_items())

            type_files_cb = Checkbutton(type_frame,text=' ' + STR('Files'),variable=self.type_files_var,command=lambda : self.find_mod('files'))
            type_files_cb.grid(row=1, column=0, sticky='news',padx=4,pady=4)
            type_files_cb.bind('<Return>', lambda event : self.find_items())

            type_frame.grid_columnconfigure( 0, weight=1)

            (find_filename_frame := LabelFrame(sfdma,text=STR('Path'),bd=2,bg=self.bg_color,takefocus=False)).grid(row=2,column=0,sticky='news',padx=4,pady=4)

            r_dont = Radiobutton(find_filename_frame,text= ' ' + STR("Don't use this criterion"),variable=self.find_filename_search_kind_var,value='dont',command=self.find_mod,width=30)
            r_dont.grid(row=0, column=0, sticky='news',padx=4,pady=4)
            r_dont.bind('<Return>', lambda event : self.find_items())

            #Radiobutton(find_filename_frame,text="files with error on access",variable=self.find_filename_search_kind_var,value='error',command=self.find_mod)
            #.grid(row=1, column=0, sticky='news',padx=4,pady=4)

            regexp_radio_name=Radiobutton(find_filename_frame,text=' ' + STR("By regular expression"),variable=self.find_filename_search_kind_var,value='regexp',command=self.find_mod)
            regexp_radio_name.grid(row=2, column=0, sticky='news',padx=4,pady=4)
            regexp_radio_name.bind('<Return>', lambda event : self.find_items())

            glob_radio_name=Radiobutton(find_filename_frame,text=' ' + STR("By glob pattern"),variable=self.find_filename_search_kind_var,value='glob',command=self.find_mod)
            glob_radio_name.grid(row=3, column=0, sticky='news',padx=4,pady=4)
            glob_radio_name.bind('<Return>', lambda event : self.find_items())

            fuzzy_radio_name=Radiobutton(find_filename_frame,text=' ' + STR("By fuzzy match"),variable=self.find_filename_search_kind_var,value='fuzzy',command=self.find_mod)
            fuzzy_radio_name.grid(row=4, column=0, sticky='news',padx=4,pady=4)
            fuzzy_radio_name.bind('<Return>', lambda event : self.find_items())

            regexp_tooltip = STR("Regular expression") + "\n"
            regexp_tooltip_name = STR('Checked on the file or folder name.')
            regexp_tooltip_cd = STR('Checked on the entire Custom Data of a file.')

            glob_tooltip = STR('GLOB_TOOLTIP')
            glob_tooltip_name = STR('Checked on the file or folder name.')
            glob_tooltip_cd = STR('Checked on the entire Custom Data of a file.')

            fuzzy_tooltip = STR('FUZZY_TOOLTIP')
            fuzzy_tooltip_name = STR('based on the file or folder name.')
            fuzzy_tooltip_cd = STR('based on the entire Custom Data of a file.')

            self.find_filename_regexp_entry = Entry(find_filename_frame,textvariable=self.find_name_regexp_var,validate="key")
            self.find_filename_glob_entry = Entry(find_filename_frame,textvariable=self.find_name_glob_var,validate="key")
            self.find_filename_fuzz_entry = Entry(find_filename_frame,textvariable=self.find_name_fuzz_var,validate="key")

            self.find_filename_regexp_entry.bind("<KeyRelease>", self.find_mod_keypress)
            self.find_filename_glob_entry.bind("<KeyRelease>", self.find_mod_keypress)
            self.find_filename_fuzz_entry.bind("<KeyRelease>", self.find_mod_keypress)

            self.find_filename_regexp_entry.grid(row=2, column=1, sticky='we',padx=4,pady=4)
            self.find_filename_glob_entry.grid(row=3, column=1, sticky='we',padx=4,pady=4)
            self.find_filename_fuzz_entry.grid(row=4, column=1, sticky='we',padx=4,pady=4)

            self.find_filename_case_sens_cb = Checkbutton(find_filename_frame,text=' ' + STR('Case sensitive'),variable=self.find_name_case_sens_var,command=self.find_mod)
            self.find_filename_case_sens_cb.grid(row=3, column=2, sticky='wens',padx=4,pady=4,columnspan=2)

            self.find_filename_fuzzy_threshold_lab = Label(find_filename_frame,text=' ' + STR('Threshold:'),bg=self.bg_color,anchor='e')
            self.find_filename_fuzzy_threshold_entry = Entry(find_filename_frame,textvariable=self.find_name_fuzzy_threshold)
            self.find_filename_fuzzy_threshold_lab.grid(row=4, column=2, sticky='wens',padx=4,pady=4)
            self.find_filename_fuzzy_threshold_entry.grid(row=4, column=3, sticky='wens',padx=4,pady=4)

            self.find_filename_fuzzy_threshold_entry.bind("<KeyRelease>", self.find_mod_keypress)

            self.widget_tooltip(regexp_radio_name,regexp_tooltip + regexp_tooltip_name)
            self.widget_tooltip(self.find_filename_regexp_entry,regexp_tooltip + regexp_tooltip_name)
            self.widget_tooltip(glob_radio_name,glob_tooltip + glob_tooltip_name)
            self.widget_tooltip(self.find_filename_glob_entry,glob_tooltip + glob_tooltip_name)

            self.widget_tooltip(fuzzy_radio_name,fuzzy_tooltip + fuzzy_tooltip_name)
            self.widget_tooltip(self.find_filename_fuzz_entry,fuzzy_tooltip + fuzzy_tooltip_name)
            self.widget_tooltip(self.find_filename_fuzzy_threshold_entry,fuzzy_tooltip + fuzzy_tooltip_name)

            find_filename_frame.grid_columnconfigure( 1, weight=1)

            (find_cd_frame := LabelFrame(sfdma,text=STR('Custom Data'),bd=2,bg=self.bg_color,takefocus=False)).grid(row=3,column=0,sticky='news',padx=4,pady=4)

            r_dont2 = Radiobutton(find_cd_frame,text=' ' + STR("Don't use this criterion"),variable=self.find_cd_search_kind_var,value='dont',command=self.find_mod,width=30)
            r_dont2.grid(row=0, column=0, sticky='news',padx=4,pady=4)
            r_dont2.bind('<Return>', lambda event : self.find_items())

            r_without = Radiobutton(find_cd_frame,text=' ' + STR("No Custom Data"),variable=self.find_cd_search_kind_var,value='without',command=self.find_mod)
            r_without.grid(row=1, column=0, sticky='news',padx=4,pady=4)
            r_without.bind('<Return>', lambda event : self.find_items())

            r_correct = Radiobutton(find_cd_frame,text=' ' + STR("Any correct Custom Data"),variable=self.find_cd_search_kind_var,value='any',command=self.find_mod)
            r_correct.grid(row=2, column=0, sticky='news',padx=4,pady=4)
            r_correct.bind('<Return>', lambda event : self.find_items())

            r_error = Radiobutton(find_cd_frame,text=' ' + STR("Error on CD extraction"),variable=self.find_cd_search_kind_var,value='error',command=self.find_mod)
            r_error.grid(row=3, column=0, sticky='news',padx=4,pady=4)
            r_error.bind('<Return>', lambda event : self.find_items())

            r_error_empty = Radiobutton(find_cd_frame,text=' ' + STR("No CD extracted (empty value)"),variable=self.find_cd_search_kind_var,value='empty',command=self.find_mod)
            r_error_empty.grid(row=4, column=0, sticky='news',padx=4,pady=4)
            r_error_empty.bind('<Return>', lambda event : self.find_items())

            r_error_empty = Radiobutton(find_cd_frame,text=' ' + STR("CD extraction aborted"),variable=self.find_cd_search_kind_var,value='aborted',command=self.find_mod)
            r_error_empty.grid(row=5, column=0, sticky='news',padx=4,pady=4)
            r_error_empty.bind('<Return>', lambda event : self.find_items())

            regexp_radio_cd = Radiobutton(find_cd_frame,text=' ' + STR("By regular expression"),variable=self.find_cd_search_kind_var,value='regexp',command=self.find_mod)
            regexp_radio_cd.grid(row=6, column=0, sticky='news',padx=4,pady=4)
            regexp_radio_cd.bind('<Return>', lambda event : self.find_items())

            glob_radio_cd = Radiobutton(find_cd_frame,text=' ' + STR("By glob pattern"),variable=self.find_cd_search_kind_var,value='glob',command=self.find_mod)
            glob_radio_cd.grid(row=7, column=0, sticky='news',padx=4,pady=4)
            glob_radio_cd.bind('<Return>', lambda event : self.find_items())

            fuzzy_radio_cd = Radiobutton(find_cd_frame,text=' ' + STR("By fuzzy match"),variable=self.find_cd_search_kind_var,value='fuzzy',command=self.find_mod)
            fuzzy_radio_cd.grid(row=8, column=0, sticky='news',padx=4,pady=4)
            fuzzy_radio_cd.bind('<Return>', lambda event : self.find_items())

            self.find_cd_regexp_entry = Entry(find_cd_frame,textvariable=self.find_cd_regexp_var,validate="key")
            self.find_cd_glob_entry = Entry(find_cd_frame,textvariable=self.find_cd_glob_var,validate="key")
            self.find_cd_fuzz_entry = Entry(find_cd_frame,textvariable=self.find_cd_fuzz_var,validate="key")

            self.find_cd_regexp_entry.bind("<KeyRelease>", self.find_mod_keypress)
            self.find_cd_glob_entry.bind("<KeyRelease>", self.find_mod_keypress)
            self.find_cd_fuzz_entry.bind("<KeyRelease>", self.find_mod_keypress)

            self.find_cd_regexp_entry.grid(row=6, column=1, sticky='we',padx=4,pady=4)
            self.find_cd_glob_entry.grid(row=7, column=1, sticky='we',padx=4,pady=4)
            self.find_cd_fuzz_entry.grid(row=8, column=1, sticky='we',padx=4,pady=4)

            self.cd_case_sens_cb = Checkbutton(find_cd_frame,text=' ' + STR('Case sensitive'),variable=self.find_cd_case_sens_var,command=self.find_mod)
            self.cd_case_sens_cb.grid(row=7, column=2, sticky='wens',padx=4,pady=4,columnspan=2)

            self.find_cd_fuzzy_threshold_lab = Label(find_cd_frame,text=' ' + STR('Threshold:'),bg=self.bg_color,anchor='e')
            self.find_cd_fuzzy_threshold_entry = Entry(find_cd_frame,textvariable=self.find_cd_fuzzy_threshold)
            self.find_cd_fuzzy_threshold_lab.grid(row=8, column=2, sticky='wens',padx=4,pady=4)
            self.find_cd_fuzzy_threshold_entry.grid(row=8, column=3, sticky='wens',padx=4,pady=4)

            self.find_cd_fuzzy_threshold_entry.bind("<KeyRelease>", self.find_mod_keypress)

            self.widget_tooltip(regexp_radio_cd,regexp_tooltip + regexp_tooltip_cd)
            self.widget_tooltip(self.find_cd_regexp_entry,regexp_tooltip + regexp_tooltip_cd)
            self.widget_tooltip(glob_radio_cd,glob_tooltip + glob_tooltip_cd)
            self.widget_tooltip(self.find_cd_glob_entry,glob_tooltip + glob_tooltip_cd)

            self.widget_tooltip(fuzzy_radio_cd,fuzzy_tooltip + fuzzy_tooltip_cd)
            self.widget_tooltip(self.find_cd_fuzz_entry,fuzzy_tooltip + fuzzy_tooltip_cd)
            self.widget_tooltip(self.find_cd_fuzzy_threshold_entry,fuzzy_tooltip + fuzzy_tooltip_cd)

            find_cd_frame.grid_columnconfigure(1, weight=1)

            (find_size_frame := LabelFrame(sfdma,text=STR('File size'),bd=2,bg=self.bg_color,takefocus=False)).grid(row=4,column=0,sticky='news',padx=4,pady=4)
            find_size_frame.grid_columnconfigure((0,1,2,3), weight=1)

            self.find_size_min_label=Label(find_size_frame,text='min: ',bg=self.bg_color,anchor='e',relief='flat',bd=2)
            self.find_size_min_label.grid(row=0, column=0, sticky='we',padx=4,pady=4)
            self.find_size_max_label=Label(find_size_frame,text='max: ',bg=self.bg_color,anchor='e',relief='flat',bd=2)
            self.find_size_max_label.grid(row=0, column=2, sticky='we',padx=4,pady=4)

            self.find_size_min_entry=Entry(find_size_frame,textvariable=self.find_size_min_var)
            self.find_size_min_entry.grid(row=0, column=1, sticky='we',padx=4,pady=4)
            self.find_size_max_entry=Entry(find_size_frame,textvariable=self.find_size_max_var)
            self.find_size_max_entry.grid(row=0, column=3, sticky='we',padx=4,pady=4)

            self.find_size_min_entry.bind("<KeyRelease>", self.find_mod_keypress)
            self.find_size_max_entry.bind("<KeyRelease>", self.find_mod_keypress)

            size_tooltip = STR('SIZE_TOOLTIP')
            self.widget_tooltip(self.find_size_min_entry,size_tooltip)
            self.widget_tooltip(self.find_size_min_label,size_tooltip)
            self.widget_tooltip(self.find_size_max_entry,size_tooltip)
            self.widget_tooltip(self.find_size_max_label,size_tooltip)

            (find_modtime_frame := LabelFrame(sfdma,text=STR('File last modification time'),bd=2,bg=self.bg_color,takefocus=False)).grid(row=5,column=0,sticky='news',padx=4,pady=4)
            find_modtime_frame.grid_columnconfigure((0,1,2,3), weight=1)

            self.find_modtime_min_label=Label(find_modtime_frame,text='min: ',bg=self.bg_color,anchor='e',relief='flat',bd=2)
            self.find_modtime_min_label.grid(row=0, column=0, sticky='we',padx=4,pady=4)
            self.find_modtime_max_label=Label(find_modtime_frame,text='max: ',bg=self.bg_color,anchor='e',relief='flat',bd=2)
            self.find_modtime_max_label.grid(row=0, column=2, sticky='we',padx=4,pady=4)

            self.find_modtime_min_entry=Entry(find_modtime_frame,textvariable=self.find_modtime_min_var)
            self.find_modtime_min_entry.grid(row=0, column=1, sticky='we',padx=4,pady=4)
            self.find_modtime_max_entry=Entry(find_modtime_frame,textvariable=self.find_modtime_max_var)
            self.find_modtime_max_entry.grid(row=0, column=3, sticky='we',padx=4,pady=4)

            self.find_modtime_min_entry.bind("<KeyRelease>", self.find_mod_keypress)
            self.find_modtime_max_entry.bind("<KeyRelease>", self.find_mod_keypress)

            time_toltip = STR('TIME_TOOLTIP')
            self.widget_tooltip(self.find_modtime_min_entry,time_toltip)
            self.widget_tooltip(self.find_modtime_min_label,time_toltip)
            self.widget_tooltip(self.find_modtime_max_entry,time_toltip)
            self.widget_tooltip(self.find_modtime_max_label,time_toltip)

            self.search_butt = Button(self.find_dialog.area_buttons, text=STR('Search'), width=14, command=self.find_items )
            self.search_butt.pack(side='left', anchor='n',padx=5,pady=5)
            self.clear_res_butt = Button(self.find_dialog.area_buttons, text=STR('Clear results'), width=14, command=self.clear_results_search, state='disabled' )
            self.clear_res_butt.pack(side='left', anchor='n',padx=5,pady=5)
            self.search_show_butt = Button(self.find_dialog.area_buttons, text=STR('Show results'), width=14, command=self.find_show_results, state='disabled' )
            self.search_show_butt.pack(side='left', anchor='n',padx=5,pady=5)
            self.search_save_butt = Button(self.find_dialog.area_buttons, text=STR('Save results'), width=14, command=self.find_save_results, state='disabled' )
            self.search_save_butt.pack(side='left', anchor='n',padx=5,pady=5)

            Button(self.find_dialog.area_buttons, text=STR('Close'), width=14, command=self.find_close ).pack(side='right', anchor='n',padx=5,pady=5)

            sfdma.grid_rowconfigure(6, weight=1)
            sfdma.grid_columnconfigure(0, weight=1)

            self.info_dialog_on_find = LabelDialog(self.find_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget : self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))
            self.text_dialog_on_find = TextDialogInfo(self.find_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))

            self.fix_text_dialog(self.text_dialog_on_find)

            self.results_on_find = LabelDialogQuestion(self.find_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget : self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))

            self.results_on_find.cancel_button.configure(text=STR('Close'),width=20)

            self.results_on_find.ok_button.pack_forget()

            self.find_dialog_created = True

        return self.find_dialog

    search_results_dialog_created = False
    @restore_status_line

    def get_search_results_dialog(self):
        if not self.search_results_dialog_created:
            self.status(STR("Creating dialog ..."))

            self.search_results_dialog=GenericDialog(self.main,self.main_icon_tuple,self.bg_color,STR('Search results'),pre_show=lambda new_widget : self.pre_show(on_main_window_dialog=True,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=True),min_width=800,min_height=600 )
            #self.find_dialog.widget

            self.search_results_dialog.widget.bind('<Configure>', self.search_results_dialog_configure)
            self.search_results_dialog.do_command_after_show = self.search_results_dialog_post_show

            treeframe=Frame(self.search_results_dialog.area_main)
            treeframe.grid(row=0,column=0,sticky='news')

            buttonsframe=Frame(self.search_results_dialog.area_main)
            buttonsframe.grid(row=2,column=0,sticky='ns')

            results_tree = self.results_tree = Treeview(treeframe,takefocus=True,show=('tree','headings') )
            results_tree.pack(side='left',fill='both',expand=1)

            results_tree["columns"]=('data','size','size_h','ctime','ctime_h')
            results_tree["displaycolumns"]=('size_h','ctime_h')

            #results_tree["columns"]=('data','record','opened','path','size','size_h','ctime','ctime_h','kind')

            results_tree.heading('#0',text=STR('Name'),anchor='n')
            results_tree.heading('size_h',text=STR('Size'),anchor='n')
            results_tree.heading('ctime_h',text=STR('Time'),anchor='n')

            results_tree.column('#0', width=120, minwidth=100, stretch='yes')

            results_tree.column('size_h', width=120, minwidth=120, stretch='no',anchor='e')
            results_tree.column('ctime_h', width=160, minwidth=120, stretch='no',anchor='e')

            results_tree.bind('<ButtonPress-1>', self.tree_on_mouse_button_press_search_results)
            results_tree.bind('<Double-Button-1>', self.double_left_button_results_tree)
            results_tree.bind('<Return>', lambda event : self.return_results_tree())

            self.REAL_SORT_COLUMN_INDEX_RESULTS={}

            for disply_column in self.real_display_columns:
                self.REAL_SORT_COLUMN_INDEX_RESULTS[disply_column] = self.results_tree["columns"].index(self.REAL_SORT_COLUMN[disply_column])

            results_tree_yview = results_tree.yview
            self.results_tree_scrollbar = Scrollbar(treeframe, orient='vertical', command=results_tree_yview,takefocus=False)

            results_tree.configure(yscrollcommand=self.results_tree_scrollbar_set)

            self.search_results_dialog.focus=results_tree

            self.results_tree_scrollbar.pack(side='right',fill='y',expand=0)

            self.search_results_dialog.area_main.grid_rowconfigure(0,weight=1)

            Button(buttonsframe, text=STR('Clear results'), width=14, command=self.clear_results_search ).pack(side='left', anchor='n',padx=5,pady=5)
            Button(buttonsframe, text=STR('Another search'), width=14, command=self.find_results_search ).pack(side='left', anchor='n',padx=5,pady=5)
            Button(buttonsframe, text=STR('Save results'), width=14, command=self.find_save_results ).pack(side='left', anchor='n',padx=5,pady=5)
            Button(buttonsframe, text=STR('Close'), width=14, command=self.find_results_close ).pack(side='left', anchor='n',padx=5,pady=5)

            self.search_results_dialog.info_label=Label(self.search_results_dialog.area_main,text='',anchor='w',relief='ridge')
            self.search_results_dialog.info_label.grid(row=1,column=0,sticky='news',padx=4,pady=(4,2))

            self.search_results_dialog.area_main.grid_rowconfigure(0, weight=1)

            self.search_results_dialog_created = True

            geometry = self.cfg.get(CFG_geometry_search)
            if geometry:
                self.search_results_dialog.widget.geometry(geometry)

        return self.search_results_dialog

    def search_results_dialog_post_show(self):
        self.search_results_shown=True
        self.results_tree.focus_set()

    search_results_shown=False
    def search_results_dialog_configure(self,event):
        if self.search_results_shown:
            geometry = self.search_results_dialog.widget.geometry()
            self.cfg.set(CFG_geometry_search,str(geometry))

    def clear_results_search(self):
        self.find_clear()
        self.find_results_search()

    def find_results_search(self):
        self.find_results_close()
        self.finder_wrapper_show(False)

    def find_results_close(self):
        #self.found_item_to_data={}
        self.search_results_dialog.hide()

    about_dialog_created = False
    @restore_status_line
    @block
    def get_about_dialog(self):
        if not self.about_dialog_created:
            self.status(STR("Creating dialog ..."))

            self.about_dialog=GenericDialog(self.main,self.main_icon_tuple,self.bg_color,'',pre_show=self.pre_show,post_close=self.post_close)

            frame1 = LabelFrame(self.about_dialog.area_main,text='',bd=2,bg=self.bg_color,takefocus=False)
            frame1.grid(row=0,column=0,sticky='news',padx=4,pady=(4,2))
            self.about_dialog.area_main.grid_rowconfigure(1, weight=1)

            text= f'\n\nLibrer {VER_TIMESTAMP}\nAuthor: Piotr Jochymek\n\n{HOMEPAGE}\n\nPJ.soft.dev.x@gmail.com\n\n'

            Label(frame1,text=text,bg=self.bg_color,justify='center').pack(expand=1,fill='both')

            frame2 = LabelFrame(self.about_dialog.area_main,text='',bd=2,bg=self.bg_color,takefocus=False)
            frame2.grid(row=1,column=0,sticky='news',padx=4,pady=(2,4))

            lab2_text=  distro_info + '\n\nCurrent log file: ' + log_file

            lab_courier = Label(frame2,text=lab2_text,bg=self.bg_color,justify='center')
            lab_courier.pack(expand=1,fill='both')

            try:
                lab_courier.configure(font=('Courier', 10))
            except:
                try:
                    lab_courier.configure(font=('TkFixedFont', 10))
                except:
                    pass

            self.about_dialog_created = True

        return self.about_dialog

    license_dialog_created = False
    @restore_status_line
    @block
    def get_license_dialog(self):
        if not self.license_dialog_created:
            self.status(STR("Creating dialog ..."))

            try:
                self.license=Path(path_join(LIBRER_DIR,'LICENSE')).read_text(encoding='ASCII')
            except Exception as exception_0:
                l_error(exception_0)
                try:
                    self.license=Path(path_join(dirname(LIBRER_DIR),'LICENSE')).read_text(encoding='ASCII')
                except Exception as exception_2:
                    l_error(exception_2)
                    self.exit()

            self.license_dialog=GenericDialog(self.main,(self.ico_license,self.ico_license),self.bg_color,'',pre_show=self.pre_show,post_close=self.post_close,min_width=800,min_height=520)

            frame1 = LabelFrame(self.license_dialog.area_main,text='',bd=2,bg=self.bg_color,takefocus=False)
            frame1.grid(row=0,column=0,sticky='news',padx=4,pady=4)
            self.license_dialog.area_main.grid_rowconfigure(0, weight=1)

            lab_courier=Label(frame1,text=self.license,bg=self.bg_color,justify='center')
            lab_courier.pack(expand=1,fill='both')

            self.license_dialog_created = True

            try:
                lab_courier.configure(font=('Courier', 10))
            except:
                try:
                    lab_courier.configure(font=('TkFixedFont', 10))
                except:
                    pass

        return self.license_dialog

    @block
    def alias_name(self):
        item = self.sel_item

        is_group = bool(self.tree.tag_has(self.GROUP,item))
        is_record = bool(self.tree.tag_has(self.RECORD_RAW,item) or self.tree.tag_has(self.RECORD,item))

        if self.current_record and is_record:

            alias = librer_core.get_record_alias(self.current_record)

            alias_info = f' ({alias})' if alias else ''
            alias_init = alias if alias else self.current_record.header.label

            self.get_entry_ask_dialog().show(STR('Alias record name'),STR('New alias name for record') + ' "' + str(self.current_record.header.label) + '"' + str(alias_info) + ":",alias_init)

            if self.entry_ask_dialog.res_bool:
                alias = self.entry_ask_dialog.entry_val.get()
                if alias:
                    librer_core.alias_record_name(self.current_record,alias)
                    self.tree.item(item,text=alias)
        elif self.current_group and is_group:
            self.get_entry_ask_dialog().show(STR('Rename group'),STR("Group") + f" '{self.current_group}' " + STR("rename") + " :",self.current_group)

            if self.entry_ask_dialog.res_bool:
                rename = self.entry_ask_dialog.entry_val.get()
                if rename:
                    res2=librer_core.rename_group(self.current_group,rename)
                    if res2:
                        self.info_dialog_on_main.show(STR('Rename failed.'),res2)
                        self.alias_name()
                    else:
                        self.tree.item(item,text=rename)
                        self.current_group = rename
                        values = list(self.tree.item(item,'values'))
                        values[0]=rename
                        self.tree.item(item,values=values)

                        self.group_to_item[rename] = item
        else:
            pass
            #files/folders

        self.column_sort(self.tree)

    @restore_status_line
    @block
    def record_repack(self):
        group = None
        if self.current_group:
            group = self.current_group
        elif self.current_record :
            if group_temp:=librer_core.get_record_group(self.current_record):
                group = group_temp

        if self.current_record:
            dialog = self.get_repack_dialog()

            record_label = self.current_record.header.label
            record_name = librer_core.get_record_name(self.current_record)

            self.repack_label_var.set(record_label if record_label==record_name else record_label + "(" + record_name + ")")

            self.repack_compr_var.set(self.current_record.header.compression_level)
            self.repack_compr_var_int.set(self.current_record.header.compression_level)

            self.repack_cd_cb.configure(state='normal' if self.current_record.header.items_cd else 'disabled')
            self.repack_cd_var.set(bool(self.current_record.header.items_cd))

            dialog.show()

            if self.repack_dialog_do_it:
                if messages := librer_core.repack_record(self.current_record,self.repack_label_var.get(),self.repack_compr_var.get(),self.repack_cd_var.get(),self.single_record_show,group):
                    self.info_dialog_on_main.show(STR('Repacking failed'),'\n'.join(messages) )
                else:
                    self.find_clear()
                    self.info_dialog_on_main.show(STR('Repacking finished.'),STR('Check repacked record\nDelete original record manually if you want.'))

    def caf_import(self,pathcatname):
        from binascii import b2a_hex
        from struct import calcsize, unpack

        DEBUG = True

        ulModus = 1000000000
        ulMagicBase = 500410407

        sVersion = 8

        try:
            buffer = open(pathcatname, 'rb')
        except:
            return

        buffer_read = buffer.read

        def readbuf(fmt):
            return unpack(fmt, buffer_read(calcsize(fmt)))[0]

        delim = b'\x00'

        def readstring():
            chars={}
            i=0
            while 1:
                chr = buffer_read(1)
                if chr == delim:
                    break
                else:
                    chars[i]=chr
                    i+=1

            try:
                return b''.join([chr for i,chr in sorted(chars.items(), key=lambda x: x[0]) ]).decode('latin1')

            except Exception as e:
                return str(e)

        ul = readbuf('<L')  # 4 bytes
        if ul > 0 and ul % ulModus == ulMagicBase:
            m_sVersion = int(ul/ulModus)
        else:
            buffer.close()
            print("Incorrect magic number for caf file",pathcatname, "(", ul % ulModus, ")")
            return

        if m_sVersion > 2:
            m_sVersion = readbuf('h')  # 2 bytes

        #print(f'{m_sVersion=}')

        if m_sVersion > sVersion:
            print("Incompatible caf version for", pathcatname, "(", m_sVersion, ")")
            return

        m_timeDate = readbuf('<L')  # 4 bytes
        #print(f'{m_timeDate=}')

        if m_sVersion >= 2:
            m_strDevice = readstring()
            #print(f'{m_strDevice=}')

        m_strVolume = readstring()
        #print(f'{m_strVolume=}')

        m_strAlias = readstring()
        #print(f'{m_strAlias=}')

        # m_dwSerialNumber well, odd..
        bytesn = buffer.read(4)  # 4 bytes
        rawsn = b2a_hex(bytesn).decode().upper()
        sn = ''
        while rawsn:
            chunk = rawsn[-2:]
            rawsn = rawsn[:-2]
            sn += chunk
        m_dwSerialNumber = '%s-%s' % (sn[:4], sn[4:])

        #print(f'{m_dwSerialNumber=}')

        if m_sVersion >= 4:
            m_strComment = readstring()
            #print(f'{m_strComment=}')

        # m_fFreeSize - Starting version 1 the free size was saved
        if m_sVersion >= 1:
            m_fFreeSize = readbuf('<f')  # as megabytes (4 bytes)
        else:
            m_fFreeSize = -1  # unknow

        #print(f'{m_fFreeSize=}')

        if m_sVersion >= 6:
            m_sArchive = readbuf('h')  # 2 bytes
            if m_sArchive == -1:
                m_sArchive = 0

            #print(f'{m_sArchive=}')

        caf_folders_dict={}


        #########################################################
        lLen = readbuf('<l')  # 4 bytes
        #print(f"Folders:{lLen}")
        for l in range(lLen):
            if l == 0 or m_sVersion <= 3:
                m_pszName = readstring()
            if m_sVersion >= 3:
                m_lFiles = readbuf('<l')  # 4 bytes
                m_dTotalSize = readbuf('<d')  # 8 bytes

            caf_folders_dict[l]=(m_lFiles, m_dTotalSize)

        # files  : date, size, parentfolderid, filename
        # folder : date, -thisfolderid, parentfolderid, filename

        caf_names_dict=defaultdict(set)

        #########################################################
        lLen = readbuf('<l')  # 4 bytes
        #print(f"Files{lLen}")
        for l in range(lLen):
            date = readbuf('<L')
            m_lLength=readbuf('<l')
            m_sPathId = readbuf('H')
            m_pszName = readstring()

            caf_names_dict[m_sPathId].add( (date, m_lLength, m_pszName) )

        buffer.close()

        return m_timeDate, m_strDevice, m_strVolume, m_strAlias, m_dwSerialNumber, m_strComment, m_fFreeSize, m_sArchive, caf_folders_dict, caf_names_dict

    @restore_status_line
    @block
    def record_import_caf(self):
        initialdir = self.last_dir if self.last_dir else self.cwd

        group = None
        if self.current_group:
            group = self.current_group
        elif self.current_record :
            if group_temp:=librer_core.get_record_group(self.current_record):
                group = group_temp

        postfix = f' to group:{group}' if group else ''

        if import_filenames := askopenfilenames(initialdir=self.last_dir,parent = self.main,title=STR('Choose "Cathy" data file') + postfix, defaultextension=".caf",filetypes=[(STR("Cathy Files"),"*.caf"),(STR("All Files"),"*.*")]):
            self.last_dir = dirname(import_filenames[0])

            postfix=0

            for filename in import_filenames:
                m_timeDate, m_strDevice, m_strVolume, m_strAlias, m_dwSerialNumber, m_strComment, m_fFreeSize, m_sArchive, caf_folders_dict, caf_names_dict = self.caf_import(filename)

                m_timeStr = strftime('%Y/%m/%d %H:%M:%S',localtime_catched(m_timeDate))

                caf_info=f'Imported from "Cathy" database: {filename}\n----------------+------------------------------------------------------------------------------------------------\n  creation time : {m_timeStr}\n  device        : {m_strDevice}\n  volume        : {m_strVolume}\n  alias         : {m_strAlias}\n  serial number : {m_dwSerialNumber}\n  comment       : {m_strComment}\n  free size     : {m_fFreeSize}\n  archive       : {m_sArchive}\n----------------+------------------------------------------------------------------------------------------------'

                filenames_set={elem[2] for dir_elems in caf_names_dict.values() for elem in dir_elems}

                compr=9
                label=path_splitext(basename(filename))[0]

                sub_res = librer_core.import_records_caf_do(compr,postfix,label,caf_folders_dict, caf_names_dict,self.single_record_show,filenames_set,caf_info,group)
                postfix+=1

    def wii_import_to_local(self):
        self.wii_import_dialog_do_it=True
        self.wii_import_dialog.hide(True)

    @restore_status_line
    @block
    def record_import_wii(self):
        initialdir = self.last_dir if self.last_dir else self.cwd
        self.wii_import_dialog_do_it= False

        group = None
        if self.current_group:
            group = self.current_group
        elif self.current_record :
            if group_temp:=librer_core.get_record_group(self.current_record):
                group = group_temp

        postfix = f' to group:{group}' if group else ''

        if import_filenames := askopenfilenames(initialdir=self.last_dir,parent = self.main,title=STR('Choose "Where Is It?" Report xml files to import') + postfix, defaultextension=".xml",filetypes=[(STR("XML Files"),"*.xml"),(STR("All Files"),"*.*")]):
            self.status(STR('Parsing WII files ... '))
            self.main.update()
            dialog = self.get_progress_dialog_on_main()

            self.last_dir = dirname(import_filenames[0])

            res_list = [None]
            #self.abort_list = [False]
            wii_import_thread=Thread(target=lambda : librer_core.import_records_wii_scan(import_filenames,res_list) ,daemon=True)
            wii_import_thread_is_alive = wii_import_thread.is_alive
            wii_import_thread.start()

            wait_var=BooleanVar()
            wait_var_set = wait_var.set
            wait_var_set(False)
            wait_var_get = wait_var.get

            dialog.show(STR('Parsing file(s)'))

            self_main_after = self.main.after
            self_main_wait_variable = self.main.wait_variable

            dialog_update_lab_text = dialog.update_lab_text
            #dialog_area_main_update = dialog.area_main.update

            while wii_import_thread_is_alive():
                dialog_update_lab_text(0,f'disks:{fnumber(librer_core.wii_import_known_disk_names_len).rjust(14)}')
                dialog_update_lab_text(1,f'files:{fnumber(librer_core.wii_import_files_counter).rjust(14)}' )
                dialog_update_lab_text(2,f'space:{bytes_to_str(librer_core.wii_import_space).rjust(14)}')

                self_main_after(10,lambda : wait_var_set(not wait_var_get()))
                self_main_wait_variable(wait_var)
                #dialog_area_main_update()

            wii_import_thread.join()

            dialog.hide(True)

            if len(res_list[0])!=11:
                self.info_dialog_on_main.show(STR('Where Is It? Import failed'),str(res_list[0][1]))
                return

            quant_disks,quant_files,quant_folders,filenames_set,filenames_set_per_disk,wii_path_tuple_to_data,wii_path_tuple_to_data_per_disk,wii_paths_dict,wii_paths_dict_per_disk,cd_set,cd_set_per_disk = res_list[0]

            if quant_disks==0 or (quant_files==0 and quant_folders==0):
                self.info_dialog_on_main.show(STR('Where Is It? Import failed'),STR("No files / No folders"))
            else:
                ###########################
                dialog = self.get_wii_import_dialog()

                if len(import_filenames)>1:
                    self.wii_import_label_var.set('WII-imported-multiple-files')
                else:
                    self.wii_import_label_var.set(f'WII-imported-{Path(import_filenames[0]).stem}')

                self.wii_import_brief_label.configure(text=f'GATHERED DATA:\ndisks   : {fnumber(quant_disks).rjust(14)}\nfiles   : {fnumber(quant_files).rjust(14)}\nspace   : {bytes_to_str(librer_core.wii_import_space).rjust(14)}')
                #\nfolders : {fnumber(quant_folders)}

                dialog.show()

                compr = self.wii_import_compr_var.get()

                if self.wii_import_dialog_do_it:
                    postfix=0

                    if self.wii_import_separate.get():
                        res= []

                        for disk_name,wii_path_tuple_to_data_curr in wii_path_tuple_to_data_per_disk.items():
                            self.status(f'importing {disk_name} ... ')

                            label = disk_name
                            sub_res = librer_core.import_records_wii_do(compr,postfix,label,quant_files,quant_folders,filenames_set_per_disk[disk_name],wii_path_tuple_to_data_curr,wii_paths_dict_per_disk[disk_name],cd_set_per_disk[disk_name],self.single_record_show,group)
                            postfix+=1
                            if sub_res:
                                res.append(sub_res)

                        if res:
                            self.info_dialog_on_main.show(STR('Where Is It? Import failed'),'\n'.join(res))
                        else:
                            ###########################
                            #self.info_dialog_on_main.show('Where Is It? Import','Successful.')
                            self.find_clear()
                            self.column_sort(self.tree)
                            self.status('Where Is It? Import completed successfully.')

                    else:
                        label = self.wii_import_label_var.get()
                        self.status(f'importing {label} ... ')

                        res = librer_core.import_records_wii_do(compr,postfix,label,quant_files,quant_folders,filenames_set,wii_path_tuple_to_data,wii_paths_dict,cd_set,self.single_record_show,group)

                        if res:
                            self.info_dialog_on_main.show(STR('Where Is It? Import failed'),res)
                        else:
                            ###########################
                            #self.info_dialog_on_main.show('Where Is It? Import','Successful.')
                            self.find_clear()
                            self.column_sort(self.tree)
                            self.status('Where Is It? Import completed successfully.')

    #@restore_status_line
    @block
    def record_import(self):
        #initialdir = self.last_dir if self.last_dir else self.cwd

        group = None
        if self.current_group:
            group = self.current_group
        elif self.current_record :
            if group_temp:=librer_core.get_record_group(self.current_record):
                group = group_temp

        postfix = STR('to group:') + str(group) if group else ''

        if import_filenames := askopenfilenames(initialdir=self.last_dir,parent = self.main,title=STR('Choose record files to import') + ' ' + postfix, defaultextension=".dat",filetypes=[(STR("Dat Files"),"*.dat"),(STR("All Files"),"*.*")]):
            self.last_dir = dirname(import_filenames[0])
            if import_res := librer_core.import_records(import_filenames,self.single_record_show,group):
                self.info_dialog_on_main.show(STR('Import failed'),import_res)
            else:
                #self.info_dialog_on_main.show('Import','Successful.')
                self.find_clear()

                self.column_sort(self.tree)
                self.status(STR('Import completed successfully.'))

    @restore_status_line
    @block
    def record_export(self):
        if self.current_record:
            if export_file_path := asksaveasfilename(initialdir=self.last_dir,parent = self.main, initialfile = 'record.dat',defaultextension=".dat",filetypes=[(STR("Dat Files"),"*.dat"),(STR("All Files"),"*.*")]):
                self.last_dir = dirname(export_file_path)

                if export_res := librer_core.export_record(self.current_record,export_file_path):
                    self.info_dialog_on_main.show(STR('Export failed'),export_res)
                else:
                    self.info_dialog_on_main.show(STR('Export'),STR('Completed successfully.'))

    def focusin(self):
        if self.main_locked_by_child:
            self.main_locked_by_child.focus_set()
        else:
            self.tree.focus_set()

    def unpost(self):
        self.hide_tooltip()
        self.menubar_unpost()
        self.popup_unpost()

    tooltip_show_after_tree=''
    tooltip_show_after_widget=''

    def widget_leave(self):
        self.menubar_unpost()
        self.hide_tooltip()

    def motion_on_widget_cget(self,event,message=None):
        new_message= message + '\n' + event.widget.cget('text')
        self.motion_on_widget(event,new_message)

    def motion_on_widget(self,event,message=None):
        if message:
            self.tooltip_message[str(event.widget)]=message
        self.tooltip_show_after_widget = event.widget.after(1, self.show_tooltip_widget(event))

    def motion_on_tree(self,event):
        if not self.block_processing_stack:
            self.tooltip_show_after_tree = event.widget.after(1, self.show_tooltips_tree(event))

    def configure_tooltip(self,widget):
        try:
            self.tooltip_lab_configure(text=self.tooltip_message[str(widget)])
        except Exception as te:
            print(f'configure_tooltip error:{widget}:{te}')

    def adaptive_tooltip_geometry(self,event):
        x,y = self.tooltip_wm_geometry().split('+')[0].split('x')
        x_int=int(x)
        y_int=int(y)

        size_combo,x_main_off,y_main_off = self.main.wm_geometry().split('+')
        x_main_size,y_main_size = size_combo.split('x')

        x_middle = int(x_main_size)/2+int(x_main_off)
        y_middle = int(y_main_size)/2+int(y_main_off)

        if event.x_root>x_middle:
            x_mod = -x_int -20
        else:
            x_mod = 20

        if event.y_root>y_middle:
            y_mod = -y_int -5
        else:
            y_mod = 5

        self.tooltip_wm_geometry("+%d+%d" % (event.x_root + x_mod, event.y_root + y_mod))

    def show_tooltip_widget(self,event):
        self.unschedule_tooltip_widget(event)
        self.menubar_unpost()

        self.configure_tooltip(event.widget)

        self.tooltip_deiconify_wrapp()

        self.adaptive_tooltip_geometry(event)

    def get_item_record(self,item):
        tree = self.tree

        current_record_name=tree.set(item,'record')

        subpath_list=[]

        while not current_record_name:
            temp_record_name = tree.set(item,'record')

            if temp_record_name:
                current_record_name=temp_record_name
                break

            values = tree.item(item,'values')
            if values:
                data=values[0]
                subpath_list.append(data)

            item=tree.parent(item)

        subpath_list.reverse()
        return (item,current_record_name,subpath_list)

    def tooltip_deiconify_wrapp(self):
        if self.cfg.get(CFG_KEY_show_popups):
            self.tooltip_deiconify()

    def show_tooltips_tree(self,event):
        self.unschedule_tooltips_tree(event)
        self.menubar_unpost()

        tree = event.widget
        col=tree.identify_column(event.x)
        if col:
            colname=tree.column(col,'id')
            if tree.identify("region", event.x, event.y) == 'heading':
                if colname in ('path','size_h','ctime_h'):
                    self.tooltip_lab_configure(text='Sort by %s' % self.org_label[colname])
                    self.tooltip_deiconify_wrapp()
                else:
                    self.hide_tooltip()

            elif item := tree.identify('item', event.x, event.y):
                if col=="#0" :
                    record_item,record_name,subpath_list = self.get_item_record(item)

                    if record_item in self.item_to_record:
                        record = self.item_to_record[record_item]

                        raw_record_it_is = tree.tag_has(self.RECORD_RAW,item)
                        record_it_is = tree.tag_has(self.RECORD,item)

                        if raw_record_it_is or record_it_is:
                            self.tooltip_lab_configure(text=librer_core.record_info_alias_wrapper(record,record.txtinfo_basic + '\n\n(' + STR('Double click to show full record info') + ')') )
                        else:
                            scan_path = record.header.scan_path
                            subpath = sep + sep.join(subpath_list)

                            tooltip_list = [STR('scan path') + f' : {scan_path}']
                            tooltip_list.append(STR('subpath') + f'   : {subpath}')

                            if item in self.item_to_data:
                                data_tuple = self.item_to_data[item]
                                code = data_tuple[1]
                                is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,cd_aborted,cd_empty,aux2 = LUT_decode[code]

                                if is_symlink:
                                    tooltip_list.append('')
                                    tooltip_list.append(STR('Symlink'))

                                if is_bind:
                                    tooltip_list.append('')
                                    tooltip_list.append(STR('Binding (another device)'))

                                if has_cd:
                                    tooltip_list.append('')
                                    if not cd_ok:
                                        tooltip_list.append(STR('Custom Data Extraction ended with error'))
                                        tooltip_list.append('(' + STR('Double click to show Custom Data') + '.)')
                                    elif cd_aborted:
                                        tooltip_list.append(STR('Custom Data Extraction was aborted'))
                                        tooltip_list.append('(' + STR('Double click to show Custom Data') + '.)')
                                    elif cd_empty:
                                        tooltip_list.append(STR('Custom Data is empty'))
                                    else:
                                        tooltip_list.append('(' + STR('Double click to show Custom Data') + '.)')

                            self.tooltip_lab_configure(text='\n'.join(tooltip_list))

                        self.tooltip_deiconify_wrapp()

                    elif tree.tag_has(self.GROUP,item):
                        if values := tree.item(item,'values'):
                            name = values[0]
                            self.tooltip_lab_configure(text=STR('group') + f'   :{name}')
                        else:
                            self.tooltip_lab_configure(text='')

                    else:
                        self.tooltip_lab_configure(text='unknown_label')

                elif col:
                    coldata=tree.set(item,col)

                    if coldata:
                        self.tooltip_lab_configure(text=coldata)
                        self.tooltip_deiconify_wrapp()

                    else:
                        self.hide_tooltip()

        self.adaptive_tooltip_geometry(event)

    def unschedule_tooltip_widget(self,event):
        if self.tooltip_show_after_widget:
            event.widget.after_cancel(self.tooltip_show_after_widget)
            self.tooltip_show_after_widget = None

    def unschedule_tooltips_tree(self,event):
        if self.tooltip_show_after_tree:
            event.widget.after_cancel(self.tooltip_show_after_tree)
            self.tooltip_show_after_tree = None

    def hide_tooltip(self):
        self.tooltip_withdraw()

    status_curr_text='-'
    status_curr_image='-'

    def status_main(self,text='',image='',do_log=True):
        if text != self.status_curr_text or image!=self.status_curr_image:
            self.status_curr_text=text
            self.status_curr_image=image

            self.status_info.configure(text=text,image=image,compound='left')
            self.status_info.update()

            if do_log and text:
                l_info('STATUS:%s',text)

    def status_main_win(self,text='',image='',do_log=True):
        self.status_main(text.replace('\\\\',chr(92)).replace('\\\\',chr(92)),image,do_log)

    status=status_main_win if windows else status_main

    menu_state_stack=[]
    menu_state_stack_pop = menu_state_stack.pop
    menu_state_stack_append = menu_state_stack.append

    def menu_enable(self):
        norm = self.menubar_norm
        try:
            self.menu_state_stack_pop()
            if not self.menu_state_stack:
                norm(STR("File"))
                norm(STR("Help"))
        except Exception as e:
            l_error(e)

    def menu_disable(self):
        disable = self.menubar_disable

        self.menu_state_stack_append('x')
        disable(STR("File"))
        disable(STR("Help"))
        #self.menubar.update()

    def delete_window_wrapper(self):
        if not self.block_processing_stack:
            self.exit()
        else:
            self.status('WM_DELETE_WINDOW NOT exiting ...')

    def exit(self):
        #print(f'removing temp dir:{self.temp_dir}')
        rmtree(self.temp_dir)

        try:
            self.status('exiting ...')
            self.cfg.set(CFG_last_dir,self.last_dir)
            self.cfg.set(CFG_geometry,str(self.main.geometry()))
            self.status('saving config ...')
            self.cfg.write()
            self.status('exit.')
        except Exception as e:
            l_error(e)

        #self.main.withdraw()
        sys.exit(0)
        #self.main.destroy()

    any_valid_find_results=False

    find_params_changed=True

    @block
    def settings_show(self):
        dialog = self.get_settings_dialog()

        dialog.show(STR('Settings'))

    def finder_wrapper_show(self,from_main=True):
        if librer_core.records:

            if self.any_valid_find_results and from_main and self.all_records_find_results_can_show:
                self.find_show_results_core()
            else:
                self.finder_wrapper_show_finder()

    @block
    def finder_wrapper_show_finder(self):
        dialog = self.get_find_dialog()

        self.find_dialog_shown=True
        self.find_mod()
        self.searching_aborted = False

        dialog.show('Find')
        self.store_text_dialog_fields(self.text_dialog_on_find)

        self.find_dialog_shown=False

    def find_close(self):
        self.find_dialog.hide()

    found_item_to_data={}
    @restore_status_line
    @block
    def find_clear(self):
        self.status('Cleaning search results ...')

        librer_core.find_results_clean()

        self_tree_get_children = self.tree.get_children
        nodes_set = set(self_tree_get_children())
        nodes_set_pop = nodes_set.pop
        nodes_set_add = nodes_set.add
        self_tree_item = self.tree.item
        self_FOUND = self.FOUND

        while nodes_set:
            item=nodes_set_pop()

            tags=self_tree_item(item,'tags')
            if self_FOUND in tags:
                tags = set(tags)
                tags.remove(self_FOUND)
                self_tree_item(item,tags=list(tags))

            _ = {nodes_set_add(child) for child in self_tree_get_children(item)}

        self.status_find_tooltip(self.status_find_tooltip_default)

        self.any_valid_find_results = False
        self.external_find_params_change=True

        try:
            children=self.results_tree.get_children()

            if children:
                self.results_tree.delete(*children)
        except:
            pass


    def set_found(self):
        self_tree_get_children = self.tree.get_children
        self_tree_item = self.tree.item

        self_FOUND = self.FOUND

        for record in librer_core.records:
            record_item = self.record_to_item[record]

            nodes_set = set(self_tree_get_children(record_item))

            nodes_set_pop = nodes_set.pop
            nodes_set_add = nodes_set.add

            res_items = [ res_item for res_item,res_size,res_mtime in record.find_results ]

            while nodes_set:
                item=nodes_set_pop()

                if tuple(self.get_item_record(item)[2]) in res_items:
                    tags=self_tree_item(item,'tags')

                    self_tree_item(item,tags=list(tags) + [self_FOUND])

                _ = {nodes_set_add(child) for child in self_tree_get_children(item)}

    def find_prev(self):
        if not self.block_processing_stack:
            if not self.any_valid_find_results:
                self.finder_wrapper_show()
            else:
                self.select_find_result(-1)

    def find_next(self):
        if not self.block_processing_stack:
            if not self.any_valid_find_results:
                self.finder_wrapper_show()
            else:
                self.select_find_result(1)

    def find_save_results(self):
        if report_file_name := asksaveasfilename(parent = self.find_dialog.widget, initialfile = 'librer_search_report.txt',defaultextension=".txt",filetypes=[(STR("All Files"),"*.*"),(STR("Text Files"),"*.txt")]):
            self.status('saving file "%s" ...' % str(report_file_name))

            with open(report_file_name,'w') as report_file:
                report_file_write = report_file.write

                report_file_write('# ' + ('\n# ').join(self.search_info_lines) + '\n\n')
                for record in librer_core.records:
                    if record.find_results:
                        report_file_write(f'record:{librer_core.get_record_name(record)}\n')
                        for res_item,res_size,res_mtime in record.find_results:
                            report_file_write(f'  {sep.join(res_item)}\n')

                        report_file_write('\n')

            self.status('file saved: "%s"' % str(report_file_name))

    def find_show_results(self):
        if not self.all_records_find_results_can_show:
            self.results_on_find.show('Search results','Number of items exceeded 100 000.')
        else:
            self.find_close()
            self.find_show_results_core()

    @block
    def find_show_results_core(self):
        results_dialog = self.get_search_results_dialog()
        children=self.results_tree.get_children()

        if not children:
            #self.results_tree.delete(*children)
            self_found_item_to_data = self.found_item_to_data={}

            self_results_tree_insert=self.results_tree.insert
            sep_join = sep.join
            for record in librer_core.records:
                if record.find_results:
                    record_name=librer_core.get_record_name(record)
                    record_node = self_results_tree_insert('','end',text=record_name,values=(record_name,0,'',0,''))
                    #len(record.find_results),''

                    if self.cfg.get(CFG_KEY_expand_search_results):
                        self.results_tree.item(record_node,open=True)

                    for res_item,res_size,res_mtime in sorted(record.find_results,key = lambda x : x) :
                        item=self_results_tree_insert(record_node,'end',text=sep_join(res_item),values=(sep_join(res_item),res_size,bytes_to_str(res_size),res_mtime,strftime('%Y/%m/%d %H:%M:%S',localtime_catched(res_mtime))))
                        self_found_item_to_data[item]=(record,res_item)

            children = self.results_tree.get_children()

            if children:
                first_item = children[0]

                #self.results_tree.selection_set(first_item)
                self.results_tree.focus(first_item)

            results_dialog.info_label.configure(text=self.find_results_info)

        results_dialog.show()

    def find_mod_keypress(self,event):
        key=event.keysym

        if key=='Return':
            self.find_items()
        else:
            self.find_mod()

    def find_mod(self,field_name=None):
        try:
            self.find_params_changed=self.external_find_params_change

            sel_range = self.get_selected_records()
            sel_range_info = self.get_range_name()
            #'\n'.join([librer_core.get_record_name(rec) for rec in sel_range])

            self.widget_tooltip(self.find_range_cb1,sel_range_info)

            if self.cfg.get(CFG_KEY_type_folders) != self.type_folders_var.get():
                self.find_params_changed=True
                type_folders_switched=True
            else:
                type_folders_switched=False

            if self.cfg.get(CFG_KEY_type_files) != self.type_files_var.get():
                self.find_params_changed=True
                type_files_switched=True
            else:
                type_files_switched=False

            if not self.type_files_var.get() and not self.type_folders_var.get():
                if field_name=='folders':
                   self.type_files_var.set(True)
                elif field_name=='files':
                   self.type_folders_var.set(True)

            if self.type_files_var.get():
                self.find_size_min_entry.configure(state='normal')
                self.find_size_max_entry.configure(state='normal')
                self.find_modtime_min_entry.configure(state='normal')
                self.find_modtime_max_entry.configure(state='normal')
                self.find_size_min_label.configure(state='normal')
                self.find_size_max_label.configure(state='normal')
                self.find_modtime_min_label.configure(state='normal')
                self.find_modtime_max_label.configure(state='normal')
            else:
                self.find_size_min_entry.configure(state='disabled')
                self.find_size_max_entry.configure(state='disabled')
                self.find_modtime_min_entry.configure(state='disabled')
                self.find_modtime_max_entry.configure(state='disabled')
                self.find_size_min_label.configure(state='disabled')
                self.find_size_max_label.configure(state='disabled')
                self.find_modtime_min_label.configure(state='disabled')
                self.find_modtime_max_label.configure(state='disabled')

            if not self.find_params_changed:

                if self.cfg.get(CFG_KEY_find_cd_search_kind) != self.find_cd_search_kind_var.get():
                    self.find_params_changed=True

                elif self.cfg.get(CFG_KEY_find_filename_search_kind) != self.find_filename_search_kind_var.get():
                    self.find_params_changed=True
                elif self.cfg.get(CFG_KEY_find_range_all) != self.find_range_all.get():
                    self.find_params_changed=True

                elif self.cfg.get(CFG_KEY_find_size_min) != self.find_size_min_var.get():
                    self.find_params_changed=True
                elif self.cfg.get(CFG_KEY_find_size_max) != self.find_size_max_var.get():
                    self.find_params_changed=True

                elif self.cfg.get(CFG_KEY_find_modtime_min) != self.find_modtime_min_var.get():
                    self.find_params_changed=True
                elif self.cfg.get(CFG_KEY_find_modtime_max) != self.find_modtime_max_var.get():
                    self.find_params_changed=True

                elif self.cfg.get(CFG_KEY_find_name_regexp) != self.find_name_regexp_var.get():
                    self.find_params_changed=True
                elif self.cfg.get(CFG_KEY_find_name_glob) != self.find_name_glob_var.get():
                    self.find_params_changed=True
                elif self.cfg.get(CFG_KEY_find_name_fuzz) != self.find_name_fuzz_var.get():
                    self.find_params_changed=True

                elif self.cfg.get(CFG_KEY_find_name_case_sens) != self.find_name_case_sens_var.get():
                    self.find_params_changed=True

                elif self.cfg.get(CFG_KEY_find_cd_regexp) != self.find_cd_regexp_var.get():
                    self.find_params_changed=True
                elif self.cfg.get(CFG_KEY_find_cd_glob) != self.find_cd_glob_var.get():
                    self.find_params_changed=True
                elif self.cfg.get(CFG_KEY_find_cd_fuzz) != self.find_cd_fuzz_var.get():
                    self.find_params_changed=True

                elif self.cfg.get(CFG_KEY_find_cd_case_sens) != self.find_cd_case_sens_var.get():
                    self.find_params_changed=True

                elif self.cfg.get(CFG_KEY_filename_fuzzy_threshold) != self.find_name_fuzzy_threshold.get():
                    self.find_params_changed=True
                elif self.cfg.get(CFG_KEY_cd_fuzzy_threshold) != self.find_cd_fuzzy_threshold.get():
                    self.find_params_changed=True

            if self.find_filename_search_kind_var.get() == 'regexp':
                self.find_filename_regexp_entry.configure(state='normal')
            else:
                self.find_filename_regexp_entry.configure(state='disabled')

            if self.find_cd_search_kind_var.get() == 'regexp':
                self.find_cd_regexp_entry.configure(state='normal')
            else:
                self.find_cd_regexp_entry.configure(state='disabled')

            if self.find_filename_search_kind_var.get() == 'fuzzy':
                self.find_filename_fuzzy_threshold_lab.configure(state='normal')
                self.find_filename_fuzzy_threshold_entry.configure(state='normal')
                self.find_filename_fuzz_entry.configure(state='normal')
            else:
                self.find_filename_fuzzy_threshold_lab.configure(state='disabled')
                self.find_filename_fuzzy_threshold_entry.configure(state='disabled')
                self.find_filename_fuzz_entry.configure(state='disabled')

            if self.find_cd_search_kind_var.get() == 'fuzzy':
                self.find_cd_fuzzy_threshold_lab.configure(state='normal')
                self.find_cd_fuzzy_threshold_entry.configure(state='normal')
                self.find_cd_fuzz_entry.configure(state='normal')
            else:
                self.find_cd_fuzzy_threshold_lab.configure(state='disabled')
                self.find_cd_fuzzy_threshold_entry.configure(state='disabled')
                self.find_cd_fuzz_entry.configure(state='disabled')

            if self.find_filename_search_kind_var.get() == 'glob':
                self.find_filename_case_sens_cb.configure(state='normal')
                self.find_filename_glob_entry.configure(state='normal')
            else:
                self.find_filename_case_sens_cb.configure(state='disabled')
                self.find_filename_glob_entry.configure(state='disabled')

            if self.find_cd_search_kind_var.get() == 'glob':
                self.cd_case_sens_cb.configure(state='normal')
                self.find_cd_glob_entry.configure(state='normal')
            else:
                self.cd_case_sens_cb.configure(state='disabled')
                self.find_cd_glob_entry.configure(state='disabled')

            if self.find_params_changed:
                self.find_result_record_index=0
                self.find_result_index=0

                self.search_butt.configure(state='normal')
                self.clear_res_butt.configure(state='disabled')
                self.search_show_butt.configure(state='disabled')
                self.search_save_butt.configure(state='disabled')
            else:
                if self.searching_aborted or not self.any_valid_find_results:
                    self.search_butt.configure(state='normal')
                else:
                    self.search_butt.configure(state='disabled')

                if self.any_valid_find_results:
                    self.clear_res_butt.configure(state='normal')
                    self.search_show_butt.configure(state='normal')
                    self.search_save_butt.configure(state='normal')

            self.find_dialog.widget.update()

        except Exception as e:
            self.find_result_record_index=0
            self.find_result_index=0
            self.find_params_changed=True
            self.external_find_params_change=True
            l_error(e)

        return True #for entry validation

    def invalidate_find_results(self):
        self.any_valid_find_results=False

    def get_range_name(self):
        if self.current_group:
            return STR('group:') + str(self.current_group)

        if self.current_record:
            return STR('record:') + str(self.current_record.header.label)

        return ()

    def get_selected_records(self):
        if self.current_group:
            return librer_core.get_records_of_group(self.current_group)

        if self.current_record:
            return [self.current_record]

        return ()

    all_records_find_results_sum=0
    all_records_find_results_can_show=False
    find_results_info=''

    #@restore_status_line
    def find_items(self):
        if self.find_params_changed:
            self.find_clear()

            self.searching_aborted = False

            self.action_abort = False
            find_range_all = self.find_range_all.get()

            find_size_min = self.find_size_min_var.get()
            find_size_max = self.find_size_max_var.get()

            find_modtime_min = self.find_modtime_min_var.get()
            find_modtime_max = self.find_modtime_max_var.get()

            find_name_regexp = self.find_name_regexp_var.get()
            find_name_glob = self.find_name_glob_var.get()
            find_name_fuzz = self.find_name_fuzz_var.get()
            find_name_case_sens = self.find_name_case_sens_var.get()

            find_cd_search_kind = self.find_cd_search_kind_var.get()
            type_files_var = self.type_files_var.get()
            type_folders_var = self.type_folders_var.get()

            find_cd_regexp = self.find_cd_regexp_var.get()
            find_cd_glob = self.find_cd_glob_var.get()
            find_cd_fuzz = self.find_cd_fuzz_var.get()
            find_cd_case_sens = self.find_cd_case_sens_var.get()

            find_filename_search_kind = self.find_filename_search_kind_var.get()

            find_name = find_name_regexp if find_filename_search_kind=='regexp' else find_name_glob if find_filename_search_kind=='glob' else find_name_fuzz if find_filename_search_kind=='fuzzy' else ''
            find_cd = find_cd_regexp if find_cd_search_kind=='regexp' else find_cd_glob if find_cd_search_kind=='glob' else find_cd_fuzz if find_cd_search_kind=='fuzzy' else ''

            filename_fuzzy_threshold = self.find_name_fuzzy_threshold.get()
            cd_fuzzy_threshold = self.find_cd_fuzzy_threshold.get()

            self.search_info_lines=[]
            search_info_lines_append = self.search_info_lines.append
            if find_range_all:
                search_info_lines_append(STR('Search in all records'))
                sel_range = librer_core.records
            else:
                sel_range = self.get_selected_records()

                sel_range_info = self.get_range_name()
                search_info_lines_append(STR('Search in') + ' ' + str(sel_range_info))

            sel_range_len = len(sel_range)
            files_search_quant = sum([record.header.quant_files+record.header.quant_folders for record in sel_range])

            if files_search_quant==0:
                self.info_dialog_on_find.show(STR('Search aborted.'),STR('No files in records.'))
                return 1

            if find_filename_search_kind == 'regexp':
                if find_name_regexp:
                    if res := test_regexp(find_name_regexp):
                        self.info_dialog_on_find.show(STR('regular expression error'),res)
                        return
                    search_info_lines_append(STR('Regular expression on path element') + f':"{find_name_regexp}"')
                else:
                    self.info_dialog_on_find.show(STR('regular expression empty'),'(' + STR('for path element') + ')')
                    return
            elif find_filename_search_kind == 'glob':
                if find_name_glob:
                    info_str = STR('Glob expression on path element') + ':"' + str(find_name_glob) + '"'
                    if find_name_case_sens:
                        search_info_lines_append(info_str + ' ' + '(' + STR('Case sensitive') + ')' )
                    else:
                        search_info_lines_append(info_str)
                else:
                    self.info_dialog_on_find.show(STR('glob expression empty'),'(' + STR('for path element') + ')')
                    return
            elif find_filename_search_kind == 'fuzzy':
                if find_name_fuzz:
                    try:
                        float(filename_fuzzy_threshold)
                    except ValueError:
                        self.info_dialog_on_find.show(STR('fuzzy threshold error'),STR("wrong threshold value") + ":" + str(filename_fuzzy_threshold) )
                        return
                    search_info_lines_append(STR('Fuzzy match on path element') + f':"{find_name_fuzz}" (...>{filename_fuzzy_threshold})')
                else:
                    self.info_dialog_on_find.show(STR('fuzzy expression error'),STR('empty expression'))
                    return

            if find_cd_search_kind == 'without':
                search_info_lines_append(STR('Files without Custom Data'))
            elif find_cd_search_kind == 'any':
                search_info_lines_append(STR('Files with any correct Custom Data'))
            elif find_cd_search_kind == 'error':
                search_info_lines_append(STR('Files with error on CD extraction'))
            elif find_cd_search_kind == 'empty':
                search_info_lines_append(STR('Files with empty CD value'))
            elif find_cd_search_kind == 'aborted':
                search_info_lines_append(STR('Files with aborted CD extraction'))
            elif find_cd_search_kind == 'regexp':
                if find_cd_regexp:
                    if res := test_regexp(find_cd_regexp):
                        self.info_dialog_on_find.show(STR('regular expression error'),res)
                        return
                    search_info_lines_append(STR('Regular expression on Custom Data') + f' :"{find_cd_regexp}"')
                else:
                    self.info_dialog_on_find.show(STR('regular expression empty'),STR('(for Custom Data)'))
                    return
            elif find_cd_search_kind == 'glob':
                if find_cd_glob:
                    info_str = STR('Glob expression on Custom Data') + f' :"{find_cd_glob}"'
                    if find_cd_case_sens:
                        search_info_lines_append(info_str + ' ' + '(' + STR('Case sensitive') + ')')
                    else:
                        search_info_lines_append(info_str)
                else:
                    self.info_dialog_on_find.show(STR('glob expression empty'),STR('(for Custom Data)'))
                    return
            elif find_cd_search_kind == 'fuzzy':
                if find_cd_fuzz:
                    try:
                        float(cd_fuzzy_threshold)
                    except ValueError:
                        self.info_dialog_on_find.show(STR('fuzzy threshold error'),f"wrong threshold value:{cd_fuzzy_threshold}")
                        return
                    search_info_lines_append(STR('Fuzzy match on Custom Data') + f':"{find_cd_fuzz}" (...>{cd_fuzzy_threshold})')

                else:
                    self.info_dialog_on_find.show(STR('fuzzy expression error'),STR('empty expression'))
                    return

            if find_size_min:
                min_num = str_to_bytes(find_size_min)
                if min_num == -1:
                    self.info_dialog_on_find.show(STR('min size value error'),f'fix "{find_size_min}"')
                    return
                search_info_lines_append(STR('Min size') + f':{find_size_min}')
            else:
                min_num = ''

            if find_size_max:
                max_num = str_to_bytes(find_size_max)
                if max_num == -1:
                    self.info_dialog_on_find.show(STR('max size value error'),f'fix "{find_size_max}"')
                    return
                search_info_lines_append(STR('Max size') + f':{find_size_max}')
            else:
                max_num = ''

            if find_size_min and find_size_max:
                if max_num<min_num:
                    self.info_dialog_on_find.show('error','max size < min size')
                    return

            t_min=None
            if find_modtime_min:
                try:
                    t_min = int(mktime(parse_datetime(find_modtime_min).timetuple()))
                except Exception as te:
                    self.info_dialog_on_find.show('file modification time min error ',f'{find_modtime_min}\n{te}')
                    return
                search_info_lines_append(STR('Min modtime') + f':{find_modtime_min}')
            t_max=None
            if find_modtime_max:
                try:
                    t_max = int(mktime(parse_datetime(find_modtime_max).timetuple()))
                except Exception as te:
                    self.info_dialog_on_find.show('file modification time max error ',f'{find_modtime_max}\n{te}')
                    return
                search_info_lines_append(STR('Max modtime') + f':{find_modtime_max}')

            self.cfg.set(CFG_KEY_find_range_all,find_range_all)
            self.cfg.set(CFG_KEY_find_cd_search_kind,find_cd_search_kind)

            self.cfg.set(CFG_KEY_type_folders,type_folders_var)
            self.cfg.set(CFG_KEY_type_files,type_files_var)

            self.cfg.set(CFG_KEY_find_filename_search_kind,find_filename_search_kind)

            self.cfg.set(CFG_KEY_find_size_min,find_size_min)
            self.cfg.set(CFG_KEY_find_size_max,find_size_max)

            self.cfg.set(CFG_KEY_find_modtime_min,find_modtime_min)
            self.cfg.set(CFG_KEY_find_modtime_max,find_modtime_max)

            self.cfg.set(CFG_KEY_find_name_regexp,find_name_regexp)
            self.cfg.set(CFG_KEY_find_name_glob,find_name_glob)
            self.cfg.set(CFG_KEY_find_name_fuzz,find_name_fuzz)
            self.cfg.set(CFG_KEY_find_name_case_sens,find_name_case_sens)

            self.cfg.set(CFG_KEY_find_cd_regexp,find_cd_regexp)
            self.cfg.set(CFG_KEY_find_cd_glob,find_cd_glob)
            self.cfg.set(CFG_KEY_find_cd_fuzz,find_cd_fuzz)
            self.cfg.set(CFG_KEY_find_cd_case_sens,find_cd_case_sens)

            self.cfg.set(CFG_KEY_filename_fuzzy_threshold,filename_fuzzy_threshold)
            self.cfg.set(CFG_KEY_cd_fuzzy_threshold,cd_fuzzy_threshold)

            self_progress_dialog_on_find = self.get_progress_dialog_on_find()

            search_thread=Thread(target=lambda : librer_core.find_items_in_records(self.temp_dir,sel_range,
                min_num,max_num,
                t_min,t_max,
                find_filename_search_kind,find_name,find_name_case_sens,
                find_cd_search_kind,find_cd,find_cd_case_sens,
                filename_fuzzy_threshold,cd_fuzzy_threshold,type_folders_var,type_files_var),daemon=True)
            search_thread.start()

            search_thread_is_alive = search_thread.is_alive

            wait_var=BooleanVar()
            wait_var.set(False)

            #############################

            self_progress_dialog_on_find.lab_l1.configure(text='Records:')
            self_progress_dialog_on_find.lab_l2.configure(text='Files:' )
            self_progress_dialog_on_find.lab_r1.configure(text='--')
            self_progress_dialog_on_find.lab_r2.configure(text='--' )
            self_progress_dialog_on_find.show(STR('Search progress'))

            records_len = len(librer_core.records)
            if records_len==0:
                self.info_dialog_on_find.show(STR('Search aborted.'),STR('No records.'))
                return

            self_progress_dialog_on_find_progr1var_set = self.progress_dialog_on_find.progr1var.set
            self_progress_dialog_on_find_progr2var_set = self.progress_dialog_on_find.progr2var.set

            self_progress_dialog_on_find_update_lab_text = self.progress_dialog_on_find.update_lab_text

            self_progress_dialog_on_find_lab_r1_config = self.progress_dialog_on_find.lab_r1.config
            self_progress_dialog_on_find_lab_r2_config = self.progress_dialog_on_find.lab_r2.config

            update_once=True
            self_ico_empty = self.ico_empty
            prev_curr_files = curr_files = 0

            wait_var_set = wait_var.set
            wait_var_get = wait_var.get
            self_main_after = self.main.after
            self_main_wait_variable = self.main.wait_variable
            self_progress_dialog_on_find_update_lab_image = self_progress_dialog_on_find.update_lab_image
            self_get_hg_ico = self.get_hg_ico

            #librer_core_files_search_quant = librer_core.files_search_quant
            fnumber_files_search_quant = fnumber(files_search_quant)
            fnumber_sel_range_len = fnumber(sel_range_len)

            time_without_busy_sign=0
            while search_thread_is_alive():
                now=time()
                ######################################################################################

                change0 = self_progress_dialog_on_find_update_lab_text(0,librer_core.info_line)
                change3 = self_progress_dialog_on_find_update_lab_text(3,STR('Found Files') + f': {fnumber(librer_core.find_res_quant)}' )

                curr_files = librer_core.total_search_progress

                self_progress_dialog_on_find_progr1var_set(librer_core.records_perc_info)
                self_progress_dialog_on_find_progr2var_set(curr_files * 100.0 / files_search_quant)

                self_progress_dialog_on_find_lab_r1_config(text=f'{fnumber(librer_core.search_record_nr)} / {fnumber_sel_range_len}')
                self_progress_dialog_on_find_lab_r2_config(text=f'{fnumber(curr_files)} / {fnumber_files_search_quant}')

                if self.action_abort:
                    librer_core.abort()

                if change0 or change3 or prev_curr_files != curr_files:
                    prev_curr_files = curr_files

                    time_without_busy_sign=now

                    if update_once:
                        update_once=False
                        self_progress_dialog_on_find_update_lab_image(2,self_ico_empty)
                else :
                    if now>time_without_busy_sign+1.0:
                        self_progress_dialog_on_find_update_lab_image(2,self_get_hg_ico())
                        update_once=True

                self_main_after(25,lambda : wait_var_set(not wait_var_get()))
                self_main_wait_variable(wait_var)
                ######################################################################################

            search_thread.join
            self_progress_dialog_on_find.hide(True)

            #gc_collect()
            #gc_enable()

            colname,sort_index,is_numeric,reverse,group_code,dir_code,non_dir_code = self.column_sort_last_params
            #print('\npre sort info colname:',colname,'is_numeric',is_numeric,'reverse:',reverse)
            colname_real = self.REAL_SORT_COLUMN[colname]
            #print('colname_real:',colname_real)

            if self.action_abort:
                self.all_records_find_results_sum=0
                self.any_valid_find_results=0
                self.all_records_find_results_can_show=False
                self.find_results_info='Aborted'

                self.results_on_find.show(STR('Aborted'),STR('Searching aborted.'))
                self.searching_aborted = True
            else:
                self.all_records_find_results_sum = sum([len(record.find_results) for record in librer_core.records])
                self.any_valid_find_results=bool(self.all_records_find_results_sum>0)
                self.all_records_find_results_can_show = bool(self.all_records_find_results_sum<100000)
                find_results_quant_sum_format = fnumber(self.all_records_find_results_sum)

                for record in librer_core.records:
                    record.find_items_sort(colname_real,reverse)

                self.searching_aborted = False
                #abort_info = '\n' + STR('Searching aborted. Results may be incomplete.') if self.action_abort else ''
                #abort_info = '\n' + STR('Searching aborted.') if self.action_abort else ''

                self.set_found()

                self.find_mod()

                search_info = '\n'.join(self.search_info_lines)

                select_found=self.cfg.get(CFG_KEY_select_found)
                if select_found:
                    if self.any_valid_find_results:
                        self.select_find_result(1)

                #self.find_results_info = f"{search_info}\n" + STR("found") + ": " + str(find_results_quant_sum_format) + ' ' + STR('items') + '.\n' + abort_info
                self.find_results_info = str(find_results_quant_sum_format) + ' ' + STR('items') + ' ' + STR('found')
                # + abort_info
                #STR("Navigate search results by\n\'Find next (F3)\' & 'Find prev (Shift+F3)'\nactions.")

                #self.results_on_find.show(STR('Search results'),f"{search_info}\n\n" + STR("found") + ": " + str(find_results_quant_sum_format) + ' ' + STR('items') + '.\n\n' + STR("Navigate search results by\n\'Find next (F3)\' & 'Find prev (Shift+F3)'\nactions.") + abort_info)
                self.status_find_tooltip(f"available search results: {find_results_quant_sum_format}")

                if not self.searching_aborted and self.all_records_find_results_sum==0:
                    self.results_on_find.show('Search results','No results matching search criteria.')

                if not self.searching_aborted and self.any_valid_find_results:
                    self.search_show_butt.configure(state='normal')
                    self.search_save_butt.configure(state='normal')

                    self.search_butt.configure(state='disabled')

                    self.external_find_params_change=False

                    if self.cfg.get(CFG_KEY_after_action)==1:
                        self.find_show_results()
                    else:
                        self.find_close()
        else:
            self.info_dialog_on_find.show(STR('Search aborted.'),'Same params')

    def get_child_of_name(self,record,item,child_name):
        self_tree = self.tree

        self_item_to_data = self.item_to_data
        record_filenames = record.filenames

        #mozna by to zcachowac ale jest kwestia sortowania
        for child in self_tree.get_children(item):
            if record_filenames[self_item_to_data[child][0]]==child_name:
                return child
        return None

    @block
    def select_find_result(self,mod,record_par=None,subpath_list_par=None):
        status_to_set=None
        self_tree = self.tree
        if self.any_valid_find_results:
            settled = False

            librer_core_records_sorted =librer_core.records_sorted
            records_quant = len(librer_core_records_sorted)
            find_result_index_reset=False

            while not settled:
                record = librer_core_records_sorted[self.find_result_record_index]
                record_find_results = record.find_results

                record_find_results_len=len(record_find_results)

                if find_result_index_reset:
                    find_result_index_reset=False
                    if mod>0:
                        self.find_result_index = 0
                    else:
                        self.find_result_index = record_find_results_len-1
                else:
                    self.find_result_index += mod

                if self.find_result_index>=record_find_results_len:
                    find_result_index_reset=True
                    self.find_result_record_index += mod
                    self.find_result_record_index %= records_quant
                elif self.find_result_index<0:
                    find_result_index_reset=True
                    self.find_result_record_index += mod
                    self.find_result_record_index %= records_quant

                try:
                    items_names_tuple,res_size,res_mtime=record_find_results[self.find_result_index]
                except Exception as e:
                    continue
                else:
                    settled=True
                    status_to_set=f'record find result: {fnumber(self.find_result_index+1 if self.find_result_index>=0 else record_find_results_len+self.find_result_index+1)} / {fnumber(record_find_results_len)} / {fnumber(self.all_records_find_results_sum)}'

            record_item = self.record_to_item[record]

            current_item = record_item

            self_open_item = self.open_item

            self_open_item(current_item)

            self_get_child_of_name = self.get_child_of_name
            self_tree_update = self_tree.update

            for item_name in items_names_tuple:
                child_item = self_get_child_of_name(record,current_item,item_name)

                if child_item:
                    current_item = child_item

                    self_open_item(current_item)

                    self_tree_update()
                else:
                    self.info_dialog_on_main.show('cannot find item:',item_name)
                    break

            #if self.find_dialog_shown:
            #    self.tree.selection_set(current_item)
            #else:
            #    self.tree.focus(current_item)

            self.sel_item = current_item

            self.select_and_focus(current_item)

            #self.tree.update()

        if status_to_set:
            self.status(status_to_set)

    KEY_DIRECTION={}
    KEY_DIRECTION['Prior']=-1
    KEY_DIRECTION['Next']=1
    KEY_DIRECTION['Up']=-1
    KEY_DIRECTION['Down']=1
    KEY_DIRECTION['Home']=0
    KEY_DIRECTION['End']=-1

    @block
    def goto_next_prev_record(self,direction):
        tree=self.tree
        item=self.sel_item

        item=tree.focus()
        if item:
            record_item,record_name,subpath_list = self.get_item_record(item)
            item_to_sel = tree.next(record_item) if direction==1 else tree.prev(record_item)
            if item_to_sel:
                self.select_and_focus(item_to_sel)

    @block
    def goto_first_last_record(self,index):
        if children := self.tree_get_children():
            if next_item:=children[index]:
                self.select_and_focus(next_item)

    current_record = None
    current_group = None
    current_subpath_list = None

    visible_items=()
    visible_items_max_index=0
    visible_items_uptodate=False

    def visible_items_update(self):
        if not self.visible_items_uptodate:
            self.visible_items=tuple(self.get_visible_items())
            self.visible_items_max_index = len(self.visible_items)-1
            self.visible_items_uptodate=True

    def get_visible_items(self,item=""):
        self_tree_get_children = self.tree.get_children
        if self.tree.item(item,"open") or item=="":
            return [item] + [grandchild for child in self_tree_get_children(item) for grandchild in self.get_visible_items(child)]
        else:
            return [item]

    def get_next_index(self,index,offset,max_val):
        res=index+offset
        return max_val if res>max_val else res

    def get_prev_index(self,index,offset):
        res=index-offset
        return 0 if res<0 else res

    def wrapped_see(self, item):
        self_tree = self.tree
        try:
            item_index=self.visible_items.index(item)
        except:
            return

        try:
            if self.see_direction<1:
                pi=self.get_prev_index(item_index,self.rows_offset)

                prev_item=self.visible_items[pi]

                if prev_item:
                    self_tree.see(prev_item)
                    self_tree.update()
                else:
                    self_tree.see(item)

            if self.see_direction>-1:
                ni=self.get_next_index(item_index,self.rows_offset,self.visible_items_max_index)
                next_item=self.visible_items[ni]

                if next_item:
                    self_tree.see(next_item)
                    self_tree.update()
                else:
                    self_tree.see(item)
        except:
            self_tree.see(item)

    def tree_item_focused(self,item,can_move=True):
        self_tree = self.tree

        if can_move:
            self.wrapped_see(item)
            self_tree.update()

        if item:
            if self_tree.tag_has(self.GROUP,item):
                values = self_tree.item(item,'values')
                if values:
                    self.current_group=values[0]
                else:
                    self.current_group=None

                self.status_record.configure(image = self.ico_empty, text = '---',compound='left')
                self.current_record = None
                self.current_subpath_list = None
            else:
                self.current_group = None

                record_item,record_name,subpath_list = self.get_item_record(item)
                if record_item in self.item_to_record:
                    record = self.item_to_record[record_item]

                    self.current_subpath_list = subpath_list
                    if record != self.current_record:
                        self.current_record = record
                        if not self.cfg.get(CFG_KEY_find_range_all):
                            self.external_find_params_change = True

                    image=self_tree.item(record_item,'image')

                    self.status_record.configure(image = image, text = record_name,compound='left')
                    self.widget_tooltip(self.status_record,librer_core.record_info_alias_wrapper(record,record.txtinfo_basic + '\n\n(' + STR('Click to show full record info') + ')') )
                else:
                    self.status_record.configure(image = '', text = '')
                    self.widget_tooltip(self.status_record,'')
                    self.current_record = None
                    self.current_subpath_list = None
                    self.status_record.configure(image = self.ico_empty, text = '---',compound='left')
        else:
            self.status_record.configure(image = self.ico_empty, text = '---',compound='left')
            self.current_record = None
            self.current_group = None
            self.current_subpath_list = None

    rows_offset=0
    def tree_configure(self):
        try:
            self.rows_offset = int( (self.tree.winfo_height() / self.rowhight) / 3)
        except :
            self.rows_offset = 0

    def tree_on_select(self,can_move=True):
        item = self.tree.focus()

        if item:
            self.sel_item = item
            record_item,record_name,subpath_list = self.get_item_record(item)
            self.status(sep.join(subpath_list))

            self.tree_item_focused(item,can_move)

    see_direction=0

    def key_press(self,event):
        #print('event:',event)
        if not self.block_processing_stack:
            self.hide_tooltip()
            self.menubar_unpost()
            self.popup_unpost()

            try:
                tree=event.widget
                item=tree.focus()
                key=event.keysym

                if key in ("Prior","Next"):
                    self.see_direction = self.KEY_DIRECTION[key]
                    self.visible_items_update()
                    self.goto_next_prev_record(self.KEY_DIRECTION[key])
                    return "break"
                elif key in ("Home","End"):
                    self.goto_first_last_record(self.KEY_DIRECTION[key])
                    return "break"
                elif key in ("Up","Down"):
                    self.see_direction = self.KEY_DIRECTION[key]
                    self.visible_items_update()
                elif key == "Return":
                    event_str=str(event)
                    alt_pressed = ('0x20000' in event_str) if windows else ('Mod1' in event_str or 'Mod5' in event_str)
                    if alt_pressed:
                        self.record_info()
                        return "break"
                    elif self.show_customdata():
                        return
                    else:
                        item = tree.focus()
                        self.open_item(item)
                        tree.update()
                elif key == "Alt_L":
                    return "break"
                else:
                    #print(key)

                    #alt_pressed = ('0x20000' in event_str) if windows else ('Mod1' in event_str or 'Mod5' in event_str)
                    #ctrl_pressed = 'Control' in event_str
                    #shift_pressed = 'Shift' in event_str
                    pass

            except Exception as e:
                l_error(e)
                self.info_dialog_on_main.show('INTERNAL ERROR',str(e))

            self.tree_on_select()

#################################################
    def select_and_focus(self,item):
        #print('select_and_focus',item)
        self_tree = self.tree

        self.tree_focus(item)
        self.tree_item_focused(item)

        self_tree.see(item)
        self_tree.update()

        self.see_direction=0
        self.visible_items_update()

        self.wrapped_see(item)

        self_tree.update()

    def tree_on_mouse_button_press_search_results(self,event):
        tree=event.widget
        region = tree.identify("region", event.x, event.y)

        if region != 'separator':
            if region == 'heading':
                col_nr = tree.identify_column(event.x)
                colname = col_nr if col_nr=='#0' else tree.column(col_nr,'id')

                #print('colname:',colname)
                ##0,size_h,ctime_h

                #if colname in self.REAL_SORT_COLUMN:
                self.column_sort_click_results(tree,colname)

                #    self.column_sort_click(tree,colname)
            elif item:=tree.identify('item',event.x,event.y):
                pass

    def tree_on_mouse_button_press(self,event):
        if not self.block_processing_stack:
            self.menubar_unpost()
            self.hide_tooltip()
            self.popup_unpost()

            tree=self.tree
            region = tree.identify("region", event.x, event.y)

            if region != 'separator':
                if region == 'heading':
                    col_nr = tree.identify_column(event.x)
                    colname = col_nr if col_nr=='#0' else tree.column(col_nr,'id')

                    if colname in self.REAL_SORT_COLUMN:
                        self.column_sort_click(tree,colname)
                    else :
                        print('unknown col:',col_nr,colname)
                elif item:=tree.identify('item',event.x,event.y):
                    #tree.selection_remove(tree.selection())

                    tree.focus(item)
                    self.tree_on_select(False)
                    self.set_find_result_record_index()

                    self.set_find_result_indexes(self.current_subpath_list)
        else:
            return "break"

    sel_item = None

    def menubar_unpost(self):
        try:
            self.menubar.unpost()
        except Exception as e:
            l_error(e)

    def context_menu_show(self,event):
        if not self.block_processing_stack:
            tree=self.tree

            if tree.identify("region", event.x, event.y) == 'heading':
                return

            tree.focus_set()
            self.tree_on_mouse_button_press(event)
            tree.update()

            item=self.tree.focus()

            is_group = bool(self.tree.tag_has(self.GROUP,item))

            if self.current_record:
                record_item = self.record_to_item[self.current_record]
                is_record_loaded = bool(self.tree.tag_has(self.RECORD,record_item))
            else:
                is_record_loaded = False

            is_record = bool(self.tree.tag_has(self.RECORD_RAW,item) or self.tree.tag_has(self.RECORD,item))

            record_in_group = is_record and bool(librer_core.get_record_group(self.current_record))

            there_are_groups = bool(librer_core.groups)

            pop=self.popup

            pop.delete(0,'end')

            pop_add_separator = pop.add_separator
            pop_add_command = pop.add_command

            state_on_records = 'normal' if is_record else 'disabled'

            state_on_records_or_groups = 'normal' if is_record or is_group else 'disabled'

            c_nav = Menu(self.menubar,tearoff=0,bg=self.bg_color)
            c_nav_add_command = c_nav.add_command
            c_nav_add_separator = c_nav.add_separator

            c_nav_add_command(label = STR('Go to next record')       ,command = lambda : self.goto_next_prev_record(1),accelerator="Pg Down",state='normal', image = self.ico_empty,compound='left')
            c_nav_add_command(label = STR('Go to previous record')   ,command = lambda : self.goto_next_prev_record(-1), accelerator="Pg Up",state='normal', image = self.ico_empty,compound='left')
            c_nav_add_separator()
            c_nav_add_command(label = STR('Go to first record')       ,command = lambda : self.goto_first_last_record(0),accelerator="Home",state='normal', image = self.ico_empty,compound='left')
            c_nav_add_command(label = STR('Go to last record')   ,command = lambda : self.goto_first_last_record(-1), accelerator="End",state='normal', image = self.ico_empty,compound='left')

            pop_add_command(label = STR('New record ...'),  command = self.scan_dialog_show,accelerator='Ctrl+N',image = self.ico_record_new,compound='left')
            pop_add_separator()
            pop_add_command(label = STR('Export record ...'), accelerator='Ctrl+E', command = self.record_export,image = self.ico_record_export,compound='left',state=state_on_records)
            pop_add_command(label = STR('Import record ...'), accelerator='Ctrl+I', command = self.record_import,image = self.ico_record_import,compound='left')
            pop_add_command(label = STR('Rename / Repack ...'),accelerator="F5" , command = self.record_repack,image = self.ico_empty,compound='left',state=state_on_records)
            pop_add_command(label = STR('Record Info ...'), accelerator='Alt+Enter', command = self.record_info,image = self.ico_info,compound='left',state=state_on_records)
            pop_add_command(label = STR('Delete record ...'),accelerator="Delete, F8",command = self.delete_action,image = self.ico_record_delete,compound='left',state=state_on_records)
            pop_add_separator()
            pop_add_command(label = STR('New group ...'),accelerator="F7",  command = self.new_group,image = self.ico_group_new,compound='left')
            pop_add_command(label = STR('Remove group ...'),accelerator="Delete" ,  command = self.remove_group,image = self.ico_group_remove,compound='left',state=('disabled','normal')[is_group] )
            pop_add_command(label = STR('Assign record to group ...'),accelerator="F6" ,  command = self.assign_to_group,image = self.ico_group_assign,compound='left',state=('disabled','normal')[is_record and there_are_groups] )
            pop_add_command(label = STR('Remove record from group ...'),  command = self.remove_from_group,image = self.ico_empty,compound='left',state=('disabled','normal')[record_in_group])
            pop_add_separator()
            pop_add_command(label = STR('Rename / Alias name ...'), accelerator='F2', command = self.alias_name,image = self.ico_empty,compound='left',state=state_on_records_or_groups )
            pop_add_separator()
            pop_add_command(label = STR('Show Custom Data ...'), accelerator='Enter', command = self.show_customdata,image = self.ico_empty,compound='left',state=('disabled','normal')[self.item_has_cd(self.tree.focus())])
            pop_add_separator()
            pop_add_command(label = STR('Copy full path'),command = self.clip_copy_full_path_with_file,accelerator='Ctrl+C',state = 'normal' if self.sel_item is not None and self.current_record else 'disabled', image = self.ico_empty,compound='left')
            pop_add_separator()

            any_records = bool(librer_core.records)
            any_records_state = 'normal' if any_records else 'disabled'

            pop_add_command(label = STR('Find ...'),accelerator="Ctrl+F" ,command = self.finder_wrapper_show,state = any_records_state, image = self.ico_find,compound='left')
            pop_add_command(label = STR('Find next'),command = self.find_next,accelerator="F3",state = any_records_state, image = self.ico_empty,compound='left')
            pop_add_command(label = STR('Find prev'),command = self.find_prev,accelerator="Shift+F3",state = any_records_state, image = self.ico_empty,compound='left')
            pop_add_separator()
            pop_add_command(label = STR('Clear Search Results'),command = self.find_clear, image = self.ico_empty,compound='left',state = 'normal' if self.any_valid_find_results else 'disabled')
            pop_add_separator()
            pop_add_command(label = STR('Unload record data'),command = self.unload_record, accelerator="Backspace", image = self.ico_empty,compound='left',state = 'normal' if is_record_loaded else 'disabled')
            pop_add_command(label = STR('Unload all records data'),command = self.unload_all_recods, accelerator="Ctrl+Backspace", image = self.ico_empty,compound='left',state = any_records_state)
            pop_add_separator()

            pop_add_command(label = STR('Exit'),  command = self.exit ,image = self.ico['exit'],compound='left')

            try:
                pop.tk_popup(event.x_root, event.y_root)
            except Exception as e:
                print(e)

            pop.grab_release()

    def new_group(self):
        self.get_entry_ask_dialog().show(STR('New group'),STR('New group name:'))

        if self.entry_ask_dialog.res_bool:
            res = self.entry_ask_dialog.entry_val.get()
            if res:
                res2=librer_core.create_new_group(res,self.single_group_show)
                if res2:
                    self.info_dialog_on_main.show('Error',res2)
                    self.new_group()

    def remove_group(self):
        tree = self.tree
        item=tree.focus()
        if tree.tag_has(self.GROUP,item):
            values = tree.item(item,'values')
            if values:
                group=values[0]

            dialog = self.get_simple_question_dialog()
            dialog.show(STR('Delete selected group ?'), STR('group: ') + group + '\n\n' + STR('(Records assigned to group will remain untouched)'))

            if dialog.res_bool:
                for record_filename in librer_core.groups[group]:
                    if record_filename in self.record_filename_to_record:
                        record = self.record_filename_to_record[record_filename]
                        record_item = self.record_to_item[record]
                        self.tree.move(record_item,'',0)
                    else:
                        print(f'zombie record filename: {record_filename}')

                librer_core.remove_group(group)

                tree.delete(self.group_to_item[group])

                if children := tree.get_children():
                    item = children[0]
                    self.tree.focus(item)
                    self.tree_item_focused(item)
                else:
                    self.tree_on_select()

                self.find_clear()

    def remove_from_group(self):
        record = self.current_record

        group = librer_core.get_record_group(record)

        res = librer_core.remove_record_from_group(record)
        if res :
            self.info_dialog_on_main.show('Error',res)
        else:
            record_item = self.record_to_item[record]
            self.tree.move(record_item,'',0)

            if group:
                size=record.header.sum_size
                self.group_to_size_sum[group]-=size
                self.single_group_update_size(group)

            self.find_clear()

            self.column_sort(self.tree)

    last_assign_to_group_group = None
    @logwrapper
    def assign_to_group(self):
        if self.current_record:
            record = self.current_record
            current = prev_group = librer_core.get_record_group(record)
            #print(f'{current=}')

            dial = self.get_assign_to_group_dialog()
            values = list(librer_core.groups.keys())
            dial.combobox.configure(values=values)

            size=record.header.sum_size

            if not current:
                if self.last_assign_to_group_group in values:
                    current = self.last_assign_to_group_group
                else:
                    current = values[0]

            dial.show(STR('Assign to group'),STR('Assign record to group:'),current)

            if dial.res_bool:
                group = dial.entry_val.get()

                if group:

                    self.last_assign_to_group_group = group
                    res2=librer_core.assign_new_group(record,group)
                    if res2:
                        self.info_dialog_on_main.show('assign_new_group Error',res2)
                    else:
                        if prev_group:
                            self.group_to_size_sum[current] -= size
                            self.single_group_update_size(current)

                        group_item = self.group_to_item[group]
                        record_item = self.record_to_item[record]
                        self.tree.move(record_item,group_item,0)

                        self.group_to_size_sum[group] += size
                        self.single_group_update_size(group)

                        self.open_item(group_item)
                        self.tree.focus(record_item)
                        #self.tree.see(record_item)
                        self.wrapped_see(record_item)
                        #self.tree.update()

                        self.find_clear()

                        self.column_sort(self.tree)

    @logwrapper
    def column_sort_click(self, tree, colname):
        prev_colname,prev_sort_index,prev_is_numeric,prev_reverse,prev_group_code,prev_dir_code,prev_non_dir_code = self.column_sort_last_params
        reverse = not prev_reverse if colname == prev_colname else prev_reverse
        tree.heading(prev_colname, text=self.org_label[prev_colname])

        group_code,dir_code,non_dir_code = (2,1,0) if reverse else (0,1,2)

        sort_index=self.REAL_SORT_COLUMN_INDEX[colname]
        is_numeric=self.REAL_SORT_COLUMN_IS_NUMERIC[colname]
        self.column_sort_last_params=(colname,sort_index,is_numeric,reverse,group_code,dir_code,non_dir_code)
        self.cfg.set(CFG_SORTING,self.column_sort_last_params)

        #print('\npre sort info colname:',colname,'is_numeric',is_numeric,'reverse:',reverse)
        colname_real = self.REAL_SORT_COLUMN[colname]
        #print('colname_real:',colname_real)

        for record in librer_core.records:
            record.find_items_sort(colname_real,reverse)
            #print(record.find_result)

        self.column_sort(tree)

    def tree_sort_item(self,parent_item):
        tree = self.tree

        colname,sort_index,is_numeric,reverse,group_code,dir_code,non_dir_code = self.column_sort_last_params

        real_column_to_sort=self.REAL_SORT_COLUMN[colname]

        tlist=[]
        tree_set = tree.set
        tlist_append = tlist.append

        dir_or_dirlink = (self.DIR,self.DIRLINK)

        children = tree.get_children(parent_item)

        #dont sort single item and dummy item
        #if len(children)>1:

        self_GROUP = self.GROUP
        tree_item=tree.item

        self_REAL_SORT_COLUMN_INDEX_colname = self.REAL_SORT_COLUMN_INDEX[colname]

        for item in children:
            values = tree_item(item,'values')

            if not values: #dummy node
                continue

            sortval_org = values[self_REAL_SORT_COLUMN_INDEX_colname]

            sortval=(int(sortval_org) if sortval_org.isdigit() else 0) if is_numeric else sortval_org

            kind = tree_set(item,'kind')

            code = group_code if kind is self_GROUP else dir_code if kind in dir_or_dirlink else non_dir_code
            tlist_append( ( (code,sortval),item) )

        tlist.sort(reverse=reverse,key=lambda x: x[0])

        if not parent_item:
            parent_item=''

        tree_move = tree.move
        _ = {tree_move(item_temp, parent_item, index) for index,(val_tuple,item_temp) in enumerate(sorted(tlist,reverse=reverse,key=lambda x: x[0]) ) }
        _ = {self.tree_sort_item(item_temp) for (val_tuple,item_temp) in tlist }

    @restore_status_line
    @block_and_log
    def column_sort(self, tree):
        self.status('Sorting...')
        colname,sort_index,is_numeric,reverse,group_code,dir_code,non_dir_code = self.column_sort_last_params

        self.column_sort_set_arrow(tree)
        self.tree_sort_item(None)

        tree.update()
        self.visible_items_uptodate=False

    def column_sort_set_arrow(self, tree):
        colname,sort_index,is_numeric,reverse,group_code,dir_code,non_dir_code = self.column_sort_last_params
        tree.heading(colname, text=self.org_label[colname] + ' ' + str('\u25BC' if reverse else '\u25B2') )

    #@logwrapper
    def column_sort_click_results(self, tree, colname):
        prev_colname,prev_sort_index,prev_is_numeric,prev_reverse,prev_group_code,prev_dir_code,prev_non_dir_code = self.column_sort_last_params_results
        reverse = not prev_reverse if colname == prev_colname else prev_reverse
        tree.heading(prev_colname, text=self.org_label[prev_colname])

        group_code,dir_code,non_dir_code = (2,1,0) if reverse else (0,1,2)

        sort_index=self.REAL_SORT_COLUMN_INDEX[colname]
        is_numeric=self.REAL_SORT_COLUMN_IS_NUMERIC[colname]
        self.column_sort_last_params_results=(colname,sort_index,is_numeric,reverse,group_code,dir_code,non_dir_code)
        self.cfg.set(CFG_SORTING_RESULTS,self.column_sort_last_params_results)

        colname_real = self.REAL_SORT_COLUMN[colname]

        self.column_sort_results(tree)

    def tree_sort_item_results(self,parent_item):
        tree = self.results_tree

        colname,sort_index,is_numeric,reverse,group_code,dir_code,non_dir_code = self.column_sort_last_params_results

        real_column_to_sort=self.REAL_SORT_COLUMN[colname]

        tlist=[]
        tree_set = tree.set
        tlist_append = tlist.append

        dir_or_dirlink = (self.DIR,self.DIRLINK)

        children = tree.get_children(parent_item)

        self_REAL_SORT_COLUMN_INDEX_RESULTS_colname=self.REAL_SORT_COLUMN_INDEX_RESULTS[colname]

        tree_item=tree.item

        for item in children:
            values = tree_item(item,'values')

            sortval_org = values[self_REAL_SORT_COLUMN_INDEX_RESULTS_colname]

            sortval=(int(sortval_org) if sortval_org.isdigit() else 0) if is_numeric else sortval_org

            tlist_append( ( sortval,item) )

        tlist.sort(reverse=reverse,key=lambda x: x[0])

        #if not parent_item:
        #    parent_item=''

        tree_move = tree.move
        _ = {tree_move(item_temp, parent_item, index) for index,(val_tuple,item_temp) in enumerate(sorted(tlist,reverse=reverse,key=lambda x: x[0]) ) }

    #@restore_status_line
    #@block_and_log
    def column_sort_results(self, tree):
        #self.status('Sorting...')
        colname,sort_index,is_numeric,reverse,group_code,dir_code,non_dir_code = self.column_sort_last_params_results

        self.column_sort_set_arrow_results(tree)

        children = self.results_tree.get_children('')

        for item in children:
            self.tree_sort_item_results(item)

        tree.update()
        #self.visible_items_uptodate=False

    def column_sort_set_arrow_results(self, tree):
        colname,sort_index,is_numeric,reverse,group_code,dir_code,non_dir_code = self.column_sort_last_params_results
        tree.heading(colname, text=self.org_label[colname] + ' ' + str('\u25BC' if reverse else '\u25B2') )

    def path_to_scan_set(self,path):
        print('path_to_scan_set',path)

    scanning_in_progress=False
    def scan_wrapper(self):
        gc_disable()
        gc_collect()

        group = self.scan_dialog_group

        path_to_scan_from_entry = str(abspath(self.path_to_scan_entry_var.get()))

        old_records_same_path=[record_temp for record_temp in librer_core.records if path_to_scan_from_entry == record_temp.header.scan_path]

        if self.scanning_in_progress:
            l_warning('scan_wrapper collision')
            return

        if self.scan_label_entry_var.get()=='':
            self.scan_label_entry_var.set(platform_node() + ':' + path_to_scan_from_entry )
            #self.get_info_dialog_on_scan().show('Error. Empty label.','Set internal label.')
            #return

        self.scanning_in_progress=True

        compression_level = self.scan_compr_var_int.get()
        threads = self.scan_threads_var_int.get()

        try:
            if self.scan(compression_level,threads,group):
                self.scan_dialog_hide_wrapper()
                {self.remove_record(record_temp) for record_temp in old_records_same_path}

        except Exception as e:
            l_error(f'scan_wraper: {e}')
            self.status(f'scan_wraper {e}')
            self.scan_dialog_hide_wrapper()

        self.scanning_in_progress=False
        gc_collect()
        gc_enable()

    def scan_dialog_hide_wrapper(self):
        self.scan_dialog.hide()
        self.tree.focus_set()

        self.tree_on_select()

    @restore_status_line
    @logwrapper
    def scan(self,compression_level,threads,group=None):
        path_to_scan_from_entry = abspath(self.path_to_scan_entry_var.get())

        if not path_to_scan_from_entry:
            self.get_info_dialog_on_scan().show('Error. ' + STR('No paths to scan.'),STR('Add paths to scan.'))
            return False

        #weryfikacja
        for e in range(self.CDE_ENTRIES_MAX):
            if self.CDE_use_var_list[e].get():
                mask = self.CDE_mask_var_list[e].get().strip()
                if not mask:
                    self.get_info_dialog_on_scan().show(STR('Wrong mask expression'),STR('Empty mask nr') + f':{e+1}.')
                    return False
                exe = self.CDE_executable_var_list[e].get().strip()
                if not exe:
                    self.get_info_dialog_on_scan().show(STR('Wrong executable'),STR('Empty executable nr') + f':{e+1}.')
                    return False

                #PARAM_INDICATOR_SIGN

                executable = self.CDE_executable_var_list[e].get()
                parameters = self.CDE_parameters_var_list[e].get()
                shell = self.CDE_shell_var_list[e].get()

                command,command_info = get_command(executable,parameters,'dummy full_file_path',shell)

        all_timeout_set = True
        for e in range(self.CDE_ENTRIES_MAX):
            if self.CDE_use_var_list[e].get():
                timeout = self.CDE_timeout_var_list[e].get().strip()

                try:
                    timeout_int = int(timeout)
                except:
                    all_timeout_set = False

        if not all_timeout_set:
            ask_dialog = self.get_ask_dialog_on_scan()
            ask_dialog.show(STR('CDE Timeout not set'),STR('Continue without Custom Data Extractor timeout ?'))

            if not ask_dialog.res_bool:
                return False


        self.last_dir = path_to_scan_from_entry

        new_label = self.scan_label_entry_var.get()

        self.main_update()

        #############################
        self_progress_dialog_on_scan = self.progress_dialog_on_scan = self.get_progress_dialog_on_scan()
        self_progress_dialog_on_scan_lab = self_progress_dialog_on_scan.lab
        self_progress_dialog_on_scan_area_main_update = self_progress_dialog_on_scan.area_main.update

        self_progress_dialog_on_scan_progr1var = self_progress_dialog_on_scan.progr1var
        self_progress_dialog_on_scan_progr2var = self_progress_dialog_on_scan.progr2var

        self_progress_dialog_on_scan_lab_r1_config = self_progress_dialog_on_scan.lab_r1.config
        self_progress_dialog_on_scan_lab_r2_config = self_progress_dialog_on_scan.lab_r2.config

        str_self_progress_dialog_on_scan_abort_button = str(self_progress_dialog_on_scan.abort_button)
        str_self_progress_dialog_on_scan_abort_single_button = str(self_progress_dialog_on_scan.abort_single_button)

        self_progress_dialog_on_scan.abort_single_button.pack_forget()
        #############################

        self_tooltip_message = self.tooltip_message
        self_configure_tooltip = self.configure_tooltip

        self_tooltip_message[str_self_progress_dialog_on_scan_abort_button]=STR('If you abort at this stage,\nData record will not be created.')
        self_progress_dialog_on_scan.abort_button.configure(image=self.ico_abort,text=STR("Cancel"),compound='left',width=15)

        self.scan_dialog.widget.update()

        self.action_abort=False
        self_progress_dialog_on_scan.abort_button.configure(state='normal')

        self_progress_dialog_on_scan.lab_l1.configure(text=STR('CDE Total space:'))
        self_progress_dialog_on_scan.lab_l2.configure(text=STR('CDE Files number:'))

        self_progress_dialog_on_scan_update_lab_text = self.progress_dialog_on_scan.update_lab_text
        self_progress_dialog_on_scan_update_lab_image = self_progress_dialog_on_scan.update_lab_image
        self_ico_empty = self.ico_empty

        self_progress_dialog_on_scan_update_lab_text(1,'')
        self_progress_dialog_on_scan_update_lab_image(2,self_ico_empty)
        self_progress_dialog_on_scan_update_lab_text(3,'')
        self_progress_dialog_on_scan_update_lab_text(4,'')

        self_progress_dialog_on_scan.show(STR('Creating new data record (scanning)'))

        local_bytes_to_str = bytes_to_str

        self_progress_dialog_on_scan_progr1var.set(0)
        self_progress_dialog_on_scan_lab_r1_config(text='- - - -')
        self_progress_dialog_on_scan_progr2var.set(0)
        self_progress_dialog_on_scan_lab_r2_config(text='- - - -')

        wait_var=BooleanVar()
        wait_var.set(False)

        self_progress_dialog_on_scan_lab[2].configure(image='',text='')

        any_cde_enabled=False
        cde_sklejka_list=[]
        cde_list=[]

        for e in range(self.CDE_ENTRIES_MAX):
            mask = self.CDE_mask_var_list[e].get().strip()
            smin = self.CDE_size_min_var_list[e].get().strip()
            smax = self.CDE_size_max_var_list[e].get().strip()
            exe = self.CDE_executable_var_list[e].get().strip()
            pars = self.CDE_parameters_var_list[e].get().strip()
            shell = self.CDE_shell_var_list[e].get()
            timeout = self.CDE_timeout_var_list[e].get().strip()
            crc = self.CDE_crc_var_list[e].get()

            smin_int = str_to_bytes(smin)
            smax_int = str_to_bytes(smax)

            try:
                timeout_int = int(timeout)
            except:
                timeout_int = None

            line_list = [
            '1' if self.CDE_use_var_list[e].get() else '0',
            mask,
            smin,
            smax,
            exe,
            pars,
            '1' if shell else '0',
            timeout,
            '1' if self.CDE_crc_var_list[e].get() else '0' ]

            cde_sklejka_list.append(line_list)

            if self.CDE_use_var_list[e].get():
                any_cde_enabled=True

                cde_list.append( (
                    tuple([elem.strip() for elem in mask.split(',')]),
                    bool(smin_int>=0),
                    smin_int,
                    bool(smax_int>=0),
                    smax_int,
                    exe,
                    pars,
                    shell,
                    timeout_int,
                    crc ) )

        self.cfg.set(CFG_KEY_CDE_SETTINGS,cde_sklejka_list)

        check_dev = self.single_device.get()

        #################################################################################################################################################

        include_hidden=self.cfg.get(CFG_KEY_include_hidden)

        try:
            with open(sep.join([self.temp_dir,SCAN_DAT_FILE]), "wb") as f:
                f.write(ZstdCompressor(level=8,threads=1).compress(dumps([new_label,path_to_scan_from_entry,check_dev,compression_level,threads,cde_list,include_hidden])))

        except Exception as e:
            print(e)
        else:
            creation_thread=Thread(target=lambda : librer_core.create_new_record(self.temp_dir,self.single_record_show,group),daemon=True)
            creation_thread.start()

            creation_thread_is_alive = creation_thread.is_alive

            #############################

            self_progress_dialog_on_scan_progr1var_set = self.progress_dialog_on_scan.progr1var.set
            self_progress_dialog_on_scan_progr2var_set = self.progress_dialog_on_scan.progr2var.set

            self_progress_dialog_on_scan_lab_r1_config = self.progress_dialog_on_scan.lab_r1.config
            self_progress_dialog_on_scan_lab_r2_config = self.progress_dialog_on_scan.lab_r2.config

            update_once=True

            prev_curr_files = curr_files = 0

            wait_var=BooleanVar()
            wait_var_set = wait_var.set
            wait_var_get = wait_var.get
            wait_var_set(False)

            self_main_after = self.main.after
            self_main_wait_variable = self.main.wait_variable

            self_get_hg_ico = self.get_hg_ico

            self_tooltip_message[str_self_progress_dialog_on_scan_abort_button]=STR('If you abort at this stage,\nData record will not be created.')
            self_configure_tooltip(str_self_progress_dialog_on_scan_abort_button)

            time_to_show_busy_sign=0

            switch_done=False

            prev_stage=-1
            while creation_thread_is_alive():
                try:
                    now=time()
                    ######################################################################################

                    if self.action_abort:
                        librer_core.abort()
                        self.action_abort=False
                    elif self.action_abort_single:
                        librer_core.abort_single()
                        self.action_abort_single=False

                    if prev_stage!=librer_core.stage:
                        self_progress_dialog_on_scan_update_lab_text(0,'')
                        self_progress_dialog_on_scan_update_lab_text(1,'')
                        self_progress_dialog_on_scan_update_lab_image(2,self_ico_empty)
                        self_progress_dialog_on_scan_update_lab_text(3,'')
                        self_progress_dialog_on_scan_update_lab_text(4,'')
                        prev_stage=librer_core.stage
                        switch_done=False

                    if librer_core.stage==0: #scan stage
                        if not switch_done:
                            self_progress_dialog_on_scan.widget.title(STR('Creating new data record (scanning)'))
                            self_progress_dialog_on_scan.abort_single_button.pack_forget()
                            switch_done=True

                        change3 = self_progress_dialog_on_scan_update_lab_text(3,local_bytes_to_str(librer_core.stdout_sum_size) )
                        change4 = self_progress_dialog_on_scan_update_lab_text(4,'%s files' % fnumber(librer_core.stdout_quant_files) )
                    elif librer_core.stage==1: #cde stage
                        if not switch_done:
                            self_progress_dialog_on_scan.widget.title(STR('Creating new data record (Custom Data Extraction)'))
                            self_progress_dialog_on_scan.abort_single_button.pack(side='left', anchor='center',padx=5,pady=5)

                            if threads==1:
                                self_progress_dialog_on_scan.abort_single_button.configure(image=self.ico_abort,text=STR('Abort single file'),compound='left',width=15,command=self.abort_single,state='normal')
                            else:
                                self_progress_dialog_on_scan.abort_single_button.configure(image=self.ico_abort,text=STR('Abort single file'),compound='left',width=15,state='disabled')

                            self_progress_dialog_on_scan.abort_button.configure(image=self.ico_abort,text=STR('Abort'),compound='left',width=15,state='normal')

                            self_tooltip_message[str_self_progress_dialog_on_scan_abort_button]=STR('If you abort at this stage,\nCustom Data will be incomplete.')
                            self_tooltip_message[str_self_progress_dialog_on_scan_abort_single_button]=STR('ABORT_PROGRESS_TOOLTIP')
                            switch_done=True

                        change3 = self_progress_dialog_on_scan_update_lab_text(3,STR('Extracted Custom Data: ') + local_bytes_to_str(librer_core.stdout_cde_size_extracted) )
                        change4 = self_progress_dialog_on_scan_update_lab_text(4,STR('Extraction Errors : ') + fnumber(librer_core.stdout_cde_errors_quant_all) )

                        files_q = librer_core.stdout_files_cde_quant

                        files_size = librer_core.stdout_files_cde_size
                        files_size_perc = files_size * 100.0 / librer_core.stdout_files_cde_size_sum if librer_core.stdout_files_cde_size_sum else 0

                        self_progress_dialog_on_scan_progr1var_set(files_size_perc)
                        self_progress_dialog_on_scan_progr2var_set(files_q * 100.0 / librer_core.stdout_files_cde_quant_sum if librer_core.stdout_files_cde_quant_sum else 0)

                        self_progress_dialog_on_scan_lab_r1_config(text=f'{local_bytes_to_str(librer_core.stdout_files_cde_size)} / {local_bytes_to_str(librer_core.stdout_files_cde_size_sum)}')
                        self_progress_dialog_on_scan_lab_r2_config(text=f'{fnumber(files_q)} / {fnumber(librer_core.stdout_files_cde_quant_sum)}')

                    else:
                        change3 = False
                        change4 = False

                        self_progress_dialog_on_scan.abort_button.configure(state='disabled')
                        self_progress_dialog_on_scan.abort_single_button.configure(state='disabled')

                        if len(librer_core.stdout_info_line_current)>50:
                            change0 = self_progress_dialog_on_scan_update_lab_text(0,f'...{librer_core.stdout_info_line_current[-50:]}')
                        else:
                            change0 = self_progress_dialog_on_scan_update_lab_text(0,librer_core.stdout_info_line_current)

                    ###############################################
                    if change3 or change4:
                        time_to_show_busy_sign=now+1.0

                        if update_once:
                            update_once=False
                            self_progress_dialog_on_scan_update_lab_image(2,self_ico_empty)
                            self_progress_dialog_on_scan_update_lab_text(0,'')
                    else :
                        if now>time_to_show_busy_sign:
                            if len(librer_core.stdout_info_line_current)>50:
                                change0 = self_progress_dialog_on_scan_update_lab_text(0,f'...{librer_core.stdout_info_line_current[-50:]}')
                            else:
                                change0 = self_progress_dialog_on_scan_update_lab_text(0,librer_core.stdout_info_line_current)

                            self_progress_dialog_on_scan_update_lab_image(2,self_get_hg_ico())
                            update_once=True
                    ###############################################

                except Exception as e:
                    print(e)
                    l_error(e)
                    change0 = self_progress_dialog_on_scan_update_lab_text(0,str(e))

                self_main_after(25,lambda : wait_var_set(not wait_var_get()))
                self_main_wait_variable(wait_var)

                ######################################################################################

            creation_thread.join

        self_progress_dialog_on_scan.hide(True)

        #################################################################################################################################################

        self.cfg.set(CFG_KEY_SINGLE_DEVICE,check_dev)
        self.cfg.write()

        self_progress_dialog_on_scan_update_lab_text(1,'')
        self_progress_dialog_on_scan_update_lab_image(2,self_ico_empty)
        self_progress_dialog_on_scan_update_lab_text(3,'')
        self_progress_dialog_on_scan_update_lab_text(4,'')

        self_progress_dialog_on_scan.abort_single_button.configure(state='disabled')
        self_progress_dialog_on_scan.abort_button.configure(state='disabled')

        self_progress_dialog_on_scan_update_lab_image(2,self_ico_empty)
        ##################################

        self.find_clear()

        return True

    def remove_record(self,record_par=None):
        record = record_par if record_par else self.current_record

        label = librer_core.get_record_name(record)
        path = record.header.scan_path
        creation_time = record.header.creation_time
        group = librer_core.get_record_group(record)
        size=record.header.sum_size

        dialog = self.get_simple_question_dialog()

        title=STR('Delete old data record with the same scanned path ?') if record_par else STR('Delete selected data record ?')
        message=librer_core.record_info_alias_wrapper(record,record.txtinfo_medium if record_par else record.txtinfo_short)

        if record_par:
            message = message + "\n\n" + "Custom Data and filestrucure in the old record may be different !" + "\n\n" + "This operation cannot be undone !"

        dialog.show(title,message )

        if dialog.res_bool:
            record_item = self.record_to_item[record]
            self.tree.delete(record_item)

            del self.record_to_item[record]
            del self.item_to_record[record_item]

            res=librer_core.delete_record(record)
            l_info(f'deleted file:{res}')

            if group:
                self.group_to_size_sum[group]-=size
                self.single_group_update_size(group)

            self.find_clear()

            self.status_record.configure(image = self.ico_empty, text = '---',compound='left')

            if remaining_items := self.tree.get_children():
                if item := remaining_items[0]:
                    self.tree.focus(item)
                    self.tree_on_select()
            else:
                self.sel_item = None

            self.tree.focus_set()

    def delete_action(self):
        if not self.block_processing_stack:
            item = self.sel_item

            is_group = bool(self.tree.tag_has(self.GROUP,item))
            is_record = bool(self.tree.tag_has(self.RECORD_RAW,item) or self.tree.tag_has(self.RECORD,item))

            if self.current_record and is_record:
                self.remove_record()

            elif self.current_group and is_group:
                self.remove_group()

    def scan_dialog_show(self):
        dialog = self.get_scan_dialog()

        group = None
        if self.current_group:
            group = self.current_group
        elif self.current_record :
            if group_temp:=librer_core.get_record_group(self.current_record):
                group = group_temp

        if group:
            dialog.widget.title(STR('Create new data record in group:') + f'{group}' )
            self.scan_dialog_group = group
        else:
            dialog.widget.title( STR('Create new data record') )
            self.scan_dialog_group = None

        self.status(STR("Opening dialog ..."))
        e=0
        sklejka_settings = self.cfg.get(CFG_KEY_CDE_SETTINGS)

        do_clear_settings = False
        if sklejka_settings:
            for e_section in sklejka_settings:
                try:
                    v1,v2,v3,v4,v5,v6,v7,v8,v9 = e_section

                    self.CDE_use_var_list[e].set(bool(v1=='1'))
                    self.CDE_mask_var_list[e].set(v2)
                    self.CDE_size_min_var_list[e].set(v3)
                    self.CDE_size_max_var_list[e].set(v4)
                    self.CDE_executable_var_list[e].set(v5)
                    self.CDE_parameters_var_list[e].set(v6)
                    self.CDE_shell_var_list[e].set(bool(v7=='1'))
                    self.CDE_timeout_var_list[e].set(v8)
                    self.CDE_crc_var_list[e].set(bool(v9=='1'))
                    e+=1
                except Exception as e:
                    print(e,e_section)
                    do_clear_settings=True

                    break
        else:
            do_clear_settings=True

        if do_clear_settings:
            for e in range(self.CDE_ENTRIES_MAX):
                self.CDE_use_var_list[e].set(False)
                self.CDE_mask_var_list[e].set('')
                self.CDE_size_min_var_list[e].set('')
                self.CDE_size_max_var_list[e].set('')
                self.CDE_executable_var_list[e].set('')
                self.CDE_parameters_var_list[e].set('')
                self.CDE_shell_var_list[e].set(False)
                self.CDE_timeout_var_list[e].set('')
                self.CDE_crc_var_list[e].set(False)

            self.cfg.set(CFG_KEY_CDE_SETTINGS,[])
            self.cfg.write()

        for e in range(self.CDE_ENTRIES_MAX):
            self.use_checkbutton_mod(e,False)

        self.configure_scan_button()

        dialog.do_command_after_show=lambda : self.status("")
        dialog.show()

    def set_dev_to_scan_menu(self):
        self.drives_menu.delete(0,'end')

        if not windows:
            try:
                labes_dict = get_dev_labes_dict()
            except Exception as lsblk_ex:
                print(lsblk_ex)

        for part in disk_partitions(all=False):
            filesystem_label=None

            if windows:
                if 'cdrom' in part.opts or part.fstype == '':
                    # skip cd-rom drives with no disk in it; they may raise
                    # ENOENT, pop-up a Windows GUI error for a non-ready
                    # partition or just hang.
                    continue

                try:
                    filesystem_label = GetVolumeInformation(part.mountpoint)[0]
                except Exception as lab_ex:
                    print(lab_ex)
            else:
                try:
                    filesystem_label = labes_dict[part.mountpoint]
                except Exception as lab_ex:
                    print(lab_ex)

            if part.fstype != 'squashfs':
                self.drives_menu.add_command(label=f'{part.mountpoint} ({filesystem_label})' if filesystem_label else part.mountpoint,command = lambda dev=part.mountpoint,label=filesystem_label : self.set_dev_to_scan(dev,label) )

    def set_dev_to_scan(self,dev,label=None):
        self.path_to_scan_entry_var.set(dev)
        self.scan_label_entry_var.set(label if label else dev)
        self.scan_label_entry.selection_range(0, 'end')

    def set_path_to_scan(self):
        initialdir = self.last_dir if self.last_dir else self.cwd
        if res:=askdirectory(title=STR('Select Directory'),initialdir=initialdir,parent=self.scan_dialog.area_main):
            self.last_dir = res
            self.path_to_scan_entry_var.set(normpath(abspath(res)))
            self.scan_label_entry.focus_set()
            self.scan_label_entry_var.set( platform_node() + ':' + str(abspath(self.path_to_scan_entry_var.get())) )
            self.scan_label_entry.selection_range(0, 'end')

    def threaded_simple_run(self,command_list,shell):
        l_info(f'threaded_simple_run {command_list=}')
        output_list_append = self.output_list.append

        try:
            self.subprocess = uni_popen(command_list,shell)
        except Exception as re:
            print('test run error',re,flush = True)
            output_list_append(str(re))
        else:
            subprocess_stdout_readline = self.subprocess.stdout.readline
            subprocess_poll = self.subprocess.poll
            while True:
                try:
                    line = subprocess_stdout_readline()
                except Exception as le:
                    #print(command_list,le,flush = True)
                    line = f'{le}'
                    self.test_decoding_error = True

                self.info_line = line
                output_list_append(line.rstrip('\n\r'))

                if not line and subprocess_poll() is not None:
                    self.returncode[0]=self.subprocess.returncode
                    break

        self.subprocess = True
        sys.exit(0) #thread

    def abort_single(self):
        self.status(STR("Abort single pressed ..."))
        l_info("Abort single pressed ...")
        self.action_abort_single=True

    def kill_test(self):
        if self.subprocess and self.subprocess!=True:
            kill_subprocess(self.subprocess)

    def cde_test(self,e):
        initialdir = self.last_dir if self.last_dir else self.cwd
        if full_file_path:=askopenfilename(title=STR('Select File'),initialdir=initialdir,parent=self.scan_dialog.area_main,filetypes=( (STR("All Files"),"*.*"),(STR("All Files"),"*.*") ) ):
            self.last_dir=dirname(full_file_path)

            executable = self.CDE_executable_var_list[e].get()
            parameters = self.CDE_parameters_var_list[e].get()
            shell = self.CDE_shell_var_list[e].get()
            timeout = self.CDE_timeout_var_list[e].get()

            try:
                timeout_int = int(timeout)
            except:
                timeout_int = None

            command,command_info = get_command(executable,parameters,normpath(full_file_path),shell)

            info = command_info + '\n' + ( ('\ntimeout:' + str(timeout_int)) if timeout_int else '') + f'\nshell:{"Yes" if shell else "No"}'

            ask_dialog = self.get_text_ask_dialog_on_scan()
            simple_progress_dialog_scan = self.get_simple_progress_dialog_on_scan()

            ask_dialog.show(STR('Test Custom Data Extractor on selected file ?'),info)
            self.store_text_dialog_fields(ask_dialog)

            wait_var=BooleanVar()
            wait_var.set(False)

            self_main_after = self.main.after
            self_main_wait_variable = self.main.wait_variable
            wait_var_set = wait_var.set
            wait_var_get = wait_var.get

            self.cfg.write()

            if ask_dialog.res_bool:
                self.returncode=[100]
                self.output_list = []

                self.action_abort=False
                crc = False

                self.test_decoding_error = False

                self.subprocess = None

                test_thread = Thread(target = lambda: self.threaded_simple_run(command,shell),daemon=True)

                simple_progress_dialog_scan.command_on_close=self.kill_test

                self.info_line=''
                simple_progress_dialog_scan_update_lab_text = simple_progress_dialog_scan.update_lab_text
                simple_progress_dialog_scan_update_lab_image = simple_progress_dialog_scan.update_lab_image
                simple_progress_dialog_scan_update_lab_text(0,'')
                simple_progress_dialog_scan_update_lab_text(1,'')
                simple_progress_dialog_scan.show(STR('Testing selected Custom Data Extractor'))

                test_thread.start()

                timeout_val=time()+float(timeout_int) if timeout_int else None

                while test_thread.is_alive():
                    simple_progress_dialog_scan_update_lab_image(2,self.get_hg_ico())

                    if timeout_val :
                        time_left = timeout_val-time()
                        if time_left>0:
                            simple_progress_dialog_scan_update_lab_text(0,f'timeout: {int(time_left)}')
                        else:
                            simple_progress_dialog_scan_update_lab_text(0,'')
                            self.output_list.append(f'Timeout {timeout_int}s.')
                            self.kill_test()

                    simple_progress_dialog_scan_update_lab_text(1,f'...{self.info_line[-50:]}')

                    self_main_after(25,lambda : wait_var_set(not wait_var_get()))
                    self_main_wait_variable(wait_var)

                test_thread.join()

                simple_progress_dialog_scan.hide(True)

                output = '\n'.join(self.output_list).strip()

                self.get_text_dialog_on_scan().show(STR('CDE Test finished') + f' {"OK" if self.returncode[0]==0 and not self.test_decoding_error else STR("with Error")}',output)
                self.store_text_dialog_fields(self.text_dialog_on_scan)

    def cde_up(self,e):
        e_up=e-1

        for n_list in [self.CDE_use_var_list,self.CDE_mask_var_list,self.CDE_size_min_var_list,self.CDE_size_max_var_list,self.CDE_executable_var_list,self.CDE_parameters_var_list,self.CDE_shell_var_list,self.CDE_timeout_var_list]:
            ve = n_list[e].get()
            v_e_up = n_list[e_up].get()

            n_list[e].set(v_e_up)
            n_list[e_up].set(ve)

            self.use_checkbutton_mod(e)
            self.use_checkbutton_mod(e_up)

    def cde_entry_open(self,e) :
        initialdir = self.last_dir if self.last_dir else self.cwd
        if res:=askopenfilename(title=STR('Select File'),initialdir=initialdir,parent=self.scan_dialog.area_main,filetypes=((STR("Executable Files"),"*.exe"),(STR("Bat Files"),"*.bat"),(STR("All Files"),"*.*")) if windows else ((STR("Bash Files"),"*.sh"),(STR("All Files"),"*.*")) ):
            self.last_dir=dirname(res)

            expr = normpath(abspath(res))
            self.CDE_executable_var_list[e].set(expr)

    @restore_status_line
    @block
    def access_filestructure(self,record):
        self.hide_tooltip()
        self.popup_unpost()
        self.status(STR('loading filestructure ...'))
        self.main.update()
        record.decompress_filestructure()

    @restore_status_line
    @block
    def access_customdata(self,record):
        self.hide_tooltip()
        self.popup_unpost()
        self.status(STR('loading Custom Data ...'))
        self.main.update()
        record.decompress_filestructure()
        record.decompress_customdata()

        item = self.record_to_item[record]
        self.tree.item(item,image=self.ico_record_cd_loaded)

    find_result_record_index = 0
    find_result_record_index = 0
    def set_find_result_record_index(self):
        if self.current_record:
            new_index=librer_core.records_sorted.index(self.current_record)
            if self.find_result_record_index != new_index:
                self.find_result_record_index = new_index
                self.find_result_index=0

    def set_find_result_indexes(self,subpath_list=None):
           if subpath_list:
            record = librer_core.records_sorted[self.find_result_record_index]

            if record:
                temp_index=0
                if record.find_results:
                    for found_result in record.find_results:
                        items_names_tuple,res_size,res_mtime = found_result
                        if items_names_tuple==subpath_list:
                            break
                        else:
                            temp_index+=1

                    self.find_result_index=temp_index

    @block
    def locate_found_item(self,item):
        record,items_names_tuple = self.found_item_to_data[item]

        self.access_filestructure(record)
        top_data_tuple = record.filestructure

        record_item = self.record_to_item[record]

        current_item = record_item

        self_open_item = self.open_item

        self_open_item(current_item)

        self_get_child_of_name = self.get_child_of_name
        self_tree_update = self.tree.update

        for item_name in items_names_tuple:
            child_item = self_get_child_of_name(record,current_item,item_name)

            if child_item:
                current_item = child_item
                self_open_item(current_item)
                self_tree_update()
            else:
                self.info_dialog_on_main.show('cannot find item:',item_name)
                break

        #if self.find_dialog_shown:
        #    self.tree.selection_set(current_item)
        #else:
        #    self.tree.focus(current_item)

        self.sel_item = current_item
        self.select_and_focus(current_item)
        #self.tree.update()

    def close_item(self,item=None):
        self.visible_items_uptodate=False

    @block
    def open_item(self,item=None):
        tree=self.tree

        if not item:
            item=tree.focus()

        if tree.tag_has(self.GROUP,item):
            pass
        else:
            children=tree.get_children(item)
            opened = tree.set(item,'opened')

            LUT_decode_loc = LUT_decode
            if opened=='0' and children:
                colname,sort_index,is_numeric,reverse,group_code,dir_code,non_dir_code = self.column_sort_last_params
                sort_index_local=sort_index

                sort_val_func = int if is_numeric else lambda x : x

                tree.delete(*children)

                self_FILE = self.FILE
                self_DIR = self.DIR
                self_SYMLINK = self.SYMLINK
                local_bytes_to_str = bytes_to_str

                new_items_values = {}

                ###############################################
                record_item,record_name,subpath_list = self.get_item_record(item)

                record = self.item_to_record[record_item]

                self_item_to_data = self.item_to_data

                if tree.tag_has(self.RECORD_RAW,item):
                    self.access_filestructure(record)

                    self_item_to_data[item] = record.filestructure
                    self.tree.item(item,tags=self.RECORD, image=self.ico_record_cd if record.has_cd() else self.ico_record)
                    self.tree_on_select() #tylko dla aktualizacji ikony

                top_data_tuple = self_item_to_data[item]

                (top_entry_name_nr,top_code,top_size,top_mtime) = top_data_tuple[0:4]

                top_is_dir,top_is_file,top_is_symlink,top_is_bind,top_has_cd,top_has_files,top_cd_ok,top_cd_aborted,top_cd_empty,top_aux2 = LUT_decode_loc[top_code]

                record_filenames = record.filenames

                self_ico_folder_error = self.ico_folder_error
                self_ico_folder_link = self.ico_folder_link
                self_ico_folder = self.ico_folder
                self_ico_cd_ok = self.ico_cd_ok
                self_ico_cd_error = self.ico_cd_error

                self_cd_ico_aborted = self.ico_cd_aborted
                self_cd_ico_empty = self.ico_cd_empty

                self_ico_empty = self.ico_empty

                record_find_results = record.find_results
                record_find_results_tuples_set = record.find_results_tuples_set

                self_FOUND = self.FOUND
                if top_has_files:
                    for data_tuple in top_data_tuple[4]:

                        (entry_name_nr,code,size,mtime) = data_tuple[0:4]

                        entry_name = record_filenames[entry_name_nr]

                        entry_subpath_tuple = tuple(subpath_list + [entry_name])

                        is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,cd_aborted,cd_empty,aux2 = LUT_decode_loc[code]

                        sub_data_tuple = None

                        elem_index = 4
                        if has_files:
                            sub_dictionary = True
                            sub_data_tuple = data_tuple[elem_index]
                            elem_index+=1
                        else:
                            sub_dictionary = False

                        if has_cd:
                            elem_index+=1

                        kind = self_DIR if is_dir else self_FILE

                        image = (self_ico_folder_error if size==-1 else self_ico_folder_link if is_symlink or is_bind else self_ico_folder) if is_dir else (self_ico_cd_ok if cd_ok else self_cd_ico_aborted if cd_aborted else self_cd_ico_empty if cd_empty else self_ico_cd_error) if has_cd else self_ico_empty

                        if is_symlink or is_bind:
                            tags=self_SYMLINK
                        else:
                            tags=self_FOUND if self.any_valid_find_results and entry_subpath_tuple in record_find_results_tuples_set else ''

                        #('data','record','opened','path','size','size_h','ctime','ctime_h','kind')
                        values = (entry_name,'','0',entry_name,size,bytes_to_str(size),mtime,strftime('%Y/%m/%d %H:%M:%S',localtime_catched(mtime)),kind)
                        sort_index = ( dir_code if is_dir else non_dir_code , sort_val_func(values[sort_index_local]) )
                        new_items_values[ ( sort_index,values,entry_name,image,bool(has_files) ) ] = (has_files,tags,data_tuple)

                    tree_insert = tree.insert
                    for (sort_index,values,entry_name,image,sub_dictionary_bool),(has_files,tags,data_tuple) in sorted(new_items_values.items(),key = lambda x : x[0][0],reverse=reverse) :
                        new_item=tree_insert(item,'end',iid=None,values=values,open=False,text=entry_name,image=image,tags=tags)
                        self_item_to_data[new_item] = data_tuple
                        if sub_dictionary_bool:
                            tree_insert(new_item,'end') #dummy_sub_item
                            #if to_the_bottom:
                            #    self.open_item(new_item,to_the_bottom)

                    tree.set(item,'opened','1')

        self.visible_items_uptodate=False

    def get_record_raw_icon(self,record):
        return self.ico_record_raw_cd if record.has_cd() else self.ico_record_raw

    @logwrapper
    def groups_show(self):
        #('data','record','opened','path','size','size_h','ctime','ctime_h','kind')
        self.group_to_item = {}
        self.group_to_size_sum = {}

        self.group_to_size_sum[None]=0
        self.group_to_item[None]=''

        for group in librer_core.groups:
            self.single_group_show(group)

    def single_group_update_size(self, group):
        sum_size = self.group_to_size_sum[group]
        self.tree.item(self.group_to_item[group],values=(group,group,0,'',sum_size,bytes_to_str(sum_size),0,'',self.GROUP))

    def single_group_show(self,group):
        self.group_to_size_sum[group]=0
        group_item=self.tree.insert('','end',iid=None,open=False,text=group,image=self.ico_group,tags=self.GROUP)

        self.group_to_item[group] = group_item
        self.single_group_update_size(group)

        self.sel_item = group_item
        self.tree.focus(group_item)
        #self.tree.see(group_item)
        self.wrapped_see(group_item)

        self.tree_item_focused(group_item)

        self.column_sort(self.tree)

    @block_and_log
    def single_record_show(self,record,expand_groups=True):
        size=record.header.sum_size

        #('data','record','opened','path','size','size_h','ctime','ctime_h','kind')
        values = (librer_core.get_record_name(record),librer_core.get_record_name(record),0,record.header.scan_path,size,bytes_to_str(size),record.header.creation_time,strftime('%Y/%m/%d %H:%M:%S',localtime_catched(record.header.creation_time)),self.RECORD)

        group = librer_core.get_record_group(record)
        group_item = self.group_to_item[group]

        self_tree = self.tree

        record_item=self_tree.insert(group_item,'end',iid=None,values=values,open=False,text=librer_core.get_record_name(record),image=self.get_record_raw_icon(record),tags=self.RECORD_RAW)
        self_tree.insert(record_item,'end',text='dummy') #dummy_sub_item

        self_tree.item(group_item, open = expand_groups)

        self.group_to_size_sum[group]+=size
        self.single_group_update_size(group)

        self.tree_sort_item(None)

        self.item_to_record[record_item]=record
        self.record_to_item[record]=record_item

        if expand_groups:
            self_tree.focus(record_item)
            #self_tree.see(record_item)
            self.wrapped_see(record_item)
        else:
            self_tree.focus(group_item)
            #self_tree.see(group_item)
            self.wrapped_see(group_item)

        self.tree_on_select()

        records_len=len(librer_core.records)
        self.status_records_all_configure(STR('Records') + f':{records_len}')

        self.record_filename_to_record[record.file_name] = record

        sum_size=0
        quant_files=0
        for record_temp in librer_core.records:
            sum_size+=record_temp.header.sum_size
            quant_files+=record_temp.header.quant_files

        self.widget_tooltip(self.status_records_all,STR('Records in repository  ') + f': {records_len}\n' + STR('Sum data size         ') + f': {bytes_to_str(sum_size)}\n' + STR('Sum files quantity    ') + f': {fnumber(quant_files)}\n\n' + STR('Click to unload (free memory) data of selected record\nDouble click to unload data of all records.'))

        self.main_update()

        self.find_clear()

        self.column_sort(self_tree)

    def tree_update(self,item):
        self_tree = self.tree

        self_tree.see(item)
        self_tree.update()

        #self.wrapped_see(item)

    folder_items=set()
    folder_items_clear=folder_items.clear
    folder_items_add=folder_items.add

    @logwrapper
    def clip_copy_full_path_with_file(self):
        try:
            item=self.tree.focus()
            record_item,record_name,subpath_list = self.get_item_record(item)
            record = self.item_to_record[record_item]
            self.main.clipboard_clear()
            self.main.clipboard_append(normpath(sep.join([record.header.scan_path,sep.join(subpath_list)])))

            if subpath_list:
                self.status(STR('Full path copied to clipboard'))
        except:
            #np seleckcja na grupe
            pass

    @logwrapper
    def clip_copy(self,what):
        self.main.clipboard_clear()
        self.main.clipboard_append(what)
        self.status(STR('Copied to clipboard:') + '"' + str(what) + '"')

    def return_results_tree(self):
        if item:=self.results_tree.focus():
            try:
                record,subpath_list = self.found_item_to_data[item]

                self.locate_found_item(item)

                self.current_record=record
                self.set_find_result_record_index()
                self.set_find_result_indexes(subpath_list)

                self.find_results_close()
            except:
                #rekord nie zamyka
                pass

    def double_left_button_results_tree(self,event):
        if self.results_tree.identify("region", event.x, event.y) != 'heading':
            if item:=self.results_tree.identify('item',event.x,event.y):
                try:
                    record,subpath_list = self.found_item_to_data[item]

                    self.locate_found_item(item)

                    self.current_record=record
                    self.set_find_result_record_index()
                    self.set_find_result_indexes(subpath_list)

                    self.find_results_close()
                except:
                    #rekord nie zamyka
                    pass


    def double_left_button(self,event):
        if not self.block_processing_stack:
            tree=event.widget
            if tree.identify("region", event.x, event.y) != 'heading':
                if item:=tree.identify('item',event.x,event.y):
                    if self.tree.tag_has(self.RECORD,item) or self.tree.tag_has(self.RECORD_RAW,item):
                        self.record_info()
                    else:
                        self.main.after_idle(self.show_customdata)
        return "break"

    @logwrapper
    def show_customdata(self):
        if not self.block_processing_stack:
            item=self.tree.focus()
            if item:
                error_infos=[]
                try:
                    kind = self.tree.set(item,'kind')

                    if kind in (self.GROUP,self.DIR,self.DIRLINK):
                        return False

                    if self.tree.tag_has(self.RECORD,item) or self.tree.tag_has(self.RECORD_RAW,item):
                        #self.record_info()
                        return False
                    else:
                        record_item,record_name,subpath_list = self.get_item_record(item)
                        record = self.item_to_record[record_item]

                        if item in self.item_to_data: #dla rekordu nie spelnione
                            data_tuple = self.item_to_data[item]
                            (entry_name,code,size,mtime) = data_tuple[0:4]

                            is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,cd_aborted,cd_empty,aux2 = LUT_decode[code]

                            if has_cd: #wiec nie has_files
                                cd_index = data_tuple[4]
                                error_infos.append(f'{cd_index=},type:{type(cd_index)}')

                                self.access_customdata(record)
                                cd_field = record.customdata[cd_index]

                                error_infos.append(' '.join(str(cd_field)))
                                if cd_data := cd_field[2]:
                                    rule_nr=cd_field[0]
                                    returncode=cd_field[1]

                                    expressions,use_smin,smin_int,use_smax,smax_int,executable,parameters,shell,timeout,crc = record.header.cde_list[rule_nr]

                                    file_path = normpath(sep.join([record.header.scan_path,sep.join(subpath_list)]))

                                    cd_txt = str(cd_data)

                                    command,command_info = get_command(executable,parameters,file_path,shell)

                                    shell_info = (STR('No'),STR('Yes'))[shell]
                                    timeout_info = f'\ntimeout:{timeout}' if timeout else ''
                                    self.get_text_info_dialog().show(STR('Custom Data of') + f': {file_path}',cd_txt,uplabel_text=f"{command_info}\n\nshell:{shell_info}{timeout_info}\nreturncode:{returncode}\nsize:{bytes_to_str(asizeof(cd_txt))}")
                                    self.store_text_dialog_fields(self.text_info_dialog)
                                    return True

                            self.info_dialog_on_main.show(STR('Information'),STR('No Custom data.'))

                except Exception as e:
                    self.info_dialog_on_main.show('Custom Data Info Error',str(e) + ('\n' + '\n'.join(error_infos)) if error_infos else '')

        return False

    def record_info(self):
        if not self.block_processing_stack:
            if self.current_record:
                time_info = strftime('%Y/%m/%d %H:%M:%S',localtime_catched(self.current_record.header.creation_time))
                self.get_text_info_dialog().show(STR('Record Info'),librer_core.record_info_alias_wrapper(self.current_record,self.current_record.txtinfo) )
                self.store_text_dialog_fields(self.text_info_dialog)

    def purify_items_cache(self):
        self_item_to_data = self.item_to_data
        self_tree_exists = self.tree.exists
        for item in list(self_item_to_data):
            if not self_tree_exists(item):
                del self_item_to_data[item]

    @block_and_log
    def unload_record(self,record=None):
        if not record:
            record = self.current_record

        if record:
            record_item = self.record_to_item[record]

            self_tree = self.tree

            self_tree.delete(*self_tree.get_children(record_item))

            if record_item in self.item_to_data:
                del self.item_to_data[record_item]
                self.purify_items_cache()

            record.unload_filestructure()
            record.unload_customdata()

            self_tree.insert(record_item,'end',text='dummy') #dummy_sub_item
            self_tree.set(record_item,'opened','0')
            self_tree.item(record_item, open=False)

            self_tree.item(record_item, image=self.get_record_raw_icon(record),tags=self.RECORD_RAW)
            self_tree.focus(record_item)
            #self_tree.see(record_item)
            #self.wrapped_see(record_item)
            #self.tree_on_select()

            #self.visible_items_update()
            self.select_and_focus(record_item)

    @block_and_log
    def unload_all_recods(self):
        for record in librer_core.records:
            self.unload_record(record)

    @logwrapper
    def show_log(self):
        try:
            if windows:
                self.status('opening: %s' % log)
                startfile(log)
            else:
                self.status('executing: xdg-open "%s"' % log)
                system("xdg-open "+ '"' + log + '"')
        except Exception as e:
            l_error(e)
            self.status(str(e))

    @logwrapper
    def show_logs_dir(self):
        try:
            if windows:
                self.status('opening: %s' % LOG_DIR)
                startfile(LOG_DIR)
            else:
                self.status('executing: xdg-open "%s"' % LOG_DIR)
                system("xdg-open " + '"' + LOG_DIR + '"')
        except Exception as e:
            l_error(e)
            self.status(str(e))

    @logwrapper
    def show_homepage(self):
        try:
            if windows:
                self.status('opening: %s' % HOMEPAGE)
                startfile(HOMEPAGE)
            else:
                self.status('executing: xdg-open %s' % HOMEPAGE)
                system("xdg-open " + HOMEPAGE)
        except Exception as e:
            l_error(e)
            self.status(str(e))

if __name__ == "__main__":
    try:
        allocs, g1, g2 = gc_get_threshold()
        gc_set_threshold(100_000, g1*5, g2*10)

        LIBRER_FILE = normpath(__file__)
        LIBRER_DIR = dirname(LIBRER_FILE)

        is_frozen = bool(getattr(sys, 'frozen', False) or "__compiled__" in globals())

        LIBRER_EXECUTABLE_FILE = normpath(abspath(sys.executable if is_frozen else sys.argv[0]))
        LIBRER_EXECUTABLE_DIR = dirname(LIBRER_EXECUTABLE_FILE)
        DATA_DIR = sep.join([LIBRER_EXECUTABLE_DIR,'data'])
        LOG_DIR = sep.join([LIBRER_EXECUTABLE_DIR,'logs'])

        if windows:
            if is_frozen:
                record_exe = [sep.join([LIBRER_EXECUTABLE_DIR,'record.exe']) ]
            else:
                record_exe = ['python',sep.join([LIBRER_EXECUTABLE_DIR,'record.py']) ]
        else:
            if is_frozen:
                record_exe = [sep.join([LIBRER_EXECUTABLE_DIR,'record']) ]
            else:
                record_exe = ['python3',sep.join([LIBRER_EXECUTABLE_DIR,'record.py']) ]

        #print(f'{is_frozen=}\n{record_exe=}\n')

        #######################################################################

        VER_TIMESTAMP = get_ver_timestamp()

        log_file = strftime('%Y_%m_%d_%H_%M_%S',localtime_catched(time())) +'.txt'
        log=abspath(LOG_DIR + sep + log_file)

        Path(LOG_DIR).mkdir(parents=True,exist_ok=True)
        Path(DATA_DIR).mkdir(parents=True,exist_ok=True)

        print('log:',log)

        logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s', filename=log,filemode='w')

        l_info('LIBRER %s',VER_TIMESTAMP)
        l_info('executable: %s',LIBRER_EXECUTABLE_FILE)

        try:
            distro_info=Path(path_join(LIBRER_DIR,'distro.info.txt')).read_text(encoding='ASCII') + f'\nrecord file format version: {DATA_FORMAT_VERSION}'
        except Exception as exception_1:
            l_error(exception_1)
            distro_info = 'Error. No distro.info.txt file.'
        else:
            l_info('distro info:\n%s',distro_info)

        librer_core = LibrerCore(DATA_DIR,record_exe,logging)

        Gui(getcwd())

    except Exception as e_main:
        print(e_main)
        l_error(e_main)
        sys.exit(1)
