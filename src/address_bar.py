import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

class AddressBarEntry(ttk.Entry):
	def __init__(self, mainapp, branch_tab):
		super(AddressBarEntry, self).__init__(branch_tab)
		self.branch_tab = branch_tab
		self.bind('<Return>', self.enter_event)
		
	def update_bar(self):
		self.delete(0, END) #deletes the current value
		self.insert(0, self.branch_tab.explorer.current_directory) #inserts new value assigned by 2nd parameter
		
	def enter_event(self, event):
		self.branch_tab.explorer.address_bar_updateed(self.get())
		self.branch_tab.update_tab()
		self.update_bar()