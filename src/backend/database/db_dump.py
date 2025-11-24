import pandas as pd
from bs4 import BeautifulSoup
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

def upload_to_supabase(df:pd.DataFrame, table_name: str="output"):
    
    load_dotenv()

    # Fetch database credentials
    USER = os.getenv("PGUSER")
    PASSWORD = os.getenv("PGPASSWORD")
    HOST = os.getenv("PGHOST")
    PORT = os.getenv("PGPORT")
    DBNAME = os.getenv("PGDATABASE")

    # Establish connection
    try:
        conn = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        print("Connection successful!")

        cur = conn.cursor()

        # Create table if it doesn’t exist
        columns = ", ".join([f'"{col}" TEXT' for col in df.columns])
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            {columns}
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        print(f"Made sure Table '{table_name}' exists.")

        cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY;")
        conn.commit()
        print(f"Table '{table_name}' old data deleted.")

        # Insert data into table
        for _, row in df.iterrows():
            placeholders = ", ".join(["%s"] * len(row))
            columns = ", ".join([f'"{col}"' for col in df.columns])
            insert_query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders});'
            cur.execute(insert_query, tuple(row))

        conn.commit()
        print(f"Inserted {len(df)} rows into '{table_name}'.")

        # Cleanup
        cur.close()
        conn.close()
        print("Connection closed.")

    except Exception as e:
        print(f" Failed to connect or insert: {e}")
