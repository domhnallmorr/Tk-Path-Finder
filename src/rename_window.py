import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

class RenameWindow:			
	def __init__(self, lopa, mainapp, master, side, row_data):
		top=self.top=Toplevel(master)
		top.grab_set()