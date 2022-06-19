import os
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

def initialise_plugin():
	show_in_right_click_menu = True
	run_on_files = False
	run_on_folders = True
	extension_filter = [] # which files the plugin can run on

	return locals()
		
class Plugin:
	def __init__(self, mainapp, master, plugin, path, *args, **kwargs):
		print(*args)
		self.mainapp = mainapp
		self.master = master
		self.plugin = plugin
		self.path = path
		
		self.find_files()
		self.w = FileWindow(self.mainapp, self.master, self)
		self.master.wait_window(self.w.top)		
		
	def find_files(self):
		self.files = []
		for file in os.listdir(self.path):
			if file.endswith(".csv"):
				self.files.append(file)
				
		
class FileWindow(ttk.Frame):
	def __init__(self, mainapp, master, plugin):
		super(FileWindow, self).__init__()
		top=self.top=Toplevel(master)
		#top.grab_set()
		self.mainapp = mainapp
		
		if len(plugin.files) == 0:
			ttk.Label(self.top, text="No csv files found").grid(row=1, column=0, padx=5, pady=5, sticky='nw')
		else:
			self.search_text = tk.Text(self.top, width=110, height=20)
			self.search_text.grid(row=1, column=0, columnspan=8, sticky='NSEW', padx=5, pady=5, ipadx=2, ipady=5)
			
			for file in plugin.files:
				self.search_text.insert(END, file + "\n")
		
		self.button = 'cancel'
		
		# Buttons
		self.ok_btn = ttk.Button(self.top, text='OK', width=10, style='success.TButton', command=lambda button='ok': self.cleanup(button))
		self.ok_btn.grid(row=2, column=0, padx=5, pady=5, sticky='ne')
		
	def cleanup(self, button):
		self.top.destroy()