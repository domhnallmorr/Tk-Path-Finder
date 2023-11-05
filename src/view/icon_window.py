import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox

def launch_icon_window(controller):
	master = controller.mainapp.root
	controller.w = IconWindow(master, controller.view)
	master.wait_window(controller.w.top)

class IconWindow(ttk.Frame):
	def __init__(self, master, view):
		super(IconWindow, self).__init__()
		top=self.top=Toplevel(master)
		top.grab_set()
		self.view = view

		self.top.title("Change Icon")

		self.button = "cancel"
		self.add_icons()

		self.cancel_btn = ttk.Button(self.top, text="Cancel", width=10, style="danger.TButton", command=lambda button="cancel": self.cleanup(button))
		self.cancel_btn.grid(row=2, column=7, padx=self.view.default_padx, pady=self.view.default_pady, sticky="ne")	

	def add_icons(self):

		icon_frame = LabelFrame(self.top, text="Select Icon")
		icon_frame.grid(row=1, column=0, columnspan=8, padx=self.view.default_padx, pady=self.view.default_pady, sticky="ew")

		col = 0
		row = 0

		icons_added = []
		for extension in self.view.known_file_types.keys():
			icon = self.view.known_file_types[extension]

			if icon not in icons_added: # avoid duplicates
				icons_added.append(icon)

				if self.view.style_type == "dark":
					style = "dark.TButton"
				else:
					style = "light.TButton"
				icon_button = ttk.Button(icon_frame, image=icon, style=style, command=lambda button="ok", extension=extension: self.cleanup(button, extension))
				icon_button.grid(row=row, column=col, padx=self.view.default_padx, pady=self.view.default_pady, sticky="nsew")

				col += 1

				if col == 8:
					col = 0
					row += 1

	def cleanup(self, button, extension=None):
		self.button = button
		self.extension = extension

		self.top.destroy()