import csv


def csv_to_ldif(csv_file: str, ldif_file: str) -> None:
    try:
        print("Creating LDIF, please wait!\n")
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            total_users = len(rows)
            with open(ldif_file, 'w') as ldif:
                for index, row in enumerate(rows, start=1):
                    if row['Status'].lower() != 'active':
                        continue
                    print(f"Creating user {index} of {total_users}\n")
                    first_name = row['First Name']
                    last_name = row['Last Name']
                    email = row['Email Address']
                    cn = first_name
                    uid = f"{first_name[0].lower()}.{last_name.lower()}"
                    dn = f"dn: cn={
                        cn}+mail={email}+sn={last_name},ou=Staff,o=KSIMN\n"
                    ldif.write(dn)
                    ldif.write("objectClass: inetOrgPerson\n")
                    ldif.write("objectClass: organizationalPerson\n")
                    ldif.write("objectClass: person\n")
                    ldif.write("objectClass: top\n")
                    ldif.write(f"cn: {cn}\n")
                    ldif.write(f"sn: {last_name}\n")
                    ldif.write(f"displayName: {first_name} {last_name}\n")
                    ldif.write(f"mail: {email}\n")
                    ldif.write(f"uid: {uid}\n")
                    ldif.write("userPassword:: \n")
                    ldif.write("\n")
    except Exception as e:
        print(f"Something went wrong! Error: {e}")


if __name__ == "__main__":
    csv_file = input("Enter the CSV filename: ")
    ldif_file = input("Enter the LDIF filename: ")
    csv_to_ldif(csv_file, ldif_file)
