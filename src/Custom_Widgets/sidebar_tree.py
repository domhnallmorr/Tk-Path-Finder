import copy
import os
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import simpledialog
from tkinter import messagebox

from ttkbootstrap.themes import standard
import config_file_manager

class QuickAccessTreeview(ttk.Treeview):
	def __init__(self, mainapp, nodes=['Default']):
		super(QuickAccessTreeview, self).__init__(mainapp.sidebar_frame, selectmode='browse', show="tree") #check if this convention is right
		self.mainapp = mainapp
		#self.nodes = {n: None for n in nodes} #this is to keep track of the tree iids for each node
		#self.links = {self.nodes[node]: {} for node in self.nodes}
		
		self.links = copy.deepcopy(mainapp.config_data['links'])
		self.node_iids = copy.deepcopy(mainapp.config_data['node_iids'])
		self.nodes = copy.deepcopy(mainapp.config_data['nodes'])
		self.setup_nodes()
		self.setup_links()
		
		#bind left click event
		self.bind('<<TreeviewSelect>>',lambda event, : self.singleclick(event))
		self.bind("<Button-3>",lambda event,: self.onrightclick(event))
		self.bind("<Motion>", self.highlight_row)

		self.close_btn = tk.Button(mainapp.sidebar_frame, image=self.mainapp.close_icon2, background='white', relief=FLAT,
				command= lambda action=False: self.open_close_all_nodes(action))
		self.close_btn.grid(row=1, column=0, sticky='w', padx = 0)
		self.up_btn = tk.Button(mainapp.sidebar_frame, image=self.mainapp.up_icon2, background='white', relief=FLAT,
				command=self.move_up)
		self.up_btn.grid(row=1, column=1, sticky='w', padx = 0)
		self.down_btn = tk.Button(self.mainapp.sidebar_frame, image=self.mainapp.down_icon2, background='white', relief=FLAT,
				command=self.move_down)
		self.down_btn.grid(row=1, column=2, sticky='w', padx = 0)
		
		self.update_btn_bg()
		
		self.update_tags()
		
	def update_btn_bg(self):
		s = ttk.Style()
		bg = s.lookup('TFrame', 'background')
		
		self.close_btn.config(bg=bg)
		self.up_btn.config(bg=bg)
		self.down_btn.config(bg=bg)

	def update_tags(self):
		highlight_color = standard.STANDARD_THEMES[self.mainapp.style_name]["colors"]["active"]
		self.tag_configure('highlight', background=highlight_color)
		
	def highlight_row(self, event):
		item = self.identify_row(event.y)
		item = f'"{item}"'
		self.tk.call(self, "tag", "remove", "highlight")
		self.tk.call(self, "tag", "add", "highlight", item)
		
	def setup_nodes(self):
		self.node_iids = {}
		for node in self.nodes:
			#self.insert("",'end', node, text=node, image=self.mainapp.folder_icon2)
			iid = self.insert("",'end', self.nodes[node], text=node, image=self.mainapp.folder_icon2)
			self.nodes[node] = iid
			self.node_iids[iid] = node
	
	def setup_links(self):	
		for node in self.links.keys():
			for link in self.links[node].keys():
				self.insert(node,'end', text=link)
				
	def add_new_node(self, mode='new', event=None):
		initialvalue = ''
		if mode == 'edit':
			item_iid = event.widget.selection()[0]
			initialvalue = self.item(item_iid, 'text')

		node = simpledialog.askstring(title="New Node", prompt="Node Name:".ljust(100), initialvalue=initialvalue)
		if node:
			if mode == 'new': #add a new node
				iid = self.insert("",0, text=node, image=self.mainapp.folder_icon2)
				self.nodes[node] = iid
				self.node_iids[iid] = node
				self.links[iid] = {}
				self.update_links_data()
			else:
				current_text = self.item(item_iid, 'text')
				self.item(item_iid, text=node)
				
				self.node_iids[item_iid] = node
				self.nodes[node] = item_iid
				self.nodes.pop(current_text)
				
			config_file_manager.write_config_file(self.mainapp)

	def edit_node(self, event):
		self.add_new_node(mode='edit', event=event)
		
	def singleclick(self, event, click='single'):
		if click == 'single':
			item_iid = event.widget.selection()[0]
			parent_iid = event.widget.parent(item_iid)
			
			if parent_iid: #if it is a link and not a node
				node = event.widget.item(parent_iid, 'text')
				link = event.widget.item(item_iid, 'text')
				path = self.links[self.nodes[node]][link]
				
				current_root_tab = self.mainapp.notebook.nametowidget(self.mainapp.notebook.select())
				current_branch_tab = current_root_tab.notebook.nametowidget(current_root_tab.notebook.select())
				current_branch_tab.update_tab(path)

	def onrightclick(self, event):
		self.unbind("<Button 1>")
		# select row under mouse
		iid = self.identify_row(event.y)
		if iid:
			# mouse pointer over item
			self.selection_set(iid)
			self.bind('<<TreeviewSelect>>',lambda event, click='right': self.singleclick(event, click))
			
		popup_menu = tk.Menu(event.widget, tearoff=0)
		popup_menu.add_command(label="Add New Node", command=event.widget.add_new_node, image=self.mainapp.plus_icon2, compound='left',)

		item_iid = event.widget.selection()[0]
		parent_iid = event.widget.parent(item_iid)
		
		if not parent_iid: #if it is a node and not a link
			popup_menu.add_command(label="Edit Node", command=lambda event=event: event.widget.edit_node(event), image=self.mainapp.edit_icon2, compound='left',)
			popup_menu.add_command(label="Delete Node", command=lambda event=event: event.widget.delete_node(event), image=self.mainapp.delete_icon2, compound='left',)
			popup_menu.add_separator()
			popup_menu.add_command(label="Add New Link", command=lambda event=event, mode='new': event.widget.add_link(event, mode), image=self.mainapp.new_link_icon2, compound='left',)
		else:
			popup_menu.add_separator()
			popup_menu.add_command(label="Edit Link", command=lambda event=event, mode='edit': event.widget.add_link(event, mode), image=self.mainapp.edit_link_icon2, compound='left',)
			popup_menu.add_command(label="Delete Link", command=lambda event=event: event.widget.delete_link(event), image=self.mainapp.delete_link_icon2, compound='left',)
		
		try:
			popup_menu.tk_popup(event.x_root, event.y_root, 0)
		finally:
			popup_menu.grab_release()
		
		self.bind('<<TreeviewSelect>>',lambda event, click='single': self.singleclick(event, click))

	def add_link(self, event, mode):
		#Get the Node
		item_iid = event.widget.selection()[0]
		parent_iid = event.widget.parent(item_iid)	
		if parent_iid:
			node = parent_iid
		else:
			node = item_iid
			
		if mode == 'edit':
			item_iid = event.widget.selection()[0]
			parent_iid = event.widget.parent(item_iid)
			name = self.item(item_iid, 'text')
			path = self.links[parent_iid][name]
		else:
			name = ''
			path = ''
			
		self.w=AddLinkWindow(self.mainapp, self.master, mode, node, name=name, path=path)
		self.master.wait_window(self.w.top)
		
		if self.w.button == 'ok':
			if mode == 'new':
				item_iid = event.widget.selection()[0]
				iid = self.insert(item_iid,'end', text=self.w.name)
				self.links[item_iid][self.w.name] = self.w.path
			else:
				self.item(item_iid, text=self.w.name)
				del self.links[parent_iid][name]
				self.links[parent_iid][self.w.name] = self.w.path
			config_file_manager.write_config_file(self.mainapp)

	def delete_node(self, event):
		msg = messagebox.askyesno(title='Delete Link', message='Are you sure you want to delete this link? All links will be lost! This cannot be undone!')
		if msg:
			item_iid = self.focus()	
			self.detach(item_iid)
			del self.links[item_iid]
			del self.node_iids[item_iid]
			for n in self.nodes:
				if self.nodes[n] == item_iid:
					del self.nodes[n]
					break
			config_file_manager.write_config_file(self.mainapp)
			
	def delete_link(self, event):
		msg = messagebox.askyesno(title='Delete Link', message='Are you sure you want to delete this link? This cannot be undone!')
		if msg:
			item_iid = event.widget.selection()[0]
			parent_iid = event.widget.parent(item_iid)
			
			self.detach(item_iid)
			name = self.item(item_iid, 'text')
			del self.links[parent_iid][name]
			config_file_manager.write_config_file(self.mainapp)

	def open_close_all_nodes(self, action):
		for node in self.get_children():
			self.item(node, open=action)

	def move_up(self):
		leaves = self.selection()
		for i in leaves:
			self.move(i, self.parent(i), self.index(i)-1)
		
		self.update_links_data()

	def move_down(self):
		leaves = self.selection()
		for i in leaves:
			self.move(i, self.parent(i), self.index(i)+1)

		self.update_links_data()
		
	def update_links_data(self):
		nodes = {}
		for node in self.get_children():
			nodes[self.item(node, 'text')] = node
		
		self.nodes = copy.deepcopy(nodes)
		del nodes
		config_file_manager.write_config_file(self.mainapp)
		
class AddLinkWindow(ttk.Frame):
	def __init__(self, mainapp, master, mode, node, name='', path='',):
		super(AddLinkWindow, self).__init__()
		top=self.top=Toplevel(master)
		top.grab_set()
		self.mainapp = mainapp
		self.node = node

		self.mode = mode	
		self.top.title(f"Add New Link")
		self.button = 'cancel'
		
		ttk.Label(self.top, text='Name:').grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
		ttk.Label(self.top, text='Path:').grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
		
		self.name_entry = ttk.Entry(self.top, width=100)
		self.name_entry.grid(row=0, column=1, columnspan=4, padx=5, pady=5, sticky='nsew')
		
		self.path_entry = ttk.Entry(self.top, width=100)
		self.path_entry.grid(row=1, column=1, columnspan=4, padx=5, pady=5, sticky='nsew')
		
		self.ok_btn = ttk.Button(self.top, text='OK', width=10, style='success.TButton', command=lambda button='ok': self.cleanup(button))
		self.ok_btn.grid(row=2, column=0, padx=5, pady=5, sticky='ne')
		self.cancel_btn = ttk.Button(self.top, text='Cancel', width=10, style='danger.TButton', command=lambda button='cancel': self.cleanup(button))
		self.cancel_btn.grid(row=2, column=1, padx=5, pady=5, sticky='nw')
		
		if mode == 'edit':
			self.name_entry.insert(0, name)
			self.path_entry.insert(0, path)
			self.original_name = name
				
	def cleanup(self, button):
		if button == 'ok':
			self.name = self.name_entry.get().strip()
			self.path = self.path_entry.get()
			data_ok = True
			
			if self.name == '':
				messagebox.showerror('Error', message='Enter A Name')
				data_ok = False
				
			elif self.name in self.mainapp.quick_access_tree.links[self.node].keys():
				name_msg = 'Name Entered Already Exists Under Selected Node, Choose Another Name'
				if self.mode == 'edit' and self.name != self.original_name:
					messagebox.showerror('Error', message=name_msg)
					data_ok = False
				elif self.mode == 'new':
					messagebox.showerror('Error', message=name_msg)
					data_ok = False
					
			elif not os.path.isdir(self.path):
				messagebox.showerror('Error', message='The Path Entered Does Not Exist')
				data_ok = False
				
			if data_ok:	
				# For mapped drive, handle for inclusion of trailing \ e.g C:\
				if len(self.path) == 2 and self.path[-1] == ':':
					self.path = self.path + '\\'
				self.button = button
				self.top.destroy()
		else:
			self.top.destroy()
			

		
		