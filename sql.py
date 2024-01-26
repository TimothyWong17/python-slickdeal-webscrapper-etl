import os
import sqlite3

class SQL:
    def __init__(self,db_path):
        self.conn = sqlite3.connect(db_path)
        
    def query(self, query):
        cur = self.conn.cursor()
        cur.execute(query)

        rows = cur.fetchall()

        for row in rows:
            print(row)
    
    def table_stats(self, table_name):
        cur = self.conn.cursor()
        cur.execute(f"""
                    PRAGMA table_info({table_name})
                    """)

        rows = cur.fetchall()

        for row in rows:
            print(row)
    
if __name__ == "__main__":
    sqlite_db = SQL('db/db_deals')
    sqlite_db.table_stats("item_deals")
    sqlite_db.query("""
                        SELECT item_store, count(*) as n_items 
                        FROM item_deals
                        group by 1
                        order by 2 desc
                    
                    """)
    


    
    