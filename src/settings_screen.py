import os
import tkinter as tk
from tkinter import *
from tkinter import ttk
import copy

from tkinter.ttk import *
from tkinter import messagebox
from tkinter import simpledialog
import win32api

import autoscrollbar
import treeview_functions

def get_file_description(windows_exe):
    try:
        language, codepage = win32api.GetFileVersionInfo(windows_exe, '\\VarFileInfo\\Translation')[0]
        stringFileInfo = u'\\StringFileInfo\\%04X%04X\\%s' % (language, codepage, "FileDescription")
        description = win32api.GetFileVersionInfo(windows_exe, stringFileInfo)
    except:
        description = "unknown"
        
    return description

class SettingsWindow(ttk.Frame):
	def __init__(self, mainapp, master):
		super(SettingsWindow, self).__init__()
		top=self.top=Toplevel(master)
		top.grab_set()
		self.mainapp = mainapp
		self.button = 'cancel'
		
		self.open_with_apps = copy.deepcopy(mainapp.open_with_apps)
		treeview_data = self.convert_open_with_apps_to_list()
		self.setup_label_frames()
		self.setup_text_editor()
		self.setup_open_with()
		treeview_functions.write_data_to_treeview_general(self.treeview, 'replace', treeview_data)

	def setup_label_frames(self):
		self.text_editor_frame = LabelFrame(self.top,text="Text Editor:")
		self.text_editor_frame.grid(row=0, column=0, columnspan = 8, rowspan = 2,sticky='NSEW',padx=5, pady=5, ipadx=2, ipady=5)

		self.open_with_frame = LabelFrame(self.top,text="Open With:")
		self.open_with_frame.grid(row=2, column=0, columnspan = 8, rowspan = 2,sticky='NSEW',padx=5, pady=5, ipadx=2, ipady=5)
	
	def setup_text_editor(self):
		ttk.Label(self.text_editor_frame, text='Text Editor:').grid(row=0, column=0, columnspan=1, sticky='NSEW', pady=self.mainapp.default_pady)
		self.text_editor_entry = ttk.Entry(self.text_editor_frame, width=100)
		self.text_editor_entry.grid(row=0, column=1, columnspan=15, sticky='NSEW', pady=self.mainapp.default_pady)
		
		if self.mainapp.text_editor is not None:
			self.text_editor_entry.insert(0, self.mainapp.text_editor)
			
	def setup_open_with(self):
		ttk.Label(self.open_with_frame, text='File Extension:').grid(row=0, column=0, columnspan=1, sticky='NSEW', pady=self.mainapp.default_pady)
		self.extension_entry = ttk.Entry(self.open_with_frame)
		self.extension_entry.grid(row=0, column=1, columnspan=15, sticky='NSEW', pady=self.mainapp.default_pady)
		#self.extension_entry.insert(0, '.py')
		
		ttk.Label(self.open_with_frame, text='App Path:').grid(row=1, column=0, columnspan=1, sticky='NSEW', pady=self.mainapp.default_pady)
		self.app_entry = ttk.Entry(self.open_with_frame)
		self.app_entry.grid(row=1, column=1, columnspan=15, sticky='NSEW', pady=self.mainapp.default_pady)
		#self.app_entry.insert(0, 'C:\Program Files\Sublime Text 3\sublime_text.exe')

		
		# submit button
		self.submit = ttk.Button(self.open_with_frame, text='Add', style='success.TButton', command=self.add)
		self.submit.grid(row=3, column=0, sticky='ew', pady=10, padx=(0, 10))
		
		self.edit = ttk.Button(self.open_with_frame, text='Edit Selected', style='info.TButton', command=self.edit_row)
		self.edit.grid(row=3, column=1, sticky='ew', pady=10, padx=(0, 10))

		self.delete_btn = ttk.Button(self.open_with_frame, text='Delete Selected', style='danger.TButton', command=self.delete_row)
		self.delete_btn.grid(row=3, column=2, sticky='ew', pady=10, padx=(0, 10))
		
		column_names = ['File Extension', 'App']
		column_widths = [200, 600]
		height = 20

		self.treeview = treeview_functions.create_treeview(self.open_with_frame, column_names, column_widths, height)
		#self.treeview.pack(expand=True, fill=BOTH)
		self.treeview.grid(row=4, column=0, columnspan=16, sticky='NSEW', pady=self.mainapp.default_pady)
		self.treeview.bind("<Double-1>", self.on_left_click)
		
		vsb = autoscrollbar.AutoScrollbar(self.open_with_frame, orient="vertical", command=self.treeview.yview)
		vsb.grid(row=4, column=16, sticky='NSEW')
		self.treeview.configure(yscrollcommand=vsb.set)
		
		# Buttons
		self.ok_btn = ttk.Button(self.open_with_frame, text='OK', width=10, style='success.TButton', command=lambda button='ok': self.cleanup(button))
		self.ok_btn.grid(row=5, column=0, padx=5, pady=5, sticky='ne')
		self.cancel_btn = ttk.Button(self.open_with_frame, text='Cancel', width=10, style='danger.TButton', command=lambda button='cancel': self.cleanup(button))
		self.cancel_btn.grid(row=5, column=1, padx=5, pady=5, sticky='nw')
		
	def add(self):
		file_extension = self.extension_entry.get()
		app_path = self.app_entry.get()
		
		if file_extension in self.open_with_apps.keys():
			self.open_with_apps[file_extension].append(app_path)
		else:
			self.open_with_apps[file_extension] = [app_path]
		
		treeview_data = self.convert_open_with_apps_to_list()
		treeview_functions.write_data_to_treeview_general(self.treeview, 'replace', treeview_data)
	
	def edit_row(self):
		idx, data = treeview_functions.get_current_selection(self.treeview)
		iid = self.treeview.selection()[0]
		
		current_extension = self.treeview.item(iid, 'text')
		current_app = self.treeview.item(iid, 'values')[0]
		
		if self.extension_entry.get() != current_extension:
			self.open_with_apps[current_extension].remove(current_app)
			
			if len(self.open_with_apps[current_extension]) == 0:
				del self.open_with_apps[current_extension]
			
			if self.extension_entry.get() not in self.open_with_apps.keys():
				self.open_with_apps[self.extension_entry.get()] = []
			
			self.open_with_apps[self.extension_entry.get()].append(self.app_entry.get())
			
		else:
			self.open_with_apps[self.extension_entry.get()].replace(current_app, self.app_entry.get())
		
		self.treeview.item(iid, text=self.extension_entry.get())
		self.treeview.item(iid, values=[self.app_entry.get()])
		
	def delete_row(self):
		iid = self.treeview.selection()[0]
		current_extension = self.treeview.item(iid, 'text')
		current_app = self.treeview.item(iid, 'values')[0]
		
		msg = messagebox.askyesno(title='Delete App', message='Delete This App? This Cannot be Undone.')
		if msg:
			self.treeview.delete(iid)
			self.open_with_apps[current_extension].remove(current_app)
			
			if len(self.open_with_apps[current_extension]) == 0:
				del self.open_with_apps[current_extension]

	def convert_open_with_apps_to_list(self):
		extensions = sorted(list(self.open_with_apps.keys()))
		treeview_data = []
		
		for e in extensions:
			for app in self.open_with_apps[e]:
				treeview_data.append([e, app])
				
		return treeview_data

	def get_app_name(self):
		app_name = get_file_description(self.app_entry.get())
		
		self.app_entry.insert(0, app_name)

	def on_left_click(self, event):
		self.extension_entry.delete(0, 'end')
		self.extension_entry.insert(0, self.treeview.item(self.treeview.selection(), 'text'))

		self.app_entry.delete(0, 'end')
		self.app_entry.insert(0, self.treeview.item(self.treeview.selection(), 'values')[0])		
		
	def cleanup(self, button):
		self.button = button
		self.text_editor = self.text_editor_entry.get()
		self.top.destroy()