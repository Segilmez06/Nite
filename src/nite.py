#!/bin/python3
import sys
import os
import platform

from tkinter import *
from tkinter.messagebox import *
from tkinter.dialog import *
from tkinter.filedialog import *

import base64, zlib
import tempfile

# Blank icon
icon_data = zlib.decompress(base64.b64decode('eJxjYGAEQgEBBiDJwZDBysAgxsDAoAHEQCEGBQaIOAg4sDIgACMUj4JRMApGwQgF/ykEAFXxQRc='))
icon_file = tempfile.mkstemp()[1]
icon = open(icon_file, 'wb')
icon.write(icon_data)
icon.close()

# Check for Mica style support
if platform.system() == 'Windows':
    sys_ver = platform.version()
    win_ver = sys_ver[sys_ver.rfind('.')+1:]
    if int(win_ver) > 22000:
        mica_supported = True
        try:
            from win32mica import MICAMODE, ApplyMica
            from ctypes import windll
        except ImportError as e:
            mica_supported = False
    else:
        mica_supported = False
mica_supported = False

class Nite(Tk):

    def __init__(self, filename, icon_file, mica_supported):
        super().__init__()
        self.filename = filename
        self.iconpath = icon_file
        self.mica_support = mica_supported
        self.document = os.path.basename(self.filename)
        
        
        # Window
        self.title(f'{self.document} - Nite')
        self.geometry('800x450')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.bind('<Control-s>', self.nite_save)
        self.bind('<Control-w>', self.nite_exit)
        
        
        # Customizations
        self.iconbitmap(default=self.iconpath)
        self.bg = '#fff'
        self.fg = '#000'
        self.h_bg = Label().cget('bg')
        if self.mica_support:
            self.bg = '#000'
            self.fg = '#fff'
            self.h_bg = '#000'
            self.configure(bg=self.bg)
            self.update()
            handle = windll.user32.GetParent(self.winfo_id())
            ApplyMica(handle, MICAMODE.DARK)

        
        # Input Box
        self.edit = Text(self, font=('Helvetica 12'), borderwidth=0, background=self.bg, foreground=self.fg, insertbackground=self.fg)
        self.edit.grid(row=0, column=0, columnspan=4, sticky=N+S+W+E, padx=10, pady=10)
        self.edit.focus_set()
        self.edit.bind('<KeyPress>', self.hide_hint)


        # Hint Label
        self.label = Label(self, text="Ctrl+S : Save     CTRL+W : Exit", background=self.h_bg, foreground=self.fg)
        self.label.grid(column=0, row=1)
        
        
        # Read from file
        f = open(self.filename, 'r')
        c = f.read()
        self.edit.insert(END, c)
        f.close()
        self.checkpoint()

        
    # Hide hint message after key pressed    
    def hide_hint(self,e,*args,**kwargs):
        self.label.grid_forget()
        self.edit.unbind('<KeyPress>')

        
    def nite_exit(self,*args,**kwargs):
        if self.file_content != self.get_content():
            if askyesno('Unsaved changes', 'Do you want to save changes to the file?', icon='info'):
                self.nite_save()
        exit()

    def nite_save(self,*args,**kwargs):
        c = self.get_content()
        f = open(self.filename, 'w')
        f.write(c)
        f.close()
        self.checkpoint()

    def get_content(self,*args,**kwargs):
        text = self.edit.get(0.0, END)
        return text[:text.rfind('\n')]

    def checkpoint(self,*args,**kwargs):
        self.file_content = self.get_content()

if len(sys.argv) > 1:
    filepath = sys.argv[1]
    if os.path.exists(filepath):
        Nite(filepath,icon_file,mica_supported).mainloop()
