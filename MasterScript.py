#
# Author: Adam Makowski
#
# 25/04/2024

import subprocess
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import zipfile
import glob
import shutil
import sqlite3


def select_files():
    """Open a file dialog to select APK files."""
    Tk().withdraw()
    filename = askopenfilename(title="Select APK file", filetypes=[("APK Files", "*.apk")])
    return filename


def unpack_apk(apk_path, output_dir):
    """Unpack APK if it hasn't been unpacked yet."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.listdir(output_dir):
        with zipfile.ZipFile(apk_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        print(f"APK unpacked at {output_dir}")
    else:
        print(f"APK has already been unpacked at {output_dir}, skipping unpacking.")


def analyze_with_ghidra(dex_files, output_dir, apk_name):
    """Run Ghidra headless analysis and export both BinExport and combined C/C++ code."""
    ghidra_headless = "C:/Users/tedlj/OneDrive/Desktop/ghidra/ghidra_11.0.3_PUBLIC/support/analyzeHeadless.bat"
    project_path = f"C:/Users/tedlj/OneDrive/Desktop/Exjobb_Script/Project_path_temp{apk_name}"

    # Ensure project directory is ready
    if not os.path.exists(project_path):
        os.makedirs(project_path)

    for dex_path in dex_files:
        base_name = os.path.splitext(os.path.basename(dex_path))[0]
        bin_export_path = os.path.join(output_dir, base_name + ".BinExport")
        c_output_path = os.path.join(output_dir, base_name + ".c")
        analysis_marker = bin_export_path + "_analysis_done.marker"

        if os.path.exists(analysis_marker):
            print(f"Analysis already completed for {dex_path}, skipping analysis.")
            continue

        args = [
            ghidra_headless, project_path, "tempProject", "-import", dex_path,
            "-postScript", "ExportBinAndC", bin_export_path, c_output_path,  # Pass paths to script
            "-scriptPath", "C:/Users/tedlj/OneDrive/Desktop/ghidra/ghidra_11.0.3_PUBLIC/Ghidra/Features/Base/ghidra_scripts",
            "-deleteProject"
        ]
        subprocess.run(args, check=True)
        print(f"Analysis and export completed for {dex_path}")

        # Mark analysis as done by creating a marker file
        with open(analysis_marker, 'w') as f:
            f.write("Analysis completed.")



def merge_bindiff_files(output_dir):
    """Merge BinDiff SQLite files into one."""
    all_bindiff_files = glob.glob(os.path.join(output_dir, "*.bindiff"))
    if len(all_bindiff_files) > 1:
        merged_db_path = os.path.join(output_dir, "merged_bindiff_results.db")

        with sqlite3.connect(merged_db_path) as merged_conn:
            merged_cursor = merged_conn.cursor()

            print(f"Total BinDiff files found: {len(all_bindiff_files)}")

            # Iterate over each BinDiff file
            for index, bindiff_file in enumerate(all_bindiff_files):
                print(f"Processing BinDiff file {index + 1}/{len(all_bindiff_files)}: {bindiff_file}")

                with sqlite3.connect(bindiff_file) as conn:
                    cursor = conn.cursor()

                    # Get the list of tables in the current BinDiff file
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()

                    # Iterate over each table in the current BinDiff file
                    for table in tables:
                        table_name = table[0]
                        print(f"Processing table: {table_name}")

                        # Retrieve the schema of the current table
                        cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}'")
                        schema = cursor.fetchone()[0]

                        # Create the corresponding table in the merged database
                        try:
                            merged_cursor.execute(schema)
                            print(f"Table {table_name} created.")
                        except sqlite3.OperationalError:
                            print(f"Table {table_name} already exists. Skipping creation.")

                        # Merge data from the current table
                        cursor.execute(f"SELECT * FROM {table_name}")
                        rows = cursor.fetchall()
                        print(f"Found {len(rows)} rows in table {table_name}.")
                        if rows:  # Check if there are any rows to merge
                            if "id" in schema:
                                placeholders = ','.join(['?' for _ in range(len(rows[0]))])
                                for row in rows:
                                    new_id = generate_unique_id(merged_cursor, table_name)
                                    if new_id is not None:
                                        row = (new_id,) + row[1:]
                                    merged_cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row)
                            else:
                                # If no "id" column exists, insert rows without modification
                                placeholders = ','.join(['?' for _ in range(len(rows[0]))])
                                for row in rows:
                                    merged_cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row)

            print(f"Merged Bindiff results saved to {merged_db_path}.")
    else:
        print("No need to merge, only one Bindiff file present.")


def generate_unique_id(cursor, table_name):
    """Generate a unique ID for a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    # Check if the table has an "id" column
    id_column_exists = any(col[1] == "id" for col in columns)

    if id_column_exists:
        # If an "id" column exists, retrieve the maximum ID
        cursor.execute(f"SELECT MAX(id) FROM {table_name}")
        max_id = cursor.fetchone()[0]
        return max_id + 1 if max_id is not None else 1
    else:
        # If no "id" column exists, return None
        return None


def run_bindiff(binexport1, binexport2, output_file):
    """Run BinDiff on two .BinExport files if analysis hasn't been done."""
    analysis_marker = output_file + "_analysis_done.marker"
    if os.path.exists(analysis_marker):
        print(f"BinDiff analysis already completed for: {output_file}, skipping.")
        return

    bindiff_executable = "C:/Program Files/BinDiff/bin/bindiff.exe"  # Adjust this to your BinDiff installation path
    output_dir = os.path.normpath(os.path.dirname(output_file))

    print(f"Running BinDiff on: {binexport1} and {binexport2}")

    bindiff_cmd = [
        bindiff_executable,
        '--primary=' + binexport1,
        '--secondary=' + binexport2,
        '--output_dir=' + output_dir
    ]

    try:
        subprocess.run(bindiff_cmd, check=True)
        print(f"BinDiff analysis completed for: {output_file}")
        # Mark analysis as done by creating a marker file
        with open(analysis_marker, 'w') as f:
            f.write("Analysis completed.")
    except subprocess.CalledProcessError as e:
        print(f"Error running BinDiff: {e}")
        print(f"Command: {' '.join(bindiff_cmd)}")

def filter_function_table(merged_db_path):

    # Connect to the database
    conn = sqlite3.connect(merged_db_path)
    cursor = conn.cursor()

    # Create a new table called "filteredfunction"
    cursor.execute('CREATE TABLE IF NOT EXISTS filteredfunction (id INT,address1 BIGINT,name1 TEXT,address2 BIGINT,name2 TEXT,similarity DOUBLE PRECISION,confidence DOUBLE PRECISION,flags INTEGER,algorithm SMALLINT,evaluate BOOLEAN,commentsported BOOLEAN,basicblocks INTEGER,edges INTEGER,instructions INTEGER,UNIQUE(address1, address2),PRIMARY KEY(id),FOREIGN KEY(algorithm) REFERENCES functionalgorithm(id))')  

    # Copy rows from "function" table to "filteredfunction" table where "simularity" is less than 0
    cursor.execute('INSERT INTO filteredfunction SELECT * FROM function WHERE similarity < 1')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()



def main():
    apk1 = select_files()
    apk2 = select_files()

    unpack_dir1 = f"output/unpacked_{os.path.splitext(os.path.basename(apk1))[0]}"
    unpack_dir2 = f"output/unpacked_{os.path.splitext(os.path.basename(apk2))[0]}"

    unpack_apk(apk1, unpack_dir1)
    unpack_apk(apk2, unpack_dir2)

    dex_files1 = glob.glob(os.path.join(unpack_dir1, "*.dex"))
    dex_files2 = glob.glob(os.path.join(unpack_dir2, "*.dex"))

    analyze_with_ghidra(dex_files1, unpack_dir1, os.path.splitext(os.path.basename(apk1))[0])
    analyze_with_ghidra(dex_files2, unpack_dir2, os.path.splitext(os.path.basename(apk2))[0])

    # Assuming dex files are similarly named in both directories
    for dex_file1, dex_file2 in zip(sorted(dex_files1), sorted(dex_files2)):
        binexport1 = os.path.splitext(dex_file1)[0] + ".BinExport"
        binexport2 = os.path.splitext(dex_file2)[0] + ".BinExport"
        output_file = binexport1.replace('.BinExport', '_diff')
        run_bindiff(binexport1, binexport2, output_file)

    # Merge BinDiff files into one
    merge_bindiff_files(os.path.dirname(output_file))

    # Filter the "function" table and copy the results to a new table
    merge_db_path = os.path.join(os.path.dirname(output_file), "merged_bindiff_results.db")
    filter_function_table(merge_db_path)


if __name__ == "__main__":
    main()
