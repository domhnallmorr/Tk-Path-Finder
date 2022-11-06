# Python program to illustrate the usage of 
# autohiding scrollbars using tkinter
   
# Importing tkinter
from tkinter import *
from tkinter import ttk
   
# Creating class AutoScrollbar
class AutoScrollbar(ttk.Scrollbar):
       
    # Defining set method with all 
    # its parameter
    def set(self, low, high):
           
        if float(low) <= 0.0 and float(high) >= 1.0:
               
            # Using grid_remove
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, low, high)
       
    # Defining pack method
    def pack(self, **kw):
           
        # If pack is used it throws an error
        raise (TclError,"pack cannot be used with \
        this widget")
       
    # Defining place method
    def place(self, **kw):
           
        # If place is used it throws an error
        raise (TclError, "place cannot be used  with \
        this widget")