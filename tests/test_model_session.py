import sys
from types import SimpleNamespace


sys.modules.setdefault(
	"natsort",
	SimpleNamespace(
		natsorted=sorted,
		os_sorted=sorted,
		ns=SimpleNamespace(IGNORECASE=None),
	),
)

from model import model as model_module


class FakeBranchTabModel:
	def __init__(self, model, id_key, current_directory, root_id, default_text, default_icon):
		self.model = model
		self.id_key = id_key
		self.root_id = root_id
		self.text = default_text or "branch"
		self.current_directory = current_directory
		self.icon_extension = default_icon
		self.text_locked = default_text is not None


def make_model(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)
	monkeypatch.setattr(model_module.branch_tab_model, "BranchTabModel", FakeBranchTabModel)
	return model_module.Model()


def test_add_root_tab_updates_root_tabs_and_session_data(tmp_path, monkeypatch):
	model = make_model(tmp_path, monkeypatch)

	root_id = model.add_root_tab("Root")

	assert model.root_tabs[root_id] == {"text": "Root", "branch_tabs": []}
	assert model.config_data["session_data"][root_id] == {"text": "Root", "branch_tabs": {}}


def test_add_branch_tab_links_branch_to_root_and_session_data(tmp_path, monkeypatch):
	model = make_model(tmp_path, monkeypatch)
	root_id = model.add_root_tab("Root")

	branch_id = model.add_branch_tab(
		root_id,
		default_text="Docs",
		default_directory=r"C:\docs",
		default_icon=".txt",
	)

	assert model.root_tabs[root_id]["branch_tabs"] == [branch_id]
	assert model.branch_tabs[branch_id].text == "Docs"
	assert model.config_data["session_data"][root_id]["branch_tabs"][branch_id] == {
		"text": "Docs",
		"directory": r"C:\docs",
		"icon": ".txt",
	}


def test_rename_root_and_branch_tabs_update_session_data(tmp_path, monkeypatch):
	model = make_model(tmp_path, monkeypatch)
	root_id = model.add_root_tab("Root")
	branch_id = model.add_branch_tab(root_id, default_text="Docs", default_directory=r"C:\docs")

	model.rename_root_tab(root_id, "Client")
	model.rename_branch_tab(branch_id, "Drawings", text_locked=True)

	assert model.root_tabs[root_id]["text"] == "Client"
	assert model.config_data["session_data"][root_id]["text"] == "Client"
	assert model.branch_tabs[branch_id].text == "Drawings"
	assert model.branch_tabs[branch_id].text_locked is True
	assert model.config_data["session_data"][root_id]["branch_tabs"][branch_id]["text"] == "Drawings"


def test_delete_branch_and_root_tabs_update_session_data(tmp_path, monkeypatch):
	model = make_model(tmp_path, monkeypatch)
	root_id = model.add_root_tab("Root")
	branch_id = model.add_branch_tab(root_id, default_text="Docs", default_directory=r"C:\docs")

	model.delete_branch_tab(root_id, branch_id)

	assert model.root_tabs[root_id]["branch_tabs"] == []
	assert branch_id not in model.config_data["session_data"][root_id]["branch_tabs"]

	model.delete_root_tab(root_id)

	assert root_id not in model.root_tabs
	assert root_id not in model.config_data["session_data"]


def test_reordering_root_and_branch_tabs_updates_session_data_order(tmp_path, monkeypatch):
	model = make_model(tmp_path, monkeypatch)
	root1 = model.add_root_tab("One")
	root2 = model.add_root_tab("Two")
	branch1 = model.add_branch_tab(root1, default_text="A", default_directory=r"C:\a")
	branch2 = model.add_branch_tab(root1, default_text="B", default_directory=r"C:\b")

	model.update_root_tabs_order([root2, root1])
	model.update_branch_tabs_order(root1, [branch2, branch1])

	assert list(model.config_data["session_data"].keys()) == [root2, root1]
	assert list(model.config_data["session_data"][root1]["branch_tabs"].keys()) == [branch2, branch1]


def test_delete_all_tabs_clears_live_and_session_state(tmp_path, monkeypatch):
	model = make_model(tmp_path, monkeypatch)
	root_id = model.add_root_tab("Root")
	model.add_branch_tab(root_id, default_text="Docs", default_directory=r"C:\docs")

	model.delete_all_tabs()

	assert model.root_tabs == {}
	assert model.branch_tabs == {}
	assert model.config_data["session_data"] == {}
