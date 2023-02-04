# Tk-Path-Finder ![python](https://img.shields.io/badge/python-3.6+-blue)

## Description
A lightweight file explorer based on tabs within tabs written in python (Tkinter). Written primarily to assist working with text files and MS office files spread across many folders/servers.

## Running the App
To run, download the code, unzip the files and run the main.py file. You will need several python libraries installed which are listed further below.

Note the app creates 2 files, "tk_path_finder_config.json" and "notes.db" (sqlite database). These will be created in the default working directory. The json file stores all links and tabs created by the user. Several backups are automatically generated for this file. The database contains any notes entered into the diary.

## Features
  - Quick Access Sidebar, links can be grouped into individual folders.
  - Tabs within tabs layout.
  - Tabs can be reordered.
  - Load Last Session.
  - Search functionality.
  - Sort by date/file type
  - Filter by file extension.
  - Filter files containing string.
  - Rename files and folders.
  - Cut/Copy Files using the default windows dialog.
  - Create multiple folders at once (hit cntrl-d in the craete folder window to duplicate line).
  - "Open with" functionality.
  - Compatible with MS Teams folders.
  - To Do List.
  - Diary.
  - PDF Tools
		- Extract Pages.
		- Merge PDFs.
  - Dark and Light themes.

## Limitations
  - Only tested on windows 10.
  - No delete functionality.
  - Search is very slow on sub-directories with many files.

## Prerequisites

[natsort](https://natsort.readthedocs.io/en/master/)

[openpycl](https://openpyxl.readthedocs.io/en/stable/)

[pyperclip](https://pypi.org/project/pyperclip/)

[python-docx](https://python-docx.readthedocs.io/en/latest/)

[ttkbootstrap](https://ttkbootstrap.readthedocs.io/en/latest/)

[PyPDF2](https://pypi.org/project/PyPDF2/)

pip install natsort

pip install openpyxl

pip install pyperclip

pip install python-docx

pip install ttkbootstrap

pip install PyPDF2


## Preview
![alt text](https://imgur.com/hPORcAR.png)

![alt text](https://imgur.com/trjQ4QE.png)

![alt text](https://imgur.com/haNY5f5.png)

![alt text](https://i.imgur.com/oJ79w68.png)

![alt text](https://i.imgur.com/Ms0HQ7l.png
)
![alt text](https://i.imgur.com/C4p6s9J.png)

![alt text](https://i.imgur.com/AOYEmRY.png)

![alt text](https://imgur.com/wvWuekP.png)




