from datetime import date
import datetime
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import font as tkfont
from tkinter import colorchooser

from ttkbootstrap.dialogs import dialogs

from custom_widgets import autoscrollbar
from model import config_file_manager

def normalise_note_data(note_data):
	if isinstance(note_data, str):
		return {"text": note_data, "tags": []}
	
	if isinstance(note_data, dict):
		return {
			"text": note_data.get("text", ""),
			"tags": note_data.get("tags", []),
		}
	
	return {"text": "", "tags": []}

def launch_diary(mainapp):
	if mainapp.diary_open is False:
		mainapp.diary_open = True
		
		mainapp.diary_window = DiaryWindow(mainapp)
		mainapp.master.wait_window(mainapp.diary_window.top)
		config_file_manager.write_config_file(mainapp)
		
		mainapp.diary_open = False
	else:
		mainapp.diary_window.top.lift()
		
class DiaryWindow(ttk.Frame):
	def __init__(self, master, view):
		super(DiaryWindow, self).__init__()
		top=self.top=Toplevel(master)
		#top.grab_set()
		# self.backend = diary_backend.DiaryBackend()
		self.view = view
		self.data = {}
		
		self.top.title("Diary")
		self.button = 'cancel'
		
		self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
		self.title_font.configure(underline=True)
		self.body_font = tkfont.Font(family="Segoe UI", size=10)
		self.bold_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
		self.italic_font = tkfont.Font(family="Segoe UI", size=10, slant="italic")
		self.heading_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")
		self.subheading_font = tkfont.Font(family="Segoe UI", size=13, weight="bold")
		self.code_font = tkfont.Font(family="Consolas", size=10)
		
		self.setup_label_frames()
		self.setup_labels()
		self.setup_buttons()
		self.setup_text_widget()
	
		self.top.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.autosave_job = self.top.after(60000, self.autosave)
		
		self.top.geometry("800x650")
		
	def on_closing(self):
		if self.autosave_job is not None:
			self.top.after_cancel(self.autosave_job)
			self.autosave_job = None
		self.get_text_input()

		for date in self.data.keys():
			self.view.controller.write_diary_text_to_database(date, self.data[date])
			
		self.top.destroy()
	
	def setup_label_frames(self):
		self.date_frame = LabelFrame(self.top, text="Date:")
		self.date_frame.pack(fill=BOTH, padx=self.view.default_padx, pady=self.view.default_pady)

		self.notes_frame = LabelFrame(self.top, text="Notes:")
		self.notes_frame.pack(expand=True, fill=BOTH, padx=self.view.default_padx, pady=self.view.default_pady)
		self.notes_frame.grid_columnconfigure(1, weight=1)
		self.notes_frame.grid_rowconfigure(1, weight=1)
		
	def setup_labels(self):
		today = date.today()
		self.checked_date_in_database = False
		self.data[today] = self.view.controller.read_date_from_database(today)
		
		self.top_label = tk.Label(self.date_frame, text=(today), font=self.title_font, anchor="w")
		#self.top_label.pack(fill=tk.BOTH, expand=True)
		self.top_label.grid(row=0, column=0, padx=self.view.default_padx)
		
		self.date = today
		self.update_top_label()
		
	def setup_buttons(self):
		ttk.Button(self.date_frame, text=u'\u2190', command=self.back_one_day, style='primary.TButton').grid(row=0, column=2, padx=2)
		ttk.Button(self.date_frame, image=self.view.calender_white_icon2, style='primary.Outline.TButton', command=self.calender_select).grid(row=0, column=3, padx=2)
		ttk.Button(self.date_frame, text=u'\u2192', command=self.forward_one_day, style='primary.TButton').grid(row=0, column=4, padx=2)
		self.date_frame.grid_columnconfigure(1, weight=1)
		
		toolbar = ttk.Frame(self.notes_frame)
		toolbar.grid(row=0, column=0, columnspan=3, sticky="W", padx=self.view.default_padx, pady=(self.view.default_pady, 0))
		
		ttk.Button(toolbar, text="B", width=3, command=lambda: self.toggle_tag("bold"), style='primary.TButton').grid(row=0, column=0, padx=1)
		ttk.Button(toolbar, text="I", width=3, command=lambda: self.toggle_tag("italic"), style='primary.TButton').grid(row=0, column=1, padx=1)
		ttk.Button(toolbar, text="U", width=3, command=lambda: self.toggle_tag("underline"), style='primary.TButton').grid(row=0, column=2, padx=1)
		ttk.Button(toolbar, text="S", width=3, command=lambda: self.toggle_tag("strikethrough"), style='primary.TButton').grid(row=0, column=3, padx=1)
		ttk.Button(toolbar, text="HL", width=4, command=lambda: self.toggle_tag("highlight"), style='primary.TButton').grid(row=0, column=4, padx=(6, 1))
		ttk.Button(toolbar, text="Color", command=self.apply_text_color, style='primary.TButton').grid(row=0, column=5, padx=1)
		ttk.Button(toolbar, text="Clear", command=self.clear_formatting, style='secondary.TButton').grid(row=0, column=6, padx=1)
		ttk.Button(toolbar, image=self.view.bullet_point_dark_icon2, command=self.add_bullet_point, style='primary.TButton').grid(row=0, column=7, padx=(6, 1))
		ttk.Button(toolbar, text=u"\u2610", width=3, command=self.toggle_checklist_line, style='primary.TButton').grid(row=0, column=8, padx=1)
		ttk.Button(toolbar, text="Save", command=self.save_current_date, style='success.TButton').grid(row=0, column=9, padx=(6, 1))

		style_menu_button = ttk.Menubutton(toolbar, text="Style", style='primary.TButton')
		style_menu_button.grid(row=0, column=10, padx=(6, 1))
		style_menu = tk.Menu(style_menu_button, tearoff=0)
		style_menu_button["menu"] = style_menu
		style_menu.add_command(label="Normal", command=self.clear_paragraph_style)
		style_menu.add_command(label="Heading", command=lambda: self.apply_line_tag("heading"))
		style_menu.add_command(label="Subheading", command=lambda: self.apply_line_tag("subheading"))
		style_menu.add_command(label="Code", command=lambda: self.apply_line_tag("code"))
		style_menu.add_command(label="Quote", command=lambda: self.apply_line_tag("quote"))
		
	def back_one_day(self):
		self.save_current_date()
		self.date = self.date - datetime.timedelta(days=1)
		self.date_changed()
		
	def forward_one_day(self):
		self.save_current_date()
		self.date = self.date + datetime.timedelta(days=1)
		self.date_changed()

	def calender_select(self):
		self.save_current_date()
		w = dialogs.DatePickerDialog()
		self.date = w.date_selected
		self.date_changed()

	def setup_text_widget(self):
		self.general_text = tk.Text(self.notes_frame, wrap="word", undo=True, font=self.body_font)# width=110, height=10)
		#self.general_text.pack(side=LEFT, expand=True, fill=BOTH, padx=self.mainapp.default_padx, pady=self.mainapp.default_pady)
		self.general_text.grid(row=1, column=0, columnspan=2, sticky="NSEW", padx=self.view.default_padx, pady=self.view.default_pady)
		
		vsb = autoscrollbar.AutoScrollbar(self.notes_frame, orient="vertical", command=self.general_text.yview)
		vsb.grid(row=1, column=2, columnspan=1, sticky="NS")
		
		self.general_text.configure(yscrollcommand=vsb.set)
		self.setup_text_tags()
		
		# Add any text present in database_thread
		txt = self.view.controller.read_date_from_database(self.date)
		self.load_note_data(txt["General"])
		self.general_text.bind('<Return>', self.enter_event)
		self.general_text.bind('<Tab>', self.tab_event)
		self.general_text.bind('<Control-b>', lambda event: self.shortcut_event(event, "bold"))
		self.general_text.bind('<Control-i>', lambda event: self.shortcut_event(event, "italic"))
		self.general_text.bind('<Control-u>', lambda event: self.shortcut_event(event, "underline"))
		self.general_text.bind('<Control-s>', self.save_shortcut_event)
		self.general_text.bind('<Control-Return>', self.checklist_shortcut_event)

	def setup_text_tags(self):
		self.format_tags = [
			"bold", "italic", "underline", "strikethrough", "highlight",
			"text_color", "heading", "subheading", "code", "quote",
		]
		self.paragraph_tags = ["heading", "subheading", "code", "quote"]
		self.general_text.tag_configure("bold", font=self.bold_font)
		self.general_text.tag_configure("italic", font=self.italic_font)
		self.general_text.tag_configure("underline", underline=True)
		self.general_text.tag_configure("strikethrough", overstrike=True)
		self.general_text.tag_configure("highlight", background="#fff3a3")
		self.general_text.tag_configure("text_color", foreground="#d63384")
		self.general_text.tag_configure("heading", font=self.heading_font, spacing1=8, spacing3=4)
		self.general_text.tag_configure("subheading", font=self.subheading_font, spacing1=6, spacing3=3)
		self.general_text.tag_configure("code", font=self.code_font, background="#202020", foreground="#f2f2f2", lmargin1=8, lmargin2=8)
		self.general_text.tag_configure("quote", lmargin1=18, lmargin2=18, foreground="#6c757d")

	def get_selection_range(self):
		try:
			return self.general_text.index("sel.first"), self.general_text.index("sel.last")
		except tk.TclError:
			return None, None

	def toggle_tag(self, tag):
		start, end = self.get_selection_range()
		if start is None:
			return
		
		if tag in self.general_text.tag_names("sel.first"):
			self.general_text.tag_remove(tag, start, end)
		else:
			self.general_text.tag_add(tag, start, end)
		
	def apply_line_tag(self, tag):
		start, end = self.get_selected_line_range()
		for paragraph_tag in self.paragraph_tags:
			self.general_text.tag_remove(paragraph_tag, start, end)
		self.general_text.tag_add(tag, start, end)

	def clear_paragraph_style(self):
		start, end = self.get_selected_line_range()
		for paragraph_tag in self.paragraph_tags:
			self.general_text.tag_remove(paragraph_tag, start, end)

	def get_selected_line_range(self):
		start, end = self.get_selection_range()
		if start is None:
			start = self.general_text.index("insert")
			end = start
		start_line = start.split(".")[0]
		end_line = end.split(".")[0]
		return f"{start_line}.0", f"{end_line}.end"

	def apply_text_color(self):
		start, end = self.get_selection_range()
		if start is None:
			return
		
		color = colorchooser.askcolor(parent=self.top, title="Choose Text Color")[1]
		if color is None:
			return
		
		tag = f"text_color_{color.replace('#', '')}"
		if tag not in self.format_tags:
			self.format_tags.append(tag)
		self.general_text.tag_configure(tag, foreground=color)
		self.general_text.tag_add(tag, start, end)

	def clear_formatting(self):
		start, end = self.get_selection_range()
		if start is None:
			return
		
		for tag in self.general_text.tag_names():
			if tag != "sel":
				self.general_text.tag_remove(tag, start, end)

	def shortcut_event(self, event, tag):
		self.toggle_tag(tag)
		return "break"

	def save_shortcut_event(self, event):
		self.save_current_date()
		return "break"

	def checklist_shortcut_event(self, event):
		self.toggle_checklist_line()
		return "break"

	def add_bullet_point(self):
		self.general_text.insert("insert", u"\u2022" + " ")
		
	def enter_event(self, event):
		multiple_lines_selected, first_line, last_line = self.check_if_multiple_lines_selected()
		
		if multiple_lines_selected is False:
			current_pos = self.general_text.index(tk.INSERT)
			current_line = current_pos.split(".")[0]
			line_text = self.general_text.get(f"{current_line}.0", f"{current_line}.end")
			
			bullet_type = None
			if line_text.lstrip().startswith(u"\u2022"):
				bullet_type = u"\u2022"
			elif line_text.lstrip().startswith("-"):
				bullet_type = "-"
				
			if bullet_type is not None:
				leading_text = line_text[:line_text.index(bullet_type)]
			
				self.general_text.insert(current_pos, "\n" + leading_text + bullet_type)
				
				return "break"
		
	def get_text_input(self):
		self.data[self.date] = {"General": self.serialize_note_data()}

	def serialize_note_data(self):
		note_data = {"text": self.general_text.get("1.0", "end-1c"), "tags": []}
		
		for tag in self.general_text.tag_names():
			if tag == "sel":
				continue
			
			ranges = self.general_text.tag_ranges(tag)
			for idx in range(0, len(ranges), 2):
				note_data["tags"].append({
					"tag": tag,
					"start": str(ranges[idx]),
					"end": str(ranges[idx + 1]),
					"options": self.get_serializable_tag_options(tag),
				})
		
		return note_data

	def get_serializable_tag_options(self, tag):
		if tag.startswith("text_color_"):
			return {"foreground": self.general_text.tag_cget(tag, "foreground")}
		return {}

	def load_note_data(self, note_data):
		self.general_text.delete("1.0", "end")
		note_data = normalise_note_data(note_data)
		self.general_text.insert("end", note_data["text"])
		for tag_range in note_data["tags"]:
			tag = tag_range.get("tag")
			start = tag_range.get("start")
			end = tag_range.get("end")
			if not tag or not start or not end:
				continue
			
			options = tag_range.get("options", {})
			if options:
				self.general_text.tag_configure(tag, **options)
			if tag not in self.format_tags:
				self.format_tags.append(tag)
			self.general_text.tag_add(tag, start, end)

	def save_current_date(self):
		self.get_text_input()
		self.view.controller.write_diary_text_to_database(self.date, self.data[self.date])

	def autosave(self):
		if self.top.winfo_exists():
			self.save_current_date()
			self.autosave_job = self.top.after(60000, self.autosave)
		
	def date_changed(self):
		self.general_text.delete(1.0, "end",)
	
		if self.date not in self.data.keys():
			self.data[self.date] = self.view.controller.read_date_from_database(str(self.date))
			
		self.load_note_data(self.data[self.date]["General"])
		self.update_top_label()
		
	def update_top_label(self):
		date_text = f"{self.date.strftime('%d')} {self.date.strftime('%B')} {self.date.strftime('%Y')}"
		self.top_label.config(text=date_text)

	def cut(self, event):
		if self.general_text.selection_get():
			self.selected = self.general_text.selection_get()
			self.selected.delete("sel.first", "self.last")
		
	def copy(self, event):
		print("Copying")

	def paste(self, event):
		print("Copying")
		
	def tab_event(self, event):
		current_pos = self.general_text.index(tk.INSERT)
		
		multiple_lines_selected, first_line, last_line = self.check_if_multiple_lines_selected()
		
		if not multiple_lines_selected:
			self.general_text.insert(current_pos, "\t")
		else:
			for line in range(int(first_line), int(last_line)+1):
				self.general_text.insert(f"{line}.0", "\t")
				
		return "break"

	def toggle_checklist_line(self):
		current_pos = self.general_text.index(tk.INSERT)
		current_line = current_pos.split(".")[0]
		line_start = f"{current_line}.0"
		line_end = f"{current_line}.end"
		line_text = self.general_text.get(line_start, line_end)
		stripped_text = line_text.lstrip()
		leading_text = line_text[:len(line_text) - len(stripped_text)]
		
		if stripped_text.startswith(u"\u2610 "):
			checkmark_start = f"{current_line}.{len(leading_text)}"
			checkmark_end = f"{current_line}.{len(leading_text) + 1}"
			self.general_text.delete(checkmark_start, checkmark_end)
			self.general_text.insert(checkmark_start, u"\u2611")
		elif stripped_text.startswith(u"\u2611 "):
			checkmark_start = f"{current_line}.{len(leading_text)}"
			checkmark_end = f"{current_line}.{len(leading_text) + 1}"
			self.general_text.delete(checkmark_start, checkmark_end)
			self.general_text.insert(checkmark_start, u"\u2610")
		else:
			self.general_text.insert(f"{current_line}.{len(leading_text)}", u"\u2610 ")
		
	def check_if_multiple_lines_selected(self):
		multiple_lines_selected = False
		first_line = None
		last_line = None
		
		try:
			first_line = self.general_text.index("sel.first").split(".")[0]
			last_line = self.general_text.index("sel.last").split(".")[0]
			
			if first_line != last_line:
				multiple_lines_selected = True
		except Exception as e:
			if 'contain any characters tagged with "sel"' in str(e):
				pass
			else:
				self.view.show_error(str(e))
				
		return multiple_lines_selected, first_line, last_line
