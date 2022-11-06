from datetime import date
import datetime
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import font as tkfont
import threading
import time

from ttkbootstrap.dialogs import dialogs
from ttkbootstrap.scrolled import ScrolledText

from view import treeview_functions
from custom_widgets import autoscrollbar
from model import config_file_manager

def launch_diary(mainapp):
	if mainapp.diary_open is False:
		mainapp.diary_open = True
		
		mainapp.diary_window = DiaryWindow(mainapp)
		mainapp.master.wait_window(mainapp.diary_window.top)
		config_file_manager.write_config_file(mainapp)
		
		mainapp.diary_open = False
	else:
		mainapp.diary_window.top.state('zoomed')
		mainapp.diary_window.top.lift()
		
class DiaryWindow(ttk.Frame):
	def __init__(self, master, view):
		super(DiaryWindow, self).__init__()
		top=self.top=Toplevel(master)
		#top.grab_set()
		# self.backend = diary_backend.DiaryBackend()
		self.view = view
		self.data = {}
		
		self.top.title("Diary")
		self.button = 'cancel'
		
		self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
		self.title_font.configure(underline=True)
		
		self.setup_label_frames()
		self.setup_labels()
		self.setup_buttons()
		self.setup_text_widget()
	
		self.top.protocol("WM_DELETE_WINDOW", self.on_closing)

		self.top.state('zoomed')
		
	def on_closing(self):
		self.get_text_input()

		for date in self.data.keys():
			self.view.controller.write_diary_text_to_database(date, self.data[date])
			
		self.top.destroy()
	
	def setup_label_frames(self):
		self.date_frame = LabelFrame(self.top, text="Date:")
		self.date_frame.pack(fill=BOTH, padx=self.view.default_padx, pady=self.view.default_pady)

		self.notes_frame = LabelFrame(self.top, text="Notes:")
		self.notes_frame.pack(expand=True, fill=BOTH, padx=self.view.default_padx, pady=self.view.default_pady)
		self.notes_frame.grid_columnconfigure(1, weight=1)
		self.notes_frame.grid_rowconfigure(1, weight=1)
		
	def setup_labels(self):
		today = date.today()
		self.checked_date_in_database = False
		self.data[today] = self.view.controller.read_date_from_database(today)
		
		self.top_label = tk.Label(self.date_frame, text=(today), font=self.title_font, anchor="w")
		#self.top_label.pack(fill=tk.BOTH, expand=True)
		self.top_label.grid(row=0, column=0, padx=self.view.default_padx)
		
		self.date = today
		self.update_top_label()
		
	def setup_buttons(self):
		ttk.Button(self.date_frame, text=u'\u2190', command=self.back_one_day, style='primary.TButton').grid(row=0, column=2, padx=2)
		ttk.Button(self.date_frame, image=self.view.calender_white_icon2, style='primary.Outline.TButton', command=self.calender_select).grid(row=0, column=3, padx=2)
		ttk.Button(self.date_frame, text=u'\u2192', command=self.forward_one_day, style='primary.TButton').grid(row=0, column=4, padx=2)
		self.date_frame.grid_columnconfigure(1, weight=1)
		
		ttk.Button(self.notes_frame, image=self.view.bullet_point_dark_icon2, command=self.add_bullet_point, style='primary.TButton').grid(row=0, column=0, padx=self.view.default_padx, pady=self.view.default_pady)
		
	def back_one_day(self):
		self.get_text_input()
		self.date = self.date - datetime.timedelta(days=1)
		self.date_changed()
		
	def forward_one_day(self):
		self.get_text_input()
		self.date = self.date + datetime.timedelta(days=1)
		self.date_changed()

	def calender_select(self):
		self.get_text_input()
		w = dialogs.DatePickerDialog()
		self.date = w.date_selected
		self.date_changed()

	def setup_text_widget(self):
		self.general_text = tk.Text(self.notes_frame)# width=110, height=10)
		#self.general_text.pack(side=LEFT, expand=True, fill=BOTH, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		self.general_text.grid(row=1, column=0, columnspan=2, sticky="NSEW", padx=self.view.default_padx, pady=self.view.default_pady)
		
		vsb = autoscrollbar.AutoScrollbar(self.notes_frame, orient="vertical", command=self.general_text.yview)
		vsb.grid(row=1, column=2, columnspan=1, sticky="NS")
		
		self.general_text.configure(yscrollcommand=vsb.set)
		
		# Add any text present in database_thread
		txt = self.view.controller.read_date_from_database(self.date)
		self.general_text.insert("end", txt["General"])		
		self.general_text.bind('<Return>', self.enter_event)

	def add_bullet_point(self):
		self.general_text.insert("insert", u"\u2022" + " ")
		
	def enter_event(self, event):
		pass
		
	def get_text_input(self):
		self.data[self.date] = {"General": self.general_text.get("1.0","end")}
		
	def date_changed(self):
		self.general_text.delete(1.0, "end",)
	
		if self.date not in self.data.keys():
			self.data[self.date] = self.view.controller.read_date_from_database(str(self.date))
			
		self.general_text.insert("end", self.data[self.date]["General"])
		self.update_top_label()
		
	def update_top_label(self):
		date_text = f"{self.date.strftime('%d')} {self.date.strftime('%B')} {self.date.strftime('%Y')}"
		self.top_label.config(text=date_text)

	def cut(self, event):
		if self.general_text.selection_get():
			self.selected = self.general_text.selection_get()
			self.selected.delete("sel.first", "self.last")
		
	def copy(self, event):
		print("Copying")

	def paste(self, event):
		print("Copying")
		