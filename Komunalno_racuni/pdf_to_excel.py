import pandas as pd
import pdfplumber
import tkinter as tk
from tkinter import filedialog
from pandas import ExcelWriter


def convert_pdf_to_excel():
    # Open file dialog to select PDF
    pdf_path = filedialog.askopenfilename(
        title="Select PDF File", filetypes=(("PDF Files", "*.pdf"),))

    if pdf_path:
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=(("Excel Files", "*.xlsx"),))

        if save_path:
            with pdfplumber.open(pdf_path) as pdf:
                with ExcelWriter(save_path) as writer:
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        data = [line.split() for line in text.split('\n')]

                        # Create a DataFrame for each page
                        df = pd.DataFrame(data)

                        # Save each DataFrame to a separate sheet
                        sheet_name = f'Page_{i+1}'
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

            print(f"File saved as {save_path}")


# Create the main window
root = tk.Tk()
root.title("PDF to Excel Converter")

# Create a button to start the conversion process
convert_button = tk.Button(
    root, text="Convert PDF to Excel", command=convert_pdf_to_excel)
convert_button.pack(pady=20)

# Run the application
root.mainloop()
