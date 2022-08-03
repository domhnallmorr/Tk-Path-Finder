import os
import sqlite3
from Tools import diary_backend


class NotesBackend:
	def __init__(self):
		if not os.path.isfile("notes.db"):
			diary_backend.create_database()
			
		self.conn = sqlite3.connect('notes.db')
		self.cursor = self.conn.cursor()
			
	def write_notes_database(self, category, sub_category, page, txt):
		data = self.cursor.execute("SELECT * FROM notes WHERE category = ? AND subcategory = ? AND page = ?", (category, sub_category, page)).fetchall()
		
		if len(data) == 0:
			self.cursor.execute("INSERT INTO notes VALUES(?, ?, '', ?, ?)", (category, sub_category, page, txt))
		else:
			self.cursor.execute("UPDATE notes SET text = ? WHERE category = ? AND subcategory = ? AND page = ?", (txt, category, sub_category, page))
			
		self.conn.commit()		
			
	def get_all_pages(self, category, sub_category):
		pages = self.cursor.execute("SELECT DISTINCT page FROM notes WHERE category = ? AND subcategory = ?", (category, sub_category)).fetchall()
		
		return [p[0] for p in pages]
		
	def get_page_text(self, category, sub_category, page):
		data = self.cursor.execute("SELECT * FROM notes WHERE category = ? AND subcategory = ? AND page = ?", (category, sub_category, page)).fetchall()

		return data[0][-1]
		
	def delete_page(self, category, sub_category, page):
		self.cursor.execute("DELETE FROM notes WHERE category = ? AND subcategory = ? AND page = ?", (category, sub_category, page))
		self.conn.commit()