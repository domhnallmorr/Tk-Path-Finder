import os

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from ttkbootstrap.constants import *

class AddressBarEntry(ttk.Entry):
	def __init__(self, branch_tab):
		super(AddressBarEntry, self).__init__(branch_tab)
		self.branch_tab = branch_tab
		self.bind('<Return>', self.enter_event)
		self.raw_path = False
		
		self.buttons = []
		self.bind("<FocusIn>", self.on_focusin)
		self.bind("<FocusOut>", self.on_focusout)
		self.bind("<Escape>", self.on_escape)
		self.bind("<Configure>", lambda event: self.truncate_breadcrumbs())
		self.text = None

	def update_bar(self, text):
		self.text = text
		self.delete(0, END) #deletes the current value
		self.update()
		
		# Add buttons to address bar
		for btn in self.buttons:
			btn.grid_forget()
			
		self.raw_path = False
		if text.startswith("\\"):
			self.raw_path = True
			
		if self.raw_path is False:
			folders = text.split(os.sep)
		else:
			folders = text[2:].split(os.sep)
			folders[0]
		
		self.buttons = []
		
		for idx, folder in enumerate(folders):
			if idx == 0:
				path = folder + os.sep
			else:
				path = os.path.join(path, folder)
			
			btn = Button(self, text=folder, bootstyle="secondary",)
			btn.grid(row=0, column=idx)
			btn.bind("<Button-1>", lambda event=None, path=path: self.button_clicked(event, path))
			btn.bindtags((btn, btn.winfo_class(), self, self.winfo_class(), "all"))
			self.buttons.append(btn)

		self.truncate_breadcrumbs()
		self.branch_tab.focus()
		
	def enter_event(self, event):
		# -------------- CALL THE CONTROLLER METHOD TO UPDATE THE BRANCH TAB BASED ON DIRECTORY IN THE ADDRESS BAR -------------
		self.branch_tab.view.controller.update_branch_tab(self.branch_tab.branch_id, self.get().rstrip().lstrip())
		
	def button_clicked(self, event, path):
		if self.raw_path == True:
			path = r"\\" + path
			
		self.branch_tab.view.controller.update_branch_tab(self.branch_tab.branch_id, path)
		
	def on_focusin(self, event):
		for btn in self.buttons:
			btn.grid_remove()
		self.delete(0, END)
		self.insert(0, self.text)

		self.select_range(0, "end")
		self.icursor("end")

	def on_focusout(self, event):
		self.update_bar(self.text)

	def on_escape(self, event):
		self.update_bar(self.text)
		self.branch_tab.focus()
	
	def truncate_breadcrumbs(self, event=None):
		available_width = self.winfo_width()								
		total_width = 0
		widths = []

		for idx, btn in enumerate(self.buttons):
			total_width += btn.winfo_reqwidth()
			widths.append(btn.winfo_reqwidth())
		
		if total_width > available_width:
			for idx, btn in enumerate(self.buttons): # remove butons until total_width is less than available_width
				btn.grid_forget()
				total_width -= widths[idx]

				if total_width < available_width:
					break