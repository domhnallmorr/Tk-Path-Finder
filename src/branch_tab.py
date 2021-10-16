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
		
		self.treeview.selection_set(iid)
		popup_menu = tk.Menu(event.widget, tearoff=0)
		if iid:
			popup_menu.add_command(label="Open in Text Editor", command=self.open_in_text_editor)
			popup_menu.add_separator()
		
		new_menu = tk.Menu(popup_menu, tearoff = 0)
		popup_menu.add_cascade(label = 'New',menu=new_menu)
		new_menu.add_command(label="New Folder(s)", command=self.new_folders, image=self.mainapp.folder_icon2, compound='left',)
		
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

	def new_folders(self):
		self.w=AddFoldersWindow(self.mainapp, self.master, self)
		self.master.wait_window(self.w.top)
		
		if self.w.button == 'ok':
			self.explorer.new_folders(self.w.folders)
			self.update_tab(self.explorer.current_directory)
		
class AddFoldersWindow(ttk.Frame):
	def __init__(self, mainapp, master, branch_tab):
		super(AddFoldersWindow, self).__init__()
		top=self.top=Toplevel(master)
		top.grab_set()
		self.mainapp = mainapp
		self.branch_tab = branch_tab
		
		self.top.title(f"New Folder(s)")
		self.button = 'cancel'

		self.folder_text = tk.Text(self.top, width=110, height=10)
		self.folder_text.grid(row=1, column=0, columnspan = 8, sticky='NE',padx=5, pady=5, ipadx=2, ipady=5)
		
		# Buttons
		self.ok_btn = ttk.Button(self.top, text='OK', width=10, style='success.TButton', command=lambda button='ok': self.cleanup(button))
		self.ok_btn.grid(row=2, column=0, padx=5, pady=5, sticky='ne')
		self.cancel_btn = ttk.Button(self.top, text='Cancel', width=10, style='danger.TButton', command=lambda button='cancel': self.cleanup(button))
		self.cancel_btn.grid(row=2, column=1, padx=5, pady=5, sticky='nw')
		
	def cleanup(self, button):
		if button == 'ok':
			self.folders = list(filter(None, [n.strip() for n in self.folder_text.get("1.0","end").split('\n')])) #avoid empty lines

			msg = None
			# Check for duplicates
			if len(self.folders) != len(set(self.folders)):
				msg = 'There are duplicate folder names present!'
			
			# Check if any of the folders already exist
			if not msg:
				for folder in self.folders:
					if os.path.isdir(os.path.join(self.branch_tab.explorer.current_directory, folder)):
						msg = f'Folder "{folder}" already exists!'
				
			# Check if there are any special characters
			if not msg:
				for folder in self.folders:
					for character in self.branch_tab.explorer.special_characters:
						if character in folder:
							msg = f'Character {character} is not allowed in a folder name!'
							break
							
			if not msg:
				self.button = 'ok'
				self.top.destroy()
			else:
				messagebox.showerror('Error', message=msg)
		else:
			self.top.destroy()