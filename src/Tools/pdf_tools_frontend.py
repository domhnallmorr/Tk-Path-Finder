import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import simpledialog
from tkinter.filedialog import askopenfilename

from Tools import pdf_tools_backend

def launch_pdf_extractor(mainapp):
	w = PdfExtractorWindow(mainapp)
	mainapp.master.wait_window(w.top)

class PdfExtractorWindow(ttk.Frame):
	def __init__(self, mainapp):
		super(PdfExtractorWindow, self).__init__()
		top=self.top=Toplevel(mainapp.master)
		top.grab_set()
		self.mainapp = mainapp
		
		self.top.title("Extract PDF Pages")
		self.button = 'cancel'
		
		self.setup_label_frames()
		self.setup_input_widgets()
		
	def setup_label_frames(self):
		self.options_frame = LabelFrame(self.top, text="Options:")
		self.options_frame.pack(fill=BOTH, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		self.options_frame.grid_columnconfigure(9, weight=1)
	
	def setup_input_widgets(self):
		self.file_name_entry = ttk.Entry(self.options_frame, width=120)
		self.file_name_entry.grid(row=0, column=0, columnspan=10, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady, sticky="EW")
		self.file_name_entry.config(state="disabled")
		
		ttk.Button(self.options_frame, text="Browse", width=10, command=self.select_file).grid(row=0, column=10, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
	
		ttk.Label(self.options_frame, text="First Page:").grid(row=1, column=0, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		self.start_page_combo =  ttk.Combobox(self.options_frame, values=[], state='disabled')
		self.start_page_combo.grid(row=1, column=1, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)

		ttk.Label(self.options_frame, text="Last Page:").grid(row=1, column=2, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		self.end_page_combo =  ttk.Combobox(self.options_frame, values=[], state='disabled')
		self.end_page_combo.grid(row=1, column=3, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		
		ttk.Button(self.options_frame, text="Extract", style='success.TButton', command=self.extract_pages).grid(row=1, column=10, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady, sticky="EW")
		
	def select_file(self):
		path = askopenfilename()
		
		if path:
			if not path.lower().endswith(".pdf"):
				messagebox.showerror('Error', message="File Selected Must be a PDF File")
			else:
				self.file_name_entry.config(state="normal")
				self.file_name_entry.delete(0, END)
				self.file_name_entry.insert(0, path)
				self.file_name_entry.config(state="readonly")
				
				self.pdf_file = pdf_tools_backend.read_pdf(path)
				self.pdf_path = path
				self.number_of_pages = pdf_tools_backend.get_number_of_pages(self.pdf_file)
				
				
				self.start_page_combo.config(state="normal", values=[i+1 for i in range(self.number_of_pages)])
				self.start_page_combo.set(1)
				self.end_page_combo.config(state="normal", values=[i+1 for i in range(self.number_of_pages)])
				self.end_page_combo.set(1)
				
	def extract_pages(self):
		start_page = int(self.start_page_combo.get())
		end_page = int(self.end_page_combo.get())
		
		if start_page > end_page:
			messagebox.showerror('Error', message="Start Page Must be Less Than or Equal to End Page")
		else:
			output_filename = pdf_tools_backend.extract_pages(self.file_name_entry.get(), start_page, end_page)
			messagebox.showerror('Info', message=f"Successfully Created File {output_filename}")
			
	
class PdfMergeWindow(ttk.Frame):
	def __init__(self, mainapp):
		super(PdfMergeWindow, self).__init__()
		top=self.top=Toplevel(mainapp.master)
		top.grab_set()
		self.mainapp = mainapp
		
		self.top.title("Merge PDFs")
		self.button = 'cancel'		
		