import aiomysql
import asyncio

host = "46.17" # your ip phpmyadmin server
user = "" # username database 
password = "" # password database
db = "" #name database

async def create_connection(host, user, password, db):
    """Create a connection to the MySQL database."""
    for attempt in range(3):  
        try:
            conn = await aiomysql.connect(host=host, user=user, password=password, db=db, autocommit=True)
            return conn
        except Exception as e:
            print(f"Error creating connection (attempt {attempt + 1}): {e}")
            await asyncio.sleep(2)  
    return None

async def ensure_connection(conn):
    """Ensure the connection is valid."""
    try:
        await conn.ping()
    except Exception:
        print("Connection lost, attempting to reconnect...")
        conn = await create_connection(host, user, password, db)
    return conn

async def create_table(conn):
    """Create the users table if it doesn't exist."""
    if conn is None:
        print("Connection is not established.")
        return

    async with conn.cursor() as cursor:
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT UNSIGNED PRIMARY KEY,
            admin INTEGER DEFAULT 0,
            username TEXT,
            translate_value TEXT DEFAULT 'en'
        )
        """)

async def alter_table(conn):
    """Alter the users table to change the user_id column type."""
    if conn is None:
        print("Connection is not established.")
        return

    async with conn.cursor() as cursor:
        await cursor.execute("""
        ALTER TABLE users 
        MODIFY COLUMN user_id BIGINT UNSIGNED
        """)
