# bot.py
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import register_handlers  
from database import create_connection, create_table, alter_table 
from aiomysql import InterfaceError  

TOKEN = '' # bot token @botfather
host = "46.17" # ip address database (phpmyadmin)
user = "" # username database (phpmyadmin)
password = "" # password database (phpmyadmin)
database = "" # database name database (phpmyadmin)

async def main() -> None:
    while True:
        try:
            storage = MemoryStorage()
            bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
            dp = Dispatcher(storage=storage)

            conn = await create_connection(host, user, password, database)
            if conn is None:
                print("Failed to connect to the database. Restarting...")
                await asyncio.sleep(5)  
                continue
            await create_table(conn) 
            await alter_table(conn)

            register_handlers(dp, conn, bot)

            await dp.start_polling(bot)

            await conn.close()

        except InterfaceError as e:
            logging.error(f"Database connection error: {e}")
            print("Database connection lost. Restarting the bot...")
            conn = await create_connection(host, user, password, database)  
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            print("An error occurred. Restarting the bot...")
            await asyncio.sleep(5) 
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())