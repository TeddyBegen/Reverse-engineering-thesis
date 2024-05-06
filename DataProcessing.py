import sqlite3

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


def create_function_list(database_path):
    # Connect to the database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Retrieve function names from the database
    cursor.execute("SELECT name1 FROM filteredfunction")  
    function_names_apk1 = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT name2 FROM filteredfunction")  
    function_names_apk2 = [row[0] for row in cursor.fetchall()]


    # Close the database connection
    conn.close()
    print(f"Total function names from apk1 retrieved: {len(function_names_apk1)}")
    print(f"Total function names from apk2 retrieved: {len(function_names_apk2)}")


def find_lines_with_words(filename, target_words):
    found_lines = []  # Define the variable "found_lines" as an empty list
    line_counter = 0  # Initialize a line counter variable

    with open(filename, 'r') as file:
        for line in file:
            line_counter += 1  # Increment the line counter
            for word in target_words:
                if word in line:
                    found_lines.append((word, line_counter))  # Append the word, line number, and line itself
    
    return found_lines