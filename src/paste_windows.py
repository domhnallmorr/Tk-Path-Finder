from distutils.dir_util import copy_tree
from multiprocessing import Process
import os
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import simpledialog
import time

import autoscrollbar


def paste_folder(mainapp, branch_tab, source, destination):
	launch_window(mainapp, branch_tab, source, destination)
	
def start_paste_folder(source, destination):
	copy_tree(source, destination)

def launch_window(mainapp, branch_tab, source, destination):
	mainapp.w = PasteWindow(mainapp, branch_tab.master, branch_tab, source, destination)
	mainapp.root.after(1000, mainapp.w.check_progress)
	#mainapp.master.wait_window(self.w.top)		


	
class PasteWindow(ttk.Frame):
	def __init__(self, mainapp, master, branch_tab, source, destination):
		super(PasteWindow, self).__init__()
		top=self.top=Toplevel(master)
		self.top.attributes('-topmost', 'true')
		#top.grab_set()
		self.mainapp = mainapp
		self.source = source
		self.destination = destination
	
		processes = []
		processes.append(Process(target=start_paste_folder, args=[source, destination]))	
		
		for p in processes:
			p.start()
		
		#for p in processes:
		#	p.join()
		self.total_size = self.get_size(source)
		ttk.Label(self.top, text=f'Source: {source}').grid(row=0, column=0, pady=5, sticky='NW')
		ttk.Label(self.top, text=f'Destination: {destination}').grid(row=1, column=0, pady=5, sticky='NW')
		size = int(self.total_size*0.001)
		ttk.Label(self.top, text=f'Total size: {size:,} KB').grid(row=2, column=0, pady=5, sticky='NW')
		self.l = ttk.Label(self.top, text='Progress: 0%')
		self.l.grid(row=3, column=0, pady=5, sticky='NW')
		
		self.pb1 = Progressbar(self.top, orient=HORIZONTAL, length=100, mode='determinate')
		self.pb1.grid(row=4, column=0, pady=5, sticky='NSEW')
		#self.check_progress()
		
	def get_size(self, folder):
		total_size = 0
		for dirpath, dirnames, filenames in os.walk(folder):
			for f in filenames:
				fp = os.path.join(dirpath, f)
				# skip if it is symbolic link
				if not os.path.islink(fp):
					total_size += os.path.getsize(fp)
		
		return total_size
		
	def check_progress(self):
		attempts = 0

		while True:
			attempts += 1
			time.sleep(1)
			current_size = self.get_size(self.destination)
			progress = round(current_size/self.total_size, 2)

			# if attempts > 30:
				# break
				
			if progress == 1.0:
				break
			else:
				self.l.config(text=f'Progress: {str(int(progress*100))}%')
				self.pb1['value'] = progress*100
				self.mainapp.root.update()
				
		self.top.destroy()