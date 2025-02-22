# This is just a whole bunch of functions I have that I might use in new project.

import csv
import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar, Treeview, Combobox, Checkbutton
import chardet as crd

# Check if elements are unique


def isUnique(comboboxes: dict) -> bool:
    Combo_Keys: list = comboboxes.keys()
    seen = set()
    return not any(i in seen or seen.add(i) for i in Combo_Keys)

# data type to keep our stuff arround


class DataStorage:
    def __init__(self, csv_file: str = None, ldif_file: str = None):
        # Names of the files in use
        self.InFile: str = csv_file
        self.OutFile: str = ldif_file
        # Extracted list of dictionaries
        self.Data: list[dict] = None
        # Headers from data
        self.Headers: list = None
        # ldap entries
        # required to get
        self.OU: str = None
        self.O: str = None
        # optional entry must be example.com and split into dc=example, dc=com
        self.DC: str = None
        self.file_enc = 'utf-8'
        self.REQUIRED_COLUMNS: set = {
            'First Name', 'Last Name', 'Email Address', 'Status'}
    # set name of the input file and path to it

    def set_input(self, file_path: str = None) -> tuple[bool, str]:
        try:
            if not file_path:
                print("exited first if in set input")
                return False, "No file path"
            else:
                self.InFile = file_path
                print("set file ok")
                return True, "File path set"
        except Exception as e:
            result: str = f"Something went wrong, error {e}"
            print(result)
            return False, result
    # set name of output file and path to ir

    def set_output(self, file_path: str = None) -> tuple[bool, str]:
        try:
            if not file_path:
                return False, "No file path"
            else:
                self.OutFile: str = file_path
                return True, "File path set"
        except Exception as e:
            result: str = f"Something went wrong, error {e}"
            print(result)
            return False, result
    # get encoding of input file

    def det_encoding(self, file: str = None) -> None:
        """
        Detects the encoding of file and returns it as str
        Args:
            file (str): File name of source *.csv file

        Returns:
            str: Returns the encoding of source csv file

        """
        with open(file, 'rb') as rawdata:
            result = crd.detect(rawdata.read())
            self.file_enc = result['encoding']
            print(self.file_enc)
    # Set Data and get header, check for validity of header and 0 length
    # input csv.DictReader out bool and result message

    def set_data(self, reader: csv.DictReader = None) -> tuple[bool, str]:
        try:
            print("called set data")
            if not reader and not self.InFile:
                print("exited first if on set data")
                # rework if no reader passed check if self.InFle !None and use it for to process
                return False, "Pass a valid file or set set_input(file)"
            # process file
            if reader:
                print("Processed for reader")
                self.Data: list[dict] = list(reader)
                self.Headers: list = reader.fieldnames
                if not self.Headers:
                    return False, "No headers in file"
                if len(self.Data) == 1:
                    return False, "File contains headers only"
                if any(header is None for header in self.Headers):
                    return False, "Bad Header format, recreate CSV"
                return True, "Data and Header set successfully"
            if self.InFile and not reader:
                print("processed for self.InFile")
                self.det_encoding(self.InFile)
                with open(self.InFile, 'r', encoding=self.file_enc, errors='replace') as f:
                    reader = csv.DictReader(f)
                    self.Data: list[dict] = list(reader)
                    self.Headers: list = reader.fieldnames
                    print(self.Headers)
                    if not self.Headers:
                        return False, "No headers in file"
                    if len(self.Data) == 1:
                        return False, "File contains headers only"
                    if any(header is None for header in self.Headers):
                        return False, "Bad Header format, recreate CSV"
                    if not self.REQUIRED_COLUMNS.issubset(self.Headers):
                        return False, "CSV file does not have the required columns."
                    return True, "Data and Header set successfully"
            print("Did nothing")
        except Exception as e:
            result = f"Something went wrong, {e}"
            return False, result

    def set_required_columns(self, INPUT_REQUIRED_COLUMNS: set) -> tuple[bool, str]:
        self.REQUIRED_COLUMNS.clear()
        self.REQUIRED_COLUMNS.update(INPUT_REQUIRED_COLUMNS)
        return True, f"Required columns set to {self.REQUIRED_COLUMNS}"


# required columns in our file
REQUIRED_COLUMNS = {'First Name', 'Last Name', 'Email Address', 'Status'}
# Meat and potato of script
# progress bar update function


def create_dn_entry(row: dict, ou_value: str, o_value: str, dc_value: str | None = None) -> tuple[str, str, str, str, str]:
    first_name = row['First Name']
    last_name = row['Last Name']
    cn = first_name
    if dc_value:
        dc_parts: list = dc_value.split('.')
        if len(dc_parts) == 2:
            # dn = f"dn: cn={cn},ou={ou_value},o={o_value},dc={dc_value.split('.')[0]},dc={dc_value.split('.')[1]}\n"
            dn = f"dn: cn={cn},ou={ou_value},o={
                o_value},dc={dc_parts[0]},dc={dc_parts[1]}\n"
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
        if file_path:
            ldif_file: str = filedialog.asksaveasfilename(
                defaultextension=".ldif", filetypes=[("LDIF files", "*.ldif")])
            if ldif_file:
                csv_to_ldif(file_path, ldif_file, ou_value, o_value, dc_value)

    except Exception as e:
        result_label.config(
            text=f"Something went wrong while opening files, error: {e}!")


if __name__ == "__main__":
    print("You Should not start this file")
