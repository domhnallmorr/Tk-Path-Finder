import json
from types import SimpleNamespace

from model import config_file_manager


def make_config_model(last_session=None):
	return SimpleNamespace(
		last_session=last_session,
		config_data={
			"quick_access_tree": {"folder1": {"text": "Project", "links": {}}},
			"text_editor": "notepad.exe",
			"open_with_apps": {".txt": ["notepad.exe"]},
			"default_file_width": 400,
			"default_date_width": 200,
			"default_type_width": 300,
			"default_size_width": 100,
			"default_style": "darkly",
			"to_do_list": ["ship tests"],
			"session_data": {"current": {"text": "Current", "branch_tabs": {}}},
		},
	)


def read_config(path):
	return json.loads(path.read_text())


def test_generate_default_config_file_creates_minimum_config(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)

	config_file_manager.generate_default_config_file()

	assert read_config(tmp_path / "tk_path_finder_config.json") == {
		"text_editor": "",
		"to_do_list": [],
	}


def test_load_config_file_generates_config_when_missing(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)

	data = config_file_manager.load_config_file(SimpleNamespace())

	assert data["text_editor"] == ""
	assert data["to_do_list"] == []
	assert (tmp_path / "tk_path_finder_config.json").is_file()


def test_load_config_file_rotates_existing_backups(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)
	(tmp_path / "tk_path_finder_config.json").write_text('{"name": "current"}')
	(tmp_path / "tk_path_finder_config_backup1.json").write_text('{"name": "backup1"}')
	(tmp_path / "tk_path_finder_config_backup2.json").write_text('{"name": "backup2"}')
	(tmp_path / "tk_path_finder_config_backup3.json").write_text('{"name": "backup3"}')
	(tmp_path / "tk_path_finder_config_backup4.json").write_text('{"name": "backup4"}')

	config_file_manager.load_config_file(SimpleNamespace())

	assert read_config(tmp_path / "tk_path_finder_config_backup1.json") == {"name": "current"}
	assert read_config(tmp_path / "tk_path_finder_config_backup2.json") == {"name": "backup1"}
	assert read_config(tmp_path / "tk_path_finder_config_backup3.json") == {"name": "backup2"}
	assert read_config(tmp_path / "tk_path_finder_config_backup4.json") == {"name": "backup3"}
	assert read_config(tmp_path / "tk_path_finder_config_backup5.json") == {"name": "backup4"}


def test_write_config_file_writes_current_session_data(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)
	model = make_config_model(last_session={"previous": {"text": "Previous", "branch_tabs": {}}})

	config_file_manager.write_config_file(model)

	data = read_config(tmp_path / "tk_path_finder_config.json")
	assert data["session_data"] == model.config_data["session_data"]
	assert data["quick_access_tree"] == model.config_data["quick_access_tree"]
	assert data["text_editor"] == "notepad.exe"


def test_write_config_file_startup_preserves_last_session(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)
	last_session = {"previous": {"text": "Previous", "branch_tabs": {}}}
	model = make_config_model(last_session=last_session)

	config_file_manager.write_config_file(model, startup=True)

	data = read_config(tmp_path / "tk_path_finder_config.json")
	assert data["session_data"] == last_session
