import os
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

from custom_widgets import address_bar, autoscrollbar
from ttkbootstrap.themes import standard
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.constants import *
from view import treeview_functions
from view import settings_window

class BranchTab(ttk.Frame):
	def __init__(self, view, branch_id, root_tab):
		super(BranchTab, self).__init__(root_tab.notebook)
		self.view = view
		self.branch_id = branch_id
		self.root_tab = root_tab
		
		# ----------------- GRID -----------------
		self.tree_colspan = 16
		self.grid_columnconfigure(self.tree_colspan-1, weight=1)
		self.grid_rowconfigure(1, weight=1)
		
		# ----------------- SETUP WIDGETS -----------------
		self.setup_buttons()
		self.setup_adress_bar()
		self.setup_treeview()

	def setup_buttons(self):
		tool_top_delay = 600
		#Up a level
		self.back_button = ttk.Button(self, text=u"\u2190", command=lambda branch_id=self.branch_id: self.view.controller.back_one_level(branch_id), state="disabled", style="primary.TButton")
		self.back_button.grid(row=0, column=0, padx=(self.view.default_padx, 0))
		ToolTip(self.back_button, text="Back", bootstyle=(INFO, INVERSE), delay=tool_top_delay)
		
		self.forward_button = ttk.Button(self, text=u"\u2192", command=lambda branch_id=self.branch_id: self.view.controller.fwd_one_level(branch_id), state="disabled", style="primary.TButton")
		self.forward_button.grid(row=0, column=1)
		ToolTip(self.forward_button, text="Forward", bootstyle=(INFO, INVERSE), delay=tool_top_delay)
		
		self.dropdown_button = ttk.Button(self, text="v", state="disabled", style="primary.TButton")
		self.dropdown_button.grid(row=0, column=2)
		self.dropdown_button.bind("<Button-1>", self.dropdown_menu)
		ToolTip(self.dropdown_button, text="Recent Locations", bootstyle=(INFO, INVERSE), delay=tool_top_delay)
		
		b = ttk.Button(self, text=u"\u2191", command=lambda branch_id=self.branch_id: self.view.controller.up_one_level(branch_id), style="primary.TButton")
		b.grid(row=0, column=3)
		ToolTip(b, text="Up One Level", bootstyle=(INFO, INVERSE))

		b = ttk.Button(self, command=lambda branch_id=self.branch_id: self.view.controller.search(branch_id), image=self.view.search_icon2, style="primary.Outline.TButton")
		b.grid(row=0, column=4, padx=6)
		ToolTip(b, text="Search", bootstyle=(INFO, INVERSE), delay=tool_top_delay)
		
	def setup_adress_bar(self):
		self.address_bar_entry = address_bar.AddressBarEntry(self)
		self.address_bar_entry.grid(row=0, column=5, columnspan=self.tree_colspan-1, padx=6, sticky="NSEW", pady=self.view.default_pady)
		
	def setup_treeview(self):
		column_names = ["Filename", "Date Modified", "Type", "Size"]
		column_widths = [self.view.default_file_width, self.view.default_date_width, self.view.default_type_width, self.view.default_size_width]
		height = 20

		self.treeview = treeview_functions.create_treeview(self, column_names, column_widths, height)
		self.treeview.grid(row=1, column=0, columnspan=16, sticky='NSEW', padx=0, pady=(self.view.default_pady, 0))
		self.treeview.bind("<Double-1>", self.double_click_treeview)
		self.treeview.bind("<Button-1>", self.left_click_treeview)
		self.treeview.bind("<Button-3>", self.right_click_treeview)
		self.treeview.bind("<Motion>", self.highlight_row)
		self.treeview.bind("<Leave>", self.leave_treeview)
		
		# ------------------ ADD SCROLLBAR ------------------
		vsb = autoscrollbar.AutoScrollbar(self, orient="vertical", command=self.treeview.yview)
		vsb.grid(row=1, column=16, sticky='NSEW')
		self.treeview.configure(yscrollcommand=vsb.set)
		
		# # tags
		self.update_tags()

	def update_tags(self):
		highlight_color = standard.STANDARD_THEMES[self.view.style_name]["colors"]["active"]
		self.treeview.tag_configure('highlight', background=highlight_color)

	def leave_treeview(self, event):
		self.treeview.tk.call(self.treeview, "tag", "remove", "highlight")
		
	def highlight_row(self, event):
		item = self.treeview.identify_row(event.y)
		self.treeview.tk.call(self.treeview, "tag", "remove", "highlight")
		self.treeview.tk.call(self.treeview, "tag", "add", "highlight", item)
		
	def update(self, data, mode):
		# ------------- IF USER RENAMED TAB -------------
		if mode == "rename":
			self.root_tab.notebook.tab(self, text=data["text"].ljust(20))
		else: # ------------- ELSE IF USER CHANGED DIRECTORY -------------
			# ------------- IF THE TAB TEXT IS NOT LOCKED BY USER, UPDATE IT -------------
			if data["text_locked"] is False:
				self.root_tab.notebook.tab(self, text=data["text"].ljust(20))

			self.address_bar_entry.update_bar(data["current_directory"])
			self.update_treeview(data["tabular_data"])
			
			# ------------- ENABLE/DISABLE BUTTONS -------------
			if data["no_previous_directories"] == 0:
				self.back_button.config(state="disabled")
			else:
				self.back_button.config(state="enabled")
			
			if data["no_forward_directories"] == 0:
				self.forward_button.config(state="disabled")
			else:
				self.forward_button.config(state="enabled")
				
			if data["no_forward_directories"] + data["no_previous_directories"] == 0:
				self.dropdown_button.config(state="disabled")
			else:
				self.dropdown_button.config(state="enabled")
				
		# ------------- ADD ASTERISK IN HEADER TO INDICATE IF FILTER IS IN PLACE -------------
		if data["len_filter"] != 0:
			self.treeview.heading('#2', text='Type*')
		else:
			self.treeview.heading('#2', text='Type')
		
	def update_treeview(self, tabular_data):
		treeview_functions.write_data_to_treeview(self.view, self.treeview, "replace", tabular_data)

	def left_click_treeview(self, event):
		region = self.treeview.identify("region", event.x, event.y)
		if region == "heading":
			col = self.treeview.identify_column(event.x)
			if col == "#1":
				self.view.controller.refresh_tab(self.branch_id, sort="date")
			elif col == "#2":
				self.view.controller.refresh_tab(self.branch_id, sort="file_type")
			elif col == "#3":
				self.view.controller.refresh_tab(self.branch_id, sort="size")
			else:
				self.view.controller.refresh_tab(self.branch_id)
			
		# If no item selected, deselect any existing items
		if not self.treeview.identify_row(event.y):
			for item in self.treeview.selection():
				self.treeview.selection_remove(item)

	def double_click_treeview(self, event):
		current_selection = treeview_functions.get_current_selection(self.treeview)

		if len(current_selection[1]) > 0:
			if current_selection[1][2] == "Folder":
				self.view.controller.change_directory(self.branch_id, current_selection[1][0])
			else:
				self.view.controller.double_clicked_file(self.branch_id, current_selection[1][0])
		
	def right_click_treeview(self, event):
		region = self.treeview.identify("region", event.x, event.y)
		if region == "heading":
			self.on_right_click_heading(event)
		else:
			iid = self.treeview.identify_row(event.y)

			if len(self.treeview.selection()) == 1:
				self.treeview.selection_set(iid)

			popup_menu = tk.Menu(event.widget, tearoff=0)
			# plugins = [plugin["name"] for plugin in self.mainapp.plugins if plugin["run_on_folders"]]
			# plugin_menu = tk.Menu(popup_menu, tearoff=0)
			
			if iid:
				file_name, file_extension = os.path.splitext(self.treeview.item(iid, "text"))
				file_name = self.treeview.item(iid, "text")
				item_type = self.treeview.item(iid, "values")[1]

				# ------------------ SETUP MENU IF FILE RIGHT CLICKED ------------------
				if item_type != "Folder":
					
					# ------------------ FIND ANY PLUGINS RELEVANT TO THIS FILE EXTENSION ------------------
					# file_plugins = self.check_for_plugins(file_name, True)
					# for p in file_plugins:
						# plugins.append(p)
					
					# --------------- Open With Default Text Editor
					popup_menu.add_command(label="Open in Text Editor", command=lambda branch_id=self.branch_id, file_name=file_name: self.view.controller.open_file_clicked(branch_id, file_name), image=self.view.text_editor_icon2, compound="left")

					# --------------- Open With Another App
					# Ask controller to get open_with_apps
					open_with_apps = self.view.controller.get_open_with_apps()
					
					if file_extension in open_with_apps.keys():
						open_with_menu = tk.Menu(popup_menu, tearoff=0)
						popup_menu.add_cascade(label = "Open With", menu=open_with_menu)
						for app in open_with_apps[file_extension]:
							app_name = settings_window.get_file_description(app)
							open_with_menu.add_command(label=app_name,
									command=lambda branch_id=self.branch_id, file_name=file_name, app=app: self.view.controller.open_file_clicked(branch_id, file_name, app), compound="left",)

				# --------------- File Options
				if len(self.treeview.selection()) == 1:
					if item_type != "Folder":
						mode="edit_file"
					else:
						mode="edit_folder"
						
					popup_menu.add_command(label="Rename", command=lambda mode=mode, initialvalue=file_name, branch_id=self.branch_id: self.view.controller.new_edit_file_folder(mode, initialvalue, branch_id), image=self.view.rename_icon2, compound="left")
					
					popup_menu.add_separator()
					
					popup_menu.add_command(label="Copy Full Path to Clipboard", command= lambda file_name=file_name, branch_id=self.branch_id, mode="full":self.view.controller.copy_to_clipboard(file_name, branch_id, mode))
					popup_menu.add_command(label="Copy File Name Only to Clipboard", command= lambda file_name=file_name, branch_id=self.branch_id, mode="file_name_only":self.view.controller.copy_to_clipboard(file_name, branch_id, mode))
						
					popup_menu.add_separator()
					
					# --------------- Filtering
					if item_type != "Folder":
						filter_menu = tk.Menu(popup_menu, tearoff=0)
						popup_menu.add_cascade(label = "Filter", menu=filter_menu, image=self.view.filter_icon2, compound="left")
						filter_menu.add_command(label="Hide This File Type",
									command=lambda branch_id=self.branch_id, mode="hide_this", file_extension=file_extension: self.view.controller.filter_files(branch_id, mode, file_extension), compound="left",)
						filter_menu.add_command(label="Show Just This File Type",
									command=lambda branch_id=self.branch_id, mode="show_this", file_extension=file_extension: self.view.controller.filter_files(branch_id, mode, file_extension), compound="left",)
						filter_menu.add_command(label="Remove Filter",
									command=lambda branch_id=self.branch_id, mode="remove_filter", file_extension=None: self.view.controller.filter_files(branch_id, mode, file_extension), compound="left",)
						popup_menu.add_separator()
				
			# ------------------ NEW MENU ------------------				
			new_menu = tk.Menu(popup_menu, tearoff=0)
			popup_menu.add_cascade(label="New", menu=new_menu)
			new_menu.add_command(label="Folder(s)", command=lambda branch_id=self.branch_id: self.view.controller.new_folders(branch_id), image=self.view.folder_icon2, compound="left",)
			new_menu.add_command(label="File", command=lambda mode="new_file", initialvalue="", branch_id=self.branch_id: self.view.controller.new_edit_file_folder(mode, initialvalue, branch_id), image=self.view.new_icon2, compound="left",)
			new_menu.add_command(label="Excel Worksheet", command=lambda mode="new_excel", initialvalue=".xlsx", branch_id=self.branch_id: self.view.controller.new_edit_file_folder(mode, initialvalue, branch_id), image=self.view.excel_icon2, compound="left",)
			new_menu.add_command(label="Word Document", command=lambda mode="new_word", initialvalue=".docx", branch_id=self.branch_id: self.view.controller.new_edit_file_folder(mode, initialvalue, branch_id), image=self.view.word_icon2, compound="left",)
			
			popup_menu.add_separator()
			
			# ------------------ COPY PASTE MENU ------------------
			if iid:
				selection = []
				for file_iid in self.treeview.selection():
					selection.append(self.treeview.item(file_iid, 'text'))
				
				popup_menu.add_command(label="Cut", command=lambda files=selection, branch_id=self.branch_id, mode="cut": self.view.controller.copy_cut_file_folder(files, branch_id, mode), image=self.view.cut_icon2, compound="left")
				popup_menu.add_command(label="Copy", command=lambda files=selection, branch_id=self.branch_id, mode="copy": self.view.controller.copy_cut_file_folder(files, branch_id, mode), image=self.view.copy_icon2, compound="left")
				
			if self.view.controller.file_to_copy != None or self.view.controller.file_to_cut != None:
				popup_menu.add_command(label="Paste", command=lambda branch_id=self.branch_id: self.view.controller.paste_file_folder(branch_id), image=self.view.paste_icon2, compound="left")		
				
				
			if iid:
				if item_type != "Folder":
					popup_menu.add_separator()
					popup_menu.add_command(label="Duplicate File", command=lambda files=selection, branch_id=self.branch_id: self.view.controller.duplicate_files(files, branch_id), image=self.view.duplicate_icon2, compound="left")
				popup_menu.add_separator()
			
			# ------------------ OPEN CMD/EXPLORER ------------------	
			popup_menu.add_command(label="Open in cmd", command=lambda mode="cmd", branch_id=self.branch_id: self.view.controller.open_in_cmd_explorer(mode, branch_id), image=self.view.cmd_icon2, compound="left")
			popup_menu.add_command(label="Open in explorer", command=lambda mode="explorer", branch_id=self.branch_id: self.view.controller.open_in_cmd_explorer(mode, branch_id), image=self.view.file_explorer_icon2, compound="left")
			
			try:
				popup_menu.tk_popup(event.x_root, event.y_root, 0)
			finally:
				popup_menu.grab_release()
				
	def on_right_click_heading(self, event):
		col = self.treeview.identify_column(event.x)
		if col == '#2':		
			popup_menu = tk.Menu(event.widget, tearoff=0)
			popup_menu.add_command(label="Filter by File Type", command=lambda branch_id=self.branch_id, mode="select_file_types": self.view.controller.filter_files(branch_id, mode))
			popup_menu.add_command(label="Filter by File Name", command=lambda branch_id=self.branch_id, mode="select_file_names": self.view.controller.filter_files(branch_id, mode))

			try:
				popup_menu.tk_popup(event.x_root, event.y_root, 0)
			finally:
				popup_menu.grab_release()
				
	def dropdown_menu(self, event):

			popup_menu = tk.Menu(event.widget, tearoff=0)
			
			fwd_directories, previous_directories, current_directory = self.view.controller.get_forward_and_previous_current_directories(self.branch_id)

			# fwd
			for directory in reversed(fwd_directories):
				label = u"\u2192" + "    " + directory
				popup_menu.add_command(label=label, command=lambda branch_id=self.branch_id, directory=directory:self.view.controller.update_branch_tab(branch_id, directory, mode="fwd"))			
			
			popup_menu.add_command(label=u"\u2713" + "    " + current_directory)
			
			# previous_directories_directories
			for directory in previous_directories:
				label = u"\u2190" + "    " + directory
				popup_menu.add_command(label=label, command=lambda branch_id=self.branch_id, directory=directory:self.view.controller.update_branch_tab(branch_id, directory, mode="back"))
						
			try:
				popup_menu.tk_popup(event.x_root + 100, event.y_root + 25, 0)
			finally:
				popup_menu.grab_release()