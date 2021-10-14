import os
import subprocess

class FileExplorerBackend:
	def __init__(self, mainapp):
		self.current_directory = self.get_default_directory()
		#self.previous_directories = []
		
	def get_default_directory(self):
		return os.getcwd()
		
	def list_directory(self):
		# Handle Directories
		directory_data = []
		files_dirs = os.listdir(self.current_directory)
		directories = [o for o in files_dirs if os.path.isdir(os.path.join(self.current_directory,o))]
		for d in directories:
			directory_data.append([d, '-', 'Folder', ''])

		# Handle Files
		file_data = []
		files = [o for o in files_dirs if not os.path.isdir(os.path.join(self.current_directory,o))]
		for f in files:
			file_data.append([f, '-', 'File', ''])
			
		return directory_data + file_data
		
	def get_file_type(self, filename):
		filename, file_extension = os.path.splitext(filename)
		print(file_extension)
		file_type = 'file'
		
		return file_type
		
	def setup_file_type_dict(self):
		self.known_file_types = {'.exe': 'application'}
		
	def double_clicked_on_directory(self, directory):
		#self.previous_directories.append(self.current_directory)
		self.current_directory = os.path.join(self.current_directory, directory)
		
	def double_clicked_on_file(self, file):
		os.startfile(os.path.join(self.current_directory, file))
		print(os.path.join(self.current_directory, file))
		#subprocess.run(['open', os.path.join(self.current_directory, file)], check=True)

		
	def address_bar_updateed(self, directory):
		print('bar updated')
		print(directory)
		if os.path.isdir(directory):
			self.current_directory = directory
			print('dsd')
	
	def up_one_level(self):
		self.current_directory = os.path.dirname(self.current_directory)
		
	def update_explorer(self):
		pass