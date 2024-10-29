import csv
import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar, Treeview, Combobox, Checkbutton


# Define required columns
REQUIRED_COLUMNS = {'cn', 'sn', 'mail'}

# Initialize global variable
work_rows = []
comboboxes = {}


def get_dropdown_values(comboboxes) -> dict:
    result = {combobox_value.get(): col_key for col_key, combobox_value in comboboxes.items()}
    print(result) 
    return result


def validate_selections(comboboxes):
    values = get_dropdown_values(comboboxes)
    selected_attributes = set(values.keys())
    if not REQUIRED_COLUMNS.issubset(selected_attributes):
        missing_attributes = REQUIRED_COLUMNS - selected_attributes
        print(f"Missing attributes: {', '.join(missing_attributes)}")
    else:
        print("All required attributes are selected")


def process_csv(comboboxes: dict) -> list[dict]:
    global work_rows
    results = []

    values = get_dropdown_values(comboboxes)
    cn_column = values['cn']
    sn_column = values['sn']
    mail_column = values['mail']

    left_columns = set(values.keys()) - {'cn', 'sn', 'mail'}

    for row in work_rows:
        cn = row[cn_column]
        sn = row[sn_column]
        mail = row[mail_column]

        row_data = {
            "CN": cn,
            "SN": sn,
            "Mail": mail
        }
        if row['Status']:
            row_data['Status'] = row['Status']
        for attr in left_columns:
            if attr == "n/a":
                continue
            row_data[attr] = row[values[attr]]

        results.append(row_data)

    return results


def create_ldif_entries(data_to_process):
    ldif_entries = []
    for index, row in enumerate(data_to_process, start=0):
        dn = f"dn: cn={row['CN']},ou=SomeOU,o=SomeO,dc=example,dc=com"
        entry = f"""{dn}
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
cn: {row['CN']}
sn: {row['SN']}
mail: {row['Mail']}
"""
        for key, value in row.items():
            if key in ['CN', 'SN', 'Mail'] or key == "n/a" or key.lower() == 'status':
                continue

            entry += f"{key}: {value}\n"
        ldif_entries.append(entry)

        # Update the progress bar
        update_progress(index + 1, len(data_to_process))

    return ldif_entries


def write_ldif(ldif_entries, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        for entry in ldif_entries:
            f.write(entry + "\n")


def open_and_validate_csv() -> None:
    global work_rows
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            header = reader.fieldnames
            csv_size = len(rows)

            if not header or csv_size == 0:
                print("Empty CSV!")
                work_rows = []
                return
            if None in header:
                print("Invalid headers detected. Please check the CSV file.")
                work_rows = []
                return

            work_rows = rows
            populate_table(work_rows, ldap_attributes)


def populate_table(rows: list[dict], ldap_attributes: list[str]):
    global comboboxes
    if rows:
        tree.delete(*tree.get_children())  # Clear existing data
        tree["columns"] = ()
        tree["show"] = "tree"  # Temporarily hide column headings

        # Reset columns based on new data
        columns = list(rows[0].keys())
        tree["columns"] = columns
        tree["show"] = "headings"  # Show column headings again

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        for row in rows:
            tree.insert('', 'end', values=[row[col] for col in columns])

        # Create a frame for comboboxes to ensure proper alignment
        combobox_frame = tk.Frame(app)
        combobox_frame.grid(row=0, column=0, columnspan=len(
            columns), padx=5, pady=5, sticky='ew')

        # Create the dropdowns for the first row (header)
        for col in columns:
            combobox = Combobox(
                combobox_frame, values=ldap_attributes, width=15)
            combobox.grid(row=0, column=columns.index(col), padx=5, pady=5)
            combobox.set("n/a")
            comboboxes[col] = combobox

    return comboboxes


def process_and_save_ldif():
    global comboboxes
    processed_data = process_csv(comboboxes)
    print(comboboxes)
    if skip_suspended_var.get():
        active_users = [
            row for row in processed_data if row['Status'].lower() == 'active']
        active_users_count = len(active_users)
        print(active_users)
    else:
        active_users = processed_data
        active_users_count = len(processed_data)
        print(active_users)

    progress_bar["maximum"] = active_users_count

    ldif_entries = create_ldif_entries(active_users)

    ldif_file_path = filedialog.asksaveasfilename(
        defaultextension=".ldif", filetypes=[("LDIF files", "*.ldif")])
    if ldif_file_path:
        write_ldif(ldif_entries, ldif_file_path)


def open_file_and_populate():
    global work_rows
    open_and_validate_csv()
    if work_rows:
        global comboboxes
        populate_table(work_rows, ldap_attributes)


def process_ldif():
    global comboboxes
    if 'comboboxes' in globals():
        process_and_save_ldif()
    else:
        print("No data to process.")


def update_progress(index: int, total_users: int) -> None:
    progress_label.config(text=f"Creating user {index} of {total_users}")
    progress_bar["value"] = index
    app.update_idletasks()


if __name__ == "__main__":
    app = tk.Tk()
    app.title("CSV to LDIF Converter")
    app.geometry("700x500")

    data = [
        ['Name', 'Last Name', 'Email', 'Password', 'Status'],
        ['John', 'Doe', 'john@example.com', '2025', 'active'],
        ['Jane', 'Smith', 'jane@example.com', '2026', 'suspended'],
    ]

    REQUIRED_COLUMNS = {'cn', 'sn', 'mail'}
    ldap_attributes = ["n/a", "cn", "sn", "givenName",
                       "mail", "uid", "o", "ou", "dc", "password"]

    tree = Treeview(app)
    tree.grid(row=1, column=0, columnspan=len(data[0]), sticky='nsew')

    validate_button = tk.Button(
        app, text="Validate Selections", command=lambda: validate_selections(comboboxes))
    validate_button.grid(row=2, column=0, columnspan=len(data[0]), pady=10)

    open_button = tk.Button(app, text="Open CSV File",
                            command=open_file_and_populate)
    open_button.grid(row=3, column=0, columnspan=len(data[0]), pady=10)

    save_ldif_button = tk.Button(app, text="Save LDIF", command=process_ldif)
    save_ldif_button.grid(row=4, column=0, columnspan=len(data[0]), pady=10)

    skip_suspended_var = tk.BooleanVar()
    skip_suspended_check = tk.Checkbutton(
        app, text="Skip Suspended", variable=skip_suspended_var)
    skip_suspended_check.grid(
        row=5, column=0, columnspan=len(data[0]), pady=10)

    progress_bar = Progressbar(
        app, orient="horizontal", length=300, mode="determinate")
    progress_bar.grid(row=6, column=0, columnspan=len(data[0]), pady=10)

    progress_label = tk.Label(app, text="Waiting for Input!")
    progress_label.grid(row=7, column=0, columnspan=len(data[0]), pady=10)

    app.mainloop()
