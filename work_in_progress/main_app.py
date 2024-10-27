#Import modules
import csv
from logging import raiseExceptions
import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar, Treeview, Combobox, Checkbutton
import chardet as crd

#redo when rest of code done 
comboboxes:dict=[]
def validate_selection(comboboxes:dict)->None:
    raise ValueError("To be implemented")

#main body
if __name__ == "__main__":
    app = tk.Tk()
    app.title("CSV to LDIF Converter")
    app.geometry("700x500")


 
   

    REQUIRED_COLUMNS = {'cn', 'sn', 'mail'}
    ldap_attributes = ["n/a", "cn", "sn", "givenName", "mail", "uid", "o", "ou", "dc", "password"]

    tree = Treeview(app)
    tree.grid(row=1, column=0, columnspan=1, sticky='nsew')

    validate_button = tk.Button(app, text="Validate Selections", command=lambda: validate_selections(comboboxes))
    validate_button.grid(row=2, column=0, columnspan=1, pady=10)

    open_button = tk.Button(app, text="Open CSV File", command=open_file_and_populate)
    open_button.grid(row=3, column=0, columnspan=1, pady=10)

    save_ldif_button = tk.Button(app, text="Save LDIF", command=process_ldif)
    save_ldif_button.grid(row=4, column=0, columnspan=1, pady=10)

    skip_suspended_var = tk.BooleanVar()
    skip_suspended_check = tk.Checkbutton(app, text="Skip Suspended", variable=skip_suspended_var)
    skip_suspended_check.grid(row=5, column=0, columnspan=1, pady=10)

    progress_bar = Progressbar(app, orient="horizontal", length=300, mode="determinate")
    progress_bar.grid(row=6, column=0, columnspan=1, pady=10)

    progress_label = tk.Label(app, text="Waiting for Input!")
    progress_label.grid(row=7, column=0, columnspan=1, pady=10)

    app.mainloop()