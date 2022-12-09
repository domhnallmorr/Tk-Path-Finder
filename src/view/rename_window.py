import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

class RenameWindow(ttk.Frame):
	def __init__(self, master, view, initialvalue, component_type, mode="Rename"):
		super(RenameWindow, self).__init__()
		top=self.top=Toplevel(master)
		top.grab_set()
		self.view = view
		
		if component_type == "branch_tab":
			self.top.title(f"{mode} Branch Tab")
		else:
			self.top.title(f"{mode} Tab")
			
		if mode == "new_file":
			self.top.title("New File")
		if mode == "edit_file":
			self.top.title("Rename File")

		if mode == "new_excel":
			self.top.title("New Excel File")

		if mode == "new_word":
			self.top.title("New Word File")
			
		if mode == "new_quick_access":
			self.top.title("New Quick Access Folder")

		if mode == "edit_quick_access":
			self.top.title("Edit Quick Access Folder")
			
		self.initialvalue = initialvalue
		self.component_type = component_type
		self.button = "cancel"
		
		self.name_entry = ttk.Entry(self.top, width=60)
		self.name_entry.grid(row=1, column=0, columnspan=5, padx=self.view.default_padx, pady=self.view.default_pady, sticky="ew")
		self.name_entry.insert(0, initialvalue)
		self.name_entry.bind('<Return>', lambda event, button="ok": self.cleanup(button, event))
		self.top.grid_columnconfigure(0, weight=1)
		
		if component_type == "branch_tab":
			self.lock = IntVar(value=1)
			ttk.Checkbutton(self.top, text="Lock Name", variable=self.lock).grid(row=2, column=2, sticky='w', padx=self.view.default_padx, pady=self.view.default_pady)
		
		# Buttons
		self.ok_btn = ttk.Button(self.top, text="OK", width=10, style="success.TButton", command=lambda button="ok": self.cleanup(button))
		self.ok_btn.grid(row=2, column=3, padx=self.view.default_padx, pady=self.view.default_pady, sticky='ne')
		self.cancel_btn = ttk.Button(self.top, text='Cancel', width=10, style='danger.TButton', command=lambda button='cancel': self.cleanup(button))
		self.cancel_btn.grid(row=2, column=4, padx=self.view.default_padx, pady=self.view.default_pady, sticky='nw')	
		
		self.name_entry.focus()

	def cleanup(self, button, event=None):
		if button == "ok":
			if self.name_entry.get() == '':
				messagebox.showerror("Error", message="Enter a Name")
			else:
				self.name = self.name_entry.get()
				
				if self.component_type == "branch_tab":
					if self.lock.get() == 1:
						self.text_locked = True
					else:
						self.text_locked = False
						
				self.button = "ok"
				self.top.destroy()
		else:
			self.top.destroy()
		