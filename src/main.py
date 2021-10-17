import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
import os

from ttkbootstrap import Style

import about_screen
import autoscrollbar
import config_file_manager
import root_tab
import sidebar_tree
import tkexplorer_icons

class MainApplication(ttk.Frame):
	def __init__(self, parent, *args, **kwargs):
		ttk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		self.root_tabs = {}
		self.id = 0
		tkexplorer_icons.setup_icons(self)
		self.setup_variables()
		
		# Styles
		self.style = Style('darkly')
		self.default_pady = 10

		self.setup_menu()
		
		self.setup_main_frames()
		self.setup_notebook()
		self.setup_quick_access()
		self.setup_tabs()

	def setup_variables(self):
		self.version = '0.11.0'
		self.parent.title(f"Tk Path Finder V{self.version}")
		self.config_data = config_file_manager.load_config_file(self)

		self.known_file_types = {
			'.csv': ['CSV File', self.excel_icon2],
			'.doc': ['Word 97-2003 Document', self.word_icon2],
			'.docx': ['Word Document', self.word_icon2],
			'.exe': ['application', self.new_icon2],
			'.ipynb': ['Jupyter Notebook', self.notebook_icon2],
			'.jpeg': ['JPEG Image', self.image_icon2],
			'.jpg': ['JPG Image', self.image_icon2],
			'.mkv': ['MKV Video', self.video_icon2],
			'.mp3': ['MP4 Audio', self.audio_icon2],
			'.mp4': ['MP4 Video', self.video_icon2],
			'.pdf': ['PDF', self.pdf_icon2],
			'.png': ['PNG Image', self.image_icon2],
			'.py': ['Python File', self.python_icon2],
			'.rar': ['RAR File', self.rar_icon2],
			'.txt': ['Text File', self.text_icon2],
			'.xlsx': ['Excel Worksheet', self.excel_icon2],
			'.zip': ['ZIP File', self.zip_icon2],
		}
		
		self.file_to_copy = None

	def setup_menu(self):
		menu = tk.Menu(self.master)
		self.master.config(menu=menu)

		# ________ ABOUT ________
		about_menu = tk.Menu(menu, tearoff=0)
		menu.add_cascade(label='About',menu=about_menu)
		about_menu.add_command(label = 'About Tk Path Finder', command = lambda self=self: about_screen.about(self))
		
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
		self.notebook.add(tab, text=f'{str(self.id).ljust(20)}')

		self.id += 1
		
		return tab

	def delete_root_tab(self, tab):
		if len(self.notebook.tabs()) > 1:
			self.notebook.forget(tab)

	def delete_branch_tab(self, tab):
		if len(tab.root_tab.notebook.tabs()) > 1:
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
		self.rootpane.add(self.sidebar_frame)

		self.container = tk.Frame(self.rootpane, bg='pink')
		self.container.pack(expand=True, fill=BOTH, side=LEFT)
		#self.container.grid_columnconfigure(0, weight=1)
		
		self.rootpane.add(self.container,)#stretch="always")	
		
		ttk.Label(self.sidebar_frame, text='Quick Access').grid(row=0, column=0, columnspan=8, sticky='NSEW')
		#ttk.Button(self.container, text='Add Root', command=self.create_root_tab).pack()
		
	def copy(self, event):
		current_root_tab = self.notebook.nametowidget(self.notebook.select())
		current_branch_tab = current_root_tab.notebook.nametowidget(current_root_tab.notebook.select())
		if current_branch_tab.treeview.selection() != ():
			item = current_branch_tab.treeview.selection()[0]
			current_branch_tab.copy_file(current_branch_tab.treeview.item(item,"text"))
	
	def paste(self, event):
		if self.file_to_copy != None:
			current_root_tab, current_branch_tab = self.get_current_tabs()
			current_branch_tab.paste_file()

	def get_current_tabs(self):
		current_root_tab = self.notebook.nametowidget(self.notebook.select())
		current_branch_tab = current_root_tab.notebook.nametowidget(current_root_tab.notebook.select())
		
		return current_root_tab, current_branch_tab
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
	    
	root.state('zoomed') #mamimise window
	root.mainloop()