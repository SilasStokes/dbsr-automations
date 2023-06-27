import csv
import tkinter as tk
from tkinter import filedialog #, messagebox

r"""
Setup:
1) Download and install python on the computer.
2) Save this file as "convert_cirrus_to_soundexchange.py", note the absolute path of where you save the file - should be something like: "C:\Users\DBS Radio Intern\code\sound_exchange\convert_cirrus_to_soundexchange.py"
3) Find the executable location of python by running: `python -c "import sys; print(sys.executable);"` in the windows command line
4) create a new .bat file on the desktop (can be done with notepad or vscode) with the contents of
        @echo off
        "C:\Python311\python.exe" "C:\Users\DBS Radio Intern\code\sound_exchange\convert_cirrus_to_soundexchange.py"
    but with the path to the python executable replaced with the output of step 3 and and python script path replaced with the location saved in step 2. 
5) Double click the .bat file on the desktop and it will run the file which will prompt you to select the input location of the csv file downloaded from cirrus and the prompt you to select the output location.
"""

def process_file(input_path: str, output_path:str):
    # Open the input CSV file
    with open(input_path, 'r', encoding='utf-8') as csv_infile:
        reader = csv.DictReader(csv_infile)

        # Open the output CSV file
        with open(output_path, 'w', newline='', encoding='utf-8') as csv_outfile:
            # Define the field names for the output file
            fieldnames = ["Name Of Service", "Transmission Category Code", "Sound Recording Title",
                          "Featured Artist", "Album Title", "ISRC", "Actual Total Performances (ATP)"]

            writer = csv.DictWriter(csv_outfile, fieldnames=fieldnames)

            # Write the headers to the output file
            writer.writeheader()

            # Process each row in the input file
            for row in reader:
                # Handle missing values
                # for key in row:
                #     if row[key] == '':
                #         row[key] = 'N/A'

                # Write the corresponding data to the output file
                writer.writerow({
                    "Name Of Service": "DSR",
                    "Transmission Category Code": "A",
                    "Sound Recording Title": row["TITLE"],
                    "Featured Artist": row["ARTIST"],
                    "Album Title": row["ALBUM"],
                    "ISRC": row["ISRC"],
                    "Actual Total Performances (ATP)": row["PERFORMANCES"]
                })
    # messagebox.showinfo("Success", f"File processed successfully! Output saved as {output_path}") # type: ignore

def open_files():
    input_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if input_path:
        output_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="MONTH 2023 SoundExchange Report Of Use.csv", filetypes=[("CSV files", "*.csv")])
        if output_path:
            process_file(input_path, output_path)

root = tk.Tk()
root.withdraw()  # Hide the main window
open_files()  # Run the open_file function
