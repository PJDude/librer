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

from os import sep,system,getcwd,name as os_name
from os.path import abspath,normpath,dirname
from os.path import join as path_join
from os.path import isfile as path_isfile
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
from psutil import disk_partitions,disk_usage
from librer_images import librer_image

from dialogs import *
from core import *

windows = bool(os_name=='nt')

if windows:
    from os import startfile

#l_debug = logging.debug
l_info = logging.info
l_warning = logging.warning
l_error = logging.error

###########################################################################################################################################

CFG_KEY_USE_REG_EXPR='use_reg_expr'
CFG_KEY_EXCLUDE_REGEXP='excluderegexpp'
CFG_KEY_EXCLUDE='exclude'
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

cfg_defaults={
    CFG_KEY_USE_REG_EXPR:False,
    CFG_KEY_EXCLUDE_REGEXP:False,
    CFG_KEY_SINGLE_DEVICE:True,
    CFG_KEY_EXCLUDE:'',
    CFG_KEY_CDE_SETTINGS:'',

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
    CFG_geometry:''
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
    actions_processing=False

    def __init__(self,cwd):
        self.cwd=cwd

        self.cfg = Config(DATA_DIR)
        self.cfg.read()

        self.last_dir = self.cfg.get(CFG_last_dir).replace('/',sep)

        self.cfg_get=self.cfg.get

        self.exclude_frames=[]

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
        self.ico_crc = self_ico['crc']
        self.ico_license = self_ico['license']

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

        #self.ico_delete = self_ico['delete']

        self_ico_librer = self.ico_librer = self_ico['librer']
        self.ico_librer_small = self_ico['librer_small']
        self.ico_test = self_ico['test']

        #self_main.iconphoto(True, self_ico_librer,self.ico_record)
        self_main.iconphoto(True, self_ico_librer,self.ico_librer_small)

        self.RECORD_RAW='r'
        self.RECORD='R'
        self.DIR='D'
        self.DIRLINK='L'
        self.LINK='l'
        self.FILE='F'
        self.FILELINK='l'

        self.SYMLINK='S'

        self.FOUND = 'X'

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
        bg_sel='#AAAAAA'

        style_map('Treeview', background=[('focus',bg_focus),('selected',bg_sel),('','white')])

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

        self.status_records_all=Label(status_frame,image=self.ico_record,text='--',width=200,borderwidth=2,bg=self.bg_color,relief='groove',anchor='w')
        self.status_records_all.pack(fill='x',expand=0,side='left')
        self.status_records_all_configure = lambda x : self.status_records_all.configure(image = self.ico_records_all, text = x,compound='left')
        self.widget_tooltip(self.status_records_all,'All records in repository')
        self.status_records_all.bind("<ButtonPress-1>", lambda event : self.unload_recod() )
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
        vsb1 = Scrollbar(self_main, orient='vertical', command=tree_yview,takefocus=False)

        tree.configure(yscrollcommand=vsb1.set)

        vsb1.pack(side='right',fill='y',expand=0)
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

        self.info_dialog_on_main = LabelDialog(self_main,(self.ico_librer,self.ico_librer_small),self.bg_color,pre_show=self.pre_show,post_close=self.post_close)

        #self.text_ask_dialog_on_main = TextDialogQuestion(self_main,self_ico_librer,self.bg_color,pre_show=self.pre_show,post_close=self.post_close,image=self.ico_warning)

        self.progress_dialog_on_load = ProgressDialog(self_main,(self.ico_librer,self.ico_librer_small),self.bg_color,pre_show=self.pre_show,post_close=self.post_close)
        self.progress_dialog_on_load.command_on_close = self.progress_dialog_load_abort

        self.widget_tooltip(self.progress_dialog_on_load.abort_button,'')

        #######################################################################

        def file_cascade_post():
            item_actions_state=('disabled','normal')[self.sel_item is not None]

            self.file_cascade.delete(0,'end')
            if self.actions_processing:
                self_file_cascade_add_command = self.file_cascade.add_command
                self_file_cascade_add_separator = self.file_cascade.add_separator
                state_on_records = 'normal' if librer_core.records else 'disabled'

                state_has_cd = ('disabled','normal')[self.item_has_cd(self.tree.focus())]

                item_actions_state=('disabled','normal')[self.sel_item is not None]
                self_file_cascade_add_command(label = 'New Record ...',command = self.scan_dialog_show, accelerator="Ctrl+N",image = self.ico_record_new,compound='left')

                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = 'Import record ...', accelerator='Ctrl+I', command = self.record_import,image = self.ico_record_import,compound='left')
                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = 'Find ...',command = self.finder_wrapper_show, accelerator="Ctrl+F",image = self.ico_find,compound='left',state = 'normal' if self.sel_item is not None and self.current_record else 'disabled')
                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = 'Clear Search Results',command = self.find_clear, image = self.ico_empty,compound='left',state = 'normal' if self.any_find_result else 'disabled')
                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = 'Exit',command = self.exit,image = self_ico['exit'],compound='left')

        self.file_cascade= Menu(menubar,tearoff=0,bg=self.bg_color,postcommand=file_cascade_post)
        menubar.add_cascade(label = 'File',menu = self.file_cascade,accelerator="Alt+F")

        def help_cascade_post():
            self.help_cascade.delete(0,'end')
            if self.actions_processing:

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

        #colname,sort_index,is_numeric,reverse,dir_code,non_dir_code
        self.column_sort_last_params=self.column_groups_sort_params_default=('#0',self_REAL_SORT_COLUMN_INDEX['#0'],self_REAL_SORT_COLUMN_IS_NUMERIC['#0'],0,0,1)

        #######################################################################

        self.main_update()
        try:
            cfg_geometry=self.cfg.get(CFG_geometry)

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

        self.records_show()

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
        self_progress_dialog_on_load.abort_button.configure(state='normal')

        self.status_info.configure(image='',text = 'Checking records to load ...')
        records_quant,records_size = librer_core.read_records_pre()

        load_errors = []
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

        self.actions_processing=True

        self.tree_semi_focus()
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

        self_main_bind('<KeyPress-Delete>', lambda event : self.delete_data_record())
        self_main_bind('<F3>', lambda event : self.find_next())
        self_main_bind('<Shift-F3>', lambda event : self.find_prev())

        self_main.mainloop()


    def item_has_cd(self,item):
        has_cd=False
        if item in self.item_to_data:
            data_tuple = self.item_to_data[item]
            code = data_tuple[1]

            is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc = LUT_decode[code]
        return has_cd

    def block_actions_processing(func):
        def block_actions_processing_wrapp(self,*args,**kwargs):
            prev_active=self.actions_processing
            self.actions_processing=False
            try:
                res=func(self,*args,**kwargs)
            except Exception as e:
                self.status('block_actions_processing_wrapp func:%s error:%s args:%s kwargs:%s' % (func.__name__,e,args,kwargs) )
                l_error('block_actions_processing_wrapp func:%s error:%s args:%s kwargs: %s',func.__name__,e,args,kwargs)
                l_error(''.join(format_stack()))
                self.info_dialog_on_main.show('INTERNAL ERROR block_actions_processing_wrapp',str(e))
                res=None

            self.actions_processing=prev_active

            return res
        return block_actions_processing_wrapp

    def gui_block(func):
        def gui_block_wrapp(self,*args,**kwargs):
            prev_cursor=self.menubar_cget('cursor')
            self_menubar_config = self.menubar_config
            self_main_config = self.main_config

            self.menu_disable()

            self_menubar_config(cursor='watch')
            self_main_config(cursor='watch')

            try:
                res=func(self,*args,**kwargs)
            except Exception as e:
                self.status('gui_block_wrapp func:%s error:%s args:%s kwargs:%s' % (func.__name__,e,args,kwargs) )
                l_error('gui_block_wrapp func:%s error:%s args:%s kwargs: %s',func.__name__,e,args,kwargs)
                l_error(''.join(format_stack()))
                self.info_dialog_on_main.show('INTERNAL ERROR gui_block_wrapp',func.__name__ + '\n' + str(e))
                res=None

            self.menu_enable()
            self_main_config(cursor=prev_cursor)
            self_menubar_config(cursor=prev_cursor)

            return res
        return gui_block_wrapp

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
        #self.status("Opening dialog ...")
        self.menubar_unpost()
        self.hide_tooltip()
        self.popup_unpost()

        if on_main_window_dialog:
            if new_widget:
                self.main_locked_by_child=new_widget

            self.actions_processing=False
            self.menu_disable()
            self.menubar_config(cursor="watch")

    def post_close(self,on_main_window_dialog=True):
        self.main.focus_set()

        if on_main_window_dialog:
            self.main_locked_by_child=None
            self.actions_processing=True
            self.menu_enable()
            self.menubar_config(cursor="")

    text_info_dialog_created = False
    @restore_status_line
    @block_actions_processing
    @gui_block
    def get_text_info_dialog(self):
        if not self.text_info_dialog_created:
            self.status("Creating dialog ...")

            self.text_info_dialog = TextDialogInfo(self.main,(self.ico_librer,self.ico_librer_small),self.bg_color,pre_show=self.pre_show,post_close=self.post_close)

            self.text_info_dialog_created = True

        return self.text_info_dialog


    delete_record_dialog_created = False
    @restore_status_line
    @block_actions_processing
    @gui_block
    def get_delete_record_dialog(self):
        if not self.delete_record_dialog_created:
            self.status("Creating dialog ...")

            self.delete_record_dialog = LabelDialogQuestion(self.main,(self.ico_record_delete,self.ico_record_delete),self.bg_color,pre_show=self.pre_show,post_close=self.post_close,image=self.ico_warning)

            self.delete_record_dialog.label.configure(justify='left')
            try:
                self.delete_record_dialog.label.configure(font=('Courier', 10))
            except:
                try:
                    self.delete_record_dialog.label.configure(font=('TkFixedFont', 10))
                except:
                    pass

            self.delete_record_dialog_created = True

        return self.delete_record_dialog

    def configure_scan_button(self):
        self.scan_button.configure(image=self.ico_start if all(bool(self.CDE_use_var_list[e_local].get())==False for e_local in range(self.CDE_ENTRIES_MAX) ) else self.ico_warning)

    def use_checkbutton_mod(self,e,do_configure_scan_button=True):
        #do_crc = bool( self.CDE_crc_var_list[e].get() )
        do_crc = False
        do_cd = bool( self.CDE_use_var_list[e].get() )

        if self.CDE_use_var_list[e].get():
            self.executable_entry[e].configure(state='normal')
            self.parameters_entry[e].configure(state='normal')
            self.shell_checkbutton[e].configure(state='normal')
            self.open_button[e].configure(state='normal')
            self.timeout_entry[e].configure(state='normal')
            self.test_button[e].configure(state='normal')

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

    scan_dialog_created = False
    @restore_status_line
    @block_actions_processing
    @gui_block
    def get_scan_dialog(self):
        if not self.scan_dialog_created:
            self.status("Creating dialog ...")

            self_ico_librer = self.ico_librer

            self.scan_dialog=dialog=GenericDialog(self.main,(self.ico_record_new,self.ico_record_new),self.bg_color,'Create new data record',pre_show=self.pre_show,post_close=self.post_close,min_width=800,min_height=550)

            self_ico = self.ico

            self.log_skipped_var=BooleanVar()
            self.log_skipped_var.set(False)

            dialog.area_main.grid_columnconfigure(0, weight=1)
            dialog.area_main.grid_rowconfigure(3, weight=1)

            dialog.widget.bind('<Alt_L><p>',lambda event : self.set_path_to_scan())
            dialog.widget.bind('<Alt_L><P>',lambda event : self.set_path_to_scan())
            dialog.widget.bind('<Alt_L><s>',lambda event : self.scan_wrapper())
            dialog.widget.bind('<Alt_L><S>',lambda event : self.scan_wrapper())
            #dialog.widget.bind('<Alt_L><E>',lambda event : self.exclude_mask_add_dialog())
            #dialog.widget.bind('<Alt_L><e>',lambda event : self.exclude_mask_add_dialog())

            ##############

            temp_frame = Frame(dialog.area_main,borderwidth=2,bg=self.bg_color)
            temp_frame.grid(row=0,column=0,sticky='we',padx=4,pady=4)

            ul_lab=Label(temp_frame,text="User label:",bg=self.bg_color,anchor='w')
            ul_lab.grid(row=0, column=0, sticky='news',padx=4,pady=4)\

            self.widget_tooltip(ul_lab,"Label of record to be created\nCannot be changed later.")

            self.scan_label_entry_var=StringVar(value='')
            scan_label_entry = Entry(temp_frame,textvariable=self.scan_label_entry_var)
            scan_label_entry.grid(row=0, column=1, sticky='news',padx=4,pady=4)

            self.widget_tooltip(scan_label_entry,"Label of record to be created\nCannot be changed later.")

            Label(temp_frame,text="Path to scan:",bg=self.bg_color,anchor='w').grid(row=0, column=2, sticky='news',padx=4,pady=4)

            self.path_to_scan_entry_var=StringVar(value=self.last_dir)
            path_to_scan_entry = Entry(temp_frame,textvariable=self.path_to_scan_entry_var)
            path_to_scan_entry.grid(row=0, column=3, sticky='news',padx=4,pady=4)

            self.add_path_button = Button(temp_frame,width=18,image = self.ico_open, command=self.set_path_to_scan,underline=0)
            self.add_path_button.grid(row=0, column=4, sticky='news',padx=4,pady=4)
            self.widget_tooltip(self.add_path_button,"Set path to scan.")

            self.add_dev_button = Menubutton(temp_frame,width=18,image = self.ico_drive,underline=0)
            self.add_dev_button.grid(row=0, column=5, sticky='news',padx=4,pady=4)
            self.widget_tooltip(self.add_dev_button,"Select device to scan.")

            self.drives_menu = Menu(self.add_dev_button, tearoff=0,postcommand=self.set_dev_to_scan_menu)
            self.add_dev_button["menu"] = self.drives_menu

            temp_frame.grid_columnconfigure(3, weight=1)

            ##############
            self.exclude_regexp_scan=BooleanVar()

            temp_frame2 = LabelFrame(dialog.area_main,text='Exclude from scan:',borderwidth=2,bg=self.bg_color,takefocus=False)

            #TODO
            #temp_frame2.grid(row=2,column=0,sticky='news',padx=4,pady=4,columnspan=4)

            self.exclude_scroll_frame=SFrame(temp_frame2,bg=self.bg_color)
            self.exclude_scroll_frame.pack(fill='both',expand=True,side='top',ipadx=4,ipady=4)
            self.exclude_frame=self.exclude_scroll_frame.frame()

            buttons_fr2 = Frame(temp_frame2,bg=self.bg_color,takefocus=False)
            buttons_fr2.pack(fill='x',expand=False,side='bottom')

            self.add_exclude_button_dir = Button(buttons_fr2,width=18,image = self.ico_open,command=self.exclude_mask_add_dir)
            self.add_exclude_button_dir.pack(side='left',pady=4,padx=4)

            self.widget_tooltip(self.add_exclude_button_dir,"Add path as exclude expression ...")

            self.add_exclude_button = Button(buttons_fr2,width=18,image= self_ico['expression'],command=self.exclude_mask_add_dialog,underline=4)

            tooltip_string = 'Add expression ...\nduring the scan, the entire path is checked \nagainst the specified expression,\ne.g.:' + ('*windows* etc. (without regular expression)\nor .*windows.*, etc. (with regular expression)' if windows else '*.git* etc. (without regular expression)\nor .*\\.git.* etc. (with regular expression)')

            self.widget_tooltip(self.add_exclude_button,tooltip_string)

            self.add_exclude_button.pack(side='left',pady=4,padx=4)

            Checkbutton(buttons_fr2,text='treat as a regular expression',variable=self.exclude_regexp_scan,command=self.exclude_regexp_set).pack(side='left',pady=4,padx=4)

            self.exclude_frame.grid_columnconfigure(1, weight=1)
            self.exclude_frame.grid_rowconfigure(99, weight=1)
            ##############

            skip_button = Checkbutton(dialog.area_main,text='log skipped files',variable=self.log_skipped_var)
            #TODO
            #skip_button.grid(row=4,column=0,sticky='news',padx=8,pady=3,columnspan=3)

            self.widget_tooltip(skip_button,"log every skipped file (softlinks, hardlinks, excluded, no permissions etc.)")

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

            self.scan_compr_var.set(9)
            self.scan_compr_var_int.set(9)

            (compr_in_label := Label(scan_options_frame, textvariable=self.scan_compr_var_int,width=3,bg=self.bg_color,relief='groove',borderwidth=2)).pack(side='right',padx=2,pady=2)
            (compr_scale := Scale(scan_options_frame, variable=self.scan_compr_var, orient='horizontal',from_=0, to=22,command=lambda x : self.scan_comp_set(),style="TScale",length=200)).pack(fill='x',side='right',expand=1,padx=2)
            (compr_label := Label(scan_options_frame, text='Compression:',bg=self.bg_color,relief='flat')).pack(side='left',padx=2,pady=2)
            compr_tooltip = "Data record internal compression. A higher value\nmeans a smaller file and longer compression time.\nvalues above 20 may result in extremely long compression\nand memory consumption. The default value is 9."
            self.widget_tooltip(compr_scale,compr_tooltip)
            self.widget_tooltip(compr_label,compr_tooltip)
            self.widget_tooltip(compr_in_label,compr_tooltip)

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

            (lab_use := Label(cde_frame,text='Use',bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=0, column=1,sticky='news')
            (lab_mask := Label(cde_frame,text='File Mask',bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=0, column=2,sticky='news')
            (lab_min := Label(cde_frame,text='Min\nSize',bg=self.bg_color,anchor='n',relief='groove',bd=2,width=3)).grid(row=0, column=3,sticky='news')
            (lab_max := Label(cde_frame,text='Max\nSize',bg=self.bg_color,anchor='n',relief='groove',bd=2,width=3)).grid(row=0, column=4,sticky='news')
            (lab_exec := Label(cde_frame,text='Executable',bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=0, column=5,sticky='news')
            (lab_open := Label(cde_frame,text='',bg=self.bg_color,anchor='n')).grid(row=0, column=6,sticky='news')
            (lab_pars  := Label(cde_frame,text='Parameters',bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=0, column=7,sticky='news')
            (lab_shell := Label(cde_frame,text='Shell',bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=0, column=8,sticky='news')
            (lab_timeout := Label(cde_frame,text='TO',bg=self.bg_color,anchor='n',relief='groove',bd=2,width=3)).grid(row=0, column=9,sticky='news')
            (lab_test := Label(cde_frame,text='CD\nTest',bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=0, column=10,sticky='news')
            #(lab_crc := Label(cde_frame,text='CRC',bg=self.bg_color,anchor='n',relief='groove',bd=2)).grid(row=0, column=9,sticky='news')

            up_tooltip = "Use the arrow to change the order\nin which CDE criteria are checked.\n\nIf a file meets several CDE criteria\n(mask & size), the one with higher priority\nwill be executed. In this table, the first\none from the top has the highest priority,\nthe next ones have lower and lower priority."
            use_tooltip = "Mark to use CD Extractor"
            mask_tooltip = "glob expresions separated by comma (',')\ne.g.: '*.7z, *.zip, *.gz'\n\nthe given executable will run\nwith every file matching the expression\n(and size citeria if provided)"
            max_tooltip = min_tooltip = 'Integer value [in bytes] or integer with unit.\nLeave the value blank to ignore this criterion.\n\nexamples:\n399\n100B\n125kB\n10MB'
            exec_tooltip = "A binary executable or batch script that will run\nwith the full path to the file to be extracted as a parameter.\nThe executable may have a full path, be located in a PATH\nenvironment variable, or be interpreted by the system shell"
            pars_tooltip = f"The executable will run with the full path to the file to extract as a parameter.\nIf other constant parameters are necessary, they should be placed here\nand the scanned file should be indicated with the '{PARAM_INDICATOR_SIGN}' sign.\nThe absence of the '{PARAM_INDICATOR_SIGN}' sign means that the file will be passed as the last parameter.\ne.g.:const_param % other_const_param"
            shell_tooltip = "Execute in system shell\nUse only when necessary."
            open_tooltip = "Point executable as custom data extractor..."
            timeout_tooltip = "Timeout limit in seconds for single CD extraction.\nAfter timeout executed process will be terminated\n\n'0' or empty field means no timeout."
            test_tooltip = "Select a file and test your Custom Data Extractor.\n\nBefore you run scan, and therefore run your CDE on all\nfiles that will match on the scan path,\ntest your Custom Data Extractor\non a single, manually selected file.\nCheck if it's getting the expected data\nand has no unexpected side-effects."

            self_widget_tooltip = self.widget_tooltip

            self_widget_tooltip(lab_use,use_tooltip)
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

                row = e+1

                self.up_button[e] = Button(cde_frame,image=self.ico_up,command = lambda x=e : self.cde_up(x) )

                if row>1:
                    self.up_button[e].grid(row=row,column=0,sticky='news')

                self.use_checkbutton[e] = Checkbutton(cde_frame,variable=self.CDE_use_var_list[e],command = lambda x=e : self.use_checkbutton_mod(x))
                self.use_checkbutton[e].grid(row=row,column=1,sticky='news')

                self.mask_entry[e] = Entry(cde_frame,textvariable=self.CDE_mask_var_list[e])
                self.mask_entry[e].grid(row=row, column=2,sticky='news')

                self.size_min_entry[e] = Entry(cde_frame,textvariable=self.CDE_size_min_var_list[e],width=6)
                self.size_min_entry[e].grid(row=row, column=3,sticky ='news')

                self.size_max_entry[e] = Entry(cde_frame,textvariable=self.CDE_size_max_var_list[e],width=6)
                self.size_max_entry[e].grid(row=row, column=4,sticky ='news')

                self.executable_entry[e] = Entry(cde_frame,textvariable=self.CDE_executable_var_list[e])
                self.executable_entry[e].grid(row=row, column=5,sticky='news')

                self.open_button[e] = Button(cde_frame,image=self.ico_folder,command = lambda x=e : self.cde_entry_open(x) )
                self.open_button[e].grid(row=row,column=6,sticky='news')

                self.parameters_entry[e] = Entry(cde_frame,textvariable=self.CDE_parameters_var_list[e])
                self.parameters_entry[e].grid(row=row, column=7,sticky='news')

                self.shell_checkbutton[e] = Checkbutton(cde_frame,variable=self.CDE_shell_var_list[e])
                self.shell_checkbutton[e].grid(row=row, column=8,sticky='news')

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
            cde_frame.grid_columnconfigure(5, weight=2)
            cde_frame.grid_columnconfigure(7, weight=1)

            self.scan_dialog_created = True

            ###########################################

            #self.exclude_dialog_on_scan = EntryDialogQuestion(dialog.widget,(self.ico_librer,self.ico_librer_small),self.bg_color,pre_show=self.pre_show,post_close=self.post_close)

            self.exclude_regexp_scan.set(self.cfg_get(CFG_KEY_EXCLUDE_REGEXP))

        return self.scan_dialog

    progress_dialog_on_scan_created = False
    @restore_status_line
    @block_actions_processing
    @gui_block
    def get_progress_dialog_on_scan(self):
        if not self.progress_dialog_on_scan_created:
            self.status("Creating dialog ...")

            self.progress_dialog_on_scan = ProgressDialog(self.scan_dialog.widget,(self.ico_librer,self.ico_librer_small),self.bg_color,pre_show=lambda new_widget : self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))

            self.progress_dialog_on_scan.command_on_close = self.progress_dialog_abort

            self.widget_tooltip(self.progress_dialog_on_scan.abort_button,'')
            self.progress_dialog_on_scan_created = True

        return self.progress_dialog_on_scan

    simple_progress_dialog_on_scan_created = False
    @restore_status_line
    @block_actions_processing
    @gui_block
    def get_simple_progress_dialog_on_scan(self):
        if not self.simple_progress_dialog_on_scan_created:
            self.status("Creating dialog ...")

            self.simple_progress_dialog_on_scan = ProgressDialog(self.scan_dialog.widget,(self.ico_librer,self.ico_librer_small),self.bg_color,pre_show=lambda new_widget : self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False),ShowProgress=False,min_width=400,min_height=200)

            self.simple_progress_dialog_on_scan.command_on_close = self.progress_dialog_abort

            self.widget_tooltip(self.simple_progress_dialog_on_scan.abort_button,'Abort test')

            str_simple_progress_dialog_scan_abort_button = str(self.simple_progress_dialog_on_scan.abort_button)
            self.tooltip_message[str_simple_progress_dialog_scan_abort_button]='Abort test.'

            self.simple_progress_dialog_on_scan_created = True

        return self.simple_progress_dialog_on_scan

    info_dialog_on_scan_created = False
    @restore_status_line
    @block_actions_processing
    @gui_block
    def get_info_dialog_on_scan(self):
        if not self.info_dialog_on_scan_created:
            self.status("Creating dialog ...")

            self.info_dialog_on_scan = LabelDialog(self.scan_dialog.widget,(self.ico_librer,self.ico_librer_small),self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))
            self.info_dialog_on_scan_created = True

        return self.info_dialog_on_scan

    text_dialog_on_scan_created = False
    @restore_status_line
    @block_actions_processing
    @gui_block
    def get_text_dialog_on_scan(self):
        if not self.text_dialog_on_scan_created:
            self.status("Creating dialog ...")

            self.text_dialog_on_scan = TextDialogInfo(self.scan_dialog.widget,(self.ico_librer,self.ico_librer_small),self.bg_color,pre_show=lambda new_widget : self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))
            self.text_dialog_on_scan_created = True

        return self.text_dialog_on_scan

    text_ask_dialog_on_scan_created = False
    @restore_status_line
    @block_actions_processing
    @gui_block
    def get_text_ask_dialog_on_scan(self):
        if not self.text_ask_dialog_on_scan_created:
            self.status("Creating dialog ...")

            self.text_ask_dialog_on_scan = TextDialogQuestion(self.scan_dialog.widget,(self.ico_librer,self.ico_librer_small),self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False),image=self.ico_warning)
            self.text_ask_dialog_on_scan_created = True

        return self.text_ask_dialog_on_scan

    text_ask_dialog_on_main_created = False
    @restore_status_line
    @block_actions_processing
    @gui_block
    def get_text_ask_dialog_on_main(self):
        if not self.text_ask_dialog_on_main_created:
            self.status("Creating dialog ...")

            self.text_ask_dialog_on_main = TextDialogQuestion(self.main,(self.ico_librer,self.ico_librer_small),self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))
            #,image=self.ico_warning
            self.text_ask_dialog_on_main_created = True

        return self.text_ask_dialog_on_main

    progress_dialog_on_find_created = False
    @restore_status_line
    @block_actions_processing
    @gui_block
    def get_progress_dialog_on_find(self):
        if not self.progress_dialog_on_find_created:
            self.status("Creating dialog ...")

            self.progress_dialog_on_find = ProgressDialog(self.find_dialog.widget,(self.ico_librer,self.ico_librer_small),self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))
            self.progress_dialog_on_find.command_on_close = self.progress_dialog_find_abort
            self.widget_tooltip(self.progress_dialog_on_find.abort_button,'Abort searching.')

            self.progress_dialog_on_find_created = True

        return self.progress_dialog_on_find

    def export_to_local(self):
        self.export_dialog_file = sep.join([DATA_DIR,f'imp_{int(time())}.dat']),True
        self.export_dialog.hide()

    def export_to_file(self):
        self.export_dialog_file = asksaveasfilename(initialdir=self.last_dir,parent = self.export_dialog.widget, initialfile = 'record.dat',defaultextension=".dat",filetypes=[("Dat Files","*.dat"),("All Files","*.*")]),False
        self.export_dialog.hide()

    def export_comp_set(self):
        self.export_compr_var_int.set(int(self.export_compr_var.get()))

    export_dialog_created = False
    @restore_status_line
    @block_actions_processing
    @gui_block
    def get_export_dialog(self):
        if not self.export_dialog_created:

            self.export_dialog=GenericDialog(self.main,(self.ico_librer,self.ico_librer_small),self.bg_color,'Export record',pre_show=self.pre_show,post_close=self.post_close,min_width=400,min_height=200)
            self.export_cd_var = BooleanVar()
            #self.export_crc_var = BooleanVar()
            self.export_compr_var = IntVar()
            self.export_compr_var_int = IntVar()
            self.export_label_var = StringVar()

            self.export_cd_var.set(self.cfg.get(CFG_KEY_export_cd))
            #self.export_crc_var.set(self.cfg.get(CFG_KEY_export_crc))

            self.export_compr_var.set(9)
            self.export_compr_var_int.set(9)
            self.export_label_var.set('')

            (label_frame := LabelFrame(self.export_dialog.area_main,text='Record Label',bd=2,bg=self.bg_color,takefocus=False)).grid(row=0,column=0,sticky='news',padx=4,pady=4,columnspan=2)
            Entry(label_frame,textvariable=self.export_label_var).pack(expand='yes',fill='x',padx=2,pady=2)

            (export_frame := LabelFrame(self.export_dialog.area_main,text='Data options',bd=2,bg=self.bg_color,takefocus=False)).grid(row=1,column=0,sticky='news',padx=4,pady=4,columnspan=2)
            self.export_dialog.area_main.grid_columnconfigure( 0, weight=1)
            self.export_dialog.area_main.grid_columnconfigure( 1, weight=1)

            self.export_dialog.area_main.grid_rowconfigure( 2, weight=1)

            self.export_cd_cb = Checkbutton(export_frame,text='Include \'Custom Data\'',variable=self.export_cd_var)
            #self.export_crc_cb = Checkbutton(export_frame,text='Include CRC values',variable=self.export_crc_var)

            self.export_cd_cb.grid(row=0, column=0, sticky='wens',padx=4,pady=4)
            #self.export_crc_cb.grid(row=1, column=0, sticky='wens',padx=4,pady=4)

            export_frame.grid_columnconfigure( 0, weight=1)

            (export_frame_compr := LabelFrame(self.export_dialog.area_main,text='Compression (0-22)',bd=2,bg=self.bg_color,takefocus=False)).grid(row=2,column=0,sticky='news',padx=4,pady=4,columnspan=2)

            Scale(export_frame_compr, variable=self.export_compr_var, orient='horizontal',from_=0, to=22,command=lambda x : self.export_comp_set(),style="TScale").pack(fill='x',side='left',expand=1,padx=2)
            Label(export_frame_compr, textvariable=self.export_compr_var_int,width=3,bg=self.bg_color,relief='ridge').pack(side='right',padx=2,pady=2)

            self.export_dialog_file=None,False

            Button(self.export_dialog.area_buttons, text='To Local Repo', width=14, command= self.export_to_local ).pack(side='left', anchor='n',padx=5,pady=5)
            Button(self.export_dialog.area_buttons, text='Select File ...', width=14, command= self.export_to_file ).pack(side='left', anchor='n',padx=5,pady=5)
            Button(self.export_dialog.area_buttons, text='Close', width=14, command=self.export_dialog.hide ).pack(side='right', anchor='n',padx=5,pady=5)

            self.export_dialog_created = True
        return self.export_dialog

    def import_files_confirm(self):
        self.do_import=True
        self.import_dialog.hide()

    def import_comp_set(self):
        self.import_compr_var_int.set(int(self.import_compr_var.get()))

    import_dialog_created = False
    @restore_status_line
    @block_actions_processing
    @gui_block
    def get_import_dialog(self):
        self.do_import=False
        if not self.import_dialog_created:

            self.import_dialog=GenericDialog(self.main,(self.ico_librer,self.ico_librer_small),self.bg_color,'Import record(s)',pre_show=self.pre_show,post_close=self.post_close,min_width=400,min_height=200)
            self.import_cd_var = BooleanVar()
            #self.import_crc_var = BooleanVar()
            self.import_compr_var = IntVar()
            self.import_compr_var_int = IntVar()

            self.import_cd_var.set(self.cfg.get(CFG_KEY_import_cd))
            #self.import_crc_var.set(self.cfg.get(CFG_KEY_import_crc))

            self.import_compr_var.set(9)
            self.import_compr_var_int.set(9)

            (import_frame := LabelFrame(self.import_dialog.area_main,text='Data options',bd=2,bg=self.bg_color,takefocus=False)).grid(row=0,column=0,sticky='news',padx=4,pady=4,columnspan=2)
            self.import_dialog.area_main.grid_columnconfigure( 0, weight=1)
            self.import_dialog.area_main.grid_columnconfigure( 1, weight=1)

            self.import_dialog.area_main.grid_rowconfigure( 2, weight=1)

            self.import_cd_cb = Checkbutton(import_frame,text='Include \'Custom Data\'',variable=self.import_cd_var)
            #self.import_crc_cb = Checkbutton(import_frame,text='Include CRC values',variable=self.import_crc_var)

            self.import_cd_cb.grid(row=0, column=0, sticky='wens',padx=4,pady=4)
            #self.import_crc_cb.grid(row=1, column=0, sticky='wens',padx=4,pady=4)

            import_frame.grid_columnconfigure( 0, weight=1)

            (import_frame_compr := LabelFrame(self.import_dialog.area_main,text='Compression (0-22)',bd=2,bg=self.bg_color,takefocus=False)).grid(row=1,column=0,sticky='news',padx=4,pady=4,columnspan=2)

            Scale(import_frame_compr, variable=self.import_compr_var, orient='horizontal',from_=0, to=22,command=lambda x : self.import_comp_set()).pack(fill='x',side='left',expand=1,padx=2)
            Label(import_frame_compr, textvariable=self.import_compr_var_int,width=3,bg=self.bg_color,relief='ridge').pack(side='right',padx=2,pady=2)

            self.import_dialog_file=None
            Button(self.import_dialog.area_buttons, text='OK', width=14, command= self.import_files_confirm ).pack(side='left', anchor='n',padx=5,pady=5)
            Button(self.import_dialog.area_buttons, text='Cancel', width=14, command=self.import_dialog.hide ).pack(side='right', anchor='n',padx=5,pady=5)

            self.import_dialog_created = True
        return self.import_dialog


    find_dialog_created = False
    @restore_status_line
    @block_actions_processing
    @gui_block
    def get_find_dialog(self):
        if not self.find_dialog_created:
            self.status("Creating dialog ...")

            ###################################
            self.find_dialog=GenericDialog(self.main,(self.ico_librer,self.ico_librer_small),self.bg_color,'Search records',pre_show=self.pre_show,post_close=self.post_close)

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

            self.find_size_min_var.trace_add("write", lambda i,j,k : self.find_mod())
            self.find_size_max_var.trace_add("write", lambda i,j,k : self.find_mod())

            self.find_modtime_min_var.trace_add("write", lambda i,j,k : self.find_mod())
            self.find_modtime_max_var.trace_add("write", lambda i,j,k : self.find_mod())

            self.find_name_regexp_var.trace_add("write", lambda i,j,k : self.find_mod())
            self.find_name_glob_var.trace_add("write", lambda i,j,k : self.find_mod())
            self.find_name_fuzz_var.trace_add("write", lambda i,j,k : self.find_mod())
            self.find_name_case_sens_var.trace_add("write", lambda i,j,k : self.find_mod())

            self.find_cd_regexp_var.trace_add("write", lambda i,j,k : self.find_mod())
            self.find_cd_glob_var.trace_add("write", lambda i,j,k : self.find_mod())
            self.find_cd_fuzz_var.trace_add("write", lambda i,j,k : self.find_mod())
            self.find_cd_case_sens_var.trace_add("write", lambda i,j,k : self.find_mod())

            self.find_name_fuzzy_threshold.trace_add("write", lambda i,j,k : self.find_mod())
            self.find_cd_fuzzy_threshold.trace_add("write", lambda i,j,k : self.find_mod())

            sfdma = self.find_dialog.area_main

            (find_filename_frame := LabelFrame(sfdma,text='Search range',bd=2,bg=self.bg_color,takefocus=False)).grid(row=0,column=0,sticky='news',padx=4,pady=4)
            (find_range_cb1 := Radiobutton(find_filename_frame,text='Selected record',variable=self.find_range_all,value=False,command=self.find_mod)).grid(row=0, column=0, sticky='news',padx=4,pady=4)
            (find_range_cb2 := Radiobutton(find_filename_frame,text='All records',variable=self.find_range_all,value=True,command=self.find_mod)).grid(row=0, column=1, sticky='news',padx=4,pady=4)

            (find_filename_frame := LabelFrame(sfdma,text='File path and name',bd=2,bg=self.bg_color,takefocus=False)).grid(row=1,column=0,sticky='news',padx=4,pady=4)

            Radiobutton(find_filename_frame,text="Don't use this criterion",variable=self.find_filename_search_kind_var,value='dont',command=self.find_mod,width=30).grid(row=0, column=0, sticky='news',padx=4,pady=4)
            Radiobutton(find_filename_frame,text="files with error on access",variable=self.find_filename_search_kind_var,value='error',command=self.find_mod)
            #.grid(row=1, column=0, sticky='news',padx=4,pady=4)
            (regexp_radio_name:=Radiobutton(find_filename_frame,text="by regular expression",variable=self.find_filename_search_kind_var,value='regexp',command=self.find_mod)).grid(row=2, column=0, sticky='news',padx=4,pady=4)
            (glob_radio_name:=Radiobutton(find_filename_frame,text="by glob pattern",variable=self.find_filename_search_kind_var,value='glob',command=self.find_mod)).grid(row=3, column=0, sticky='news',padx=4,pady=4)
            (fuzzy_radio_name:=Radiobutton(find_filename_frame,text="by fuzzy match",variable=self.find_filename_search_kind_var,value='fuzzy',command=self.find_mod)).grid(row=4, column=0, sticky='news',padx=4,pady=4)

            regexp_tooltip = "Regular expression\n"
            regexp_tooltip_name = "checked on the file\nor folder name."
            regexp_tooltip_cd = "checked on the entire\nCustom Data of a file."

            glob_tooltip = "An expression containing wildcard characters\nsuch as '*','?' or character range '[a-c]'.\n"
            glob_tooltip_name = 'checked on the file or folder name.'
            glob_tooltip_cd = 'checked on the entire Custom Data of a file.'

            fuzzy_tooltip = 'Fuzzy matching is implemented using SequenceMatcher\nfrom the difflib module. Any file whose similarity\nscore exceeds the threshold will be classified as found.\nThe similarity score is calculated\n'
            fuzzy_tooltip_name = 'based on the file or folder name.'
            fuzzy_tooltip_cd = 'based on the entire Custom Data of a file.'

            self.find_filename_regexp_entry = Entry(find_filename_frame,textvariable=self.find_name_regexp_var,validate="key")
            self.find_filename_glob_entry = Entry(find_filename_frame,textvariable=self.find_name_glob_var,validate="key")
            self.find_filename_fuzz_entry = Entry(find_filename_frame,textvariable=self.find_name_fuzz_var,validate="key")

            self.find_filename_regexp_entry.bind("<KeyPress>", lambda event : self.find_mod)
            self.find_filename_glob_entry.bind("<KeyPress>", lambda event : self.find_mod)
            self.find_filename_fuzz_entry.bind("<KeyPress>", lambda event : self.find_mod)

            self.find_filename_regexp_entry.grid(row=2, column=1, sticky='we',padx=4,pady=4)
            self.find_filename_glob_entry.grid(row=3, column=1, sticky='we',padx=4,pady=4)
            self.find_filename_fuzz_entry.grid(row=4, column=1, sticky='we',padx=4,pady=4)

            self.find_filename_case_sens_cb = Checkbutton(find_filename_frame,text='Case sensitive',variable=self.find_name_case_sens_var,command=self.find_mod)
            self.find_filename_case_sens_cb.grid(row=3, column=2, sticky='wens',padx=4,pady=4,columnspan=2)

            self.find_filename_fuzzy_threshold_lab = Label(find_filename_frame,text='Threshold:',bg=self.bg_color,anchor='e')
            self.find_filename_fuzzy_threshold_entry = Entry(find_filename_frame,textvariable=self.find_name_fuzzy_threshold)
            self.find_filename_fuzzy_threshold_lab.grid(row=4, column=2, sticky='wens',padx=4,pady=4)
            self.find_filename_fuzzy_threshold_entry.grid(row=4, column=3, sticky='wens',padx=4,pady=4)

            self.widget_tooltip(regexp_radio_name,regexp_tooltip + regexp_tooltip_name)
            self.widget_tooltip(self.find_filename_regexp_entry,regexp_tooltip + regexp_tooltip_name)
            self.widget_tooltip(glob_radio_name,glob_tooltip + glob_tooltip_name)
            self.widget_tooltip(self.find_filename_glob_entry,glob_tooltip + glob_tooltip_name)

            self.widget_tooltip(fuzzy_radio_name,fuzzy_tooltip + fuzzy_tooltip_name)
            self.widget_tooltip(self.find_filename_fuzz_entry,fuzzy_tooltip + fuzzy_tooltip_name)
            self.widget_tooltip(self.find_filename_fuzzy_threshold_entry,fuzzy_tooltip + fuzzy_tooltip_name)

            find_filename_frame.grid_columnconfigure( 1, weight=1)

            (find_cd_frame := LabelFrame(sfdma,text='Custom Data',bd=2,bg=self.bg_color,takefocus=False)).grid(row=2,column=0,sticky='news',padx=4,pady=4)

            Radiobutton(find_cd_frame,text="Don't use this criterion",variable=self.find_cd_search_kind_var,value='dont',command=self.find_mod,width=30).grid(row=0, column=0, sticky='news',padx=4,pady=4)
            Radiobutton(find_cd_frame,text="files without Custom Data ",variable=self.find_cd_search_kind_var,value='without',command=self.find_mod).grid(row=1, column=0, sticky='news',padx=4,pady=4)
            Radiobutton(find_cd_frame,text="files with any correct Custom Data ",variable=self.find_cd_search_kind_var,value='any',command=self.find_mod).grid(row=2, column=0, sticky='news',padx=4,pady=4)
            Radiobutton(find_cd_frame,text="files with error on CD extraction",variable=self.find_cd_search_kind_var,value='error',command=self.find_mod).grid(row=3, column=0, sticky='news',padx=4,pady=4)
            (regexp_radio_cd:=Radiobutton(find_cd_frame,text="by regular expression",variable=self.find_cd_search_kind_var,value='regexp',command=self.find_mod)).grid(row=4, column=0, sticky='news',padx=4,pady=4)
            (glob_radio_cd:=Radiobutton(find_cd_frame,text="by glob pattern",variable=self.find_cd_search_kind_var,value='glob',command=self.find_mod)).grid(row=5, column=0, sticky='news',padx=4,pady=4)
            (fuzzy_radio_cd:=Radiobutton(find_cd_frame,text="by fuzzy match",variable=self.find_cd_search_kind_var,value='fuzzy',command=self.find_mod)).grid(row=6, column=0, sticky='news',padx=4,pady=4)

            self.find_cd_regexp_entry = Entry(find_cd_frame,textvariable=self.find_cd_regexp_var,validate="key")
            self.find_cd_glob_entry = Entry(find_cd_frame,textvariable=self.find_cd_glob_var,validate="key")
            self.find_cd_fuzz_entry = Entry(find_cd_frame,textvariable=self.find_cd_fuzz_var,validate="key")

            self.find_cd_regexp_entry.bind("<KeyPress>", lambda event : self.find_mod)
            self.find_cd_glob_entry.bind("<KeyPress>", lambda event : self.find_mod)
            self.find_cd_fuzz_entry.bind("<KeyPress>", lambda event : self.find_mod)

            self.find_cd_regexp_entry.grid(row=4, column=1, sticky='we',padx=4,pady=4)
            self.find_cd_glob_entry.grid(row=5, column=1, sticky='we',padx=4,pady=4)
            self.find_cd_fuzz_entry.grid(row=6, column=1, sticky='we',padx=4,pady=4)

            self.cd_case_sens_cb = Checkbutton(find_cd_frame,text='Case sensitive',variable=self.find_cd_case_sens_var,command=self.find_mod)
            self.cd_case_sens_cb.grid(row=5, column=2, sticky='wens',padx=4,pady=4,columnspan=2)

            self.find_cd_fuzzy_threshold_lab = Label(find_cd_frame,text='Threshold:',bg=self.bg_color,anchor='e')
            self.find_cd_fuzzy_threshold_entry = Entry(find_cd_frame,textvariable=self.find_cd_fuzzy_threshold)
            self.find_cd_fuzzy_threshold_lab.grid(row=6, column=2, sticky='wens',padx=4,pady=4)
            self.find_cd_fuzzy_threshold_entry.grid(row=6, column=3, sticky='wens',padx=4,pady=4)

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

            time_toltip = 'Date and time in the format below.\nLeave the value blank to ignore this criterion.\n\nexamples:\n2023-12-14 22:21:20\n2023-12-14 22:21\n2023-12-14\n2023-12'
            self.widget_tooltip(find_modtime_min_entry,time_toltip)
            self.widget_tooltip(find_modtime_min_label,time_toltip)
            self.widget_tooltip(find_modtime_max_entry,time_toltip)
            self.widget_tooltip(find_modtime_max_label,time_toltip)

            Button(self.find_dialog.area_buttons, text='Search', width=14, command=self.find_items ).pack(side='left', anchor='n',padx=5,pady=5)
            self.search_show_butt = Button(self.find_dialog.area_buttons, text='Show results', width=14, command=self.find_show_results )
            self.search_show_butt.pack(side='left', anchor='n',padx=5,pady=5)
            self.search_save_butt = Button(self.find_dialog.area_buttons, text='Save results', width=14, command=self.find_save_results )
            self.search_save_butt.pack(side='left', anchor='n',padx=5,pady=5)

            Button(self.find_dialog.area_buttons, text='Close', width=14, command=self.find_close ).pack(side='right', anchor='n',padx=5,pady=5)

            sfdma.grid_rowconfigure(5, weight=1)
            sfdma.grid_columnconfigure(0, weight=1)

            self.info_dialog_on_find = LabelDialog(self.find_dialog.widget,(self.ico_librer,self.ico_librer_small),self.bg_color,pre_show=lambda new_widget : self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))
            self.text_dialog_on_find = TextDialogInfo(self.find_dialog.widget,(self.ico_librer,self.ico_librer_small),self.bg_color,pre_show=lambda new_widget: self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))

            self.results_on_find = LabelDialogQuestion(self.find_dialog.widget,(self.ico_librer,self.ico_librer_small),self.bg_color,pre_show=lambda new_widget : self.pre_show(on_main_window_dialog=False,new_widget=new_widget),post_close=lambda : self.post_close(on_main_window_dialog=False))

            self.results_on_find.cancel_button.configure(text='Continue search.',width=20)
            self.results_on_find.ok_button.configure(text='Close Search dialog',width=20)

            self.find_dialog_created = True

        return self.find_dialog

    about_dialog_created = False
    @restore_status_line
    @block_actions_processing
    @gui_block
    def get_about_dialog(self):
        if not self.about_dialog_created:
            self.status("Creating dialog ...")

            self.aboout_dialog=GenericDialog(self.main,(self.ico_librer,self.ico_librer_small),self.bg_color,'',pre_show=self.pre_show,post_close=self.post_close)

            frame1 = LabelFrame(self.aboout_dialog.area_main,text='',bd=2,bg=self.bg_color,takefocus=False)
            frame1.grid(row=0,column=0,sticky='news',padx=4,pady=(4,2))
            self.aboout_dialog.area_main.grid_rowconfigure(1, weight=1)

            text= f'\n\nLibrer {VER_TIMESTAMP}\nAuthor: Piotr Jochymek\n\n{HOMEPAGE}\n\nPJ.soft.dev.x@gmail.com\n\n'

            Label(frame1,text=text,bg=self.bg_color,justify='center').pack(expand=1,fill='both')

            frame2 = LabelFrame(self.aboout_dialog.area_main,text='',bd=2,bg=self.bg_color,takefocus=False)
            frame2.grid(row=1,column=0,sticky='news',padx=4,pady=(2,4))

            lab2_text=  distro_info + '\n\nCurrent log file   :  ' + log_file

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
    @block_actions_processing
    @gui_block
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

    @restore_status_line
    @block_actions_processing
    @gui_block
    def record_export(self):
        if self.current_record:
            dialog = self.get_export_dialog()

            self.export_compr_var.set(self.current_record.header.compression_level)
            self.export_compr_var_int.set(self.current_record.header.compression_level)
            self.export_label_var.set(self.current_record.header.label)

            self.export_dialog_file=None,False

            dialog.show()

            new_label = self.export_label_var.get()
            new_compression = self.export_compr_var_int.get()

            new_file_path,is_local = self.export_dialog_file
            if new_file_path:
                self.record_export_do(new_file_path,is_local,new_label,new_compression)

    @block_actions_processing
    @gui_block
    def record_export_do(self,new_file_path,is_local,new_label,new_compression):

        keep_cd = self.cfg.set(CFG_KEY_export_cd,self.export_cd_var.get())
        keep_crc = False
        self.status('exporting "%s" ...' % str(new_file_path))
        self.main_update()

        #print(f'{is_local=}')
        cres=LibrerRecord.clone_record_file(self.current_record.file_path,new_file_path,new_label,new_compression)
        #print('cloned',cres)

        if is_local:
            new_record = librer_core.create()
            if res:=new_record.load(new_file_path):
                print(f'record_import:{res}')
                self.info_dialog_on_main.show('Export-Import failed (3)',f'local load failed :{new_file_path}\nerror: {res}')
            else:
                self.single_record_show(new_record)

    #@restore_status_line
    @block_actions_processing
    @gui_block
    def record_import(self):
        initialdir = self.last_dir if self.last_dir else self.cwd

        filenames = askopenfilenames(initialdir=self.last_dir,parent = self.main,title='Choose record file(s) to import', defaultextension=".dat",filetypes=[("Dat Files","*.dat"),("All Files","*.*")])

        if not filenames:
            return

        ok_counter=0
        messages_all=[]
        for dat_file in filenames:
            temp_record = librer_core.create()

            record_short_info=[]
            record_short_info.append(f'file:{dat_file}')
            if res:=temp_record.load(dat_file):

                record_short_info.append(res + '\n')
                l_error(f'import failed :{dat_file} error: {res}')
            else:
                record_short_info.append('\n' + temp_record.txtinfo_short + '\n')
                ok_counter+=1

            messages_all.append('\n'.join(record_short_info))
            del temp_record
            self.last_dir = dirname(dat_file)

        ask_dialog = self.get_text_ask_dialog_on_main()

        ask_dialog.show('Continue importing selected record(s) ?',('-'*84 + '\n').join(messages_all))

        if ask_dialog.res_bool:

            if ok_counter:
                dialog = self.get_import_dialog()
                dialog.show()

                if self.do_import:
                    keep_cd = self.cfg.set(CFG_KEY_import_cd,self.import_cd_var.get())
                    #keep_crc = self.cfg.set(CFG_KEY_import_crc,self.import_crc_var.get())
                    keep_crc = False

                    counter=0
                    for dat_file in filenames:
                        counter+=1
                        self.status(f'importing {dat_file} ({counter}/{ok_counter})...')
                        self.main_update()

                        new_record = librer_core.create()
                        if res:=new_record.load(dat_file):
                            l_error(f'import failed :{dat_file} error: {res}')
                            self.info_dialog_on_main.show('Import failed',f'import failed :{dat_file}\nerror: {res}')

                            continue

                        local_file_name = 'imported.'+ str(time()) + '.dat'
                        local_file = sep.join([DATA_DIR,local_file_name])

                        new_record.clone_record(local_file,keep_cd,keep_crc,self.import_compr_var_int.get())

                        if res:=new_record.load_wrap(DATA_DIR,local_file_name):
                            #print(f'record_import:{res}')
                            self.info_dialog_on_main.show('Import failed (2)',f'local load failed :{local_file_name}\nerror: {res}')
                        else:
                            self.single_record_show(new_record)

                    self.status(f'records import finished.')
            else:
                self.info_dialog_on_main.show('Import failed','No valid record files to import.')

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
        if self.actions_processing:
            self.tooltip_show_after_tree = event.widget.after(1, self.show_tooltips_tree(event))

    def configure_tooltip(self,widget):
        self.tooltip_lab_configure(text=self.tooltip_message[str(widget)])

    def show_tooltip_widget(self,event):
        self.unschedule_tooltip_widget(event)
        self.menubar_unpost()

        self.configure_tooltip(event.widget)

        self.tooltip_deiconify()
        self.tooltip_wm_geometry("+%d+%d" % (event.x_root + 20, event.y_root + 5))

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
            #else:
                #print(f'get_item_record no values: {item=},{values=}')
                #dummy item

            item=tree.parent(item)

        subpath_list.reverse()
        return (item,current_record_name,subpath_list)
        #sep + sep.join(reversed(subpath_list))

    def show_tooltips_tree(self,event):
        self.unschedule_tooltips_tree(event)
        self.menubar_unpost()

        self.tooltip_wm_geometry("+%d+%d" % (event.x_root + 20, event.y_root + 5))

        tree = event.widget
        col=tree.identify_column(event.x)
        if col:
            colname=tree.column(col,'id')
            if tree.identify("region", event.x, event.y) == 'heading':
                if colname in ('path','size_h','ctime_h'):
                    self.tooltip_lab_configure(text='Sort by %s' % self.org_label[colname])
                    self.tooltip_deiconify()
                else:
                    self.hide_tooltip()

            elif item := tree.identify('item', event.x, event.y):
                if col=="#0" :
                    record_item,record_name,subpath_list = self.get_item_record(item)
                    record = self.item_to_record[record_item]

                    raw_record_it_is = tree.tag_has(self.RECORD_RAW,item)
                    record_it_is = tree.tag_has(self.RECORD,item)

                    if raw_record_it_is or record_it_is:
                        self.tooltip_lab_configure(text=record.txtinfo_basic + '\n\n(Double click to show full record info)')
                    else:
                        scan_path = record.header.scan_path
                        subpath = sep + sep.join(subpath_list)

                        tooltip_list = [f'scan path : {scan_path}']
                        tooltip_list.append(f'subpath   : {subpath}')

                        if item in self.item_to_data:
                            data_tuple = self.item_to_data[item]
                            code = data_tuple[1]
                            is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc = LUT_decode[code]

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

                    self.tooltip_deiconify()

                elif col:
                    coldata=tree.set(item,col)

                    if coldata:
                        self.tooltip_lab_configure(text=coldata)
                        self.tooltip_deiconify()

                    else:
                        self.hide_tooltip()

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
        if self.actions_processing:
            self.exit()
        else:
            self.status('WM_DELETE_WINDOW NOT exiting ...')

    def exit(self):
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

    any_find_result=False

    find_params_changed=True

    def finder_wrapper_show(self):
        if self.current_record:
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
    @block_actions_processing
    @gui_block
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

        self.any_find_result = False

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

    #@restore_status_line
    @block_actions_processing
    @gui_block
    def find_prev(self):
        if not self.any_find_result:
            self.finder_wrapper_show()
        else:
            self.select_find_result(-1)

    #@restore_status_line
    @block_actions_processing
    @gui_block
    def find_next(self):
        if not self.any_find_result:
            self.finder_wrapper_show()
        else:
            self.select_find_result(1)

    def find_save_results(self):
        self.find_items()

        if report_file_name := asksaveasfilename(parent = self.find_dialog.widget, initialfile = 'librer_search_report.txt',defaultextension=".txt",filetypes=[("All Files","*.*"),("Text Files","*.txt")]):
            self.status('saving file "%s" ...' % str(report_file_name))

            with open(report_file_name,'w') as report_file:
                report_file_write = report_file.write
                #report_file_write('criteria: \n')

                for record in librer_core.records:
                    if record.find_results:
                        report_file_write(f'record:{record.header.label}\n')
                        for res_item,res_size,res_mtime in record.find_results:
                            report_file_write(f'  {sep.join(res_item)}\n')

                        report_file_write('\n')

            self.status('file saved: "%s"' % str(report_file_name))

    def find_show_results(self):
        self.find_items()

        rest_txt_list = []
        for record in librer_core.records:
            if record.find_results:
                rest_txt_list.append(f'record:{record.header.label}')
                for res_item,res_size,res_mtime in record.find_results:
                    rest_txt_list.append(f'  {sep.join(res_item)}')

                rest_txt_list.append('')

            res_txt = '\n'.join(rest_txt_list)

        self.text_dialog_on_find.show('Search results',res_txt)


    find_result_record_index=0
    find_result_index=0

    find_dialog_shown=False

    def find_mod(self):
        try:
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

                self.search_show_butt.configure(state='disabled')
                self.search_save_butt.configure(state='disabled')

        except Exception as e:
            self.find_result_record_index=0
            self.find_result_index=0
            self.find_params_changed=True
            l_error(e)

        return True #for entry validation

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

            if find_size_min:
                min_num = str_to_bytes(find_size_min)
                if min_num == -1:
                    self.info_dialog_on_find.show('min size value error',f'fix "{find_size_min}"')
                    return
            else:
                min_num = ''

            if find_size_max:
                max_num = str_to_bytes(find_size_max)
                if max_num == -1:
                    self.info_dialog_on_find.show('max size value error',f'fix "{find_size_max}"')
                    return
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

            t_max=None
            if find_modtime_max:
                try:
                    t_max = int(mktime(parse_datetime(find_modtime_max).timetuple()))
                except Exception as te:
                    self.info_dialog_on_find.show('file modification time max error ',f'{find_modtime_max}\n{te}')
                    return

            range_par = self.current_record if not find_range_all else None

            if check_res := librer_core.find_items_in_records_check(
                range_par,
                min_num,max_num,
                find_filename_search_kind,find_name,find_name_case_sens,
                find_cd_search_kind,find_cd,find_cd_case_sens,
                filename_fuzzy_threshold,cd_fuzzy_threshold):
                self.info_dialog_on_find.show('regular expression error',check_res)
                return

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

            search_thread=Thread(target=lambda : librer_core.find_items_in_records(range_par,
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

            last_res_check = 0
            librer_core_files_search_quant = librer_core.files_search_quant
            fnumber_librer_core_files_search_quant = fnumber(librer_core_files_search_quant)
            fnumber_records_len = fnumber(records_len)

            time_without_busy_sign=0
            while search_thread_is_alive():
                now=time()
                ######################################################################################

                change0 = self_progress_dialog_on_find_update_lab_text(0,librer_core.info_line)
                if now>last_res_check+1:
                    #change3 = self_progress_dialog_on_find_update_lab_text(3,f'Found Files: {fnumber(librer_core.find_res_quant)} ({fnumber(len(librer_core.search_record_ref.find_results))})' )
                    change3 = self_progress_dialog_on_find_update_lab_text(3,f'Found Files: {fnumber(librer_core.find_res_quant)}' )
                    last_res_check=now
                else:
                    change3 = False

                curr_files = librer_core.total_search_progress

                files_perc = curr_files * 100.0 / librer_core_files_search_quant

                self_progress_dialog_on_find_progr1var_set(librer_core.records_perc_info)
                self_progress_dialog_on_find_progr2var_set(files_perc)

                self_progress_dialog_on_find_lab_r1_config(text=fnumber(librer_core.search_record_nr) + '/' + fnumber_records_len)
                self_progress_dialog_on_find_lab_r2_config(text=fnumber(curr_files) + '/' + fnumber_librer_core_files_search_quant)

                if self.action_abort:
                    librer_core.abort()
                    #librer_core.search_record_ref.abort()
                    #break

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

            find_results_quant_sum = 0

            colname,sort_index,is_numeric,reverse,dir_code,non_dir_code = self.column_sort_last_params
            #print('\npre sort info colname:',colname,'is_numeric',is_numeric,'reverse:',reverse)
            colname_real = self.REAL_SORT_COLUMN[colname]
            #print('colname_real:',colname_real)

            for record in librer_core.records:
                find_results_quant_sum += len(record.find_results)

                record.find_items_sort(colname_real,reverse)
                #print(record.find_result)

            self.any_find_result=bool(find_results_quant_sum>0)

            abort_info = '\nSearching aborted. Resuls may be incomplete.' if self.action_abort else ''

            self.all_records_find_results_len = find_results_quant_sum
            find_results_quant_sum_format = fnumber(find_results_quant_sum)

            self.set_found()

            self.results_on_find.show('Search results',f"found: {find_results_quant_sum_format} items.\n\nNavigate search results by\n\'Find next (F3)\' & 'Find prev (Shift+F3)'\nactions." + abort_info)
            self.status_find_tooltip(f"available search results: {find_results_quant_sum_format}")

            if self.action_abort:
                self.searching_aborted = True
            else:
                self.find_params_changed=False
                self.searching_aborted = False

            if not self.searching_aborted and self.any_find_result:
                self.search_show_butt.configure(state='normal')
                self.search_save_butt.configure(state='normal')

            if self.results_on_find.res_bool:
                self.find_dialog.hide()

                if find_results_quant_sum_format:
                    self.find_result_index=-1
                    self.find_next()



    def get_child_of_name(self,item,child_name):
        self_tree = self.tree
        for child in self_tree.get_children(item):
            values = self_tree.item(child,'values')
            data=values[0]
            if data==child_name:
                return child
        return None

    def select_find_result(self,mod):
        status_to_set=None
        self_tree = self.tree
        if self.any_find_result:
            settled = False

            records_quant = len(librer_core.records_sorted)
            find_result_index_reset=False

            while not settled:
                #print('self.find_result_record_index:',self.find_result_record_index)
                #print('self.find_result_index:',self.find_result_index)

                record = librer_core.records_sorted[self.find_result_record_index]
                #print('\n'.join([sep.join(x[0]) for x in record.find_results]))
                record_find_results_len=len(record.find_results)


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
                    items_names_tuple,res_size,res_mtime=record.find_results[self.find_result_index]
                except Exception as e:
                    continue
                else:
                    settled=True
                    status_to_set=f'record find result: {self.find_result_index+1 if self.find_result_index>=0 else record_find_results_len+self.find_result_index+1} / {fnumber(record_find_results_len)} / {fnumber(self.all_records_find_results_len)}'

            #print(record_result)

            record_item = self.record_to_item[record]

            #record = self.item_to_record[record_item]

            current_item = record_item

            self.open_item(current_item)

            for item_name in items_names_tuple:
                #print('item_name:',item_name)
                child_item = self.get_child_of_name(current_item,item_name)
                #print('child_item:',child_item)

                if child_item:
                    current_item = child_item
                    self.open_item(current_item)
                    #self_tree.see(current_item)
                    self_tree.update()
                else:
                    self.info_dialog_on_main.show('cannot find item:',item_name)
                    break

            self.tree.see(current_item)
            self.tree.update()

            self_tree.selection_set(current_item)

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

    @block_actions_processing
    @gui_block
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

    @catched
    def goto_first_last_record(self,index):
        #print('goto_first_last_record',index)
        if children := self.tree_get_children():
            if next_item:=children[index]:
                self.select_and_focus(next_item)

    current_record=None
    def tree_select(self):

        item=self.tree.focus()
        parent = self.tree.parent(item)

        if item:
            record_item,record_name,subpath_list = self.get_item_record(item)
            self.current_record = record = self.item_to_record[record_item]

            record_name = self.tree.item(record_item,'text')
            image=self.tree.item(record_item,'image')

            self.status_record.configure(image = image, text = record_name,compound='left')
            self.widget_tooltip(self.status_record,record.txtinfo_basic + '\n\n(Click to show full record info)')
            #\nsingle click to unload data of current record.\n
        else:
            self.current_record = None
            self.status_record_configure('---')

    def key_press(self,event):
        #print('key_press',event.keysym)

        if self.actions_processing:
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

            if tree_focus:=tree.focus():
                tree.selection_set(tree_focus)

#################################################
    def select_and_focus(self,item):
        self.tree_see(item)
        self.tree_focus(item)

        self.tree.update()

        self.tree_sel_change(item)

    def tree_on_mouse_button_press(self,event):
        if self.actions_processing:
            self.menubar_unpost()
            self.hide_tooltip()
            self.popup_unpost()

            if self.actions_processing:
                tree=event.widget

                region = tree.identify("region", event.x, event.y)

                if region == 'separator':
                    return None

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
                    tree.selection_set(item)
                    self.tree_semi_focus()

                    self.tree_sel_change(item)

                    #prevents processing of expanding nodes
                    #return "break"

            return None

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
            #tree.configure(style='semi_focus.Treeview')

            #tree.focus(item)
            tree.see(item)
            tree.selection_set(item)

            self.tree_sel_change(item,True)
        else:
            self.sel_item = None

    @catched
    def tree_sel_change(self,item,force=False,change_status_line=True):
        self.sel_item = item

        if change_status_line :
            self.status('')

        self_tree_set_item=lambda x : self.tree_set(item,x)

        #path=self_tree_set_item('path')

        #self.sel_kind = self_tree_set_item('kind')
        self.tree_select()

    def menubar_unpost(self):
        try:
            self.menubar.unpost()
        except Exception as e:
            l_error(e)

    def context_menu_show(self,event):
        if self.actions_processing:
            tree=self.tree

            if tree.identify("region", event.x, event.y) == 'heading':
                return

            if not self.actions_processing:
                return

            tree.focus_set()
            self.tree_on_mouse_button_press(event)
            tree.update()

            item_actions_state=('disabled','normal')[self.sel_item is not None]

            pop=self.popup

            pop.delete(0,'end')

            pop_add_separator = pop.add_separator
            pop_add_cascade = pop.add_cascade
            pop_add_command = pop.add_command
            self_ico = self.ico
            state_on_records = 'normal' if librer_core.records else 'disabled'
            #state_has_cd =
            #print(state_has_cd)

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
            pop_add_separator()
            pop_add_command(label = 'Record Info ...', accelerator='Alt+Enter', command = self.record_info,image = self.ico_info,compound='left',state=state_on_records)
            pop_add_separator()
            pop_add_command(label = 'Delete record ...',command = self.delete_data_record,accelerator="Delete",image = self.ico_record_delete,compound='left',state=state_on_records)
            pop_add_separator()
            pop_add_command(label = 'Show Custom Data ...', accelerator='Enter', command = self.show_customdata,image = self.ico_empty,compound='left',state=('disabled','normal')[self.item_has_cd(self.tree.focus())])
            pop_add_separator()
            pop_add_command(label = 'Copy full path',command = self.clip_copy_full_path_with_file,accelerator='Ctrl+C',state = 'normal' if self.sel_item is not None and self.current_record else 'disabled', image = self.ico_empty,compound='left')
            pop_add_separator()
            pop_add_command(label = 'Find ...',command = self.finder_wrapper_show,accelerator="Ctrl+F",state = 'normal' if self.sel_item is not None and self.current_record else 'disabled', image = self.ico_find,compound='left')
            pop_add_command(label = 'Find next',command = self.find_next,accelerator="F3",state = 'normal' if self.sel_item is not None else 'disabled', image = self.ico_empty,compound='left')
            pop_add_command(label = 'Find prev',command = self.find_prev,accelerator="Shift+F3",state = 'normal' if self.sel_item is not None else 'disabled', image = self.ico_empty,compound='left')
            pop_add_separator()
            pop_add_command(label = 'Clear Search Results',command = self.find_clear, image = self.ico_empty,compound='left',state = 'normal' if self.any_find_result else 'disabled')
            pop_add_separator()

            pop_add_command(label = 'Exit',  command = self.exit ,image = self.ico['exit'],compound='left')

            try:
                pop.tk_popup(event.x_root, event.y_root)
            except Exception as e:
                print(e)

            pop.grab_release()

    @logwrapper
    def column_sort_click(self, tree, colname):
        prev_colname,prev_sort_index,prev_is_numeric,prev_reverse,prev_dir_code,prev_non_dir_code=self.column_sort_last_params
        reverse = not prev_reverse if colname == prev_colname else prev_reverse
        tree.heading(prev_colname, text=self.org_label[prev_colname])

        dir_code,non_dir_code = (1,0) if reverse else (0,1)

        sort_index=self.REAL_SORT_COLUMN_INDEX[colname]
        is_numeric=self.REAL_SORT_COLUMN_IS_NUMERIC[colname]
        self.column_sort_last_params=(colname,sort_index,is_numeric,reverse,dir_code,non_dir_code)

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
    @block_actions_processing
    @gui_block
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
        if self.scanning_in_progress:
            l_warning('scan_wrapper collision')
            return

        if self.scan_label_entry_var.get()=='':
            self.get_info_dialog_on_scan().show('Error. Empty label.','Set user label.')
            return

        self.scanning_in_progress=True

        compression_level = self.scan_compr_var_int.get()
        try:
            if self.scan(compression_level):
                self.scan_dialog_hide_wrapper()
        except Exception as e:
            l_error(f'scan_wraper: {e}')
            self.status(f'scan_wraper {e}')
            self.scan_dialog_hide_wrapper()

        self.scanning_in_progress=False

    def scan_dialog_hide_wrapper(self):
        self.scan_dialog.hide()
        self.tree.focus_set()
        self.tree_semi_focus()

    #prev_status_progress_text=''
    #def status_progress(self,text='',image='',do_log=False):
    #    if text != self.prev_status_progress_text:
    #        self.progress_dialog_on_scan.lab[1].configure(text=text)
    #        self.progress_dialog_on_scan.area_main.update()
    #        self.prev_status_progress_text=text

    @restore_status_line
    @logwrapper
    def scan(self,compression_level):
        #self.status('Scanning...')

        #librer_core.reset()
        #self.status_path_configure(text='')
        #self.records_show()

        path_to_scan_from_entry = abspath(self.path_to_scan_entry_var.get())
        #print('path_to_scan_from_entry:',path_to_scan_from_entry)

        #exclude_from_entry = [var.get() for var in self.exclude_entry_var.values()]

        #if res:=librer_core.set_exclude_masks(self.cfg_get(CFG_KEY_EXCLUDE_REGEXP),exclude_from_entry):
        #    self.get_info_dialog_on_scan().show('Error. Fix expression.',res)
        #    return False
        #self.cfg.set(CFG_KEY_EXCLUDE,'|'.join(exclude_from_entry))

        if not path_to_scan_from_entry:
            self.get_info_dialog_on_scan().show('Error. No paths to scan.','Add paths to scan.')
            return False

        #wryfikacja
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

                command_list = get_command_list(executable,parameters,'dummy full_file_path',True)
                if not command_list:
                    self.get_info_dialog_on_scan().show('Wrong parameters',f"Non empty and without '{PARAM_INDICATOR_SIGN}' sign\n#{e}: ({parameters})")
                    return False


        self.last_dir = path_to_scan_from_entry

        new_record = librer_core.create(self.scan_label_entry_var.get(),path_to_scan_from_entry)


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

        self_progress_dialog_on_scan.abort_single_button.configure(image=self.ico_abort,text='Abort single file',compound='left',width=15,command=lambda : self.abort_single_file(new_record))

        self_progress_dialog_on_scan.abort_single_button.pack_forget()
        #############################

        self.scan_dialog.widget.update()
        self.tooltip_message[str_self_progress_dialog_on_scan_abort_button]='If you abort at this stage,\nyou will not get any results.'
        self_progress_dialog_on_scan.abort_button.configure(image=self.ico_abort,text='Cancel',compound='left',width=15)

        self.action_abort=False
        self_progress_dialog_on_scan.abort_button.configure(state='normal')

        #librer_core.log_skipped = self.log_skipped_var.get()
        self.log_skipped = self.log_skipped_var.get()

        self_progress_dialog_on_scan.lab_l1.configure(text='CDE Total space:')
        self_progress_dialog_on_scan.lab_l2.configure(text='CDE Files number:' )

        #self_progress_dialog_on_scan_progr1var.set(10)
        #self_progress_dialog_on_scan_progr2var.set(20)

        self_progress_dialog_on_scan.show('Creating new data record (scanning)')

        update_once=True

        time_without_busy_sign=0

        self_hg_ico = self.hg_ico

        local_bytes_to_str = bytes_to_str

        self_progress_dialog_on_scan_progr1var.set(0)
        self_progress_dialog_on_scan_lab_r1_config(text='- - - -')
        self_progress_dialog_on_scan_progr2var.set(0)
        self_progress_dialog_on_scan_lab_r2_config(text='- - - -')

        wait_var=BooleanVar()
        wait_var.set(False)

        self_progress_dialog_on_scan_lab[2].configure(image='',text='')

        self_tooltip_message = self.tooltip_message
        self_configure_tooltip = self.configure_tooltip

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

            cde_sklejka_list.append('|'.join(line_list))

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

        self.cfg.set(CFG_KEY_CDE_SETTINGS,'\n'.join(cde_sklejka_list))

        check_dev = self.single_device.get()

        #############################
        scan_thread=Thread(target=lambda : new_record.scan(tuple(cde_list),check_dev),daemon=True)
        scan_thread.start()
        scan_thread_is_alive = scan_thread.is_alive

        self_ico_empty = self.ico_empty

        self_tooltip_message[str_self_progress_dialog_on_scan_abort_button]='If you abort at this stage,\nData record will not be created.'
        self_configure_tooltip(str_self_progress_dialog_on_scan_abort_button)

        self_main_after = self.main.after
        self_main_wait_variable = self.main.wait_variable
        wait_var_set = wait_var.set
        wait_var_get = wait_var.get

        self_progress_dialog_on_scan_update_lab_text = self_progress_dialog_on_scan.update_lab_text
        self_progress_dialog_on_scan_update_lab_image = self_progress_dialog_on_scan.update_lab_image

        #############################

        self.cfg.set(CFG_KEY_SINGLE_DEVICE,check_dev)
        self.cfg.write()

        #############################
        while scan_thread_is_alive():
            change0 = self_progress_dialog_on_scan_update_lab_text(0,new_record.info_line)
            change3 = self_progress_dialog_on_scan_update_lab_text(3,local_bytes_to_str(new_record.header.sum_size) )
            change4 = self_progress_dialog_on_scan_update_lab_text(4,'%s files' % fnumber(new_record.header.quant_files) )

            now=time()

            if change0 or change3 or change4:
                time_without_busy_sign=now

                if update_once:
                    update_once=False
                    self_progress_dialog_on_scan_update_lab_image(2,self_ico_empty)
                    self_progress_dialog_on_scan_update_lab_text(1,'')
            else :
                if now>time_without_busy_sign+1.0:
                    self_progress_dialog_on_scan_update_lab_image(2,self.get_hg_ico())
                    self_progress_dialog_on_scan_update_lab_text(1,new_record.info_line_current)

                    if len(new_record.info_line_current)>50:
                        self_progress_dialog_on_scan_update_lab_text(1,f'...{new_record.info_line_current[-50:]}')
                    else:
                        self_progress_dialog_on_scan_update_lab_text(1,new_record.info_line_current)

                    update_once=True

            self_progress_dialog_on_scan_area_main_update()

            if self.action_abort:
                new_record.abort()
                break

            self_main_after(25,lambda : wait_var_set(not wait_var_get()))
            self_main_wait_variable(wait_var)

        self_progress_dialog_on_scan_update_lab_text(1,'')
        self_progress_dialog_on_scan_update_lab_image(2,self_ico_empty)
        self_progress_dialog_on_scan_update_lab_text(3,'')
        self_progress_dialog_on_scan_update_lab_text(4,'')

        scan_thread.join()

        if self.action_abort:
            self_progress_dialog_on_scan.hide(True)
            del new_record

            return False

        if any_cde_enabled:
            self_progress_dialog_on_scan.widget.title('Creating new data record (Custom Data Extraction)')
            self_progress_dialog_on_scan.abort_single_button.pack(side='left', anchor='center',padx=5,pady=5)
            self_progress_dialog_on_scan.abort_single_button.configure(state='normal')
            self_progress_dialog_on_scan.abort_button.configure(image=self.ico_abort,text='Abort',compound='left',width=15,state='normal')

            self_tooltip_message[str_self_progress_dialog_on_scan_abort_button]='If you abort at this stage,\nCustom Data will be incomplete.'
            self_tooltip_message[str_self_progress_dialog_on_scan_abort_single_button]='Use if CDE has no timeout set and seems like stuck.\nCD of only single file will be incomplete.\nCDE will continue.'

            #########################################################################################
            cd_thread=Thread(target=new_record.extract_customdata_threaded,daemon=True)
            cd_thread.start()

            cd_thread_is_alive = cd_thread.is_alive

            self_progress_dialog_on_scan_progr1var_set = self_progress_dialog_on_scan_progr1var.set
            self_progress_dialog_on_scan_progr2var_set = self_progress_dialog_on_scan_progr2var.set

            while cd_thread_is_alive():
                change0 = self_progress_dialog_on_scan_update_lab_text(0,new_record.info_line)
                change3 = self_progress_dialog_on_scan_update_lab_text(3,'Extracted Custom Data: ' + local_bytes_to_str(new_record.header.files_cde_size_extracted) )
                change4 = self_progress_dialog_on_scan_update_lab_text(4,'Extraction Errors : ' + fnumber(new_record.header.files_cde_errors_quant_all) )

                files_q = new_record.header.files_cde_quant
                files_perc = files_q * 100.0 / new_record.header.files_cde_quant_sum if new_record.header.files_cde_quant_sum else 0

                files_size = new_record.header.files_cde_size
                files_size_perc = files_size * 100.0 / new_record.header.files_cde_size_sum if new_record.header.files_cde_size_sum else 0

                self_progress_dialog_on_scan_progr1var_set(files_size_perc)
                self_progress_dialog_on_scan_progr2var_set(files_perc)

                self_progress_dialog_on_scan_lab_r1_config(text=local_bytes_to_str(new_record.header.files_cde_size) + '/' + local_bytes_to_str(new_record.header.files_cde_size_sum))
                self_progress_dialog_on_scan_lab_r2_config(text=fnumber(files_q) + '/' + fnumber(new_record.header.files_cde_quant_sum))

                if self.action_abort:
                    new_record.abort()
                    break

                now=time()

                if change0 or change3 or change4:
                    time_without_busy_sign=now

                    if update_once:
                        update_once=False
                        self_progress_dialog_on_scan_update_lab_image(2,self_ico_empty)
                        self_progress_dialog_on_scan_update_lab_text(1,'')
                else :
                    if now>time_without_busy_sign+1.0:
                        self_progress_dialog_on_scan_update_lab_image(2,self.get_hg_ico())

                        if len(new_record.info_line_current)>50:
                            self_progress_dialog_on_scan_update_lab_text(1,f'...{new_record.info_line_current[-50:]}')
                        else:
                            self_progress_dialog_on_scan_update_lab_text(1,new_record.info_line_current)

                        update_once=True

                self_main_after(25,lambda : wait_var_set(not wait_var_get()))
                self_main_wait_variable(wait_var)

            cd_thread.join()
            #########################################################################################

        self_progress_dialog_on_scan_update_lab_text(1,'')
        self_progress_dialog_on_scan_update_lab_image(2,self_ico_empty)
        self_progress_dialog_on_scan_update_lab_text(3,'')
        self_progress_dialog_on_scan_update_lab_text(4,'')

        #self_progress_dialog_on_scan.abort_single_button.configure(state='disabled')
        #self_progress_dialog_on_scan.abort_button.configure(state='disabled')

        ##################################
        pack_thread=Thread(target=new_record.pack_data,daemon=True)
        pack_thread.start()
        pack_thread_is_alive = pack_thread.is_alive
        while pack_thread_is_alive():
            change0 = self_progress_dialog_on_scan_update_lab_text(0,new_record.info_line)
            self_progress_dialog_on_scan_update_lab_image(2,self.get_hg_ico())
            self_main_after(25,lambda : wait_var_set(not wait_var_get()))
            self_main_wait_variable(wait_var)
        pack_thread.join()
        self_progress_dialog_on_scan_update_lab_image(2,self_ico_empty)

        ##################################
        save_thread=Thread(target=lambda : new_record.save(compression_level=compression_level),daemon=True)
        save_thread.start()
        save_thread_is_alive = save_thread.is_alive
        while save_thread_is_alive():
            change0 = self_progress_dialog_on_scan_update_lab_text(0,new_record.info_line)
            self_progress_dialog_on_scan_update_lab_image(2,self.get_hg_ico())
            self_main_after(25,lambda : wait_var_set(not wait_var_get()))
            self_main_wait_variable(wait_var)
        save_thread.join()
        self_progress_dialog_on_scan_update_lab_image(2,self_ico_empty)
        ##################################

        self.single_record_show(new_record)

        self_progress_dialog_on_scan.hide(True)

        return True

    def delete_data_record(self):
        if self.actions_processing:
            if self.current_record:
                label = self.current_record.header.label
                path = self.current_record.header.scan_path
                creation_time = self.current_record.header.creation_time

                dialog = self.get_delete_record_dialog()

                dialog.show('Delete selected data record ?',self.current_record.txtinfo_short)

                if dialog.res_bool:
                    record_item = self.record_to_item[self.current_record]
                    self.tree.delete(record_item)

                    del self.record_to_item[self.current_record]
                    del self.item_to_record[record_item]

                    res=librer_core.delete_record(self.current_record)
                    l_info(f'deleted file:{res}')

                    self.status_record_configure('')
                    if remaining_records := self.tree.get_children():
                        if new_sel_record := remaining_records[0]:
                            self.tree.selection_set(new_sel_record)
                            self.tree.focus(new_sel_record)

                        self.tree_semi_focus()
                    self.tree.focus_set()

    def scan_dialog_show(self):
        #self.exclude_mask_update()

        dialog = self.get_scan_dialog()

        self.status("Opening dialog ...")
        e=0
        sklejka_settings = self.cfg.get(CFG_KEY_CDE_SETTINGS)

        do_clear_settings = False
        if sklejka_settings:
            for e_section in self.cfg.get(CFG_KEY_CDE_SETTINGS).split('\n'):
                try:
                    v1,v2,v3,v4,v5,v6,v7,v8,v9 = e_section  .split('|')

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
            self.cfg.set(CFG_KEY_CDE_SETTINGS,'')
            self.cfg.write()

        for e in range(self.CDE_ENTRIES_MAX):
            self.use_checkbutton_mod(e,False)

        self.configure_scan_button()

        dialog.do_command_after_show=lambda : self.status("")
        dialog.show()

    def exclude_regexp_set(self):
        self.cfg.set(CFG_KEY_EXCLUDE_REGEXP,self.exclude_regexp_scan.get())

    def exclude_mask_update(self) :
        for subframe in self.exclude_frames:
            subframe.destroy()

        self.exclude_frames=[]
        self.exclude_entry_var={}

        row=0

        for entry in self.cfg.get(CFG_KEY_EXCLUDE).split('|'):
            if entry:
                (frame:=Frame(self.exclude_frame,bg=self.bg_color)).grid(row=row,column=0,sticky='news',columnspan=3)
                self.exclude_frames.append(frame)

                self.exclude_entry_var[row]=StringVar(value=entry)
                Entry(frame,textvariable=self.exclude_entry_var[row]).pack(side='left',expand=1,fill='both',pady=1,padx=(2,0))

                remove_expression_button=Button(frame,image=self.ico['delete'],command=lambda entrypar=entry: self.exclude_mask_remove(entrypar),width=3)
                remove_expression_button.pack(side='right',padx=2,pady=1,fill='y')

                self.widget_tooltip(remove_expression_button,'Remove expression from list.')

                row+=1

        if row:
            self.exclude_scroll_frame.pack(fill='both',expand=True,side='top')
        else:
            self.exclude_scroll_frame.pack_forget()

    def set_dev_to_scan_menu(self):
        self.drives_menu.delete(0,'end')

        templ = "%-17s %8s %8s %8s %5s%% %9s  %s"
        #print(templ % ("Device", "Total", "Used", "Free", "Use ", "Type","Mount"))
        for part in disk_partitions(all=False):
            if windows:
                if 'cdrom' in part.opts or part.fstype == '':
                    # skip cd-rom drives with no disk in it; they may raise
                    # ENOENT, pop-up a Windows GUI error for a non-ready
                    # partition or just hang.
                    continue
            usage = disk_usage(part.mountpoint)
            if part.fstype != 'squashfs':
                #print(templ % (
                #    part.device,
                #    bytes_to_str(usage.total),
                #    bytes_to_str(usage.used),
                #    bytes_to_str(usage.free),
                #    int(usage.percent),
                #    part.fstype,
                #    part.mountpoint))

                self.drives_menu.add_command(label=part.mountpoint,command = lambda dev=part.mountpoint : self.set_dev_to_scan(dev) )

    def set_dev_to_scan(self,dev):
        self.path_to_scan_entry_var.set(dev)
        self.scan_label_entry_var.set(dev)

    def set_path_to_scan(self):
        initialdir = self.last_dir if self.last_dir else self.cwd
        if res:=askdirectory(title='Select Directory',initialdir=initialdir,parent=self.scan_dialog.area_main):
            self.last_dir = res
            self.path_to_scan_entry_var.set(normpath(abspath(res)))

    def threaded_simple_run(self,command_list,shell):
        output_list_append = self.output_list.append

        try:
            self.subprocess = Popen(command_list, stdout=PIPE, stderr=STDOUT,shell=shell,text=True)
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

                output_list_append(line.rstrip('\n\r'))

                if not line and subprocess_poll() is not None:
                    self.returncode[0]=self.subprocess.returncode
                    break

        self.subprocess = True
        sys.exit(0) #thread

    def abort_single_file(self,record):
        record.abort_single_file_cde=True
        print('abort_single_file')

    def kill_test(self):
        if self.subprocess and self.subprocess!=True:
            self.output_list.append('Killing.')
            print(f'{self.subprocess.pid=}',flush = True)
            rec_kill(self.subprocess.pid)

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

            command_list = get_command_list(executable,parameters,full_file_path,shell)
            if not command_list:
                self.get_info_dialog_on_scan().show('Wrong parameters string',f"Non empty and without '{PARAM_INDICATOR_SIGN}' sign")
                return

            info = ' '.join(command_list) + '\n' + ( ('\ntimeout:' + str(timeout_int)) if timeout_int else '') + f'\nshell:{"Yes" if shell else "No"}'

            ask_dialog = self.get_text_ask_dialog_on_scan()
            simple_progress_dialog_scan = self.get_simple_progress_dialog_on_scan()

            ask_dialog.show('Test selected Custom Data Extractor on selected file ?',info)

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

                test_thread = Thread(target = lambda: self.threaded_simple_run(command_list,shell),daemon=True)

                simple_progress_dialog_scan.command_on_close=self.kill_test

                #simple_progress_dialog_scan.command_on_close=self.kill_test
                test_thread.start()

                simple_progress_dialog_scan.show('Testing selected Custom Data Extractor')

                timeout_val=time()+float(timeout_int) if timeout_int else None

                simple_progress_dialog_scan_update_lab_text = simple_progress_dialog_scan.update_lab_text
                simple_progress_dialog_scan_update_lab_image = simple_progress_dialog_scan.update_lab_image

                while test_thread.is_alive():
                    simple_progress_dialog_scan_update_lab_image(2,self.get_hg_ico())

                    if timeout_val :
                        time_left = timeout_val-time()
                        if time_left>0:
                            simple_progress_dialog_scan_update_lab_text(0,f'timeout: {int(time_left)}')
                        else:
                            simple_progress_dialog_scan_update_lab_text(0,'Timeout')
                            self.output_list.append(f'Timeout {timeout_int}s.')
                            self.kill_test()

                    self_main_after(25,lambda : wait_var_set(not wait_var_get()))
                    self_main_wait_variable(wait_var)

                test_thread.join()

                simple_progress_dialog_scan.hide(True)

                output = '\n'.join(self.output_list)

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
        if res:=askopenfilename(title='Select File',initialdir=initialdir,parent=self.scan_dialog.area_main,filetypes=(("Bat Files","*.bat"),("Executable Files","*.exe"),("All Files","*.*")) if windows else (("Bash Files","*.sh"),("All Files","*.*")) ):
            self.last_dir=dirname(res)

            expr = normpath(abspath(res))
            self.CDE_executable_var_list[e].set(expr)

    def exclude_mask_add_dir(self):
        initialdir = self.last_dir if self.last_dir else self.cwd
        if res:=askdirectory(title='Select Directory',initialdir=initialdir,parent=self.scan_dialog.area_main):
            self.last_dir=res
            expr = normpath(abspath(res)) + (".*" if self.exclude_regexp_scan.get() else "*")
            self.exclude_mask_string(expr)

    def exclude_mask_add_dialog(self):
        self.exclude_dialog_on_scan.show('Specify Exclude expression','expression:','')
        confirmed=self.exclude_dialog_on_scan.res_bool
        mask=self.exclude_dialog_on_scan.res_str

        if confirmed:
            self.exclude_mask_string(mask)

    def exclude_mask_string(self,mask):
        orglist=self.cfg.get(CFG_KEY_EXCLUDE).split('|')
        orglist.append(mask)
        self.cfg.set(CFG_KEY_EXCLUDE,'|'.join(orglist))
        self.exclude_mask_update()

    def exclude_mask_remove(self,mask) :
        orglist=self.cfg.get(CFG_KEY_EXCLUDE).split('|')
        orglist.remove(mask)
        if '' in orglist:
            orglist.remove('')
        self.cfg.set(CFG_KEY_EXCLUDE,'|'.join(orglist))
        self.exclude_mask_update()

    @restore_status_line
    @block_actions_processing
    @gui_block
    def access_filestructure(self,record):
        self.hide_tooltip()
        self.popup_unpost()
        self.status('loading filestructure ...')
        self.main.update()
        record.decompress_filestructure()

    @restore_status_line
    @block_actions_processing
    @gui_block
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

    @block_actions_processing
    @gui_block
    def open_item(self,item=None):
        tree=self.tree

        if not item:
            item=tree.focus()

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

            #print('subpath_list',subpath_list)

            record = self.item_to_record[record_item]

            #try:
            #    print(record.find_results[0])
            #except Exception as e:
            #    print('totu:',e)
            self_item_to_data = self.item_to_data

            if tree.tag_has(self.RECORD_RAW,item):
                self.access_filestructure(record)
                self_item_to_data[item] = record.filestructure
                self.tree.item(item,tags=self.RECORD, image=self.ico_record_cd if record.has_cd() else self.ico_record)
                self.tree_select() #tylko dla aktualizacja ikony

            top_data_tuple = self_item_to_data[item]

            (top_entry_name_nr,top_code,top_size,top_mtime) = top_data_tuple[0:4]

            top_is_dir,top_is_file,top_is_symlink,top_is_bind,top_has_cd,top_has_files,top_cd_ok,top_has_crc = LUT_decode_loc[top_code]

            record_get_file_name = record.get_file_name

            if top_has_files:
                for data_tuple in top_data_tuple[4]:

                    (entry_name_nr,code,size,mtime) = data_tuple[0:4]

                    entry_name = record_get_file_name(entry_name_nr)

                    entry_subpath_tuple = tuple(subpath_list + [entry_name])
                    #print('entry_subpath_tuple',entry_subpath_tuple)

                    is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc = LUT_decode_loc[code]

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

                    if has_crc:
                        pass
                    kind = self_DIR if is_dir else self_FILE

                    image = (self.ico_folder_error if size==-1 else self.ico_folder_link if is_symlink or is_bind else self.ico_folder) if is_dir else (self.ico_cd_ok if cd_ok else self.ico_cd_error) if has_cd and not has_crc else (self.ico_cd_ok_crc if cd_ok else self.ico_cd_error_crc) if has_cd and has_crc else self.ico_crc if has_crc else self.ico_empty

                    if is_symlink or is_bind:
                        tags=self_SYMLINK
                    else:
                        tags=''
                        if record.find_results:
                            for find_result in record.find_results:
                                if find_result[0]==entry_subpath_tuple:
                                    tags=self.FOUND
                                    break

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

        #tree.item(item, open=True)
    def get_record_raw_icon(self,record):
        return self.ico_record_raw_cd if record.has_cd() else self.ico_record_raw

    @block_actions_processing
    @gui_block
    @logwrapper
    def single_record_show(self,record):
        size=record.header.sum_size

        #('data','record','opened','path','size','size_h','ctime','ctime_h','kind')
        values = (record.header.label,record.header.label,0,record.header.scan_path,size,bytes_to_str(size),record.header.creation_time,strftime('%Y/%m/%d %H:%M:%S',localtime_catched(record.header.creation_time)),self.RECORD)

        record_item=self.tree.insert('','end',iid=None,values=values,open=False,text=record.header.label,image=self.get_record_raw_icon(record),tags=self.RECORD_RAW)
        self.tree.insert(record_item,'end',text='dummy') #dummy_sub_item

        self.tree_sort_item(None)

        self.item_to_record[record_item]=record
        self.record_to_item[record]=record_item

        #self.item_to_data[record_item] = record.filestructure

        self.tree.focus(record_item)
        self.tree.selection_set(record_item)
        self.tree.see(record_item)

        records_len=len(librer_core.records)
        self.status_records_all_configure(f'Records:{records_len}')

        sum_size=0
        quant_files=0
        for record_temp in librer_core.records:
            sum_size+=record_temp.header.sum_size
            quant_files+=record_temp.header.quant_files

        self.widget_tooltip(self.status_records_all,f'All records in repository : {records_len}\nSum data size         : {bytes_to_str(sum_size)}\nSum files quantity    : {fnumber(quant_files)}\n\nClick to unload (free memory) data of selected record\nDouble click to unload data of all records.')

        self.main_update()

    @block_actions_processing
    @gui_block
    @logwrapper
    def records_show(self):
        self.menu_disable()

        self_tree = self.tree

        self_tree.delete(*self_tree.get_children())

        self.item_to_record={}
        self.record_to_item={}

        self.item_to_data={}

        for record in sorted(librer_core.records,key=lambda x : x.header.creation_time):
            self.single_record_show(record)

        self.menu_enable()

        #self_status=self.status=self.status_progress

        self.status('')

        #if children := self_tree.get_children():
        #    self_tree.focus(children[0])

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
            self.main.clipboard_append(record.header.scan_path + sep + sep.join(subpath_list))

            self.status('Full path copied to clipboard')

    @logwrapper
    def clip_copy(self,what):
        self.main.clipboard_clear()
        self.main.clipboard_append(what)
        self.status('Copied to clipboard: "%s"' % what)

    def double_left_button(self,event):
        if self.actions_processing:
            tree=event.widget
            if tree.identify("region", event.x, event.y) != 'heading':
                if item:=tree.identify('item',event.x,event.y):
                    if self.tree.tag_has(self.RECORD,item) or self.tree.tag_has(self.RECORD_RAW,item):
                        self.record_info()
                    else:
                        self.main.after_idle(self.show_customdata)

        return "break"

    def show_customdata(self):
        if self.actions_processing:
            item=self.tree.focus()
            if item:
                try:
                    if self.tree.tag_has(self.RECORD,item) or self.tree.tag_has(self.RECORD_RAW,item):
                        self.record_info()
                    else:
                        record_item,record_name,subpath_list = self.get_item_record(item)
                        record = self.item_to_record[record_item]

                        if item in self.item_to_data: #dla rekordu nie spelnione
                            data_tuple = self.item_to_data[item]
                            (entry_name,code,size,mtime) = data_tuple[0:4]

                            is_dir,is_file,is_symlink,is_bind,has_cd,has_files,cd_ok,has_crc = LUT_decode[code]

                            if has_cd: #wiec nie has_files
                                cd_index = data_tuple[4]

                                self.access_customdata(record)

                                cd_field = record.customdata[cd_index]
                                if cd_data := cd_field[2]:
                                    rule_nr=cd_field[0]
                                    returncode=cd_field[1]

                                    expressions,use_smin,smin_int,use_smax,smax_int,executable,parameters,shell,timeout,crc = record.header.cde_list[rule_nr]

                                    file_path = record.header.scan_path + sep + sep.join(subpath_list)

                                    cd_txt = cd_data
                                    self.get_text_info_dialog().show(f'Custom Data of: {file_path}',cd_txt,uplabel_text=f"CDE command:'{executable} {parameters}' | shell:{shell} {timeout if timeout else ''} returncode:{returncode}")
                                    return

                            self.info_dialog_on_main.show('Information','No Custom data.')

                except Exception as e:
                    self.info_dialog_on_main.show(e)

    def record_info(self):
        if self.actions_processing:
            if self.current_record:
                time_info = strftime('%Y/%m/%d %H:%M:%S',localtime_catched(self.current_record.header.creation_time))
                self.get_text_info_dialog().show('Record Info.',self.current_record.txtinfo)

    @block_actions_processing
    @gui_block
    @logwrapper
    def unload_recod(self,record=None):
        if not record:
            record = self.current_record

        if record:
            record_item = self.record_to_item[record]

            self.tree.delete(*self.tree.get_children(record_item))
            self.tree.insert(record_item,'end',text='dummy') #dummy_sub_item
            self.tree.set(record_item,'opened','0')
            self.tree.item(record_item, open=False)

            record.unload_filestructure()
            record.unload_customdata()
            self.tree.item(record_item, image=self.get_record_raw_icon(record),tags=self.RECORD_RAW)
            self.tree.focus(record_item)
            self.tree.selection_set(record_item)
            self.tree_select()

    @block_actions_processing
    @gui_block
    @logwrapper
    def unload_all_recods(self):
        for record in librer_core.records:
            self.unload_recod(record)

    #@logwrapper
    #def tree_action(self,item):
    #    tree=self.tree
    #    try:
    #        record_item,record_name,subpath_list = self.get_item_record(item)
    #        record = self.item_to_record[record_item]

            #kind = tree.set(item,'kind')
            #opened = tree.item(item)['open']
            #if kind == self.DIR :
            #    pass
                #if not opened:
                #    self.open_item(item)
            #elif kind == self.RECORD :

                #if opened:
                #    self.open_item(item)

    #    except Exception as e:
    #        print('tree_action',e)

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

        LIBRER_FILE = normpath(__file__)
        LIBRER_DIR = dirname(LIBRER_FILE)

        LIBRER_EXECUTABLE_FILE = normpath(abspath(sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]))
        LIBRER_EXECUTABLE_DIR = dirname(LIBRER_EXECUTABLE_FILE)
        DATA_DIR = sep.join([LIBRER_EXECUTABLE_DIR,'data'])
        LOG_DIR = sep.join([LIBRER_EXECUTABLE_DIR,'logs'])

        #######################################################################

        VER_TIMESTAMP = get_ver_timestamp()

        LOG_DIR = sep.join([LIBRER_EXECUTABLE_DIR,"logs"])

        log_file = strftime('%Y_%m_%d_%H_%M_%S',localtime_catched(time())) +'.txt'
        log=abspath(LOG_DIR + sep + log_file)

        Path(LOG_DIR).mkdir(parents=True,exist_ok=True)

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

        #if p_args.csv:
        #    signal(SIGINT, lambda a, k : librer_core.handle_sigint())

        #    librer_core.set_paths_to_scan(p_args.paths)

        #    if p_args.exclude:
        #        set_exclude_masks_res=librer_core.set_exclude_masks(False,p_args.exclude)
        #    elif p_args.exclude_regexp:
        #        set_exclude_masks_res=librer_core.set_exclude_masks(True,p_args.exclude_regexp)
        #    else:
        #        set_exclude_masks_res=librer_core.set_exclude_masks(False,[])

        #    if set_exclude_masks_res:
        #        print(set_exclude_masks_res)
        #        sys.exit(2)

            #run_scan_thread=Thread(target=librer_core.scan,daemon=True)
            #run_scan_thread.start()

            #while run_scan_thread.is_alive():
            #    print('Scanning ...', librer_core.info_counter,end='\r')
            #    sleep(0.04)

            #run_scan_thread.join()

            #run_crc_thread=Thread(target=librer_core.crc_calc,daemon=True)
            #run_crc_thread.start()

            #while run_crc_thread.is_alive():
            #    print(f'crc_calc...{librer_core.info_files_done}/{librer_core.info_total}                 ',end='\r')
            #    sleep(0.04)

            #run_crc_thread.join()
            #print('')
            #librer_core.write_csv(p_args.csv[0])

        #    print('Done')

        #else:

    except Exception as e_main:
        print(e_main)
        l_error(e_main)
        sys.exit(1)
