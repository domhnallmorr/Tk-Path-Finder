import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *



class NewFoldersWindow(ttk.Frame):
	def __init__(self, master, view, initialvalue):
		super(NewFoldersWindow, self).__init__()
		top=self.top=Toplevel(master)
		top.grab_set()
		
		self.top.title(f"New Folder(s)")
		self.button = "cancel"

		self.folder_text = tk.Text(self.top, width=110, height=10)
		self.folder_text.grid(row=1, column=0, columnspan = 8, sticky="NSEW",padx=5, pady=5, ipadx=2, ipady=5)
		if initialvalue is not None:
			self.folder_text.insert("1.0", initialvalue)
		
		self.top.grid_rowconfigure(1, weight=1)
		self.top.grid_columnconfigure(0, weight=1)
		
		# Buttons
		self.ok_btn = ttk.Button(self.top, text="OK", width=10, style="success.TButton", command=lambda button="ok": self.cleanup(button))
		self.ok_btn.grid(row=2, column=6, padx=5, pady=5, sticky="ne")
		self.cancel_btn = ttk.Button(self.top, text="Cancel", width=10, style="danger.TButton", command=lambda button="cancel": self.cleanup(button))
		self.cancel_btn.grid(row=2, column=7, padx=5, pady=5, sticky="nw")
		
		self.folder_text.bind("<Control-d>", self.duplicate_line)
		
	def duplicate_line(self, event):
		current_line = int(self.folder_text.index(INSERT).split(".")[0])-1 #convert to 0 index system
		all_lines = self.folder_text.get("1.0",END).split("\n")
		
		all_lines.insert(current_line+1, all_lines[current_line])
		#all_lines = "\n".join(all_lines)
		lines_to_insert = []
		
		for l in all_lines:
			if not l.replace("\n", "").strip() == "": #remove any blank lines
				lines_to_insert.append(l) 

		self.folder_text.delete("1.0", END)
		self.folder_text.insert("end", "\n".join(lines_to_insert))
		#self.folder_text.mark_set("insert", "%d.%d" % (current_line+1, 1))
		
	def cleanup(self, button):
		if button == "ok":
			self.folders = list(filter(None, [n.strip() for n in self.folder_text.get("1.0","end").split('\n')])) #avoid empty lines
			self.button = "ok"
			self.top.destroy()

		else:
			self.top.destroy()