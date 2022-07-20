import copy
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import font as tkfont

import treeview_functions
import autoscrollbar
import config_file_manager
import notes_backend

def launch_notes_categories(mainapp):
	w=NotesCategoriesWindow(mainapp)
	mainapp.master.wait_window(w.top)
	config_file_manager.write_config_file(mainapp)

def launch_notes_page(mainapp):
	w=NotesWindow(mainapp)
	mainapp.master.wait_window(w.top)

class NotesCategoriesWindow(ttk.Frame):
	def __init__(self, mainapp):
		super(NotesCategoriesWindow, self).__init__()
		top=self.top=Toplevel(mainapp.master)
		top.grab_set()
		self.mainapp = mainapp
		#self.backend = diary_backend.DiaryBackend()
		self.data = {}
		
		self.top.title("Manage Notes Categories")
		self.button = 'cancel'
		
		self.categories = sorted(list(self.mainapp.notes_categories.keys()))
		
		self.setup_label_frames()
		self.setup_labels()
		self.setup_input_widgets()
		self.setup_listboxes()
		self.setup_buttons()
		
	def setup_label_frames(self):
		self.categories_frame = LabelFrame(self.top, text="Categories:")
		self.categories_frame.pack(fill=BOTH, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)

		self.sub_categories_frame = LabelFrame(self.top, text="Sub-Categories:")
		self.sub_categories_frame.pack(expand=True, fill=BOTH, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
	def setup_labels(self):
		ttk.Label(self.categories_frame, text='Category Name:').grid(row=0, column=0, columnspan=1, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)

		# SUB-CATEGORIES
		ttk.Label(self.sub_categories_frame, text='Select Category:').grid(row=0, column=0, columnspan=1, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)		
		ttk.Label(self.sub_categories_frame, text='Sub-Category Name:').grid(row=0, column=2, columnspan=1, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
	def setup_input_widgets(self):
		self.category_entry = ttk.Entry(self.categories_frame, width=25)
		self.category_entry.grid(row=0, column=1, columnspan=1, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)

		self.category_combo = ttk.Combobox(self.sub_categories_frame, values=self.categories, state='readonly')
		self.category_combo.set(self.categories[0])
		self.category_combo.grid(row=0, column=1, columnspan=1, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
		self.sub_categories_entry = ttk.Entry(self.sub_categories_frame)
		self.sub_categories_entry.grid(row=0, column=3, columnspan=1, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
	def setup_listboxes(self):
		self.categories_listbox = Listbox(self.categories_frame)
		self.categories_listbox.grid(row=1, column=1, columnspan=15, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
		for idx, c in enumerate(self.categories):
			self.categories_listbox.insert(idx, c)
		
		
		self.sub_categories_listbox = Listbox(self.sub_categories_frame)
		self.sub_categories_listbox.grid(row=1, column=1, columnspan=15, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
		for c in self.mainapp.notes_categories[self.category_combo.get()]:
			self.sub_categories_listbox.insert(-1, c)
			
	def setup_buttons(self):
		# submit button
		self.submit_category = ttk.Button(self.categories_frame, text='Add', width=15, style='success.TButton', command=self.add_category)
		self.submit_category.grid(row=0, column=2, sticky='ew', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)		

		self.submit_sub_category = ttk.Button(self.sub_categories_frame, text='Add', width=15, style='success.TButton', command=self.add_sub_category)
		self.submit_sub_category.grid(row=0, column=4, sticky='ew', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)	
		
	def add_category(self):
		category = self.category_entry.get()
		
		# Check input valid
		msg = None
		if category == "":
			msg = "Enter a category title"
		if category in self.mainapp.notes_categories.keys():
			msg = "That category already exists, please enter an alternative"
		
		if msg:
			messagebox.showerror('Error', message=msg)
		else:
			self.mainapp.notes_categories[category] = ["Default"]
			self.categories_listbox.insert(len(self.mainapp.notes_categories.keys())-1, category)
			self.category_combo.config(values=list(self.mainapp.notes_categories.keys()))
			self.category_combo.set(category)
		
	def add_sub_category(self):
		category = self.category_combo.get()
		sub_category = self.sub_categories_entry.get()
	
		# Check input valid
		msg = None
		if sub_category == "":
			msg = "Enter a sub-category title"
		if sub_category in self.mainapp.notes_categories[category]:
			msg = "That sub-category already exists, please enter an alternative"		
		
		if msg:
			messagebox.showerror('Error', message=msg)
		else:
			self.mainapp.notes_categories[category].append(sub_category)
			self.sub_categories_listbox.insert(len(self.mainapp.notes_categories[category])-1, sub_category)		
		
class NotesWindow(ttk.Frame):
	def __init__(self, mainapp):
		super(NotesWindow, self).__init__()
		top=self.top=Toplevel(mainapp.master)
		top.grab_set()
		self.mainapp = mainapp
		self.backend = notes_backend.NotesBackend()
		self.setup_variables()
		
		self.top.title("Notes")
		self.button = 'cancel'
			
		self.setup_label_frames()
		self.setup_labels()
		self.setup_input_widgets()
		self.setup_buttons()
		
		
		self.page = None
		self.top.protocol("WM_DELETE_WINDOW", self.on_closing)
	
	def on_closing(self):
		if self.page is not None:
			self.get_text_input()

			for category in self.data.keys():
				for sub_category in self.data[category].keys():
					for page in self.data[category][sub_category].keys():
						self.backend.write_notes_database(category, sub_category, page, self.data[category][sub_category][page])
			
		self.top.destroy()
		
	def setup_variables(self):
		self.data = {}
		self.sub_category = None
		
	def setup_label_frames(self):
		self.categories_frame = LabelFrame(self.top, text="Select Category:")
		self.categories_frame.grid(row=0, column=0, columnspan=2, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)		

		self.manage_pages_frame = LabelFrame(self.top, text="Manage Pages:")
		self.manage_pages_frame.grid(row=0, column=2, columnspan=2, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
		self.pages_frame = LabelFrame(self.top, text="Pages:")
		self.pages_frame.grid(row=1, column=0, columnspan=1, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)	

		self.text_frame = LabelFrame(self.top, text="Text:")
		self.text_frame.grid(row=1, column=1, columnspan=2, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)	
		
		self.top.grid_columnconfigure(2, weight=1)
		self.top.grid_rowconfigure(1, weight=1)
		
		self.pages_frame.grid_rowconfigure(2, weight=1)

	def setup_labels(self):
		ttk.Label(self.categories_frame, text='Select Category:').grid(row=0, column=0, columnspan=1, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		ttk.Label(self.categories_frame, text='Select Sub-Category:').grid(row=1, column=0, columnspan=1, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		ttk.Label(self.manage_pages_frame, text='Page Name:').grid(row=0, column=0, columnspan=1, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
			
	def setup_input_widgets(self):
		self.category_combo = ttk.Combobox(self.categories_frame, values=list(self.mainapp.notes_categories.keys()), state='readonly')
		self.category_combo.grid(row=0, column=1, columnspan=1, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		self.category_combo.bind("<<ComboboxSelected>>", self.category_selected)

		self.sub_category_combo = ttk.Combobox(self.categories_frame, values=[], state='readonly')
		self.sub_category_combo.grid(row=1, column=1, columnspan=1, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		self.sub_category_combo.bind("<<ComboboxSelected>>", self.sub_category_selected)
		
		self.text_widget = tk.Text(self.text_frame, state="disabled")# width=110, height=10)
		self.text_widget.pack(expand=True, fill=BOTH, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
		
		self.pages_listbox = Listbox(self.pages_frame, width=50)
		self.pages_listbox.grid(row=2, column=0, columnspan=15, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		self.pages_listbox.bind('<<ListboxSelect>>', self.page_selected)
		
		self.page_name_entry = ttk.Entry(self.manage_pages_frame)
		self.page_name_entry.grid(row=0, column=1, columnspan=3, sticky='ew', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)

	def setup_buttons(self):
		# submit button
		self.add_page_btn = ttk.Button(self.manage_pages_frame, text='Add', width=15, style='success.TButton', command=self.add_page)
		self.add_page_btn.grid(row=1, column=0, sticky='ew', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)

		self.edit_page_btn = ttk.Button(self.manage_pages_frame, text='Edit Selected', width=15, style='info.TButton', command=self.edit_page)
		self.edit_page_btn.grid(row=1, column=1, sticky='ew', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
	def category_selected(self, event):
		category = self.category_combo.get()
		self.sub_category_combo.config(values=self.mainapp.notes_categories[category])
		
	def sub_category_selected(self, event):
		self.category = self.category_combo.get()
		self.sub_category = self.sub_category_combo.get()
		
		if self.category not in self.data.keys():
			self.data[self.category] = {}
		
		if self.sub_category not in self.data[self.category].keys():
			self.data[self.category][self.sub_category] = {}
			
		# need some code here to look for existing pages
		pages = self.backend.get_all_pages(self.category, self.sub_category)
		for idx, page in enumerate(pages):
			self.pages_listbox.insert(idx, page)
			
		if len(pages) > 0:
			self.pages_listbox.activate(0)
			
			text = self.backend.get_page_text(self.category, self.sub_category, pages[0])
			self.text_widget.config(state="normal")
			self.text_widget.insert("end", text)
			self.page = pages[0]
			
			self.data[self.category][self.sub_category][self.page] = text
			
	def page_selected(self, event):		
		w = event.widget
		index = int(w.curselection()[0])
		page = w.get(index)

		#Grab text from previous page
		self.get_text_input()
		
		if page not in self.data[self.category][self.sub_category].keys():
			self.data[self.category][self.sub_category][page] = self.backend.get_page_text(self.category, self.sub_category, page)
			
		self.text_widget.delete(1.0, "end")
		self.text_widget.insert("end", self.data[self.category][self.sub_category][page])
		self.page = page
		
		# Update page title entry
		self.page_name_entry.delete(0, "end")
		self.page_name_entry.insert(0, self.page)
	

	def add_page(self):
		new_page = self.page_name_entry.get().strip()
		
		# change page name valid
		msg = self.check_page_name(new_page)
			
		if msg is None:
			self.page = new_page
			
			self.data[self.category][self.sub_category][self.page] = ""
			
			self.pages_listbox.insert(0, self.page)
			
			if self.page:
				self.get_text_input()
				
			self.text_widget.delete(1.0, "end",)
			self.text_widget.config(state="normal")
				
	def edit_page(self):
		new_page = self.page_name_entry.get()
		
		msg = self.check_page_name(new_page)
		
		if msg is None:
			# get original name
			index = int(self.pages_listbox.curselection()[0])
			orig_page = self.pages_listbox.get(index)
			
			
			# update listbox
			self.pages_listbox.delete(index)
			self.pages_listbox.insert(index, new_page)
			
			# update data
			self.data[self.category][self.sub_category][new_page] = copy.deepcopy(self.data[self.category][self.sub_category][self.page])
			self.data[self.category][self.sub_category].pop(self.page)
			
			
			# delete old page from database
			self.backend.delete_page(self.category, self.sub_category, self.page)
			
			# insert new page in database
			self.page = new_page
			self.backend.write_notes_database(self.category, self.sub_category, new_page, self.data[self.category][self.sub_category][new_page])
			

			
	def check_page_name(self, name):
		msg = None

		if name in self.data[self.category][self.sub_category].keys():
			msg = "That page name already exists in this sub-category, please enter another!"
			
		if name == "":
			msg = "Enter a Page Name!"
			
		if self.sub_category is None:
			msg = "Select a Sub-Category First!"
			
		if msg is not None:
			messagebox.showerror('Error', message=msg)
			
		return msg
	
	def get_text_input(self):
		self.data[self.category][self.sub_category][self.page] = self.text_widget.get("1.0","end")
		
		