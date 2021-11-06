import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import simpledialog

import branch_tab

def right_click(event):
	clicked_tab = event.widget.mainapp.notebook.tk.call(event.widget.mainapp.notebook._w, "identify", "tab", event.x, event.y)
	#tab_object = event.widget.nametowidget(event.widget.select(clicked_tab))
	event.widget.select(clicked_tab)
	tab_object = event.widget.nametowidget(event.widget.select())
	popup_menu = tk.Menu(event.widget, tearoff=0)
	popup_menu.add_command(label="Add Root Tab", command=event.widget.mainapp.create_root_tab)
	popup_menu.add_command(label="Delete Root Tab", command=lambda tab=clicked_tab: event.widget.mainapp.delete_root_tab(tab))
	popup_menu.add_command(label="Rename Root Tab", command=tab_object.rename_tab)

	try:
		popup_menu.tk_popup(event.x_root, event.y_root, 0)
	finally:
		popup_menu.grab_release()
			
def right_click_branch(event):
	tab_object = event.widget.nametowidget(event.widget.select())
	#clicked_tab = event.widget.mainapp.notebook.tk.call(event.widget.mainapp.notebook._w, "identify", "tab", event.x, event.y)

	popup_menu = tk.Menu(event.widget, tearoff=0)
	popup_menu.add_command(label="Add Branch Tab", command=event.widget.create_branch_tab)
	popup_menu.add_command(label="Rename Branch Tab", command=lambda tab=tab_object: event.widget.root_tab.rename_branch_tab(tab))
	popup_menu.add_command(label="Delete Branch Tab", command=lambda tab=tab_object: event.widget.mainapp.delete_branch_tab(tab))

	try:
		popup_menu.tk_popup(event.x_root, event.y_root, 0)
	finally:
		popup_menu.grab_release()


	
class RootTab(ttk.Frame):
	def __init__(self, mainapp, id, text, width):
		super(RootTab, self).__init__(mainapp.notebook) #check if this convention is right
		self.mainapp = mainapp
		self.id = id
		self.text = text
		self.width = width
		
		self.id = 0
		self.branch_tabs = {}
		
		self.setup_notebook()
		self.notebook.bind('<Button-3>', right_click_branch)
		
	def setup_notebook(self):
		self.notebook = ttk.Notebook(self)
		self.notebook.pack(expand=True, fill=BOTH, side=LEFT)
		self.notebook.mainapp = self.mainapp
		self.notebook.root_tab = self
		self.setup_tabs()
		self.notebook.create_branch_tab = self.create_branch_tab
		
	def setup_tabs(self):
		if self.branch_tabs == {}:
			tab = self.create_branch_tab()
			self.branch_tabs = {0: tab}
		
	def create_branch_tab(self):
		tab = branch_tab.BranchTab(self, self.mainapp, self.id, self.id, 40)
		self.notebook.add(tab, text="Desktop")
		tab.update_tab(tab.explorer.current_directory) #initalise the treeview data in branch tab
		self.id += 1
		
		return tab
		
	def rename_tab(self):
		new_name = simpledialog.askstring(title = "Rename Tab", prompt = "New Name:".ljust(100), initialvalue=self.text)
		if new_name != None:
			self.mainapp.notebook.tab(self, text=f'{str(new_name).ljust(20)}')
			self.text = new_name
			
	def rename_branch_tab(self, tab):
		self.w=branch_tab.RenameWindow(self.mainapp, self.master, tab)
		self.master.wait_window(self.w.top)
		
		if self.w.button == 'ok':
			tab.lock_name = self.w.lock
			tab.text = self.w.name
			self.notebook.tab(tab, text=self.w.name)
