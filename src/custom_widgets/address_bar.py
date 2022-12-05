import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

class AddressBarEntry(ttk.Entry):
	def __init__(self, branch_tab):
		super(AddressBarEntry, self).__init__(branch_tab)
		self.branch_tab = branch_tab
		self.bind('<Return>', self.enter_event)
		
	def update_bar(self, text):
		self.delete(0, END) #deletes the current value
		self.insert(0, text) #inserts new value assigned by 2nd parameter
		
	def enter_event(self, event):
		# -------------- CALL THE CONTROLLER METHOD TO UPDATE THE BRANCH TAB BASED ON DIRECTORY IN THE ADDRESS BAR -------------
		self.branch_tab.view.controller.update_branch_tab(self.branch_tab.branch_id, self.get().rstrip().lstrip())
		# self.update_bar()