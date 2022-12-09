import copy
from distutils.dir_util import copy_tree
import os
import pathlib
from shutil import copyfile, move
import pythoncom
from win32com.shell import shell
import subprocess
from subprocess import DEVNULL
import threading

from docx import Document
from openpyxl import Workbook
import pyperclip
from ttkbootstrap import Style
from ttkbootstrap.themes import standard

from model import model
from view import view, diary_window, filter_windows, new_folders_window, pdf_tools_windows, rename_window, settings_window
from view import link_window, search_window, todo_list

class Controller:
	def __init__(self, root, parent, mainapp):
		self.mainapp = mainapp
		self.model = model.Model()
		self.view = view.View(root, parent, self, self.model.config_data)
		self.setup_quick_access_tree()
		
		self.special_characters = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
		
		# ________ ADD DEFAULT ROOT TAB ________
		self.add_root_tab()
		
		self.file_to_cut = None
		self.file_to_copy = None
		
	def add_root_tab(self, default_branch_tab=True, default_text=None):
		root_id = self.model.add_root_tab(default_text)
		self.view.add_root_tab(root_id, self.model.get_root_tab_text(root_id))
		
		if default_branch_tab is True:
			self.add_branch_tab(root_id)
			
		return root_id
			
	def add_branch_tab(self, root_id, default_text=None, default_directory=None):
		if default_directory is None:
			default_directory = os.getcwd()
			
		# ----------------- ADD A SINGLE DEFAULT BRANCH TAB -----------------
		id_key = self.model.add_branch_tab(root_id, default_text, default_directory)
		
		self.view.add_branch_tab(id_key, self.model.get_branch_tab_text(id_key), root_id)
		
		# ----------------- UPDATE BRANCH TAB VIEW -----------------
		self.view.update_branch_tab(copy.deepcopy(self.model.branch_tabs[id_key].assemble_view_data()))
		self.update_branch_tab(id_key, default_directory)
	
	def update_branch_tab(self, branch_id, directory, mode="normal", sort=None):
		msg = self.model.branch_tabs[branch_id].list_directory(directory=directory, mode=mode, sort=sort)
		
		if msg is None:
			# ------------------ IF NO ERROR OCCURRED UPDATE THE TAB -----------------
			data = self.model.branch_tabs[branch_id].assemble_view_data()
			self.view.update_branch_tab(copy.deepcopy(data))
			self.model.update_branch_tab_session_data(branch_id) # update session_data
			
		else:
			# ------------------ SHOW ERROR MESSAGE ------------------
			self.view.show_error(msg)

	def refresh_tab(self, branch_id, sort=None):
		current_directory = self.model.branch_tabs[branch_id].current_directory
		self.update_branch_tab(branch_id, current_directory, mode="refresh", sort=sort)
		
	def change_directory(self, branch_id, directory):
		current_directory = self.model.branch_tabs[branch_id].current_directory
		directory = os.path.join(current_directory, directory)
		self.update_branch_tab(branch_id, directory, mode="normal")
	
	def link_clicked(self, folder_id, link_id, branch_id):
		directory = self.model.quick_access_tree_model.get_link_directory(folder_id, link_id)
		self.change_directory(branch_id, directory)
	
	def back_one_level(self, branch_id):
		# ------------------ GET THE PREVIOUS DIRECTORY ------------------
		directory = self.model.branch_tabs[branch_id].previous_directories[-1]
		
		# ------------------ UPDATE BRANCH TAB ------------------
		self.update_branch_tab(branch_id, directory, mode="back")
		
	def fwd_one_level(self, branch_id):
		# ------------------ GET THE FORWARD DIRECTORY ------------------
		directory = self.model.branch_tabs[branch_id].forward_directories[0]
		
		# ------------------ UPDATE BRANCH TAB ------------------
		self.update_branch_tab(branch_id, directory, mode="fwd")		
			
	def up_one_level(self, branch_id):
		# ------------------ GET THE FORWARD DIRECTORY ------------------
		directory = os.path.dirname(self.model.branch_tabs[branch_id].current_directory)
		
		# ------------------ UPDATE BRANCH TAB ------------------
		self.update_branch_tab(branch_id, directory, mode="normal")

	def double_clicked_file(self, branch_id, file_name):
		current_directory = self.model.branch_tabs[branch_id].current_directory
		file = os.path.join(current_directory, file_name)
		
		msg = None
		try:
			os.startfile(file)
		except Exception as e:
			if "No application is associated" in str(e):
				msg = "There is no default application associated with this file type"
				
			else:
				msg == f"The Following Error Occured\n{msg}"
				
		if msg is not None:
			self.view.show_error(msg)

	def delete_root_tab(self, root_id):
		number_of_root_tabs = len(list(self.model.root_tabs.keys()))
		
		if number_of_root_tabs == 1:
			self.view.show_error("Cannot Delete Root Tab as There Must Always be 1 Root Tab Present")
		else:
			self.model.delete_root_tab(root_id)
			self.view.delete_root_tab(root_id)
		
	def delete_branch_tab(self, root_id, branch_id):
		number_of_branch_tabs = self.model.get_number_of_branch_tabs(root_id)
		
		if number_of_branch_tabs == 1:
			self.view.show_error("Cannot Delete Branch Tab as There Must Always be 1 Branch Tab Present in a Root Tab")
		else:
			self.model.delete_branch_tab(root_id, branch_id)
			self.view.delete_branch_tab(branch_id)
			
	def duplicate_branch_tab(self, root_id, branch_id):
		default_directory = self.model.get_branch_tab_directory(branch_id)
		default_text = self.model.get_branch_tab_text(branch_id)
		self.add_branch_tab(root_id, default_text=default_text, default_directory=default_directory)

	def rename_root_tab(self, root_id):
		initialvalue = self.model.root_tabs[root_id]["text"]

		self.w=rename_window.RenameWindow(self.mainapp.master, self.view, initialvalue, component_type="root_tab")
		self.mainapp.master.wait_window(self.w.top)
			
		if self.w.button == "ok":
			self.model.rename_root_tab(root_id, self.w.name)
			self.view.update_root_tab_text(root_id, self.w.name)
			
	def rename_branch_tab(self, branch_id):
		initialvalue = self.model.branch_tabs[branch_id].text
		self.w = rename_window.RenameWindow(self.mainapp.master, self.view, initialvalue, component_type="branch_tab")
		self.mainapp.master.wait_window(self.w.top)
			
		if self.w.button == "ok":
			self.model.rename_branch_tab(branch_id, self.w.name, self.w.text_locked)
			
			data = self.model.branch_tabs[branch_id].assemble_view_data()
			self.view.update_branch_tab(copy.deepcopy(data), mode="rename")
			self.model.update_branch_tab_session_data(branch_id)
			
	def edit_settings(self):
		self.w = settings_window.SettingsWindow(self.mainapp.master, self.view, copy.deepcopy(self.model.config_data))
		self.mainapp.master.wait_window(self.w.top)
		
		if self.w.button == "ok":
			self.model.update_config_data(self.w.config_data)
			
			# update view settings
			self.view.default_file_width = self.model.config_data["default_file_width"]
			self.view.default_date_width = self.model.config_data["default_date_width"]
			self.view.default_type_width = self.model.config_data["default_type_width"]
			self.view.default_size_width = self.model.config_data["default_size_width"]
		
	def open_file_clicked(self, branch_id, file_name, app=None):
		full_path = os.path.join(self.model.branch_tabs[branch_id].current_directory, file_name)
		
		if app is None:
			if self.model.text_editor:
				app = self.model.text_editor
			else:
				self.view.show_error("Default Text Editor has not been Defined")		
		
		if app:
			threading.Thread(target=lambda app=app, file=full_path:self.open_with_app(app, file)).start()

	def open_with_app(self, app, file):
		try:
			subprocess.call([app, file])
		except Exception as e:
			msg = str(e)
			if "cannot find the file" in msg:
				msg = f'The app "{app}" cannot be found'
			self.view.show_error(f"The following error occured\n\n {msg}")
			
	def get_open_with_apps(self):
		return self.model.config_data["open_with_apps"]
		
	def new_edit_file_folder(self, mode, initialvalue, branch_id):
		while True:
			self.w = rename_window.RenameWindow(self.mainapp.master, self.view, initialvalue, component_type="file", mode=mode)
			self.mainapp.master.wait_window(self.w.top)

			if self.w.button == "ok":
				msg = None
				name_input = self.w.name # the name the user entered
				current_directory = self.model.branch_tabs[branch_id].current_directory
				
				if name_input == initialvalue:
					break
				else:
					# ------------- CHECK USER INPUT IS VALID -------------
					# ------------- CHECK FOR ILLegal CHARACTERS
					for charecter in self.special_characters:
						if charecter in name_input:
							msg = f"Illegal Character {charecter} Found!"
							break
					
					# ------------- MAKE SURE FILE DOES NOT EXIST ALREADY
					if mode in ["new_file", "new_excel", "new_word"]:
						if os.path.isfile(os.path.join(current_directory, name_input)) or os.path.isdir(os.path.join(current_directory, name_input)):
							msg = "That File/Folder Already Exists"
							
					# ------------- CHECK EXCEL EXTENSION IS OK
					if mode == "new_excel":
						if name_input.endswith(".xlsx") is False:
							msg = "Excel File Extension Must be .xlsx"

					# ------------- CHECK WORD EXTENSION IS OK
					if mode == "new_word":
						if name_input.endswith(".docx") is False:
							msg = "Word File Extension Must be .docx"
							
					if not msg: # if user input is valid
						try:
							# ------------- RENAME EXISTING FILE -------------
							if mode == "edit_file" or mode == "edit_folder":
								self.rename_file(initialvalue, name_input, current_directory)
							
							# ------------- NEW FILE -------------						
							elif mode == "new_file":
								with open(os.path.join(current_directory, name_input), "w") as f:
									f.write("")
							
							# ------------- NEW EXCEL FILE -------------
							elif mode == "new_excel":
								wb = Workbook()
								wb.save(os.path.join(current_directory, name_input))
							
							# ------------- NEW WORD FILE -------------
							elif mode == "new_word":
								document = Document()
								document.save(os.path.join(current_directory, name_input))
								
							# ------------- REFRESH THE VIEW -------------
							self.update_branch_tab(branch_id, current_directory, mode="normal")
							break
						except Exception as e:
							self.view.show_error(f"The following error occured:\n{str(e)}")
						
					else:
						self.view.show_error(msg)
						initialvalue = name_input
			else: # user clicked cancel
				break
				
	def rename_file(self, initialvalue, new_name, current_directory):
		try:
			os.rename(os.path.join(current_directory, initialvalue), os.path.join(current_directory, new_name))
		except Exception as e:
			if "being used by another" in str(e).lower():
				msg = "Permission Denied, Ensure Document is not Open in Another Process"
			elif "access is denied" in str(e).lower():
					msg = "Access Denied"
			else:
				msg = f"The Following Error Occured\n{str(e)}"
				
			self.view.show_error(msg)
			
	def copy_to_clipboard(self, file_name, branch_id, mode):
		if mode == "full":
			current_directory = self.model.branch_tabs[branch_id].current_directory
			pyperclip.copy(os.path.join(current_directory, file_name))
		elif mode == "file_name_only":
			pyperclip.copy(file_name)
					
	def new_folders(self, branch_id):
		initialvalue = None
		
		while True:
			self.w = new_folders_window.NewFoldersWindow(self.mainapp.master, self.view, initialvalue)
			self.mainapp.master.wait_window(self.w.top)
			
			if self.w.button == "ok":
				msg = None
				current_directory = self.model.branch_tabs[branch_id].current_directory
				# ------------- CHECK USER INPUT IS VALID -------------
				
				for folder in self.w.folders:
					# ------------- CHECK FOR ILLEGAL CHARACTERS
					for charecter in self.special_characters:
						if charecter in folder:
							msg = f"Found Illegal Character {charecter} in Folder Name {folder}"
							break
				
					# ------------- CHECK IF FOLDER ALREADY EXITS
					if os.path.isdir(os.path.join(current_directory, folder)):
						msg = f"Folder {folder} Already Exists"
						break
				
				# ------------- CHECK FOR DUPLICATE FOLDERS
				if len(self.w.folders) != len(set(self.w.folders)):
					msg = "There are Duplicate Folder Names Present"
					
				
				if msg is None:
					for folder in self.w.folders:
						os.makedirs(os.path.join(current_directory, folder))
						
					# ------------- REFRESH THE VIEW -------------
					self.update_branch_tab(branch_id, current_directory, mode="normal")
					break
				else:
					self.view.show_error(msg)
					initialvalue = "\n".join(self.w.folders)
			
			else: # if user clicked cancel
				break
				
	def open_in_cmd_explorer(self, mode, branch_id):
		current_directory = self.model.branch_tabs[branch_id].current_directory

		if mode == "cmd":
			subprocess.Popen("start /wait cmd.exe", cwd=current_directory, shell=True, stdout=DEVNULL)
		elif mode == "explorer":
			subprocess.Popen(f'explorer "{current_directory}"')
		
	def copy_cut_file_folder(self, files, branch_id, mode):
		current_directory = self.model.branch_tabs[branch_id].current_directory
		files = [os.path.join(current_directory, f) for f in files]
		
		if mode == "cut":
			self.file_to_copy = None
			self.file_to_cut = copy.deepcopy(files)
			
		elif mode == "copy":
			self.file_to_cut = None
			self.file_to_copy = copy.deepcopy(files)			
		
	def paste_file_folder(self, branch_id):
		current_directory = self.model.branch_tabs[branch_id].current_directory
		
		if self.file_to_copy == None:
			files_to_process = self.file_to_cut
			task = "cut"
		else:
			files_to_process = self.file_to_copy
			task = "copy"
		
		fo = pythoncom.CoCreateInstance(shell.CLSID_FileOperation, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IFileOperation)
		
		for source in files_to_process:
			src = shell.SHCreateItemFromParsingName(source, None, shell.IID_IShellItem)
			dst = shell.SHCreateItemFromParsingName(current_directory, None, shell.IID_IShellItem)
			
			# Schedule the operations
			if task == "copy":
				fo.CopyItem(src, dst, None, None)
			elif task == "cut":
				fo.MoveItem(src, dst, None, None)
				
		fo.PerformOperations()
				
		self.update_branch_tab(branch_id, current_directory, mode="normal")		
		
	def filter_files(self, branch_id, mode, extension=None):
		current_directory = self.model.branch_tabs[branch_id].current_directory
		
		if mode == "select_file_types": # user will select file extensions to be filtered out
			filter_type = "extension"
			file_extensions = self.model.branch_tabs[branch_id].get_file_extensions()
			lock_filter = self.model.branch_tabs[branch_id].lock_filter

			if file_extensions == {}:
				self.view.show_error("Folder is Empty, No files Available to Filter")
			else:
				self.w = filter_windows.FilterExtensionWindow(self.mainapp.master, file_extensions, lock_filter)
				self.mainapp.master.wait_window(self.w.top)
			
				if self.w.button == "ok":
					self.model.branch_tabs[branch_id].update_filter(self.w.filter, self.w.lock_filter, filter_type)
					self.update_branch_tab(branch_id, current_directory, mode="refresh")

		elif mode in ["hide_this", "show_this", "remove_filter"]:
			filter_type = "extension"
			self.model.branch_tabs[branch_id].show_only_extension_type(extension, mode)
			self.update_branch_tab(branch_id, current_directory, mode="refresh")

		elif mode == "select_file_names":
			filter_type = "name"
			data = self.model.branch_tabs[branch_id].assemble_view_data()
			text, filter = self.view.launch_filter_filename_window(self.mainapp.master, data)
			
			if text is not None:
				self.model.branch_tabs[branch_id].update_filter(filter, False, filter_type)
				self.update_branch_tab(branch_id, current_directory, mode="refresh")			
			
			
	def launch_diary(self):
		self.diary_window = diary_window.DiaryWindow(self.mainapp.master, self.view)
		self.mainapp.master.wait_window(self.diary_window.top)
		
	def read_date_from_database(self, date):
		return self.model.diary_model.read_date_from_database(date)
		
	def write_diary_text_to_database(self, date, text):
		self.model.diary_model.write_diary_text_to_database(date, text)
		
	def launch_pdf_extractor(self):
		w = pdf_tools_windows.PdfExtractorWindow(self.mainapp.master, self.view)
		self.mainapp.master.wait_window(w.top)

	def launch_pdf_merger(self):
		w = pdf_tools_windows.PdfMergeWindow(self.mainapp.master, self.view)
		self.mainapp.master.wait_window(w.top)

	def launch_to_do_list(self):
		w = todo_list.ToDoListWindow(self.mainapp.master, self.view, self.model.config_data["to_do_list"])
		self.mainapp.master.wait_window(w.top)
		
		self.model.update_config_data({"to_do_list": w.to_do_list})
		
	def load_last_session(self):
		if self.model.last_session is None:
			self.view.show_error("No Session Data Available")
		else:
			answer = self.view.ask_yes_no("All existing tabs will be deleted, do you want to proceed?")
			
			session_data = self.model.last_session

			if answer is True:
				missing_directories = self.check_load_last_session_folders_exist(session_data)
				
				answer = True
				if missing_directories != []:
					msg = "Some Directories are not Accessible, Do You Want to Continue?"
					for d in missing_directories:
						msg = msg + "\n" + d
					
					answer = self.view.ask_yes_no(msg)
			
				if answer:
					# delete tabs from model
					self.model.delete_all_tabs()
					
					# delete tabs from view
					self.view.delete_all_tabs()
				
					for root_id in session_data.keys():
						new_root_id = self.add_root_tab(default_branch_tab=False, default_text=session_data[root_id]["text"])
				
						for branch_id in session_data[root_id]["branch_tabs"].keys():
							default_text = session_data[root_id]["branch_tabs"][branch_id]["text"]
							default_directory = session_data[root_id]["branch_tabs"][branch_id]["directory"]
							
							if default_directory in missing_directories:
								default_directory = None
								
							self.add_branch_tab(new_root_id, default_text, default_directory)
	
	def check_load_last_session_folders_exist(self, session_data):
		missing_directories = []
		for root_id in session_data.keys():
			
			for branch_id in session_data[root_id]["branch_tabs"].keys():
				default_directory = session_data[root_id]["branch_tabs"][branch_id]["directory"] 
				
				if os.path.isdir(default_directory) is False:
					missing_directories.append(default_directory)
					
		return set(missing_directories)
		
	def search(self, branch_id):
		data = self.model.branch_tabs[branch_id].assemble_view_data()
		self.w = search_window.SearchWindow(self.mainapp.master, data)
		self.mainapp.master.wait_window(self.w.top)	
		
	def add_new_quick_access_folder(self, text=None, folder_id=None, update_config_data=True, idx=0):
		# get text 
		if text is None: # Text is not None when the app loads, as it takes the text from the config file
			self.w = rename_window.RenameWindow(self.mainapp.master, self.view, initialvalue="", component_type="quick_access_folder", mode="new_quick_access")
			self.mainapp.master.wait_window(self.w.top)
			
			if self.w.button == "ok":
				text = self.w.name
		if text:
			folder_id = self.model.quick_access_tree_model.add_new_folder(text, folder_id=folder_id)
			self.view.quick_access_tree.insert_new_folder(folder_id, text, idx=idx)
			
			if update_config_data is True:
				self.model.update_quick_access_tree_config_file()
	
	def rename_quick_access_folder(self, folder_id, text=None, update_config_data=True):
		initialvalue = self.model.quick_access_tree_model.folders[folder_id].text
		
		if text is None:
			# text = self.view.quick_access_tree.edit_folder_name(mode="new", initialvalue=initialvalue)
			self.w = rename_window.RenameWindow(self.mainapp.master, self.view, initialvalue=initialvalue, component_type="quick_access_folder", mode="edit_quick_access")
			self.mainapp.master.wait_window(self.w.top)
			
			if self.w.button == "ok":
				text = self.w.name
			
		if text:
			self.model.quick_access_tree_model.rename_folder(folder_id, text)
			self.view.quick_access_tree.rename_folder(folder_id, text)
			
			if update_config_data is True:
				self.model.update_quick_access_tree_config_file()
	
	def setup_quick_access_tree(self):
		for folder_id in self.model.config_data["quick_access_tree"].keys():
			text = self.model.config_data["quick_access_tree"][folder_id]["text"]
			self.add_new_quick_access_folder(text=text, folder_id=folder_id, update_config_data=False, idx="end")
			
			for link_id in self.model.config_data["quick_access_tree"][folder_id]["links"].keys():
				text = self.model.config_data["quick_access_tree"][folder_id]["links"][link_id]["text"]
				path = self.model.config_data["quick_access_tree"][folder_id]["links"][link_id]["path"]
				self.add_new_link(folder_id, "new", text=text, path=path, link_id=link_id, update_config_data=False)
		

	def delete_quick_access_folder(self, folder_id, update_config_data=True):
		answer = self.view.ask_yes_no("Delete This Folder? This Cannot be Undone")
		
		if answer:
			self.model.quick_access_tree_model.delete_folder(folder_id)
			self.view.quick_access_tree.delete_folder(folder_id)
		
			if update_config_data is True:
				self.model.update_quick_access_tree_config_file()
				
	def add_new_link(self, folder_id, mode, text=None, path=None, link_id=None, update_config_data=True):
		if text is None:
			text, path = self.view.quick_access_tree.launch_new_link_window(self.mainapp.master, mode)
		
		if text is not None:		
			link_id = self.model.quick_access_tree_model.add_new_link(folder_id, link_id, text, path)
			self.view.quick_access_tree.insert_new_link(folder_id, link_id, text)
			
			if update_config_data is True:
				self.model.update_quick_access_tree_config_file()

	def edit_link(self, folder_id, link_id, update_config_data=True):
		text = self.model.quick_access_tree_model.folders[folder_id].links[link_id]["text"]
		path = self.model.quick_access_tree_model.folders[folder_id].links[link_id]["path"]
		mode = "edit"
		text, path = self.view.quick_access_tree.launch_new_link_window(self.mainapp.master, mode, text=text, path=path)
		
		if text is not None:
			self.model.quick_access_tree_model.update_link(folder_id, link_id, text, path)
			self.view.quick_access_tree.update_link(link_id, text)
	
			if update_config_data is True:
				self.model.update_quick_access_tree_config_file()
	
	def delete_link(self, folder_id, link_id, update_config_data=True):
		answer = self.view.ask_yes_no("Delete This Link? This Cannot be Undone")
		
		if answer:
			self.model.quick_access_tree_model.delete_link(folder_id, link_id)
			self.view.quick_access_tree.delete_link(link_id)

			if update_config_data is True:
				self.model.update_quick_access_tree_config_file()
				
	def update_quick_access_order(self, quick_access_order):
		self.model.quick_access_tree_model.update_order(quick_access_order)
		self.model.update_quick_access_tree_config_file()
		
	def update_root_tabs_order(self, root_tabs_order):
		self.model.update_root_tabs_order(root_tabs_order)
		
	def update_branch_tabs_order(self, root_id, branch_tabs_order):
		self.model.update_branch_tabs_order(root_id, branch_tabs_order)
	
	def update_style(self, style):
		self.view.switch_style(style)
		self.model.style_updated(style)
		