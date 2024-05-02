import sqlite3

# Connect to the database
conn = sqlite3.connect('C:/Users/tedlj/OneDrive/Desktop/Exjobb_Script/Reverse-engineering-thesis-main/Finished_Diff/unpacked_Signal6.47.5_Apkpure/merged_bindiff_results.db')
cursor = conn.cursor()

# Create a new table called "filteredfunction"
cursor.execute('CREATE TABLE IF NOT EXISTS filteredfunction (id INT,address1 BIGINT,name1 TEXT,address2 BIGINT,name2 TEXT,similarity DOUBLE PRECISION,confidence DOUBLE PRECISION,flags INTEGER,algorithm SMALLINT,evaluate BOOLEAN,commentsported BOOLEAN,basicblocks INTEGER,edges INTEGER,instructions INTEGER,UNIQUE(address1, address2),PRIMARY KEY(id),FOREIGN KEY(algorithm) REFERENCES functionalgorithm(id))')  

# Copy rows from "function" table to "filteredfunction" table where "simularity" is less than 0
cursor.execute('INSERT INTO filteredfunction SELECT * FROM function WHERE similarity < 1')

# Commit the changes and close the connection
conn.commit()
conn.close()