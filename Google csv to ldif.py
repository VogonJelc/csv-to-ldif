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
Version: 1.0
Description: This app converts google exported users from CSV to ldif for
Apache Directory Server. Format csv to have first name, last name, email.

Modules Required:
- requests
- CSV
- os

Usage:
1. Install the required modules using pip.
2. Copy the csv file with google users in the same directory as script.
3. Run and follow instructions

Future Features:
- Add more data sources.
- Implement a GUI. {not gonna happen any time soon, happened Copilot did the tk thing for me}

"""

import csv
import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar

# required columns in our file
REQUIRED_COLUMNS = {'First Name', 'Last Name', 'Email Address', 'Status'}

# function to convert csv to ldif.


def csv_to_ldif(csv_file: str, ldif_file: str) -> None:
    try:
        progres_label.config(text="Creating LDIF, please wait!")
        # open our csv file
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            # get headers from csv
            headers: list[str] = reader.fieldnames
            # check if headers is empty or does not contain required columns
            if not headers or not REQUIRED_COLUMNS.issubset(headers):
                result_label.config(
                    text="CSV file does not have the required columns.")
                return
            # convert to list of dictionaries
            rows: list[dict] = list(reader)
            # get total number of users
            total_users: int = len(rows)
            if total_users == 0:
                # file empty return
                result_label.config(
                    text="CSV file is empty")
                return
            # set progres bar maximum to number of total users
            progress_bar["maximum"] = total_users
            # open ldif as write and start writing in it
            with open(ldif_file, 'w') as ldif:
                for index, row in enumerate(rows, start=1):
                    if row['Status'].lower() != 'active':
                        # if not active skip user
                        continue
                    # progress bar and label update
                    progres_label.config(text=f"Creating user {
                                         index} of {total_users}")
                    progress_bar["value"] = index
                    app.update_idletasks()
                    # get details from row list of dictionaries
                    first_name: str = row['First Name']
                    last_name: str = row['Last Name']
                    email: str = row['Email Address']
                    cn: str = first_name
                    sn: str = last_name
                    uid: str = f"{first_name[0].lower()}.{last_name.lower()}"
                    dn: str = f"dn: cn={
                        cn}+mail={email}+sn={last_name},ou=Staff,o=KSIMN\n"
                    ldif.write(dn)
                    ldif.write("objectClass: inetOrgPerson\n")
                    ldif.write("objectClass: organizationalPerson\n")
                    ldif.write("objectClass: person\n")
                    ldif.write("objectClass: top\n")
                    ldif.write(f"cn: {cn}\n")
                    ldif.write(f"sn: {sn}\n")
                    ldif.write(f"displayName: {first_name} {last_name}\n")
                    ldif.write(f"mail: {email}\n")
                    ldif.write(f"uid: {uid}\n")
                    ldif.write("userPassword:: \n")
                    ldif.write("\n")
    # error handling
    except FileNotFoundError:
        # file not found error
        progres_label.config(text="")
        result_label.config(
            text="File not found. Please check the file path and try again.")
    except Exception as e:
        progres_label.config(text="")
        result_label.config(text=f"Something went wrong! Error: {e}")


# open file csv file dialog

def open_file() -> None:
    try:
        file_path: str = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")])
        if file_path:
            ldif_file: str = filedialog.asksaveasfilename(
                defaultextension=".ldif", filetypes=[("LDIF files", "*.ldif")])
            if ldif_file:
                csv_to_ldif(file_path, ldif_file)
                result_label.config(text="LDIF file created successfully!")
    except Exception as e:
        result_label.config(
            text=f"Something went wrong while opening files, error: {e}!")


if __name__ == "__main__":

    app = tk.Tk()
    app.title("CSV to LDIF Converter")
    app.geometry("400x200")
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
    open_button.pack(pady=20)

    progress_bar = Progressbar(
        app, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)

    progres_label = tk.Label(app, text="")
    progres_label.pack(pady=20)

    result_label = tk.Label(app, text="")
    result_label.pack(pady=20)

    app.mainloop()
