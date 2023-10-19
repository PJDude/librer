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

from fnmatch import fnmatch
from shutil import rmtree

from time import sleep
from time import strftime
from time import localtime
from time import time

from os import sep
from os import stat
from os import scandir
from os import readlink
from os import rmdir
from os import system
from os import getcwd
from os import name as os_name

windows = bool(os_name=='nt')

if windows:
    from os import startfile

from os.path import abspath
from os.path import normpath
from os.path import dirname
from os.path import join as path_join
from os.path import isfile as path_isfile
from os.path import split as path_split
from os.path import exists as path_exists

from platform import node
from pathlib import Path
from re import search

from signal import signal
from signal import SIGINT

from configparser import ConfigParser
from subprocess import Popen

from tkinter import Tk
from tkinter import Toplevel
from tkinter import PhotoImage
from tkinter import Menu
from tkinter import PanedWindow
from tkinter import Label
from tkinter import LabelFrame
from tkinter import Frame
from tkinter import StringVar
from tkinter import BooleanVar

from tkinter.ttk import Checkbutton
from tkinter.ttk import Treeview
from tkinter.ttk import Scrollbar
from tkinter.ttk import Button
from tkinter.ttk import Entry
from tkinter.ttk import Combobox
from tkinter.ttk import Style

from tkinter.filedialog import askdirectory
from tkinter.filedialog import asksaveasfilename

from collections import defaultdict
from threading import Thread
from traceback import format_stack

import sys
import logging

import core
import console
import dialogs

from librer_images import librer_image

#l_debug = logging.debug
l_info = logging.info
l_warning = logging.warning
l_error = logging.error

#log_levels={logging.DEBUG:'DEBUG',logging.INFO:'INFO'}

core_bytes_to_str=core.bytes_to_str

###########################################################################################################################################

CFG_KEY_FULL_CRC='show_full_crc'
CFG_KEY_FULL_PATHS='show_full_paths'
CFG_KEY_CROSS_MODE='cross_mode'
CFG_KEY_REL_SYMLINKS='relative_symlinks'

CFG_KEY_USE_REG_EXPR='use_reg_expr'
CFG_KEY_EXCLUDE_REGEXP='excluderegexpp'

CFG_ERASE_EMPTY_DIRS='erase_empty_dirs'
CFG_ABORT_ON_ERROR='abort_on_error'
CFG_SEND_TO_TRASH='send_to_trash'
CFG_CONFIRM_SHOW_CRCSIZE='confirm_show_crcsize'
CFG_CONFIRM_SHOW_LINKSTARGETS='confirm_show_links_targets'

CFG_ALLOW_DELETE_ALL='allow_delete_all'
CFG_SKIP_INCORRECT_GROUPS='skip_incorrect_groups'
CFG_ALLOW_DELETE_NON_DUPLICATES='allow_delete_non_duplicates'

CFG_KEY_EXCLUDE='exclude'
CFG_KEY_WRAPPER_FILE = 'file_open_wrapper'
CFG_KEY_WRAPPER_FOLDERS = 'folders_open_wrapper'
CFG_KEY_WRAPPER_FOLDERS_PARAMS = 'folders_open_wrapper_params'

cfg_defaults={
    CFG_KEY_FULL_CRC:False,
    CFG_KEY_FULL_PATHS:False,
    CFG_KEY_CROSS_MODE:False,
    CFG_KEY_REL_SYMLINKS:True,
    CFG_KEY_USE_REG_EXPR:False,
    CFG_KEY_EXCLUDE_REGEXP:False,
    CFG_ERASE_EMPTY_DIRS:True,
    CFG_ABORT_ON_ERROR:True,
    CFG_SEND_TO_TRASH:True,
    CFG_CONFIRM_SHOW_CRCSIZE:False,
    CFG_CONFIRM_SHOW_LINKSTARGETS:True,
    CFG_ALLOW_DELETE_ALL:False,
    CFG_SKIP_INCORRECT_GROUPS:True,
    CFG_ALLOW_DELETE_NON_DUPLICATES:False,
    CFG_KEY_WRAPPER_FILE:'',
    CFG_KEY_WRAPPER_FOLDERS:'',
    CFG_KEY_WRAPPER_FOLDERS_PARAMS:'2',
    CFG_KEY_EXCLUDE:''
}

#DELETE=0
#SOFTLINK=1
#HARDLINK=2

#NAME={DELETE:'Delete',SOFTLINK:'Softlink',HARDLINK:'Hardlink'}

HOMEPAGE='https://github.com/PJDude/librer'

#DE_NANO = 1_000_000_000

class Config:
    def __init__(self,config_dir):
        #l_debug('Initializing config: %s', config_dir)
        self.config = ConfigParser()
        self.config.add_section('main')
        self.config.add_section('geometry')

        self.path = config_dir
        self.file = self.path + '/cfg.ini'

    def write(self):
        l_info('writing config')
        Path(self.path).mkdir(parents=True,exist_ok=True)
        with open(self.file, 'w', encoding='ASCII') as configfile:
            self.config.write(configfile)

    def read(self):
        l_info('reading config')
        if path_isfile(self.file):
            try:
                with open(self.file, 'r', encoding='ASCII') as configfile:
                    self.config.read_file(configfile)
            except Exception as e:
                l_error(e)
        else:
            l_warning('no config file: %s',self.file)

    def set(self,key,val,section='main'):
        self.config.set(section,key,str(val))

    def set_bool(self,key,val,section='main'):
        self.config.set(section,key,('0','1')[val])

    def get(self,key,default='',section='main'):
        try:
            res=self.config.get(section,key)
        except Exception as e:
            l_warning('gettting config key: %s',key)
            l_warning(e)
            res=default
            if not res:
                res=cfg_defaults[key]

            self.set(key,res,section=section)

        return str(res)

    def get_bool(self,key,section='main'):
        try:
            res=self.config.get(section,key)
            return res=='1'

        except Exception as e:
            l_warning('gettting config key: %s',key)
            l_warning(e)
            res=cfg_defaults[key]
            self.set_bool(key,res,section=section)
            return res

###########################################################

class Gui:
    sel_path_full=''
    sel_record=''
    tagged=set()

    actions_processing=False

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

    #######################################################################
    action_abort=False

    def progress_dialog_abort(self):
        self.status("Abort pressed ...")
        l_info("Abort pressed ...")
        self.action_abort=True

    other_tree={}

    def handle_sigint(self):
        self.status("Received SIGINT signal")
        l_warning("Received SIGINT signal")
        self.action_abort=True

    def __init__(self,cwd,paths_to_add=None,exclude=None,exclude_regexp=None,norun=None):
        self.cwd=cwd
        self.last_dir=self.cwd

        self.cfg = Config(CONFIG_DIR)
        self.cfg.read()

        self.cfg_get_bool=self.cfg.get_bool

        self.paths_to_scan_frames=[]
        self.exclude_frames=[]

        self.paths_to_scan_from_dialog=[]

        signal(SIGINT, lambda a, k : self.handle_sigint())

        self.two_dots_condition = lambda path : Path(path)!=Path(path).parent if path else False

        self.tagged_add=self.tagged.add
        self.tagged_discard=self.tagged.discard

        self.current_folder_items_tagged_discard=self.current_folder_items_tagged.discard
        self.current_folder_items_tagged_add=self.current_folder_items_tagged.add

        ####################################################################
        self.main = Tk()
        self_main = self.main

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

        #self.icon_nr={ i:self_ico[str(i+1)] for i in range(8) }

        hg_indices=('01','02','03','04','05','06','07','08', '11','12','13','14','15','16','17','18', '21','22','23','24','25','26','27','28', '31','32','33','34','35','36','37','38',)
        self.hg_ico={ i:self_ico[str('hg'+j)] for i,j in enumerate(hg_indices) }

        #self.icon_softlink_target=self_ico['softlink_target']
        #self.icon_softlink_dir_target=self_ico['softlink_dir_target']

        self_main.iconphoto(False, self_ico['librer'])

        self.RECORD='R'

        self.MARK='M'
        self.DIR='D'
        self.DIRLINK='L'
        self.LINK='l'
        self.FILE='F'
        #self.FILELINK='l'
        #self.SINGLE='5'
        self.SINGLEHARDLINKED='H'
        self.CRC='C'

        self_main_bind = self_main.bind

        self_main_bind('<KeyPress-F2>', lambda event : self.settings_dialog.show())
        self_main_bind('<KeyPress-F1>', lambda event : self.aboout_dialog.show())
        self_main_bind('<KeyPress-s>', lambda event : self.scan_dialog_show())
        self_main_bind('<KeyPress-S>', lambda event : self.scan_dialog_show())

        #self_main_bind('<KeyPress>', self.main_key_press)

        #self.defaultFont = font.nametofont("TkDefaultFont")
        #self.defaultFont.configure(family="Monospace regular",size=8,weight=font.BOLD)
        #self.defaultFont.configure(family="Monospace regular",size=10)
        #self_main.option_add("*Font", self.defaultFont)

        self.tooltip = Toplevel(self_main)
        self.tooltip_withdraw = self.tooltip.withdraw
        self.tooltip_withdraw()
        self.tooltip_deiconify = self.tooltip.deiconify
        self.tooltip_wm_geometry = self.tooltip.wm_geometry

        self.tooltip.wm_overrideredirect(True)
        self.tooltip_lab=Label(self.tooltip, justify='left', background="#ffffe0", relief='solid', borderwidth=0, wraplength = 1200)
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

        style_configure("TCheckbutton", background = self.bg_color)
        style_configure("TCombobox", borderwidth=2,highlightthickness=1,bordercolor='darkgray')

        style_map = style.map

        style_map("TButton",  relief=[('disabled',"flat"),('',"raised")] )
        style_map("TButton",  fg=[('disabled',"gray"),('',"black")] )

        style_map("Treeview.Heading",  relief=[('','raised')] )
        style_configure("Treeview",rowheight=18)

        bg_focus='#90DD90'
        bg_focus_off='#90AA90'
        bg_sel='#AAAAAA'

        style_map('Treeview', background=[('focus',bg_focus),('selected',bg_sel),('','white')])

        style_map('semi_focus.Treeview', background=[('focus',bg_focus),('selected',bg_focus_off),('','white')])
        style_map('no_focus.Treeview', background=[('focus',bg_focus),('selected',bg_sel),('','white')])
        #style_map('no_focus.Treeview', background=[('focus',bg_sel),('selected',bg_sel),('','white')])

        #works but not for every theme
        #style_configure("Treeview", fieldbackground=self.bg_color)

        #######################################################################
        self.menubar = Menu(self_main,bg=self.bg_color)
        self_main.config(menu=self.menubar)
        #######################################################################

        self.tooltip_message={}

        self.menubar_config = self.menubar.config
        self.menubar_cget = self.menubar.cget

        self.menubar_entryconfig = self.menubar.entryconfig
        self.menubar_norm = lambda x : self.menubar_entryconfig(x, state="normal")
        self.menubar_disable = lambda x : self.menubar_entryconfig(x, state="disabled")

        self.paned = PanedWindow(self_main,orient='vertical',relief='sunken',showhandle=0,bd=0,bg=self.bg_color,sashwidth=2,sashrelief='flat')
        self.paned.pack(fill='both',expand=1)

        frame_groups = Frame(self.paned,bg=self.bg_color)
        self.paned.add(frame_groups)
        frame_folder = Frame(self.paned,bg=self.bg_color)
        #self.paned.add(frame_folder)

        frame_groups.grid_columnconfigure(0, weight=1)
        frame_groups.grid_rowconfigure(0, weight=1,minsize=200)

        #frame_folder.grid_columnconfigure(0, weight=1)
        #frame_folder.grid_rowconfigure(0, weight=1,minsize=200)

        (status_frame_groups := Frame(frame_groups,bg=self.bg_color)).pack(side='bottom', fill='both')

        #self.status_all_quant=Label(status_frame_groups,width=10,borderwidth=2,bg=self.bg_color,relief='groove',foreground='red',anchor='w')
        #self.status_all_quant_configure = self.status_all_quant.configure

        #self.status_all_quant.pack(fill='x',expand=0,side='right')
        # ~ Label(status_frame_groups,width=16,text="All marked files # ",relief='groove',borderwidth=2,bg=self.bg_color,anchor='e').pack(fill='x',expand=0,side='right')
        # ~ self.status_all_size=Label(status_frame_groups,width=10,borderwidth=2,bg=self.bg_color,relief='groove',foreground='red',anchor='w')
        #self.status_all_size.pack(fill='x',expand=0,side='right')
        #self.status_all_size_configure=self.status_all_size.configure

        # ~ Label(status_frame_groups,width=18,text='All marked files size: ',relief='groove',borderwidth=2,bg=self.bg_color,anchor='e').pack(fill='x',expand=0,side='right')

        Label(status_frame_groups,width=10,text='Record: ',relief='groove',borderwidth=2,bg=self.bg_color,anchor='e').pack(fill='x',expand=0,side='left')
        #self.status_path = Label(status_frame_groups,text='',relief='flat',borderwidth=1,bg=self.bg_color,anchor='w')

        #self.status_record=Label(status_frame_groups,text='--',image=self_ico['empty'],width=80,compound='right',borderwidth=2,bg=self.bg_color,relief='groove',anchor='e')
        self.status_record=Label(status_frame_groups,text='--',width=30,borderwidth=2,bg=self.bg_color,relief='groove',anchor='w')
        self.status_record.pack(fill='x',expand=0,side='left')
        self.status_record_configure = self.status_record.configure

        Label(status_frame_groups,width=10,text='Scan Path: ',relief='groove',borderwidth=2,bg=self.bg_color,anchor='e').pack(fill='x',expand=0,side='left')
        self.status_scan_path = Label(status_frame_groups,text='',relief='flat',borderwidth=1,bg=self.bg_color,anchor='w')

        #self.status_record=Label(status_frame_groups,text='--',image=self_ico['empty'],width=80,compound='right',borderwidth=2,bg=self.bg_color,relief='groove',anchor='e')
        self.status_scan_path=Label(status_frame_groups,text='--',width=30,borderwidth=2,bg=self.bg_color,relief='groove',anchor='w')
        self.status_scan_path.pack(fill='x',expand=0,side='left')
        self.status_scan_path_configure = self.status_scan_path.configure

        self.status_record.bind("<Motion>", lambda event : self.motion_on_widget(event,'Number of groups with consideration od "cross paths" option'))
        self.status_record.bind("<Leave>", lambda event : self.widget_leave())


        #self.status_path.pack(fill='x',expand=1,side='left')
        #self.status_path.bind("<Motion>", lambda event : self.motion_on_widget(event,'The full path of a directory shown in the bottom panel.'))
        #self.status_path.bind("<Leave>", lambda event : self.widget_leave())

        #self.status_scan_path_configure=self.status_path.configure

        (status_frame_folder := Frame(frame_folder,bg=self.bg_color)).pack(side='bottom',fill='both')

        self.status_line_lab=Label(status_frame_folder,width=30,image=self_ico['expression'],compound= 'left',text='',borderwidth=2,bg=self.bg_color,relief='groove',anchor='w')
        self.status_line_lab.pack(fill='x',expand=1,side='left')
        self.status_line_lab_configure = self.status_line_lab.configure
        self.status_line_lab_update = self.status_line_lab.update

        #self.status_folder_quant=Label(status_frame_folder,width=10,borderwidth=2,bg=self.bg_color,relief='groove',foreground='red',anchor='w')
        #self.status_folder_quant.pack(fill='x',expand=0,side='right')
        #self.status_folder_quant_configure=self.status_folder_quant.configure

        #Label(status_frame_folder,width=16,text='Marked files # ',relief='groove',borderwidth=2,bg=self.bg_color,anchor='e').pack(fill='x',expand=0,side='right')
        #self.status_folder_size=Label(status_frame_folder,width=10,borderwidth=2,bg=self.bg_color,relief='groove',foreground='red',anchor='w')
        #self.status_folder_size.pack(expand=0,side='right')
        #self.status_folder_size_configure=self.status_folder_size.configure

        #Label(status_frame_folder,width=18,text='Marked files size: ',relief='groove',borderwidth=2,bg=self.bg_color,anchor='e').pack(fill='x',expand=0,side='right')

        self_main_unbind_class = self.main_unbind_class = self_main.unbind_class

        self_main_bind_class = self.main_bind_class = self_main.bind_class

        #self_main_unbind_class('Treeview', '<KeyPress-Up>')
        #self_main_unbind_class('Treeview', '<KeyPress-Down>')
        #self_main_unbind_class('Treeview', '<KeyPress-Next>')
        #self_main_unbind_class('Treeview', '<KeyPress-Prior>')
        #self_main_unbind_class('Treeview', '<KeyPress-space>')
        #self_main_unbind_class('Treeview', '<KeyPress-Return>')
        #self_main_unbind_class('Treeview', '<KeyPress-Left>')
        #self_main_unbind_class('Treeview', '<KeyPress-Right>')
        #self_main_unbind_class('Treeview', '<Double-Button-1>')

        self.main_tree=Treeview(frame_groups,takefocus=True,show=('tree','headings') )
        self_main_tree = self.main_tree

        self_main_tree.bind('<KeyPress>', self.key_press )
        self_main_tree.bind('<<TreeviewOpen>>', self.open_item )
        self_main_tree.bind('<ButtonPress-3>', self.context_menu_show)

        self_main_tree.bind("<<TreeviewSelect>>", self.main_tree_select)
        self.selected_record_item=''
        self.selected_record_name=''

        #selectmode='none',

        self.main_tree_set = self_main_tree.set
        self.main_tree_see = self_main_tree.see
        self.main_tree_get_children = self.main_tree.get_children
        self.main_tree_focus = lambda item : self.main_tree.focus(item)

        self.org_label={}
        self_org_label = self.org_label

        self_org_label['opened']='--opened'
        self_org_label['record']='record'
        self_org_label['path']='--path'
        self_org_label['info']='--info'
        self_org_label['file']='File'
        self_org_label['size_h']='Size'
        self_org_label['ctime_h']='Time'

        self_main_tree["columns"]=('record','opened','path','file','size','size_h','ctime','ctime_h','info','dev','inode','crc','kind')
        self_main_tree["displaycolumns"]=('size','size_h','ctime_h')

        self_main_tree_column = self_main_tree.column

        self_main_tree_column('#0', width=120, minwidth=100, stretch='yes')
        #self_main_tree_column('path', width=100, minwidth=10, stretch='yes' )
        #self_main_tree_column('file', width=100, minwidth=10, stretch='yes' )
        self_main_tree_column('size_h', width=80, minwidth=80, stretch='no')
        self_main_tree_column('ctime_h', width=150, minwidth=100, stretch='no')

        self_main_tree_heading = self_main_tree.heading

        self_main_tree_heading('#0',text='Label',anchor='w')
        self_main_tree_heading('path',anchor='w' )
        self_main_tree_heading('file',anchor='w' )
        self_main_tree_heading('size_h',anchor='w')
        self_main_tree_heading('ctime_h',anchor='w')
        self_main_tree_heading('size_h', text='Size \u25BC')

        #bind_class breaks columns resizing
        self_main_tree.bind('<ButtonPress-1>', self.tree_on_mouse_button_press)
        self_main_tree.bind('<Control-ButtonPress-1>',  lambda event :self.tree_on_mouse_button_press(event,True) )
        #self_main_unbind_class('Treeview', '<<TreeviewClose>>')
        #self_main_unbind_class('Treeview', '<<TreeviewOpen>>')

        vsb1 = Scrollbar(frame_groups, orient='vertical', command=self_main_tree.yview,takefocus=False)

        self_main_tree.configure(yscrollcommand=vsb1.set)

        vsb1.pack(side='right',fill='y',expand=0)
        self_main_tree.pack(fill='both',expand=1, side='left')

        self_main_tree.bind('<Double-Button-1>', self.double_left_button)

        #self.files_tree=Treeview(frame_folder,takefocus=True,selectmode='none')
        #self_files_tree = self.files_tree

        #self.files_tree_see = self_files_tree.see

        #self.files_tree_set_item = lambda item,x : self_files_tree.set(item,x)
        #self.files_tree_configure = self_files_tree.configure
        #self.files_tree_delete = self_files_tree.delete

        #self_files_tree['columns']=('file','dev','inode','kind','crc','size','size_h','ctime','ctime_h')

        #self_files_tree['displaycolumns']=('file','size_h','ctime_h')

        #self_files_tree_column = self_files_tree.column

        #self_files_tree_column('#0', width=120, minwidth=100, stretch='no')

        #self_files_tree_column('file', width=200, minwidth=100, stretch='yes')
        #self_files_tree_column('size_h', width=80, minwidth=80, stretch='no')
        #self_files_tree_column('ctime_h', width=150, minwidth=100, stretch='no')

        #self_files_tree_heading = self_files_tree.heading

        #self_files_tree_heading('#0',text='CRC',anchor='w')
        #self_files_tree_heading('file',anchor='w')
        #self_files_tree_heading('size_h',anchor='w')
        #self_files_tree_heading('ctime_h',anchor='w')

        #,self_files_tree
        tree = self_main_tree
        tree_heading = tree.heading
        for col in tree["displaycolumns"]:
            if col in self_org_label:
                tree_heading(col,text=self_org_label[col])

        #self_files_tree_heading('file', text='File \u25B2')

        #vsb2 = Scrollbar(frame_folder, orient='vertical', command=self_files_tree.yview,takefocus=False)
        #,bg=self.bg_color
        #self.files_tree_configure(yscrollcommand=vsb2.set)

        #vsb2.pack(side='right',fill='y',expand=0)
        #self_files_tree.pack(fill='both',expand=1,side='left')

        #self_files_tree.bind('<Double-Button-1>', self.double_left_button)

        self_main_tree_tag_configure = self_main_tree.tag_configure

        self_main_tree_tag_configure(self.RECORD, foreground='green')

        self_main_tree_tag_configure(self.MARK, foreground='red')
        self_main_tree_tag_configure(self.MARK, background='red')
        self_main_tree_tag_configure(self.CRC, foreground='gray')

        #self_files_tree_tag_configure = self_files_tree.tag_configure

        #self_files_tree_tag_configure(self.MARK, foreground='red')
        #self_files_tree_tag_configure(self.MARK, background='red')

        #self_files_tree_tag_configure(self.SINGLE, foreground='gray')
        #self_files_tree_tag_configure(self.DIR, foreground='blue2')
        #self_files_tree_tag_configure(self.DIRLINK, foreground='blue2')
        #self_files_tree_tag_configure(self.LINK, foreground='darkgray')

        #bind_class breaks columns resizing
        #self_files_tree.bind('<ButtonPress-1>', self.tree_on_mouse_button_press)
        #self_files_tree.bind('<Control-ButtonPress-1>',  lambda event :self.tree_on_mouse_button_press(event,True) )

        #self.other_tree[self_files_tree]=self_main_tree
        #self.other_tree[self_main_tree]=self_files_tree

        self.biggest_file_of_path={}
        self.biggest_file_of_path_id={}

        self.iid_to_size={}

        try:
            self.main_update()
            cfg_geometry=self.cfg.get('main','',section='geometry')

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

        self.paned.update()
        #self.paned.sash_place(0,0,self.cfg.get('sash_coord',400,section='geometry'))

        #prevent displacement
        if cfg_geometry :
            self_main.geometry(cfg_geometry)

        self.popup_groups = Menu(self_main_tree, tearoff=0,bg=self.bg_color)
        self.popup_groups_unpost = self.popup_groups.unpost
        self.popup_groups.bind("<FocusOut>",lambda event : self.popup_groups_unpost() )

        #self.popup_folder = Menu(self_files_tree, tearoff=0,bg=self.bg_color)
        #self.popup_folder_unpost = self.popup_folder.unpost
        #self.popup_folder.bind("<FocusOut>",lambda event : self.popup_folder_unpost() )

        self_main_bind("<FocusOut>",lambda event : self.unpost() )

        #######################################################################
        #scan dialog

        def pre_show(on_main_window_dialog=True):
            self.menubar_unpost()
            self.hide_tooltip()
            self.popup_groups_unpost()
            #self.popup_folder_unpost()

            if on_main_window_dialog:
                self.actions_processing=False
                self.menu_disable()
                self.menubar_config(cursor="watch")

        def post_close(on_main_window_dialog=True):
            if on_main_window_dialog:
                self.actions_processing=True
                self.menu_enable()
                self.menubar_config(cursor="")

        self.scan_dialog=dialogs.GenericDialog(self_main,self_ico['librer'],self.bg_color,'Scan',pre_show=pre_show,post_close=post_close)

        self.log_skipped_var=BooleanVar()
        self.log_skipped_var.set(False)

        self.scan_dialog.area_main.grid_columnconfigure(0, weight=1)
        #self.scan_dialog.area_main.grid_rowconfigure(0, weight=1)
        self.scan_dialog.area_main.grid_rowconfigure(2, weight=1)

        self.scan_dialog.widget.bind('<Alt_L><a>',lambda event : self.path_to_scan_add_dialog())
        self.scan_dialog.widget.bind('<Alt_L><A>',lambda event : self.path_to_scan_add_dialog())
        self.scan_dialog.widget.bind('<Alt_L><s>',lambda event : self.scan_wrapper())
        self.scan_dialog.widget.bind('<Alt_L><S>',lambda event : self.scan_wrapper())

        self.scan_dialog.widget.bind('<Alt_L><E>',lambda event : self.exclude_mask_add_dialog())
        self.scan_dialog.widget.bind('<Alt_L><e>',lambda event : self.exclude_mask_add_dialog())

        ##############


        temp_frame = LabelFrame(self.scan_dialog.area_main,text='Path To scan:',borderwidth=2,bg=self.bg_color,takefocus=False)
        temp_frame.grid(row=0,column=0,sticky='we',padx=4,pady=4,columnspan=4)

        self.path_to_scan_entry_var=StringVar(value='')
        path_to_scan_entry = Entry(temp_frame,textvariable=self.path_to_scan_entry_var)
        path_to_scan_entry.pack(side='left',expand=1,fill='x',pady=4,padx=5)

        self.add_path_button = Button(temp_frame,width=18,image = self_ico['open'], command=self.path_to_scan_add_dialog,underline=0)
        self.add_path_button.pack(side='left',pady=4,padx=4)

        self.add_path_button.bind("<Motion>", lambda event : self.motion_on_widget(event,"Add path to scan.\nA maximum of 8 paths are allowed."))
        self.add_path_button.bind("<Leave>", lambda event : self.widget_leave())

        #sf_par=dialogs.SFrame(temp_frame,bg=self.bg_color)
        #sf_par.pack(fill='both',expand=True,side='top')
        #self.paths_frame=sf_par.frame()

        #buttons_fr = Frame(temp_frame,bg=self.bg_color,takefocus=False)
        #buttons_fr.pack(fill='both',expand=False,side='bottom')


        #self.paths_frame.grid_columnconfigure(1, weight=1)
        #self.paths_frame.grid_rowconfigure(99, weight=1)

        temp_frame2 = LabelFrame(self.scan_dialog.area_main,text='Label:',borderwidth=2,bg=self.bg_color,takefocus=False)
        temp_frame2.grid(row=1,column=0,sticky='we',padx=4,pady=4,columnspan=4)

        self.scan_label_entry_var=StringVar(value='')
        scan_label_entry = Entry(temp_frame2,textvariable=self.scan_label_entry_var)
        scan_label_entry.pack(side='left',expand=1,fill='x',pady=4,padx=5)

        ##############
        self.exclude_regexp_scan=BooleanVar()

        temp_frame2 = LabelFrame(self.scan_dialog.area_main,text='Exclude from scan:',borderwidth=2,bg=self.bg_color,takefocus=False)
        temp_frame2.grid(row=2,column=0,sticky='news',padx=4,pady=4,columnspan=4)

        sf_par2=dialogs.SFrame(temp_frame2,bg=self.bg_color)
        sf_par2.pack(fill='both',expand=True,side='top')
        self.exclude_frame=sf_par2.frame()

        buttons_fr2 = Frame(temp_frame2,bg=self.bg_color,takefocus=False)
        buttons_fr2.pack(fill='both',expand=False,side='bottom')

        self.add_exclude_button_dir = Button(buttons_fr2,width=18,image = self_ico['open'],command=self.exclude_mask_add_dir)
        self.add_exclude_button_dir.pack(side='left',pady=4,padx=4)
        self.add_exclude_button_dir.bind("<Motion>", lambda event : self.motion_on_widget(event,"Add path as exclude expression ..."))
        self.add_exclude_button_dir.bind("<Leave>", lambda event : self.widget_leave())

        self.add_exclude_button = Button(buttons_fr2,width=18,image= self_ico['expression'],command=self.exclude_mask_add_dialog,underline=4)

        tooltip_string = 'Add expression ...\nduring the scan, the entire path is checked \nagainst the specified expression,\ne.g.' + ('*windows* etc. (without regular expression)\nor .*windows.*, etc. (with regular expression)' if windows else '*.git* etc. (without regular expression)\nor .*\\.git.* etc. (with regular expression)')
        self.add_exclude_button.bind("<Motion>", lambda event : self.motion_on_widget(event,tooltip_string))
        self.add_exclude_button.bind("<Leave>", lambda event : self.widget_leave())

        self.add_exclude_button.pack(side='left',pady=4,padx=4)

        Checkbutton(buttons_fr2,text='treat as a regular expression',variable=self.exclude_regexp_scan,command=self.exclude_regexp_set).pack(side='left',pady=4,padx=4)

        self.exclude_frame.grid_columnconfigure(1, weight=1)
        self.exclude_frame.grid_rowconfigure(99, weight=1)
        ##############

        skip_button = Checkbutton(self.scan_dialog.area_main,text='log skipped files',variable=self.log_skipped_var)
        skip_button.grid(row=3,column=0,sticky='news',padx=8,pady=3,columnspan=3)

        skip_button.bind("<Motion>", lambda event : self.motion_on_widget(event,"log every skipped file (softlinks, hardlinks, excluded, no permissions etc.)"))
        skip_button.bind("<Leave>", lambda event : self.widget_leave())

        self.scan_button = Button(self.scan_dialog.area_buttons,width=12,text="Scan",image=self_ico['scan'],compound='left',command=self.scan_wrapper,underline=0)
        self.scan_button.pack(side='right',padx=4,pady=4)

        self.scan_cancel_button = Button(self.scan_dialog.area_buttons,width=12,text="Cancel",image=self_ico['cancel'],compound='left',command=self.scan_dialog_hide_wrapper,underline=0)
        self.scan_cancel_button.pack(side='left',padx=4,pady=4)

        self.scan_dialog.focus=self.scan_cancel_button

        def pre_show_settings():
            _ = {var.set(self.cfg_get_bool(key)) for var,key in self.settings}
            _ = {var.set(self.cfg.get(key)) for var,key in self.settings_str}
            return pre_show()

        #######################################################################
        #Settings Dialog
        self.settings_dialog=dialogs.GenericDialog(self_main,self_ico['librer'],self.bg_color,'Settings',pre_show=pre_show_settings,post_close=post_close)

        self.show_full_crc = BooleanVar()
        self.show_full_paths = BooleanVar()
        self.cross_mode = BooleanVar()

        self.create_relative_symlinks = BooleanVar()
        self.erase_empty_directories = BooleanVar()
        self.abort_on_error = BooleanVar()
        self.send_to_trash = BooleanVar()

        self.allow_delete_all = BooleanVar()
        self.skip_incorrect_groups = BooleanVar()
        self.allow_delete_non_duplicates = BooleanVar()

        self.confirm_show_crc_and_size = BooleanVar()

        self.confirm_show_links_targets = BooleanVar()
        self.file_open_wrapper = StringVar()
        self.folders_open_wrapper = StringVar()
        self.folders_open_wrapper_params = StringVar()

        self.settings = [
            (self.show_full_crc,CFG_KEY_FULL_CRC),
            (self.show_full_paths,CFG_KEY_FULL_PATHS),
            (self.cross_mode,CFG_KEY_CROSS_MODE),
            (self.create_relative_symlinks,CFG_KEY_REL_SYMLINKS),
            (self.erase_empty_directories,CFG_ERASE_EMPTY_DIRS),
            (self.abort_on_error,CFG_ABORT_ON_ERROR),
            (self.send_to_trash,CFG_SEND_TO_TRASH),
            (self.confirm_show_crc_and_size,CFG_CONFIRM_SHOW_CRCSIZE),
            (self.confirm_show_links_targets,CFG_CONFIRM_SHOW_LINKSTARGETS),
            (self.allow_delete_all,CFG_ALLOW_DELETE_ALL),
            (self.skip_incorrect_groups,CFG_SKIP_INCORRECT_GROUPS),
            (self.allow_delete_non_duplicates,CFG_ALLOW_DELETE_NON_DUPLICATES)
        ]
        self.settings_str = [
            (self.file_open_wrapper,CFG_KEY_WRAPPER_FILE),
            (self.folders_open_wrapper,CFG_KEY_WRAPPER_FOLDERS),
            (self.folders_open_wrapper_params,CFG_KEY_WRAPPER_FOLDERS_PARAMS)
        ]

        row = 0
        label_frame=LabelFrame(self.settings_dialog.area_main, text="Main panels",borderwidth=2,bg=self.bg_color)
        label_frame.grid(row=row,column=0,sticky='wens',padx=3,pady=3) ; row+=1

        (cb_1:=Checkbutton(label_frame, text = 'Show full CRC', variable=self.show_full_crc)).grid(row=0,column=0,sticky='wens',padx=3,pady=2)
        cb_1.bind("<Motion>", lambda event : self.motion_on_widget(event,'If disabled, shortest necessary prefix of full CRC wil be shown'))
        cb_1.bind("<Leave>", lambda event : self.widget_leave())

        (cb_2:=Checkbutton(label_frame, text = 'Show full scan paths', variable=self.show_full_paths)).grid(row=1,column=0,sticky='wens',padx=3,pady=2)
        cb_2.bind("<Motion>", lambda event : self.motion_on_widget(event,'If disabled, scan path symbols will be shown instead of full paths\nfull paths are always displayed as tooltips'))
        cb_2.bind("<Leave>", lambda event : self.widget_leave())

        (cb_3:=Checkbutton(label_frame, text = '"Cross paths" mode', variable=self.cross_mode)).grid(row=2,column=0,sticky='wens',padx=3,pady=2)
        cb_3.bind("<Motion>", lambda event : self.motion_on_widget(event,'Ignore (hide) records containing duplicates in only one search path.\nShow only groups with files in different search paths.\nIn this mode, you can treat one search path as a "reference"\nand delete duplicates in all other paths with ease'))
        cb_3.bind("<Leave>", lambda event : self.widget_leave())

        label_frame=LabelFrame(self.settings_dialog.area_main, text="Confirmation dialogs",borderwidth=2,bg=self.bg_color)
        label_frame.grid(row=row,column=0,sticky='wens',padx=3,pady=3) ; row+=1

        (cb_3:=Checkbutton(label_frame, text = 'Skip groups with invalid selection', variable=self.skip_incorrect_groups)).grid(row=0,column=0,sticky='wens',padx=3,pady=2)
        cb_3.bind("<Motion>", lambda event : self.motion_on_widget(event,'Groups with incorrect marks set will abort action.\nEnable this option to skip those groups.\nFor delete or soft-link action, one file in a group \nmust remain unmarked (see below). For hardlink action,\nmore than one file in a group must be marked.'))
        cb_3.bind("<Leave>", lambda event : self.widget_leave())

        (cb_4:=Checkbutton(label_frame, text = 'Allow deletion of all copies', variable=self.allow_delete_all,image=self_ico['warning'],compound='right')).grid(row=1,column=0,sticky='wens',padx=3,pady=2)
        cb_4.bind("<Motion>", lambda event : self.motion_on_widget(event,'Before deleting selected files, files selection in every CRC \ngroup is checked, at least one file should remain unmarked.\nIf This option is enabled it will be possible to delete all copies'))
        cb_4.bind("<Leave>", lambda event : self.widget_leave())

        Checkbutton(label_frame, text = 'Show soft links targets', variable=self.confirm_show_links_targets ).grid(row=2,column=0,sticky='wens',padx=3,pady=2)
        Checkbutton(label_frame, text = 'Show CRC and size', variable=self.confirm_show_crc_and_size ).grid(row=3,column=0,sticky='wens',padx=3,pady=2)

        label_frame=LabelFrame(self.settings_dialog.area_main, text="Processing",borderwidth=2,bg=self.bg_color)
        label_frame.grid(row=row,column=0,sticky='wens',padx=3,pady=3) ; row+=1

        Checkbutton(label_frame, text = 'Create relative symbolic links', variable=self.create_relative_symlinks                  ).grid(row=0,column=0,sticky='wens',padx=3,pady=2)
        Checkbutton(label_frame, text = 'Send Files to %s instead of deleting them' % ('Recycle Bin' if windows else 'Trash'), variable=self.send_to_trash ).grid(row=1,column=0,sticky='wens',padx=3,pady=2)
        Checkbutton(label_frame, text = 'Erase remaining empty directories', variable=self.erase_empty_directories).grid(row=2,column=0,sticky='wens',padx=3,pady=2)
        Checkbutton(label_frame, text = 'Abort on first error', variable=self.abort_on_error).grid(row=3,column=0,sticky='wens',padx=3,pady=2)

        #Checkbutton(fr, text = 'Allow to delete regular files (WARNING!)', variable=self.allow_delete_non_duplicates        ).grid(row=row,column=0,sticky='wens',padx=3,pady=2)

        label_frame=LabelFrame(self.settings_dialog.area_main, text="Opening wrappers",borderwidth=2,bg=self.bg_color)
        label_frame.grid(row=row,column=0,sticky='wens',padx=3,pady=3) ; row+=1

        Label(label_frame,text='parameters #',bg=self.bg_color,anchor='n').grid(row=0, column=2,sticky='news')

        Label(label_frame,text='File: ',bg=self.bg_color,anchor='w').grid(row=1, column=0,sticky='news')
        (en_1:=Entry(label_frame,textvariable=self.file_open_wrapper)).grid(row=1, column=1,sticky='news',padx=3,pady=2)
        en_1.bind("<Motion>", lambda event : self.motion_on_widget(event,'Command executed on "Open File" with full file path as parameter.\nIf empty, default os association will be executed.'))
        en_1.bind("<Leave>", lambda event : self.widget_leave())

        Label(label_frame,text='Folders: ',bg=self.bg_color,anchor='w').grid(row=2, column=0,sticky='news')
        (en_2:=Entry(label_frame,textvariable=self.folders_open_wrapper)).grid(row=2, column=1,sticky='news',padx=3,pady=2)
        en_2.bind("<Motion>", lambda event : self.motion_on_widget(event,'Command executed on "Open Folder" with full path as parameter.\nIf empty, default os filemanager will be used.'))
        en_2.bind("<Leave>", lambda event : self.widget_leave())
        (cb_2:=Combobox(label_frame,values=('1','2','3','4','5','6','7','8','all'),textvariable=self.folders_open_wrapper_params,state='readonly')).grid(row=2, column=2,sticky='ew',padx=3)
        cb_2.bind("<Motion>", lambda event : self.motion_on_widget(event,'Number of parameters (paths) passed to\n"Opening wrapper" (if defined) when action\nis performed on crc groups\ndefault is 2'))
        cb_2.bind("<Leave>", lambda event : self.widget_leave())

        label_frame.grid_columnconfigure(1, weight=1)

        bfr=Frame(self.settings_dialog.area_main,bg=self.bg_color)
        self.settings_dialog.area_main.grid_rowconfigure(row, weight=1); row+=1

        bfr.grid(row=row,column=0) ; row+=1

        Button(bfr, text='Set defaults',width=14, command=self.settings_reset).pack(side='left', anchor='n',padx=5,pady=5)
        Button(bfr, text='OK', width=14, command=self.settings_ok ).pack(side='left', anchor='n',padx=5,pady=5)
        self.cancel_button=Button(bfr, text='Cancel', width=14 ,command=self.settings_dialog.hide )
        self.cancel_button.pack(side='right', anchor='n',padx=5,pady=5)

        self.settings_dialog.area_main.grid_columnconfigure(0, weight=1)

        #######################################################################
        self.info_dialog_on_main = dialogs.LabelDialog(self_main,self_ico['librer'],self.bg_color,pre_show=pre_show,post_close=post_close)
        self.text_ask_dialog = dialogs.TextDialogQuestion(self_main,self_ico['librer'],self.bg_color,pre_show=pre_show,post_close=post_close,image=self_ico['warning'])
        self.text_info_dialog = dialogs.TextDialogInfo(self_main,self_ico['librer'],self.bg_color,pre_show=pre_show,post_close=post_close)
        self.info_dialog_on_scan = dialogs.LabelDialog(self.scan_dialog.widget,self_ico['librer'],self.bg_color,pre_show=pre_show,post_close=post_close)
        self.exclude_dialog_on_scan = dialogs.EntryDialogQuestion(self.scan_dialog.widget,self_ico['librer'],self.bg_color,pre_show=pre_show,post_close=post_close)

        self.progress_dialog_on_scan = dialogs.ProgressDialog(self.scan_dialog.widget,self_ico['librer'],self.bg_color,pre_show=pre_show,post_close=post_close)
        self.progress_dialog_on_scan.command_on_close = self.progress_dialog_abort

        self.progress_dialog_on_scan.abort_button.bind("<Leave>", lambda event : self.widget_leave())
        self.progress_dialog_on_scan.abort_button.bind("<Motion>", lambda event : self.motion_on_widget(event) )

        self.mark_dialog_on_groups = dialogs.CheckboxEntryDialogQuestion(self_main_tree,self_ico['librer'],self.bg_color,pre_show=pre_show,post_close=post_close)
        #self.mark_dialog_on_folder = dialogs.CheckboxEntryDialogQuestion(self_files_tree,self_ico['librer'],self.bg_color,pre_show=pre_show,post_close=post_close)

        self.info_dialog_on_mark={}

        self.info_dialog_on_mark[self_main_tree] = dialogs.LabelDialog(self.mark_dialog_on_groups.widget,self_ico['librer'],self.bg_color,pre_show=lambda : pre_show(False),post_close=lambda : post_close(False))
        #self.info_dialog_on_mark[self_files_tree] = dialogs.LabelDialog(self.mark_dialog_on_folder.widget,self_ico['librer'],self.bg_color,pre_show=lambda : pre_show(False),post_close=lambda : post_close(False))

        self.find_dialog_on_groups = dialogs.FindEntryDialog(self_main_tree,self_ico['librer'],self.bg_color,self.find_mod,self.find_prev_from_dialog,self.find_next_from_dialog,pre_show=pre_show,post_close=post_close)
        #self.find_dialog_on_folder = dialogs.FindEntryDialog(self_files_tree,self_ico['librer'],self.bg_color,self.find_mod,self.find_prev_from_dialog,self.find_next_from_dialog,pre_show=pre_show,post_close=post_close)

        self.info_dialog_on_find={}

        self.info_dialog_on_find[self_main_tree] = dialogs.LabelDialog(self.find_dialog_on_groups.widget,self_ico['librer'],self.bg_color,pre_show=lambda : pre_show(False),post_close=lambda : post_close(False))
        #self.info_dialog_on_find[self_files_tree] = dialogs.LabelDialog(self.find_dialog_on_folder.widget,self_ico['librer'],self.bg_color,pre_show=lambda : pre_show(False),post_close=lambda : post_close(False))

       #######################################################################
        #About Dialog
        self.aboout_dialog=dialogs.GenericDialog(self_main,self_ico['librer'],self.bg_color,'',pre_show=pre_show,post_close=post_close)

        frame1 = LabelFrame(self.aboout_dialog.area_main,text='',bd=2,bg=self.bg_color,takefocus=False)
        frame1.grid(row=0,column=0,sticky='news',padx=4,pady=(4,2))
        self.aboout_dialog.area_main.grid_rowconfigure(1, weight=1)

        text= f'\n\nLibrer {VER_TIMESTAMP}\nAuthor: Piotr Jochymek\n\n{HOMEPAGE}\n\nPJ.soft.dev.x@gmail.com\n\n'

        Label(frame1,text=text,bg=self.bg_color,justify='center').pack(expand=1,fill='both')

        frame2 = LabelFrame(self.aboout_dialog.area_main,text='',bd=2,bg=self.bg_color,takefocus=False)
        frame2.grid(row=1,column=0,sticky='news',padx=4,pady=(2,4))
        lab2_text=  'LOGS DIRECTORY     :  ' + LOG_DIR + '\n' + \
                    'SETTINGS DIRECTORY :  ' + CONFIG_DIR + '\n' + \
                    'DATABASE DIRECTORY :  ' + DB_DIR + '\n\n' + \
                    'Current log file   :  ' + log

        #'LOGGING LEVEL      :  ' + log_levels[LOG_LEVEL] + '\n\n' + \

        lab_courier = Label(frame2,text=lab2_text,bg=self.bg_color,justify='left')
        lab_courier.pack(expand=1,fill='both')

        try:
            lab_courier.configure(font=('Courier', 10))
        except:
            try:
                lab_courier.configure(font=('TkFixedFont', 10))
            except:
                pass

        #######################################################################
        #License Dialog
        try:
            self.license=Path(path_join(LIBRER_DIR,'LICENSE')).read_text(encoding='ASCII')
        except Exception as exception_1:
            l_error(exception_1)
            try:
                self.license=Path(path_join(dirname(LIBRER_DIR),'LICENSE')).read_text(encoding='ASCII')
            except Exception as exception_2:
                l_error(exception_2)
                self.exit()

        self.license_dialog=dialogs.GenericDialog(self_main,self_ico['license'],self.bg_color,'',pre_show=pre_show,post_close=post_close,min_width=800,min_height=520)

        frame1 = LabelFrame(self.license_dialog.area_main,text='',bd=2,bg=self.bg_color,takefocus=False)
        frame1.grid(row=0,column=0,sticky='news',padx=4,pady=4)
        self.license_dialog.area_main.grid_rowconfigure(0, weight=1)

        lab_courier=Label(frame1,text=self.license,bg=self.bg_color,justify='center')
        lab_courier.pack(expand=1,fill='both')

        try:
            lab_courier.configure(font=('Courier', 10))
        except:
            try:
                lab_courier.configure(font=('TkFixedFont', 10))
            except:
                pass

        def file_cascade_post():
            item_actions_state=('disabled','normal')[self.sel_item is not None]

            self.file_cascade.delete(0,'end')
            if self.actions_processing:
                self_file_cascade_add_command = self.file_cascade.add_command
                self_file_cascade_add_separator = self.file_cascade.add_separator

                item_actions_state=('disabled','normal')[self.sel_item is not None]
                self_file_cascade_add_command(label = 'Scan ...',command = self.scan_dialog_show, accelerator="S",image = self_ico['scan'],compound='left')
                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = 'Settings ...',command=self.settings_dialog.show, accelerator="F2",image = self_ico['settings'],compound='left')
                self_file_cascade_add_separator()
                #self_file_cascade_add_command(label = 'Remove empty folders in specified directory ...',command=self.empty_folder_remove_ask,image = self_ico['empty'],compound='left')
                #self_file_cascade_add_separator()
                self_file_cascade_add_command(label = 'Save CSV',command = self.csv_save,state=item_actions_state,image = self_ico['empty'],compound='left')
                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = 'Erase CRC Cache',command = self.db_clean,image = self_ico['empty'],compound='left')
                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = 'Exit',command = self.exit,image = self_ico['exit'],compound='left')

        self.file_cascade= Menu(self.menubar,tearoff=0,bg=self.bg_color,postcommand=file_cascade_post)
        self.menubar.add_cascade(label = 'File',menu = self.file_cascade,accelerator="Alt+F")

        def navi_cascade_post():
            return
            self.navi_cascade.delete(0,'end')
            if self.actions_processing:
                item_actions_state=('disabled','normal')[self.sel_item is not None]

        def help_cascade_post():
            self.help_cascade.delete(0,'end')
            if self.actions_processing:

                self_help_cascade_add_command = self.help_cascade.add_command
                self_help_cascade_add_separator = self.help_cascade.add_separator

                self_help_cascade_add_command(label = 'About',command=self.aboout_dialog.show,accelerator="F1", image = self_ico['about'],compound='left')
                self_help_cascade_add_command(label = 'License',command=self.license_dialog.show, image = self_ico['license'],compound='left')
                self_help_cascade_add_separator()
                self_help_cascade_add_command(label = 'Open current Log',command=self.show_log, image = self_ico['log'],compound='left')
                self_help_cascade_add_command(label = 'Open logs directory',command=self.show_logs_dir, image = self_ico['logs'],compound='left')
                self_help_cascade_add_separator()
                self_help_cascade_add_command(label = 'Open homepage',command=self.show_homepage, image = self_ico['home'],compound='left')

        self.help_cascade= Menu(self.menubar,tearoff=0,bg=self.bg_color,postcommand=help_cascade_post)

        self.menubar.add_cascade(label = 'Help',menu = self.help_cascade)

        #######################################################################
        self.reset_sels()

        self.REAL_SORT_COLUMN={}
        self_REAL_SORT_COLUMN = self.REAL_SORT_COLUMN
        self_REAL_SORT_COLUMN['path'] = 'path'
        self_REAL_SORT_COLUMN['file'] = 'file'
        self_REAL_SORT_COLUMN['size_h'] = 'size'
        self_REAL_SORT_COLUMN['ctime_h'] = 'ctime'

        #self_main_tree["columns"]=('record','opened','path','file','size','size_h','ctime','ctime_h','info','dev','inode','crc','kind')
        self.REAL_SORT_COLUMN_INDEX={}
        self_REAL_SORT_COLUMN_INDEX = self.REAL_SORT_COLUMN_INDEX

        self_REAL_SORT_COLUMN_INDEX['path'] = 3
        self_REAL_SORT_COLUMN_INDEX['file'] = 4
        self_REAL_SORT_COLUMN_INDEX['size_h'] = 5
        self_REAL_SORT_COLUMN_INDEX['ctime_h'] = 7

        self.REAL_SORT_COLUMN_IS_NUMERIC={}
        self_REAL_SORT_COLUMN_IS_NUMERIC = self.REAL_SORT_COLUMN_IS_NUMERIC

        self_REAL_SORT_COLUMN_IS_NUMERIC['path'] = False
        self_REAL_SORT_COLUMN_IS_NUMERIC['file'] = False
        self_REAL_SORT_COLUMN_IS_NUMERIC['size_h'] = True
        self_REAL_SORT_COLUMN_IS_NUMERIC['ctime_h'] = True

        self.column_sort_last_params={}
        #colname,sort_index,is_numeric,reverse,updir_code,dir_code,non_dir_code

        self.column_sort_last_params[self_main_tree]=self.column_groups_sort_params_default=('size_h',self_REAL_SORT_COLUMN_INDEX['size_h'],self_REAL_SORT_COLUMN_IS_NUMERIC['size_h'],1,2,1,0)
        #self.column_sort_last_params[self_files_tree]=('file',self_REAL_SORT_COLUMN_INDEX['file'],self_REAL_SORT_COLUMN_IS_NUMERIC['file'],0,0,1,2)

        self.records_show()

        #######################################################################

        self_main_tree.bind("<Motion>", self.motion_on_main_tree)
        #self_files_tree.bind("<Motion>", self.motion_on_files_tree)

        self_main_tree.bind("<Leave>", lambda event : self.widget_leave())
        #self_files_tree.bind("<Leave>", lambda event : self.widget_leave())

        #######################################################################

        if paths_to_add:
            if len(paths_to_add)>self.MAX_PATHS:
                l_warning('only %s search paths allowed. Following are ignored:\n%s',self.MAX_PATHS, '\n'.join(paths_to_add[8:]))
            for path in paths_to_add[:self.MAX_PATHS]:
                if windows and path[-1]==':':
                    path += '\\'
                self.path_to_scan_add(abspath(path))

        run_scan_condition = bool(paths_to_add and not norun)

        if exclude:
            self.cfg.set(CFG_KEY_EXCLUDE,'|'.join(exclude))
            self.cfg.set_bool(CFG_KEY_EXCLUDE_REGEXP,False)
        elif exclude_regexp:
            self.cfg.set(CFG_KEY_EXCLUDE,'|'.join(exclude_regexp))
            self.cfg.set_bool(CFG_KEY_EXCLUDE_REGEXP,True)
        else:
            if run_scan_condition:
                self.cfg.set(CFG_KEY_EXCLUDE,'')

        self.exclude_regexp_scan.set(self.cfg_get_bool(CFG_KEY_EXCLUDE_REGEXP))

        self.main_update()

        self.scan_dialog_show(run_scan_condition)

        self.actions_processing=True

        self.tree_semi_focus(self_main_tree)

        self_main.mainloop()
        #######################################################################

    def unpost(self):
        self.hide_tooltip()
        self.menubar_unpost()
        #self.popup_groups_unpost()
        #self.popup_folder_unpost()

    tooltip_show_after_groups=''
    tooltip_show_after_folder=''
    tooltip_show_after_widget=''

    def widget_leave(self):
        self.menubar_unpost()
        self.hide_tooltip()

    def motion_on_widget(self,event,message=None):
        if message:
            self.tooltip_message[str(event.widget)]=message
        self.tooltip_show_after_widget = event.widget.after(1, self.show_tooltip_widget(event))

    def motion_on_main_tree(self,event):
        if self.actions_processing:
            self.tooltip_show_after_groups = event.widget.after(1, self.show_tooltip_groups(event))

    #def motion_on_files_tree(self,event):
    #    if self.actions_processing:
    #        self.tooltip_show_after_folder = event.widget.after(1, self.show_tooltip_folder(event))

    def configure_tooltip(self,widget):
        self.tooltip_lab_configure(text=self.tooltip_message[str(widget)])

    def show_tooltip_widget(self,event):
        return

        self.unschedule_tooltip_widget(event)
        self.menubar_unpost()

        self.configure_tooltip(event.widget)

        self.tooltip_deiconify()
        self.tooltip_wm_geometry("+%d+%d" % (event.x_root + 20, event.y_root + 5))

    def show_tooltip_groups(self,event):
        return

        self.unschedule_tooltip_groups(event)
        self.menubar_unpost()

        self.tooltip_wm_geometry("+%d+%d" % (event.x_root + 20, event.y_root + 5))

        tree = event.widget
        col=tree.identify_column(event.x)
        if col:
            colname=tree.column(col,'id')
            if tree.identify("region", event.x, event.y) == 'heading':
                if colname in ('path','size_h','file','ctime_h'):
                    self.tooltip_lab_configure(text='Sort by %s' % self.org_label[colname])
                    self.tooltip_deiconify()
                else:
                    self.hide_tooltip()

            elif item := tree.identify('item', event.x, event.y):
                if col=="#0" :
                    crc=item
                    self.tooltip_lab_configure(text='CRC: %s' % crc )
                    self.tooltip_deiconify()

                elif col:

                    coldata=tree.set(item,col)

                    if coldata:
                        self.tooltip_lab_configure(text=coldata)
                        self.tooltip_deiconify()

                    else:
                        self.hide_tooltip()

    def show_tooltip_folder(self,event):
        return

        self.unschedule_tooltip_folder(event)
        self.menubar_unpost()

        self.tooltip_wm_geometry("+%d+%d" % (event.x_root + 20, event.y_root + 5))

        tree = event.widget
        col=tree.identify_column(event.x)
        if col:
            colname=tree.column(col,'id')
            if tree.identify("region", event.x, event.y) == 'heading':
                if colname in ('size_h','file','ctime_h'):
                    self.tooltip_lab_configure(text='Sort by %s' % self.org_label[colname])
                    self.tooltip_deiconify()
                else:
                    self.hide_tooltip()
            elif item := tree.identify('item', event.x, event.y):

                coldata=''
                #KIND_INDEX=3
                kind=tree.set(item,3)
                if kind==self.LINK:
                    coldata='(soft-link)'
                elif kind==self.DIRLINK:
                    coldata='(directory soft-link)'

                if col=="#0" :
                    pass
                elif col:
                    coldata = coldata + ' ' + tree.set(item,col)

                if coldata:
                    self.tooltip_lab_configure(text=coldata)
                    self.tooltip_deiconify()
                else:
                    self.hide_tooltip()

    def unschedule_tooltip_widget(self,event):
        if self.tooltip_show_after_widget:
            event.widget.after_cancel(self.tooltip_show_after_widget)
            self.tooltip_show_after_widget = None

    def unschedule_tooltip_groups(self,event):
        if self.tooltip_show_after_groups:
            event.widget.after_cancel(self.tooltip_show_after_groups)
            self.tooltip_show_after_groups = None

    def unschedule_tooltip_folder(self,event):
        if self.tooltip_show_after_folder:
            event.widget.after_cancel(self.tooltip_show_after_folder)
            self.tooltip_show_after_folder = None

    def hide_tooltip(self):
        self.tooltip_withdraw()

    status_curr_text='-'

    def status_main(self,text='',image='',do_log=True):
        if text != self.status_curr_text:

            self.status_curr_text=text
            self.status_line_lab_configure(text=text,image=image,compound='left')

            if do_log and text:
                l_info('STATUS:%s',text)
            self.status_line_lab_update()

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
        #disable("Navigation")
        disable("Help")
        #self.menubar.update()

    def reset_sels(self):
        self.sel_path = None
        self.sel_file = None
        self.sel_crc = None
        self.sel_item = None

        self.sel_tree=self.main_tree

        self.sel_kind = None

    def get_index_tuple_main_tree(self,item):
        self_main_tree_set = lambda x : self.main_tree_set(item,x)
        int_self_main_tree_set = lambda x : int(self_main_tree_set(x))

        #path,file,ctime,dev,inode
        return (\
                self_main_tree_set('path'),\
                self_main_tree_set('file'),\
                int_self_main_tree_set('ctime'),\
                int_self_main_tree_set('dev'),\
                int_self_main_tree_set('inode')
        )

    def delete_window_wrapper(self):
        if self.actions_processing:
            self.exit()
        else:
            self.status('WM_DELETE_WINDOW NOT exiting ...')

    def exit(self):
        try:
            self.cfg.set('main',str(self.main.geometry()),section='geometry')
            #coords=self.paned.sash_coord(0)
            #self.cfg.set('sash_coord',str(coords[1]),section='geometry')
            self.cfg.write()
        except Exception as e:
            l_error(e)

        self.status('exiting ...')
        #self.main.withdraw()
        sys.exit(0)
        #self.main.destroy()

    find_result=()
    find_params_changed=True
    find_tree_index=-1

    find_by_tree={}

    def finder_wrapper_show(self):
        tree=self.sel_tree

        self.find_dialog_shown=True

        scope_info = 'Scope: All groups.' if self.sel_tree==self.main_tree else 'Scope: Selected directory.'

        if tree in self.find_by_tree:
            initialvalue=self.find_by_tree[tree]
        else:
            initialvalue='*'

        #self.find_dialog_on_main.show('Find',scope_info,initial=initialvalue,checkbutton_text='treat as a regular expression',checkbutton_initial=False)
        #self.find_by_tree[tree]=self.find_dialog_on_main.entry.get()

        self.find_dialog_on_groups.show('Find',scope_info,initial=initialvalue,checkbutton_text='treat as a regular expression',checkbutton_initial=False)
        self.find_by_tree[tree]=self.find_dialog_on_groups.entry.get()

        #if self.sel_tree==self.main_tree:
        #else:
            #self.find_dialog_on_folder.show('Find',scope_info,initial=initialvalue,checkbutton_text='treat as a regular expression',checkbutton_initial=False)
            #self.find_by_tree[tree]=self.find_dialog_on_folder.entry.get()

        self.find_dialog_shown=False
        self.tree_semi_focus(tree)

    def find_prev_from_dialog(self,expression,use_reg_expr):
        self.find_items(expression,use_reg_expr)
        self.select_find_result(-1)

    def find_prev(self):
        if not self.find_result or self.find_tree!=self.sel_tree:
            self.find_params_changed=True
            self.finder_wrapper_show()
        else:
            self.select_find_result(-1)

    def find_next_from_dialog(self,expression,use_reg_expr):
        self.find_items(expression,use_reg_expr)
        self.select_find_result(1)

    def find_next(self):
        if not self.find_result or self.find_tree!=self.sel_tree:
            self.find_params_changed=True
            self.finder_wrapper_show()
        else:
            self.select_find_result(1)

    find_result_index=0
    find_tree=''
    find_dialog_shown=False
    use_reg_expr_prev=''
    find_expression_prev=''

    def find_mod(self,expression,use_reg_expr):
        if self.use_reg_expr_prev!=use_reg_expr or self.find_expression_prev!=expression:
            self.use_reg_expr_prev=use_reg_expr
            self.find_expression_prev=expression
            self.find_params_changed=True
            self.cfg.set_bool(CFG_KEY_USE_REG_EXPR,use_reg_expr)
            self.find_result_index=0

    @restore_status_line
    def find_items(self,expression,use_reg_expr):
        self.status('finding ...')

        if self.find_params_changed or self.find_tree != self.sel_tree:
            self.find_tree=self.sel_tree

            items=[]
            items_append = items.append

            self_main_tree_get_children = self.main_tree_get_children
            self_item_full_path = self.item_full_path

            if expression:
                if self.sel_tree==self.main_tree:
                    crc_range = self_main_tree_get_children()

                    try:
                        for crc_item in crc_range:
                            for item in self_main_tree_get_children(crc_item):
                                fullpath = self_item_full_path(item)
                                if (use_reg_expr and search(expression,fullpath)) or (not use_reg_expr and fnmatch(fullpath,expression) ):
                                    items_append(item)
                    except Exception as e:
                        try:
                            self.info_dialog_on_find[self.find_tree].show('Error',str(e))
                        except Exception as e2:
                            print(e2)
                        return
                #else:
                #    try:
                #        for item in self.current_folder_items:
                #            #if tree.set(item,'kind')==self.FILE:
                #            file=self.files_tree.set(item,'file')
                #            if (use_reg_expr and search(expression,file)) or (not use_reg_expr and fnmatch(file,expression) ):
                #                items_append(item)
                #    except Exception as e:
                #        self.info_dialog_on_find[self.find_tree].show('Error',str(e))
                #        return
            if items:
                self.find_result=tuple(items)
                self.find_params_changed=False
            else:
                self.find_result=()
                scope_info = 'Scope: All groups.' if self.find_tree==self.main_tree else 'Scope: Selected directory.'
                self.info_dialog_on_find[self.find_tree].show(scope_info,'No files found.')

    def select_find_result(self,mod):
        if self.find_result:
            items_len=len(self.find_result)
            self.find_result_index+=mod
            next_item=self.find_result[self.find_result_index%items_len]

            self.find_tree.focus(next_item)

            if self.find_dialog_shown:
                #focus is still on find dialog
                self.find_tree.selection_set(next_item)
            else:
                self.find_tree.selection_set(next_item)
                self.tree_semi_focus(self.find_tree)

            self.find_tree.see(next_item)
            self.find_tree.update()

            if self.find_tree==self.main_tree:
                self.main_tree_sel_change(next_item)
            #else:
            #    self.files_tree_sel_change(next_item)

            if mod>0:
                self.status('Find next %s' % self.find_expression_prev)
            else:
                self.status('Find Previous %s' % self.find_expression_prev)

    def tag_toggle_selected(self,tree, *items):
        self_FILE=self.FILE
        self_CRC=self.CRC
        self_invert_mark=self.invert_mark

        self_main_tree_item=self.main_tree.item
        #self_files_tree_item=self.files_tree.item
        tree_set=tree.set

        for item in items:
            if tree_set(item,'kind')==self_FILE:
                self_invert_mark(item, self.main_tree)
                #try:
                    #self_files_tree_item(item,tags=self_main_tree_item(item)['tags'])
                #except Exception :
                #    pass
            elif tree_set(item,'kind')==self_CRC:
                self.tag_toggle_selected(tree, *tree.get_children(item) )

        #self.calc_mark_stats_groups()
        self.calc_mark_stats_folder()

    KEY_DIRECTION={}
    KEY_DIRECTION['Prior']=-1
    KEY_DIRECTION['Next']=1
    KEY_DIRECTION['Home']=0
    KEY_DIRECTION['End']=-1

    reftuple1=('1','2','3','4','5','6','7')
    reftuple2=('exclam','at','numbersign','dollar','percent','asciicircum','ampersand')

    @block_actions_processing
    @gui_block
    def goto_next_prev_record(self,direction):
        #status ='selecting next record' if direction==1 else 'selecting prev record'

        current_record_name=None
        #current_path_components_reversed=[]

        loop_item=self.main_tree.focus()

        while not current_record_name:
            temp_record_name = tree.set(loop_item,'record')
            if temp_record_name:
                current_record_name=temp_record_name
                break
            else:
                path = tree.set(loop_item,'path')
                #current_path_components_reversed.append(path)
                loop_item=tree.parent(loop_item)

        print('current_record_name:',current_record_name)

        if children := self.main_tree_get_children():
            #if next_item:=children[index]:
            #    self.select_and_focus(next_item)
            pass


        tree=self.main_tree
        current_item=self.sel_item
        self_sel_item = self.sel_item

        self_my_next = self.my_next
        self_my_prev = self.my_prev

        tree_set = tree.set

        self_CRC = self.CRC

        move_func = lambda item : (self_my_next(tree,item) if direction==1 else self_my_prev(tree,item))

        while current_item:
            current_item = move_func(current_item)
            if tree_set(current_item,'kind')==self_CRC:
                self.select_and_focus(current_item)
                self.status(status,do_log=False)
                break
            if current_item==self_sel_item:
                self.status('%s ... (no file)' % status,do_log=False)
                break

    @catched
    def goto_first_last_record(self,index):
        #print('goto_first_last_record',index)
        if children := self.main_tree_get_children():
            if next_item:=children[index]:
                self.select_and_focus(next_item)

    def my_next(self,tree,item):
        if children := tree.get_children(item):
            next_item=children[0]
        else:
            next_item=tree.next(item)

        if not next_item:
            next_item = tree.next(tree.parent(item))

        if not next_item:
            try:
                next_item=tree.get_children()[0]
            except:
                return None

        return next_item

    def my_prev(self,tree,item):
        prev_item=tree.prev(item)

        if prev_item:
            if prev_children := tree.get_children(prev_item):
                prev_item = prev_children[-1]
        else:
            prev_item = tree.parent(item)

        if not prev_item:
            try:
                last_parent=tree.get_children()[-1]
            except :
                return None

            if last_parent_children := tree.get_children(last_parent):
                prev_item=last_parent_children[-1]
            else:
                prev_item=last_parent
        return prev_item


    current_record=None
    def main_tree_select(self,event):
        #print('main_tree_select',event)

        item=self.main_tree.focus()
        parent = self.main_tree.parent(item)

        if not parent:
            record_name = self.main_tree.item(item,'text')
            self.status_record_configure(text=record_name)
            self.current_record = record = self.item_to_record[item]
            self.status_scan_path_configure(text=record.db.path)

    #def main_key_press(self,event):
    #    print('main_key_press',event.keysym)
    #    if self.actions_processing:
    #        self.hide_tooltip()
    #        self.menubar_unpost()
    #        self.popup_groups_unpost()
    #        try:
    #            tree=event.widget
    #            item=tree.focus()
    #            key=event.keysym

    #            if key in ("Prior","Next"):
    #                self.goto_next_prev_record(self.KEY_DIRECTION[key])

    #        except Exception as e:
    #            #l_error(e)
    #            print(e)
    #            self.info_dialog_on_main.show('INTERNAL ERROR',str(e))

    def key_press(self,event):
        #print('key_press',event.keysym)

        if self.actions_processing:
            #self.main.unbind_class('Treeview','<KeyPress>')

            self.hide_tooltip()
            self.menubar_unpost()
            self.popup_groups_unpost()
            #self.popup_folder_unpost()

            try:
                tree=event.widget
                item=tree.focus()
                key=event.keysym
                #state=event.state

                #if key in ("Up","Down"):
                #    new_item = self.my_next(tree,item) if key=='Down' else self.my_prev(tree,item)

                #    if new_item:
                #        tree.focus(new_item)
                #        tree.see(new_item)
                #        tree.selection_set(tree.focus())

                #        if tree==self.main_tree:
                #            self.main_tree_sel_change(new_item)
                        #else:
                        #    self.files_tree_sel_change(new_item)
                #el
                if key in ("Right","Left"):
                    pass
                    #for record in librer_core.records:
                        #print('record.db.path:',record.db.path,' record.db.time:',record.db.time)
                        #self_main_tree["columns"]=('path','file','size','size_h','ctime','dev','inode','crc','ctime_h','kind')
                        #print(record.file_name,' vs ',self.sel_record)
                        #crc_item=self_main_tree_insert('','end',str(record.db.time),values =(record.db.path,record.db.time),open=True,text= 'label')

                        #if record.file_name == self.sel_record + ".dat":
                        #    path = tree.set(item,'path')
                            #self.fill_files_tree_level(item, record.db.data)


                elif key in ("Prior","Next"):
                    self.goto_next_prev_record(self.KEY_DIRECTION[key])
                elif key in ("Home","End"):
                    self.goto_first_last_record(self.KEY_DIRECTION[key])
                elif key == "space":
                    if tree==self.main_tree:
                        if tree.set(item,'kind')==self.CRC:
                            self.tag_toggle_selected(tree,*tree.get_children(item))
                        else:
                            self.tag_toggle_selected(tree,item)
                    else:
                        self.tag_toggle_selected(tree,item)
                elif key == "Tab":
                    #old_node=tree.focus()
                    #self.tree_semi_focus(self.other_tree[tree])
                    pass
                elif key in ('KP_Multiply','asterisk'):
                    self.mark_on_all(self.invert_mark)
                else:
                    event_str=str(event)

                    alt_pressed = ('0x20000' in event_str) if windows else ('Mod1' in event_str or 'Mod5' in event_str)
                    ctrl_pressed = 'Control' in event_str
                    shift_pressed = 'Shift' in event_str

                    if key=='F3':
                        if shift_pressed:
                            self.find_prev()
                        else:
                            self.find_next()

                    #elif key == "Right":
                    #elif key == "Left":
                    elif key in ('KP_Add','plus'):
                        self.mark_expression(self.set_mark,'Mark files',ctrl_pressed)
                    elif key in ('KP_Subtract','minus'):
                        self.mark_expression(self.unset_mark,'Unmark files',ctrl_pressed)
                    #elif key == "Delete":
                    #    self.process_files_in_groups_wrapper(DELETE,ctrl_pressed)
                        #if tree==self.main_tree:
                        #else:
                            #self.process_files_in_folder_wrapper(DELETE,self.sel_kind in (self.DIR,self.DIRLINK))
                    #elif key == "Insert":
                    #    if tree==self.main_tree:
                    #        self.process_files_in_groups_wrapper((SOFTLINK,HARDLINK)[shift_pressed],ctrl_pressed)
                    #    else:
                    #        self.process_files_in_folder_wrapper((SOFTLINK,HARDLINK)[shift_pressed],self.sel_kind in (self.DIR,self.DIRLINK))
                    #elif key=='F5':
                    #    self.goto_max_folder(1,-1 if shift_pressed else 1)
                    #elif key=='F6':
                    #    self.goto_max_folder(0,-1 if shift_pressed else 1)
                    #elif key=='F7':
                    #    self.goto_max_group(1,-1 if shift_pressed else 1)
                    #elif key=='F8':
                    #    self.goto_max_group(0,-1 if shift_pressed else 1)
                    elif key=='BackSpace':
                        #self.go_to_parent_dir()
                        pass
                    elif key in ('i','I'):
                        if ctrl_pressed:
                            self.mark_on_all(self.invert_mark)
                        else:
                            if tree==self.main_tree:
                                self.mark_in_group(self.invert_mark)
                            else:
                                self.mark_in_folder(self.invert_mark)
                    elif key in ('o','O'):
                        if ctrl_pressed:
                            if shift_pressed:
                                self.mark_all_by_ctime('oldest',self.unset_mark)
                            else:
                                self.mark_all_by_ctime('oldest',self.set_mark)
                        else:
                            if tree==self.main_tree:
                                self.mark_in_group_by_ctime('oldest',self.invert_mark)
                    elif key in ('y','Y'):
                        if ctrl_pressed:
                            if shift_pressed:
                                self.mark_all_by_ctime('youngest',self.unset_mark)
                            else:
                                self.mark_all_by_ctime('youngest',self.set_mark)
                        else:
                            if tree==self.main_tree:
                                self.mark_in_group_by_ctime('youngest',self.invert_mark)
                    elif key in ('c','C'):
                        if ctrl_pressed:
                            if shift_pressed:
                                self.clip_copy_file()
                            else:
                                self.clip_copy_full_path_with_file()
                        else:
                            self.clip_copy_full()

                    elif key in ('a','A'):
                        if tree==self.main_tree:
                            if ctrl_pressed:
                                self.mark_on_all(self.set_mark)
                            else:
                                self.mark_in_group(self.set_mark)
                        else:
                            self.mark_in_folder(self.set_mark)

                    elif key in ('n','N'):
                        if tree==self.main_tree:
                            if ctrl_pressed:
                                self.mark_on_all(self.unset_mark)
                            else:
                                self.mark_in_group(self.unset_mark)
                        else:
                            self.mark_in_folder(self.unset_mark)
                    #elif key in ('d','D'):
                        #if tree==self.files_tree:
                        #    if shift_pressed:
                        #        self.sel_dir(self.unset_mark)
                        #    else:
                        #        self.sel_dir(self.set_mark)

                    #elif key in ('r','R'):
                        #if tree==self.files_tree:

                        #    self.files_tree_update()
                        #    self.tree_semi_focus(self.files_tree)
                        #    try:
                        #        self.files_tree.focus(self.sel_item)
                        #    except Exception :
                        #        pass
                    elif key in self.reftuple1:
                        index = self.reftuple1.index(key)

                        #if index<len(librer_core.scanned_paths):
                            #if tree==self.main_tree:
                                #self.action_on_path(librer_core.scanned_paths[index],self.set_mark,ctrl_pressed)
                    elif key in self.reftuple2:
                        index = self.reftuple2.index(key)

                        #if index<len(librer_core.scanned_paths):
                        #    if tree==self.main_tree:
                        #        self.action_on_path(librer_core.scanned_paths[index],self.unset_mark,ctrl_pressed)
                    #elif key in ('KP_Divide','slash'):
                    #    if tree==self.main_tree:
                    #        self.mark_subpath(self.set_mark,True)
                    #elif key=='question':
                    #    if tree==self.main_tree:
                    #        self.mark_subpath(self.unset_mark,True)
                    elif key in ('f','F'):
                        self.finder_wrapper_show()

                    elif key=='Return':
                        item=tree.focus()
                        if item:
                            self.tree_action(tree,item,alt_pressed)
                    #else:
                    #    print(key)
                    #    print(event_str)

            except Exception as e:
                l_error(e)
                self.info_dialog_on_main.show('INTERNAL ERROR',str(e))

            if tree_focus:=tree.focus():
                tree.selection_set(tree_focus)
            #self.main.bind_class('Treeview','<KeyPress>', self.key_press )

#################################################
    def select_and_focus(self,item):
        #print('select_and_focus',item)
        #if try_to_show_all:
        #    self.main_tree_see(self.main_tree_get_children(item)[-1])
        #    self.main_tree.update()

        self.main_tree_see(item)
        self.main_tree_focus(item)
        #self.main_tree.selection_set(item)

        #self.tree_semi_focus(self.main_tree)
        self.main_tree.update()

        self.main_tree_sel_change(item)

    def tree_on_mouse_button_press(self,event,toggle=False):
        self.menubar_unpost()
        self.hide_tooltip()
        self.popup_groups_unpost()
        #self.popup_folder_unpost()

        if self.actions_processing:
            tree=event.widget

            region = tree.identify("region", event.x, event.y)

            if region == 'separator':
                return None

            if region == 'heading':
                if (colname:=tree.column(tree.identify_column(event.x),'id') ) in self.REAL_SORT_COLUMN:
                    self.column_sort_click(tree,colname)
            elif item:=tree.identify('item',event.x,event.y):
                tree.selection_remove(tree.selection())

                tree.focus(item)
                tree.selection_set(item)
                self.tree_semi_focus(tree)

                if tree==self.main_tree:
                    self.main_tree_sel_change(item)
                #else:
                #    self.files_tree_sel_change(item)

                if toggle:
                    self.tag_toggle_selected(tree,item)
                #prevents processing of expanding nodes
                return "break"

        return None

    def tree_semi_focus(self,tree):
        item=None

        if sel:=tree.selection():
            item=sel[0]

        if not item:
            item=tree.focus()

        if not item:
            if tree==self.main_tree:
                try:
                    item = tree.get_children()[0]
                except :
                    pass
            #else:
            #    try:
            #        item = self.current_folder_items[0]
            #    except :
            #        pass

        if item:
            self.sel_tree=tree

            tree.focus_set()
            tree.configure(style='semi_focus.Treeview')
            #self.other_tree[tree].configure(style='no_focus.Treeview')

            tree.focus(item)
            tree.see(item)
            tree.selection_set(item)

            if tree==self.main_tree:
                self.main_tree_sel_change(item,True)
            #else:
            #    self.files_tree_sel_change(item)

    #def set_full_path_to_file_win(self):
    #    self.sel_full_path_to_file=str(Path(sep.join([self.sel_path_full,self.sel_file]))) if self.sel_path_full and self.sel_file else None

    #def set_full_path_to_file_lin(self):
    #    self.sel_full_path_to_file=(self.sel_path_full+self.sel_file if self.sel_path_full=='/' else sep.join([self.sel_path_full,self.sel_file])) if self.sel_path_full and self.sel_file else None

    #set_full_path_to_file = set_full_path_to_file_win if windows else set_full_path_to_file_lin

    def sel_path_set(self,path):
        if self.sel_path_full != path:
            self.sel_path_full = path
            self.status_scan_path_configure(text=self.sel_path_full)

            self.dominant_groups_folder={0:-1,1:-1}

    @catched
    def main_tree_sel_change(self,item,force=False,change_status_line=True):
        self.sel_item = item

        if change_status_line :
            self.status()

        self_main_tree_set_item=lambda x : self.main_tree_set(item,x)

        self.sel_file = self_main_tree_set_item('file')

        new_crc = self_main_tree_set_item('crc')
        if self.sel_crc != new_crc:
            self.sel_crc = new_crc

            self.dominant_groups_index={0:-1,1:-1}

        path=self_main_tree_set_item('path')
        record=self_main_tree_set_item('file')
        #print('sel record:',record)

        self.sel_record = record
        #self.files_tree_update()
        return

        if record!=self.sel_record or force:
            if self.find_tree_index==1:
                self.find_result=()

            self.sel_path = None
            self.sel_path_set(None)

            #self.set_full_path_to_file()

        self.sel_kind = self_main_tree_set_item('kind')

        #self.files_tree_update()
        #if self.sel_kind==self.FILE:
        #else:
        #    self.files_tree_update_none()



    def menubar_unpost(self):
        try:
            self.menubar.unpost()
        except Exception as e:
            l_error(e)

    def context_menu_show(self,event):

        tree=event.widget

        if tree.identify("region", event.x, event.y) == 'heading':
            return

        if not self.actions_processing:
            return

        tree.focus_set()
        self.tree_on_mouse_button_press(event)
        tree.update()

        item_actions_state=('disabled','normal')[self.sel_item is not None]

        pop=self.popup_groups if tree==self.main_tree else self.popup_folder

        pop.delete(0,'end')

        pop_add_separator = pop.add_separator
        pop_add_cascade = pop.add_cascade
        pop_add_command = pop.add_command

        c_nav = Menu(self.menubar,tearoff=0,bg=self.bg_color)
        c_nav_add_command = c_nav.add_command
        c_nav_add_separator = c_nav.add_separator

        c_nav_add_command(label = 'Go to next record'       ,command = lambda : self.goto_next_prev_record(1),accelerator="Pg Down",state='normal', image = self.ico['empty'],compound='left')
        c_nav_add_command(label = 'Go to previous record'   ,command = lambda : self.goto_next_prev_record(-1), accelerator="Pg Up",state='normal', image = self.ico['empty'],compound='left')
        c_nav_add_separator()
        c_nav_add_command(label = 'Go to first crc group'       ,command = lambda : self.goto_first_last_record(0),accelerator="Home",state='normal', image = self.ico['empty'],compound='left')
        c_nav_add_command(label = 'Go to last crc group'   ,command = lambda : self.goto_first_last_record(-1), accelerator="End",state='normal', image = self.ico['empty'],compound='left')

        pop_add_command(label = 'Scan ...',  command = self.scan_dialog_show,accelerator='S',image = self.ico['scan'],compound='left')
        pop_add_command(label = 'Settings ...',  command = self.settings_dialog.show,accelerator='F2',image = self.ico['settings'],compound='left')
        pop_add_separator()
        pop_add_command(label = 'Copy full path',command = self.clip_copy_full_path_with_file,accelerator='Ctrl+C',state = 'normal' if (self.sel_kind and self.sel_kind!=self.CRC) else 'disabled', image = self.ico['empty'],compound='left')
        #pop_add_command(label = 'Copy only path',command = self.clip_copy_full,accelerator="C",state = 'normal' if self.sel_item!=None else 'disabled')
        pop_add_separator()
        pop_add_command(label = 'Find ...',command = self.finder_wrapper_show,accelerator="F",state = 'normal' if self.sel_item is not None else 'disabled', image = self.ico['empty'],compound='left')
        pop_add_command(label = 'Find next',command = self.find_next,accelerator="F3",state = 'normal' if self.sel_item is not None else 'disabled', image = self.ico['empty'],compound='left')
        pop_add_command(label = 'Find prev',command = self.find_prev,accelerator="Shift+F3",state = 'normal' if self.sel_item is not None else 'disabled', image = self.ico['empty'],compound='left')
        pop_add_separator()

        pop_add_command(label = 'Exit',  command = self.exit ,image = self.ico['exit'],compound='left')

        try:
            pop.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            print(e)

        pop.grab_release()

    @logwrapper
    def column_sort_click(self, tree, colname):

        prev_colname,prev_sort_index,prev_is_numeric,prev_reverse,prev_updir_code,prev_dir_code,prev_non_dir_code=self.column_sort_last_params[tree]
        reverse = not prev_reverse if colname == prev_colname else prev_reverse
        tree.heading(prev_colname, text=self.org_label[prev_colname])

        updir_code,dir_code,non_dir_code = (2,1,0) if reverse else (0,1,2)

        sort_index=self.REAL_SORT_COLUMN_INDEX[colname]
        is_numeric=self.REAL_SORT_COLUMN_IS_NUMERIC[colname]
        self.column_sort_last_params[tree]=(colname,sort_index,is_numeric,reverse,updir_code,dir_code,non_dir_code)

        self.column_sort(tree)

    @logwrapper
    def tree_sort_item(self,tree,parent_item,lower_tree):
        colname,sort_index,is_numeric,reverse,updir_code,dir_code,non_dir_code = self.column_sort_last_params[tree]

        real_column_to_sort=self.REAL_SORT_COLUMN[colname]

        tlist=[]
        tree_set = tree.set
        tlist_append = tlist.append

        dir_or_dirlink = (self.DIR,self.DIRLINK)

        for item in (tree.get_children(parent_item) if parent_item else tree.get_children(parent_item)):
            sortval_org=tree_set(item,real_column_to_sort)
            sortval=(int(sortval_org) if sortval_org.isdigit() else 0) if is_numeric else sortval_org

            if lower_tree:
                kind = tree_set(item,'kind')
                code= dir_code if kind in dir_or_dirlink else non_dir_code
                tlist_append( ( (code,sortval),item) )
            else:
                tlist_append( (sortval,item) )

        tlist.sort(reverse=reverse,key=lambda x: x[0])

        if not parent_item:
            parent_item=''

        tree_move = tree.move
        _ = {tree_move(item, parent_item, index) for index,(val_tuple,item) in enumerate(sorted(tlist,reverse=reverse,key=lambda x: x[0]) ) }

        if lower_tree:
            self.current_folder_items = tree.get_children()

    @restore_status_line
    @block_actions_processing
    @gui_block
    @logwrapper
    def column_sort(self, tree):
        self.status('Sorting...')
        colname,sort_index,is_numeric,reverse,updir_code,dir_code,non_dir_code = self.column_sort_last_params[tree]

        self.column_sort_set_arrow(tree)

        self_tree_sort_item = self.tree_sort_item

        if tree==self.main_tree:
            if colname in ('path','file','ctime_h'):
                for crc in tree.get_children():
                    self_tree_sort_item(tree,crc,False)
            else:
                self_tree_sort_item(tree,None,False)
        else:
            self_tree_sort_item(tree,None,True)

        tree.update()

    def column_sort_set_arrow(self, tree):
        colname,sort_index,is_numeric,reverse,updir_code,dir_code,non_dir_code = self.column_sort_last_params[tree]
        tree.heading(colname, text=self.org_label[colname] + ' ' + str('\u25BC' if reverse else '\u25B2') )

    def path_to_scan_add(self,path):
        if len(self.paths_to_scan_from_dialog)<10:
            self.paths_to_scan_from_dialog.append(path)
        else:
            l_error('can\'t add:%s. limit exceeded',path)

    scanning_in_progress=False
    def scan_wrapper(self):
        if self.scanning_in_progress:
            l_warning('scan_wrapper collision')
            return

        self.scanning_in_progress=True

        try:
            if self.scan():
                self.scan_dialog_hide_wrapper()
        except Exception as e:
            l_error(e)
            self.status(str(e))

        self.scanning_in_progress=False

    def scan_dialog_hide_wrapper(self):
        self.scan_dialog.hide()
        self.tree_semi_focus(self.main_tree)

    prev_status_progress_text=''
    def status_progress(self,text='',image='',do_log=False):
        if text != self.prev_status_progress_text:
            self.progress_dialog_on_scan.lab[1].configure(text=text)
            self.progress_dialog_on_scan.area_main.update()
            self.prev_status_progress_text=text

    @restore_status_line
    @logwrapper
    def scan(self):
        self.status('Scanning...')
        self.cfg.write()

        #librer_core.reset()
        #self.status_path_configure(text='')
        self.records_show()

        path_to_scan_from_entry = self.path_to_scan_entry_var.get()
        print('path_to_scan_from_entry:',path_to_scan_from_entry)

        exclude_from_entry = [var.get() for var in self.exclude_entry_var.values()]

        #if res:=librer_core.set_exclude_masks(self.cfg_get_bool(CFG_KEY_EXCLUDE_REGEXP),exclude_from_entry):
        #    self.info_dialog_on_scan.show('Error. Fix expression.',res)
        #    return False
        #self.cfg.set(CFG_KEY_EXCLUDE,'|'.join(exclude_from_entry))


        if not path_to_scan_from_entry:
            self.info_dialog_on_scan.show('Error. No paths to scan.','Add paths to scan.')
            return False

        new_core_element = librer_core.create(self.scan_label_entry_var.get(),path_to_scan_from_entry)

        #new_core_element.db.path = path_to_scan_from_entry
        #if res:=librer_core.set_path_to_scan(path_to_scan_from_entry):
        #    self.info_dialog_on_scan.show('Error. Fix paths selection.',res)
        #    return False

        #librer_core.scan_update_info_path_nr=self.scan_update_info_path_nr

        self.main_update()

        #############################
        self_progress_dialog_on_scan = self.progress_dialog_on_scan
        self_progress_dialog_on_scan_lab = self_progress_dialog_on_scan.lab
        self_progress_dialog_on_scan_area_main_update = self_progress_dialog_on_scan.area_main.update

        self_progress_dialog_on_scan_progr1var = self_progress_dialog_on_scan.progr1var
        self_progress_dialog_on_scan_progr2var = self_progress_dialog_on_scan.progr2var

        self_progress_dialog_on_scan_lab_r1_config = self_progress_dialog_on_scan.lab_r1.config
        self_progress_dialog_on_scan_lab_r2_config = self_progress_dialog_on_scan.lab_r2.config

        str_self_progress_dialog_on_scan_abort_button = str(self_progress_dialog_on_scan.abort_button)
        #############################

        self.scan_dialog.widget.update()
        self.tooltip_message[str_self_progress_dialog_on_scan_abort_button]='If you abort at this stage,\nyou will not get any results.'
        self_progress_dialog_on_scan.abort_button.configure(image=self.ico['cancel'],text='Cancel',compound='left')
        self_progress_dialog_on_scan.abort_button.pack(side='bottom', anchor='n',padx=5,pady=5)

        self.action_abort=False
        self_progress_dialog_on_scan.abort_button.configure(state='normal')

        #self.update_scan_path_nr=False

        #librer_core.log_skipped = self.log_skipped_var.get()
        self.log_skipped = self.log_skipped_var.get()

        scan_thread=Thread(target=lambda : new_core_element.scan(librer_core.db_dir),daemon=True)
        scan_thread.start()

        self_progress_dialog_on_scan.lab_l1.configure(text='Total space:')
        self_progress_dialog_on_scan.lab_l2.configure(text='Files number:' )

        self_progress_dialog_on_scan_progr1var.set(0)
        self_progress_dialog_on_scan_progr2var.set(0)

        self_progress_dialog_on_scan.show('Scanning')
        #,image=self.ico['empty'],image_text=' '

        update_once=True

        prev_data={}
        new_data={}
        prev_path_nr=-1
        for i in range(1,5):
            prev_data[i]=''
            new_data[i]=''

        time_without_busy_sign=0

        hr_index=0

        self_progress_dialog_on_scan_progr1var.set(0)
        self_progress_dialog_on_scan_lab_r1_config(text='- - - -')
        self_progress_dialog_on_scan_progr2var.set(0)
        self_progress_dialog_on_scan_lab_r2_config(text='- - - -')

        wait_var=BooleanVar()
        wait_var.set(False)

        self_progress_dialog_on_scan_lab[2].configure(image='',text='')

        #self_icon_nr = self.icon_nr
        self_tooltip_message = self.tooltip_message
        self_configure_tooltip = self.configure_tooltip

        scan_thread_is_alive = scan_thread.is_alive

        self_hg_ico = self.hg_ico
        len_self_hg_ico = len(self_hg_ico)

        local_core_bytes_to_str = core_bytes_to_str

        while scan_thread_is_alive():
            new_data[3]=local_core_bytes_to_str(new_core_element.db.size)
            new_data[4]='%s files' % new_core_element.db.files

            anything_changed=False
            for i in (3,4):
                if new_data[i] != prev_data[i]:
                    prev_data[i]=new_data[i]
                    self_progress_dialog_on_scan_lab[i].configure(text=new_data[i])
                    anything_changed=True

            now=time()
            #if self.update_scan_path_nr:
            #    self.update_scan_path_nr=False
            #    self_progress_dialog_on_scan_lab[0].configure(image=self_icon_nr[librer_core.info_path_nr])
            #    self_progress_dialog_on_scan_lab[1].configure(text=librer_core.info_path_to_scan)

            if anything_changed:
                time_without_busy_sign=now

                if update_once:
                    update_once=False
                    self_tooltip_message[str_self_progress_dialog_on_scan_abort_button]='If you abort at this stage,\nyou will not get any results.'
                    self_configure_tooltip(str_self_progress_dialog_on_scan_abort_button)

                    self_progress_dialog_on_scan_lab[2].configure(image=self.ico['empty'])
            else :
                if now>time_without_busy_sign+1.0:
                    self_progress_dialog_on_scan_lab[2].configure(image=self_hg_ico[hr_index],text = '', compound='left')
                    hr_index=(hr_index+1) % len_self_hg_ico

                    self_tooltip_message[str_self_progress_dialog_on_scan_abort_button]='currently scanning:\n%s...' % new_core_element.info_line
                    self_configure_tooltip(str_self_progress_dialog_on_scan_abort_button)
                    update_once=True

            self_progress_dialog_on_scan_area_main_update()

            if self.action_abort:
                librer_core.abort()
                break

            self.main.after(100,lambda : wait_var.set(not wait_var.get()))
            self.main.wait_variable(wait_var)

        scan_thread.join()

        if self.action_abort:
            self_progress_dialog_on_scan.hide(True)
            return False

        #############################
        #if librer_core.sum_size==0:
        #    self_progress_dialog_on_scan.hide(True)
        #    self.info_dialog_on_scan.show('Cannot Proceed.','No Duplicates.')
        #    return False
        #############################

        self.records_show()

        self_progress_dialog_on_scan.hide(True)

        return

        self_status=self.status=self.status_progress

        self_status('Calculating CRC ...')
        self_progress_dialog_on_scan.widget.title('CRC calculation')

        self_tooltip_message[str_self_progress_dialog_on_scan_abort_button]='If you abort at this stage,\npartial results may be available\n(if any records are found).'
        self_progress_dialog_on_scan.abort_button.configure(image=self.ico['abort'],text='Abort',compound='left')

        self_status('Starting CRC threads ...')
        crc_thread=Thread(target=librer_core.crc_calc,daemon=True)
        crc_thread.start()

        update_once=True
        self_progress_dialog_on_scan_lab[0].configure(image='',text='')
        self_progress_dialog_on_scan_lab[1].configure(image='',text='')
        self_progress_dialog_on_scan_lab[2].configure(image='',text='')
        self_progress_dialog_on_scan_lab[3].configure(image='',text='')
        self_progress_dialog_on_scan_lab[4].configure(image='',text='')

        prev_progress_size=0
        prev_progress_quant=0

        crc_thread_is_alive = crc_thread.is_alive
        self_progress_dialog_on_scan_progr1var_set = self_progress_dialog_on_scan_progr1var.set
        self_progress_dialog_on_scan_progr2var_set = self_progress_dialog_on_scan_progr2var.set

        core_bytes_to_str_librer_core_sum_size = local_core_bytes_to_str(librer_core.sum_size)

        self_main_after = self.main.after
        wait_var_get = wait_var.get
        wait_var_set = wait_var.set
        self_main_wait_variable = self.main.wait_variable

        while crc_thread_is_alive():
            anything_changed=False

            size_progress_info=librer_core.info_size_done_perc
            if size_progress_info!=prev_progress_size:
                prev_progress_size=size_progress_info

                self_progress_dialog_on_scan_progr1var_set(size_progress_info)
                self_progress_dialog_on_scan_lab_r1_config(text='%s / %s' % (local_core_bytes_to_str(librer_core.info_size_done),core_bytes_to_str_librer_core_sum_size))
                anything_changed=True

            quant_progress_info=librer_core.info_files_done_perc
            if quant_progress_info!=prev_progress_quant:
                prev_progress_quant=quant_progress_info

                self_progress_dialog_on_scan_progr2var_set(quant_progress_info)
                self_progress_dialog_on_scan_lab_r2_config(text='%s / %s' % (librer_core.info_files_done,librer_core.info_total))
                anything_changed=True

            if anything_changed:
                if librer_core.info_found_groups:
                    #new_data[1]='Results'
                    new_data[2]='records: %s' % librer_core.info_found_groups
                    new_data[3]='space: %s' % local_core_bytes_to_str(librer_core.info_found_dupe_space)
                    new_data[4]='folders: %s' % librer_core.info_found_folders

                    for i in (2,3,4):
                        if new_data[i] != prev_data[i]:
                            prev_data[i]=new_data[i]
                            self_progress_dialog_on_scan_lab[i].configure(text=new_data[i])

                self_progress_dialog_on_scan_area_main_update()

            now=time()
            if anything_changed:
                time_without_busy_sign=now
                #info_line = librer_core.info_line if len(librer_core.info_line)<48 else ('...%s' % librer_core.info_line[-48:])
                #self_progress_dialog_on_scan_lab[1].configure(text=info_line)

                if update_once:
                    update_once=False
                    self_tooltip_message[str_self_progress_dialog_on_scan_abort_button]='If you abort at this stage,\npartial results may be available\n(if any records are found).'
                    self_configure_tooltip(str_self_progress_dialog_on_scan_abort_button)

                    self_progress_dialog_on_scan_lab[0].configure(image=self.ico['empty'])
            else :
                if now>time_without_busy_sign+1.0:
                    self_progress_dialog_on_scan_lab[0].configure(image=self_hg_ico[hr_index],text='')
                    hr_index=(hr_index+1) % len_self_hg_ico

                    self_tooltip_message[str_self_progress_dialog_on_scan_abort_button]='crc calculating:\n%s...' % librer_core.info_line
                    self_configure_tooltip(str_self_progress_dialog_on_scan_abort_button)
                    update_once=True

            if librer_core.can_abort:
                if self.action_abort:
                    self_progress_dialog_on_scan_lab[0].configure(image='',text='Aborted.')
                    self_progress_dialog_on_scan_lab[1].configure(text='... Rendering data ...')
                    self_progress_dialog_on_scan_lab[2].configure(text='')
                    self_progress_dialog_on_scan_lab[3].configure(text='')
                    self_progress_dialog_on_scan_lab[4].configure(text='')
                    self_progress_dialog_on_scan_area_main_update()
                    librer_core.abort()
                    break

            self_status(librer_core.info)

            self_main_after(100,lambda : wait_var_set(not wait_var_get()))
            self_main_wait_variable(wait_var)

        self_progress_dialog_on_scan.widget.config(cursor="watch")

        if not self.action_abort:
            self_progress_dialog_on_scan_lab[0].configure(image='',text='Finished.')
            self_progress_dialog_on_scan_lab[1].configure(image='',text='... Rendering data ...')
            self_progress_dialog_on_scan_lab[2].configure(image='',text='')
            self_progress_dialog_on_scan_lab[3].configure(image='',text='')
            self_progress_dialog_on_scan_lab[4].configure(image='',text='')
            self_progress_dialog_on_scan_area_main_update()

        #self_status('Finishing CRC Thread...')
        #############################

        #self_progress_dialog_on_scan.label.configure(text='\n\nrendering data ...\n')
        self_progress_dialog_on_scan.abort_button.configure(state='disabled',text='',image='')
        self_progress_dialog_on_scan.abort_button.pack_forget()
        self_tooltip_message[str_self_progress_dialog_on_scan_abort_button]=''
        self_progress_dialog_on_scan.widget.update()
        self.main.focus_set()

        crc_thread.join()
        #self_progress_dialog_on_scan.label.update()

        self.records_show()

        self_progress_dialog_on_scan.widget.config(cursor="")
        self_progress_dialog_on_scan.hide(True)
        self.status=self.status_main_win if windows else self.status_main

        if self.action_abort:
            self.info_dialog_on_scan.show('CRC Calculation aborted.','\nResults are partial.\nSome files may remain unidentified as duplicates.')

        return True

    def scan_dialog_show(self,do_scan=False):
        self.exclude_mask_update()

        self.scan_dialog.do_command_after_show=self.scan if do_scan else None

        self.scan_dialog.show()

        return

        if librer_core.scanned_paths:
            self.paths_to_scan_from_dialog=librer_core.scanned_paths.copy()

    def exclude_regexp_set(self):
        self.cfg.set_bool(CFG_KEY_EXCLUDE_REGEXP,self.exclude_regexp_scan.get())

    def exclude_mask_update(self) :
        for subframe in self.exclude_frames:
            subframe.destroy()

        self.exclude_frames=[]
        self.exclude_entry_var={}

        row=0

        for entry in self.cfg.get(CFG_KEY_EXCLUDE,'').split('|'):
            if entry:
                (frame:=Frame(self.exclude_frame,bg=self.bg_color)).grid(row=row,column=0,sticky='news',columnspan=3)
                self.exclude_frames.append(frame)

                self.exclude_entry_var[row]=StringVar(value=entry)
                Entry(frame,textvariable=self.exclude_entry_var[row]).pack(side='left',expand=1,fill='both',pady=1,padx=(2,0))

                remove_expression_button=Button(frame,image=self.ico['delete'],command=lambda entrypar=entry: self.exclude_mask_remove(entrypar),width=3)
                remove_expression_button.pack(side='right',padx=2,pady=1,fill='y')

                remove_expression_button.bind("<Motion>", lambda event : self.motion_on_widget(event,'Remove expression from list.'))
                remove_expression_button.bind("<Leave>", lambda event : self.widget_leave())

                row+=1

    def path_to_scan_add_dialog(self):
        initialdir = self.last_dir if self.last_dir else self.cwd
        if res:=askdirectory(title='Select Directory',initialdir=initialdir,parent=self.scan_dialog.area_main):
            self.last_dir=res
            self.path_to_scan_entry_var.set(normpath(abspath(res)))

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
        orglist=self.cfg.get(CFG_KEY_EXCLUDE,'').split('|')
        orglist.append(mask)
        self.cfg.set(CFG_KEY_EXCLUDE,'|'.join(orglist))
        self.exclude_mask_update()

    def exclude_mask_remove(self,mask) :
        orglist=self.cfg.get(CFG_KEY_EXCLUDE,'').split('|')
        orglist.remove(mask)
        if '' in orglist:
            orglist.remove('')
        self.cfg.set(CFG_KEY_EXCLUDE,'|'.join(orglist))
        self.exclude_mask_update()

    def settings_ok(self):
        update0=False
        update1=False
        update2=False

        if self.cfg_get_bool(CFG_KEY_FULL_CRC)!=self.show_full_crc.get():
            self.cfg.set_bool(CFG_KEY_FULL_CRC,self.show_full_crc.get())
            update1=True
            update2=True

        if self.cfg_get_bool(CFG_KEY_FULL_PATHS)!=self.show_full_paths.get():
            self.cfg.set_bool(CFG_KEY_FULL_PATHS,self.show_full_paths.get())
            update1=True
            update2=True

        if self.cfg_get_bool(CFG_KEY_CROSS_MODE)!=self.cross_mode.get():
            self.cfg.set_bool(CFG_KEY_CROSS_MODE,self.cross_mode.get())
            update0=True

        if self.cfg_get_bool(CFG_KEY_REL_SYMLINKS)!=self.create_relative_symlinks.get():
            self.cfg.set_bool(CFG_KEY_REL_SYMLINKS,self.create_relative_symlinks.get())

        if self.cfg_get_bool(CFG_ERASE_EMPTY_DIRS)!=self.erase_empty_directories.get():
            self.cfg.set_bool(CFG_ERASE_EMPTY_DIRS,self.erase_empty_directories.get())

        if self.cfg_get_bool(CFG_ABORT_ON_ERROR)!=self.abort_on_error.get():
            self.cfg.set_bool(CFG_ABORT_ON_ERROR,self.abort_on_error.get())

        if self.cfg_get_bool(CFG_SEND_TO_TRASH)!=self.send_to_trash.get():
            self.cfg.set_bool(CFG_SEND_TO_TRASH,self.send_to_trash.get())

        if self.cfg_get_bool(CFG_ALLOW_DELETE_ALL)!=self.allow_delete_all.get():
            self.cfg.set_bool(CFG_ALLOW_DELETE_ALL,self.allow_delete_all.get())

        if self.cfg_get_bool(CFG_SKIP_INCORRECT_GROUPS)!=self.skip_incorrect_groups.get():
            self.cfg.set_bool(CFG_SKIP_INCORRECT_GROUPS,self.skip_incorrect_groups.get())

        if self.cfg_get_bool(CFG_ALLOW_DELETE_NON_DUPLICATES)!=self.allow_delete_non_duplicates.get():
            self.cfg.set_bool(CFG_ALLOW_DELETE_NON_DUPLICATES,self.allow_delete_non_duplicates.get())

        if self.cfg_get_bool(CFG_CONFIRM_SHOW_CRCSIZE)!=self.confirm_show_crc_and_size.get():
            self.cfg.set_bool(CFG_CONFIRM_SHOW_CRCSIZE,self.confirm_show_crc_and_size.get())

        if self.cfg_get_bool(CFG_CONFIRM_SHOW_LINKSTARGETS)!=self.confirm_show_links_targets.get():
            self.cfg.set_bool(CFG_CONFIRM_SHOW_LINKSTARGETS,self.confirm_show_links_targets.get())

        if self.cfg.get(CFG_KEY_WRAPPER_FILE)!=self.file_open_wrapper.get():
            self.cfg.set(CFG_KEY_WRAPPER_FILE,self.file_open_wrapper.get())

        if self.cfg.get(CFG_KEY_WRAPPER_FOLDERS)!=self.folders_open_wrapper.get():
            self.cfg.set(CFG_KEY_WRAPPER_FOLDERS,self.folders_open_wrapper.get())

        if self.cfg.get(CFG_KEY_WRAPPER_FOLDERS_PARAMS)!=self.folders_open_wrapper_params.get():
            self.cfg.set(CFG_KEY_WRAPPER_FOLDERS_PARAMS,self.folders_open_wrapper_params.get())

        self.cfg.write()

        self.settings_dialog.hide()

        if update0:
            self.records_show()

        #if update2:
        #    if self.sel_crc and self.sel_item and self.sel_path_full:
        #        self.files_tree_update()
        #    else:
        #        self.files_tree_update_none()

    def settings_reset(self):
        _ = {var.set(cfg_defaults[key]) for var,key in self.settings}
        _ = {var.set(cfg_defaults[key]) for var,key in self.settings_str}

    @catched
    def crc_node_update(self,crc):
        self_main_tree = self.main_tree
        self_main_tree_delete = self_main_tree.delete
        self_get_index_tuple_main_tree = self.get_index_tuple_main_tree

        size=int(self_main_tree.set(crc,'size'))

        if size not in librer_core.files_of_size_of_crc:
            self_main_tree_delete(crc)
            #l_debug('crc_node_update-1 %s',crc)
        elif crc not in librer_core.files_of_size_of_crc[size]:
            self_main_tree_delete(crc)
            #l_debug('crc_node_update-2 %s',crc)
        else:
            crc_dict=librer_core.files_of_size_of_crc[size][crc]
            for item in list(self_main_tree.get_children(crc)):
                index_tuple=self_get_index_tuple_main_tree(item)

                if index_tuple not in crc_dict:
                    self_main_tree_delete(item)
                    #l_debug('crc_node_update-3:%s',item)

            if not self_main_tree.get_children(crc):
                self_main_tree_delete(crc)
                #l_debug('crc_node_update-4:%s',crc)

    def open_item(self,event):
        #print('open_item',event)
        tree=self.main_tree

        item=tree.focus()

        children=tree.get_children(item)
        opened = tree.set(item,'opened')

        if opened=='0' and children:
            tree.delete(*children)

            current_record_name=None
            current_path_components_reversed=[]

            loop_item=item
            while not current_record_name:
                temp_record_name = tree.set(loop_item,'record')
                if temp_record_name:
                    current_record_name=temp_record_name
                    break
                else:
                    path = tree.set(loop_item,'path')
                    current_path_components_reversed.append(path)
                    loop_item=tree.parent(loop_item)

            record_dict={}
            for temp_record in librer_core.records:
                if temp_record.file_name==current_record_name:
                    record_dict=temp_record.db.data
                    break

            #print('current_record:',current_record_name,' current_path_components_reversed:',current_path_components_reversed)
            local_dict=record_dict
            for path_component in reversed(current_path_components_reversed):
                local_dict = local_dict[path_component][5]

            self_ico_folder = self.ico['folder']
            self_FILE = self.FILE
            core_bytes_to_str = core.bytes_to_str
            for entry_name,(is_dir,is_file,is_symlink,size,mtime,sub_dictionary) in sorted(sorted(local_dict.items(),key=lambda x : x[0]),key = lambda x : x[1][0],reverse=True):
                if is_dir:
                    image=self_ico_folder
                else:
                    image=''
                    #self.ico['empty']
                record_item=tree.insert(item,'end',iid=None,values=('','0',entry_name,'file',size,core_bytes_to_str(size),mtime,strftime('%Y/%m/%d %H:%M:%S',localtime(mtime//1000000000)),'info','dev','inode'),open=False,text=entry_name,tags=self_FILE,image=image)
                if sub_dictionary:
                    dummy_sub_item=tree.insert(record_item,'end')

            tree.set(item,'opened','1')

    @block_actions_processing
    @gui_block
    @logwrapper
    def records_show(self):
        #print('records_show...')

        self.menu_disable()

        self_main_tree = self.main_tree

        self_main_tree.delete(*self_main_tree.get_children())

        self_main_tree_insert=self_main_tree.insert

        self_ico_record = self.ico['record']
        self_RECORD = self.RECORD
        core_bytes_to_str = core.bytes_to_str

        self.item_to_record={}
        self_item_to_record = self.item_to_record
        for record in sorted(librer_core.records,key=lambda x : x.file_name):
            #('record','opened','path','file','size','size_h','ctime','ctime_h','info','dev','inode','crc','kind')
            #print('record.file_name:',record.file_name)
            record_db = record.db
            size=record_db.size

            record_item=self_main_tree_insert('','end',iid=None,values=(record.file_name,'0',record_db.path,'record_file',size,core_bytes_to_str(size),record_db.time,strftime('%Y/%m/%d %H:%M:%S',localtime(record_db.get_time())) ),open=False,text=record_db.label,tags=self_RECORD,image=self_ico_record)
            dummy_sub_item=self_main_tree_insert(record_item,'end',text='dummy')

            self_item_to_record[record_item]=record

        self.menu_enable()

        self_status=self.status=self.status_progress

        self_status('')

    def main_tree_update_none(self):
        self.main_tree.selection_remove(self.main_tree.selection())

    def main_tree_update(self,item):
        self_main_tree = self.main_tree

        #self_main_tree.see(self.sel_crc)
        #self_main_tree.update()

        #self_main_tree.selection_set(item)
        self_main_tree.see(item)
        self_main_tree.update()

    current_folder_items=()
    current_folder_items_tagged=set()
    current_folder_items_tagged_clear=current_folder_items_tagged.clear

    #def files_tree_update_none(self):
    #    print('files_tree_update_none')
    #    self.files_tree_configure(takefocus=False)

    #    if self.current_folder_items:
    #        self.files_tree_delete(*self.current_folder_items)

    #    self.status_folder_size_configure(text='')
    #    self.status_folder_quant_configure(text='')

    #    self.status_path_configure(text='')
    #    self.current_folder_items=()

    #    self.current_folder_items_tagged_clear()


    folder_items=set()
    folder_items_clear=folder_items.clear
    folder_items_add=folder_items.add

    #def fill_files_tree_level(self, parent_item, local_dict ):
    #    print('fill_files_tree_level:',parent_item)
    #    for entry in local_dict:
    #        print('  ->',entry)
    #        item=self.main_tree.insert(parent_item,'end',iid=None,values =(entry,entry),open=True,text= 'label',tags=self.FILE)


    #def calc_mark_stats_groups(self):
    #    self.status_all_quant_configure(text=str(len(self.tagged)))
    #    self_iid_to_size=self.iid_to_size
    #    self.status_all_size_configure(text=core_bytes_to_str(sum([self_iid_to_size[iid] for iid in self.tagged])))

    def calc_mark_stats_folder(self):
        self.status_folder_quant_configure(text=str(len(self.current_folder_items_tagged)))

        self_iid_to_size = self.iid_to_size
        self.status_folder_size_configure(text=core_bytes_to_str(sum(self_iid_to_size[iid] for iid in self.current_folder_items_tagged)))

    def mark_in_specified_group_by_ctime(self, action, crc, reverse,select=False):
        self_main_tree = self.main_tree
        self_main_tree_set = self_main_tree.set
        item=sorted([ (item,self_main_tree_set(item,'ctime') ) for item in self_main_tree.get_children(crc)],key=lambda x : int(x[1]),reverse=reverse)[0][0]
        if item:
            action(item,self_main_tree)
            if select:
                self_main_tree.see(item)
                self_main_tree.focus(item)
                self.main_tree_sel_change(item)
                self_main_tree.update()

    #@block_actions_processing
    #@gui_block
    #def mark_all_by_ctime(self,order_str, action):
    #    self.status('Un/Setting marking on all files ...')
    #    reverse=1 if order_str=='oldest' else 0

    #    self_mark_in_specified_group_by_ctime = self.mark_in_specified_group_by_ctime
    #    _ = { self_mark_in_specified_group_by_ctime(action, crc, reverse) for crc in self.main_tree_get_children() }
    #    self.update_marks_folder()
    #    self.calc_mark_stats_groups()
    #    self.calc_mark_stats_folder()

    #@block_actions_processing
    #@gui_block
    #def mark_in_group_by_ctime(self,order_str,action):
    #    self.status('Un/Setting marking in group ...')
    #    reverse=1 if order_str=='oldest' else 0
    #    self.mark_in_specified_group_by_ctime(action,self.sel_crc,reverse,True)
    #    self.update_marks_folder()
    #    self.calc_mark_stats_groups()
    #    self.calc_mark_stats_folder()

    def set_mark(self,item,tree):
        tree.item(item,tags=self.MARK)
        self.tagged_add(item)
        if item in self.current_folder_items:
            self.current_folder_items_tagged_add(item)

    def unset_mark(self,item,tree):
        tree.item(item,tags='')
        self.tagged_discard(item)
        self.current_folder_items_tagged_discard(item)

    def invert_mark(self,item,tree):
        if tree.item(item)['tags']:
            tree.item(item,tags='')
            self.tagged_discard(item)
            self.current_folder_items_tagged_discard(item)
        else:
            tree.item(item,tags=self.MARK)
            self.tagged_add(item)
            self.current_folder_items_tagged_add(item)

    expr_by_tree={}

    def mark_expression(self,action,prompt,all_groups=True):
        tree=self.main.focus_get()

        if tree in self.expr_by_tree:
            initialvalue=self.expr_by_tree[tree]
        else:
            initialvalue='*'

        if tree==self.main_tree:
            range_str = " (all groups)" if all_groups else " (selected group)"
            title='Specify expression for full file path.'
        else:
            range_str = ''
            title='Specify expression for file names in selected directory.'

        if tree==self.main_tree:
            self.mark_dialog_on_groups.show(title,prompt + f'{range_str}', initialvalue,'treat as a regular expression',self.cfg_get_bool(CFG_KEY_USE_REG_EXPR))
            use_reg_expr = self.mark_dialog_on_groups.res_check
            expression = self.mark_dialog_on_groups.res_str
        else:
            self.mark_dialog_on_folder.show(title,prompt + f'{range_str}', initialvalue,'treat as a regular expression',self.cfg_get_bool(CFG_KEY_USE_REG_EXPR))
            use_reg_expr = self.mark_dialog_on_folder.res_check
            expression = self.mark_dialog_on_folder.res_str

        items=[]
        items_append = items.append
        use_reg_expr_info = '(regular expression)' if use_reg_expr else ''

        if expression:
            self.cfg.set_bool(CFG_KEY_USE_REG_EXPR,use_reg_expr)
            self.expr_by_tree[tree]=expression

            self_item_full_path = self.item_full_path
            self_main_tree_get_children = self.main_tree_get_children

            if tree==self.main_tree:
                crc_range = self_main_tree_get_children() if all_groups else [str(self.sel_crc)]

                for crc_item in crc_range:
                    for item in self_main_tree_get_children(crc_item):
                        fullpath = self_item_full_path(item)
                        try:
                            if (use_reg_expr and search(expression,fullpath)) or (not use_reg_expr and fnmatch(fullpath,expression) ):
                                items_append(item)
                        except Exception as e:
                            self.info_dialog_on_main.show('expression Error !',f'expression:"{expression}"  {use_reg_expr_info}\n\nERROR:{e}')
                            tree.focus_set()
                            return

            if items:
                self.main_config(cursor="watch")
                self.menu_disable()
                self.main_update()

                first_item=items[0]

                tree.focus(first_item)
                tree.see(first_item)

                if tree==self.main_tree:
                    for item in items:
                        action(item,tree)

                    self.main_tree_sel_change(first_item)
                else:
                    for item in items:
                        action(item,self.main_tree)


                self.update_marks_folder()
                #self.calc_mark_stats_groups()
                self.calc_mark_stats_folder()

                self.main_config(cursor="")
                self.menu_enable()
                self.main_update()

            else:
                #self.info_dialog_on_main
                self.info_dialog_on_mark[self.sel_tree].show('No files found.',f'expression:"{expression}"  {use_reg_expr_info}\n')

        tree.focus_set()

    dominant_groups_index={0:-1,1:-1}
    dominant_groups_folder={0:-1,1:-1}

    BY_WHAT={0:"by quantity",1:"by sum size"}

    def item_full_path(self,item):
        self_main_tree_set = self.main_tree_set

        path=self_main_tree_set(item,'path')
        file=self_main_tree_set(item,'file')
        return abspath(librer_core.get_full_path_scanned(path,file))

    def file_check_state(self,item):
        fullpath = self.item_full_path(item)
        l_info('checking file: %s',fullpath)
        try:
            stat_res = stat(fullpath)
            ctime_check=str(stat_res.st_ctime_ns)
        except Exception as e:
            self.status(str(e))
            mesage = f'can\'t check file: {fullpath}\n\n{e}'
            l_error(mesage)
            return mesage

        if ctime_check != (ctime:=self.main_tree_set(item,'ctime')) :
            message = {f'ctime inconsistency {ctime_check} vs {ctime}'}
            return message

        return None

    @logwrapper
    def get_this_or_existing_parent(self,path):
        if path:
            if path_exists(path):
                return path

            return self.get_this_or_existing_parent(Path(path).parent.absolute())

    @logwrapper
    def get_closest_in_crc(self,prev_list,item,new_list):
        if item in new_list:
            return item

        if not new_list:
            return None

        if item in prev_list:
            sel_index=prev_list.index(item)

            new_list_len=len(new_list)
            for i in range(new_list_len):
                if (index_m_i:=sel_index-i) >=0:
                    nearest = prev_list[index_m_i]
                    if nearest in new_list:
                        return nearest
                elif (index_p_i:=sel_index+i) < new_list_len:
                    nearest = prev_list[index_p_i]
                    if nearest in new_list:
                        return nearest
                else:
                    return None

        return None

    @logwrapper
    def csv_save(self):
        if csv_file := asksaveasfilename(initialfile = 'librer_scan.csv',defaultextension=".csv",filetypes=[("All Files","*.*"),("CSV Files","*.csv")]):

            self.status('saving CSV file "%s" ...' % str(csv_file))
            librer_core.write_csv(str(csv_file))
            self.status('CSV file saved: "%s"' % str(csv_file))

    @logwrapper
    def db_clean(self):
        try:
            rmtree(DB_DIR)
        except Exception as e:
            l_error(e)

    @logwrapper
    def clip_copy_full_path_with_file(self):
        if self.sel_path_full and self.sel_file:
            self.clip_copy(path_join(self.sel_path_full,self.sel_file))
        elif self.sel_crc:
            self.clip_copy(self.sel_crc)

    @logwrapper
    def clip_copy_full(self):
        if self.sel_path_full:
            self.clip_copy(self.sel_path_full)
        elif self.sel_crc:
            self.clip_copy(self.sel_crc)

    @logwrapper
    def clip_copy_file(self):
        if self.sel_file:
            self.clip_copy(self.sel_file)
        elif self.sel_crc:
            self.clip_copy(self.sel_crc)

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
                    self.main.after_idle(lambda : self.tree_action(tree,item))

        return "break"

    @logwrapper
    def tree_action(self,tree,item,alt_pressed=False):
        if alt_pressed:
            self.open_folder()
        elif tree.set(item,'kind') in (self.DIR,self.DIRLINK):
            #self.enter_dir(self.sel_path_full+self.files_tree.set(item,'file') if self.sel_path_full=='/' else sep.join([self.sel_path_full,self.files_tree.set(item,'file')]),'..' )
            pass
        elif tree.set(item,'kind')!=self.CRC:
            self.open_file()

    @logwrapper
    def open_folder(self):
        tree=self.sel_tree

        params=[]
        if tree.set(self.sel_item,'kind')==self.CRC:
            self.status('Opening folders(s)')
            for item in tree.get_children(self.sel_item):
                item_path=tree.set(item,'path')
                params.append(item_path)
        elif self.sel_path_full:
            self.status(f'Opening: {self.sel_path_full}')
            params.append(self.sel_path_full)
        else:
            return

        if wrapper:=self.cfg.get(CFG_KEY_WRAPPER_FOLDERS):
            params_num = self.cfg.get(CFG_KEY_WRAPPER_FOLDERS_PARAMS)

            num = 1024 if params_num=='all' else int(params_num)
            run_command = lambda : Popen([wrapper,*params[:num]])
        elif windows:
            run_command = lambda : startfile(params[0])
        else:
            run_command = lambda : Popen(["xdg-open",params[0]])

        Thread(target=run_command,daemon=True).start()

    @logwrapper
    def open_file(self):
        if self.sel_path_full and self.sel_file:
            file_to_open = sep.join([self.sel_path_full,self.sel_file])

            if wrapper:=self.cfg.get(CFG_KEY_WRAPPER_FILE) and self.sel_kind in (self.FILE,self.LINK,self.SINGLE,self.SINGLEHARDLINKED):
                self.status('opening: %s' % file_to_open)
                run_command = lambda : Popen([wrapper,file_to_open])
            elif windows:
                self.status('opening: %s' % file_to_open)
                run_command = lambda : startfile(file_to_open)
            else:
                self.status('executing: xdg-open "%s"' % file_to_open)
                run_command = lambda : Popen(["xdg-open",file_to_open])

            Thread(target=run_command,daemon=True).start()

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
        DB_DIR = sep.join([LIBRER_EXECUTABLE_DIR,'db'])


        #######################################################################

        VER_TIMESTAMP = console.get_ver_timestamp()

        p_args = console.parse_args(VER_TIMESTAMP)

        use_appdir=bool(p_args.appdirs)

        if not use_appdir:
            try:
                DB_DIR_TEST = sep.join([DB_DIR,'access.test'])
                Path(DB_DIR_TEST).mkdir(parents=True,exist_ok=False)
                rmdir(DB_DIR_TEST)
            except Exception as e_portable:
                print('Cannot store files in portable mode:',e_portable)
                use_appdir=True

        if use_appdir:
            try:
                from appdirs import user_cache_dir,user_log_dir,user_config_dir
                #CACHE_DIR_DIR = user_cache_dir('librer','PJDude-%s' % VER_TIMESTAMP)
                LOG_DIR = user_log_dir('librer','PJDude')
                CONFIG_DIR = user_config_dir('librer')
            except Exception as e_import:
                print(e_import)

        else:
            #CACHE_DIR_DIR = sep.join([DB_DIR,"cache-%s" % VER_TIMESTAMP])
            LOG_DIR = sep.join([DB_DIR,"logs"])
            CONFIG_DIR = DB_DIR

        #dont mix device id for different hosts in portable mode
        #CACHE_DIR = sep.join([CACHE_DIR_DIR,node()])

        log=abspath(p_args.log[0]) if p_args.log else LOG_DIR + sep + strftime('%Y_%m_%d_%H_%M_%S',localtime(time()) ) +'.txt'
        #LOG_LEVEL = logging.DEBUG if p_args.debug else logging.INFO

        Path(LOG_DIR).mkdir(parents=True,exist_ok=True)

        #print('LIBRER_EXECUTABLE_FILE:',LIBRER_EXECUTABLE_FILE,'\nLIBRER_EXECUTABLE_DIR:',LIBRER_EXECUTABLE_DIR,'\nDB_DIR:',DB_DIR)
        print('log:',log)

        logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s', filename=log,filemode='w')

        l_info('LIBRER %s',VER_TIMESTAMP)
        l_info('executable: %s',LIBRER_EXECUTABLE_FILE)
        #l_debug('DEBUG LEVEL ENABLED')

        try:
            distro_info=Path(path_join(LIBRER_DIR,'distro.info.txt')).read_text(encoding='ASCII')
        except Exception as exception_1:
            l_error(exception_1)
        else:
            l_info('distro info:\n%s',distro_info)

        librer_core = core.LibrerCore(DB_DIR,logging)

        if p_args.csv:
            signal(SIGINT, lambda a, k : librer_core.handle_sigint())

            librer_core.set_paths_to_scan(p_args.paths)

            if p_args.exclude:
                set_exclude_masks_res=librer_core.set_exclude_masks(False,p_args.exclude)
            elif p_args.exclude_regexp:
                set_exclude_masks_res=librer_core.set_exclude_masks(True,p_args.exclude_regexp)
            else:
                set_exclude_masks_res=librer_core.set_exclude_masks(False,[])

            if set_exclude_masks_res:
                print(set_exclude_masks_res)
                sys.exit(2)

            run_scan_thread=Thread(target=librer_core.scan,daemon=True)
            run_scan_thread.start()

            while run_scan_thread.is_alive():
                print('Scanning ...', librer_core.info_counter,end='\r')
                sleep(0.04)

            run_scan_thread.join()

            run_crc_thread=Thread(target=librer_core.crc_calc,daemon=True)
            run_crc_thread.start()

            while run_crc_thread.is_alive():
                print(f'crc_calc...{librer_core.info_files_done}/{librer_core.info_total}                 ',end='\r')
                sleep(0.04)

            run_crc_thread.join()
            print('')
            librer_core.write_csv(p_args.csv[0])
            print('Done')

        else:
            Gui(getcwd(),p_args.paths,p_args.exclude,p_args.exclude_regexp,p_args.norun)

    except Exception as e_main:
        print(e_main)
        l_error(e_main)
        sys.exit(1)
