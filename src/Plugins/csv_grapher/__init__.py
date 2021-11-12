import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *

import matplotlib.pyplot as plt

def initialise_plugin():
	show_in_right_click_menu = True
	run_on_files = True
	run_on_folders = False
	extension_filter = ['.csv']

	return locals()
	
class Plugin:
	def __init__(self, mainapp, master, plugin, file, *args, **kwargs):
		print(*args)
		self.mainapp = mainapp
		self.master = master
		self.plugin = plugin
		self.file = file
		self.read_csv()
		
		for idx, plugin in enumerate(self.mainapp.plugins):
			if plugin['name'] == self.plugin:
				self.plugin_idx = idx
				if 'plot_grid' not in plugin.keys():
					self.mainapp.plugins[idx]['plot_grid'] = 1
		
				self.plot_grid = self.mainapp.plugins[idx]['plot_grid']
				
		self.w = OptionsWindow(self.mainapp, self.master, self)
		self.master.wait_window(self.w.top)		
		
		if self.w.button == 'ok':
			self.plot_grid = self.w.plot_grid.get()
			self.mainapp.plugins[self.plugin_idx]['plot_grid'] = self.plot_grid 
			self.gen_plot()
			
	def read_csv(self):
		with open(self.file) as f:
			data = f.readlines()
			
		self.x = []
		self.y = []
		for row in data:
			row = row.split(',')
			self.x.append(int(row[0]))
			self.y.append(int(row[1]))
			
	def gen_plot(self):
		plt.plot(self.x, self.y)
		if self.plot_grid == 1:
			plt.grid()
		plt.show()
		
class OptionsWindow(ttk.Frame):
	def __init__(self, mainapp, master, plugin):
		super(OptionsWindow, self).__init__()
		top=self.top=Toplevel(master)
		#top.grab_set()
		self.mainapp = mainapp
		self.button = 'cancel'
		
		self.plot_grid = IntVar(value=plugin.plot_grid)
		ttk.Checkbutton(self.top, text="Include Grid", variable=self.plot_grid).grid(row=0, column=2, sticky='w', padx=5, pady=5)
		
		# Buttons
		self.ok_btn = ttk.Button(self.top, text='OK', width=10, style='success.TButton', command=lambda button='ok': self.cleanup(button))
		self.ok_btn.grid(row=2, column=0, padx=5, pady=5, sticky='ne')
		self.cancel_btn = ttk.Button(self.top, text='Cancel', width=10, style='danger.TButton', command=lambda button='cancel': self.cleanup(button))
		self.cancel_btn.grid(row=2, column=1, padx=5, pady=5, sticky='nw')	
		
	def cleanup(self, button):
		if button == 'ok':
				self.button = 'ok'
				self.top.destroy()
		else:
			self.top.destroy()