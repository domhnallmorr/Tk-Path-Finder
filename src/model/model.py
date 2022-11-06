import copy
import os
import random
import string

from model import branch_tab_model, config_file_manager, diary_model, quick_access_tree_model

class Model:
	def __init__(self):
		self.setup_variables()
		
	def setup_variables(self):
		self.config_data = config_file_manager.load_config_file(self)
		
		# ---------------- SETTINGS ----------------
		if "text_editor" in self.config_data.keys():
			self.text_editor = self.config_data["text_editor"]
		else:
			self.text_editor = None
		
		if "open_with_apps" not in self.config_data.keys():
			self.config_data["open_with_apps"] = {}
		
		if "to_do_list" not in self.config_data.keys():
			self.config_data["to_do_list"] = []
		
		if "session_data" in self.config_data.keys():
			self.last_session = copy.deepcopy(self.config_data["session_data"])
		else:
			self.last_session = None
		
		# ------------ TREEVIEW COLUMN WIDTHS ------------
		if "default_file_width" not in self.config_data.keys():
			self.config_data["default_file_width"] = 400 # column width in treeview

		if "default_date_width" not in self.config_data.keys():
			self.config_data["default_date_width"] = 200 # column width in treeview

		if "default_type_width" not in self.config_data.keys():
			self.config_data["default_type_width"] = 300 # column width in treeview

		if "default_size_width" not in self.config_data.keys():
			self.config_data["default_size_width"] = 100 # column width in treeview
			
		if "quick_access_tree" not in self.config_data.keys():
			self.config_data["quick_access_tree"] = {}
			
		self.config_data["session_data"] = {}
		
	
		self.root_tabs = {}
		self.branch_tabs = {}
		
		self.default_root_tab_text = 0

		self.known_file_types = {
			".csv": "CSV File",
			".das": "Das file",
			".doc": "Word 97-2003 Document",
			".docx": "Word Document",
			".exe": "application",
			".ipynb": "Jupyter Notebook",
			".jpeg": "JPEG Image",
			".jpg": "JPG Image",
			".json": "JSON file",
			".keyx": "key file",
			".mkv": "MKV Video",
			".mp3": "MP4 Audio",
			".mp4": "MP4 Video",
			".mplt": "mplt file",
			".msg": "Email",
			".out": "Output file",
			".pdf": "PDF",
			".png": "PNG Image",
			".pptx": "Powerpoint Presentation",
			".py": "Python File",
			".rar": "RAR File",
			".torrent": "Torrent File",
			".txt": "Text File",
			".xls": "Excel Worksheet 97-2003",
			".xlsm": "Marco Enabled Excel Worksheet",
			".xlsx": "Excel Worksheet",
			".zip": "ZIP File",
		}		
		
		# Adding this assert as "Folder" is used in right click logic (see branch_tab, right_click_treeview method)
		assert "Folder" not in self.known_file_types.values(), "Folder Cannot be Included in known_file_types"
		
		self.diary_model = diary_model.DiaryModel()
		
		self.quick_access_tree_model = quick_access_tree_model.QuickAccessTreeModel(self)
		
	def gen_id(self):
		link_ids = self.quick_access_tree_model.get_all_link_ids()
		count = 0
		while True:
			characters = string.ascii_letters + string.digits
			new_id = ''.join(random.choice(characters) for i in range(8))
		
			count += 1
			
			if new_id not in self.quick_access_tree_model.folders.keys() and new_id not in self.root_tabs.keys() and new_id not in self.branch_tabs.keys() and new_id not in link_ids:
				break
			elif count > 10_000:
				raise Exception("id not generated after 10,000 attempts")
				
		return new_id
		
	def add_root_tab(self, default_text):
		
		root_id = self.gen_id()
		if default_text is None:
			default_text = str(self.default_root_tab_text)
			
		self.root_tabs[root_id] = {"text": default_text, "branch_tabs": []}
		self.default_root_tab_text += 1
		
		self.config_data["session_data"][root_id] = {"text": default_text, "branch_tabs": {}}
		config_file_manager.write_config_file(self)
		
		return root_id
		
	def get_root_tab_text(self, root_id):
		return self.root_tabs[root_id]["text"]
		
	def add_branch_tab(self, root_id, default_text=None, default_directory=None):
		branch_id = self.gen_id()
		
		if default_directory is None:
			default_directory = os.getcwd()
		#self.branch_tabs[id] = {"id": id, "text": "branch", "current_directory": os.getcwd()}
		self.branch_tabs[branch_id] = branch_tab_model.BranchTabModel(self, branch_id, default_directory, root_id, default_text)
		self.root_tabs[root_id]["branch_tabs"].append(branch_id)
		
		self.update_branch_tab_session_data(branch_id)
		config_file_manager.write_config_file(self)
		return branch_id
		
	def get_branch_tab_text(self, branch_id):
		return self.branch_tabs[branch_id].text

	def get_branch_tab_directory(self, branch_id):
		return self.branch_tabs[branch_id].current_directory
		
	def get_file_type(self, filename):
		filename, file_extension = os.path.splitext(filename)
		file_type = 'file'
		
		if file_extension in self.known_file_types.keys():
			file_type = self.known_file_types[file_extension]
			
		return file_type
		
	def update_branch_tab(self, branch_id, directory, sort=None):
		msg = self.branch_tabs[branch_id].list_directory(directory=directory, sort=None)

	def delete_root_tab(self, root_id):
		self.root_tabs.pop(root_id)
		self.config_data["session_data"].pop(root_id)
		
	def delete_branch_tab(self, root_id, branch_id):
		self.root_tabs[root_id]["branch_tabs"].remove(branch_id)
		self.config_data["session_data"][root_id]["branch_tabs"].pop(branch_id)
		config_file_manager.write_config_file(self)
		
	def rename_root_tab(self, root_id, text):
		self.root_tabs[root_id]["text"] = text
		self.config_data["session_data"][root_id]["text"] = text
		config_file_manager.write_config_file(self)
		
	def rename_branch_tab(self, branch_id, text, text_locked):
		self.branch_tabs[branch_id].text = text
		self.branch_tabs[branch_id].text_locked = text_locked
		
		root_id = self.branch_tabs[branch_id].root_id
		self.config_data["session_data"][root_id]["branch_tabs"][branch_id]["text"] = text
		
	def get_number_of_branch_tabs(self, root_id):
		return len(self.root_tabs[root_id]["branch_tabs"])

	def update_config_data(self, new_settings):
		for param in new_settings.keys():
			self.config_data[param] = new_settings[param]
			
		config_file_manager.write_config_file(self)

	def update_branch_tab_session_data(self, branch_id):
		root_id = self.branch_tabs[branch_id].root_id
		self.config_data["session_data"][root_id]["branch_tabs"][branch_id] = {"text": self.branch_tabs[branch_id].text, "directory": self.branch_tabs[branch_id].current_directory}
		
		config_file_manager.write_config_file(self)
		
	def delete_all_tabs(self):
		self.root_tabs = {}
		self.branch_tabs = {}
		
		self.config_data["session_data"] = {}
		
	def update_quick_access_tree_config_file(self):
		data = self.quick_access_tree_model.assemble_config_file_data()
		self.update_config_data({"quick_access_tree": data})
		
		