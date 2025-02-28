from dotenv import load_dotenv
import os
import snowflake.connector

load_dotenv()


def get_connector(): 
    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        role=os.getenv('SNOWFLAKE_ROLE'), 
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA')
    )
    return conn

def query(conn, sql):
    with conn.cursor() as cur:
        cur.execute(sql)
        df = cur.fetch_pandas_all()
    
    return df


if __name__ == "__main__": 

    conn = get_connector()
    sql = "SELECT AUTHORID, NB_FOLLOWERS FROM MART_AUTHORS LIMIT 3"
    df = query(conn, sql)
    print(df)
    conn.close()