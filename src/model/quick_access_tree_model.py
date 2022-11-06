import copy

class QuickAccessTreeModel:
	def __init__(self, model):
		self.model = model
		self.folders = {}
		
	def add_new_folder(self, text, folder_id=None):
		if folder_id is None:
			folder_id = self.model.gen_id()
		self.folders[folder_id] = QuickAccessFolder(folder_id, text)
		
		return folder_id
		
	def assemble_config_file_data(self):
		return {folder_id: self.folders[folder_id].assemble_config_file_data() for folder_id in self.folders.keys()}
		
	def delete_folder(self, folder_id):
		self.folders.pop(folder_id)
		
	def rename_folder(self, folder_id, text):
		self.folders[folder_id].rename(text)
		
	def add_new_link(self, folder_id, link_id, text, path):
		if link_id is None:
			link_id = self.model.gen_id()

		self.folders[folder_id].links[link_id] = {"text": text, "path": path}
		
		return link_id
			
	def get_all_link_ids(self):
		link_ids = []
		
		for folder_id in self.folders:
			for link in self.folders[folder_id].links.keys():
				link_ids.append(link)
				
		return link_ids
		
	def update_order(self, new_order):
		msg = None
		
		new_folders = {}
		for folder_id in new_order:
			new_folders[folder_id] = self.folders[folder_id]
			msg = self.folders[folder_id].update_links_order(new_order[folder_id])
		
			if msg is not None:
				break
			
		if msg is None:
			self.folders = copy.deepcopy(new_folders)
			
		return msg

	def get_link_directory(self, folder_id, link_id):
		return self.folders[folder_id].links[link_id]["path"]
		
	def update_link(self, folder_id, link_id, text, path):
		self.folders[folder_id].links[link_id]["text"] = text
		self.folders[folder_id].links[link_id]["path"] = path
		
	def delete_link(self, folder_id, link_id):
		self.folders[folder_id].links.pop(link_id)
		
class QuickAccessFolder:
	def __init__(self, folder_id, text):
		self.folder_id = folder_id
		self.text = text
		
		self.links = {}
		
	def assemble_config_file_data(self):
		config_file_data = {"text": self.text, "links": self.links}
		
		return config_file_data
		
	def rename(self, text):
		self.text = text
		
	def update_links_order(self, links):
		msg = None
		try:
			new_links = {}
			for link_id in links:
				new_links[link_id] = copy.deepcopy(self.links[link_id]) 
			
		except Expection as e:
			msg = str(e)
		
		if msg is None:
			self.links = copy.deepcopy(new_links)
			del new_links
		
		return msg
		
		
		
		
		