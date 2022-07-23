import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

class TitleBar(ttk.Frame):
	def __init__(self, mainapp, parent, title):
		super(TitleBar, self).__init__(parent)
		
		self.parent = parent
		self.setup_buttons()
		ttk.Label(self, text=title).pack(side=LEFT)
		
		
	def setup_buttons(self):
		ttk.Button(self, text="close", command=self.parent.destroy).pack(side=RIGHT)
		ttk.Button(self, text="max", command=self.maximise).pack(side=RIGHT)

		
	def maximise(self):
		self.parent.state('zoomed')