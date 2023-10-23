import copy
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox

from ttkbootstrap import Style
from ttkbootstrap.themes import standard

from custom_widgets import autoscrollbar, branch_tab, root_tab, quick_access_tree
from view import filter_windows, menubar, tkexplorer_icons

class View:
	def __init__(self, root, parent, controller, config_data):
		self.root = root
		self.parent = parent
		self.controller = controller
		
		tkexplorer_icons.setup_icons(self)
		self.setup_default_settings(config_data)
		self.setup_variables()
		
		self.setup_main_frames()
		self.setup_main_notebook()
		self.setup_quick_access()
		
		menubar.setup_menubar(self)
		
		self.switch_style(self.style_name)

	def setup_variables(self):
		self.known_file_types = {
			".csv": self.excel_icon2,
			".das": self.deepriser_icon2,
			".dat": self.dat_icon2,
			".doc": self.word_icon2,
			".docx": self.word_icon2,
			".exe": self.new_icon2,
			".f06": self.f06_icon2,
			".ipynb": self.notebook_icon2,
			".jpeg": self.image_icon2,
			".jpg": self.image_icon2,
			".json": self.new_icon2,
			".keyx": self.key_file_icon2,
			".mkv": self.video_icon2,
			".mp3": self.audio_icon2,
			".mp4": self.video_icon2,
			".mplt": self.video_icon2,
			".msg": self.msg_icon2,
			".out": self.new_icon2,
			".op2": self.op2_icon2,
			".pdf": self.pdf_icon2,
			".png": self.image_icon2,
			".pptx": self.pptx_icon2,
			".py": self.python_icon2,
			".rar": self.rar_icon2,
			".torrent": self.new_icon2,
			".txt": self.text_icon2,
			".xls": self.excel_icon2,
			".xlsm": self.excel_icon2,
			".xlsx": self.excel_icon2,
			".xmcd": self.mathcad_icon2,
			".zip": self.zip_icon2,
		}
		
		self.root_tabs = {}
		self.branch_tabs = {}

		# --------------- GET THEMES ---------------
		self.themes = {"light": [], "dark":[]}

		for theme in standard.STANDARD_THEMES.keys():
			theme_type = standard.STANDARD_THEMES[theme]["type"].lower()
			self.themes[theme_type].append(theme)
		
		self.tool_top_delay = 600
		self.clipboard_label_text = "Clipboard: 0 Selected"
		
	def setup_main_frames(self):
		self.rootpane = ttk.PanedWindow(self.parent, orient=tk.HORIZONTAL)
		self.rootpane.pack(expand=True, fill=BOTH, side=LEFT)

		self.sidebar_frame = ttk.Frame()
		self.sidebar_frame.grid_rowconfigure(2, weight=1)
		self.sidebar_frame.grid_columnconfigure(7, weight=1)
		self.rootpane.add(self.sidebar_frame, weight=1)

		self.container = tk.Frame(self.rootpane, bg='pink')
		self.container.pack(expand=True, fill=BOTH, side=LEFT)
		
		self.rootpane.add(self.container)
		
		ttk.Label(self.sidebar_frame, text='Quick Access').grid(row=0, column=0, columnspan=8, sticky='NSEW')

	def setup_main_notebook(self):
		self.main_notebook = ttk.Notebook(self.container)
		self.main_notebook.pack(expand=True, fill=BOTH, side=LEFT)
		self.main_notebook.bind("<Button-3>", self.right_click_root)
		self.main_notebook.bind("<B1-Motion>", self.reorder)

	def setup_quick_access(self):
		self.quick_access_tree = quick_access_tree.QuickAccessTreeview(self)
		self.quick_access_tree.grid(row=2, column=0, columnspan=8, sticky='NSEW')
		
		vsb = autoscrollbar.AutoScrollbar(self.sidebar_frame, orient="vertical", command=self.quick_access_tree.yview)
		vsb.grid(row=2, column=8, sticky='NSEW')
		self.quick_access_tree.configure(yscrollcommand=vsb.set)
		
	def add_root_tab(self, id, text):
		tab = root_tab.RootTab(self, id, text)
		self.main_notebook.add(tab, image=self.root_icon2, compound=tk.LEFT, text=f"{text.ljust(20)}")

		self.root_tabs[id] = tab
		
	def add_branch_tab(self, id, text, root_id):
		root_tab = self.root_tabs[root_id]
		
		tab = branch_tab.BranchTab(self, id, root_tab)
		root_tab.add_branch_tab(tab, text)
		
		self.branch_tabs[id] = tab
		
	def setup_default_settings(self, config_data):
		# --------------- PADX AND PADY ---------------
		self.default_padx = 5
		self.default_pady = 10
		
		# --------------- TREEVIEW COLUMN WIDTHS ---------------
		self.default_file_width = config_data["default_file_width"]
		self.default_date_width = config_data["default_date_width"]
		self.default_type_width = config_data["default_type_width"]
		self.default_size_width = config_data["default_size_width"]
		
		self.style_name = config_data["default_style"]
	
	def update_root_tab_text(self, root_id, text):
		self.main_notebook.tab(self.root_tabs[root_id], text=f"{text.ljust(20)}")
	
	def update_branch_tab(self, data, mode="normal"):
		self.branch_tabs[data["id"]].update(data, mode)

	def delete_root_tab(self, root_id):
		self.root_tabs[root_id].destroy()
		
	def delete_branch_tab(self, branch_id):
		self.branch_tabs[branch_id].destroy()
		
	def show_error(self, msg):
		messagebox.showerror("Error", message=msg)

	def show_success(self, msg):
		messagebox.showinfo("Success", message=msg)

	def right_click_root(self, event):
		tab_object = event.widget.nametowidget(event.widget.select())
		root_id = tab_object.root_id
		
		popup_menu = tk.Menu(event.widget, tearoff=0)
		popup_menu.add_command(label="Add Root Tab", command=self.controller.add_root_tab, image=self.root_icon2, compound='left')
		popup_menu.add_command(label="Rename Root Tab", command=lambda root_id=root_id: self.controller.rename_root_tab(root_id), image=self.edit_icon2, compound='left')
		popup_menu.add_command(label="Delete Root Tab", command=lambda root_id=root_id: self.controller.delete_root_tab(root_id), image=self.delete_icon2, compound='left')

		try:
			popup_menu.tk_popup(event.x_root, event.y_root, 0)
		finally:
			popup_menu.grab_release()

	def switch_style(self, style):
		self.style_name = style
		
		try:
			self.style = Style(style)
			
		except Exception as e:
			if "bad window path name" in str(e):
				pass # ignore error when trying to acceess a top level window that's been destroyed
			else:
				messagebox.showerror("Error", message=f"The following message occured {str(e)}")
		
		self.style.configure('Treeview', rowheight=18)
		self.style.configure('Treeview.Heading', background=self.style.colors.secondary)
		
		# Update hover color in treeviews
		for tab in self.branch_tabs.keys():
			self.branch_tabs[tab].update_tags()
				
		self.quick_access_tree.update_tags()
		
	def ask_yes_no(self, msg):
		answer = messagebox.askyesno(title="Confirm", message=msg)
		
		return answer
		
	def delete_all_tabs(self):
		for root_id in self.root_tabs:
			self.delete_root_tab(root_id)
		self.root_tabs = {}
		self.branch_tabs = {}	

	def launch_filter_filename_window(self, master, data):
		self.w = filter_windows.FilterNameWindow(master, self, data)
		master.wait_window(self.w.top)
		
		return self.w.text, self.w.filter
		
	def reorder(self, event):
		try:
			index = self.main_notebook.index(f"@{event.x},{event.y}")
			self.main_notebook.insert(index, child=self.main_notebook.select())
			self.get_root_tabs_order()
		except tk.TclError:
			pass
			
	def get_root_tabs_order(self):
		root_tabs_order = []
		for t in self.main_notebook.tabs():
			root_tabs_order.append(self.main_notebook.nametowidget(t).root_id)
		
		reordered_dict = {k: self.root_tabs[k] for k in root_tabs_order}
		self.root_tabs = reordered_dict
		self.controller.update_root_tabs_order(root_tabs_order)
		
	def update_clipboard_labels(self, number_of_items, total_size_selected, mode):
		
		for branch_id in self.branch_tabs.keys():
			if total_size_selected is None:
				self.clipboard_label_text = f"Clipboard: {number_of_items} Selected to {mode.capitalize()}"
			else:
				self.clipboard_label_text = f"Clipboard: {number_of_items} Selected to {mode.capitalize()} {total_size_selected}"

			self.branch_tabs[branch_id].clipboard_label.config(text=self.clipboard_label_text)