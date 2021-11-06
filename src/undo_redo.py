import collections
import os
from send2trash import send2trash
from tkinter import messagebox
import winshell 

class UndoRedo:
	def __init__(self, mainapp):
		self.mainapp = mainapp
		self.undo_stack = collections.deque(maxlen=10)
		self.reset_redo()
		
	def add_action_to_undo_stack(self, data):
		self.undo_stack.append(data)
		
	def undo(self, event=None):
		if len(self.undo_stack) > 0:
			msg = None
			
			# Undo Renaming of file #####################################################
			if self.undo_stack[-1]['action'] == 'rename_file':
				#Check file still exists
				if not os.path.isfile(self.undo_stack[-1]['new_name']):
					msg = f'Cannot undo renaming of file {self.undo_stack[-1]["new_name"]}, the file no longer exists, it may have been deleted by another program.'
					
				#Check original name exists
				if os.path.isfile(self.undo_stack[-1]['orig_name']):
					msg = f'Cannot undo renaming of file {self.undo_stack[-1]["new_name"]}, the original file currently exists.'
				
				if not msg:
					os.rename(self.undo_stack[-1]['new_name'], self.undo_stack[-1]['orig_name'])
				else:
					messagebox.showerror('Error', message=msg)
		
			# Undo Creation of New File ################################################
			if self.undo_stack[-1]['action'] == 'new_file':
				if not os.path.isfile(self.undo_stack[-1]['file_name']):
					msg = f'Cannot undo creation of file {self.undo_stack[-1]["file_name"]}, the file no longer exists, it may have been deleted by another program.'
				
				if not msg:
					send2trash(self.undo_stack[-1]['file_name'])
					r = winshell.recycle_bin()  # this lists the original path of all the all items in the recycling bin
					r = list(r.versions(self.undo_stack[-1]['file_name']))
					
					times = []
					for idx, file in enumerate(r):
						times.append(file.recycle_date())
						
					idx = times.index(max(times))
					for file in r:
						if file.recycle_date() == times[idx]:
							self.undo_stack[-1]['recycled_file'] = file
					
				else:
					messagebox.showerror('Error', message=msg)
			
			# Undo Creation of New Folders ################################################
			if self.undo_stack[-1]['action'] == 'new_folders':
				base_folder = self.undo_stack[-1]['base_folder']
				self.undo_stack[-1]['recycled_folders'] = []
				
				for folder in self.undo_stack[-1]['folder_names']:
					if os.path.isdir(os.path.join(base_folder, folder)):
						send2trash(os.path.join(base_folder, folder))
						
						r = winshell.recycle_bin()  # this lists the original path of all the all items in the recycling bin
						r = list(r.versions(os.path.join(base_folder, folder)))
						
						times = []
						for idx, file in enumerate(r):
							times.append(file.recycle_date())
							
						idx = times.index(max(times))
						for file in r:
							if file.recycle_date() == times[idx]:
								self.undo_stack[-1]['recycled_folders'].append(file)
				
			if not msg:
				try:
					self.undo_stack[-1]['branch_tab'].update_tab(self.undo_stack[-1]['branch_tab'].explorer.current_directory)
				except Exception as e:
					if 'is not managed by' in str(e): #tab has been deleted
						msg = 'Completed undo, however note the tab has been deleted'
					else:
						print(e)
						
				self.redo_stack.insert(0, self.undo_stack[-1])
				self.undo_stack.pop()
				
				if msg:
					messagebox.showerror('Error', message=msg)
			


	def redo(self, event=None):
		if len(self.redo_stack) > 0:
			msg = None
			
			# Redo Renaming of file #####################################################
			if self.redo_stack[0]['action'] == 'rename_file':
				#Check file still exists
				if not os.path.isfile(self.redo_stack[0]['orig_name']):
					msg = f'Cannot redo renaming of file {self.redo_stack[0]["orig_name"]}, the file no longer exists, it may have been deleted by another program.'
					
				#Check original name exists
				if os.path.isfile(self.redo_stack[0]['new_name']):
					msg = f'Cannot undo renaming of file {self.redo_stack[0]["orig_name"]}, the original file currently exists.'
				
				if not msg:
					os.rename(self.redo_stack[0]['orig_name'], self.redo_stack[0]['new_name'])
					self.redo_stack[0]['branch_tab'].update_tab(self.redo_stack[0]['branch_tab'].explorer.current_directory)
					self.undo_stack.append(self.redo_stack[0])
					self.redo_stack.popleft()
				else:
					messagebox.showerror('Error', message=msg)		
			
			# Redo Recycling of File ################################################
			if self.redo_stack[0]['action'] == 'new_file':
				r = list(winshell.recycle_bin())

				for idx, file in enumerate(r):
					if file.original_filename() == self.redo_stack[0]['recycled_file'].original_filename():
						if file.recycle_date() == self.redo_stack[0]['recycled_file'].recycle_date():
							winshell.undelete(r[idx].original_filename())

			# Redo Recycling of Folders ################################################
			if self.redo_stack[0]['action'] == 'new_folders':
				r = list(winshell.recycle_bin())
				
				for idx, file in enumerate(r):
					for folder in self.redo_stack[0]['recycled_folders']:
						if file.original_filename() == folder.original_filename():
							if file.recycle_date() == folder.recycle_date():
								winshell.undelete(r[idx].original_filename())
								
			if not msg:
				try:
					self.redo_stack[0]['branch_tab'].update_tab(self.redo_stack[0]['branch_tab'].explorer.current_directory)
				except Exception as e:
					if 'is not managed by' in str(e): #tab has been deleted
						msg = 'Completed undo, however note the tab has been deleted'
					else:
						print(e)

				self.undo_stack.append(self.redo_stack[0])
				self.redo_stack.popleft()
				
				if msg:
					messagebox.showerror('Error', message=msg)
			

	def reset_redo(self):
		self.redo_stack = collections.deque(maxlen=10)