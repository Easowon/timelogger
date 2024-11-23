# Copyright (c) 2024 Eason Chen. Licensed under the MIT Licence.

import sqlite3

class Category:
    def __init__(self, cat_id, *, name):
        self.cat_id = cat_id
        self.name = name
    
    def __repr__(self):
        return f"Category({self.cat_id}, '{self.name}')"
    
class LogEntry:
    def __init__(self, *, cat_id, time_start, time_end = "", details = '', log_id=None, billed=0):
        self.log_id = log_id
        self.cat_id = cat_id
        self.time_start = time_start
        self.time_end = time_end
        self.details = details
        self.billed = billed
    
    def __repr__(self):
        return f"LogEntry({self.log_id}, {self.cat_id}, {self.time_start}, {self.time_end}, '{self.details}', {self.billed})"
        
class AppState:
    def __init__(self, cursor):
        state = cursor.execute("SELECT ID, LastEntryID FROM app_state;")
        self.__id, self.__last_entry_id = next(state)
    
    def get_last_entry_id(self):
        return self.__last_entry_id
    
    def get_id(self):
        return self.__id
        
class LogBook:
    create_cat_table_query = """CREATE TABLE IF NOT EXISTS categories (
                                CatID   INTEGER   PRIMARY KEY AUTOINCREMENT
                                        UNIQUE
                                        NOT NULL,
                                CatName TEXT (64) NOT NULL
                                        UNIQUE
                                );"""
    create_log_table_query = """CREATE TABLE IF NOT EXISTS entries (
                                EntryID   INTEGER     PRIMARY KEY AUTOINCREMENT
                                          NOT NULL
                                          UNIQUE,
                                CatID     INTEGER     REFERENCES categories (CatID) ON DELETE RESTRICT
                                                                                    ON UPDATE RESTRICT
                                                                                    MATCH SIMPLE
                                          NOT NULL,
                                TimeStart TEXT        NOT NULL,
                                TimeEnd   TEXT        DEFAULT (0),
                                Details   TEXT (255),
                                Billed    INTEGER (1) CHECK (Billed == 1 OR 
                                                             Billed == 0) 
                                          NOT NULL
                                          DEFAULT (0) 
                                );"""
    create_app_table_query = """CREATE TABLE IF NOT EXISTS app_state (
                                ID          INTEGER PRIMARY KEY
                                            DEFAULT (1),
                                LastEntryID INTEGER UNIQUE
                                );"""
    add_cat_query = """INSERT INTO categories (CatName) VALUES
                                              ('{cat_name}');"""
    add_log_query = """INSERT INTO entries (CatID, TimeStart, TimeEnd, Details, Billed) VALUES
                                           ({log_cat_id}, '{log_time_start}', '{log_time_end}', '{log_details}', {log_billed});"""
    get_cat_query = "SELECT CatID, CatName FROM categories;"
    get_cat_name_by_id_query = "SELECT CatName FROM categories WHERE CatID = {cat_id};"
    get_log_query = "SELECT EntryID, CatID, TimeStart, TimeEnd, Details, Billed FROM entries;"
    get_log_by_cat_id_query = "SELECT EntryID, CatID, TimeStart, TimeEnd, Details, Billed FROM entries WHERE CatID = '{cat_id}';"
    get_log_by_id_query = "SELECT EntryID, CatID, TimeStart, TimeEnd, Details, Billed FROM entries WHERE EntryID = {entry_id};"
    
    get_cat_id_by_name_query = "SELECT CatID FROM categories WHERE CatName = '{name}'"
    
    update_cat_query = """UPDATE categories
                          SET CatName = '{cat_updated_name}',
                              CatDetails = '{cat_updated_details}'
                          WHERE CatID = {cat_id}"""
    
    update_cat_name_by_id_query = """UPDATE categories
                          SET CatName = '{cat_updated_name}'
                          WHERE CatID = {cat_id}"""
    update_cat_name_by_name_query = """UPDATE categories
                          SET CatName = '{cat_updated_name}'
                          WHERE CatName = '{cat_name}'"""
    
    update_log_query = """UPDATE entries
                          SET CatID = {log_updated_cat_id},
                              TimeStart = '{log_updated_time_start}',
                              TimeEnd = '{log_updated_time_end}',
                              Details = '{log_updated_details}',
                              Billed = {log_updated_billed}
                          WHERE EntryID = {log_id}"""
    update_log_end_by_start_query = """UPDATE entries
                          SET TimeEnd = '{log_updated_time_end}'
                          WHERE TimeStart = '{time_start}'"""
    update_log_details_by_start_query = """UPDATE entries
                          SET Details = '{log_updated_details}'
                          WHERE TimeStart = '{time_start}'"""
    
    delete_cat_query = "DELETE FROM categories WHERE CatID = {cat_id}"
    delete_cat_by_name_query = "DELETE FROM categories WHERE CatName = '{cat_name}'"
    delete_log_query = "DELETE FROM entries WHERE EntryID = {log_id}"
    delete_log_by_time_query = "DELETE FROM entries WHERE TimeStart = '{log_time_start}'"
    delete_log_by_cat_id_query = "DELETE FROM entries WHERE CatID = {cat_id}"

    update_last_entry_query = """UPDATE app_state
                          SET LastEntryID = {last_entry_id}
                          WHERE ID = 1"""
    get_billed_by_time_query = "SELECT Billed FROM entries WHERE TimeStart = '{log_time_start}';"
    update_billed_by_time_query = """UPDATE entries
                                SET Billed = {new_billed}
                                WHERE TimeStart = '{log_time_start}';"""
    
    def __init__(self, database):
        try:
            self.connector = sqlite3.connect(database)
            self.cursor = self.connector.cursor()
            self.cursor.execute(LogBook.create_app_table_query)
            self.cursor.execute(LogBook.create_cat_table_query)
            self.cursor.execute(LogBook.create_log_table_query)
            if len(self.cursor.execute("""SELECT * FROM app_state;""").fetchall()) < 1:
                self.cursor.execute("""INSERT INTO app_state (ID, LastEntryID) VALUES (1, 0);""")
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
            self.AppState = AppState(self.cursor)
            self.connector.commit()
        except sqlite3.Error as e:
            print(f"An sqlite3 error occured: {type(e)}")
            raise(e)
        
    def get_full_database(self):
        cat_query = LogBook.get_cat_query
        log_query = LogBook.get_log_query
        app_query = "SELECT ID, LastEntryID FROM app_state;"
        cats = self.cursor.execute(cat_query).fetchall()
        logs = self.cursor.execute(log_query).fetchall()
        app_state = self.cursor.execute(app_query).fetchall()
        return cats, logs, app_state
        
    def get_billed_by_time(self, log_time_start):
        query = LogBook.get_billed_by_time_query.format(log_time_start=log_time_start)
        return next(self.cursor.execute(query))
    
    def update_billed_by_time(self, log_time_start, new_billed):
        query = LogBook.update_billed_by_time_query.format(log_time_start=log_time_start, new_billed=new_billed)
        self.cursor.execute(query)
        self.connector.commit()
        
    def update_last_entry(self, entry_id):
        query = LogBook.update_last_entry_query.format(last_entry_id=entry_id)
        self.cursor.execute(query)
        self.connector.commit()
    
    def add_cat(self, cat):
        """Adds a category to the database"""
        query = LogBook.add_cat_query.format(cat_name=cat.name)
        self.cursor.execute(query)
        self.connector.commit()
        
    def add_log(self, log):
        """Adds a log to the database"""
        query = LogBook.add_log_query.format(log_cat_id=log.cat_id, log_time_start=log.time_start, \
                                             log_time_end=log.time_end, log_details=log.details, log_billed=log.billed)
        self.cursor.execute(query)
        self.connector.commit()
        
        return self.cursor.lastrowid
    
    def get_cats(self):
        """Returns a list of all categories in the database"""
        cats = []
        results = self.cursor.execute(LogBook.get_cat_query)
        for cat_id, cat_name in results:
            cats.append(Category(cat_id, name=cat_name))
        return cats
    
    def get_cat_names(self):
        cats = self.get_cats()
        return [cat.name for cat in cats]
    
    def get_cat_name_by_id(self, cat_id):
        query = LogBook.get_cat_name_by_id_query.format(cat_id=cat_id)
        return tuple(self.cursor.execute(query))[0][0]
    
    def get_cat_id_by_name(self, name):
        query = LogBook.get_cat_id_by_name_query.format(name=name)
        return tuple(self.cursor.execute(query))[0][0]
        
    
    def get_logs(self, cat_id=None):
        """Returns a list of all logs in the database"""
        entries = []
        query = LogBook.get_log_by_cat_id_query.format(cat_id=cat_id) if cat_id else LogBook.get_log_by_query
        
        results = self.cursor.execute(query)
        for entry_id, cat_id, time_start, time_end, details, billed in results:
            entries.append(LogEntry(cat_id=cat_id, time_start=time_start, \
                                    time_end=time_end, details=details, billed=billed))
        return entries
    
    def get_log_by_id(self, entry_id):
        query = LogBook.get_log_by_id_query.format(entry_id=entry_id)
        results = self.cursor.execute(query).fetchall()
        if len(results) <= 0:
            return None
        else:
            entry_id, cat_id, time_start, time_end, details, billed = results[0]
            
            return LogEntry(log_id=entry_id, cat_id=cat_id, time_start=time_start, time_end=time_end, details=details, billed=billed)
    
    def update_cat_by_id(self, cat_id, cat_updated):
        """Updates an existing category based on cat_id"""
        query = LogBook.update_cat_query.format(cat_id=cat_id, cat_updated_name=cat_updated.name, \
                                                cat_updated_details=cat_updated.details)
        self.cursor.execute(query)
        self.connector.commit()
        
    def update_cat_name_by_id(self, cat_id, new_name):
        """Updates an existing category name based on cat_id"""
        query = LogBook.update_cat_name_by_id_query.format(cat_id=cat_id, cat_updated_name=new_name)
        self.cursor.execute(query)
        self.connector.commit()
        
    def update_cat_name_by_name(self, cat_name, new_name):
        """Updates an existing category name based on cat_name"""
        query = LogBook.update_cat_name_by_name_query.format(cat_name=cat_name, cat_updated_name=new_name)
        self.cursor.execute(query)
        self.connector.commit()
    
    def update_log_by_id(self, log_id, log_updated):
        """Updates an existing log based on log_id"""
        query = LogBook.update_log_query.format(log_id=log_id, log_updated_cat_id=log_updated.cat_id, \
                                                log_updated_time_start=log_updated.time_start, \
                                                log_updated_time_end=log_updated.time_end, \
                                                log_updated_details=log_updated.details)
        self.cursor.execute(query)
        self.connector.commit()
    
    def update_log_end_by_start(self, log_start_time, log_end_time):
        """Updates end time of log via start time"""
        query = LogBook.update_log_end_by_start_query.format(time_start=log_start_time, log_updated_time_end=log_end_time)
        self.cursor.execute(query)
        self.connector.commit()
    
    def update_log_details_by_start(self, log_start_time, log_details):
        """Updates end time of log via start time"""
        query = LogBook.update_log_details_by_start_query.format(time_start=log_start_time, log_updated_details=log_details)
        self.cursor.execute(query)
        self.connector.commit()
    
    def del_cat_by_id(self, cat_id):
        """Deletes a category with id cat_id"""
        query = LogBook.delete_cat_query.format(cat_id=cat_id)
        self.cursor.execute(query)
        self.connector.commit()
        
    def del_cat_by_name(self, cat_name):
        """Deletes a category with name cat_name"""
        query = LogBook.delete_cat_by_name_query.format(cat_name=cat_name)
        self.cursor.execute(query)
        self.connector.commit()
                
    def del_log_by_id(self, log_id):
        """Deletes a log with id log_id"""
        query = LogBook.delete_log_query.format(log_id=log_id)
        self.cursor.execute(query)
        self.connector.commit()
    
    def del_log_by_time(self, log_time_start):
        """Deletes a log with TimeStart log_time_start"""
        query = LogBook.delete_log_by_time_query.format(log_time_start=log_time_start)
        self.cursor.execute(query)
        self.connector.commit()
    
    def del_log_by_cat_id(self, cat_id):
        query = LogBook.delete_log_by_cat_id_query.format(cat_id=cat_id)
        self.cursor.execute(query)
        self.connector.commit()
            
    def purge_db(self):
        self.cursor.execute("DELETE FROM entries;")
        self.cursor.execute("DELETE FROM categories;")
        self.cursor.execute("DELETE FROM sqlite_sequence;")
        self.connector.commit()
