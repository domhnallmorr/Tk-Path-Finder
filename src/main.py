import copy
import importlib
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox
import os
import time

from ttkbootstrap import Style
from ttkbootstrap.themes import standard

import about_screen
import autoscrollbar
import config_file_manager
from Custom_Widgets import sidebar_tree
import root_tab
import settings_screen
import tkexplorer_icons
from Tools import diary_frontend
from Tools import notes_frontend
from Tools import pdf_tools_frontend
import todo_list
import undo_redo

class MainApplication(ttk.Frame):
	def __init__(self, parent, *args, **kwargs):
		ttk.Frame.__init__(self, parent, *args, **kwargs)
		self.root = root
		self.parent = parent
		self.root_tabs = {}
		self.id = 0
		tkexplorer_icons.setup_icons(self)
		self.setup_variables()
		
		# Styles
		self.style = Style("darkly")
		self.style_name = "darkly"

		self.setup_menu()
		
		self.setup_main_frames()
		self.setup_notebook()
		self.setup_quick_access()
		self.setup_tabs()
		#config_file_manager.write_config_file(self)
		self.load_plugins()

	def setup_variables(self):
		self.version = "0.32.11"
		self.parent.title(f"Tk Path Finder V{self.version}")
		self.config_data = config_file_manager.load_config_file(self)
		self.plugin_folder = ".\Plugins"
		self.main_module = "__init__"
		self.diary_open = False
		
		if 'text_editor' in self.config_data.keys():
			self.text_editor = self.config_data['text_editor']
		else:
			self.text_editor = None
			
		self.known_file_types = {
			'.csv': ['CSV File', self.excel_icon2],
			'.das': ['Das file', self.deepriser_icon2],
			'.doc': ['Word 97-2003 Document', self.word_icon2],
			'.docx': ['Word Document', self.word_icon2],
			'.exe': ['application', self.new_icon2],
			'.ipynb': ['Jupyter Notebook', self.notebook_icon2],
			'.jpeg': ['JPEG Image', self.image_icon2],
			'.jpg': ['JPG Image', self.image_icon2],
			'.json': ['JSON file', self.new_icon2],
			'.keyx': ['key file', self.key_file_icon2],
			'.mkv': ['MKV Video', self.video_icon2],
			'.mp3': ['MP4 Audio', self.audio_icon2],
			'.mp4': ['MP4 Video', self.video_icon2],
			'.mplt': ['mplt file', self.video_icon2],
			'.msg': ['Email', self.msg_icon2],
			'.out': ['Output file', self.new_icon2],
			'.pdf': ['PDF', self.pdf_icon2],
			'.png': ['PNG Image', self.image_icon2],
			'.pptx': ['Powerpoint Presentation', self.pptx_icon2],
			'.py': ['Python File', self.python_icon2],
			'.rar': ['RAR File', self.rar_icon2],
			'.torrent': ['Torrent File', self.new_icon2],
			'.txt': ['Text File', self.text_icon2],
			'.xlsm': ['Marco Enabled Excel Worksheet', self.excel_icon2],
			'.xlsx': ['Excel Worksheet', self.excel_icon2],
			'.zip': ['ZIP File', self.zip_icon2],
		}
		
		self.file_to_cut = None
		self.file_to_copy = None
		self.file_compare_left = None
		self.file_compare_right = None
		
		self.undo_redo_states = undo_redo.UndoRedo(self)
		
		if "open_with_apps" in self.config_data.keys():
			self.open_with_apps = self.config_data["open_with_apps"]
		else:
			self.open_with_apps = {}
			
		# --------------- DISPLAY SETTINGS ---------------
		self.default_padx = 5
		self.default_pady = 10
		
		if "default_file_width" in self.config_data.keys():
			self.default_file_width = int(self.config_data["default_file_width"])
		else:
			self.default_file_width = 400

		if "default_date_width" in self.config_data.keys():
			self.default_date_width = int(self.config_data["default_date_width"])
		else:
			self.default_date_width = 200

		if "default_type_width" in self.config_data.keys():
			self.default_type_width = int(self.config_data["default_type_width"])
		else:
			self.default_type_width = 300

		if "default_size_width" in self.config_data.keys():
			self.default_size_width = int(self.config_data["default_size_width"])
		else:
			self.default_size_width = 100
			
		# --------------- TODO LIST ---------------
		if "to_do_list" in self.config_data.keys():
			self.to_do_list = self.config_data["to_do_list"]
		else:
			self.to_do_list = []
			
		# --------------- NOTES CATEGORIES ---------------
		if "notes_categories" in self.config_data.keys():
			self.notes_categories = self.config_data["notes_categories"]
		else:
			self.notes_categories = {"General": ["Default"],}# "Projects": ["Default"]}	

		# --------------- LAST SESSION ---------------
		if "last_session" in self.config_data.keys():
			self.last_session = self.config_data["last_session"]
		else:
			self.last_session = None
		
		# --------------- GET THEMES ---------------
		self.themes = {"light": [], "dark":[]}

		for theme in standard.STANDARD_THEMES.keys():
			theme_type = standard.STANDARD_THEMES[theme]["type"].lower()
			self.themes[theme_type].append(theme)
	
	def setup_menu(self):
		menu = tk.Menu(self.master)
		self.master.config(menu=menu)

		# ________ FILE ________
		file_menu = tk.Menu(menu, tearoff=0)
		menu.add_cascade(label="File", menu=file_menu)
		file_menu.add_command(label="Load Last Session", command=self.load_last_session)

		# ________ SETTINGS ________
		settings_menu = tk.Menu(menu, tearoff=0)
		menu.add_cascade(label="Settings", menu=settings_menu)
		settings_menu.add_command(label="Edit Settings", command=self.edit_settings)

		style_menu = tk.Menu(menu, tearoff=0)
		settings_menu.add_cascade(label="Style", menu=style_menu)
		
		light_style_menu = tk.Menu(menu, tearoff=0)
		dark_style_menu = tk.Menu(menu, tearoff=0)
		style_menu.add_cascade(label="Light", menu=light_style_menu)
		style_menu.add_cascade(label="Dark", menu=dark_style_menu)
		
		for s in self.themes["light"]:
			light_style_menu.add_command(label=s, command = lambda style=s: self.switch_style(style))

		for s in self.themes["dark"]:
			dark_style_menu.add_command(label=s, command = lambda style=s: self.switch_style(style))

		# ________ TOOLS ________
		tools_menu = tk.Menu(menu, tearoff=0)
		menu.add_cascade(label="Tools", menu=tools_menu)
		
		notes_menu = tk.Menu(menu, tearoff=0)
		tools_menu.add_command(label="Diary", command=lambda self=self: diary_frontend.launch_diary(self))
		
		tools_menu.add_cascade(label="Notes", menu=notes_menu)
		notes_menu.add_command(label="Manage Notes Categories", command=lambda self=self: notes_frontend.launch_notes_categories(self))
		notes_menu.add_command(label="Edit Notes", command=lambda self=self: notes_frontend.launch_notes_page(self))
		
		pdf_menu = tk.Menu(menu, tearoff=0)
		tools_menu.add_cascade(label="PDF Tools", menu=pdf_menu)
		pdf_menu.add_command(label="Extract Pages", command=lambda self=self: pdf_tools_frontend.launch_pdf_extractor(self))
		pdf_menu.add_command(label="Merge PDFs", command=lambda self=self: pdf_tools_frontend.launch_pdf_merger(self))
		
		tools_menu.add_command(label = "To Do List", command=lambda self=self: todo_list.launch_to_do_list(self))
		
		# ________ ABOUT ________
		about_menu = tk.Menu(menu, tearoff=0)
		menu.add_cascade(label="About" ,menu=about_menu)
		about_menu.add_command(label="About Tk Path Finder", command = lambda self=self: about_screen.about(self))
		
	def setup_notebook(self):
		self.notebook = ttk.Notebook(self.container)
		self.notebook.pack(expand=True, fill=BOTH, side=LEFT)
		self.notebook.bind('<Button-3>', root_tab.right_click)
		self.notebook.mainapp = self

	def setup_quick_access(self):
		self.quick_access_tree = sidebar_tree.QuickAccessTreeview(self)
		self.quick_access_tree.grid(row=2, column=0, columnspan=8, sticky='NSEW')
		
		vsb = autoscrollbar.AutoScrollbar(self.sidebar_frame, orient="vertical", command=self.quick_access_tree.yview)
		vsb.grid(row=2, column=8, sticky='NSEW')
		self.quick_access_tree.configure(yscrollcommand=vsb.set)

	def setup_tabs(self):
		if self.root_tabs == {}:
			tab = self.create_root_tab()
			self.root_tabs = {0: tab}
		
	def create_root_tab(self):
		tab = root_tab.RootTab(self, self.id, self.id, 40)
		self.notebook.add(tab, image=self.root_icon2, compound=tk.LEFT, text=f'{str(self.id).ljust(20)}')

		self.id += 1
		
		self.gen_session_data()
		return tab

	def delete_root_tab(self, tab):
		if len(self.notebook.tabs()) > 1:
			self.notebook.forget(tab)
			self.gen_session_data()

	def delete_branch_tab(self, tab):
		if len(tab.root_tab.notebook.tabs()) > 1:
			tab.root_tab.branch_tab_deleted(tab)
			tab.root_tab.notebook.forget(tab)
			
	def setup_main_frames(self):
		#self.top_frame = Frame(self.parent) # for toolbar and address bar
		#self.top_frame.grid(row=0,column=0, sticky="n")

		self.rootpane = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
		self.rootpane.pack(expand=True, fill=BOTH, side=LEFT)
		#self.rootpane.grid(row=1,column=0, columnspan=4,sticky="nsew")		

		self.sidebar_frame = ttk.Frame()
		self.sidebar_frame.grid_rowconfigure(2, weight=1)
		self.sidebar_frame.grid_columnconfigure(7, weight=1)
		self.rootpane.add(self.sidebar_frame, weight=1)

		self.container = tk.Frame(self.rootpane, bg='pink')
		self.container.pack(expand=True, fill=BOTH, side=LEFT)
		#self.container.grid_columnconfigure(0, weight=1)
		
		self.rootpane.add(self.container)#stretch="always")	
		
		ttk.Label(self.sidebar_frame, text='Quick Access').grid(row=0, column=0, columnspan=8, sticky='NSEW')
		#ttk.Button(self.container, text='Add Root', command=self.create_root_tab).pack()
		
	def copy(self, event):
		current_root_tab = self.notebook.nametowidget(self.notebook.select())
		current_branch_tab = current_root_tab.notebook.nametowidget(current_root_tab.notebook.select())
		if current_branch_tab.treeview.selection() != ():
			item = current_branch_tab.treeview.selection()[0]
			current_branch_tab.copy_file(current_branch_tab.treeview.item(item,"text"))
	
	def paste(self, event):
		if self.file_to_copy != None and 'addressbar' not in str(self.focus_get()).split('.')[-1]:
			current_root_tab, current_branch_tab = self.get_current_tabs()
			current_branch_tab.paste_file()

	def get_current_tabs(self):
		current_root_tab = self.notebook.nametowidget(self.notebook.select())
		current_branch_tab = current_root_tab.notebook.nametowidget(current_root_tab.notebook.select())
		
		return current_root_tab, current_branch_tab
		
	def switch_style(self, style):
		self.style_name = style
		
		try:
			self.style = Style(style)
		except Exception as e:
			if "bad window path name" in str(e):
				pass # ignore error when trying to acceess a top level window that's been destroyed
			else:
				messagebox.showerror("Error", message=f"The following message occured {str(e)}")
				
		self.quick_access_tree.update_btn_bg()
		
		# Update hover color in treeviews
		for tab in self.notebook.children.keys():
			if "tab" in tab.lower():
				self.notebook.children[tab].update_tags()

		self.quick_access_tree.update_tags()
	
	def gen_session_data(self):
		self.session = []
		for tab in self.notebook.children.keys():
			if "tab" in str(type(self.notebook.children[tab])).lower():
				if self.notebook.children[tab].tab_type == "root":
					root_tab_name = self.notebook.children[tab].text
					self.session.append({root_tab_name: []})
					
					for branch in self.notebook.children[tab].branch_tabs:
						txt = self.notebook.children[tab].branch_tabs[branch].text
						directory = self.notebook.children[tab].branch_tabs[branch].explorer.current_directory
						
						self.session[-1][root_tab_name].append({txt: directory})
						
		config_file_manager.write_config_file(self)
		
	def edit_settings(self):
		self.w=settings_screen.SettingsWindow(self, self.master)
		self.master.wait_window(self.w.top)	
		
		if self.w.button == 'ok':
			self.open_with_apps = copy.deepcopy(self.w.open_with_apps)
			self.text_editor = self.w.text_editor
			self.default_file_width = self.w.default_file_width
			self.default_date_width = self.w.default_date_width
			self.default_type_width = self.w.default_type_width
			self.default_size_width = self.w.default_size_width
			config_file_manager.write_config_file(self)

	def load_last_session(self):
		
		if self.last_session is not None:
			for root in self.last_session:
				root_name = list(root.keys())[0]
				
				tab = self.create_root_tab()
				tab.enact_rename(root_name)
				
				for branch in root[root_name]:
					branch_tab = tab.create_branch_tab()
					tab.enact_branch_tab_rename(branch_tab, True, list(branch.keys())[0])
					branch_tab.update_tab(branch[list(branch.keys())[0]])
					
				# delete the default first tab
				first_tab = branch_tab.root_tab.notebook.tabs()[0]
				branch_tab.root_tab.notebook.forget(first_tab)

	def load_plugins(self):
		loader_details = (
			importlib.machinery.ExtensionFileLoader,
			importlib.machinery.EXTENSION_SUFFIXES
			)
	
		self.plugins = []
		possible_plugins = os.listdir(self.plugin_folder)
		for i in possible_plugins:
			location = os.path.join(self.plugin_folder, i)
			if not os.path.isdir(location) or not self.main_module + ".py" in os.listdir(location):
				continue
			plugin = "Plugins." + i + ".__init__"
			plugin = importlib.import_module(plugin)
			
			options = plugin.initialise_plugin()
			
			self.plugins.append({"name": i, "info": plugin, "show_in_right_click_menu": options["show_in_right_click_menu"],
				"run_on_files": options["run_on_files"], "run_on_folders": options["run_on_folders"], "extension_filter": options["extension_filter"]})
		
if __name__ == "__main__":
	root = tk.Tk()
	root.resizable(width=tk.TRUE, height=tk.TRUE)
	#MainApplication(root).pack(side="top", fill="both", expand=True)
	MA = MainApplication(root)
	#MA.pack(expand=True, fill=BOTH, side=LEFT)
	#MA.grid(row=1, columnspan=4, sticky='nsew')
	# root.bind('<Control-s>', lambda event, MA=MA: fm.save(event, MA))
	# root.bind('<Control-Shift-KeyPress-S>', lambda event, MA=MA: fm.save_as(event, MA))
	# root.bind('<Control-z>', MA.states.undo)
	# root.bind('<Control-y>', MA.states.redo)
	root.bind('<Control-c>', MA.copy)
	root.bind('<Control-v>', MA.paste)
	root.bind('<Control-z>', MA.undo_redo_states.undo)
	root.bind('<Control-y>', MA.undo_redo_states.redo)
	    
	root.state('zoomed') #mamimise window
	root.mainloop()