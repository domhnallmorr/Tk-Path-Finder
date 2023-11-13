import os
import subprocess
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import simpledialog

from custom_widgets import autoscrollbar

class SearchWindow(ttk.Frame):
	def __init__(self, master, data, view, file_extensions):
		super(SearchWindow, self).__init__()
		top=self.top=Toplevel(master)
		#top.grab_set()
		self.data = data
		self.view = view
		self.directory = data["current_directory"]
		self.top.title(f"Search: {self.directory}")
		self.file_extensions = file_extensions

		self.button = "cancel"
		self.top.grid_rowconfigure(1, weight=1)
		self.top.grid_columnconfigure(1, weight=1)


		# Notebook
		self.notebook = ttk.Notebook(self.top)
		self.notebook.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='EW')

		self.search_files_tab = ttk.Frame(self.notebook)
		self.search_text_tab = ttk.Frame(self.notebook)
		self.notebook.add(self.search_files_tab, text="Search for Files")
		self.notebook.add(self.search_text_tab, text="Search for Text")

		self.search_files_tab.grid_columnconfigure(1, weight=1)

		#Label_frames
		self.options_frame = ttk.LabelFrame(self.search_files_tab, text='Options:')
		self.options_frame.grid(row=0, column=0, padx=5, pady=5, sticky='W')

		self.text_search_options_frame = ttk.LabelFrame(self.search_text_tab, text='Options:')
		self.text_search_options_frame.grid(row=0, column=0, padx=5, pady=5, sticky='W')

		self.results_frame = ttk.LabelFrame(self.top, text='Search Results:')
		self.results_frame.grid(row=1, column=0,  columnspan=2, padx=5, pady=5, sticky='NSEW')
		self.results_frame.grid_rowconfigure(1, weight=1)
		self.results_frame.grid_columnconfigure(0, weight=1)
		
		# WIDGETS SEARCH FOR FILES TAB
		
		ttk.Label(self.options_frame, text='Search For:').grid(row=1, column=0, padx=5, pady=5, sticky="E")
		self.search_for_combo = ttk.Combobox(self.options_frame, width=30, values=['Files', 'Folders'], state='readonly')
		self.search_for_combo.set('Files')
		self.search_for_combo.grid(row=1, column=1, padx=5, pady=5, sticky='W')

		ttk.Label(self.options_frame, text='Search Where:').grid(row=2, column=0, padx=5, pady=5, sticky="E")
		self.search_where_combo = ttk.Combobox(self.options_frame, width=30, values=['Parent Directory', 'Parent and Sub Directories'], state='readonly')
		self.search_where_combo.set('Parent Directory')
		self.search_where_combo.grid(row=2, column=1, padx=5, pady=5, sticky='W')

		ttk.Label(self.options_frame, text='Output:').grid(row=3, column=0, padx=5, pady=5, sticky="E")
		self.output_combo = ttk.Combobox(self.options_frame, width=30, values=["Full Path", "Name Only"], state="readonly")
		self.output_combo.set('Full Path')
		self.output_combo.grid(row=3, column=1, padx=5, pady=5, sticky='W')
		
		ttk.Label(self.options_frame, text='Text:').grid(row=4, column=0, padx=5, pady=5, sticky="E")
		self.search_bar = ttk.Entry(self.options_frame, width=60)
		self.search_bar.grid(row=4, column=1, padx=5, pady=5)
		self.search_bar.bind('<Return>', self.on_search)
		
		ttk.Label(self.options_frame, text='File Extension:').grid(row=5, column=0, padx=5, pady=5, sticky="E")
		self.extension_extry = ttk.Entry(self.options_frame, width=60)
		self.extension_extry.grid(row=5, column=1, padx=5, pady=5)
		self.extension_extry.bind('<Return>', self.on_search)
		
		self.python_raw_string = IntVar()
		ttk.Checkbutton(self.options_frame, text="Python Raw String List Output", variable=self.python_raw_string).grid(row=6, column=1, columnspan=1, sticky='w', padx=5, pady=5)

		b1 = ttk.Button(self.options_frame, text='Search', width=10,
					command=self.on_search, style='primary.TButton')
		b1.grid(row=7, column=1, sticky='e', padx=5, pady=5, ipadx=10)

		# WIDGETS SEARCH FOR TEXT TAB
		ttk.Label(self.text_search_options_frame, text='Text:').grid(row=4, column=0, padx=5, pady=5, sticky="E")
		self.text_to_find_entry = ttk.Entry(self.text_search_options_frame, width=60)
		self.text_to_find_entry.grid(row=4, column=1, padx=5, pady=5)
		self.text_to_find_entry.bind('<Return>', self.on_search)

		ttk.Label(self.text_search_options_frame, text="File Extension:").grid(row=5, column=0, padx=5, pady=5, sticky="E")
		self.text_extension_combo = ttk.Combobox(self.text_search_options_frame, values=self.file_extensions)
		if len(self.file_extensions) > 0:
			self.text_extension_combo.set(self.file_extensions[0])
			self.text_extension_combo.config(state="readonly")
		else:
			self.text_extension_combo.config(state="disabled")
		self.text_extension_combo.grid(row=5, column=1, padx=5, pady=5, sticky="W")

		self.case_insensitive = IntVar(value=0)
		ttk.Checkbutton(self.text_search_options_frame, text="Case Insensitive", variable=self.case_insensitive).grid(row=6, column=1, padx=5, pady=5, sticky="W")
		
		b2 = ttk.Button(self.text_search_options_frame, text="Search", width=10,
					command=self.on_search_text, style="primary.TButton")
		b2.grid(row=7, column=1, sticky='e', padx=5, pady=5, ipadx=10)

		# Raw Text Widget
		self.search_text = tk.Text(self.results_frame, width=130, height=20)
		self.search_text.grid(row=1, column=0, columnspan=8, sticky='NSEW', padx=5, pady=5, ipadx=2, ipady=5)
		
		vsb = autoscrollbar.AutoScrollbar(self.results_frame, orient="vertical", command=self.search_text.yview)
		vsb.grid(row=1, column=8, sticky='NSEW')
		self.search_text.configure(yscrollcommand=vsb.set)
		
	def on_search(self, event=None):
		#results = []
		self.search_text.delete('1.0', END)
		
		if self.search_where_combo.get() == 'Parent and Sub Directories':
			for root, dirs, files in os.walk(self.directory):
				# SEARCH FOR FILES #################################
				if self.search_for_combo.get() == 'Files':
					for file in files:
						if self.search_bar.get().lower() in file.lower():
							process_file = True
							if self.extension_extry.get().strip() != '':
								filename, file_extension = os.path.splitext(file)
								if file_extension != self.extension_extry.get():
									process_file = False
									
							if process_file:
								self.add_file_to_text(root, file)
			
				# SEARCH FOR FOLDERS #################################
				else:
					for d in dirs:
						if self.search_bar.get().lower() in d.lower():
							if self.python_raw_string.get() == 1:
								self.search_text.insert(END, 'r"')

							if self.output_combo.get() == "Name Only":
								self.search_text.insert(END, d)	
							else:
								self.search_text.insert(END, os.path.join(root, d))

							if self.python_raw_string.get() == 1:
								self.search_text.insert(END, '",')
							self.search_text.insert(END, '\n')						

		else: # Parent directory only
			if self.search_for_combo.get() == "Files":
				for file in self.data["file_data"]:
					if self.search_bar.get().lower() in file[0].lower():
						process_file = True
						if self.extension_extry.get().strip() != '':
							filename, file_extension = os.path.splitext(file[0])
							if file_extension != self.extension_extry.get():
								process_file = False
						
						if process_file:
							self.add_file_to_text(self.directory, file[0])
			else: # search for folders
				for d in self.data["directory_data"]:
					if self.search_bar.get().lower() in d[0].lower():
						if self.python_raw_string.get() == 1:
							self.search_text.insert(END, 'r"')

						if self.output_combo.get() == "Name Only":
							self.search_text.insert(END, d[0])
						else:
							self.search_text.insert(END, os.path.join(self.directory, d[0]))

						if self.python_raw_string.get() == 1:
							self.search_text.insert(END, '",')
						self.search_text.insert(END, '\n')	

		# If text widget is empty, add text saying nothing found
		text_content = self.search_text.get("1.0", "end-1c").strip()
		if text_content == "":
			self.search_text.insert(END, "No items match your search")

	def on_search_text(self, event=None):
		self.search_text.delete('1.0', END)

		if len(self.file_extensions):
			text_to_find = self.text_to_find_entry.get()
			extensions_to_check = self.text_extension_combo.get()

			if self.case_insensitive.get() == 1:
				command = ['findstr', "/I", f'{text_to_find}', f'{self.directory}\\*{extensions_to_check}']
			else:
				command = ['findstr', f'{text_to_find}', f'{self.directory}\\*{extensions_to_check}']

			try:
				result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True).stdout
				self.search_text.insert(END, result)
			except Exception as e:
				if "non-zero" in str(e):
					self.search_text.insert(END, "Failed to Find Matching Text")
				else:
					self.view.show_error(str(e))
		else:
			self.search_text.insert(END, "No Files in Directory")

	def add_file_to_text(self, directory, filename):
		if not filename.startswith('~$'): # avoid temporary files
			
			if self.python_raw_string.get() == 1:
				self.search_text.insert(END, 'r"')
			
			if self.output_combo.get() == "Name Only":
				self.search_text.insert(END, filename)
			else:
				self.search_text.insert(END, os.path.join(directory, filename))
			 
			if self.python_raw_string.get() == 1:
				self.search_text.insert(END, '",')	

			self.search_text.insert(END, '\n')