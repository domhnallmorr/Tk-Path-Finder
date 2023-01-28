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
		
		self.buttons = []
		self.bind("<FocusIn>", self.on_focusin)
		self.bind("<FocusOut>", self.on_focusout)
		
	def update_bar(self, text):
		self.delete(0, END) #deletes the current value
		self.insert(0, text) #inserts new value assigned by 2nd parameter
		
		# Add buttons to address bar
		for btn in self.buttons:
			btn.grid_forget()
			
		folders = text.split(os.sep)
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

		
	def enter_event(self, event):
		# -------------- CALL THE CONTROLLER METHOD TO UPDATE THE BRANCH TAB BASED ON DIRECTORY IN THE ADDRESS BAR -------------
		self.branch_tab.view.controller.update_branch_tab(self.branch_tab.branch_id, self.get().rstrip().lstrip())
		
	def button_clicked(self, event, path):
		self.branch_tab.view.controller.update_branch_tab(self.branch_tab.branch_id, path)
		
		
	def on_focusin(self, event):
		for btn in self.buttons:
			btn.grid_remove()
	
	def on_focusout(self, event):
		for btn in self.buttons:
			btn.grid()
	