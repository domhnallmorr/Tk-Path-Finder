from distutils.dir_util import copy_tree
from multiprocessing import Process
import os
import pathlib
from shutil import copyfile, move
import subprocess
import threading
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import simpledialog

from docx import Document
from openpyxl import Workbook
import pyperclip
from ttkbootstrap.themes import standard

from Custom_Widgets import address_bar
import autoscrollbar
import explorer_backend
import file_comparison
import paste_windows
import search_window
import settings_screen
import treeview_functions

class BranchTab(ttk.Frame):
	def __init__(self, root_tab, mainapp, id, text, width):
		super(BranchTab, self).__init__(mainapp.notebook) #check if this convention is right
		self.mainapp = mainapp
		self.id = id
		self.root_tab = root_tab
		self.text = text
		self.width = width
		self.filter = []
		self.lock_name = False
		self.lock_filter = False
		
		self.tab_type = "branch"
		
		# GRID
		self.tree_colspan = 16
		self.grid_columnconfigure(self.tree_colspan-1, weight=1)
		self.grid_rowconfigure(1, weight=1)
		
		self.explorer = explorer_backend.FileExplorerBackend(self.mainapp)
		self.setup_adress_bar()
		self.setup_buttons()
		self.setup_treeview()
		self.address_bar_entry.update_bar()
	
	def update_tab(self, directory, mode=None, sort=None):
		if directory != self.explorer.current_directory:
			if not self.lock_filter:
				self.filter = [] #reset filter if we change directories

		if self.filter != []:
			self.treeview.heading('#2', text='Type*')
		else:
			self.treeview.heading('#2', text='Type')
			
		directory_data, msg = self.explorer.list_directory(directory, mode=mode, sort=sort)
		self.directory_data = directory_data
		
		if isinstance(directory_data, str):
			messagebox.showerror('Error', message=directory_data)
		elif msg is not None:
			messagebox.showerror('Error', message=msg)
		else:
			self.address_bar_entry.update_bar()
			self.update_treeview(directory_data)
			if not self.lock_name:
				self.text = os.path.basename(self.explorer.current_directory)
				self.root_tab.notebook.tab(self, text=self.text)
			
			# Enable/Disable Buttons as required
			if len(self.explorer.previous_directories) > 0:
				self.back_button.config(state='enabled')
			else:
				self.back_button.config(state='disabled')

			if len(self.explorer.forward_directories) > 0:
				self.forward_button.config(state='enabled')
			else:
				self.forward_button.config(state='disabled')
				
			self.mainapp.gen_session_data()
				
	def setup_buttons(self):
		#Up a level
		self.back_button = ttk.Button(self, text=u'\u2190', command=self.back_one_level, state='disabled', style='primary.TButton')
		self.back_button.grid(row=0, column=0)
		self.forward_button = ttk.Button(self, text=u'\u2192', command=self.forward_one_level, state='disabled', style='primary.TButton')
		self.forward_button.grid(row=0, column=1)
		ttk.Button(self, text=u'\u2191', command=self.up_one_level, style='primary.TButton').grid(row=0, column=2)
		ttk.Button(self, command=self.search, image=self.mainapp.search_icon2, style='primary.Outline.TButton').grid(row=0, column=3, padx=6)
		
	def setup_adress_bar(self):
		self.address_bar_entry = address_bar.AddressBarEntry(self.mainapp, self)
		#self.address_bar_entry.pack(expand=True, fill=X)
		self.address_bar_entry.grid(row=0, column=4, columnspan=self.tree_colspan-1, padx=6, sticky='NSEW', pady=self.mainapp.default_pady)
		
	def setup_treeview(self):
		column_names = ['Filename', 'Date Modified', 'Type', 'Size']
		column_widths = [self.mainapp.default_file_width, self.mainapp.default_date_width, self.mainapp.default_type_width, self.mainapp.default_size_width]
		height = 20

		self.treeview = treeview_functions.create_treeview(self, column_names, column_widths, height)
		#self.treeview.pack(expand=True, fill=BOTH)
		self.treeview.grid(row=1, column=0, columnspan=16, sticky='NSEW', pady=self.mainapp.default_pady)
		self.treeview.bind("<Double-1>", self.OnDoubleClick)
		self.treeview.bind("<Button-1>", self.OnLeftClick)
		self.treeview.bind("<Button-3>", self.OnRightClick)
		self.treeview.bind("<Motion>", self.highlight_row)


		
		vsb = autoscrollbar.AutoScrollbar(self, orient="vertical", command=self.treeview.yview)
		vsb.grid(row=1, column=16, sticky='NSEW')
		self.treeview.configure(yscrollcommand=vsb.set)
		
		# tags
		self.update_tags()

	def update_tags(self):
		highlight_color = standard.STANDARD_THEMES[self.mainapp.style_name]["colors"]["active"]
		self.treeview.tag_configure('highlight', background=highlight_color)
		
	def highlight_row(self, event):
		item = self.treeview.identify_row(event.y)
		self.treeview.tk.call(self.treeview, "tag", "remove", "highlight")
		self.treeview.tk.call(self.treeview, "tag", "add", "highlight", item)

	def update_treeview(self, directory_data):
		treeview_functions.write_data_to_treeview(self, self.mainapp, self.treeview, 'replace', directory_data)

	def OnLeftClick(self, event):
		region = self.treeview.identify("region", event.x, event.y)
		if region == 'heading':
			col = self.treeview.identify_column(event.x)
			if col == '#1':
				self.update_tab(self.explorer.current_directory, sort='date')
			elif col == '#2':
				self.update_tab(self.explorer.current_directory, sort='file_type')
			elif col == '#3':
				self.update_tab(self.explorer.current_directory, sort='size')
			else:
				self.update_tab(self.explorer.current_directory)
			
		
	def OnDoubleClick(self, event):
		msg = None
		current_selection = treeview_functions.get_current_selection(self.treeview)
		if len(current_selection[1]) > 0:
			if current_selection[1][2] == 'Folder':
				directory = os.path.join(self.explorer.current_directory, current_selection[1][0])
				if os.path.isdir(directory):
					self.update_tab(directory)
				else:
					try:
						self.update_tab(directory)
					except:
						pass
						msg = 'This directory does not exist, it may have been moved or deleted'

			else:
				if os.path.isfile(os.path.join(self.explorer.current_directory, current_selection[1][0])):
					msg = self.explorer.double_clicked_on_file(current_selection[1][0])
				else:
					msg = 'This file does not exist, it may have been moved or deleted'
			if msg:
				messagebox.showerror('Error', message=msg)
			
	def OnRightClick(self, event):
		region = self.treeview.identify("region", event.x, event.y)
		if region == 'heading':
			self.on_right_click_heading(event)
		else:
			iid = self.treeview.identify_row(event.y)

			if len(self.treeview.selection()) == 1:
				self.treeview.selection_set(iid)
				
			popup_menu = tk.Menu(event.widget, tearoff=0)
			plugins = [plugin["name"] for plugin in self.mainapp.plugins if plugin["run_on_folders"]]
			plugin_menu = tk.Menu(popup_menu, tearoff=0)
			
			if iid:
				#file_name = self.treeview.item(iid, 'text')
				file_name, file_extension = os.path.splitext(self.treeview.item(iid, 'text'))
				file_name = self.treeview.item(iid, 'text')
				
				if os.path.isfile(os.path.join(self.explorer.current_directory, file_name)):
					full_file_name = os.path.join(self.explorer.current_directory, file_name)
					
					file_plugins = self.check_for_plugins(file_name, True)
					for p in file_plugins:
						plugins.append(p)
					
					popup_menu.add_command(label="Open in Text Editor", command=self.open_in_text_editor)
					
					# --------------- Open With
					if file_extension in self.mainapp.open_with_apps.keys():
						open_with_menu = tk.Menu(popup_menu, tearoff=0)
						popup_menu.add_cascade(label = 'Open With',menu=open_with_menu)
						for app in self.mainapp.open_with_apps[file_extension]:
							app_name = settings_screen.get_file_description(app)
							open_with_menu.add_command(label=app_name,
									command=lambda app=app: self.open_in_text_editor(app), compound='left',)
					
					# --------------- File Options
					if len(self.treeview.selection()) == 1:
						popup_menu.add_command(label="Rename", command=lambda mode='edit', initialvalue=file_name: self.new_file(mode, initialvalue))
						popup_menu.add_command(label="Left Compare", command=self.left_compare)
						if self.mainapp.file_compare_left:
							popup_menu.add_command(label="Right Compare", command=self.right_compare)
						popup_menu.add_command(label="Copy Path to Clipboard", command=self.copy_to_clipboard)
						popup_menu.add_separator()
					
						# --------------- Filtering
						filter_menu = tk.Menu(popup_menu, tearoff=0)
						popup_menu.add_cascade(label = 'Filter',menu=filter_menu)
						filter_menu.add_command(label="Hide This File Type",
									command=lambda mode='all but', item=iid: self.filter_right_click(mode, item), compound='left',)
						filter_menu.add_command(label="Show Just This File Type",
									command=lambda mode='just this', item=iid: self.filter_right_click(mode, item), compound='left',)
						filter_menu.add_command(label="Remove Filter",
									command=lambda mode='remove', item=iid: self.filter_right_click(mode, item), compound='left',)
					
					# --------------- PLUGINS
					if len(plugins) > 0:
						popup_menu.add_cascade(label = 'Plugins',menu=plugin_menu)
						for plugin in self.mainapp.plugins:
							if plugin['name'] in plugins:
								plugin_menu.add_command(label=plugin['name'], command=lambda plugin=plugin['name'], file=full_file_name: self.run_plugin(plugin, file))
								
					popup_menu.add_separator()
			
			else: # if file not selected, add plugin menu if any run_on_folders plugins are present
				if len(plugins) > 0:
					popup_menu.add_cascade(label = 'Plugins',menu=plugin_menu)
					for plugin in self.mainapp.plugins:
						if plugin['name'] in plugins:
							plugin_menu.add_command(label=plugin['name'], command=lambda plugin=plugin['name'], path=self.explorer.current_directory: self.run_plugin(plugin, path))
				popup_menu.add_separator()
				
			new_menu = tk.Menu(popup_menu, tearoff=0)
			popup_menu.add_cascade(label = 'New',menu=new_menu)
			new_menu.add_command(label="New Folder(s)", command=self.new_folders, image=self.mainapp.folder_icon2, compound='left',)
			new_menu.add_command(label="File", command=lambda mode='new': self.new_file(mode), image=self.mainapp.new_icon2, compound='left',)
			new_menu.add_command(label="Excel Worksheet", command=lambda mode='new excel': self.new_file(mode), image=self.mainapp.excel_icon2, compound='left',)
			new_menu.add_command(label="Word Document", command=lambda mode='new word': self.new_file(mode), image=self.mainapp.word_icon2, compound='left',)

			popup_menu.add_separator()
			# --------------- COPY/PASTE
			if iid:
				popup_menu.add_command(label="Cut", command=lambda file=file_name: self.cut_file(file))
				popup_menu.add_command(label="Copy", command=lambda file=file_name: self.copy_file(file))
			if self.mainapp.file_to_copy != None or self.mainapp.file_to_cut != None:
				popup_menu.add_command(label="Paste", command=self.paste_file)		
				popup_menu.add_separator()
			popup_menu.add_command(label="Open in cmd", command=self.explorer.open_in_cmd)
			popup_menu.add_command(label="Open in explorer", command=self.explorer.open_in_explorer)
			
			try:
				popup_menu.tk_popup(event.x_root, event.y_root, 0)
			finally:
				popup_menu.grab_release()

	def check_for_plugins(self, name, is_file):
		plugins = []
		file_name, file_extension = os.path.splitext(name)
		
		for plugin in self.mainapp.plugins:
			if plugin['show_in_right_click_menu']:
			
			# FILE PLUGINS
				if is_file and plugin['run_on_files']:
					if len(plugin['extension_filter']) == 0 or file_extension in plugin['extension_filter']:
						plugins.append(plugin["name"])
		return plugins
		
	def on_right_click_heading(self, event):
		col = self.treeview.identify_column(event.x)
		if col == '#2':		
			popup_menu = tk.Menu(event.widget, tearoff=0)
			popup_menu.add_command(label="Filter File Type", command=self.filter_files)

			try:
				popup_menu.tk_popup(event.x_root, event.y_root, 0)
			finally:
				popup_menu.grab_release()
				
	def filter_files(self):
		self.w = FilterWindow(self.mainapp, self.master, self)
		self.master.wait_window(self.w.top)	
		
		if self.w.button == 'ok':
			self.filter = self.w.filter
			self.update_tab(self.explorer.current_directory)
			self.lock_filter = self.w.lock_filter

	def filter_right_click(self, mode, item):
		filter = []
		item_filename, item_file_extension = os.path.splitext(self.treeview.item(item, 'text'))
		if mode == 'just this':
			for row in self.directory_data:
				if row[2] != 'Folder':
					filename, file_extension = os.path.splitext(row[0])
					if file_extension != item_file_extension:
						filter.append(file_extension)
		elif mode == 'all but':
			filter.append(item_file_extension)
		self.filter = filter
		self.update_tab(self.explorer.current_directory)
		
	def up_one_level(self):
		directory = self.explorer.up_one_level()
		self.update_tab(directory)

	def back_one_level(self):
		self.update_tab(self.explorer.previous_directories[-1], mode='back')

	def forward_one_level(self):
		self.update_tab(self.explorer.forward_directories[0], mode='fwd')
		
	def open_in_text_editor(self, app=None):
		if self.mainapp.text_editor:
			current_selection = treeview_functions.get_current_selection(self.treeview)
			if app:
				#subprocess.call([app, fr"{self.explorer.current_directory}\\{current_selection[1][0]}"])
				threading.Thread(target=lambda app=app, file=fr"{self.explorer.current_directory}\\{current_selection[1][0]}":self.open_with_app(app, file)).start()
			else:
				if current_selection[1][2] != 'Folder':
					subprocess.call([fr"{self.mainapp.text_editor}", fr"{self.explorer.current_directory}\\{current_selection[1][0]}"])
		else:
			messagebox.showerror('Error', message='Default Text Editor has not been Defined')
			
	def open_with_app(self, app, file):
		subprocess.call([app, file])
	
	def new_folders(self):
		self.w=AddFoldersWindow(self.mainapp, self.master, self)
		self.master.wait_window(self.w.top)
		
		if self.w.button == 'ok':
			self.explorer.new_folders(self.w.folders)
			self.update_tab(self.explorer.current_directory)

			# Add to Undo Stack
			#if mode == 'edit':
				#data = {'action': 'rename_file', 'orig_name': os.path.join(self.explorer.current_directory, self.orig_file_name), 'new_name': os.path.join(self.explorer.current_directory, new_name), 'branch_tab': self, 'root_tab':self.root_tab}
			#else:
			data = {'action': 'new_folders', 'base_folder': self.explorer.current_directory, 'branch_tab': self, 'root_tab': self.root_tab, 'folder_names': self.w.folders}
			self.mainapp.undo_redo_states.add_action_to_undo_stack(data)

			self.mainapp.undo_redo_states.reset_redo()		
			
	def new_file(self, mode, initialvalue=''):
		if mode == 'edit':
			self.orig_file_name = initialvalue
		elif mode == 'new excel':
			initialvalue = '.xlsx'
		elif mode == 'new word':
			initialvalue = '.docx'
			
		new_name = simpledialog.askstring(title="New File", prompt = "File Name:".ljust(100), initialvalue=initialvalue)
		
		if new_name:
			msg = None
			
			#check file does not exist
			if mode == 'new' or mode == 'new excel':
				if os.path.isfile(os.path.join(self.explorer.current_directory, new_name)):
					msg = 'That File Already Exists!'
					
			# Check if user input is just a bunch of spaces
			if new_name.strip() == '':
				msg = 'Enter a File Name'
				
			# Check for special characters
			msg = self.explorer.check_special_characters(new_name)
			
			if msg:
				messagebox.showerror('Error', message=msg)
				self.new_file(mode, initialvalue=new_name)
			else:
				if mode == 'new':
					with open(os.path.join(self.explorer.current_directory, new_name), 'w') as f:
						f.write('')
						
				# New Excel File
				elif mode == 'new excel':
					wb = Workbook()
					wb.save(os.path.join(self.explorer.current_directory, new_name))

				# New Excel File
				elif mode == 'new word':
					document = Document()
					document.save(os.path.join(self.explorer.current_directory, new_name))
					
				else:
					try:
						os.rename(os.path.join(self.explorer.current_directory, self.orig_file_name), os.path.join(self.explorer.current_directory, new_name))
					except Exception as e:
						if "being used by another" in str(e).lower():
							msg = "Permission Denied, Ensure Document is not Open in Another Process"
							
						else:
							msg = f"The Following Error Occured\n{str(e)}"
							
						messagebox.showerror('Error', message=msg)
						
						
				self.update_tab(self.explorer.current_directory)

			# Add to Undo Stack
			if mode == 'edit':
				data = {'action': 'rename_file', 'orig_name': os.path.join(self.explorer.current_directory, self.orig_file_name), 'new_name': os.path.join(self.explorer.current_directory, new_name), 'branch_tab': self, 'root_tab':self.root_tab}
			else:
				data = {'action': 'new_file', 'file_name': os.path.join(self.explorer.current_directory, new_name), 'branch_tab': self, 'root_tab':self.root_tab}
			self.mainapp.undo_redo_states.add_action_to_undo_stack(data)

			self.mainapp.undo_redo_states.reset_redo()
			
	def cut_file(self, file):
		self.mainapp.file_to_cut = []
		for iid in self.treeview.selection():
				self.mainapp.file_to_cut.append({'Name': self.treeview.item(iid, 'text'), 'Path': self.explorer.current_directory})
		self.mainapp.file_to_copy = None
		
	def copy_file(self, file):
		self.mainapp.file_to_copy = []
		for iid in self.treeview.selection():
			self.mainapp.file_to_copy.append({'Name': self.treeview.item(iid, 'text'), 'Path': self.explorer.current_directory})
		self.mainapp.file_to_cut = None
		
	def paste_file(self):
		action_if_duplicate = 'ask'
		if self.mainapp.file_to_copy == None:
			files_to_process = self.mainapp.file_to_cut
			task = 'cut'
		else:
			files_to_process = self.mainapp.file_to_copy
			task = 'copy'
		
		for file in files_to_process:
			source = os.path.join(file['Path'], file['Name'])
			destination = os.path.join(self.explorer.current_directory, file['Name'])
			
			try:
				# Copy File
				if os.path.isfile(os.path.join(file['Path'], file['Name'])):
					# handle for file already existing in destination
					if os.path.isfile(os.path.join(self.explorer.current_directory, file['Name'])):

						counter = 1
						while True: # Check if File Exists
							filename, file_extension = os.path.splitext(file['Name'])
							if not os.path.isfile(os.path.join(self.explorer.current_directory, f"{filename}({counter}){file_extension}")):
								destination = os.path.join(self.explorer.current_directory, f"{filename}({counter}){file_extension}")
								break
							counter += 1
					if task == 'copy':
						copyfile(os.path.join(file['Path'], file['Name']), destination)
					elif task == 'cut':
						# check if we are moving file to another drive
						drive_source = pathlib.Path(source).drive
						drive_destination = pathlib.Path(destination).drive
						
						if drive_source != drive_destination:
							move(source, destination)
						else: # not moving drives so os.rename is sufficient
							os.rename(os.path.join(file['Path'], file['Name']), destination)
				
				# Copy Directory
				elif os.path.isdir(os.path.join(file['Path'], file['Name'])):
					# handle for folder already existing in destination
					if os.path.isdir(os.path.join(self.explorer.current_directory, file['Name'])):
						counter = 1
						while True: # Check if File Exists
							if not os.path.isdir(os.path.join(self.explorer.current_directory, f"{file['Name']}({counter})")):
								destination = os.path.join(self.explorer.current_directory, f"{file['Name']}({counter})")
								break
							counter += 1	
					if task == 'copy':
						#copy_tree(os.path.join(file['Path'], file['Name']), destination)
						paste_windows.paste_folder(self.mainapp, self, os.path.join(file['Path'], file['Name']), destination)
					elif task == 'cut':
						move(os.path.join(file['Path'], file['Name']), destination)
			except PermissionError:
				messagebox.showerror('Error', message=f'Permission Denied to Paste {file["Name"]}')
			except Exception as e:
				messagebox.showerror('Error', message=f'An error occured pasting {file["Name"]}')
				print(e)
				
		self.update_tab(self.explorer.current_directory)
	
	def search(self):
		self.w = search_window.SearchWindow(self.mainapp, self.master, self)
		self.master.wait_window(self.w.top)		

	def left_compare(self):
		current_selection = treeview_functions.get_current_selection(self.treeview)
		self.mainapp.file_compare_left = os.path.join(self.explorer.current_directory, current_selection[1][0])
		
	def right_compare(self):
		current_selection = treeview_functions.get_current_selection(self.treeview)
		self.mainapp.file_compare_right = os.path.join(self.explorer.current_directory, current_selection[1][0])	
		
		threading.Thread(target=self.compare_files).start()
		
	def compare_files(self):
		self.w=file_comparison.ComparisonWindow(self.mainapp, self.master, self)
		self.master.wait_window(self.w.top)	

	def copy_to_clipboard(self):
		current_selection = treeview_functions.get_current_selection(self.treeview)
		pyperclip.copy(os.path.join(self.explorer.current_directory, current_selection[1][0]))

	def run_plugin(self, plugin, file):
		for p in self.mainapp.plugins:
			if p['name'] == plugin:
				p['info'].Plugin(self.mainapp, self.master, p['name'], file)
				
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
		self.folder_text.bind('<Control-d>', self.duplicate_line)
		
	def duplicate_line(self, event):
		current_line = int(self.folder_text.index(INSERT).split('.')[0])-1 #convert to 0 index system
		all_lines = self.folder_text.get("1.0",END).split('\n')
		
		all_lines.insert(current_line+1, all_lines[current_line])
		#all_lines = '\n'.join(all_lines)
		lines_to_insert = []
		
		for l in all_lines:
			if not l.replace('\n', '').strip() == '': #remove any blank lines
				lines_to_insert.append(l) 

		self.folder_text.delete('1.0', END)
		self.folder_text.insert("end", '\n'.join(lines_to_insert))
		#self.folder_text.mark_set("insert", "%d.%d" % (current_line+1, 1))
		
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
							msg = f'Character {character} is not allowed!'
							break
							
			if not msg:
				self.button = 'ok'
				self.top.destroy()
			else:
				messagebox.showerror('Error', message=msg)
		else:
			self.top.destroy()
			
class RenameWindow(ttk.Frame):
	def __init__(self, mainapp, master, branch_tab, tab_type="branch"):
		super(RenameWindow, self).__init__()
		top=self.top=Toplevel(master)
		top.grab_set()
		
		self.top.title("Rename Tab")
		
		self.mainapp = mainapp
		self.branch_tab = branch_tab
		self.tab_type = tab_type
		self.button = "cancel"

		#self.setup_title_bar()		
		self.name_entry = ttk.Entry(self.top, width=60)
		self.name_entry.grid(row=1, column=0, columnspan=5, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady, sticky="ew")
		self.name_entry.insert(0, branch_tab.text)
		self.top.grid_columnconfigure(0, weight=1)
		
		if tab_type == "branch":
			self.lock = IntVar(value=1)
			ttk.Checkbutton(self.top, text="Lock Name", variable=self.lock).grid(row=2, column=2, sticky='w', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
		# Buttons
		self.ok_btn = ttk.Button(self.top, text="OK", width=10, style="success.TButton", command=lambda button="ok": self.cleanup(button))
		self.ok_btn.grid(row=2, column=3, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady, sticky='ne')
		self.cancel_btn = ttk.Button(self.top, text='Cancel', width=10, style='danger.TButton', command=lambda button='cancel': self.cleanup(button))
		self.cancel_btn.grid(row=2, column=4, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady, sticky='nw')		
		
	def setup_title_bar(self):
		self.top.overrideredirect(True)
		title_bar = tk.Frame(self.top, bg="red")
		close_button = Button(title_bar, text="X", command=self.top.destroy)
		close_button.pack(side=RIGHT)
		title_bar.grid(row=0, column=0, columnspan=5, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
	def cleanup(self, button):
		
		if button == "ok":
			if self.name_entry.get() == '':
				messagebox.showerror("Error", message="Enter a Name")
			else:
				self.name = self.name_entry.get()
				
				if self.tab_type == "branch":
					if self.lock.get() == 1:
						self.lock = True
					else:
						self.lock = False
						
				self.button = "ok"
				self.top.destroy()
		else:
			self.top.destroy()
		
class FilterWindow(ttk.Frame):
	def __init__(self, mainapp, master, branch_tab):
		super(FilterWindow, self).__init__()
		top=self.top=Toplevel(master)
		top.grab_set()
		self.mainapp = mainapp
		self.branch_tab = branch_tab
		self.button = "cancel"
		
		self.file_types = {}
		for file in branch_tab.directory_data:
			if file[2] != "Folder":
				filename, file_extension = os.path.splitext(file[0])
				if file_extension not in self.file_types.keys():
					if file_extension in mainapp.known_file_types.keys():
						description = mainapp.known_file_types[file_extension][0]
					else:
						description = f"{file_extension} file"
					
					if file_extension in branch_tab.filter:
						initialvalue = 0
					else:
						initialvalue = 1
						
					self.file_types[file_extension] = {"description": description, "var": IntVar(value=initialvalue)}
		
		self.all_files = IntVar(value=1)
		ttk.Checkbutton(self.top, text=f"File Types in Current Directory:", variable=self.all_files, command=self.select_all_file).grid(row=0, column=0, sticky='w', padx=5, pady=5)		
		row = 1
		for file_extension in sorted(list(self.file_types.keys())):
			var = self.file_types[file_extension]["var"]
			description = self.file_types[file_extension]["description"]
			ttk.Checkbutton(self.top, text=f"{description} ({file_extension})", variable=var).grid(row=row, column=1, sticky='w', padx=5, pady=5)
			row +=  1
					
		# Buttons
		self.ok_btn = ttk.Button(self.top, text="OK", width=10, style="success.TButton", command=lambda button="ok": self.cleanup(button))
		self.ok_btn.grid(row=row, column=0, padx=5, pady=5, sticky="ne")
		self.cancel_btn = ttk.Button(self.top, text="Cancel", width=10, style="danger.TButton", command=lambda button="cancel": self.cleanup(button))
		self.cancel_btn.grid(row=row, column=1, padx=5, pady=5, sticky="nw")		

		# Lock filter
		initialvalue = 0
		if branch_tab.lock_filter:
			initialvalue = 1
		self.lock_filter = IntVar(value=initialvalue)
		ttk.Checkbutton(self.top, text=f"Lock in this filter:", variable=self.lock_filter).grid(row=row, column=2, sticky="w", padx=5, pady=5)	
		
	def select_all_file(self):
		for file_extension in self.file_types.keys():
			self.file_types[file_extension]["var"].set(self.all_files.get())
		
	def cleanup(self, button):
		if button == "ok":
			self.filter = []		
			for file_extension in self.file_types.keys():
				if self.file_types[file_extension]["var"].get() == 0:
					self.filter.append(file_extension)
			
			if self.lock_filter.get() == 1:
				self.lock_filter = True
			else:
				self.lock_filter = False
			self.button = button
				
		self.top.destroy()
			
			
					