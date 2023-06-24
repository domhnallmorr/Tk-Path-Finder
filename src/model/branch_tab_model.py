import collections
from datetime import datetime
import os
import subprocess
import re

from natsort import natsorted, ns, os_sorted

class BranchTabModel:
	def __init__(self, model, id_key, current_directory, root_id, default_text):
		self.model = model
		self.id_key = id_key
		self.root_id = root_id
		self.text = default_text
		self.setup_variables()
		self.current_directory = current_directory
		
		self.list_directory(self.current_directory)
	
	def setup_variables(self):
		if self.text is None:
			self.text_locked = False # If text should update to folder name when user switches folder
		else:
			self.text_locked = True
		self.directory_data = []
		self.filter_type = None # filter by extension or filename
		self.filter = [] # the file extensions that will be removed from view, or the text to search for in files
		self.lock_filter = False
		self.filter_text = ""

		self.previous_directories = collections.deque(maxlen=10)
		self.forward_directories = collections.deque(maxlen=10)
		self.special_characters = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']	
		
		self.default_folder_selected = None
		
	def assemble_view_data(self):
		# Remove any filtered out extensions
		if self.filter != []:
			file_data = []
			
			for file in self.file_data:
				filename, file_extension = os.path.splitext(file[0])
				
				if self.filter_type == "extension":
					if file_extension not in self.filter:
						file_data.append(file)
				
				elif self.filter_type == "name":
					if self.filter[0] in filename:
						file_data.append(file)		
		else:
			file_data = self.file_data
		
		return {"id": self.id_key, "current_directory": self.current_directory, "tabular_data": self.directory_data + file_data,
				"text_locked": self.text_locked, "text": self.text, "len_filter": len(self.filter), "file_data": file_data,
				"directory_data": self.directory_data, "lock_filter": self.lock_filter, "filter_text": self.filter_text,
				"no_previous_directories": len(self.previous_directories), "no_forward_directories": len(self.forward_directories),
				"default_folder_selected": self.default_folder_selected}

	def directory_changed(self, directory):
		self.list_directory(directory=directory)
	
	def list_directory(self, directory=None, mode="normal", sort=None):
		file_data = ""
		msg = None
		directory_data = []
		file_data = []
		
		self.default_folder_selected = None
		
		# RESET FILTER IF REQUIRED
		if mode != "refresh":
			if self.lock_filter is False:
				self.filter = []
		
		data = subprocess.run(f'chcp 65001 | dir "{directory}"', shell=True, stdout=subprocess.PIPE).stdout.splitlines()

		if data == [] or len(data) == 5: #empty list means something has gone wrong
			try:
				msg = subprocess.check_output(['dir', 'E:\\'], stderr=subprocess.STDOUT)
			except Exception as e:
				msg = str(e)
			
		elif type(data) is list:
			data = data[5:-2]
			for d in data:
				d = d.decode("utf-8") 
				
				if '<DIR>' in d:
					d = d.split('<DIR>')
					if d[-1].strip() != '.' and d[-1].strip() != '..':
						directory_data.append([d[-1].strip(), '-', 'Folder', '-'])
				else:
					d = re.split("(?<!\s) ", d)
					filename = ' '.join(d[3:])
					try:
						size = int(int(d[2].replace(',', ''))*0.001)
					except:
						size = 'N/A'
						
					if sort == 'size' or size == 'N/A':
						file_data.append([filename, f'{d[0]} {d[1]}', self.model.get_file_type(filename), size])
					else:
						file_data.append([filename, f'{d[0]} {d[1]}', self.model.get_file_type(filename), f'{size:,} KB'])

			if mode == "normal":
				if self.current_directory != directory:
					self.previous_directories.append(self.current_directory)
					self.forward_directories.clear()
			elif mode == 'back': # when user clicks back arrow button
				self.previous_directories.pop()
				self.forward_directories.appendleft(self.current_directory)
			elif mode == 'fwd':
				self.forward_directories.popleft()
				self.previous_directories.append(self.current_directory)
		

		# Determine what the default folder to be selected is (if the user clicks up button, in the treeview, select the folder they were in)
		for new_dir in directory_data:
			if os.path.normpath(f"{directory}\\{new_dir[0]}") == os.path.normpath(self.current_directory): # normpath handles for inconsistent use of slashes
				self.default_folder_selected = new_dir[0]
				break
		
		directory_data = natsorted(directory_data, alg=ns.IGNORECASE)
		file_data = natsorted(file_data, alg=ns.IGNORECASE)
		# Sorting
		if sort == 'date':
			directory_data = list(reversed(sorted(directory_data, key=lambda x: x[1])))

			# add date time data
			for idx, file in enumerate(file_data):
				dt_object1 = datetime.strptime(file[1], "%d/%m/%Y %H:%M")
				file_data[idx].append(dt_object1)
			
			file_data = list(reversed(sorted(file_data, key=lambda x: x[-1])))
			file_data = [f[:-1] for f in file_data] # remove dt_object1
			
		elif sort == 'file_type':
			directory_data = list(reversed(sorted(directory_data, key=lambda x: x[2])))
			file_data = list(reversed(sorted(file_data, key=lambda x: x[2])))
			
		elif sort == 'size':
			directory_data = list(reversed(sorted(directory_data, key=lambda x: x[3])))
			file_data = list(reversed(sorted(file_data, key=lambda x: x[3])))
			for f in file_data:
				f[-1] = f'{int(f[-1]):,} KB'
		
		# ----------- HANDLE IF SUBPROCESS RETURNED A STRING ---------------
		if isinstance(directory_data, str):
			msg = directory_data
			
		if msg is None:
			self.current_directory = directory
				
			self.directory_data = directory_data
			self.file_data = file_data
			
			if self.text_locked is False:
				self.text = os.path.basename(os.path.normpath(self.current_directory))

		return msg
		
	def get_file_extensions(self):
		file_extensions = {}
		for file in self.file_data:
			if file[2] != "Folder":
				filename, file_extension = os.path.splitext(file[0])
				if file_extension in self.model.known_file_types.keys():
					description = self.model.known_file_types[file_extension]
				else:
					description = f"{file_extension} file"
				
				if file_extension in self.filter:
					initialvalue = 0
				else:
					initialvalue = 1

				file_extensions[file_extension] = {"description": description, "var": initialvalue}
			
		return file_extensions
		
	def update_filter(self, filter, lock_filter, filter_type):
		self.lock_filter = lock_filter
		self.filter = filter
		self.filter_type = filter_type

		if self.filter_type == "name":
			self.filter_text = self.filter[0]
	
	def show_only_extension_type(self, extension, mode):
		self.filter = []
		
		if mode != "remove_filter":
			self.filter_type = "extension"
			
			for file in self.file_data:
				filename, file_extension = os.path.splitext(file[0])
				
				if mode == "hide_this":
					if file_extension == extension and file_extension not in self.filter:
						self.filter.append(file_extension)

				elif mode == "show_this":
					if file_extension != extension and file_extension not in self.filter:
						self.filter.append(file_extension)
					
	def get_forward_and_previous_current_directories(self):
		return self.forward_directories, self.previous_directories, self.current_directory