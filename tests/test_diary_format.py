from view.diary_window import normalise_note_data


def test_normalise_note_data_supports_legacy_plain_text():
	assert normalise_note_data("plain note") == {"text": "plain note", "tags": []}


def test_normalise_note_data_preserves_styled_note_shape():
	note = {
		"text": "styled note",
		"tags": [
			{
				"tag": "text_color_ff0000",
				"start": "1.0",
				"end": "1.6",
				"options": {"foreground": "#ff0000"},
			}
		],
	}

	assert normalise_note_data(note) == note


def test_normalise_note_data_fills_missing_keys():
	assert normalise_note_data({}) == {"text": "", "tags": []}


def test_normalise_note_data_handles_unexpected_data():
	assert normalise_note_data(None) == {"text": "", "tags": []}
