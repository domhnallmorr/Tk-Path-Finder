import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

from custom_widgets import branch_tab

class RootTab(ttk.Frame):
	def __init__(self, view, root_id, text):
		super(RootTab, self).__init__(view.main_notebook)
		self.view = view
		self.root_id = root_id
		
		self.setup_notebook()
		
	def setup_notebook(self):
		self.notebook = ttk.Notebook(self)
		self.notebook.pack(expand=True, fill=BOTH, side=LEFT)
		self.notebook.bind('<Button-3>', self.right_click_branch)
		self.notebook.bind("<B1-Motion>", self.reorder)
		
	def add_branch_tab(self, tab, text):
		self.notebook.add(tab, image=self.view.branch_icon2, compound=tk.LEFT, text=f"{text.ljust(20)}")
		
	def right_click_branch(self, event):
		tab_object = event.widget.nametowidget(event.widget.select())
		branch_id = tab_object.branch_id
		
		popup_menu = tk.Menu(event.widget, tearoff=0)
		popup_menu.add_command(label="Add Branch Tab", command=lambda root_id=self.root_id: self.view.controller.add_branch_tab(root_id), image=self.view.plus_icon2, compound='left')
		popup_menu.add_command(label="Rename Branch Tab", command=lambda branch_id=branch_id: self.view.controller.rename_branch_tab(branch_id), image=self.view.edit_icon2, compound='left')
		popup_menu.add_command(label="Delete Branch Tab", command=lambda root_id=self.root_id, branch_id=branch_id: self.view.controller.delete_branch_tab(root_id, branch_id), image=self.view.delete_icon2, compound='left')
		popup_menu.add_command(label="Duplicate Branch Tab", command=lambda root_id=self.root_id, branch_id=branch_id: self.view.controller.duplicate_branch_tab(root_id, branch_id), image=self.view.duplicate_icon2, compound='left')

		try:
			popup_menu.tk_popup(event.x_root, event.y_root, 0)
		finally:
			popup_menu.grab_release()

	def reorder(self, event):
		try:
			index = self.notebook.index(f"@{event.x},{event.y}")
			self.notebook.insert(index, child=self.notebook.select())
		except tk.TclError:
			pass