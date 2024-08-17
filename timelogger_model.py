import sqlite3

class Category:
    def __init__(self, cat_id, *, name):
        self.cat_id = cat_id
        self.name = name
    
    def __repr__(self):
        return f"Category({self.cat_id}, '{self.name}')"
    
class LogEntry:
    def __init__(self, log_id, *, cat_id, time_start, time_end = "", details = ''):
        self.log_id = log_id
        self.cat_id = cat_id
        self.time_start = time_start
        self.time_end = time_end
        self.details = details
    
    def __repr__(self):
        return f"LogEntry({self.log_id}, {self.cat_id}, {self.time_start}, {self.time_end}, '{self.details}')"
        
class LogBook:
    add_cat_query = """INSERT INTO categories (CatName) VALUES
                                              ('{cat_name}');"""
    add_log_query = """INSERT INTO entries (CatID, TimeStart, TimeEnd, Details) VALUES
                                           ({log_cat_id}, '{log_time_start}', '{log_time_end}', '{log_details}');"""
    get_cat_query = "SELECT CatID, CatName FROM categories;"
    get_log_query = "SELECT EntryID, CatID, TimeStart, TimeEnd, Details FROM entries;"
    get_log_by_cat_id_query = "SELECT EntryID, CatID, TimeStart, TimeEnd, Details FROM entries WHERE CatID = '{cat_id}';"
    
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
                              TimeStart = {log_updated_time_start},
                              TimeEnd = {log_updated_time_end},
                              Details = '{log_updated_details}'
                          WHERE EntryID = {log_id}"""
    
    delete_cat_query = "DELETE FROM categories WHERE CatID = {cat_id}"
    delete_cat_by_name_query = "DELETE FROM categories WHERE CatName = '{cat_name}'"
    delete_log_query = "DELETE FROM entries WHERE EntryID = {log_id}"
    
    def __init__(self, database):
        try:
            self.connector = sqlite3.connect(database)
            self.cursor = self.connector.cursor()
        except sqlite3.Error as e:
            print(f"An sqlite3 error occured: {type(e)}")
            raise(e)
    
    def add_cat(self, cat):
        """Adds a category to the database"""
        query = LogBook.add_cat_query.format(cat_name=cat.name)
        self.cursor.execute(query)
        self.connector.commit()
        
    def add_log(self, log):
        """Adds a log to the database"""
        query = LogBook.add_log_query.format(log_cat_id=log.cat_id, log_time_start=log.time_start, \
                                             log_time_end=log.time_end, log_details=log.details)
        self.cursor.execute(query)
        self.connector.commit()
    
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
    
    def get_cat_id_by_name(self, name):
        query = LogBook.get_cat_id_by_name_query.format(name=name)
        
        return tuple(self.cursor.execute(query))[0][0]
        
    
    def get_logs(self, cat_id=None):
        """Returns a list of all logs in the database"""
        entries = []
        query = LogBook.get_log_by_cat_id_query.format(cat_id=cat_id) if cat_id else LogBook.get_log_by_query
        
        results = self.cursor.execute(query)
        for entry_id, cat_id, time_start, time_end, details in results:
            entries.append(LogEntry(entry_id, cat_id=cat_id, time_start=time_start, \
                                    time_end=time_end, details=details))
        return entries
    
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

    def del_cat_by_id(self, cat_id):
        """Deletes a category with id cat_id"""
        query = LogBook.delete_cat_query.format(cat_id=cat_id)
        self.cursor.execute(query)
        self.connector.commit()
        
    def del_cat_by_name(self, cat_name):
        """Deletes a category with id cat_id"""
        query = LogBook.delete_cat_by_name_query.format(cat_name=cat_name)
        self.cursor.execute(query)
        self.connector.commit()
                
    def del_log_by_id(self, log_id):
        """Deletes a log with id log_id"""
        query = LogBook.delete_log_query.format(log_id=log_id)
        self.cursor.execute(query)
        self.connector.commit()
            
    def purge_db(self):
        self.cursor.execute("DELETE FROM entries;")
        self.cursor.execute("DELETE FROM categories;")
        self.cursor.execute("DELETE FROM sqlite_sequence;")
        self.connector.commit()
