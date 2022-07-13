import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import simpledialog
import treeview_functions

import time

import autoscrollbar
import config_file_manager

def launch_to_do_list(mainapp):
	w=ToDoListWindow(mainapp,)
	mainapp.master.wait_window(w.top)
	config_file_manager.write_config_file(mainapp)

class ToDoListWindow(ttk.Frame):
	def __init__(self, mainapp,):
		super(ToDoListWindow, self).__init__()
		top=self.top=Toplevel(mainapp.master)
		top.grab_set()
		self.mainapp = mainapp
		
		self.top.title(f"To Do List")
		self.button = 'cancel'
		self.setup_label_frames()
		self.setup_input_widgets()
		self.setup_buttons()
		self.setup_treeview()
		
		self.top.grid_columnconfigure(7, weight=1)
		self.top.grid_rowconfigure(2, weight=1)
		self.todo_frame.grid_columnconfigure(14, weight=1)
		self.todo_frame.grid_rowconfigure(4, weight=1)
		
	def setup_label_frames(self):
		self.todo_frame = LabelFrame(self.top, text="To Do List:")
		self.todo_frame.grid(row=2, column=0, columnspan=8, rowspan=2, sticky='NSEW', padx=self.mainapp.default_padx, pady=5, ipadx=2, ipady=5)
		
	def setup_treeview(self):
		column_names = ["#", "Status", "Task"]
		column_widths = [50, 100, 500]
		height = 20

		self.treeview = treeview_functions.create_treeview(self.todo_frame, column_names, column_widths, height)
		self.treeview.grid(row=4, column=0, columnspan=16, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		treeview_functions.write_data_to_treeview_general(self.treeview, 'replace', self.mainapp.to_do_list)
		self.update_tags()
		self.treeview.bind("<<TreeviewSelect>>", self.on_left_click)
		self.treeview.bind("<Button-1>", self.header_click)
		
		self.treeview.tag_configure("open", foreground="white", background="#6e4905")
		self.treeview.tag_configure("closed", foreground="white", background="#24751e")

		vsb = autoscrollbar.AutoScrollbar(self.todo_frame, orient="vertical", command=self.treeview.yview)
		vsb.grid(row=4, column=16, sticky='NSEW')
		self.treeview.configure(yscrollcommand=vsb.set)
		
	def setup_input_widgets(self):

		ttk.Label(self.todo_frame, text='Task:').grid(row=0, column=0, columnspan=1, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		self.task_entry = ttk.Entry(self.todo_frame)
		self.task_entry.grid(row=0, column=1, columnspan=15, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
		ttk.Label(self.todo_frame, text='Status:').grid(row=1, column=0, columnspan=1, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		self.status_combo = ttk.Combobox(self.todo_frame, values=["Open", "Closed"], state='readonly')
		self.status_combo.set("Open")
		self.status_combo.grid(row=1, column=1, columnspan=1, sticky='NSEW', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
	def setup_buttons(self):
		# submit button
		self.submit = ttk.Button(self.todo_frame, text='Add', width=15, style='success.TButton', command=self.add)
		self.submit.grid(row=3, column=0, sticky='ew', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
		self.edit = ttk.Button(self.todo_frame, text='Edit Selected', width=15, style='info.TButton', command=self.edit_row)
		self.edit.grid(row=3, column=1, sticky='ew', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)

		self.delete_btn = ttk.Button(self.todo_frame, text='Delete Selected', width=15, style='danger.TButton', command=self.delete_row)
		self.delete_btn.grid(row=3, column=2, sticky='ew', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
		self.delete_all_btn = ttk.Button(self.todo_frame, text='Delete All', width=15, style='danger.TButton', command=self.delete_all)
		self.delete_all_btn.grid(row=3, column=15, sticky='ew', padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
	def add(self):
		task = self.task_entry.get()
		self.mainapp.to_do_list.append([len(self.mainapp.to_do_list)+1, "Open", task])
		
		treeview_functions.write_data_to_treeview_general(self.treeview, 'replace', self.mainapp.to_do_list)
		self.update_tags()
		
	def edit_row(self):
		idx, data = treeview_functions.get_current_selection(self.treeview)
		selected_iid = self.treeview.selection()[0]
		current_idx = self.treeview.index(selected_iid)
		
		self.treeview.item(selected_iid)
		self.treeview.item(selected_iid, text=self.treeview.item(selected_iid, 'text'))
		self.treeview.item(selected_iid, values=[self.status_combo.get(), self.task_entry.get()])
		
		self.mainapp.to_do_list[current_idx] = [self.treeview.item(selected_iid, 'text'), self.status_combo.get(), self.task_entry.get()]
		self.update_tags()
		
	def delete_row(self):
		selected_iid = self.treeview.selection()[0]
		current_idx = self.treeview.index(selected_iid)
		
		msg = messagebox.askyesno(title='Delete Task', message='Delete This Task? This Cannot be Undone.')
		
		if msg:
			self.treeview.delete(selected_iid)
			self.mainapp.to_do_list.pop(current_idx)

	def delete_all(self):		
		msg = messagebox.askyesno(title='Delete All Tasks', message='Delete All Tasks? This Cannot be Undone.')
		
		if msg:
			self.mainapp.to_do_list = []
			treeview_functions.write_data_to_treeview_general(self.treeview, 'replace', self.mainapp.to_do_list)
			
	def update_tags(self):
		for child in self.treeview.get_children():
			self.treeview.item(child, tags=(self.treeview.item(child)["values"][0].lower()))
			
	def on_left_click(self, event):
		region = self.treeview.identify("region", event.x, event.y)
		if region == 'heading':
			for item in self.treeview.selection():
				self.treeview.selection_remove(item)
				
		else:
			if len(self.treeview.item(self.treeview.selection(), "values")) > 0:
				self.task_entry.delete(0, "end")
				self.task_entry.insert(0, self.treeview.item(self.treeview.selection(), "values")[-1])
				self.status_combo.set(self.treeview.item(self.treeview.selection(), "values")[0])	
		
	def header_click(self, event):
		'''
			When we click header, unselect everything in the treeview (so tag colors can be seen clearly)
		'''
		region = self.treeview.identify("region", event.x, event.y)
		if region == 'heading':
			for item in self.treeview.selection():
				self.treeview.selection_remove(item)