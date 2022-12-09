import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

from view import about_window

def setup_menubar(view):

	menu = tk.Menu(view.controller.mainapp.master)
	view.controller.mainapp.master.config(menu=menu)
	
	# ________ FILE ________
	file_menu = tk.Menu(menu, tearoff=0)
	menu.add_cascade(label="File", menu=file_menu)
	file_menu.add_command(label="Load Last Session", command=view.controller.load_last_session)

	# ________ SETTINGS ________
	settings_menu = tk.Menu(menu, tearoff=0)
	menu.add_cascade(label="Settings", menu=settings_menu)
	settings_menu.add_command(label="Edit Settings", command=view.controller.edit_settings)
	
	style_menu = tk.Menu(menu, tearoff=0)
	settings_menu.add_cascade(label="Style", menu=style_menu)
	
	light_style_menu = tk.Menu(menu, tearoff=0)
	dark_style_menu = tk.Menu(menu, tearoff=0)
	style_menu.add_cascade(label="Light", menu=light_style_menu)
	style_menu.add_cascade(label="Dark", menu=dark_style_menu)
	
	for s in view.themes["light"]:
		light_style_menu.add_command(label=s, command=lambda style=s: view.controller.update_style(style))

	for s in view.themes["dark"]:
		dark_style_menu.add_command(label=s, command=lambda style=s: view.controller.update_style(style))

	# ________ TOOLS ________
	tools_menu = tk.Menu(menu, tearoff=0)
	menu.add_cascade(label="Tools", menu=tools_menu)
	
	notes_menu = tk.Menu(menu, tearoff=0)
	tools_menu.add_command(label="Diary", command=view.controller.launch_diary)

	pdf_menu = tk.Menu(menu, tearoff=0)
	tools_menu.add_cascade(label="PDF Tools", menu=pdf_menu)
	pdf_menu.add_command(label="Extract Pages", command=view.controller.launch_pdf_extractor)
	pdf_menu.add_command(label="Merge PDFs", command=view.controller.launch_pdf_merger)
	
	tools_menu.add_command(label="To Do List", command=view.controller.launch_to_do_list)
		
	# ________ ABOUT ________
	about_menu = tk.Menu(menu, tearoff=0)
	menu.add_cascade(label="About" ,menu=about_menu)
	about_menu.add_command(label="About Tk Path Finder", command=lambda mainapp=view.controller.mainapp: about_window.about(mainapp))