import collections
import copy
import os
import subprocess
from subprocess import DEVNULL
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
		
	# def list_directory(self, directory=None, mode=None, sort=None):	
		# if directory == None:
			# directory = self.current_directory
		# try:
			# # Handle Directories
			# directory_data = []
			# files_dirs = os.listdir(directory)
			
			# if len(files_dirs) > 200:
				# directories = [o for o in files_dirs if os.path.isdir(os.path.join(directory,o))]
				# for d in directories:
					# directory_data.append([d, '-', 'Folder', '-'])

				# # Handle Files
				# file_data = []
				# files = [o for o in files_dirs if not os.path.isdir(os.path.join(directory,o))]
				# for f in files:
					# full_path = os.path.join(directory,f)
					
					# size = os.path.getsize(full_path)*0.001 # in kb
					
					# modified = os.path.getmtime(full_path)
					# modified = datetime.datetime.fromtimestamp(modified)
					
					# if sort != 'size':
						# file_data.append([f, modified.strftime("%d/%m/%Y, %H:%M:%S"), self.get_file_type(f), f'{int(size):,} KB'])
					# else:
						# file_data.append([f, modified.strftime("%d/%m/%Y, %H:%M:%S"), self.get_file_type(f), int(size)])
						
			# else:
				# # Large Folders
				# data = subprocess.run(f'dir "{directory}"', shell=True, stdout=subprocess.PIPE).stdout.splitlines()
				# data = data[5:-2]
				# directory_data = []
				# file_data = []
				# for d in data:
					# d= d.decode("utf-8") 
					
					# if '<DIR>' in d:
						# d = d.split('<DIR>')
						# if d[-1].strip() != '.' and d[-1].strip() != '..':
							# directory_data.append([d[-1].strip(), '-', 'Folder', '-'])
					# else:
						# d = d.split()
						# file_data.append([' '.join(d[3:]), '-', 'File', '-'])
		
				# #file_data.append([f, '-', 'File', '-'])
			# if mode == None:
				# if self.current_directory != directory:
					# self.previous_directories.append(self.current_directory)
					# self.forward_directories.clear()
			# elif mode == 'back': # when user clicks back arrow button
				# self.previous_directories.pop()
				# self.forward_directories.appendleft(self.current_directory)
			# elif mode == 'fwd':
				# self.forward_directories.popleft()
				# self.previous_directories.append(self.current_directory)
			
			# if sort == 'date':
				# directory_data = list(reversed(sorted(directory_data, key=lambda x: x[1])))
				# file_data = list(reversed(sorted(file_data, key=lambda x: x[1])))
			# elif sort == 'file_type':
				# directory_data = list(reversed(sorted(directory_data, key=lambda x: x[2])))
				# file_data = list(reversed(sorted(file_data, key=lambda x: x[2])))
			# elif sort == 'size':
				# directory_data = list(reversed(sorted(directory_data, key=lambda x: x[3])))
				# file_data = list(reversed(sorted(file_data, key=lambda x: x[3])))
				# for f in file_data:
					# f[-1] = f'{int(f[-1]):,} KB'
				
			# self.current_directory = directory
			
		# except PermissionError:
			# directory_data = 'Permission Denied'
			# file_data = ''
		# except Exception as e:
			# print(e)
			# directory_data = 'An Error Ocurred'
			# file_data = ''
			# if not os.path.isdir(directory):
				# directory_data = 'Location Does Not Exist'
				# file_data = ''

		# #for i in file_data:
		# #	directory_data.append(i)
			
		# return directory_data + file_data

	def list_directory(self, directory=None, mode=None, sort=None):
		file_data = ''
		
		if os.path.isdir(directory):
			data = subprocess.run(f'dir "{directory}"', shell=True, stdout=subprocess.PIPE).stdout.splitlines()
			
			if type(data) is list:
				data = data[5:-2]
				directory_data = []
				file_data = []
				for d in data:
					d= d.decode("utf-8") 
					
					if '<DIR>' in d:
						d = d.split('<DIR>')
						if d[-1].strip() != '.' and d[-1].strip() != '..':
							directory_data.append([d[-1].strip(), '-', 'Folder', '-'])
					else:
						d = d.split()
						filename = ' '.join(d[3:])
						size = int(int(d[2].replace(',', ''))*0.001)
						if sort == 'size':
							file_data.append([filename, f'{d[0]} {d[1]}', self.get_file_type(filename), size])
						else:
							file_data.append([filename, f'{d[0]} {d[1]}', self.get_file_type(filename), f'{size:,} KB'])

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

			# Sorting
			if sort == 'date':
				directory_data = list(reversed(sorted(directory_data, key=lambda x: x[1])))
				file_data = list(reversed(sorted(file_data, key=lambda x: x[1])))
			elif sort == 'file_type':
				directory_data = list(reversed(sorted(directory_data, key=lambda x: x[2])))
				file_data = list(reversed(sorted(file_data, key=lambda x: x[2])))
			elif sort == 'size':
				directory_data = list(reversed(sorted(directory_data, key=lambda x: x[3])))
				file_data = list(reversed(sorted(file_data, key=lambda x: x[3])))
				for f in file_data:
					f[-1] = f'{int(f[-1]):,} KB'
					
			self.current_directory = directory
		else:
			directory_data = 'Location Does Not Exist'
				
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
		for folder in folders:
			os.makedirs(os.path.join(self.current_directory, folder))
			
	def check_special_characters(self, string_to_check):
		msg = None
		for character in self.special_characters:
			if character in string_to_check:
				msg = f'Character {character} is not allowed!'
				break
		return msg
		
	def open_in_cmd(self):
		subprocess.Popen("start /wait cmd.exe", cwd=self.current_directory, shell=True, stdout=DEVNULL)
				