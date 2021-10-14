import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

from ttkbootstrap import Style

import about_screen
import root_tab
import tkexplorer_icons

class MainApplication(ttk.Frame):
	def __init__(self, parent, *args, **kwargs):
		ttk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		self.root_tabs = {}
		self.id = 0
		self.setup_variables()
		
		# Styles
		self.style = Style('darkly')
		self.default_pady = 10
		tkexplorer_icons.setup_icons(self)

		self.setup_menu()
		
		self.setup_main_frames()
		self.setup_notebook()
		self.setup_tabs()

	def setup_variables(self):
		self.version = '0.01.0'
		self.parent.title(f"Tk Path Finder V{self.version}")

	def setup_menu(self):
		menu = tk.Menu(self.master)
		self.master.config(menu=menu)

		# ________ ABOUT ________
		about_menu = tk.Menu(menu, tearoff = 0)
		menu.add_cascade(label='About',menu=about_menu)
		about_menu.add_command(label = 'About Tk Path Finder', command = lambda self=self: about_screen.about(self))
		
	def setup_notebook(self):
		self.notebook = ttk.Notebook(self.container)
		self.notebook.pack(expand=True, fill=BOTH, side=LEFT)
		self.notebook.bind('<Button-3>', root_tab.right_click)
		self.notebook.mainapp = self
		
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
		self.sidebar_frame.grid_rowconfigure(1, weight=1)
		self.sidebar_frame.grid_columnconfigure(19, weight=1)
		self.rootpane.add(self.sidebar_frame)

		self.container = tk.Frame(self.rootpane, bg='pink')
		self.container.pack(expand=True, fill=BOTH, side=LEFT)
		#self.container.grid_columnconfigure(0, weight=1)
		
		self.rootpane.add(self.container,)#stretch="always")	
		
		ttk.Label(self.sidebar_frame, text='Quick Access').pack()
		#ttk.Button(self.container, text='Add Root', command=self.create_root_tab).pack()
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
	
	#root.geometry('{}x{}'.format(MA.screen_width, MA.screen_height))    
	root.state('zoomed') #mamimise window
	root.mainloop()