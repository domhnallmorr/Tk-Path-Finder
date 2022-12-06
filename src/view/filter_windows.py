import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *


class FilterExtensionWindow(ttk.Frame):
	def __init__(self, master, file_types, lock_filter):
		super(FilterExtensionWindow, self).__init__()
		top=self.top=Toplevel(master)
		top.grab_set()
		self.file_types = file_types
		self.lock_filter = lock_filter

		self.button = "cancel"
		self.top.title(f"Filter Files by Extension")
		
		self.all_files = IntVar(value=1)
		ttk.Checkbutton(self.top, text=f"File Types in Current Directory:", variable=self.all_files, command=self.select_all_file).grid(row=0, column=1, sticky='w', padx=5, pady=5)
		ttk.Separator(self.top, orient="horizontal").grid(row=1, column=1, sticky='ew', padx=5, pady=5)
		
		row = 2
		for file_extension in sorted(list(self.file_types.keys()), key=str.casefold): #ignore case
			self.file_types[file_extension]["var"] = IntVar(value=self.file_types[file_extension]["var"])
			var = self.file_types[file_extension]["var"]
			description = self.file_types[file_extension]["description"]
			ttk.Checkbutton(self.top, text=f"{description} ({file_extension})", variable=var).grid(row=row, column=1, sticky='w', padx=5, pady=5)
			row +=  1

		ttk.Separator(self.top, orient="horizontal").grid(row=row, column=1, sticky='ew', padx=5, pady=5)
		
		# Lock filter
		initialvalue = 0
		if self.lock_filter is True:
			initialvalue = 1
		self.lock_filter = IntVar(value=initialvalue)
		ttk.Checkbutton(self.top, text=f"Lock in this filter", variable=self.lock_filter).grid(row=row+1, column=1, sticky="w", padx=5, pady=10)	
					
		# Buttons
		self.ok_btn = ttk.Button(self.top, text="OK", width=10, style="success.TButton", command=lambda button="ok": self.cleanup(button))
		self.ok_btn.grid(row=row+2, column=2, padx=5, pady=10, sticky="ne")
		self.cancel_btn = ttk.Button(self.top, text="Cancel", width=10, style="danger.TButton", command=lambda button="cancel": self.cleanup(button))
		self.cancel_btn.grid(row=row+2, column=3, padx=5, pady=10, sticky="nw")		
		
	def select_all_file(self):
		for file_extension in self.file_types.keys():
			self.file_types[file_extension]["var"].set(self.all_files.get())
		
	def cleanup(self, button):
		if button == "ok":
			self.filter = []		
			for file_extension in self.file_types.keys():
				if self.file_types[file_extension]["var"].get() == 0:
					self.filter.append(file_extension)
			
			if self.lock_filter.get() == 1:
				self.lock_filter = True
			else:
				self.lock_filter = False
			self.button = button
				
		self.top.destroy()
		
		
class FilterNameWindow(ttk.Frame):
	def __init__(self, master, view, data):
		super(FilterNameWindow, self).__init__()
		top=self.top=Toplevel(master)
		top.grab_set()
		
		self.view = view
		self.files = data["file_data"]
		self.lock_filter = data["lock_filter"]

		self.button = "cancel"
		self.top.title(f"Filter Files by Name")
		
		
		Label(self.top, text="Enter Text:").grid(row=0, column=0, sticky='ew', padx=5, pady=5)
		self.text_entry = Entry(self.top, width=50)
		self.text_entry.grid(row=0, column=1, columnspan=3 ,sticky='ew', padx=5, pady=5)
		self.text_entry.insert(0, data["filter_text"])
		
		# Buttons
		self.ok_btn = ttk.Button(self.top, text="OK", width=10, style="success.TButton", command=lambda button="ok": self.cleanup(button))
		self.ok_btn.grid(row=1, column=2, padx=5, pady=10, sticky="ne")
		self.cancel_btn = ttk.Button(self.top, text="Cancel", width=10, style="danger.TButton", command=lambda button="cancel": self.cleanup(button))
		self.cancel_btn.grid(row=1, column=3, padx=5, pady=10, sticky="nw")	
		
		self.top.grid_columnconfigure(1, weight=1)
		
	def cleanup(self, button):
		if button == "ok":
			self.text = self.text_entry.get()
			if self.text.strip() == "":
				self.text = None
				
			self.button = button
		else:
			self.text = None
			
		self.filter = [self.text]
		self.top.destroy()
			
		