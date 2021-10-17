import difflib
import os
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import simpledialog

import autoscrollbar

class ComparisonWindow(ttk.Frame):
	def __init__(self, mainapp, master, branch_tab):
		super(ComparisonWindow, self).__init__()
		top=self.top=Toplevel(master)
		top.grab_set()
		self.mainapp = mainapp
		self.branch_tab = branch_tab
		
		# File name labels
		ttk.Label(self.top, text=self.mainapp.file_compare_left).grid(row=0, column=0, columnspan=8, sticky='NSEW', padx=5, pady=5, ipadx=2, ipady=5)
		ttk.Label(self.top, text=self.mainapp.file_compare_right).grid(row=0, column=8, columnspan=8, sticky='NSEW', padx=5, pady=5, ipadx=2, ipady=5)
		
		# Text widgets
		self.left_text = tk.Text(self.top, wrap="none", width=50, height=20)
		self.left_text.grid(row=1, column=0, columnspan=8, sticky='NSEW', padx=5, pady=5, ipadx=2, ipady=5)

		self.right_text = tk.Text(self.top, wrap="none", width=50, height=20)
		self.right_text.grid(row=1, column=8, columnspan=8, sticky='NSEW', padx=5, pady=5, ipadx=2, ipady=5)
		
		vsb = autoscrollbar.AutoScrollbar(self.top, orient="vertical", command=self.multiple_yview)
		vsb.grid(row=1, column=16, sticky='NSEW')
		self.left_text.configure(yscrollcommand=vsb.set)
		self.right_text.configure(yscrollcommand=vsb.set)
		
		# Tags for text widgets
		for t in [self.left_text, self.right_text]:
			t.tag_configure("SAME", foreground='white', background='dark green')
			t.tag_configure("DIFF", foreground='white', background='red4')
		
		self.top.grid_rowconfigure(1, weight=1)
		self.top.grid_columnconfigure(0, weight=1)
		self.top.grid_columnconfigure(8, weight=1)
		
		self.compare_files()
		
	def compare_files(self):
		f1 = open(self.mainapp.file_compare_left, "r").readlines()
		f2 = open(self.mainapp.file_compare_right, "r").readlines()

		self.differ = difflib.Differ()
		self.comparison = self.differ.compare(f1, f2)
		self.update_text_widgets()
		
	def update_text_widgets(self):
		for line in self.comparison:
			marker = line[0]
			if marker == " ":
				# line is same in both
				self.left_text.insert("end", line[2:], 'SAME')
				self.right_text.insert("end", line[2:], 'SAME')

			elif marker == "-":
				# line is only on the left
				self.left_text.insert("end", line[2:], 'DIFF')
				self.right_text.insert("end", "\n")

			elif marker == "+":
				# line is only on the right
				self.left_text.insert("end", "\n")
				self.right_text.insert("end", line[2:], 'DIFF')
				
	def multiple_yview(self, *args):
		self.left_text.yview(*args)
		self.right_text.yview(*args)