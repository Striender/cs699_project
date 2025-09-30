import psycopg2
from psycopg2.extras import execute_values

class Database:
    def __init__(self, dbname, user, password, host='localhost', port=5432):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def insert_data(self, table, columns, data):
        # data is a list of tuples, each tuple corresponds to a row
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES %s"
        execute_values(self.cur, query, data)

    def close(self):
        self.cur.close()
        self.conn.close()
