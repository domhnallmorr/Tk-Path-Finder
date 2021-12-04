import copy
import json
import os

def write_config_file(mainapp):
	save_dict = {}
	
	# Get the Quick Access Links
	save_dict['links'] = copy.deepcopy(mainapp.quick_access_tree.links)
	save_dict['node_iids'] = copy.deepcopy(mainapp.quick_access_tree.node_iids)
	save_dict['nodes'] = copy.deepcopy(mainapp.quick_access_tree.nodes)
	save_dict['text_editor'] = mainapp.text_editor
	save_dict['open_with_apps'] = copy.deepcopy(mainapp.open_with_apps)
	
	with open('tk_path_finder_config.json', 'w') as outfile:
		json.dump(save_dict, outfile, indent=4)
		
def load_config_file(mainapp):
	if not os.path.isfile('tk_path_finder_config.json'):
		generate_default_config_file()
		
	with open('tk_path_finder_config.json') as f:
		data = json.load(f)
	return data
	
def generate_default_config_file():
	
	save_dict = {}
	save_dict['links'] = {"I001": {}}
	save_dict["node_iids"] = {"I001": 'Default'}
	save_dict["nodes"] = {"Default": 'I001'}
	save_dict["open_with_apps"] = {}
	
	with open('tk_path_finder_config.json', 'w') as outfile:
		json.dump(save_dict, outfile, indent=4)
		