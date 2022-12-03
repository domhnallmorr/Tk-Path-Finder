import datetime
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox

from controller import controller
from model import config_file_manager

from ttkbootstrap import Style
from ttkbootstrap.themes import standard

class MainApplication(ttk.Frame):
	def __init__(self, parent, *args, **kwargs):
		ttk.Frame.__init__(self, parent, *args, **kwargs)
		self.root = root
		self.parent = parent
		
		self.controller = controller.Controller(root, parent, self)
		
		# ----------------- VERSION -----------------------
		self.version = "0.39.0"
		# ----------------- WEEK NUMBER -----------------------
		year, week_num, day_of_week = datetime.date.today().isocalendar()
		
		self.parent.title(f"Tk Path Finder V{self.version} - Week {week_num}")
		
	def on_closing(self):
		# Ensure Config File is Saved on Closing Main Window
		config_file_manager.write_config_file(self.controller.model)
		root.destroy()
		
if __name__ == "__main__":
	root = tk.Tk()
	root.resizable(width=tk.TRUE, height=tk.TRUE)
	MA = MainApplication(root)

	root.state("zoomed") # mamimise window
	root.protocol("WM_DELETE_WINDOW", MA.on_closing)
	root.mainloop()