import ast
import json
import os
import sqlite3

def create_database():
	conn = sqlite3.connect('notes.db')
	cursor = conn.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS diary(datestamp TEXT, tags TEXT, text TEXT)")
	cursor.execute("CREATE TABLE IF NOT EXISTS notes(category TEXT, subcategory TEXT, tags TEXT, page TEXT, text TEXT)")

	conn.commit()
	cursor.close()
	conn.close()
	
	
def read_database():
	conn = sqlite3.connect('notes.db')
	cursor = conn.cursor()	
	
	cursor.execute('SELECT * FROM diary')
	data = cursor.fetchall()
	
class DiaryBackend:
	def __init__(self):
		if not os.path.isfile("notes.db"):
			create_database()
			
		self.conn = sqlite3.connect('notes.db')
		self.cursor = self.conn.cursor()
		
	def write_diary_text_to_database(self, date, data):
		txt = json.dumps(data)
		
		data = self.cursor.execute(f"SELECT * FROM diary WHERE datestamp = '{date}'").fetchall()

		if len(data) == 0:
			self.cursor.execute(f"INSERT INTO diary VALUES('{date}', '', '{txt}')")
		else:
			self.cursor.execute(f"UPDATE diary SET text = '{txt}' WHERE datestamp = '{date}'")
			
		self.conn.commit()		
	
	def check_date_in_database(self, date):
		self.cursor.execute(f"SELECT * FROM diary WHERE datestamp = '{date}'")
		data = self.cursor.fetchall()
		if len(data) == 0:
			self.cursor.execute(f"INSERT INTO diary VALUES('{date}', '', 'General', 'Some Text')")
			self.conn.commit()	
			
			
	def read_date_from_database(self, date):
		data = self.cursor.execute(f"SELECT * FROM diary WHERE datestamp = '{date}'").fetchall()
		if len(data) > 0:
			txt = ast.literal_eval(data[0][-1])
		else:
			txt = {"General": ""}
			
		return txt

if __name__ == "__main__":
	
	if not os.path.isfile("notes.db"):
		create_database()
	else:
		read_database()