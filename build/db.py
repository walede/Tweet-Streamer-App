import sqlite3
import math

class Database:
    def __init__(self, db):
        self.db = db
        self.cnx = sqlite3.connect(db)
        self.cur1 = self.cnx.cursor()
        self.cur1.execute("DROP TABLE IF EXISTS tweets")
        table = """CREATE TABLE IF NOT EXISTS tweets (verified BOOLEAN,
                time DATETIME,
                tweet VARCHAR(1000),
                sentiment VARCHAR(255), 
                media_type VARCHAR(255),
                user_name VARCHAR(255),
                location VARCHAR(255))"""
        self.cur1.execute(table)
        self.cnx.commit()
        self.cur1.close()
        self.cnx.close()
        self.page = 1
        self.buckets = None 
        self.filtered = False

    def get_locs(self): 
        '''Get the location options for the stored tweets'''
        self.cnx3 = sqlite3.connect(self.db)
        self.cur3 = self.cnx3.cursor()        
        query = f'''SELECT DISTINCT location FROM tweets'''
        self.cur3.execute(query)
        rows = self.cur3.fetchall()
        self.cur3.close()
        self.cnx3.close()
        return rows

    def count_results(self): 
        '''Count the results from the last query'''
        try:
            self.cur2.close()
            self.cnx2.close()
        except:
            pass
        self.cnx2 = sqlite3.connect(self.db)
        self.cur2 = self.cnx2.cursor()        
        query = f'''SELECT COUNT(*) FROM tweets'''
        self.cur2.execute(query)
        self.cnx2.commit()
        rows = self.cur2.fetchall()
        self.buckets = math.ceil(int(rows[0][0])/50)
        self.cur2.close()
        self.cnx2.close()
        return rows[0][0]

    def count_f_results(self): 
        '''Count the results from the last filter query'''
        try:
            self.cur2.close()
            self.cnx2.close()
        except:
            pass
        self.cnx2 = sqlite3.connect(self.db)
        self.cur2 = self.cnx2.cursor()       
        query = f'''SELECT COUNT(*) FROM last_f_query'''
        self.cur2.execute(query)
        rows = self.cur2.fetchall()
        self.buckets = math.ceil(int(rows[0][0])/50)
        self.cur2.close()
        self.cnx2.close()        
        return rows[0][0]

    def fetch_all(self): 
        '''Get all stored results, with a limit of 50 and pagination'''
        try:
            self.cur2.close()
            self.cnx2.close()
        except:
            pass
        self.cnx2 = sqlite3.connect(self.db)
        self.cur2 = self.cnx2.cursor()        
        index = (self.page - 1) * 50
        query = f'''SELECT user_name,time,tweet,sentiment,verified,location,media_type 
                FROM tweets LIMIT {index}, 50'''
        self.cur2.execute(query)
        rows = self.cur2.fetchall()
        self.cur2.close()
        self.cnx2.close()
        return rows

    def filter_fetch(self, keyword, field):
        '''Get all filtered results, with a limit of 50 and pagination'''
        try:
            self.cur2.close()
            self.cnx2.close()
        except:
            pass
        self.cnx2 = sqlite3.connect(self.db)
        self.cur2 = self.cnx2.cursor()        
        index = (self.page - 1) * 50
        self.cur2.execute("DROP VIEW IF EXISTS last_f_query")
        self.cnx2.commit()
        if field == 'verified':
            query = f'''CREATE VIEW last_f_query AS SELECT user_name,
                    time,tweet,sentiment,verified,location,media_type 
                    FROM tweets WHERE {field} IS {keyword}'''
        elif field == 'sentiment':
            query = f'''CREATE VIEW last_f_query AS SELECT user_name,
                    time,tweet,sentiment,verified,location,media_type 
                    FROM tweets WHERE {field} = '{keyword}' '''
        elif field == 'time':
            from_t = keyword[0:5]
            to_t = keyword[6:]
            query = f'''CREATE VIEW last_f_query AS SELECT user_name,
                    time,tweet,sentiment,verified,location,media_type 
                    FROM tweets WHERE TIME({field}) BETWEEN '{from_t}' AND '{to_t}' '''
        else:
            query = f'''CREATE VIEW last_f_query AS SELECT user_name,
                    time,tweet,sentiment,verified,location,media_type 
                    FROM tweets WHERE {field} LIKE '%{keyword}%' '''
        self.cur2.execute(query)
        self.cnx2.commit()
        query2 = f'''SELECT * FROM last_f_query LIMIT {index}, 50'''
        self.cur2.execute(query2)
        rows = self.cur2.fetchall()
        self.cur2.close()
        self.cnx2.close()
        return rows

    def delete_entry(self):
        '''Delete all entries in the table'''
        self.cnx2 = self.cnx2 = sqlite3.connect(self.db)
        self.cur2 = self.cnx2.cursor()
        self.cur2.execute('DELETE FROM tweets')
        self.cnx2.commit()
        self.cur2.close()
        self.cnx2.close()
        return None 
