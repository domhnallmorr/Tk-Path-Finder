from model.quick_access_tree_model import QuickAccessTreeModel


class IdSource:
	def __init__(self):
		self.count = 0

	def gen_id(self):
		self.count += 1
		return f"id{self.count}"


def test_add_rename_and_delete_folder():
	tree = QuickAccessTreeModel(IdSource())

	folder_id = tree.add_new_folder("Project")
	tree.rename_folder(folder_id, "Renamed")

	assert tree.folders[folder_id].text == "Renamed"

	tree.delete_folder(folder_id)

	assert folder_id not in tree.folders


def test_add_update_delete_and_read_link():
	tree = QuickAccessTreeModel(IdSource())
	folder_id = tree.add_new_folder("Project")

	link_id = tree.add_new_link(folder_id, None, "Source", r"C:\src")
	tree.update_link(folder_id, link_id, "Docs", r"C:\docs")

	assert tree.get_link_directory(folder_id, link_id) == r"C:\docs"
	assert tree.folders[folder_id].links[link_id] == {"text": "Docs", "path": r"C:\docs"}
	assert tree.get_all_link_ids() == [link_id]

	tree.delete_link(folder_id, link_id)

	assert tree.folders[folder_id].links == {}


def test_assemble_config_file_data_preserves_folder_and_link_data():
	tree = QuickAccessTreeModel(IdSource())
	folder_id = tree.add_new_folder("Project", folder_id="folder1")
	tree.add_new_link(folder_id, "link1", "Source", r"C:\src")

	assert tree.assemble_config_file_data() == {
		"folder1": {
			"text": "Project",
			"links": {"link1": {"text": "Source", "path": r"C:\src"}},
		}
	}


def test_update_order_reorders_folders_and_links():
	tree = QuickAccessTreeModel(IdSource())
	folder1 = tree.add_new_folder("One", folder_id="folder1")
	folder2 = tree.add_new_folder("Two", folder_id="folder2")
	tree.add_new_link(folder1, "link1", "One A", r"C:\one-a")
	tree.add_new_link(folder1, "link2", "One B", r"C:\one-b")
	tree.add_new_link(folder2, "link3", "Two A", r"C:\two-a")

	msg = tree.update_order({"folder2": ["link3"], "folder1": ["link2", "link1"]})

	assert msg is None
	assert list(tree.folders.keys()) == ["folder2", "folder1"]
	assert list(tree.folders["folder1"].links.keys()) == ["link2", "link1"]


def test_update_order_returns_message_for_unknown_link_and_keeps_existing_order():
	tree = QuickAccessTreeModel(IdSource())
	folder_id = tree.add_new_folder("Project", folder_id="folder1")
	tree.add_new_link(folder_id, "link1", "Source", r"C:\src")

	msg = tree.update_order({"folder1": ["missing"]})

	assert "missing" in msg
	assert list(tree.folders["folder1"].links.keys()) == ["link1"]
