import os
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import simpledialog

import autoscrollbar

class SearchWindow(ttk.Frame):
	def __init__(self, mainapp, master, branch_tab):
		super(SearchWindow, self).__init__()
		top=self.top=Toplevel(master)
		top.grab_set()
		self.mainapp = mainapp
		self.branch_tab = branch_tab
		
		self.top.title(f"Search: {self.branch_tab.explorer.current_directory}")
		self.directory = self.branch_tab.explorer.current_directory
		self.button = 'cancel'
		self.top.grid_rowconfigure(1, weight=1)
		
		#Label_frames
		self.options_frame = ttk.LabelFrame(self.top, text='Options:')
		self.options_frame.grid(row=0, column=0, padx=5, pady=5, sticky='W')

		self.results_frame = ttk.LabelFrame(self.top, text='Search Results:')
		self.results_frame.grid(row=1, column=0,  padx=5, pady=5, sticky='NS')
		self.results_frame.grid_rowconfigure(1, weight=1)
		
		# Widgets
		ttk.Label(self.options_frame, text='Search Type:').grid(row=0, column=0, padx=5, pady=5)
		self.search_type_combo = ttk.Combobox(self.options_frame, values=['Raw Text', 'Clickable Text'], state='readonly')
		self.search_type_combo.set('Raw Text')
		self.search_type_combo.config(state='disabled')
		self.search_type_combo.grid(row=0, column=1, padx=5, pady=5, sticky='W')
		
		ttk.Label(self.options_frame, text='Text:').grid(row=1, column=0, padx=5, pady=5)
		self.search_bar = ttk.Entry(self.options_frame, width=50)
		self.search_bar.grid(row=1, column=1, padx=5, pady=5)

		ttk.Label(self.options_frame, text='File Extension:').grid(row=2, column=0, padx=5, pady=5)
		self.extension_extry = ttk.Entry(self.options_frame, width=50)
		self.extension_extry.grid(row=2, column=1, padx=5, pady=5)
		
		self.python_raw_string = IntVar()
		ttk.Checkbutton(self.options_frame, text="Python Raw String List Output", variable=self.python_raw_string).grid(row=1, column=2, sticky='w', padx=5, pady=5)

		b1 = ttk.Button(self.options_frame, text='Search', 
					command=self.on_search, style='primary.TButton')
		b1.grid(row=3, column=0, sticky='ew', pady=5, ipadx=10)
		
		# Raw Text Widget
		self.search_text = tk.Text(self.results_frame, width=110, height=20)
		self.search_text.grid(row=1, column=0, columnspan=8, sticky='NSEW', padx=5, pady=5, ipadx=2, ipady=5)
		
		vsb = autoscrollbar.AutoScrollbar(self.results_frame, orient="vertical", command=self.search_text.yview)
		vsb.grid(row=1, column=8, sticky='NSEW')
		self.search_text.configure(yscrollcommand=vsb.set)
		
	def on_search(self):
		print('searching')
		#results = []
		self.search_text.delete('1.0', END)

		for root, dirs, files in os.walk(self.directory):
			for file in files:
				if self.search_bar.get() in file:
					process_file = True
					if self.extension_extry.get().strip() != '':
						filename, file_extension = os.path.splitext(file)
						if file_extension != self.extension_extry.get():
							process_file = False
							
					if process_file:
						if self.python_raw_string.get() == 1:
							self.search_text.insert(END, 'r"')
							
						self.search_text.insert(END, os.path.join(root, file))
						 
						if self.python_raw_string.get() == 1:
							self.search_text.insert(END, '",')	

						self.search_text.insert(END, '\n')
		