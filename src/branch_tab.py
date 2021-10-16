import os
import subprocess
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox


import address_bar
import autoscrollbar
import explorer_backend
import treeview_functions

class BranchTab(ttk.Frame):
	def __init__(self, root_tab, mainapp, id, text, width):
		super(BranchTab, self).__init__(mainapp.notebook) #check if this convention is right
		self.mainapp = mainapp
		self.id = id
		self.root_tab = root_tab
		self.text = text
		self.width = width
		
		# GRID
		self.tree_colspan = 16
		self.grid_columnconfigure(self.tree_colspan-1, weight=1)
		self.grid_rowconfigure(1, weight=1)
		
		self.explorer = explorer_backend.FileExplorerBackend(self.mainapp)
		self.setup_adress_bar()
		self.setup_buttons()
		self.setup_treeview()
		self.address_bar_entry.update_bar()
		self.update_treeview()
	
	def update_tab(self, directory, mode=None):
		directory_data = self.explorer.list_directory(directory, mode)
		if isinstance(directory_data, str):
			messagebox.showerror('Error', message=directory_data)
		else:
			self.address_bar_entry.update_bar()
			self.update_treeview()
			self.root_tab.notebook.tab(self, text=os.path.basename(self.explorer.current_directory))
			
			# Enable/Disable Buttons as required
			if len(self.explorer.previous_directories) > 0:
				self.back_button.config(state='enabled')
			else:
				self.back_button.config(state='disabled')

			if len(self.explorer.forward_directories) > 0:
				self.forward_button.config(state='enabled')
			else:
				self.forward_button.config(state='disabled')
				
	def setup_buttons(self):
		#Up a level
		self.back_button = ttk.Button(self, text=u'\u2190', command=self.back_one_level, state='disabled', style='primary.TButton')
		self.back_button.grid(row=0, column=0)
		self.forward_button = ttk.Button(self, text=u'\u2192', command=self.forward_one_level, state='disabled', style='primary.TButton')
		self.forward_button.grid(row=0, column=1)
		ttk.Button(self, text=u'\u2191', command=self.up_one_level, style='primary.TButton').grid(row=0, column=2)
		
	def setup_adress_bar(self):
		self.address_bar_entry = address_bar.AddressBarEntry(self.mainapp, self)
		#self.address_bar_entry.pack(expand=True, fill=X)
		self.address_bar_entry.grid(row=0, column=3, columnspan=self.tree_colspan-1, padx=6, sticky='NSEW', pady=self.mainapp.default_pady)
		
	def setup_treeview(self):
		column_names = ['Filename', 'Date Modified', 'Type', 'Size']
		column_widths = [400, 200, 300, 100]
		height = 20

		self.treeview = treeview_functions.create_treeview(self, column_names, column_widths, height)
		#self.treeview.pack(expand=True, fill=BOTH)
		self.treeview.grid(row=1, column=0, columnspan=16, sticky='NSEW', pady=self.mainapp.default_pady)
		self.treeview.bind("<Double-1>", self.OnDoubleClick)
		self.treeview.bind("<Button-3>", self.OnRightClick)
		
		#vsb = ttk.Scrollbar(self, orient="vertical", command=self.treeview.yview)
		vsb = autoscrollbar.AutoScrollbar(self, orient="vertical", command=self.treeview.yview)
		vsb.grid(row=1, column=16, sticky='NSEW')
		self.treeview.configure(yscrollcommand=vsb.set)


	def update_treeview(self):
		directory_data = self.explorer.list_directory()
		treeview_functions.write_data_to_treeview(self.mainapp, self.treeview, 'replace', directory_data)
		
	def OnDoubleClick(self, event):
		current_selection = treeview_functions.get_current_selection(self.treeview)
		if current_selection[1][2] == 'Folder':
			directory = os.path.join(self.explorer.current_directory, current_selection[1][0])
			#self.explorer.double_clicked_on_directory(directory)
			self.update_tab(directory)
		else:
			self.explorer.double_clicked_on_file(current_selection[1][0])
			
			
	def OnRightClick(self, event):
		iid = self.treeview.identify_row(event.y)
		if iid:
			self.treeview.selection_set(iid)
			popup_menu = tk.Menu(event.widget, tearoff=0)
			popup_menu.add_command(label="Open in Text Editor", command=self.open_in_text_editor)
		#popup_menu.add_command(label="Delete Root Tab", command=lambda tab=clicked_tab: event.widget.mainapp.delete_root_tab(tab))

		try:
			popup_menu.tk_popup(event.x_root, event.y_root, 0)
		finally:
			popup_menu.grab_release()
			
	def up_one_level(self):
		directory = self.explorer.up_one_level()
		self.update_tab(directory)

	def back_one_level(self):
		self.update_tab(self.explorer.previous_directories[-1], mode='back')

	def forward_one_level(self):
		self.update_tab(self.explorer.forward_directories[0], mode='fwd')
		
	def open_in_text_editor(self):
		current_selection = treeview_functions.get_current_selection(self.treeview)
		if current_selection[1][2] != 'Folder':
			subprocess.call([r"C:\Program Files (x86)\Notepad++\notepad++.exe", fr"{self.explorer.current_directory}\\{current_selection[1][0]}"])

			