# Import modules
import csv
import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar, Treeview, Combobox, Checkbutton
import chardet as crd
from my_functions import DataStorage as DS
# redo when rest of code done
csv_object: DS = DS
comboboxes: dict = []


def validate_selections(comboboxes: dict) -> None:
    raise ValueError("To be implemented")


def open_file_and_process() -> None:
    try:
        # check if ou and o values are present or not
        o_value: str = o_entry.get()
        ou_value: str = ou_entry.get()
        dc_value: str = dc_entry.get()
        if not ou_value or not o_value:
            result_label.config(text="Enter OU and O")
            return

        file_path: str = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")])
        # print(file_path)
        if file_path:
            csv_object.set_input(file_path)
            print(file_path)
            # call function to populate treeview
    except Exception as e:
        result_label.config(
            text=f"Something went wrong while opening files, error: {e}!")


def process_ldif() -> None:
    raise ValueError("To be implemented")


# main body
if __name__ == "__main__":
    app = tk.Tk()
    app.title("CSV to LDIF Converter")
    app.geometry("700x700")

    REQUIRED_COLUMNS = {'cn', 'sn', 'mail'}
    ldap_attributes = ["n/a", "cn", "sn", "givenName",
                       "mail", "uid", "o", "ou", "dc", "password"]

    tree = Treeview(app)
    tree.grid(row=1, column=0, columnspan=1, sticky='nsew')

    validate_button = tk.Button(
        app, text="Validate Selections", command=lambda: validate_selections(comboboxes))
    validate_button.grid(row=2, column=0, columnspan=1, pady=10)

    open_button = tk.Button(app, text="Open CSV File",
                            command=open_file_and_process)
    open_button.grid(row=3, column=0, columnspan=1, pady=10)

    save_ldif_button = tk.Button(app, text="Save LDIF", command=process_ldif)
    save_ldif_button.grid(row=4, column=0, columnspan=1, pady=10)

    skip_suspended_var = tk.BooleanVar()
    skip_suspended_check = tk.Checkbutton(
        app, text="Skip Suspended", variable=skip_suspended_var)
    skip_suspended_check.grid(row=5, column=0, columnspan=1, pady=10)

    progress_bar = Progressbar(
        app, orient="horizontal", length=300, mode="determinate")
    progress_bar.grid(row=6, column=0, columnspan=1, pady=10)

    progress_label = tk.Label(app, text="Waiting for Input!")
    progress_label.grid(row=7, column=0, columnspan=1, pady=10)
    o_label = tk.Label(app, text="Organization (o):")
    o_entry = tk.Entry(app)
    result_label = tk.Label(app, text="Open the CSV file!")
    result_label.grid(row=11, column=0, padx=5, sticky="w")
    ou_label = tk.Label(app, text="Organizational Unit (ou):")
    ou_entry = tk.Entry(app)

    dc_label = tk.Label(app, text="Domain Component (dc) ea example.com:")
    dc_entry = tk.Entry(app)

    o_label.grid(row=8, column=0, pady=5, sticky="e")
    o_entry.grid(row=8, column=1, pady=5, sticky="w")

    ou_label.grid(row=9, column=0, pady=9, sticky="e")
    ou_entry.grid(row=9, column=1, pady=9, sticky="w")

    dc_label.grid(row=10, column=0, pady=5, sticky="e")
    dc_entry.grid(row=10, column=1, pady=5, sticky="w")

    app.mainloop()
