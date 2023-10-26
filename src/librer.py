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
#from subprocess import Popen

from tkinter import Tk
from tkinter import Toplevel
from tkinter import PhotoImage
from tkinter import Menu
#from tkinter import PanedWindow
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
from tkinter.filedialog import askopenfilename

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

core_bytes_to_str=core.bytes_to_str

###########################################################################################################################################

CFG_KEY_USE_REG_EXPR='use_reg_expr'
CFG_KEY_EXCLUDE_REGEXP='excluderegexpp'
CFG_KEY_EXCLUDE='exclude'
CFG_KEY_WRAPPER_FILE = 'file_open_wrapper'
CFG_KEY_WRAPPER_FILE_USE = 'file_open_wrapper_use'

cfg_defaults={
    CFG_KEY_USE_REG_EXPR:False,
    CFG_KEY_EXCLUDE_REGEXP:False,
    CFG_KEY_EXCLUDE:'',
    CFG_KEY_WRAPPER_FILE:'',
    CFG_KEY_WRAPPER_FILE_USE:False
}

HOMEPAGE='https://github.com/PJDude/librer'

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
    #sel_record=''

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

        signal(SIGINT, lambda a, k : self.handle_sigint())

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

        self.ico_record = self_ico['record']
        self.ico_folder = self_ico['folder']
        self.ico_folder_link = self_ico['folder_link']
        self.ico_folder_error = self_ico['folder_error']
        self.ico_empty = self_ico['empty']

        self_main.iconphoto(False, self_ico['librer'])

        self.RECORD='R'
        self.DIR='D'
        self.DIRLINK='L'
        self.LINK='l'
        self.FILE='F'
        self.FILELINK='l'

        self.SYMLINK='S'

        self_main_bind = self_main.bind

        #self_main_bind('<KeyPress-F2>', lambda event : self.settings_dialog.show())
        self_main_bind('<KeyPress-F1>', lambda event : self.aboout_dialog.show())
        self_main_bind('<KeyPress-s>', lambda event : self.scan_dialog_show())
        self_main_bind('<KeyPress-S>', lambda event : self.scan_dialog_show())

        self_main_bind('<KeyPress-Delete>', lambda event : self.delete_data_record())

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

        #style_map('semi_focus.Treeview', background=[('focus',bg_focus),('selected',bg_focus_off),('','white')])

        #style_map('no_focus.Treeview', background=[('focus',bg_focus),('selected',bg_sel),('','white')])
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

        #self.paned = PanedWindow(self_main,orient='vertical',relief='sunken',showhandle=0,bd=0,bg=self.bg_color,sashwidth=2,sashrelief='flat')
        #self.paned.pack(fill='both',expand=1)

        #frame_groups = self_main

        #frame_groups = Frame(self.paned,bg=self.bg_color)
        #self.paned.add(frame_groups)
        #frame_folder = Frame(self.paned,bg=self.bg_color)

        #frame_groups.grid_columnconfigure(0, weight=1)
        #frame_groups.grid_rowconfigure(0, weight=1,minsize=200)

        (status_frame := Frame(self_main,bg=self.bg_color)).pack(side='bottom', fill='both')

        #Label(status_frame,width=6,text='Info:',relief='groove',borderwidth=2,bg=self.bg_color,anchor='e').pack(fill='x',expand=0,side='left')

        self.status_info = Label(status_frame,text='Initializing...',relief='sunken',borderwidth=1,bg=self.bg_color,anchor='w')
        self.status_info.pack(fill='x',expand=1,side='left')
        self.status_info_configure = self.status_info.configure

        Label(status_frame,width=10,text='Record: ',relief='groove',borderwidth=2,bg=self.bg_color,anchor='e').pack(fill='x',expand=0,side='left')
        #self.status_record=Label(status_frame,text='--',image=self_ico['empty'],width=80,compound='right',borderwidth=2,bg=self.bg_color,relief='groove',anchor='e')
        self.status_record=Label(status_frame,text='--',width=30,borderwidth=2,bg=self.bg_color,relief='groove',anchor='w')
        self.status_record.pack(fill='x',expand=0,side='left')
        self.status_record_configure = self.status_record.configure

        Label(status_frame,width=10,text='Scan Path: ',relief='groove',borderwidth=2,bg=self.bg_color,anchor='e').pack(fill='x',expand=0,side='left')
        self.status_scan_path = Label(status_frame,text='',relief='flat',borderwidth=1,bg=self.bg_color,anchor='w')

        #self.status_record=Label(status_frame,text='--',image=self_ico['empty'],width=80,compound='right',borderwidth=2,bg=self.bg_color,relief='groove',anchor='e')
        self.status_scan_path=Label(status_frame,text='--',width=30,borderwidth=2,bg=self.bg_color,relief='groove',anchor='w')
        self.status_scan_path.pack(fill='x',expand=0,side='left')
        self.status_scan_path_configure = self.status_scan_path.configure

        self.status_record.bind("<Motion>", lambda event : self.motion_on_widget(event,'Selected record name'))
        self.status_record.bind("<Leave>", lambda event : self.widget_leave())

        self.tree=Treeview(self_main,takefocus=True,show=('tree','headings') )
        self_tree = self.tree

        self_tree.bind('<KeyPress>', self.key_press )
        self_tree.bind('<<TreeviewOpen>>', self.open_item )
        self_tree.bind('<ButtonPress-3>', self.context_menu_show)

        self_tree.bind("<<TreeviewSelect>>", self.tree_select)
        self.selected_record_item=''
        self.selected_record_name=''

        #selectmode='none',

        self.tree_set = self_tree.set
        self.tree_see = self_tree.see
        self.tree_get_children = self.tree.get_children
        self.tree_focus = lambda item : self.tree.focus(item)

        self.org_label={}
        self_org_label = self.org_label

        self_org_label['#0']='Label'
        self_org_label['size_h']='Size'
        self_org_label['ctime_h']='Time'

        self_tree["columns"]=('data','record','opened','path','size','size_h','ctime','ctime_h','kind')
        self_tree["displaycolumns"]=('size_h','ctime_h')
        self.real_display_columns=('#0','size_h','ctime_h')

        self_tree_column = self_tree.column

        self_tree_column('#0', width=120, minwidth=100, stretch='yes')
        self_tree_column('size_h', width=80, minwidth=80, stretch='no',anchor='e')
        self_tree_column('ctime_h', width=150, minwidth=100, stretch='no',anchor='e')

        self_tree_heading = self_tree.heading

        self_tree_heading('#0',text='Label',anchor='w')
        self_tree_heading('size_h',anchor='w')
        self_tree_heading('ctime_h',anchor='n')
        #self_tree_heading('size_h', text='Size \u25BC',anchor='n')

        self_tree.bind('<ButtonPress-1>', self.tree_on_mouse_button_press)

        vsb1 = Scrollbar(self_main, orient='vertical', command=self_tree.yview,takefocus=False)

        self_tree.configure(yscrollcommand=vsb1.set)

        vsb1.pack(side='right',fill='y',expand=0)
        self_tree.pack(fill='both',expand=1, side='left')

        self_tree.bind('<Double-Button-1>', self.double_left_button)

        tree = self_tree
        tree_heading = tree.heading
        #tree["displaycolumns"]
        for col in self.real_display_columns:
            if col in self_org_label:
                tree_heading(col,text=self_org_label[col])

        self_tree_tag_configure = self_tree.tag_configure

        self_tree_tag_configure(self.RECORD, foreground='green')
        self_tree_tag_configure(self.SYMLINK, foreground='gray')

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

        #self.paned.update()
        #self.paned.sash_place(0,0,self.cfg.get('sash_coord',400,section='geometry'))

        #prevent displacement
        if cfg_geometry :
            self_main.geometry(cfg_geometry)

        self.popup = Menu(self_tree, tearoff=0,bg=self.bg_color)
        self.popup_unpost = self.popup.unpost
        self.popup.bind("<FocusOut>",lambda event : self.popup_unpost() )

        self_main_bind("<FocusOut>",lambda event : self.menubar_unpost() )

        #######################################################################
        #scan dialog

        def pre_show(on_main_window_dialog=True):
            self.menubar_unpost()
            self.hide_tooltip()
            self.popup_unpost()

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

        temp_frame = LabelFrame(self.scan_dialog.area_main,text='Create new database record',borderwidth=2,bg=self.bg_color,takefocus=False)
        temp_frame.grid(row=0,column=0,sticky='we',padx=4,pady=4,columnspan=4)


        lab1=Label(temp_frame,text="Path To scan:",bg=self.bg_color,anchor='w')
        lab1.grid(row=0, column=0, sticky='news',padx=4,pady=4)

        lab2=Label(temp_frame,text="User label:",bg=self.bg_color,anchor='w')
        lab2.grid(row=1, column=0, sticky='news',padx=4,pady=4)

        self.path_to_scan_entry_var=StringVar(value='')
        path_to_scan_entry = Entry(temp_frame,textvariable=self.path_to_scan_entry_var)
        path_to_scan_entry.grid(row=0, column=1, sticky='news',padx=4,pady=4)
        #.pack(side='left',expand=1,fill='x',pady=4,padx=5)

        self.add_path_button = Button(temp_frame,width=18,image = self_ico['open'], command=self.path_to_scan_add_dialog,underline=0)
        self.add_path_button.grid(row=0, column=2, sticky='news',padx=4,pady=4)
        #.pack(side='left',pady=4,padx=4)

        self.add_path_button.bind("<Motion>", lambda event : self.motion_on_widget(event,"Add path to scan.\nA maximum of 8 paths are allowed."))
        self.add_path_button.bind("<Leave>", lambda event : self.widget_leave())

        #sf_par=dialogs.SFrame(temp_frame,bg=self.bg_color)
        #sf_par.pack(fill='both',expand=True,side='top')
        #self.paths_frame=sf_par.frame()

        #buttons_fr = Frame(temp_frame,bg=self.bg_color,takefocus=False)
        #buttons_fr.pack(fill='both',expand=False,side='bottom')

        temp_frame.grid_columnconfigure(1, weight=1)
        #temp_frame.grid_rowconfigure(99, weight=1)

        #temp_frame2 = LabelFrame(self.scan_dialog.area_main,text='Label:',borderwidth=2,bg=self.bg_color,takefocus=False)
        #temp_frame2.grid(row=1,column=0,sticky='we',padx=4,pady=4,columnspan=4)

        self.scan_label_entry_var=StringVar(value='')
        scan_label_entry = Entry(temp_frame,textvariable=self.scan_label_entry_var)
        scan_label_entry.grid(row=1, column=1, sticky='news',padx=4,pady=4,columnspan=2)
        #.pack(side='left',expand=1,fill='x',pady=4,padx=5)

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

        ############
        temp_frame_cw = LabelFrame(self.scan_dialog.area_main,text='Custom Data Extractor:',borderwidth=2,bg=self.bg_color,takefocus=False)
        temp_frame_cw.grid(row=3,column=0,sticky='news',padx=4,pady=4,columnspan=3)

        self.file_open_wrapper_use = BooleanVar(value=self.cfg.get_bool(CFG_KEY_WRAPPER_FILE_USE))
        use_ow_button = Checkbutton(temp_frame_cw,text='Use CDEW',variable=self.file_open_wrapper_use)
        use_ow_button.grid(row=0,column=0,sticky='news',padx=8,pady=3,columnspan=3)

        self.file_open_wrapper = StringVar(value=self.cfg.get(CFG_KEY_WRAPPER_FILE))
        Label(temp_frame_cw,text='File: ',bg=self.bg_color,anchor='w').grid(row=1, column=0,sticky='news')
        (en_1:=Entry(temp_frame_cw,textvariable=self.file_open_wrapper)).grid(row=1, column=1,sticky='ew',padx=3,pady=3)
        en_1.bind("<Motion>", lambda event : self.motion_on_widget(event,'Command executed on "Open File" with full file path as parameter.\nIf empty, default os association will be executed.'))
        en_1.bind("<Leave>", lambda event : self.widget_leave())

        self.add_path_button = Button(temp_frame_cw,width=18,image = self_ico['open'], command=self.custom_data_wrappper_dialog,underline=0)
        self.add_path_button.grid(row=1, column=2, sticky='news',padx=4,pady=4)

        temp_frame_cw.grid_columnconfigure(1, weight=1)

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

        self.mark_dialog_on_groups = dialogs.CheckboxEntryDialogQuestion(self_tree,self_ico['librer'],self.bg_color,pre_show=pre_show,post_close=post_close)

        self.info_dialog_on_mark={}

        self.info_dialog_on_mark[self_tree] = dialogs.LabelDialog(self.mark_dialog_on_groups.widget,self_ico['librer'],self.bg_color,pre_show=lambda : pre_show(False),post_close=lambda : post_close(False))

        self.find_dialog = dialogs.FindEntryDialog(self_tree,self_ico['librer'],self.bg_color,self.find_mod,self.find_prev_from_dialog,self.find_next_from_dialog,pre_show=pre_show,post_close=post_close)

        self.info_dialog_on_find={}

        self.info_dialog_on_find[self_tree] = dialogs.LabelDialog(self.find_dialog.widget,self_ico['librer'],self.bg_color,pre_show=lambda : pre_show(False),post_close=lambda : post_close(False))

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
        lab2_text=  \
                    'SETTINGS DIRECTORY :  ' + CONFIG_DIR + '\n' + \
                    'DATABASE DIRECTORY :  ' + DB_DIR + '\n' + \
                    'LOGS DIRECTORY     :  ' + LOG_DIR + '\n\n' + \
                    'Current log file   :  ' + log

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
                #self_file_cascade_add_command(label = 'Delete data record ...',command = self.delete_data_record,accelerator="Delete",image = self_ico['delete'],compound='left')
                #self_file_cascade_add_separator()
                #self_file_cascade_add_command(label = 'Settings ...',command=self.settings_dialog.show, accelerator="F2",image = self_ico['settings'],compound='left')
                #self_file_cascade_add_separator()
                self_file_cascade_add_command(label = 'Save CSV',command = self.csv_save,state=item_actions_state,image = self_ico['empty'],compound='left')
                self_file_cascade_add_separator()
                self_file_cascade_add_command(label = 'Exit',command = self.exit,image = self_ico['exit'],compound='left')

        self.file_cascade= Menu(self.menubar,tearoff=0,bg=self.bg_color,postcommand=file_cascade_post)
        self.menubar.add_cascade(label = 'File',menu = self.file_cascade,accelerator="Alt+F")

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

        self_REAL_SORT_COLUMN = self.REAL_SORT_COLUMN = self.REAL_SORT_COLUMN={}

        self_REAL_SORT_COLUMN['#0'] = 'data'
        self_REAL_SORT_COLUMN['size_h'] = 'size'
        self_REAL_SORT_COLUMN['ctime_h'] = 'ctime'

        self_REAL_SORT_COLUMN_INDEX = self.REAL_SORT_COLUMN_INDEX = self.REAL_SORT_COLUMN_INDEX={}

        #self_tree["displaycolumns"]
        for disply_column in self.real_display_columns:
            self_REAL_SORT_COLUMN_INDEX[disply_column] = self_tree["columns"].index(self_REAL_SORT_COLUMN[disply_column])

        self_REAL_SORT_COLUMN_IS_NUMERIC = self.REAL_SORT_COLUMN_IS_NUMERIC = self.REAL_SORT_COLUMN_IS_NUMERIC={}

        self_REAL_SORT_COLUMN_IS_NUMERIC['#0'] = False
        self_REAL_SORT_COLUMN_IS_NUMERIC['size_h'] = True
        self_REAL_SORT_COLUMN_IS_NUMERIC['ctime_h'] = True

        self.column_sort_last_params={}
        #colname,sort_index,is_numeric,reverse,dir_code,non_dir_code
        self.column_sort_last_params[self_tree]=self.column_groups_sort_params_default=('size_h',self_REAL_SORT_COLUMN_INDEX['size_h'],self_REAL_SORT_COLUMN_IS_NUMERIC['size_h'],1,1,0)

        #######################################################################

        self_tree.bind("<Motion>", self.motion_on_tree)

        self_tree.bind("<Leave>", lambda event : self.widget_leave())

        #######################################################################

        if paths_to_add:
            if len(paths_to_add)>self.MAX_PATHS:
                l_warning('only %s search paths allowed. Following are ignored:\n%s',self.MAX_PATHS, '\n'.join(paths_to_add[8:]))
            for path in paths_to_add[:self.MAX_PATHS]:
                if windows and path[-1]==':':
                    path += '\\'
                self.path_to_scan_set(abspath(path))

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
        self.records_show()

        librer_core.read_list(self.single_record_show)

        self.actions_processing=True

        self.tree_semi_focus(self_tree)

        #self_tree.configure(style='semi_focus.Treeview')
        self_tree.focus_set()
        #self_tree.update()
        #self.main_update()

        if children := self_tree.get_children():
            self_tree.focus(children[0])

        self_main.mainloop()
        #######################################################################

    def unpost(self):
        self.hide_tooltip()
        self.menubar_unpost()
        self.popup_unpost()

    tooltip_show_after_tree=''
    tooltip_show_after_widget=''

    def widget_leave(self):
        self.menubar_unpost()
        self.hide_tooltip()

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
        current_record_name=None

        tree = self.tree

        while not current_record_name:
            temp_record_name = tree.set(item,'record')
            if temp_record_name:
                current_record_name=temp_record_name
                break
            else:
                path = tree.set(item,'path')
                item=tree.parent(item)

        return (item,current_record_name)

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
                    record_item,record_name = self.get_item_record(item)
                    record = self.item_to_record[record_item]

                    #values = tree.item(item,'values')
                    #print('values',values)

                    try:
                        inode,dev = self.node_to_inodedev[item]
                        #print(inode,dev)
                        node_cd_org = record.custom_data[(inode,dev)] if inode and dev else None
                        node_cd_list = []
                        if node_cd_org:
                            line_nr=0
                            for line in node_cd_org.split('\n'):

                                node_cd_list.append((line[0:127] + '...') if len(line)>127 else line)
                                line_nr+=1
                                if line_nr>10:
                                    break
                            node_cd = '\n'.join(node_cd_list)

                    except :
                        node_cd = None
                    #print(inode,dev)
                    #print('node_cd',node_cd)

                    record_path = record.db.scan_path
                    size = core_bytes_to_str(record.db.sum_size)
                    self.tooltip_lab_configure(text=f'record:{record_name}\npath:{record_path}\nsize:{size}' + (f'\n\n{node_cd}' if node_cd else ''))

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
        disable("Help")
        #self.menubar.update()

    def reset_sels(self):
        self.sel_path = None
        self.sel_item = None

        self.sel_kind = None

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

    find_initialvalue='*'

    def finder_wrapper_show(self):
        #print('finder_wrapper_show')
        tree=self.tree

        self.find_dialog_shown=True

        scope_info = ''

        self.find_dialog.show('Find',scope_info,initial=self.find_initialvalue,checkbutton_text='treat as a regular expression',checkbutton_initial=False)
        self.find_initialvalue=self.find_dialog.entry.get()

        self.find_dialog_shown=False
        self.tree_semi_focus(tree)

    def find_prev_from_dialog(self,expression,use_reg_expr):
        self.find_items(expression,use_reg_expr)
        self.select_find_result(-1)

    def find_prev(self):
        if not self.find_result:
            self.find_params_changed=True
            self.finder_wrapper_show()
        else:
            self.select_find_result(-1)

    def find_next_from_dialog(self,expression,use_reg_expr):
        self.find_items(expression,use_reg_expr)
        self.select_find_result(1)

    def find_next(self):
        if not self.find_result:
            self.find_params_changed=True
            self.finder_wrapper_show()
        else:
            self.select_find_result(1)

    find_result_index=0

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
        self.status('searching ...')

        if self.find_params_changed:
            if expression:
                func_to_call = ( lambda x : search(expression,x) ) if use_reg_expr else ( lambda x : fnmatch(x,expression) )

                results = librer_core.find_items_in_all_records(func_to_call)

                results_len = len(results)

                self.status_info_configure(text = f'Search results:{results_len}')

                if results:
                    self.find_result=results
                    self.find_params_changed=False
                else:
                    self.find_result=()
                    scope_info = ''
                    self.info_dialog_on_find[self.tree].show(scope_info,'No files found.')

    def get_child_of_name(self,item,child_name):
        self_tree = self.tree
        for child in self_tree.get_children(item):
            values = self_tree.item(child,'values')
            data=values[0]
            if data==child_name:
                return child
        return None

    def select_find_result(self,mod):
        self_tree = self.tree
        if self.find_result:
            items_len=len(self.find_result)
            self.find_result_index+=mod
            next_item=self.find_result[self.find_result_index%items_len]

            if next_item:
                record,record_result = next_item

                record_item = self.record_to_item[record]

                record = self.item_to_record[record_item]

                current_item = record_item

                self.open_item(None,current_item)

                for item_name in record_result:
                    child_item = self.get_child_of_name(current_item,item_name)
                    if child_item:
                        current_item = child_item
                        self.open_item(None,current_item)
                    else:
                        self.info_dialog_on_main.show('cannot find item:',item_name)
                        break

                self_tree.selection_set(current_item)

                if not self.find_dialog_shown:
                    self_tree.focus(current_item)

                self.tree_semi_focus(self.tree)
                self.tree.see(current_item)
                self.tree.update()

                self.tree_sel_change(current_item)

                if mod>0:
                    self.status('Find next %s' % self.find_expression_prev)
                else:
                    self.status('Find Previous %s' % self.find_expression_prev)

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
        self_sel_item = self.sel_item

        item=tree.focus()
        record_item,record_name = self.get_item_record(item)

        item_to_sel = tree.next(record_item) if direction==1 else tree.prev(record_item)

        #if children := self.tree_get_children():
            #if next_item:=children[index]:
            #    self.select_and_focus(next_item)
        #    pass
        if item_to_sel:
            self.select_and_focus(item_to_sel)

        return

    @catched
    def goto_first_last_record(self,index):
        #print('goto_first_last_record',index)
        if children := self.tree_get_children():
            if next_item:=children[index]:
                self.select_and_focus(next_item)

    current_record=None
    def tree_select(self,event):
        #print('tree_select',event)

        item=self.tree.focus()
        parent = self.tree.parent(item)

        if item and not parent:
            record_name = self.tree.item(item,'text')
            self.status_record_configure(text=record_name)
            self.current_record = record = self.item_to_record[item]
            self.status_scan_path_configure(text=record.db.scan_path)

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

                #print(key)

                if key in ("Prior","Next"):
                    self.goto_next_prev_record(self.KEY_DIRECTION[key])
                elif key in ("Home","End"):
                    self.goto_first_last_record(self.KEY_DIRECTION[key])
                elif key=='Return':
                    item=tree.focus()
                    if item:
                        self.tree_action(item)

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

                    elif key=='BackSpace':
                        pass
                    elif key in ('c','C'):
                        if ctrl_pressed:
                            if shift_pressed:
                                self.clip_copy_file()
                            else:
                                self.clip_copy_full_path_with_file()
                        else:
                            self.clip_copy_full()
                    elif key in ('f','F'):
                        self.finder_wrapper_show()


                    #else:
                    #    print(key)
                    #    print(event_str)

            except Exception as e:
                l_error(e)
                self.info_dialog_on_main.show('INTERNAL ERROR',str(e))

            if tree_focus:=tree.focus():
                tree.selection_set(tree_focus)

#################################################
    def select_and_focus(self,item):
        #print('select_and_focus',item)
        #if try_to_show_all:
        #    self.tree_see(self.tree_get_children(item)[-1])
        #    self.tree.update()

        self.tree_see(item)
        self.tree_focus(item)
        #self.tree.selection_set(item)

        #self.tree_semi_focus(self.tree)
        self.tree.update()

        self.tree_sel_change(item)

    def tree_on_mouse_button_press(self,event):
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
                self.tree_semi_focus(tree)

                self.tree_sel_change(item)

                #prevents processing of expanding nodes
                #return "break"

        return None

    def tree_semi_focus(self,tree):
        #print('tree_semi_focus')
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

    def sel_path_set(self,path):
        if self.sel_path_full != path:
            self.sel_path_full = path
            self.status_scan_path_configure(text=self.sel_path_full)

    @catched
    def tree_sel_change(self,item,force=False,change_status_line=True):
        self.sel_item = item

        if change_status_line :
            self.status()

        self_tree_set_item=lambda x : self.tree_set(item,x)

        #self.sel_file = self_tree_set_item('file')

        #new_crc = self_tree_set_item('crc')
        #if self.sel_crc != new_crc:
        #    self.sel_crc = new_crc

        path=self_tree_set_item('path')
        #record=self_tree_set_item('file')
        #print('sel record:',record)

        #self.sel_record = record
        return

        if record!=self.sel_record or force:
            if self.find_tree_index==1:
                self.find_result=()

            self.sel_path = None
            self.sel_path_set(None)

            #self.set_full_path_to_file()

        self.sel_kind = self_tree_set_item('kind')

    def menubar_unpost(self):
        try:
            self.menubar.unpost()
        except Exception as e:
            l_error(e)

    def context_menu_show(self,event):
        tree=self.tree

        if tree.identify("region", event.x, event.y) == 'heading':
            print('heading')
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

        c_nav = Menu(self.menubar,tearoff=0,bg=self.bg_color)
        c_nav_add_command = c_nav.add_command
        c_nav_add_separator = c_nav.add_separator

        c_nav_add_command(label = 'Go to next record'       ,command = lambda : self.goto_next_prev_record(1),accelerator="Pg Down",state='normal', image = self.ico['empty'],compound='left')
        c_nav_add_command(label = 'Go to previous record'   ,command = lambda : self.goto_next_prev_record(-1), accelerator="Pg Up",state='normal', image = self.ico['empty'],compound='left')
        c_nav_add_separator()
        c_nav_add_command(label = 'Go to first crc group'       ,command = lambda : self.goto_first_last_record(0),accelerator="Home",state='normal', image = self.ico['empty'],compound='left')
        c_nav_add_command(label = 'Go to last crc group'   ,command = lambda : self.goto_first_last_record(-1), accelerator="End",state='normal', image = self.ico['empty'],compound='left')

        pop_add_command(label = 'Scan ...',  command = self.scan_dialog_show,accelerator='S',image = self.ico['scan'],compound='left')
        #pop_add_command(label = 'Settings ...',  command = self.settings_dialog.show,accelerator='F2',image = self.ico['settings'],compound='left')
        pop_add_separator()
        pop_add_command(label = 'Delete data record ...',command = self.delete_data_record,accelerator="Delete",image = self.ico['delete'],compound='left')
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
        prev_colname,prev_sort_index,prev_is_numeric,prev_reverse,prev_dir_code,prev_non_dir_code=self.column_sort_last_params[tree]
        reverse = not prev_reverse if colname == prev_colname else prev_reverse
        tree.heading(prev_colname, text=self.org_label[prev_colname])

        dir_code,non_dir_code = (1,0) if reverse else (0,1)

        sort_index=self.REAL_SORT_COLUMN_INDEX[colname]
        is_numeric=self.REAL_SORT_COLUMN_IS_NUMERIC[colname]
        self.column_sort_last_params[tree]=(colname,sort_index,is_numeric,reverse,dir_code,non_dir_code)

        self.column_sort(tree)

    @logwrapper
    def tree_sort_item(self,parent_item):
        tree = self.tree

        colname,sort_index,is_numeric,reverse,dir_code,non_dir_code = self.column_sort_last_params[tree]

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
        colname,sort_index,is_numeric,reverse,dir_code,non_dir_code = self.column_sort_last_params[tree]

        self.column_sort_set_arrow(tree)
        self.tree_sort_item(None)

        tree.update()

    def column_sort_set_arrow(self, tree):
        colname,sort_index,is_numeric,reverse,dir_code,non_dir_code = self.column_sort_last_params[tree]
        tree.heading(colname, text=self.org_label[colname] + ' ' + str('\u25BC' if reverse else '\u25B2') )

    def path_to_scan_set(self,path):
        print('path_to_scan_set',path)

    scanning_in_progress=False
    def scan_wrapper(self):
        if self.scanning_in_progress:
            l_warning('scan_wrapper collision')
            return


        if self.scan_label_entry_var.get()=='':
            self.info_dialog_on_scan.show('Error. Empty record label.','Set record label.')
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
        self.tree_semi_focus(self.tree)

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
        #self.records_show()

        path_to_scan_from_entry = self.path_to_scan_entry_var.get()
        #print('path_to_scan_from_entry:',path_to_scan_from_entry)

        exclude_from_entry = [var.get() for var in self.exclude_entry_var.values()]

        #if res:=librer_core.set_exclude_masks(self.cfg_get_bool(CFG_KEY_EXCLUDE_REGEXP),exclude_from_entry):
        #    self.info_dialog_on_scan.show('Error. Fix expression.',res)
        #    return False
        #self.cfg.set(CFG_KEY_EXCLUDE,'|'.join(exclude_from_entry))


        if not path_to_scan_from_entry:
            self.info_dialog_on_scan.show('Error. No paths to scan.','Add paths to scan.')
            return False

        new_record = librer_core.create(self.scan_label_entry_var.get(),path_to_scan_from_entry)

        #new_record.db.scan_path = path_to_scan_from_entry
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

        scan_thread=Thread(target=lambda : new_record.scan(librer_core.db_dir),daemon=True)
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

        self_tooltip_message = self.tooltip_message
        self_configure_tooltip = self.configure_tooltip

        scan_thread_is_alive = scan_thread.is_alive

        self_hg_ico = self.hg_ico
        len_self_hg_ico = len(self_hg_ico)

        local_core_bytes_to_str = core_bytes_to_str

        self.cfg.set_bool(CFG_KEY_WRAPPER_FILE_USE,self.file_open_wrapper_use.get())
        self.cfg.set(CFG_KEY_WRAPPER_FILE,self.file_open_wrapper.get())

        while scan_thread_is_alive():
            new_data[3]=local_core_bytes_to_str(new_record.db.sum_size)
            new_data[4]='%s files' % new_record.db.quant_files

            anything_changed=False
            for i in (3,4):
                if new_data[i] != prev_data[i]:
                    prev_data[i]=new_data[i]
                    self_progress_dialog_on_scan_lab[i].configure(text=new_data[i])
                    anything_changed=True

            now=time()

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

                    self_tooltip_message[str_self_progress_dialog_on_scan_abort_button]='currently scanning:\n%s...' % new_record.info_line
                    self_configure_tooltip(str_self_progress_dialog_on_scan_abort_button)
                    update_once=True

            self_progress_dialog_on_scan_area_main_update()

            if self.action_abort:
                librer_core.abort()
                break

            self.main.after(100,lambda : wait_var.set(not wait_var.get()))
            self.main.wait_variable(wait_var)

        self_progress_dialog_on_scan_lab[3].configure(text='')
        self_progress_dialog_on_scan_lab[2].configure(text='')

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


        if self.cfg.get_bool(CFG_KEY_WRAPPER_FILE_USE) and self.cfg.get(CFG_KEY_WRAPPER_FILE)!='':
            self_progress_dialog_on_scan.widget.title('Custom Data Extraction')

            scan2_thread=Thread(target=lambda : new_record.extract_custom_data(self.cfg.get(CFG_KEY_WRAPPER_FILE),path_to_scan_from_entry),daemon=True)
            scan2_thread.start()

            scan2_thread_is_alive = scan2_thread.is_alive

            while scan2_thread_is_alive():

                self_progress_dialog_on_scan_lab[3].configure(text=f'{new_record.files_cde} / {new_record.db.quant_files}')

                if self.action_abort:
                    librer_core.abort()
                    break

                self.main.after(100,lambda : wait_var.set(not wait_var.get()))
                self.main.wait_variable(wait_var)

            scan2_thread.join()

        self.single_record_show(new_record)

        #self.records_show()
        self_progress_dialog_on_scan.hide(True)

        return True

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

    def delete_data_record(self):
        label = self.current_record.db.label
        path = self.current_record.db.scan_path
        creation_time = self.current_record.db.creation_time

        self.text_ask_dialog.show('Delete Selected Data Recoord ?','Data Record: ' + label + '\n\n' + path)

        if self.text_ask_dialog.res_bool:
            librer_core.delete_record_by_id()
            print('deletingggggg')

    def scan_dialog_show(self,do_scan=False):
        self.exclude_mask_update()

        self.scan_dialog.do_command_after_show=self.scan if do_scan else None

        self.scan_dialog.show()

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

    def custom_data_wrappper_dialog(self):
        initialdir = self.last_dir if self.last_dir else self.cwd
        if res:=askopenfilename(title='Select File',initialdir=initialdir,parent=self.scan_dialog.area_main,filetypes=(("Bat Files","*.bat"),("Executable Files","*.exe"),("All Files","*.*")) if windows else (("Bash Files","*.sh"),("All Files","*.*")) ):
            self.last_dir=dirname(res)
            self.file_open_wrapper.set(normpath(abspath(res)))

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

    node_to_inodedev={}
    def open_item(self,event=None,item=None):
        tree=self.tree

        if not item:
            item=tree.focus()

        children=tree.get_children(item)
        opened = tree.set(item,'opened')

        if opened=='0' and children:
            colname,sort_index,is_numeric,reverse,dir_code,non_dir_code = self.column_sort_last_params[tree]
            sort_index_local=sort_index

            sort_val_func = int if is_numeric else lambda x : x

            tree.delete(*children)

            self_FILE = self.FILE
            self_DIR = self.DIR
            self_SYMLINK = self.SYMLINK
            core_bytes_to_str = core.bytes_to_str

            new_items_values = {}

            for entry_name,data_tuple in self.item_to_record_dict[item].items():
                if len(data_tuple)==8:
                    (is_dir,is_file,is_symlink,size,mtime,inode,dev,sub_dictionary) = data_tuple
                else:
                    l_error(f'data format incompatible:{data_tuple}')
                    print(f'data format incompatible:{data_tuple}')
                    continue

                if is_dir:
                    image=self.ico_folder_error if size==-1 else self.ico_folder_link if is_symlink else self.ico_folder
                    kind = self_DIR
                else:
                    image=''
                    #self.ico_empty
                    kind = self_FILE

                if is_symlink:
                    tags=self_SYMLINK
                else:
                    tags=''

                #('data','record','opened','path','size','size_h','ctime','ctime_h','kind')
                values = (entry_name,'','0',entry_name,size,core_bytes_to_str(size),mtime,strftime('%Y/%m/%d %H:%M:%S',localtime(mtime//1000000000)),kind)

                sort_index = ( dir_code if is_dir else non_dir_code , sort_val_func(values[sort_index_local]) )
                new_items_values[ ( sort_index,values,entry_name,image,True if sub_dictionary else False,inode,dev) ] = (sub_dictionary,tags)

            for (sort_index,values,entry_name,image,sub_dictionary_bool,inode,dev),(sub_dictionary,tags) in sorted(new_items_values.items(),key = lambda x : x[0][0],reverse=reverse) :
                new_item=tree.insert(item,'end',iid=None,values=values,open=False,text=entry_name,image=image,tags=tags)
                self.node_to_inodedev[new_item] = (inode,dev)
                if sub_dictionary_bool:
                    self.item_to_record_dict[new_item] = sub_dictionary
                    tree.insert(new_item,'end') #dummy_sub_item

            tree.set(item,'opened','1')

        #tree.item(item, open=True)

    @block_actions_processing
    @gui_block
    @logwrapper
    def single_record_show(self,record):

        record_db = record.db
        size=record_db.sum_size
        #print('R size:',size)

        #('data','record','opened','path','size','size_h','ctime','ctime_h','kind')
        values = (record_db.label,record.file_name,0,record_db.scan_path,size,core.bytes_to_str(size),record_db.creation_time,strftime('%Y/%m/%d %H:%M:%S',localtime(record_db.get_time())),self.RECORD)
        record_item=self.tree.insert('','end',iid=None,values=values,open=False,text=record_db.label,image=self.ico_record,tags=self.RECORD)
        self.tree.insert(record_item,'end',text='dummy') #dummy_sub_item

        self.item_to_record[record_item]=record
        self.record_to_item[record]=record_item


        self.item_to_record_dict[record_item] = record_db.data

        self.main_update()

    @block_actions_processing
    @gui_block
    @logwrapper
    def records_show(self):
        #print('records_show...')

        self.menu_disable()

        self_tree = self.tree

        self_tree.delete(*self_tree.get_children())

        self.item_to_record={}
        self.record_to_item={}

        self.item_to_record_dict={}

        for record in sorted(librer_core.records,key=lambda x : x.db.creation_time):
            self.single_record_show(record)

        self.menu_enable()

        self_status=self.status=self.status_progress

        self_status('')

        if children := self_tree.get_children():
            self_tree.focus(children[0])

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
    def csv_save(self):
        if csv_file := asksaveasfilename(initialfile = 'librer_scan.csv',defaultextension=".csv",filetypes=[("All Files","*.*"),("CSV Files","*.csv")]):

            self.status('saving CSV file "%s" ...' % str(csv_file))
            librer_core.write_csv(str(csv_file))
            self.status('CSV file saved: "%s"' % str(csv_file))

    @logwrapper
    def clip_copy_full_path_with_file(self):
        print('clip_copy_full_path_with_file')
        return
        if self.sel_path_full and self.sel_file:
            self.clip_copy(path_join(self.sel_path_full,self.sel_file))
        elif self.sel_crc:
            self.clip_copy(self.sel_crc)

    @logwrapper
    def clip_copy_full(self):
        print('clip_copy_full')
        return

        if self.sel_path_full:
            self.clip_copy(self.sel_path_full)
        elif self.sel_crc:
            self.clip_copy(self.sel_crc)

    @logwrapper
    def clip_copy_file(self):
        print('clip_copy_file')
        return

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
                    self.main.after_idle(lambda : self.tree_action(item))

        #return "break"

    @logwrapper
    def tree_action(self,item):
        tree=self.tree
        try:
            record_item,record_name = self.get_item_record(item)
            record = self.item_to_record[record_item]

            kind = tree.set(item,'kind')
            if kind == self.DIR :
                opened = tree.item(item)['open']

                if not opened:
                    self.open_item(None,item)

                #return "break"

            else:
                inode,dev = self.node_to_inodedev[item]
                node_cd = record.custom_data[(inode,dev)] if inode and dev else None

                if node_cd:
                    self.text_info_dialog.show('Custom Data',node_cd)
        except Exception as e:
            print('tree_action',e)

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
        CONFIG_DIR = LIBRER_EXECUTABLE_DIR
        LOG_DIR = sep.join([LIBRER_EXECUTABLE_DIR,'logs'])

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
                LOG_DIR = user_log_dir('librer','PJDude')
                CONFIG_DIR = user_config_dir('librer')
            except Exception as e_import:
                print(e_import)

        else:
            LOG_DIR = sep.join([LIBRER_EXECUTABLE_DIR,"logs"])
            CONFIG_DIR = LIBRER_EXECUTABLE_DIR

        log=abspath(p_args.log[0]) if p_args.log else LOG_DIR + sep + strftime('%Y_%m_%d_%H_%M_%S',localtime(time()) ) +'.txt'

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
