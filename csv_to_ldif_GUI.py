"""
"Oi mate! Ya got a loicense fer dat?"

MIT License

Copyright (c) 2024 Igor Putica

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
Info
---------------
Author: Igor Putica
Date: 2024-10-17
Version: 2.0
Description: This app converts google exported users from CSV to ldif for
Apache Directory Server. Format csv to have first name, last name, email and status.
If status is not active the script will not create entry. Added fields for ou and o
Modules Required:
- tkinter
- CSV


Usage:
1. Install the required modules using pip.
2. only for terminal version,Copy the csv file with google users in the same directory as script.
3. Run and follow instructions

Future Features:
- Add more data sources.
- Implement a GUI. {not gonna happen any time soon, happened Copilot did the tk thing for me}

"""

import csv
import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar
import chardet as crd

# required columns in our file
REQUIRED_COLUMNS = {'First Name', 'Last Name', 'Email Address', 'Status'}
# Meat and potato of script
# progress bar update function


def update_progress(index: int, total_users: int) -> None:
    """
    Updates the progress bar and label with the current progress.

    Args:
        index (int): The current user number being processed.
        total_users (int): The total number of users in the file.
    """
    progress_label.config(text=f"Creating user {index} of {total_users}")
    progress_bar["value"] = index
    app.update_idletasks()

# detect encoding


def det_encoding(file: str) -> str:
    """
    Detects the encoding of file and returns it as str
    Args:
        file (str): File name of source *.csv file

    Returns:
        str: Returns the encoding of source csv file

    """
    with open(file, 'rb') as rawdata:
        result = crd.detect(rawdata.read())
        return result['encoding']

# return dn


def create_dn_entry(row: dict, ou_value: str, o_value: str, dc_value: str | None = None) -> tuple[str, str, str, str, str]:
    first_name = row['First Name']
    last_name = row['Last Name']
    cn = f"{first_name} {last_name}"
    if dc_value:
        dc_parts: list = dc_value.split('.')
        if len(dc_parts) == 2:
            dn = f"dn: cn={cn},ou={ou_value},o={o_value},dc={
                dc_value.split('.')[0]},dc={dc_value.split('.')[1]}\n"
        else:
            raise ValueError("dc_value must be in 'domain.component' format")
    else:
        dn = f"dn: cn={cn},ou={ou_value},o={o_value}\n"
    email = row['Email Address']
    uid = f"{first_name[0].lower()}.{last_name.lower()}"
    # debug_label.config(text="Create dn entry ok!")
    return dn, first_name, last_name, email, uid
# validate csv file


def validate_csv(reader: csv.DictReader) -> tuple[bool, list[dict], int]:
    """
        Validates if csv file has appropriate headers and is not empty
    Args:
        reader (csv.DictReader): Input CSV file to process

    Returns:
        tuple[bool, list[dict], int]: Returns is valid, list of rows as DICTS, and total number of rows
    """
    # extract headers and check if required are there
    headers = reader.fieldnames
    if not headers or not REQUIRED_COLUMNS.issubset(headers):
        progress_label.config(
            text="CSV file does not have the required columns.")
        # if headers missing return false, empty list and 0 users
        return False, [], 0
    # transform csv to list of dictionaries
    all_rows: list[dict] = list(reader)
    active_rows: list[dict] = [
        row for row in all_rows if row['Status'].lower() == 'active']
    active_users: int = len(active_rows)
    # print(active_rows)
    # debug_label.configure(text=f"Active user count {active_users}")
    # number of user is equal to number of dictionaries
    total_users: int = len(all_rows)
    # check if empty
    if total_users == 0:
        progress_label.config(text="CSV file is empty")
        # if empty return false, mepty list and 0 users
        return False, [], 0

    return True, active_rows, active_users
# function to convert csv to ldif.


def csv_to_ldif(csv_file: str, ldif_file: str, ou_value: str, o_value: str, dc_value: str | None = None) -> None:
    try:
        progress_label.config(text="Creating LDIF, please wait!")
        # detect file encoding
        char_enc: str = det_encoding(csv_file)

        # open our csv file
        with open(csv_file, 'r', encoding=char_enc, errors='replace') as f:
            reader = csv.DictReader(f)

            # check if csv is valid and non empty
            is_valid, rows, total_users = validate_csv(reader)
            # get active users

            if not is_valid:
                return
            # check if user is active
            # set progres bar maximum to number of total users
            progress_bar["maximum"] = total_users
            # open ldif as write and start writing in it
            with open(ldif_file, 'w', encoding=char_enc) as ldif:
                for index, row in enumerate(rows, start=1):
                    # if row['Status'].lower() != 'active':
                    #     # if not active skip user
                    #     continue
                    # update progress bar
                    update_progress(index, total_users)
                    # create dn values
                    dn, cn, sn, email, uid = create_dn_entry(
                        row, ou_value, o_value, dc_value)                  # write them to our file
                    ldif.write(dn)
                    ldif.write("objectClass: inetOrgPerson\n")
                    ldif.write("objectClass: organizationalPerson\n")
                    ldif.write("objectClass: person\n")
                    ldif.write("objectClass: top\n")
                    ldif.write(f"cn: {cn}\n")
                    ldif.write(f"sn: {sn}\n")
                    ldif.write(f"givenName: {cn}\n")
                    ldif.write(f"displayName: {cn} {sn}\n")
                    ldif.write(f"mail: {email}\n")
                    ldif.write(f"uid: {uid}\n")
                    ldif.write("userPassword:: \n")
                    ldif.write("\n")
                    result_label.config(text="LDIF file created successfully!")
    # error handling
    except FileNotFoundError:
        # file not found error
        progress_label.config(text="")
        result_label.config(
            text="File not found. Please check the file path and try again.")
    except Exception as e:
        progress_label.config(text="")
        result_label.config(text=f"Something went wrong! Error: {e}")


# open file csv file dialog

def open_file() -> None:
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
            ldif_file: str = filedialog.asksaveasfilename(
                defaultextension=".ldif", filetypes=[("LDIF files", "*.ldif")])
            if ldif_file:
                csv_to_ldif(file_path, ldif_file, ou_value, o_value, dc_value)

    except Exception as e:
        result_label.config(
            text=f"Something went wrong while opening files, error: {e}!")


if __name__ == "__main__":

    app = tk.Tk()
    app.title("CSV to LDIF Converter")
    app.geometry("500x400")
    # Create a menu bar
    menu_bar = tk.Menu(app)

    # Create a File menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Open", command=open_file)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=app.quit)

    menu_bar.add_cascade(label="File", menu=file_menu)

    # Add the menu bar to the window
    app.config(menu=menu_bar)

    open_button = tk.Button(app, text="Open CSV File", command=open_file)
    # open_button.pack(pady=10)

    progress_bar = Progressbar(
        app, orient="horizontal", length=300, mode="determinate")
    # progress_bar.pack(pady=10)

    progress_label = tk.Label(app, text="Waiting for Input!")
    # progress_label.pack(pady=10)

    result_label = tk.Label(app, text="O and OU required, DC is optional!")
    # result_label.pack(pady=10)

    # Fields for o, ou and dc

    o_label = tk.Label(app, text="Organization (o):")
    # o_label.pack(pady=5)
    o_entry = tk.Entry(app)
    # o_entry.pack(pady=5)

    ou_label = tk.Label(app, text="Organizational Unit (ou):")
    # ou_label.pack(pady=5)
    ou_entry = tk.Entry(app)
    # ou_entry.pack(pady=5)

    dc_label = tk.Label(app, text="Domain Component (dc) ea example.com:")
    # dc_label.pack(pady=5)
    dc_entry = tk.Entry(app)
    # dc_entry.pack(pady=5)

# Layout using grid
    open_button.grid(row=0, column=0, columnspan=2, pady=10)
    progress_bar.grid(row=1, column=0, columnspan=2, pady=5)
    progress_label.grid(row=2, column=0, columnspan=2, pady=5)
    result_label.grid(row=3, column=0, columnspan=2, pady=5)

    o_label.grid(row=4, column=0, pady=5, sticky="e")
    o_entry.grid(row=4, column=1, pady=5, sticky="w")

    ou_label.grid(row=5, column=0, pady=5, sticky="e")
    ou_entry.grid(row=5, column=1, pady=5, sticky="w")

    dc_label.grid(row=6, column=0, pady=5, sticky="e")
    dc_entry.grid(row=6, column=1, pady=5, sticky="w")


# debuging stuff
    # debug_label = tk.Label(app, text="debug")
    # debug_label.grid(row=7, column=1)

    app.mainloop()
