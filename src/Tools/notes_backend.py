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
		data = self.cursor.execute(f"SELECT * FROM notes WHERE category = '{category}' AND subcategory = '{sub_category}' AND page = '{page}'").fetchall()
		
		if len(data) == 0:
			self.cursor.execute(f"INSERT INTO notes VALUES('{category}', '{sub_category}', '', '{page}', '{txt}')")
		else:
			self.cursor.execute(f"UPDATE notes SET text = '{txt}' WHERE category = '{category}' AND subcategory = '{sub_category}' AND page = '{page}'")
			
		self.conn.commit()		
			
	def get_all_pages(self, category, sub_category):
		pages = self.cursor.execute(f"SELECT DISTINCT page FROM notes WHERE category = '{category}' AND subcategory = '{sub_category}'").fetchall()
		
		return [p[0] for p in pages]
		
	def get_page_text(self, category, sub_category, page):
		data = self.cursor.execute(f"SELECT * FROM notes WHERE category = '{category}' AND subcategory = '{sub_category}' AND page = '{page}'").fetchall()

		return data[0][-1]
		
	def delete_page(self, category, sub_category, page):
		self.cursor.execute(f"DELETE FROM notes WHERE category = '{category}' AND subcategory = '{sub_category}' AND page = '{page}'")
		self.conn.commit()