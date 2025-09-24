import sqlite3
import pandas as pd
try:
    #Connect to DB and create a cursor
    sqliteConnection = sqlite3.connect("../databases/Chinook_Sqlite.sqlite")
    cursor = sqliteConnection.cursor()
    print('DB Init')

    #Write a query and execute it with cursor
    query = 'SELECT * FROM InvoiceLine LIMIT 5;'
    cursor.execute(query)

    df = pd.DataFrame(cursor.fetchall())
    df.columns = [desc[0] for desc in cursor.description]

    #Fetch and output result
    df = pd.DataFrame(cursor.fetchall())
    print(df)
    #Close the cursor
    cursor.close()
#Handle errors
except sqlite3.Error as error:
    print('Error occured -',error)
#Close DB Connection irrespective of success of failure
finally:
    if sqliteConnection:
        sqliteConnection.close()
        print('SQLite Connection closed')