import collections
import os
import subprocess
import time
import datetime

class FileExplorerBackend:
	def __init__(self, mainapp):
		self.mainapp = mainapp
		self.current_directory = self.get_default_directory()
		self.previous_directories = collections.deque(maxlen=10)
		self.forward_directories = collections.deque(maxlen=10)
		self.special_characters = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
		
	def get_default_directory(self):
		return os.getcwd()
		
	def list_directory(self, directory=None, mode=None):	
		if directory == None:
			directory = self.current_directory
		try:
			# Handle Directories
			directory_data = []
			files_dirs = os.listdir(directory)
			directories = [o for o in files_dirs if os.path.isdir(os.path.join(directory,o))]
			for d in directories:
				directory_data.append([d, '-', 'Folder', '-'])

			# Handle Files
			file_data = []
			files = [o for o in files_dirs if not os.path.isdir(os.path.join(directory,o))]
			for f in files:
				full_path = os.path.join(directory,f)
				
				size = os.path.getsize(full_path)*0.001 # in kb
				
				modified = os.path.getmtime(full_path)
				modified = datetime.datetime.fromtimestamp(modified)
				
				file_data.append([f, modified.strftime("%d/%m/%Y, %H:%M:%S"), self.get_file_type(f), f'{int(size):,} KB'])
				#file_data.append([f, '-', 'File', '-'])
			if mode == None:
				if self.current_directory != directory:
					self.previous_directories.append(self.current_directory)
					self.forward_directories.clear()
			elif mode == 'back': # when user clicks back arrow button
				self.previous_directories.pop()
				self.forward_directories.appendleft(self.current_directory)
			elif mode == 'fwd':
				self.forward_directories.popleft()
				self.previous_directories.append(self.current_directory)
				
			self.current_directory = directory
			
		except PermissionError:
			directory_data = 'Permission Denied'
			file_data = ''
		except Exception as e:
			print(e)
			directory_data = 'An Error Ocurred'
			file_data = ''
			if not os.path.isdir(directory):
				directory_data = 'Location Does Not Exist'
				file_data = ''
			
		return directory_data + file_data
		
	def get_file_type(self, filename):
		filename, file_extension = os.path.splitext(filename)
		file_type = 'file'
		icon = self.mainapp.new_icon2
		
		if file_extension in self.mainapp.known_file_types.keys():
			file_type = self.mainapp.known_file_types[file_extension][0]
		return file_type
		
	# def double_clicked_on_directory(self, directory):
		# self.previous_directories.append(self.current_directory)
		# self.current_directory = os.path.join(self.current_directory, directory)
		
	def double_clicked_on_file(self, file):
		os.startfile(os.path.join(self.current_directory, file))
		#subprocess.run(['open', os.path.join(self.current_directory, file)], check=True)

		
	def address_bar_updateed(self, directory):
		if os.path.isdir(directory):
			self.current_directory = directory
	
	def up_one_level(self):
		return os.path.dirname(self.current_directory)
		
	def update_explorer(self):
		pass
		
	def new_folders(self, folders):
		print(folders)
		
		for folder in folders:
			os.makedirs(os.path.join(self.current_directory, folder))
			
	def check_special_characters(self, string_to_check):
		msg = None
		for character in self.special_characters:
			if character in string_to_check:
				msg = f'Character {character} is not allowed!'
				break
		return msg
				