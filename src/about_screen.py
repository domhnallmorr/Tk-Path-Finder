import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

def about(mainapp):

	win = tk.Toplevel()
	win.wm_title("About Tk Path Finder")

	l = tk.Label(win, width = 20, text=f"Tk Path Finder Version {mainapp.version}")
	l.grid(row=0, column=1, columnspan = 3)

	l2 = tk.Label(win, text=f"Icons From https://icons8.com")
	l2.grid(row=1, column=0, columnspan = 5)

	l3 = tk.Label(win, text = '''
	    Tk Path Finder makes no promise of warranty, satisfaction, performance, or
        anything else. Understand that your use of this tool is completely
        at your own risk.''')
	l3.grid(row=2, column=0, columnspan = 5)
	
	b = ttk.Button(win, text="Okay", command=win.destroy)
	b.grid(row=3, column=2)