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

from os import sep,system,getcwd,name as os_name,cpu_count
from os.path import abspath,normpath,dirname,join as path_join,isfile as path_isfile
from gc import disable as gc_disable, enable as gc_enable,collect as gc_collect,set_threshold as gc_set_threshold, get_threshold as gc_get_threshold

from pathlib import Path
from time import strftime,time,mktime
from signal import signal,SIGINT

from tkinter import Tk,Toplevel,PhotoImage,Menu,Label,LabelFrame,Frame,StringVar,BooleanVar,IntVar
from tkinter.ttk import Treeview,Checkbutton,Radiobutton,Scrollbar,Button,Menubutton,Entry,Scale,Style
from tkinter.filedialog import askdirectory,asksaveasfilename,askopenfilename,askopenfilenames
from threading import Thread
from traceback import format_stack
import sys
import logging
from pickle import dumps, loads
from zstandard import ZstdCompressor,ZstdDecompressor
from ciso8601 import parse_datetime
from psutil import disk_partitions
from librer_images import librer_image

from shutil import rmtree
from re import compile as re_compile

from dialogs import *
from core import *

windows = bool(os_name=='nt')

if windows:
    from os import startfile
    from win32api import GetVolumeInformation

#l_debug = logging.debug
l_info = logging.info
l_warning = logging.warning
l_error = logging.error

###########################################################################################################################################

CFG_KEY_CDE_SETTINGS = 'cde_settings'
CFG_KEY_SINGLE_DEVICE = 'single_device'

CFG_KEY_SINGLE_DEVICE = 'single_device'

CFG_KEY_find_size_min = 'find_size_min'
CFG_KEY_find_size_max = 'find_size_max'

CFG_KEY_find_modtime_min = 'find_modtime_min'
CFG_KEY_find_modtime_max = 'find_modtime_max'

CFG_KEY_find_range_all = 'find_range_all'
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

CFG_KEY_export_cd = 'export_cd'
CFG_KEY_export_crc = 'export_crc'

CFG_KEY_import_cd = 'export_cd'
CFG_KEY_import_crc = 'export_crc'

CFG_last_dir = 'last_dir'
CFG_geometry = 'geometry'
CFG_SORTING = 'sorting'
CFG_KEY_show_popups = 'show_popups'
CFG_KEY_groups_collapse = 'groups_collapse'

cfg_defaults={
    CFG_KEY_SINGLE_DEVICE:True,
    CFG_KEY_CDE_SETTINGS:[],

    CFG_KEY_find_range_all:False,
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

    CFG_KEY_export_cd:True,
    CFG_KEY_export_crc:True,

    CFG_KEY_import_cd:True,
    CFG_KEY_import_crc:True,

    CFG_last_dir:'.',
    CFG_geometry:'',
    CFG_KEY_show_popups:True,
    CFG_KEY_groups_collapse:True
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

                cde_sklejka_list=[line_list1,line_list1a,line_list2,line_list3,line_list4,line_list4a,line_list5,line_list5a]
            else:
                line_list1 =  ['0','*.7z,*.zip,*.bz2,*.xz,*.z,*.gzip,*.iso,*.rar,*.arj,*.lzh,*.lzma,*.vdi,*.vhd','','','7z','l %','0','10','0']
                line_list2 =  ['0','*.txt,*.nfo','1','256kB','cat','%','0','5','0']
                line_list3 =  ['0','*.pls,*.m3u,*.cue,*.plp,*.m3u8,*.mpcpl','','','cat','%','0','5','0']
                line_list4 =  ['0','*.aac,*.ac3,*.aiff,*.dts,*.dtshd,*.flac,*.h261,*.h263,*.h264,*.iff,*.m4v,*.matroska,*.mpc,*.mp3,*.mp4,*.mpeg,*.mkv,*.ts,*.ogg,*.wav,*.wv','','','ffprobe','-hide_banner %','0','5','0']
                line_list5 =  ['0','*.jpg','','','exif','%','0','5','0']

                cde_sklejka_list=[line_list1,line_list2,line_list3,line_list4,line_list5]
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
        gc_disable()
        self.block_processing_stack_append(caller_id)

        disable = lambda menu : self.menubar_entryconfig(menu, state="disabled")

        _ = {disable(menu) for menu in ("File","Help") }

        self.menubar_config(cursor='watch')
        self.main_config(cursor='watch')

    ################################################
    def processing_on(self,caller_id=None):
        self.block_processing_stack_pop()

        if not self.block_processing_stack:
            norm = lambda menu : self.menubar_entryconfig(menu, state="normal")

            _ = {norm(menu) for menu in ("File","Help") }

            self.main_config(cursor='')
            self.menubar_config(cursor='')
            gc_collect()
            gc_enable()

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

        self.cwd=cwd

        self.cfg = Config(DATA_DIR)
        self.cfg.read()

        self.cfg_get=self.cfg.get

        self.last_dir = self.cfg_get(CFG_last_dir).replace('/',sep)

        signal(SIGINT, lambda a, k : self.handle_sigint())

        self.main_locked_by_child=None
        ####################################################################
        self_main = self.main = Tk()

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
        #self_hg_ico = self.hg_ico
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
        style = Style()

        style.theme_create("dummy", parent='vista' if windows else 'clam' )

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
        style_configure("Treeview",rowheight=18)

        style_configure("TScale", background=self.bg_color)
        style_configure('TScale.slider', background=self.bg_color)
        style_configure('TScale.Horizontal.TScale', background=self.bg_color)

        bg_focus='#90DD90'
        bg_focus_off='#90AA90'
        #bg_sel='#AAAAAA'

        style_map('Treeview', background=[('focus',bg_focus),('selected',bg_focus_off),('','white')])

        #style_map('semi_focus.Treeview', background=[('focus',bg_focus),('selected',bg_focus_off),('','white')])

        #style_map('no_focus.Treeview', background=[('focus',bg_focus),('selected',bg_sel),('','white')])
        #style_map('no_focus.Treeview', background=[('focus',bg_sel),('selected',bg_sel),('','white')])

        #works but not for every theme
        #style_configure("Treeview", fieldbackground=self.bg_color)

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
        self.widget_tooltip(self.status_records_all,'All records in repository')
        self.status_records_all.bind("<ButtonPress-1>", lambda event : self.unload_record() )
        self.status_records_all.bind("<Double-Button-1>", lambda event : self.unload_all_recods() )

        self.status_record=Label(status_frame,image=self.ico_record,text='--',width=200,borderwidth=2,bg=self.bg_color,relief='groove',anchor='w')
        self.status_record.pack(fill='x',expand=0,side='left')
        self.status_record_configure = lambda x : self.status_record.configure(image = self.ico_record, text = x,compound='left')

        self.widget_tooltip(self.status_record,'Selected record')
        self.status_record.bind("<ButtonPress-1>", lambda event : self.record_info() )

        self.status_info = Label(status_frame,text='Initializing...',relief='sunken',borderwidth=1,bg=self.bg_color,anchor='w')
        self.status_info.pack(fill='x',expand=1,side='left')
        self_status_info_configure = self.status_info.configure
        self.status= lambda x : self_status_info_configure(text = x)

        self.status_find = Label(status_frame,image=self.ico_find,relief='flat',state='disabled',borderwidth=1,bg=self.bg_color,width=18)
        self.status_find.pack(fill='x',expand=0,side='right')
        self_status_find_configure = self.status_find.configure
        self.status_find.bind("<ButtonPress-1>", lambda event : self.finder_wrapper_show() )
        self.status_find_tooltip = lambda message : self.widget_tooltip(self.status_find,message)

        self.status_find_tooltip_default = 'No search results\nClick to open find dialog.'
        self.status_find_tooltip(self.status_find_tooltip_default)

        ##############################################################################
        tree = self.tree = Treeview(self_main,takefocus=True,show=('tree','headings') )

        self.tree_set = tree.set
        self.tree_see = tree.see
        self.tree_get_children = self.tree.get_children
        self.tree_focus = lambda item : self.tree.focus(item)

        self_org_label = self.org_label = {}

        self_org_label['#0']='Name'
        self_org_label['size_h']='Size'
        self_org_label['ctime_h']='Time'

        tree["columns"]=('data','record','opened','path','size','size_h','ctime','ctime_h','kind')
        tree["displaycolumns"]=('size_h','ctime_h')
        self.real_display_columns=('#0','size_h','ctime_h')

        tree_column = tree.column

        tree_column('#0', width=120, minwidth=100, stretch='yes')
        tree_column('size_h', width=80, minwidth=80, stretch='no',anchor='e')
        tree_column('ctime_h', width=150, minwidth=100, stretch='no',anchor='e')

        tree_heading = tree.heading
        tree_heading('#0',text='Name \u25B2',anchor='w')
        tree_heading('size_h',anchor='w',text=self_org_label['size_h'])
        tree_heading('ctime_h',anchor='n',text=self_org_label['ctime_h'])

        tree_yview = tree.yview
        self.tree_scrollbar = Scrollbar(self_main, orient='vertical', command=tree_yview,takefocus=False)

        tree.configure(yscrollcommand=self.tree_scrollbar_set)

        self.tree_scrollbar.pack(side='right',fill='y',expand=0)
        tree.pack(fill='both',expand=1, side='left')

        tree_tag_configure = tree.tag_configure

        tree_tag_configure(self.RECORD_RAW, foreground='gray')
        tree_tag_configure(self.RECORD, foreground='green')
        tree_tag_configure(self.SYMLINK, foreground='gray')
        tree_tag_configure(self.FOUND, foreground='red')

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
            item_actions_state=('disabled','normal')[self.sel_item is not None]

            self.file_cascade.delete(0,'end')
            if not self.block_processing_stack:
                self_file_cascade_add_command = self.file_cascade.add_command
                self_file_cascade_add_separator = self.file_cascade.add_separator
                state_on_records = 'normal' if librer_core.records else 'disabled'

                state_has_cd = ('disabled','normal')[self.item_has_cd(self.tree.focus())]

                item_actions_state=('disabled','normal')[self.sel_item is not None]
                self_file_cascade_add_command(label = 'New Record ...',command = self.scan_dialog_show, accelerator="Ctrl+N",image = self.ico_record_new,compound='left')

                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = 'Import record ...', accelerator='Ctrl+I', command = self.record_import,image = self.ico_record_import,compound='left')
                self_file_cascade_add_command(label = 'Import "Where Is It?" xml ...', command = self.record_import_wii,image = self.ico_empty,compound='left')
                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = 'Find ...',command = self.finder_wrapper_show, accelerator="Ctrl+F",image = self.ico_find,compound='left',state = 'normal' if librer_core.records else 'disabled')
                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = 'Settings ...',command = self.settings_show, accelerator="F12",image = self.ico_empty,compound='left',state = 'normal')
                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = 'Clear Search Results',command = self.find_clear, image = self.ico_empty,compound='left',state = 'normal' if self.any_valid_find_results else 'disabled')
                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = 'Exit',command = self.exit,image = self_ico['exit'],compound='left')

        self.file_cascade= Menu(menubar,tearoff=0,bg=self.bg_color,postcommand=file_cascade_post)
        menubar.add_cascade(label = 'File',menu = self.file_cascade,accelerator="Alt+F")

        def help_cascade_post():
            self.help_cascade.delete(0,'end')
            if not self.block_processing_stack:

                self_help_cascade_add_command = self.help_cascade.add_command
                self_help_cascade_add_separator = self.help_cascade.add_separator

                self_help_cascade_add_command(label = 'About',command=lambda : self.get_about_dialog().show(),accelerator="F1", image = self_ico['about'],compound='left')
                self_help_cascade_add_command(label = 'License',command=lambda : self.get_license_dialog().show(), image = self.ico_license,compound='left')
                self_help_cascade_add_separator()
                self_help_cascade_add_command(label = 'Open current Log',command=self.show_log, image = self_ico['log'],compound='left')
                self_help_cascade_add_command(label = 'Open logs directory',command=self.show_logs_dir, image = self_ico['logs'],compound='left')
                self_help_cascade_add_separator()
                self_help_cascade_add_command(label = 'Open homepage',command=self.show_homepage, image = self_ico['home'],compound='left')

        self.help_cascade= Menu(menubar,tearoff=0,bg=self.bg_color,postcommand=help_cascade_post)

        menubar.add_cascade(label = 'Help',menu = self.help_cascade)

        #######################################################################
        self.reset_sels()

        self_REAL_SORT_COLUMN = self.REAL_SORT_COLUMN = self.REAL_SORT_COLUMN={}

        self_REAL_SORT_COLUMN['#0'] = 'data'
        self_REAL_SORT_COLUMN['size_h'] = 'size'
        self_REAL_SORT_COLUMN['ctime_h'] = 'ctime'

        self_REAL_SORT_COLUMN_INDEX = self.REAL_SORT_COLUMN_INDEX = self.REAL_SORT_COLUMN_INDEX={}

        #tree["displaycolumns"]
        for disply_column in self.real_display_columns:
            self_REAL_SORT_COLUMN_INDEX[disply_column] = tree["columns"].index(self_REAL_SORT_COLUMN[disply_column])

        self_REAL_SORT_COLUMN_IS_NUMERIC = self.REAL_SORT_COLUMN_IS_NUMERIC = self.REAL_SORT_COLUMN_IS_NUMERIC={}

        self_REAL_SORT_COLUMN_IS_NUMERIC['#0'] = False
        self_REAL_SORT_COLUMN_IS_NUMERIC['size_h'] = True
        self_REAL_SORT_COLUMN_IS_NUMERIC['ctime_h'] = True

        try:
            self.column_sort_last_params = self.cfg_get(CFG_SORTING)
        except:
            #colname,sort_index,is_numeric,reverse,dir_code,non_dir_code
            self.column_sort_last_params=('#0',self_REAL_SORT_COLUMN_INDEX['#0'],self_REAL_SORT_COLUMN_IS_NUMERIC['#0'],0,0,1)

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
        self_progress_dialog_on_load_area_main_update = self_progress_dialog_on_load.area_main.update

        self_progress_dialog_on_load_progr1var = self_progress_dialog_on_load.progr1var
        self_progress_dialog_on_load_progr2var = self_progress_dialog_on_load.progr2var

        self_progress_dialog_on_load_lab_r1_config = self_progress_dialog_on_load.lab_r1.config
        self_progress_dialog_on_load_lab_r2_config = self_progress_dialog_on_load.lab_r2.config

        str_self_progress_dialog_on_load_abort_button = str(self_progress_dialog_on_load.abort_button)

        #############################

        self.tooltip_message[str_self_progress_dialog_on_load_abort_button]='Abort loading.'
        self_progress_dialog_on_load.abort_button.configure(image=self.ico_cancel,text='Abort',compound='left')
        self_progress_dialog_on_load.abort_button.pack( anchor='center',padx=5,pady=5)

        self.action_abort=False
        self.action_abort_single=False
        self_progress_dialog_on_load.abort_button.configure(state='normal')

        self.status_info.configure(image='',text = 'Checking records to load ...')
        records_quant,records_size = librer_core.read_records_pre()

        load_errors = []

        self.groups_show()

        if records_quant:
            self.status_info.configure(image='',text = 'Loading records ...')

            read_thread=Thread(target=lambda : librer_core.threaded_read_records(load_errors),daemon=True)
            read_thread_is_alive = read_thread.is_alive

            self_progress_dialog_on_load.lab_l1.configure(text='Records space:')
            self_progress_dialog_on_load.lab_l2.configure(text='Records number:' )
            self_progress_dialog_on_load.show('Loading records')

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

                    self_single_record_show(new_rec)
                else:
                    self_main_after(25,lambda : wait_var_set(not wait_var_get()))
                    self_main_wait_variable(wait_var)

                if self.action_abort:
                    librer_core.abort()

            self_progress_dialog_on_load.hide(True)
            read_thread.join()

            if self.action_abort:
                self.info_dialog_on_main.show('Records loading aborted','Restart Librer to gain full access to the recordset.')


        if load_errors:
            self.get_text_info_dialog().show('Loading errors','\n\n'.join(load_errors) )

        self.menu_enable()
        self.menubar_config(cursor='')
        self.main_config(cursor='')

        self.tree_semi_focus()

        #for child in self.tree.get_children():
        #    self.tree.item(child, open=False)

        self.status_info.configure(image='',text = 'Ready')

        tree_bind = tree.bind

        tree_bind('<ButtonPress-1>', self.tree_on_mouse_button_press)
        tree_bind('<Double-Button-1>', self.double_left_button)
        tree_bind("<Motion>", self.motion_on_tree)
        tree_bind("<Leave>", lambda event : self.widget_leave())

        tree_bind('<KeyPress>', self.key_press )
        tree_bind('<<TreeviewOpen>>', lambda event : self.open_item())
        tree_bind('<ButtonPress-3>', self.context_menu_show)

        tree_bind("<<TreeviewSelect>>", lambda event : self.tree_select())

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

        self_main_bind('<Alt-Return>', lambda event : self.record_info())
        self_main_bind('<Return>', lambda event : self.show_customdata())

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

        gc_collect()
        gc_enable()

        self.any_valid_find_results = False
        self.external_find_params_change=True

        self.temp_dir = mkdtemp()
        #print(f'{self.temp_dir=}')

        self.processing_on()

        self_main.mainloop()

    def tree_focus_out(self):
        tree = self.tree
        item=tree.focus()
        if item:
            tree.selection_set(item)
            self.selected=item

    selected=None

    def tree_focus_in(self):
        tree = self.tree
        try:
            if selection := tree.selection():
                tree.selection_remove(*selection)
                item=selection[0]
                tree.focus(item)
                tree_sel_change(item,True)
            elif item:=self.selected:
                tree.focus(item)
                tree_sel_change(item,True)

        except Exception as e:
            l_error(f'groups_tree_focus_in:{e}')

    def tree_scrollbar_set(self,v1,v2):
        if v1=='0.0' and v2=='1.0':
            self.tree_scrollbar.pack_forget()
        else:
            self.tree_scrollbar.set(v1,v2)
            self.tree_scrollbar.pack(side='right',fill='y',expand=0)

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
        self.status("Abort pressed ...")
        self.action_abort=True

    def progress_dialog_load_abort(self):
        self.status("Abort pressed ...")
        self.action_abort=True

    def progress_dialog_abort(self):
        self.status("Abort pressed ...")
        l_info("Abort pressed ...")
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
            self.status("Creating dialog ...")

            self.text_info_dialog = TextDialogInfo(self.main,self.main_icon_tuple,self.bg_color,pre_show=self.pre_show,post_close=self.post_close)

            self.fix_text_dialog(self.text_info_dialog)

            self.text_info_dialog_created = True

        return self.text_info_dialog


    simple_question_dialog_created = False
    @restore_status_line
    @block
    def get_simple_question_dialog(self):
        if not self.simple_question_dialog_created:
            self.status("Creating dialog ...")

            self.simple_question_dialog = LabelDialogQuestion(self.main,(self.ico_record_delete,self.ico_record_delete),self.bg_color,pre_show=self.pre_show,post_close=self.post_close,image=self.ico_warning)

            self.simple_question_dialog.label.configure(justify='left')
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
            self.status("Creating dialog ...")

            self_ico_librer = self.ico_librer

            self.scan_dialog=dialog=GenericDialog(self.main,(self.ico_record_new,self.ico_record_new),self.bg_color,'---',pre_show=self.pre_show,post_close=self.post_close,min_width=800,min_height=550)

            self_ico = self.ico

            #self.log_skipped_var=BooleanVar()
            #self.log_skipped_var.set(False)

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

            ul_lab=Label(temp_frame,text="Label:",bg=self.bg_color,anchor='w')
            ul_lab.grid(row=0, column=4, sticky='news',padx=4,pady=4)\

            label_tooltip = "Internal Label of the record to be created"
            self.widget_tooltip(ul_lab,label_tooltip)

            self.scan_label_entry_var=StringVar(value='')
            self.scan_label_entry = Entry(temp_frame,textvariable=self.scan_label_entry_var)
            self.scan_label_entry.grid(row=0, column=5, sticky='news',padx=4,pady=4)

            self.widget_tooltip(self.scan_label_entry,label_tooltip)

            (path_to_scan_label := Label(temp_frame,text="Path:",bg=self.bg_color,anchor='w')).grid(row=0, column=0, sticky='news',padx=4,pady=4)
            self.widget_tooltip(path_to_scan_label,"Path to scan")

            self.path_to_scan_entry_var=StringVar(value=self.last_dir)
            path_to_scan_entry = Entry(temp_frame,textvariable=self.path_to_scan_entry_var)
            path_to_scan_entry.grid(row=0, column=1, sticky='news',padx=4,pady=4)
            self.widget_tooltip(path_to_scan_entry,"Path to scan")

            self.add_path_button = Button(temp_frame,width=18,image = self.ico_open, command=self.set_path_to_scan,underline=0)
            self.add_path_button.grid(row=0, column=2, sticky='news',padx=4,pady=4)
            self.widget_tooltip(self.add_path_button,"Set path to scan.")

            self.add_dev_button = Menubutton(temp_frame,width=18,image = self.ico_drive,underline=0)
            self.add_dev_button.grid(row=0, column=3, sticky='news',padx=4,pady=4)
            self.widget_tooltip(self.add_dev_button,"Select device to scan.")

            self.drives_menu = Menu(self.add_dev_button, tearoff=0,postcommand=self.set_dev_to_scan_menu)
            self.add_dev_button["menu"] = self.drives_menu

            temp_frame.grid_columnconfigure(1, weight=1)

            ##############
            self.scan_button = Button(dialog.area_buttons,width=12,text="Scan",compound='left',command=self.scan_wrapper,underline=0)
            self.scan_button.pack(side='right',padx=4,pady=4)
            self.widget_tooltip(self.scan_button,'Start scanning.\n\nIf any Custom Data Extractor is enabled it will be executed\nwith every file that meets its criteria (mask & size).')

            self.scan_cancel_button = Button(dialog.area_buttons,width=12,text="Cancel",command=self.scan_dialog_hide_wrapper)
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

            (compr_label := Label(scan_options_frame, text='Compression:',bg=self.bg_color,relief='flat')).pack(side='left',padx=2,pady=2)
            (compr_scale := Scale(scan_options_frame, variable=self.scan_compr_var, orient='horizontal',from_=0, to=22,command=lambda x : self.scan_comp_set(),style="TScale",length=160)).pack(fill='x',side='left',expand=1,padx=2)
            (compr_in_label := Label(scan_options_frame, textvariable=self.scan_compr_var_int,width=3,bg=self.bg_color,relief='groove',borderwidth=2)).pack(side='left',padx=2,pady=2)
            compr_tooltip = "Data record internal compression. A higher value\nmeans a smaller file and longer compression time.\nvalues above 20 may result in extremely long compression\nand memory consumption. The default value is 9."
            self.widget_tooltip(compr_scale,compr_tooltip)
            self.widget_tooltip(compr_label,compr_tooltip)
            self.widget_tooltip(compr_in_label,compr_tooltip)

            (threads_in_label := Label(scan_options_frame, textvariable=self.scan_threads_var_int,width=3,bg=self.bg_color,relief='groove',borderwidth=2)).pack(side='right',padx=2,pady=2)
            (threads_scale := Scale(scan_options_frame, variable=self.scan_threads_var, orient='horizontal',from_=0, to=cpu_count(),command=lambda x : self.scan_threads_set(),style="TScale",length=160)).pack(fill='x',side='right',expand=1,padx=2)
            (threads_label := Label(scan_options_frame, text='CDE Threads:',bg=self.bg_color,relief='flat')).pack(side='left',padx=2,pady=2)
            threads_tooltip = "Number of threads used to extract Custom Data\n\n0 - all available CPU cores\n1 - single thread (default value)\n\nThe optimal value depends on the CPU cores performace,\nIO subsystem performance and Custom Data Extractor specifics.\n\nConsider limitations of parallel CDE execution e.g.\nnumber of licenses of used software,\nused working directory, needed memory etc."
            self.widget_tooltip(threads_scale,threads_tooltip)
            self.widget_tooltip(threads_label,threads_tooltip)
            self.widget_tooltip(threads_in_label,threads_tooltip)

            self.single_device=BooleanVar()
            single_device_button = Checkbutton(dialog.area_buttons,text='one device mode',variable=self.single_device)
            single_device_button.pack(side='right',padx=2,pady=2)
            self.single_device.set(self.cfg_get(CFG_KEY_SINGLE_DEVICE))
            self.widget_tooltip(single_device_button,"Don't cross device boundaries (mount points, bindings etc.) - recommended")

            dialog.focus=self.scan_cancel_button

            ############
            temp_frame3 = LabelFrame(dialog.area_main,text='Custom Data Extractors:',borderwidth=2,bg=self.bg_color,takefocus=False)
            temp_frame3.grid(row=3,column=0,sticky='news',padx=4,pady=4,columnspan=3,ipadx=4,ipady=4)

            sf_par3 = SFrame(temp_frame3,bg=self.bg_color)
            sf_par3.pack(fill='both',expand=True,side='top')
            self.cde_frame = cde_frame = sf_par3.frame()

            (lab_criteria := Label(cde_frame,text='% File cryteria',bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=0, column=2,sticky='news',columnspan=3)
            (lab_command := Label(cde_frame,text='Custom Data extractor command',bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=0, column=5,sticky='news',columnspan=4)
            (lab_mask := Label(cde_frame,text='File Mask',bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=1, column=2,sticky='news')
            (lab_min := Label(cde_frame,image=self.ico_bigger,bg=self.bg_color,anchor='center',relief='groove',bd=2,width=40)).grid(row=1, column=3,sticky='news')
            (lab_max := Label(cde_frame,image=self.ico_smaller,bg=self.bg_color,anchor='center',relief='groove',bd=2,width=40)).grid(row=1, column=4,sticky='news')
            (lab_shell := Label(cde_frame,image=self.ico_shell,bg=self.bg_color,anchor='center',relief='groove',bd=2)).grid(row=1, column=5,sticky='news')
            (lab_open := Label(cde_frame,text='',bg=self.bg_color,anchor='n')).grid(row=1, column=6,sticky='news')
            (lab_exec := Label(cde_frame,text='Executable',bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=1, column=7,sticky='news')
            (lab_pars  := Label(cde_frame,text='Parameters',bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=1, column=8,sticky='news')
            (lab_timeout := Label(cde_frame,image=self.ico_timeout,bg=self.bg_color,anchor='center',relief='groove',bd=2,width=3)).grid(row=1, column=9,sticky='news')
            (lab_test := Label(cde_frame,image=self.ico_test_col,bg=self.bg_color,anchor='center',relief='groove',bd=2)).grid(row=1, column=10,sticky='news')

            up_tooltip = "Use the arrow to change the order\nin which CDE criteria are checked.\n\nIf a file meets several CDE criteria\n(mask & size), the one with higher priority\nwill be executed. In this table, the first\none from the top has the highest priority,\nthe next ones have lower and lower priority."
            use_tooltip = "Mark to use CD Extractor"
            mask_tooltip = "Glob expresions separated by comma (',')\ne.g.: '*.7z, *.zip, *.gz'\n\nthe given executable will run\nwith every file matching the expression\n(and size citeria if provided)"
            size_common_tooltip = 'Integer value [in bytes] or integer with unit.\nLeave the value blank to ignore this criterion.\n\nexamples:\n399\n100B\n125kB\n10MB'
            max_tooltip = 'Maximum file size.\n\n' + size_common_tooltip
            min_tooltip = 'Minimum file size.\n\n'+ size_common_tooltip
            exec_tooltip = "Binary executable, batch script, or entire command\n(depending on the 'shell' option setting)\nthat will run with the full path to the scanned file.\nThe executable may have a full path, be located in a PATH\nenvironment variable, or be interpreted by the system shell\n\ncheck 'shell' option tooltip."
            pars_tooltip = f"The executable will run with the full path to the file to extract as a parameter.\nIf other constant parameters are necessary, they should be placed here\nand the scanned file should be indicated with the '{PARAM_INDICATOR_SIGN}' sign.\nThe absence of the '{PARAM_INDICATOR_SIGN}' sign means that the file will be passed as the last parameter.\ne.g.:const_param % other_const_param"
            shell_example = '"C:\\Program Files\\7-Zip\\7z.exe" l % | more +13' if windows else "7z l % | tail -n +14"
            shell_tooltip = f"Execute in the system shell.\n\nWhen enabled\nCommand with parameters will be passed\nto the system shell as single string\nThe use of pipes, redirection etc. is allowed.\nUsing of quotes (\") may be necessary. Scanned\nfiles will be automatically enclosed with quotation marks.\nExample:\n{shell_example}\n\nWhen disabled\nAn executable file must be specified,\nthe contents of the parameters field will be\nsplitted and passed as a parameters list.\n\nIn more complicated cases\nit is recommended to prepare a dedicated shell\nscript and use it as a shell command."
            open_tooltip = "Choose the executable file to serve as a custom data extractor..."
            timeout_tooltip = "Timeout limit in seconds for single CD extraction.\nAfter timeout executed process will be terminated\n\n'0' or empty field means no timeout."
            test_tooltip_common = "Before you run scan, and therefore run your CDE on all\nfiles that will match on the scan path,\ntest your Custom Data Extractor\non a single, manually selected file.\nCheck if it's getting the expected data\nand has no unexpected side-effects."
            test_tooltip = "Select a file and test your Custom Data Extractor.\n\n" + test_tooltip_common

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
        dialog.find_lab.configure(image=self.ico_search_text,text=' Search:',compound='left',bg=self.bg_color)
        dialog.find_prev_butt.configure(image=self.ico_left)
        dialog.find_next_butt.configure(image=self.ico_right)

        self.widget_tooltip(dialog.find_prev_butt,'Select Prev (Shift+F3)')
        self.widget_tooltip(dialog.find_next_butt,'Select Next (F3)')
        self.widget_tooltip(dialog.find_cs,'Case Sensitive')
        self.widget_tooltip(dialog.find_info_lab,'index of the selected search result / search results total ')

        dialog.find_cs_var.set(False if windows else True)

    progress_dialog_on_scan_created = False
    @restore_status_line
    @block
    def get_progress_dialog_on_scan(self):
        if not self.progress_dialog_on_scan_created:
            self.status("Creating dialog ...")

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
            self.status("Creating dialog ...")

            self.simple_progress_dialog_on_scan = ProgressDialog(self.scan_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget : self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False),ShowProgress=False,min_width=400,min_height=200)

            self.simple_progress_dialog_on_scan.command_on_close = self.progress_dialog_abort

            self.widget_tooltip(self.simple_progress_dialog_on_scan.abort_button,'Abort test')

            str_simple_progress_dialog_scan_abort_button = str(self.simple_progress_dialog_on_scan.abort_button)
            self.tooltip_message[str_simple_progress_dialog_scan_abort_button]='Abort test.'

            self.simple_progress_dialog_on_scan_created = True

        return self.simple_progress_dialog_on_scan

    info_dialog_on_scan_created = False
    @restore_status_line
    @block
    def get_info_dialog_on_scan(self):
        if not self.info_dialog_on_scan_created:
            self.status("Creating dialog ...")

            self.info_dialog_on_scan = LabelDialog(self.scan_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))
            self.info_dialog_on_scan_created = True

        return self.info_dialog_on_scan

    text_dialog_on_scan_created = False
    @restore_status_line
    @block
    def get_text_dialog_on_scan(self):
        if not self.text_dialog_on_scan_created:
            self.status("Creating dialog ...")

            self.text_dialog_on_scan = TextDialogInfo(self.scan_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget : self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))

            self.fix_text_dialog(self.text_dialog_on_scan)

            self.text_dialog_on_scan_created = True

        return self.text_dialog_on_scan

    text_ask_dialog_on_scan_created = False
    @restore_status_line
    @block
    def get_text_ask_dialog_on_scan(self):
        if not self.text_ask_dialog_on_scan_created:
            self.status("Creating dialog ...")

            self.text_ask_dialog_on_scan = TextDialogQuestion(self.scan_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False),image=self.ico_warning)

            self.fix_text_dialog(self.text_ask_dialog_on_scan)

            self.text_ask_dialog_on_scan_created = True

        return self.text_ask_dialog_on_scan

    ask_dialog_on_scan_created = False
    @restore_status_line
    @block
    def get_ask_dialog_on_scan(self):
        if not self.ask_dialog_on_scan_created:
            self.status("Creating dialog ...")

            self.ask_dialog_on_scan = LabelDialogQuestion(self.scan_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False),image=self.ico_warning)

            self.ask_dialog_on_scan_created = True

        return self.ask_dialog_on_scan

    text_ask_dialog_on_main_created = False
    @restore_status_line
    @block
    def get_text_ask_dialog_on_main(self):
        if not self.text_ask_dialog_on_main_created:
            self.status("Creating dialog ...")

            self.text_ask_dialog_on_main = TextDialogQuestion(self.main,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))

            self.fix_text_dialog(self.text_ask_dialog_on_main)
            #,image=self.ico_warning
            self.text_ask_dialog_on_main_created = True

        return self.text_ask_dialog_on_main

    progress_dialog_on_find_created = False
    @restore_status_line
    @block
    def get_progress_dialog_on_find(self):
        if not self.progress_dialog_on_find_created:
            self.status("Creating dialog ...")

            self.progress_dialog_on_find = ProgressDialog(self.find_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))
            self.progress_dialog_on_find.command_on_close = self.progress_dialog_find_abort
            self.widget_tooltip(self.progress_dialog_on_find.abort_button,'Abort searching.')

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

            self.repack_dialog=GenericDialog(self.main,self.main_icon_tuple,self.bg_color,'Rename / Repack record',pre_show=self.pre_show,post_close=self.post_close,min_width=400,min_height=200)
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

            (label_frame := LabelFrame(self.repack_dialog.area_main,text='Record Label',bd=2,bg=self.bg_color,takefocus=False)).grid(row=0,column=0,sticky='news',padx=4,pady=4,columnspan=2)
            Entry(label_frame,textvariable=self.repack_label_var).pack(expand='yes',fill='x',padx=2,pady=2)

            (repack_frame := LabelFrame(self.repack_dialog.area_main,text='Data options',bd=2,bg=self.bg_color,takefocus=False)).grid(row=1,column=0,sticky='news',padx=4,pady=4,columnspan=2)
            self.repack_dialog.area_main.grid_columnconfigure( 0, weight=1)
            self.repack_dialog.area_main.grid_columnconfigure( 1, weight=1)

            self.repack_dialog.area_main.grid_rowconfigure( 2, weight=1)

            self.repack_cd_cb = Checkbutton(repack_frame,text='Keep \'Custom Data\'',variable=self.repack_cd_var)
            #self.repack_crc_cb = Checkbutton(repack_frame,text='Include CRC values',variable=self.repack_crc_var)

            self.repack_cd_cb.grid(row=0, column=0, sticky='wens',padx=4,pady=4)
            #self.repack_crc_cb.grid(row=1, column=0, sticky='wens',padx=4,pady=4)

            repack_frame.grid_columnconfigure( 0, weight=1)

            (repack_frame_compr := LabelFrame(self.repack_dialog.area_main,text='Compression (0-22)',bd=2,bg=self.bg_color,takefocus=False)).grid(row=2,column=0,sticky='news',padx=4,pady=4,columnspan=2)

            Scale(repack_frame_compr, variable=self.repack_compr_var, orient='horizontal',from_=0, to=22,command=lambda x : self.repack_comp_set(),style="TScale").pack(fill='x',side='left',expand=1,padx=2)
            Label(repack_frame_compr, textvariable=self.repack_compr_var_int,width=3,bg=self.bg_color,relief='ridge').pack(side='right',padx=2,pady=2)

            Button(self.repack_dialog.area_buttons, text='Proceed', width=14 , command= self.repack_to_local).pack(side='left', anchor='n',padx=5,pady=5)
            Button(self.repack_dialog.area_buttons, text='Close', width=14, command=self.repack_dialog.hide ).pack(side='right', anchor='n',padx=5,pady=5)

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
            self.wii_import_dialog=GenericDialog(self.main,self.main_icon_tuple,self.bg_color,'Where Is It ? import records',pre_show=self.pre_show,post_close=self.post_close,min_width=400,min_height=200)
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

            (wii_import_frame := LabelFrame(self.wii_import_dialog.area_main,text='Options',bd=2,bg=self.bg_color,takefocus=False)).grid(row=2,column=0,sticky='news',padx=4,pady=4,columnspan=2)
            self.wii_import_dialog.area_main.grid_columnconfigure( 0, weight=1)
            self.wii_import_dialog.area_main.grid_columnconfigure( 1, weight=1)

            self.wii_import_dialog.area_main.grid_rowconfigure( 2, weight=1)

            self.wii_import_separate_cb = Checkbutton(wii_import_frame,text=' Separate record per each disk (not recommended)',variable=self.wii_import_separate,command = self.wii_import_dialog_name_state)
            self.wii_import_separate_cb.grid(row=0, column=0, sticky='wens',padx=4,pady=4,columnspan=2)

            Label(wii_import_frame,text='Common record label:',anchor='w').grid(row=1, column=0, sticky='wens',padx=4,pady=4)
            self.wii_import_label_entry = Entry(wii_import_frame,textvariable=self.wii_import_label_var)
            self.wii_import_label_entry.grid(row=1, column=1, sticky='wens',padx=4,pady=4)

            wii_import_frame.grid_columnconfigure( 0, weight=1)
            wii_import_frame.grid_columnconfigure( 1, weight=1)

            (wii_import_frame_compr := LabelFrame(self.wii_import_dialog.area_main,text='Compression (0-22)',bd=2,bg=self.bg_color,takefocus=False)).grid(row=3,column=0,sticky='news',padx=4,pady=4,columnspan=2)

            Scale(wii_import_frame_compr, variable=self.wii_import_compr_var, orient='horizontal',from_=0, to=22,command=lambda x : self.wii_import_comp_set(),style="TScale").pack(fill='x',side='left',expand=1,padx=2)
            Label(wii_import_frame_compr, textvariable=self.wii_import_compr_var_int,width=3,bg=self.bg_color,relief='ridge').pack(side='right',padx=2,pady=2)

            Button(self.wii_import_dialog.area_buttons, text='Proceed', width=14 , command= self.wii_import_to_local).pack(side='left', anchor='n',padx=5,pady=5)
            Button(self.wii_import_dialog.area_buttons, text='Close', width=14, command=self.wii_import_dialog.hide ).pack(side='right', anchor='n',padx=5,pady=5)

            self.wii_import_dialog_created = True

        return self.wii_import_dialog

    entry_ask_dialog_created = False
    @restore_status_line
    @block
    def get_entry_ask_dialog(self):
        if not self.entry_ask_dialog_created:
            self.status("Creating dialog ...")
            self.entry_ask_dialog = EntryDialogQuestion(self.main,self.main_icon_tuple,self.bg_color,pre_show=self.pre_show,post_close=self.post_close)
            self.entry_ask_dialog_created = True
        return self.entry_ask_dialog

    assign_to_group_dialog_created = False
    @restore_status_line
    @block
    def get_assign_to_group_dialog(self):
        if not self.assign_to_group_dialog_created:
            self.status("Creating dialog ...")
            self.assign_to_group_dialog = ComboboxDialogQuestion(self.main,self.main_icon_tuple,self.bg_color,pre_show=self.pre_show,post_close=self.post_close)
            self.assign_to_group_dialog_created = True
        return self.assign_to_group_dialog

    settings_dialog_created = False
    @restore_status_line
    @block
    def get_settings_dialog(self):
        if not self.settings_dialog_created:
            self.status("Creating dialog ...")

            self.settings_dialog=GenericDialog(self.main,self.main_icon_tuple,self.bg_color,'Settings',pre_show=self.pre_show,post_close=self.post_close)

            sfdma = self.settings_dialog.area_main

            self.show_popups_var = BooleanVar()
            self.popups_cb = Checkbutton(sfdma,text='Show tooltips',variable=self.show_popups_var,command=self.popups_show_mod)
            self.popups_cb.grid(row=0, column=0, sticky='news',padx=4,pady=4)

            self.groups_collapsed_var = BooleanVar()
            self.popups_cb = Checkbutton(sfdma,text='Groups collapsed at startup',variable=self.groups_collapsed_var,command=self.groups_collapse_mod)
            self.popups_cb.grid(row=1, column=0, sticky='news',padx=4,pady=4)

            sfdma.grid_columnconfigure( 0, weight=1)

            Button(self.settings_dialog.area_buttons, text='Close', width=14, command=self.settings_close ).pack(side='right', anchor='n',padx=5,pady=5)

            self.settings_dialog_created = True

        self.show_popups_var.set(self.cfg.get(CFG_KEY_show_popups))
        self.groups_collapsed_var.set(self.cfg.get(CFG_KEY_groups_collapse))

        return self.settings_dialog

    def popups_show_mod(self):
        self.cfg.set(CFG_KEY_show_popups,self.show_popups_var.get())

    def groups_collapse_mod(self):
        self.cfg.set(CFG_KEY_groups_collapse,self.groups_collapsed_var.get())

    def settings_close(self):
        self.settings_dialog.hide()

    find_dialog_created = False
    @restore_status_line
    @block
    def get_find_dialog(self):
        if not self.find_dialog_created:
            self.status("Creating dialog ...")

            ###################################
            self.find_dialog=GenericDialog(self.main,self.main_icon_tuple,self.bg_color,'Search records',pre_show=self.pre_show,post_close=self.post_close)

            #self.find_size_use_var = BooleanVar()
            self.find_filename_search_kind_var = StringVar()
            self.find_cd_search_kind_var = StringVar()

            self.find_range_all = BooleanVar()

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

            (find_filename_frame := LabelFrame(sfdma,text='Search range',bd=2,bg=self.bg_color,takefocus=False)).grid(row=0,column=0,sticky='news',padx=4,pady=4)
            self.find_range_cb1 = Radiobutton(find_filename_frame,text='Selected record / group',variable=self.find_range_all,value=False,command=self.find_mod)
            self.find_range_cb1.grid(row=0, column=0, sticky='news',padx=4,pady=4)
            self.find_range_cb1.bind('<Return>', lambda event : self.find_items())

            find_range_cb2 = Radiobutton(find_filename_frame,text='All records',variable=self.find_range_all,value=True,command=self.find_mod)
            find_range_cb2.grid(row=0, column=1, sticky='news',padx=4,pady=4)
            find_range_cb2.bind('<Return>', lambda event : self.find_items())

            (find_filename_frame := LabelFrame(sfdma,text='Path elements',bd=2,bg=self.bg_color,takefocus=False)).grid(row=1,column=0,sticky='news',padx=4,pady=4)

            r_dont = Radiobutton(find_filename_frame,text="Don't use this criterion",variable=self.find_filename_search_kind_var,value='dont',command=self.find_mod,width=30)
            r_dont.grid(row=0, column=0, sticky='news',padx=4,pady=4)
            r_dont.bind('<Return>', lambda event : self.find_items())

            #Radiobutton(find_filename_frame,text="files with error on access",variable=self.find_filename_search_kind_var,value='error',command=self.find_mod)
            #.grid(row=1, column=0, sticky='news',padx=4,pady=4)

            regexp_radio_name=Radiobutton(find_filename_frame,text="by regular expression",variable=self.find_filename_search_kind_var,value='regexp',command=self.find_mod)
            regexp_radio_name.grid(row=2, column=0, sticky='news',padx=4,pady=4)
            regexp_radio_name.bind('<Return>', lambda event : self.find_items())

            glob_radio_name=Radiobutton(find_filename_frame,text="by glob pattern",variable=self.find_filename_search_kind_var,value='glob',command=self.find_mod)
            glob_radio_name.grid(row=3, column=0, sticky='news',padx=4,pady=4)
            glob_radio_name.bind('<Return>', lambda event : self.find_items())

            fuzzy_radio_name=Radiobutton(find_filename_frame,text="by fuzzy match",variable=self.find_filename_search_kind_var,value='fuzzy',command=self.find_mod)
            fuzzy_radio_name.grid(row=4, column=0, sticky='news',padx=4,pady=4)
            fuzzy_radio_name.bind('<Return>', lambda event : self.find_items())

            regexp_tooltip = "Regular expression\n"
            regexp_tooltip_name = "Checked on the file\nor folder name."
            regexp_tooltip_cd = "Checked on the entire\nCustom Data of a file."

            glob_tooltip = "An expression containing wildcard characters\nsuch as '*','?' or character range '[a-c]'.\n\nPlace '*' at the beginning and end of an expression\nunless you want the expression to be found exactly\nat the beginning or end of a path element\n\n"
            glob_tooltip_name = 'Checked on the file or folder name.'
            glob_tooltip_cd = 'Checked on the entire Custom Data of a file.'

            fuzzy_tooltip = 'Fuzzy matching is implemented using SequenceMatcher\nfrom the difflib module. Any file whose similarity\nscore exceeds the threshold will be classified as found.\nThe similarity score is calculated\n'
            fuzzy_tooltip_name = 'based on the file or folder name.'
            fuzzy_tooltip_cd = 'based on the entire Custom Data of a file.'

            self.find_filename_regexp_entry = Entry(find_filename_frame,textvariable=self.find_name_regexp_var,validate="key")
            self.find_filename_glob_entry = Entry(find_filename_frame,textvariable=self.find_name_glob_var,validate="key")
            self.find_filename_fuzz_entry = Entry(find_filename_frame,textvariable=self.find_name_fuzz_var,validate="key")

            self.find_filename_regexp_entry.bind("<KeyRelease>", self.find_mod_keypress)
            self.find_filename_glob_entry.bind("<KeyRelease>", self.find_mod_keypress)
            self.find_filename_fuzz_entry.bind("<KeyRelease>", self.find_mod_keypress)

            self.find_filename_regexp_entry.grid(row=2, column=1, sticky='we',padx=4,pady=4)
            self.find_filename_glob_entry.grid(row=3, column=1, sticky='we',padx=4,pady=4)
            self.find_filename_fuzz_entry.grid(row=4, column=1, sticky='we',padx=4,pady=4)

            self.find_filename_case_sens_cb = Checkbutton(find_filename_frame,text='Case sensitive',variable=self.find_name_case_sens_var,command=self.find_mod)
            self.find_filename_case_sens_cb.grid(row=3, column=2, sticky='wens',padx=4,pady=4,columnspan=2)

            self.find_filename_fuzzy_threshold_lab = Label(find_filename_frame,text='Threshold:',bg=self.bg_color,anchor='e')
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

            (find_cd_frame := LabelFrame(sfdma,text='Custom Data',bd=2,bg=self.bg_color,takefocus=False)).grid(row=2,column=0,sticky='news',padx=4,pady=4)

            r_dont2 = Radiobutton(find_cd_frame,text="Don't use this criterion",variable=self.find_cd_search_kind_var,value='dont',command=self.find_mod,width=30)
            r_dont2.grid(row=0, column=0, sticky='news',padx=4,pady=4)
            r_dont2.bind('<Return>', lambda event : self.find_items())

            r_without = Radiobutton(find_cd_frame,text="No Custom Data",variable=self.find_cd_search_kind_var,value='without',command=self.find_mod)
            r_without.grid(row=1, column=0, sticky='news',padx=4,pady=4)
            r_without.bind('<Return>', lambda event : self.find_items())

            r_correct = Radiobutton(find_cd_frame,text="Any correct Custom Data",variable=self.find_cd_search_kind_var,value='any',command=self.find_mod)
            r_correct.grid(row=2, column=0, sticky='news',padx=4,pady=4)
            r_correct.bind('<Return>', lambda event : self.find_items())

            r_error = Radiobutton(find_cd_frame,text="Error on CD extraction",variable=self.find_cd_search_kind_var,value='error',command=self.find_mod)
            r_error.grid(row=3, column=0, sticky='news',padx=4,pady=4)
            r_error.bind('<Return>', lambda event : self.find_items())

            r_error_empty = Radiobutton(find_cd_frame,text="No CD extracted (empty value)",variable=self.find_cd_search_kind_var,value='empty',command=self.find_mod)
            r_error_empty.grid(row=4, column=0, sticky='news',padx=4,pady=4)
            r_error_empty.bind('<Return>', lambda event : self.find_items())

            r_error_empty = Radiobutton(find_cd_frame,text="CD extraction aborted",variable=self.find_cd_search_kind_var,value='aborted',command=self.find_mod)
            r_error_empty.grid(row=5, column=0, sticky='news',padx=4,pady=4)
            r_error_empty.bind('<Return>', lambda event : self.find_items())

            regexp_radio_cd = Radiobutton(find_cd_frame,text="by regular expression",variable=self.find_cd_search_kind_var,value='regexp',command=self.find_mod)
            regexp_radio_cd.grid(row=6, column=0, sticky='news',padx=4,pady=4)
            regexp_radio_cd.bind('<Return>', lambda event : self.find_items())

            glob_radio_cd = Radiobutton(find_cd_frame,text="by glob pattern",variable=self.find_cd_search_kind_var,value='glob',command=self.find_mod)
            glob_radio_cd.grid(row=7, column=0, sticky='news',padx=4,pady=4)
            glob_radio_cd.bind('<Return>', lambda event : self.find_items())

            fuzzy_radio_cd = Radiobutton(find_cd_frame,text="by fuzzy match",variable=self.find_cd_search_kind_var,value='fuzzy',command=self.find_mod)
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

            self.cd_case_sens_cb = Checkbutton(find_cd_frame,text='Case sensitive',variable=self.find_cd_case_sens_var,command=self.find_mod)
            self.cd_case_sens_cb.grid(row=7, column=2, sticky='wens',padx=4,pady=4,columnspan=2)

            self.find_cd_fuzzy_threshold_lab = Label(find_cd_frame,text='Threshold:',bg=self.bg_color,anchor='e')
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

            (find_size_frame := LabelFrame(sfdma,text='File size',bd=2,bg=self.bg_color,takefocus=False)).grid(row=3,column=0,sticky='news',padx=4,pady=4)
            find_size_frame.grid_columnconfigure((0,1,2,3), weight=1)

            (find_size_min_label:=Label(find_size_frame,text='min: ',bg=self.bg_color,anchor='e',relief='flat',bd=2)).grid(row=0, column=0, sticky='we',padx=4,pady=4)
            (find_size_max_label:=Label(find_size_frame,text='max: ',bg=self.bg_color,anchor='e',relief='flat',bd=2)).grid(row=0, column=2, sticky='we',padx=4,pady=4)

            def validate_size_str(val):
                return bool(val == "" or val.isdigit())

            #entry_validator = self.main.register(validate_size_str)
            #,validate="key",validatecommand=(entry_validator,"%P")
            find_size_min_entry=Entry(find_size_frame,textvariable=self.find_size_min_var)
            find_size_min_entry.grid(row=0, column=1, sticky='we',padx=4,pady=4)
            find_size_max_entry=Entry(find_size_frame,textvariable=self.find_size_max_var)
            find_size_max_entry.grid(row=0, column=3, sticky='we',padx=4,pady=4)

            find_size_min_entry.bind("<KeyRelease>", self.find_mod_keypress)
            find_size_max_entry.bind("<KeyRelease>", self.find_mod_keypress)

            size_tooltip = 'Integer value [in bytes] or integer with unit.\nLeave the value blank to ignore this criterion.\n\nexamples:\n399\n100B\n125kB\n10MB'
            self.widget_tooltip(find_size_min_entry,size_tooltip)
            self.widget_tooltip(find_size_min_label,size_tooltip)
            self.widget_tooltip(find_size_max_entry,size_tooltip)
            self.widget_tooltip(find_size_max_label,size_tooltip)

            (find_modtime_frame := LabelFrame(sfdma,text='File last modification time',bd=2,bg=self.bg_color,takefocus=False)).grid(row=4,column=0,sticky='news',padx=4,pady=4)
            find_modtime_frame.grid_columnconfigure((0,1,2,3), weight=1)

            (find_modtime_min_label:=Label(find_modtime_frame,text='min: ',bg=self.bg_color,anchor='e',relief='flat',bd=2)).grid(row=0, column=0, sticky='we',padx=4,pady=4)
            (find_modtime_max_label:=Label(find_modtime_frame,text='max: ',bg=self.bg_color,anchor='e',relief='flat',bd=2)).grid(row=0, column=2, sticky='we',padx=4,pady=4)

            find_modtime_min_entry=Entry(find_modtime_frame,textvariable=self.find_modtime_min_var)
            find_modtime_min_entry.grid(row=0, column=1, sticky='we',padx=4,pady=4)
            find_modtime_max_entry=Entry(find_modtime_frame,textvariable=self.find_modtime_max_var)
            find_modtime_max_entry.grid(row=0, column=3, sticky='we',padx=4,pady=4)

            find_modtime_min_entry.bind("<KeyRelease>", self.find_mod_keypress)
            find_modtime_max_entry.bind("<KeyRelease>", self.find_mod_keypress)

            time_toltip = 'Date and time in the format below.\nLeave the value blank to ignore this criterion.\n\nexamples:\n2023-12-14 22:21:20\n2023-12-14 22:21\n2023-12-14\n2023-12'
            self.widget_tooltip(find_modtime_min_entry,time_toltip)
            self.widget_tooltip(find_modtime_min_label,time_toltip)
            self.widget_tooltip(find_modtime_max_entry,time_toltip)
            self.widget_tooltip(find_modtime_max_label,time_toltip)

            self.search_butt = Button(self.find_dialog.area_buttons, text='Search', width=14, command=self.find_items )
            self.search_butt.pack(side='left', anchor='n',padx=5,pady=5)
            self.search_show_butt = Button(self.find_dialog.area_buttons, text='Show results', width=14, command=self.find_show_results, state='disabled' )
            self.search_show_butt.pack(side='left', anchor='n',padx=5,pady=5)
            self.search_save_butt = Button(self.find_dialog.area_buttons, text='Save results', width=14, command=self.find_save_results, state='disabled' )
            self.search_save_butt.pack(side='left', anchor='n',padx=5,pady=5)

            Button(self.find_dialog.area_buttons, text='Close', width=14, command=self.find_close ).pack(side='right', anchor='n',padx=5,pady=5)

            sfdma.grid_rowconfigure(5, weight=1)
            sfdma.grid_columnconfigure(0, weight=1)

            self.info_dialog_on_find = LabelDialog(self.find_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget : self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))
            self.text_dialog_on_find = TextDialogInfo(self.find_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))

            self.fix_text_dialog(self.text_dialog_on_find)

            self.results_on_find = LabelDialogQuestion(self.find_dialog.widget,self.main_icon_tuple,self.bg_color,pre_show=lambda new_widget : self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))

            self.results_on_find.cancel_button.configure(text='Continue search',width=20)
            self.results_on_find.ok_button.configure(text='Close Search dialog',width=20)

            self.find_dialog_created = True

        return self.find_dialog

    about_dialog_created = False
    @restore_status_line
    @block
    def get_about_dialog(self):
        if not self.about_dialog_created:
            self.status("Creating dialog ...")

            self.aboout_dialog=GenericDialog(self.main,self.main_icon_tuple,self.bg_color,'',pre_show=self.pre_show,post_close=self.post_close)

            frame1 = LabelFrame(self.aboout_dialog.area_main,text='',bd=2,bg=self.bg_color,takefocus=False)
            frame1.grid(row=0,column=0,sticky='news',padx=4,pady=(4,2))
            self.aboout_dialog.area_main.grid_rowconfigure(1, weight=1)

            text= f'\n\nLibrer {VER_TIMESTAMP}\nAuthor: Piotr Jochymek\n\n{HOMEPAGE}\n\nPJ.soft.dev.x@gmail.com\n\n'

            Label(frame1,text=text,bg=self.bg_color,justify='center').pack(expand=1,fill='both')

            frame2 = LabelFrame(self.aboout_dialog.area_main,text='',bd=2,bg=self.bg_color,takefocus=False)
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

        return self.aboout_dialog

    license_dialog_created = False
    @restore_status_line
    @block
    def get_license_dialog(self):
        if not self.license_dialog_created:
            self.status("Creating dialog ...")

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

            self.get_entry_ask_dialog().show('Alias record name',f"New alias name for record '{self.current_record.header.label}' {alias_info} :",alias_init)

            if self.entry_ask_dialog.res_bool:
                alias = self.entry_ask_dialog.entry_val.get()
                if alias:
                    res2=librer_core.alias_record_name(self.current_record,alias)
                    #item = self.record_to_item[self.current_record]
                    self.tree.item(item,text=alias)
        elif self.current_group and is_group:
            self.get_entry_ask_dialog().show('Rename group',f"Group '{self.current_group}' rename :",self.current_group)

            if self.entry_ask_dialog.res_bool:
                rename = self.entry_ask_dialog.entry_val.get()
                if rename:
                    res2=librer_core.rename_group(self.current_group,rename)
                    if res2:
                        self.info_dialog_on_main.show('Rename failed.',res2)
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

            #librer_core.get_record_name(record)
            self.repack_label_var.set(self.current_record.header.label + "(" + librer_core.get_record_name(self.current_record) + ")")
            self.repack_compr_var.set(self.current_record.header.compression_level)
            self.repack_compr_var_int.set(self.current_record.header.compression_level)

            self.repack_cd_cb.configure(state='normal' if self.current_record.header.items_cd else 'disabled')
            self.repack_cd_var.set(True if self.current_record.header.items_cd else False)

            dialog.show()

            if self.repack_dialog_do_it:
                if messages := librer_core.repack_record(self.current_record,self.repack_label_var.get(),self.repack_compr_var.get(),self.repack_cd_var.get(),self.single_record_show,group):
                    self.info_dialog_on_main.show('Repacking failed','\n'.join(messages) )
                else:
                    self.find_clear()
                    self.info_dialog_on_main.show('Repacking finished.','Check repacked record\nDelete original record manually if you want.')

    def wii_import_to_local(self):
        self.wii_import_dialog_do_it=True
        self.wii_import_dialog.hide()

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

        if import_filenames := askopenfilenames(initialdir=self.last_dir,parent = self.main,title='Choose "Where Is It?" Report xml files to import' + postfix, defaultextension=".xml",filetypes=[("XML Files","*.xml"),("All Files","*.*")]):
            self.status('Parsing WII files ... ')
            self.main.update()

            self.last_dir = dirname(import_filenames[0])
            wiis_res = librer_core.import_records_wii_scan(import_filenames)

            if len(wiis_res)!=11:
                self.info_dialog_on_main.show('Where Is It? Import failed',f"Format error.\n{wiis_res[1]}")
                return

            quant_disks,quant_files,quant_folders,filenames_set,filenames_set_per_disk,wii_path_tuple_to_data,wii_path_tuple_to_data_per_disk,wii_paths_dict,wii_paths_dict_per_disk,cd_set,cd_set_per_disk = wiis_res

            if quant_disks==0 or (quant_files==0 and quant_folders==0):
                self.info_dialog_on_main.show('Where Is It? Import failed',"No files / No folders")
            else:
                ###########################
                dialog = self.get_wii_import_dialog()

                if len(import_filenames)>1:
                    self.wii_import_label_var.set(f'WII-imported-multiple-files')
                else:
                    self.wii_import_label_var.set(f'WII-imported-{Path(import_filenames[0]).stem}')

                self.wii_import_brief_label.configure(text=f'GATHERED DATA:\ndisks   : {fnumber(quant_disks)}\nfiles   : {fnumber(quant_files)}\nfolders : {fnumber(quant_folders)}')

                dialog.show()

                compr = self.wii_import_compr_var.get()

                if self.wii_import_dialog_do_it:
                    postfix=0

                    if self.wii_import_separate.get():
                        res= []
                        #wii_path_tuple_to_data_per_disk[(disk_name,tuple(filenames_set_sd)][tuple(path_splitted)] = sld_tuple

                        for disk_name,wii_path_tuple_to_data_curr in wii_path_tuple_to_data_per_disk.items():
                            print(f'{disk_name=}')
                            self.status(f'importing {disk_name} ... ')
                            #sld_tuple = sub_dict[path_splitted_tuple]
                            quant_files=3
                            quant_folders=3

                            label = disk_name
                            sub_res = librer_core.import_records_wii_do(compr,postfix,label,quant_files,quant_folders,filenames_set_per_disk[disk_name],wii_path_tuple_to_data_curr,wii_paths_dict_per_disk[disk_name],cd_set_per_disk[disk_name],self.single_record_show,group)
                            postfix+=1
                            if sub_res:
                                res.append(sub_res)

                        if not res:
                            ###########################
                            self.info_dialog_on_main.show('Where Is It? Import','Successful.')
                            self.find_clear()
                        else:
                            self.info_dialog_on_main.show('Where Is It? Import failed','\n'.join(res))

                    else:
                        label = self.wii_import_label_var.get()
                        self.status(f'importing {label} ... ')

                        res = librer_core.import_records_wii_do(compr,postfix,label,quant_files,quant_folders,filenames_set,wii_path_tuple_to_data,wii_paths_dict,cd_set,self.single_record_show,group)

                        if not res:
                            ###########################
                            self.info_dialog_on_main.show('Where Is It? Import','Successful.')
                            self.find_clear()
                        else:
                            self.info_dialog_on_main.show('Where Is It? Import failed',res)

                self.column_sort(self.tree)

    @restore_status_line
    @block
    def record_import(self):
        initialdir = self.last_dir if self.last_dir else self.cwd

        group = None
        if self.current_group:
            group = self.current_group
        elif self.current_record :
            if group_temp:=librer_core.get_record_group(self.current_record):
                group = group_temp

        postfix = f' to group:{group}' if group else ''

        if import_filenames := askopenfilenames(initialdir=self.last_dir,parent = self.main,title='Choose record files to import' + postfix, defaultextension=".dat",filetypes=[("Dat Files","*.dat"),("All Files","*.*")]):
            self.last_dir = dirname(import_filenames[0])
            if import_res := librer_core.import_records(import_filenames,self.single_record_show,group):
                self.info_dialog_on_main.show('Import failed',import_res)
            else:
                self.info_dialog_on_main.show('Import','Successful.')
                self.find_clear()

                self.column_sort(self.tree)

    @restore_status_line
    @block
    def record_export(self):
        if self.current_record:
            if export_file_path := asksaveasfilename(initialdir=self.last_dir,parent = self.main, initialfile = 'record.dat',defaultextension=".dat",filetypes=[("Dat Files","*.dat"),("All Files","*.*")]):
                self.last_dir = dirname(export_file_path)

                if export_res := librer_core.export_record(self.current_record,export_file_path):
                    self.info_dialog_on_main.show('Export failed',export_res)
                else:
                    self.info_dialog_on_main.show('Export','Successful.')

    def focusin(self):
        #print('focusin')
        if self.main_locked_by_child:
            self.main_locked_by_child.focus_set()

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
                            self.tooltip_lab_configure(text=librer_core.record_info_alias_wrapper(record,record.txtinfo_basic + '\n\n(Double click to show full record info)') )
                        else:
                            scan_path = record.header.scan_path
                            subpath = sep + sep.join(subpath_list)

                            tooltip_list = [f'scan path : {scan_path}']
                            tooltip_list.append(f'subpath   : {subpath}')

                            if item in self.item_to_data:
                                data_tuple = self.item_to_data[item]
                                code = data_tuple[1]
                                is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,cd_aborted,cd_empty,aux2 = LUT_decode[code]

                                if is_symlink:
                                    tooltip_list.append('')
                                    tooltip_list.append('Symlink')

                                if is_bind:
                                    tooltip_list.append('')
                                    tooltip_list.append('Binding (another device)')

                                if has_cd:
                                    tooltip_list.append('')
                                    tooltip_list.append('(Double click to show Custom Data.)')

                            self.tooltip_lab_configure(text='\n'.join(tooltip_list))

                        self.tooltip_deiconify_wrapp()
                    else:
                        self.tooltip_lab_configure(text='label')

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
                norm("File")
                #norm("Navigation")
                norm("Help")
        except Exception as e:
            l_error(e)

    def menu_disable(self):
        disable = self.menubar_disable

        self.menu_state_stack_append('x')
        disable("File")
        disable("Help")
        #self.menubar.update()

    def reset_sels(self):
        self.sel_path = None
        self.sel_item = None

        #self.sel_kind = None

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
        dialog.show('Settings')

        self.tree_semi_focus()

    @block
    def finder_wrapper_show(self):
        #if self.current_record:
        if librer_core.records:
            dialog = self.get_find_dialog()

            self.find_dialog_shown=True
            self.find_mod()
            self.searching_aborted = False

            dialog.show('Find')
            self.find_dialog_shown=False

            self.tree_semi_focus()

    def find_close(self):
        self.find_dialog.hide()

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
                self_tree_item(item,tags=tags)

            _ = {nodes_set_add(child) for child in self_tree_get_children(item)}

        self.status_find_tooltip(self.status_find_tooltip_default)

        self.any_valid_find_results = False
        self.external_find_params_change=True

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
        if report_file_name := asksaveasfilename(parent = self.find_dialog.widget, initialfile = 'librer_search_report.txt',defaultextension=".txt",filetypes=[("All Files","*.*"),("Text Files","*.txt")]):
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
        rest_txt_list = ['# ' + line for line in self.search_info_lines]
        rest_txt_list.append('')

        for record in librer_core.records:
            if record.find_results:
                rest_txt_list.append(f'record:{librer_core.get_record_name(record)}')
                for res_item,res_size,res_mtime in record.find_results:
                    rest_txt_list.append(f'  {sep.join(res_item)}')

                rest_txt_list.append('')

            res_txt = '\n'.join(rest_txt_list)

        self.text_dialog_on_find.show('Search results',res_txt)

    find_result_record_index=0
    find_result_index=0

    find_dialog_shown=False

    def find_mod_keypress(self,event):
        key=event.keysym

        if key=='Return':
            self.find_items()
        else:
            self.find_mod()

    def find_mod(self):
        try:
            self.find_params_changed=self.external_find_params_change

            sel_range = self.get_selected_records()
            sel_range_info = '\n'.join([librer_core.get_record_name(rec) for rec in sel_range])

            self.widget_tooltip(self.find_range_cb1,'records:\n\n' + sel_range_info)

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
                self.search_show_butt.configure(state='disabled')
                self.search_save_butt.configure(state='disabled')
            else:
                if self.searching_aborted or not self.any_valid_find_results:
                    self.search_butt.configure(state='normal')
                else:
                    self.search_butt.configure(state='disabled')

                if self.any_valid_find_results:
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
        self.any_valid_find_results=Fale

    def get_range_name(self):
        if self.current_group:
            return f'group: {self.current_group}'
        elif self.current_record:
            return f'record: {self.current_record}'
        else:
            return ()

    def get_selected_records(self):
        if self.current_group:
            return librer_core.get_records_of_group(self.current_group)
        elif self.current_record:
            return [self.current_record]
        else:
            return ()

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
                search_info_lines_append('Search in all records')
                sel_range = librer_core.records
            else:
                sel_range = self.get_selected_records()
                #sel_range_info = '\n'.join([librer_core.get_record_name(rec) for rec in sel_range])
                sel_range_info = self.get_range_name()
                search_info_lines_append(f'Search in records:\n{sel_range_info}')

            #if self.current_record:
            #    search_info_lines_append(f'Search in record:{librer_core.get_record_name(self.current_record)}')
            #    sel_range = [self.current_record]
            #elif self.current_group:
            #    search_info_lines_append(f'Search in group:{self.current_group}')
            #    sel_range = librer_core.get_records_of_group(self.current_group)
            #else:
            #    print('imposible1')
            #    sel_range=[]

            #print(f'{sel_range=}')
            #range_par = self.current_record if not find_range_all else None

            #sel_range = [range_par] if range_par else librer_core.records
            sel_range_len = len(sel_range)
            files_search_quant = sum([record.header.quant_files+record.header.quant_folders for record in sel_range])

            if files_search_quant==0:
                self.info_dialog_on_find.show('Search aborted.','No files in records.')
                return 1

            if find_filename_search_kind == 'regexp':
                if find_name_regexp:
                    if res := test_regexp(find_name_regexp):
                        self.info_dialog_on_find.show('regular expression error',res)
                        return
                    search_info_lines_append(f'Regular expression on path element:"{find_name_regexp}"')
                else:
                    self.info_dialog_on_find.show('regular expression empty','(for path element)')
                    return
            elif find_filename_search_kind == 'glob':
                if find_name_glob:
                    info_str = f'Glob expression on path element:"{find_name_glob}"'
                    if find_name_case_sens:
                        search_info_lines_append(info_str + ' (Case sensitive)')
                    else:
                        search_info_lines_append(info_str)
                else:
                    self.info_dialog_on_find.show('empty glob expression','(for path element)')
                    return
            elif find_filename_search_kind == 'fuzzy':
                if find_name_fuzz:
                    try:
                        float(filename_fuzzy_threshold)
                    except ValueError:
                        self.info_dialog_on_find.show('fuzzy threshold error',f"wrong threshold value:{filename_fuzzy_threshold}")
                        return
                    search_info_lines_append(f'Fuzzy match on path element:"{find_name_fuzz}" (...>{filename_fuzzy_threshold})')
                else:
                    self.info_dialog_on_find.show('fuzzy expression error','empty expression')
                    return

            if find_cd_search_kind == 'without':
                search_info_lines_append(f'Files without Custom Data')
            elif find_cd_search_kind == 'any':
                search_info_lines_append(f'Files with any correct Custom Data')
            elif find_cd_search_kind == 'error':
                search_info_lines_append('Files with error on CD extraction')
            elif find_cd_search_kind == 'empty':
                search_info_lines_append('Files with empty CD value')
            elif find_cd_search_kind == 'aborted':
                search_info_lines_append('Files with aborted CD extraction')
            elif find_cd_search_kind == 'regexp':
                if find_cd_regexp:
                    if res := test_regexp(find_cd_regexp):
                        self.info_dialog_on_find.show('regular expression error',res)
                        return
                    search_info_lines_append(f'Regular expression on Custom Data:"{find_cd_regexp}"')
                else:
                    self.info_dialog_on_find.show('regular expression empty','(for Custom Data)')
                    return
            elif find_cd_search_kind == 'glob':
                if find_cd_glob:
                    info_str = f'Glob expression on Custom Data:"{find_cd_glob}"'
                    if find_cd_case_sens:
                        search_info_lines_append(info_str + ' (Case sensitive)')
                    else:
                        search_info_lines_append(info_str)
                else:
                    self.info_dialog_on_find.show('empty glob expression','(for Custom Data)')
                    return
            elif find_cd_search_kind == 'fuzzy':
                if find_cd_fuzz:
                    try:
                        float(cd_fuzzy_threshold)
                    except ValueError:
                        self.info_dialog_on_find.show('fuzzy threshold error',f"wrong threshold value:{cd_fuzzy_threshold}")
                        return
                    search_info_lines_append(f'Fuzzy match on Custom Data:"{find_cd_fuzz}" (...>{cd_fuzzy_threshold})')

                else:
                    self.info_dialog_on_find.show('fuzzy expression error','empty expression')
                    return

            if find_size_min:
                min_num = str_to_bytes(find_size_min)
                if min_num == -1:
                    self.info_dialog_on_find.show('min size value error',f'fix "{find_size_min}"')
                    return
                search_info_lines_append(f'Min size:{find_size_min}')
            else:
                min_num = ''

            if find_size_max:
                max_num = str_to_bytes(find_size_max)
                if max_num == -1:
                    self.info_dialog_on_find.show('max size value error',f'fix "{find_size_max}"')
                    return
                search_info_lines_append(f'Max size:{find_size_max}')
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
                search_info_lines_append(f'Min modtime:{find_modtime_min}')
            t_max=None
            if find_modtime_max:
                try:
                    t_max = int(mktime(parse_datetime(find_modtime_max).timetuple()))
                except Exception as te:
                    self.info_dialog_on_find.show('file modification time max error ',f'{find_modtime_max}\n{te}')
                    return
                search_info_lines_append(f'Max modtime:{find_modtime_max}')

            self.cfg.set(CFG_KEY_find_range_all,find_range_all)
            self.cfg.set(CFG_KEY_find_cd_search_kind,find_cd_search_kind)
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

            #gc_disable()
            #gc_collect()

            #search_thread=Thread(target=lambda : librer_core.find_items_in_records(self.temp_dir,range_par,
            search_thread=Thread(target=lambda : librer_core.find_items_in_records(self.temp_dir,sel_range,
                min_num,max_num,
                t_min,t_max,
                find_filename_search_kind,find_name,find_name_case_sens,
                find_cd_search_kind,find_cd,find_cd_case_sens,
                filename_fuzzy_threshold,cd_fuzzy_threshold),daemon=True)
            search_thread.start()

            search_thread_is_alive = search_thread.is_alive

            wait_var=BooleanVar()
            wait_var.set(False)

            self_hg_ico = self.hg_ico

            #############################

            self_progress_dialog_on_find.lab_l1.configure(text='Records:')
            self_progress_dialog_on_find.lab_l2.configure(text='Files:' )
            self_progress_dialog_on_find.lab_r1.configure(text='--')
            self_progress_dialog_on_find.lab_r2.configure(text='--' )
            self_progress_dialog_on_find.show('Search progress')

            records_len = len(librer_core.records)
            if records_len==0:
                self.info_dialog_on_find.show('Search aborted.','No records.')
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
                change3 = self_progress_dialog_on_find_update_lab_text(3,f'Found Files: {fnumber(librer_core.find_res_quant)}' )

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

            find_results_quant_sum = 0

            colname,sort_index,is_numeric,reverse,dir_code,non_dir_code = self.column_sort_last_params
            #print('\npre sort info colname:',colname,'is_numeric',is_numeric,'reverse:',reverse)
            colname_real = self.REAL_SORT_COLUMN[colname]
            #print('colname_real:',colname_real)

            for record in librer_core.records:
                find_results_quant_sum += len(record.find_results)

                record.find_items_sort(colname_real,reverse)
                #print(record.find_result)

            self.any_valid_find_results=bool(find_results_quant_sum>0)

            abort_info = '\nSearching aborted. Resuls may be incomplete.' if self.action_abort else ''

            self.all_records_find_results_len = find_results_quant_sum
            find_results_quant_sum_format = fnumber(find_results_quant_sum)

            self.set_found()

            if self.action_abort:
                self.searching_aborted = True
            else:
                self.searching_aborted = False

            self.find_mod()

            search_info = '\n'.join(self.search_info_lines)
            self.results_on_find.show('Search results',f"{search_info}\n\nfound: {find_results_quant_sum_format} items.\n\nNavigate search results by\n\'Find next (F3)\' & 'Find prev (Shift+F3)'\nactions." + abort_info)
            self.status_find_tooltip(f"available search results: {find_results_quant_sum_format}")

            if not self.searching_aborted and self.any_valid_find_results:
                self.search_show_butt.configure(state='normal')
                self.search_save_butt.configure(state='normal')

                self.search_butt.configure(state='disabled')

                self.external_find_params_change=False
            if self.results_on_find.res_bool:
                self.find_dialog.hide()

                if find_results_quant_sum_format:
                    self.find_result_index=-1
                    self.find_next()
        else:
            self.info_dialog_on_find.show('Search aborted.','Same params')

    def get_child_of_name(self,record,item,child_name):
        self_tree = self.tree
        self_tree_item = self_tree.item

        self_item_to_data = self.item_to_data
        record_filenames = record.filenames

        #mozna by to zcachowac ale jest kwestia sortowania
        for child in self_tree.get_children(item):
            if record_filenames[self_item_to_data[child][0]]==child_name:
                return child
        return None

    @block
    def select_find_result(self,mod):
        status_to_set=None
        self_tree = self.tree
        if self.any_valid_find_results:
            settled = False

            records_quant = len(librer_core.records_sorted)
            find_result_index_reset=False

            while not settled:
                record = librer_core.records_sorted[self.find_result_record_index]
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
                    status_to_set=f'record find result: {fnumber(self.find_result_index+1 if self.find_result_index>=0 else record_find_results_len+self.find_result_index+1)} / {fnumber(record_find_results_len)} / {fnumber(self.all_records_find_results_len)}'

            record_item = self.record_to_item[record]

            current_item = record_item

            self.open_item(current_item)

            self_get_child_of_name = self.get_child_of_name
            self_open_item = self.open_item
            self_tree_update = self_tree.update

            for item_name in items_names_tuple:
                child_item = self_get_child_of_name(record,current_item,item_name)

                if child_item:
                    current_item = child_item
                    self_open_item(current_item)
                    #self_tree.see(current_item)
                    self_tree_update()
                else:
                    self.info_dialog_on_main.show('cannot find item:',item_name)
                    break

            self.tree.see(current_item)
            self.tree.update()

            self_tree.focus(current_item)

            self.tree_semi_focus()

            self.tree_sel_change(current_item,change_status_line=False)

            self.tree.see(current_item)
            self.tree.update()

        if status_to_set:
            self.status(status_to_set)

    KEY_DIRECTION={}
    KEY_DIRECTION['Prior']=-1
    KEY_DIRECTION['Next']=1
    KEY_DIRECTION['Home']=0
    KEY_DIRECTION['End']=-1

    @block
    def goto_next_prev_record(self,direction):
        #status ='selecting next record' if direction==1 else 'selecting prev record'

        tree=self.tree
        current_item=self.sel_item

        item=tree.focus()
        if item:
            record_item,record_name,subpath_list = self.get_item_record(item)

            item_to_sel = tree.next(record_item) if direction==1 else tree.prev(record_item)

            #if children := self.tree_get_children():
                #if next_item:=children[index]:
                #    self.select_and_focus(next_item)
            #    pass
            if item_to_sel:
                self.select_and_focus(item_to_sel)

    @block
    def goto_first_last_record(self,index):
        #print('goto_first_last_record',index)
        if children := self.tree_get_children():
            if next_item:=children[index]:
                self.select_and_focus(next_item)

    current_record=None
    current_group=None

    def tree_select(self):
        #self.find_clear()

        item=self.tree.focus()
        self.sel_item = item
        parent = self.tree.parent(item)

        self.current_group = None

        if item:
            if self.tree.tag_has(self.GROUP,item):
                values = self.tree.item(item,'values')
                if values:
                    self.current_group=values[0]

                self.status_record_configure('---')
                self.current_record=None
            else:
                record_item,record_name,subpath_list = self.get_item_record(item)
                if record_item in self.item_to_record:
                    record = self.item_to_record[record_item]
                    #if not record:
                    #    if not self.cfg.get(CFG_KEY_find_range_all):
                    #        self.external_find_params_change = True

                    if record != self.current_record:
                        self.current_record = record
                        if not self.cfg.get(CFG_KEY_find_range_all):
                            self.external_find_params_change = True

                    record_name = self.tree.item(record_item,'text')
                    image=self.tree.item(record_item,'image')

                    self.status_record.configure(image = image, text = record_name,compound='left')
                    self.widget_tooltip(self.status_record,librer_core.record_info_alias_wrapper(record,record.txtinfo_basic + '\n\n(Click to show full record info)') )
                    #\nsingle click to unload data of current record.\n
                else:
                    self.status_record.configure(image = '', text = '')
                    self.widget_tooltip(self.status_record,'')
                    self.current_record = None
                    self.status_record_configure('---')
        else:
            self.current_record = None
            self.current_group = None
            self.status_record_configure('---')

    def key_press(self,event):
        #print('key_press',event.keysym)

        if not self.block_processing_stack:
            self.hide_tooltip()
            self.menubar_unpost()
            self.popup_unpost()

            try:
                tree=event.widget
                item=tree.focus()
                key=event.keysym

                if key in ("Prior","Next"):
                    self.goto_next_prev_record(self.KEY_DIRECTION[key])
                elif key in ("Home","End"):
                    self.goto_first_last_record(self.KEY_DIRECTION[key])
                else:
                    event_str=str(event)

                    alt_pressed = ('0x20000' in event_str) if windows else ('Mod1' in event_str or 'Mod5' in event_str)
                    ctrl_pressed = 'Control' in event_str
                    shift_pressed = 'Shift' in event_str

            except Exception as e:
                l_error(e)
                self.info_dialog_on_main.show('INTERNAL ERROR',str(e))

#################################################
    def select_and_focus(self,item):
        self.tree_see(item)
        self.tree_focus(item)

        self.tree.update()

        self.tree_sel_change(item)

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
                    tree.selection_remove(tree.selection())

                    tree.focus(item)
                    self.tree_semi_focus()

                    self.tree_sel_change(item)
        else:
            return "break"

    sel_item = None
    def tree_semi_focus(self):
        tree = self.tree

        item=None

        if sel:=tree.selection():
            item=sel[0]

        if not item:
            item=tree.focus()

        if not item:
            try:
                item = tree.get_children()[0]
            except :
                pass

        if item:
            tree.focus_set()
            tree.see(item)

            self.tree_sel_change(item)
            self.sel_item = item
        else:
            self.sel_item = None

    @catched
    def tree_sel_change(self,item,change_status_line=True):
        self.sel_item = item

        if change_status_line :
            self.status('')

        self_tree_set_item=lambda x : self.tree_set(item,x)

        self.tree_select()

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

            item_actions_state=('disabled','normal')[self.sel_item is not None]


            item=self.tree.focus()

            is_group = bool(self.tree.tag_has(self.GROUP,item))
            is_record = bool(self.tree.tag_has(self.RECORD_RAW,item) or self.tree.tag_has(self.RECORD,item))

            record_in_group = False
            if is_record:
                if librer_core.get_record_group(self.current_record):
                    record_in_group = True

            there_are_groups = bool(librer_core.groups)

            pop=self.popup

            pop.delete(0,'end')

            pop_add_separator = pop.add_separator
            pop_add_cascade = pop.add_cascade
            pop_add_command = pop.add_command
            self_ico = self.ico
            #state_on_records = 'normal' if librer_core.records else 'disabled'
            state_on_records = 'normal' if is_record else 'disabled'

            state_on_records_or_groups = 'normal' if is_record or is_group else 'disabled'

            c_nav = Menu(self.menubar,tearoff=0,bg=self.bg_color)
            c_nav_add_command = c_nav.add_command
            c_nav_add_separator = c_nav.add_separator

            c_nav_add_command(label = 'Go to next record'       ,command = lambda : self.goto_next_prev_record(1),accelerator="Pg Down",state='normal', image = self.ico_empty,compound='left')
            c_nav_add_command(label = 'Go to previous record'   ,command = lambda : self.goto_next_prev_record(-1), accelerator="Pg Up",state='normal', image = self.ico_empty,compound='left')
            c_nav_add_separator()
            c_nav_add_command(label = 'Go to first record'       ,command = lambda : self.goto_first_last_record(0),accelerator="Home",state='normal', image = self.ico_empty,compound='left')
            c_nav_add_command(label = 'Go to last record'   ,command = lambda : self.goto_first_last_record(-1), accelerator="End",state='normal', image = self.ico_empty,compound='left')

            pop_add_command(label = 'New record ...',  command = self.scan_dialog_show,accelerator='Ctrl+N',image = self.ico_record_new,compound='left')
            pop_add_separator()
            pop_add_command(label = 'Export record ...', accelerator='Ctrl+E', command = self.record_export,image = self.ico_record_export,compound='left',state=state_on_records)
            pop_add_command(label = 'Import record ...', accelerator='Ctrl+I', command = self.record_import,image = self.ico_record_import,compound='left')
            pop_add_command(label = 'Rename / Repack ...',accelerator="F5" , command = self.record_repack,image = self.ico_empty,compound='left',state=state_on_records)
            pop_add_command(label = 'Record Info ...', accelerator='Alt+Enter', command = self.record_info,image = self.ico_info,compound='left',state=state_on_records)
            pop_add_command(label = 'Delete record ...',accelerator="Delete, F8",command = self.delete_action,image = self.ico_record_delete,compound='left',state=state_on_records)
            pop_add_separator()
            pop_add_command(label = 'New group ...',accelerator="F7",  command = self.new_group,image = self.ico_group_new,compound='left')
            pop_add_command(label = 'Remove group ...',accelerator="Delete" ,  command = self.remove_group,image = self.ico_group_remove,compound='left',state=('disabled','normal')[is_group] )
            pop_add_command(label = 'Assign record to group ...',accelerator="F6" ,  command = self.assign_to_group,image = self.ico_group_assign,compound='left',state=('disabled','normal')[is_record and there_are_groups] )
            pop_add_command(label = 'Remove record from group ...',  command = self.remove_from_group,image = self.ico_empty,compound='left',state=('disabled','normal')[record_in_group])
            pop_add_separator()
            pop_add_command(label = 'Rename / Alias name ...', accelerator='F2', command = self.alias_name,image = self.ico_empty,compound='left',state=state_on_records_or_groups )
            pop_add_separator()
            pop_add_command(label = 'Show Custom Data ...', accelerator='Enter', command = self.show_customdata,image = self.ico_empty,compound='left',state=('disabled','normal')[self.item_has_cd(self.tree.focus())])
            pop_add_separator()
            pop_add_command(label = 'Copy full path',command = self.clip_copy_full_path_with_file,accelerator='Ctrl+C',state = 'normal' if self.sel_item is not None and self.current_record else 'disabled', image = self.ico_empty,compound='left')
            pop_add_separator()

            #can_search = bool(self.sel_item is not None and self.current_record)
            can_search = bool(librer_core.records)
            search_state = 'normal' if can_search else 'disabled'

            pop_add_command(label = 'Find ...',accelerator="Ctrl+F" ,command = self.finder_wrapper_show,state = search_state, image = self.ico_find,compound='left')
            pop_add_command(label = 'Find next',command = self.find_next,accelerator="F3",state = search_state, image = self.ico_empty,compound='left')
            pop_add_command(label = 'Find prev',command = self.find_prev,accelerator="Shift+F3",state = search_state, image = self.ico_empty,compound='left')
            pop_add_separator()
            pop_add_command(label = 'Clear Search Results',command = self.find_clear, image = self.ico_empty,compound='left',state = 'normal' if self.any_valid_find_results else 'disabled')
            pop_add_separator()

            pop_add_command(label = 'Exit',  command = self.exit ,image = self.ico['exit'],compound='left')

            try:
                pop.tk_popup(event.x_root, event.y_root)
            except Exception as e:
                print(e)

            pop.grab_release()

    def new_group(self):
        self.get_entry_ask_dialog().show('New group','New group name:')

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
            dialog.show('Delete selected group ?', 'group: ' + group + '\n\n(Records assigned to group will remain untouched)')

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
                self.tree.focus(tree.get_children()[0])
                self.tree_semi_focus()

                self.find_clear()

    def remove_from_group(self):
        record = self.current_record

        res = librer_core.remove_record_from_group(record)
        if res :
            self.info_dialog_on_main.show('Error',res)
        else:
            record_item = self.record_to_item[record]
            self.tree.move(record_item,'',0)

            self.find_clear()

            self.column_sort(self.tree)

    last_assign_to_group_group = None
    @logwrapper
    def assign_to_group(self):
        #item=self.tree.focus()

        #is_group = bool(self.tree.tag_has(self.GROUP,item))
        #is_record = bool(self.tree.tag_has(self.RECORD_RAW,item) or self.tree.tag_has(self.RECORD,item))

        if self.current_record:
            curr_group = librer_core.get_record_group(self.current_record)

            dial = self.get_assign_to_group_dialog()

            values = list(librer_core.groups.keys())
            dial.combobox.configure(values=values)
            record = self.current_record
            current = librer_core.get_record_group(record)

            if not current:
                if self.last_assign_to_group_group in values:
                    current = self.last_assign_to_group_group
                else:
                    current = values[0]

            dial.show('Assign to group','Assign record to group:',current)

            if dial.res_bool:
                group = dial.entry_val.get()

                if group:
                    self.last_assign_to_group_group = group
                    res2=librer_core.assign_new_group(record,group)
                    if res2:
                        self.info_dialog_on_main.show('assign_new_group Error',res2)
                    else:
                        group_item = self.group_to_item[group]
                        record_item = self.record_to_item[record]
                        self.tree.move(record_item,group_item,0)
                        #self.tree.open(group_item)
                        self.open_item(group_item)
                        self.tree.focus(record_item)
                        self.tree.see(record_item)
                        self.tree.update()

                        self.find_clear()

                        self.column_sort(self.tree)

    @logwrapper
    def column_sort_click(self, tree, colname):
        prev_colname,prev_sort_index,prev_is_numeric,prev_reverse,prev_dir_code,prev_non_dir_code=self.column_sort_last_params
        reverse = not prev_reverse if colname == prev_colname else prev_reverse
        tree.heading(prev_colname, text=self.org_label[prev_colname])

        dir_code,non_dir_code = (1,0) if reverse else (0,1)

        sort_index=self.REAL_SORT_COLUMN_INDEX[colname]
        is_numeric=self.REAL_SORT_COLUMN_IS_NUMERIC[colname]
        self.column_sort_last_params=(colname,sort_index,is_numeric,reverse,dir_code,non_dir_code)
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

        colname,sort_index,is_numeric,reverse,dir_code,non_dir_code = self.column_sort_last_params

        real_column_to_sort=self.REAL_SORT_COLUMN[colname]

        tlist=[]
        tree_set = tree.set
        tlist_append = tlist.append

        dir_or_dirlink = (self.DIR,self.DIRLINK)

        children = tree.get_children(parent_item)

        #dont sort single item and dummy item
        #if len(children)>1:
        for item in children:
            values = tree.item(item,'values')

            if not values: #dummy node
                continue

            sortval_org = values[self.REAL_SORT_COLUMN_INDEX[colname]]

            sortval=(int(sortval_org) if sortval_org.isdigit() else 0) if is_numeric else sortval_org

            kind = tree_set(item,'kind')

            code= dir_code if kind in dir_or_dirlink else non_dir_code
            tlist_append( ( (code,sortval),item) )

        tlist.sort(reverse=reverse,key=lambda x: x[0])

        if not parent_item:
            parent_item=''

        tree_move = tree.move
        _ = {tree_move(item_temp, parent_item, index) for index,(val_tuple,item_temp) in enumerate(sorted(tlist,reverse=reverse,key=lambda x: x[0]) ) }
        _ = {self.tree_sort_item(item_temp) for (val_tuple,item_temp) in tlist }

    @restore_status_line
    @block
    @logwrapper
    def column_sort(self, tree):
        self.status('Sorting...')
        colname,sort_index,is_numeric,reverse,dir_code,non_dir_code = self.column_sort_last_params

        self.column_sort_set_arrow(tree)
        self.tree_sort_item(None)

        tree.update()

    def column_sort_set_arrow(self, tree):
        colname,sort_index,is_numeric,reverse,dir_code,non_dir_code = self.column_sort_last_params
        tree.heading(colname, text=self.org_label[colname] + ' ' + str('\u25BC' if reverse else '\u25B2') )

    def path_to_scan_set(self,path):
        print('path_to_scan_set',path)

    scanning_in_progress=False
    def scan_wrapper(self):
        gc_disable()
        gc_collect()

        group = self.scan_dialog_group

        if self.scanning_in_progress:
            l_warning('scan_wrapper collision')
            return

        if self.scan_label_entry_var.get()=='':
            self.scan_label_entry_var.set(platform_node() + ':' + str(abspath(self.path_to_scan_entry_var.get())) )
            #self.get_info_dialog_on_scan().show('Error. Empty label.','Set internal label.')
            #return

        self.scanning_in_progress=True

        compression_level = self.scan_compr_var_int.get()
        threads = self.scan_threads_var_int.get()

        try:
            if self.scan(compression_level,threads,group):
                self.scan_dialog_hide_wrapper()
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
        self.tree_semi_focus()

    @restore_status_line
    @logwrapper
    def scan(self,compression_level,threads,group=None):
        path_to_scan_from_entry = abspath(self.path_to_scan_entry_var.get())

        if not path_to_scan_from_entry:
            self.get_info_dialog_on_scan().show('Error. No paths to scan.','Add paths to scan.')
            return False

        #weryfikacja
        for e in range(self.CDE_ENTRIES_MAX):
            if self.CDE_use_var_list[e].get():
                mask = self.CDE_mask_var_list[e].get().strip()
                if not mask:
                    self.get_info_dialog_on_scan().show('Wrong mask expression',f'Empty mask nr:{e+1}.')
                    return False
                exe = self.CDE_executable_var_list[e].get().strip()
                if not exe:
                    self.get_info_dialog_on_scan().show('Wrong executable',f'Empty executable nr:{e+1}.')
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
            ask_dialog.show('CDE Timeout not set','Continue without Custom Data Extractor timeout ?')

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

        self_tooltip_message[str_self_progress_dialog_on_scan_abort_button]='If you abort at this stage,\nData record will not be created.'
        self_progress_dialog_on_scan.abort_button.configure(image=self.ico_abort,text='Cancel',compound='left',width=15)

        self.scan_dialog.widget.update()

        self.action_abort=False
        self_progress_dialog_on_scan.abort_button.configure(state='normal')

        #self.log_skipped = self.log_skipped_var.get()

        self_progress_dialog_on_scan.lab_l1.configure(text='CDE Total space:')
        self_progress_dialog_on_scan.lab_l2.configure(text='CDE Files number:' )

        self_progress_dialog_on_scan_update_lab_text = self.progress_dialog_on_scan.update_lab_text
        self_progress_dialog_on_scan_update_lab_image = self_progress_dialog_on_scan.update_lab_image
        self_ico_empty = self.ico_empty

        self_progress_dialog_on_scan_update_lab_text(1,'')
        self_progress_dialog_on_scan_update_lab_image(2,self_ico_empty)
        self_progress_dialog_on_scan_update_lab_text(3,'')
        self_progress_dialog_on_scan_update_lab_text(4,'')

        self_progress_dialog_on_scan.show('Creating new data record (scanning)')

        update_once=True

        self_hg_ico = self.hg_ico

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

        try:
            with open(sep.join([self.temp_dir,SCAN_DAT_FILE]), "wb") as f:
                f.write(ZstdCompressor(level=8,threads=1).compress(dumps([new_label,path_to_scan_from_entry,check_dev,compression_level,threads,cde_list])))

            #debug
            #with open(sep.join(['./tmp1',SCAN_DAT_FILE]), "wb") as f:
            #    f.write(ZstdCompressor(level=8,threads=1).compress(dumps([new_label,path_to_scan_from_entry,check_dev,compression_level,threads,cde_list])))
        except Exception as e:
            print(e)
        else:
            gc_disable()
            gc_collect()

            creation_thread=Thread(target=lambda : librer_core.create_new_record(self.temp_dir,self.single_record_show,group),daemon=True)
            creation_thread.start()

            creation_thread_is_alive = creation_thread.is_alive

            self_hg_ico = self.hg_ico

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

            self_tooltip_message[str_self_progress_dialog_on_scan_abort_button]='If you abort at this stage,\nData record will not be created.'
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
                            self_progress_dialog_on_scan.widget.title('Creating new data record (Scanning)')
                            self_progress_dialog_on_scan.abort_single_button.pack_forget()
                            switch_done=True

                        change3 = self_progress_dialog_on_scan_update_lab_text(3,local_bytes_to_str(librer_core.stdout_sum_size) )
                        change4 = self_progress_dialog_on_scan_update_lab_text(4,'%s files' % fnumber(librer_core.stdout_quant_files) )
                    elif librer_core.stage==1: #cde stage
                        if not switch_done:
                            self_progress_dialog_on_scan.widget.title('Creating new data record (Custom Data Extraction)')
                            self_progress_dialog_on_scan.abort_single_button.pack(side='left', anchor='center',padx=5,pady=5)

                            if threads==1:
                                self_progress_dialog_on_scan.abort_single_button.configure(image=self.ico_abort,text='Abort single file',compound='left',width=15,command=lambda : self.abort_single(),state='normal')
                            else:
                                self_progress_dialog_on_scan.abort_single_button.configure(image=self.ico_abort,text='Abort single file',compound='left',width=15,state='disabled')

                            self_progress_dialog_on_scan.abort_button.configure(image=self.ico_abort,text='Abort',compound='left',width=15,state='normal')

                            self_tooltip_message[str_self_progress_dialog_on_scan_abort_button]='If you abort at this stage,\nCustom Data will be incomplete.'
                            self_tooltip_message[str_self_progress_dialog_on_scan_abort_single_button]='Use if CDE has no timeout set and seems like stuck.\nCD of only single file will be incomplete.\nCDE will continue.\n\nAvailable only for single thread mode.'
                            switch_done=True

                        change3 = self_progress_dialog_on_scan_update_lab_text(3,'Extracted Custom Data: ' + local_bytes_to_str(librer_core.stdout_cde_size_extracted) )
                        change4 = self_progress_dialog_on_scan_update_lab_text(4,'Extraction Errors : ' + fnumber(librer_core.stdout_cde_errors_quant_all) )

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

            gc_collect()
            gc_enable()

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

    def remove_record(self):
        record = self.current_record
        label = librer_core.get_record_name(record)
        path = record.header.scan_path
        creation_time = record.header.creation_time

        dialog = self.get_simple_question_dialog()

        dialog.show('Delete selected data record ?',librer_core.record_info_alias_wrapper(record,record.txtinfo_short) )

        if dialog.res_bool:
            record_item = self.record_to_item[record]
            self.tree.delete(record_item)

            del self.record_to_item[record]
            del self.item_to_record[record_item]

            res=librer_core.delete_record(record)
            l_info(f'deleted file:{res}')

            self.find_clear()
            #record.find_results_clean()

            self.status_record_configure('')
            if remaining_records := self.tree.get_children():
                if new_sel_record := remaining_records[0]:
                    self.tree.focus(new_sel_record)

                self.tree_semi_focus()
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
            dialog.widget.title(f'Create new data record in group: {group}' )
            self.scan_dialog_group = group
        else:
            dialog.widget.title('Create new data record' )
            self.scan_dialog_group = None

        self.status("Opening dialog ...")
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
                    #print('clearing settings')
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
        if res:=askdirectory(title='Select Directory',initialdir=initialdir,parent=self.scan_dialog.area_main):
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
        self.status("Abort single pressed ...")
        l_info("Abort single pressed ...")
        self.action_abort_single=True

    def kill_test(self):
        if self.subprocess and self.subprocess!=True:
            kill_subprocess(self.subprocess)

    def cde_test(self,e):
        initialdir = self.last_dir if self.last_dir else self.cwd
        if full_file_path:=askopenfilename(title='Select File',initialdir=initialdir,parent=self.scan_dialog.area_main,filetypes=( ("All Files","*.*"),("All Files","*.*") ) ):
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

            ask_dialog.show('Test Custom Data Extractor on selected file ?',info)

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
                simple_progress_dialog_scan.show('Testing selected Custom Data Extractor')

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

                self.get_text_dialog_on_scan().show(f'CDE Test finished {"OK" if self.returncode[0]==0 and not self.test_decoding_error else "with Error"}',output)

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
        if res:=askopenfilename(title='Select File',initialdir=initialdir,parent=self.scan_dialog.area_main,filetypes=(("Executable Files","*.exe"),("Bat Files","*.bat"),("All Files","*.*")) if windows else (("Bash Files","*.sh"),("All Files","*.*")) ):
            self.last_dir=dirname(res)

            expr = normpath(abspath(res))
            self.CDE_executable_var_list[e].set(expr)

    @restore_status_line
    @block
    def access_filestructure(self,record):
        self.hide_tooltip()
        self.popup_unpost()
        self.status('loading filestructure ...')
        self.main.update()
        record.decompress_filestructure()

    @restore_status_line
    @block
    def access_customdata(self,record):
        self.hide_tooltip()
        self.popup_unpost()
        self.status('loading Custom Data ...')
        self.main.update()
        record.decompress_filestructure()
        record.decompress_customdata()

        item = self.record_to_item[record]
        self.tree.item(item,image=self.ico_record_cd_loaded)
        #tags=self.RECORD

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
                colname,sort_index,is_numeric,reverse,dir_code,non_dir_code = self.column_sort_last_params
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
                    self.tree_select() #tylko dla aktualizacja ikony

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
                            tags=''
                            if entry_subpath_tuple in record_find_results_tuples_set:
                                tags=self_FOUND

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

    def get_record_raw_icon(self,record):
        return self.ico_record_raw_cd if record.has_cd() else self.ico_record_raw

    @logwrapper
    def groups_show(self):
        #('data','record','opened','path','size','size_h','ctime','ctime_h','kind')
        self.group_to_item = {}
        self.group_to_item[None]=''

        for group in librer_core.groups:
            self.single_group_show(group)

    def single_group_show(self,group):
        values = (group,group,0,'',0,'',0,'',self.GROUP)

        group_item=self.tree.insert('','end',iid=None,values=values,open=False,text=group,image=self.ico_group,tags=self.GROUP)
        self.group_to_item[group] = group_item
        self.tree.focus(group_item)
        self.tree.see(group_item)
        self.column_sort(self.tree)

    @block
    @logwrapper
    def single_record_show(self,record):
        size=record.header.sum_size

        #('data','record','opened','path','size','size_h','ctime','ctime_h','kind')
        values = (librer_core.get_record_name(record),librer_core.get_record_name(record),0,record.header.scan_path,size,bytes_to_str(size),record.header.creation_time,strftime('%Y/%m/%d %H:%M:%S',localtime_catched(record.header.creation_time)),self.RECORD)

        group = librer_core.get_record_group(record)
        group_item = self.group_to_item[group]

        record_item=self.tree.insert(group_item,'end',iid=None,values=values,open=False,text=librer_core.get_record_name(record),image=self.get_record_raw_icon(record),tags=self.RECORD_RAW)
        self.tree.insert(record_item,'end',text='dummy') #dummy_sub_item

        groups_collapse = self.cfg.get(CFG_KEY_groups_collapse)

        #print(self.cfg.get(CFG_KEY_groups_collapse),group_item)
        self.tree.item(group_item, open = False)
        #self.cfg.get(CFG_KEY_groups_collapse)

        self.tree_sort_item(None)

        self.item_to_record[record_item]=record
        self.record_to_item[record]=record_item

        if groups_collapse:
            self.tree.focus(group_item)
            self.tree.see(group_item)
        else:
            self.tree.focus(record_item)
            self.tree.see(record_item)

        records_len=len(librer_core.records)
        self.status_records_all_configure(f'Records:{records_len}')

        self.record_filename_to_record[record.file_name] = record

        sum_size=0
        quant_files=0
        for record_temp in librer_core.records:
            sum_size+=record_temp.header.sum_size
            quant_files+=record_temp.header.quant_files

        self.widget_tooltip(self.status_records_all,f'Records in repository : {records_len}\nSum data size         : {bytes_to_str(sum_size)}\nSum files quantity    : {fnumber(quant_files)}\n\nClick to unload (free memory) data of selected record\nDouble click to unload data of all records.')

        self.main_update()

        self.find_clear()

        self.column_sort(self.tree)

    def tree_update_none(self):
        self.tree.selection_remove(self.tree.selection())

    def tree_update(self,item):
        self_tree = self.tree

        self_tree.see(item)
        self_tree.update()

    folder_items=set()
    folder_items_clear=folder_items.clear
    folder_items_add=folder_items.add

    @logwrapper
    def clip_copy_full_path_with_file(self):
        item=self.tree.focus()
        if item:
            record_item,record_name,subpath_list = self.get_item_record(item)
            record = self.item_to_record[record_item]

            self.main.clipboard_clear()
            self.main.clipboard_append(normpath(sep.join([record.header.scan_path,sep.join(subpath_list)])))

            self.status('Full path copied to clipboard')

    @logwrapper
    def clip_copy(self,what):
        self.main.clipboard_clear()
        self.main.clipboard_append(what)
        self.status('Copied to clipboard: "%s"' % what)

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
                        return
                    elif self.tree.tag_has(self.RECORD,item) or self.tree.tag_has(self.RECORD_RAW,item):
                        self.record_info()
                    else:
                        #print('jedziemy')
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

                                    shell_info = ('No','Yes')[shell]
                                    timeout_info = f'\ntimeout:{timeout}' if timeout else ''
                                    self.get_text_info_dialog().show(f'Custom Data of: {file_path}',cd_txt,uplabel_text=f"{command_info}\n\nshell:{shell_info}{timeout_info}\nreturncode:{returncode}\nsize:{bytes_to_str(asizeof(cd_txt))}")
                                    return

                            self.info_dialog_on_main.show('Information','No Custom data.')

                except Exception as e:
                    self.info_dialog_on_main.show('Custom Data Info Error',str(e) + ('\n' + '\n'.join(error_infos)) if error_infos else '')

    def record_info(self):
        if not self.block_processing_stack:
            if self.current_record:
                time_info = strftime('%Y/%m/%d %H:%M:%S',localtime_catched(self.current_record.header.creation_time))
                self.get_text_info_dialog().show('Record Info',librer_core.record_info_alias_wrapper(self.current_record,self.current_record.txtinfo) )

    def purify_items_cache(self):
        self_item_to_data = self.item_to_data
        self_tree_exists = self.tree.exists
        for item in list(self_item_to_data):
            if not self_tree_exists(item):
                del self_item_to_data[item]

        #print('self_item_to_data:',len(self_item_to_data.keys()),asizeof(self_item_to_data))

    @block
    @logwrapper
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
            #self.find_clear()

            self_tree.insert(record_item,'end',text='dummy') #dummy_sub_item
            self_tree.set(record_item,'opened','0')
            self_tree.item(record_item, open=False)

            self_tree.item(record_item, image=self.get_record_raw_icon(record),tags=self.RECORD_RAW)
            self_tree.focus(record_item)
            self_tree.see(record_item)
            self.tree_select()

    @block
    @logwrapper
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

        LIBRER_EXECUTABLE_FILE = normpath(abspath(sys.executable if getattr(sys, 'frozen', False) or "__compiled__" in globals() else sys.argv[0]))
        LIBRER_EXECUTABLE_DIR = dirname(LIBRER_EXECUTABLE_FILE)
        DATA_DIR = sep.join([LIBRER_EXECUTABLE_DIR,'data'])
        LOG_DIR = sep.join([LIBRER_EXECUTABLE_DIR,'logs'])

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

        librer_core = LibrerCore(DATA_DIR,logging)

        Gui(getcwd())

    except Exception as e_main:
        print(e_main)
        l_error(e_main)
        sys.exit(1)
