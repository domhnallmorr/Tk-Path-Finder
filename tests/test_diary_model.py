import datetime
import sqlite3

from model.diary_model import DiaryModel


def test_diary_model_creates_database_in_working_directory(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)

	DiaryModel()

	assert (tmp_path / "notes.db").is_file()


def test_diary_model_writes_and_reads_new_note(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)
	model = DiaryModel()
	note_date = datetime.date(2026, 7, 5)
	note = {
		"General": {
			"text": "Styled note",
			"tags": [
				{"tag": "bold", "start": "1.0", "end": "1.6", "options": {}},
			],
		},
	}

	model.write_diary_text_to_database(note_date, note)

	assert model.read_date_from_database(note_date) == note
	assert model.read_date_from_database("2026-07-05") == note


def test_diary_model_updates_existing_note(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)
	model = DiaryModel()
	note_date = "2026-07-05"

	model.write_diary_text_to_database(note_date, {"General": "first"})
	model.write_diary_text_to_database(note_date, {"General": "second"})

	assert model.read_date_from_database(note_date) == {"General": "second"}

	conn = sqlite3.connect("notes.db")
	try:
		count = conn.execute("SELECT COUNT(*) FROM diary WHERE datestamp = ?", (note_date,)).fetchone()[0]
	finally:
		conn.close()

	assert count == 1


def test_diary_model_reads_legacy_python_literal_rows(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)
	model = DiaryModel()

	model.cursor.execute(
		"INSERT INTO diary VALUES(?, '', ?)",
		("2026-07-05", "{'General': 'legacy text'}"),
	)
	model.conn.commit()

	assert model.read_date_from_database("2026-07-05") == {"General": "legacy text"}


def test_diary_model_returns_empty_note_for_missing_date(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)
	model = DiaryModel()

	assert model.read_date_from_database("2026-07-05") == {"General": ""}
