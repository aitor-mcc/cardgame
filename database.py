import sqlite3 
from sqlite3 import Error 
import os 

 

def create_connection(path): 
    connection = None 
    try: 
        connection = sqlite3.connect(path, check_same_thread = False) 
        print("Connection to SQLite DB successful") 

    except Error as e: 
        print(f"The error '{e}' occurred") 

    return connection 

 

def execute_query(connection, query): 
    cursor = connection.cursor() 
    try: 
        cursor.execute(query) 
        connection.commit() 
        print("Query executed successfully") 

    except Error as e: 
        print(f"The error '{e}' occurred") 

 

def execute_read_query(connection, query): 
    cursor = connection.cursor() 
    result = None 
    try: 
        cursor.execute(query) 
        result = cursor.fetchall() 
        return result 

    except Error as e: 
        print(f"The error '{e}' occurred") 

 

def get_last_id(connection): 
    a = execute_read_query(connection,"SELECT last_insert_rowid();")[0][0] 
    print(a) 
    if a != None: 
        print("last id fetched successfully") 

    else: 
        print("last id unsuccessful") 

    return a 

 

create_users_table = """ 
CREATE TABLE IF NOT EXISTS users ( 
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  name TEXT NOT NULL, 
  password TEXT NOT NULL,  
  gamesPlayed INT, 
  points INT 
); 
""" 

create_games_table = """ 
CREATE TABLE IF NOT EXISTS games ( 
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  date TEXT 
); 

""" 

 

create_userGame_table =  """ 
CREATE TABLE IF NOT EXISTS userGame ( 
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  user_id INTEGER NOT NULL,  
  game_id integer NOT NULL,  
  placement TEXT NOT NULL, 
  FOREIGN KEY (user_id) REFERENCES users (id) FOREIGN KEY (game_id) REFERENCES games (id) 
); 

""" 

 

#create database tables if database file not found 
if os.path.isfile("sql.sqlite") == False: 
    connection = create_connection("sql.sqlite") 
    execute_query(connection,create_users_table) 
    execute_query(connection,create_games_table) 
    execute_query(connection,create_userGame_table) 

 