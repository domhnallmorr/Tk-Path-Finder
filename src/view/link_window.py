import os
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import simpledialog
from tkinter import messagebox


class AddLinkWindow(ttk.Frame):
	def __init__(self, master, mode, text="", path="",):
		super(AddLinkWindow, self).__init__()
		top=self.top=Toplevel(master)
		top.grab_set()

		self.mode = mode
		if mode == "edit":
			self.top.title(f"Edit Link")
		else:
			self.top.title(f"Add New Link")
		self.button = "cancel"
		
		ttk.Label(self.top, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
		ttk.Label(self.top, text="Path:").grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
		
		self.name_entry = ttk.Entry(self.top, width=100)
		self.name_entry.grid(row=0, column=1, columnspan=4, padx=5, pady=5, sticky="nsew")
		
		self.path_entry = ttk.Entry(self.top, width=100)
		self.path_entry.grid(row=1, column=1, columnspan=4, padx=5, pady=5, sticky="nsew")
		
		self.ok_btn = ttk.Button(self.top, text="OK", width=10, style="success.TButton", command=lambda button="ok": self.cleanup(button))
		self.ok_btn.grid(row=2, column=3, padx=5, pady=5, sticky="ne")
		self.cancel_btn = ttk.Button(self.top, text="Cancel", width=10, style="danger.TButton", command=lambda button="cancel": self.cleanup(button))
		self.cancel_btn.grid(row=2, column=4, padx=5, pady=5, sticky="nw")
		
		self.top.grid_columnconfigure(1, weight=1)
		
		if mode == "edit":
			self.name_entry.insert(0, text)
			self.path_entry.insert(0, path)
			self.original_name = text
				
	def cleanup(self, button):
		if button == "ok":
			self.name = self.name_entry.get().strip()
			self.path = self.path_entry.get()
			data_ok = True
			
			if self.name == "":
				messagebox.showerror("Error", message="Enter A Name")
				data_ok = False
					
			elif not os.path.isdir(self.path):
				messagebox.showerror("Error", message="The Path Entered Does Not Exist")
				data_ok = False
				
			if data_ok:	
				# For mapped drive, handle for inclusion of trailing \ e.g C:\
				if len(self.path) == 2 and self.path[-1] == ":":
					self.path = self.path + "\\"
				self.button = button
				self.top.destroy()
		else:
			self.top.destroy()