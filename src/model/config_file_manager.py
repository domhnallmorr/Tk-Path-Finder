import copy
import json
import os

def write_config_file(model):
	save_dict = {}
	
	# Get the Quick Access Links
	save_dict["quick_access_tree"] = model.config_data["quick_access_tree"]
	save_dict["text_editor"] = model.config_data["text_editor"]
	save_dict["open_with_apps"] = model.config_data["open_with_apps"]
	
	# ------- TREEVIEW COLUMN WIDTHS -------
	save_dict["default_file_width"] = model.config_data["default_file_width"]
	save_dict["default_date_width"] = model.config_data["default_date_width"]
	save_dict["default_type_width"] = model.config_data["default_type_width"]
	save_dict["default_size_width"] = model.config_data["default_size_width"]
	save_dict["default_style"] = model.config_data["default_style"]

	save_dict["to_do_list"] = model.config_data["to_do_list"]
	save_dict["session_data"] = model.config_data["session_data"]
	# save_dict['notes_categories'] = mainapp.notes_categories
	# save_dict['last_session'] = mainapp.session
	
	
	with open("tk_path_finder_config.json", "w") as outfile:
		json.dump(save_dict, outfile, indent=4)
		
def load_config_file(mainapp):
	if not os.path.isfile('tk_path_finder_config.json'):
		generate_default_config_file()
		
	with open('tk_path_finder_config.json') as f:
		data = json.load(f)
	return data
	
def generate_default_config_file():
	
	save_dict = {}
	# save_dict['links'] = {"I001": {}}
	# save_dict["node_iids"] = {"I001": 'Default'}
	# save_dict["nodes"] = {"Default": 'I001'}
	# save_dict["open_with_apps"] = {}
	save_dict["text_editor"] = ""
	save_dict["to_do_list"] = []
	
	with open('tk_path_finder_config.json', 'w') as outfile:
		json.dump(save_dict, outfile, indent=4)
		