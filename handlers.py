import logging
import json
import os
import time
import random
import asyncio
import re
import requests
from database import ensure_connection
from datetime import datetime
from aiogram import Dispatcher, Bot, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hlink
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import FSInputFile
from ping3 import ping
from io import BytesIO
from states import OrderFood
from googletrans import Translator
from keyboards import get_start_keyboard, get_check_keyboard, get_language_keyboard, get_new_language_keyboard
from gtts import gTTS

logging.basicConfig(level=logging.INFO)



def register_handlers(dp: Dispatcher, conn, bot: Bot):
    async def translate_text(text, src_lang='auto', dest_lang='en'):
        translator = Translator()
        translation = translator.translate(text, src=src_lang, dest=dest_lang)
        return translation.text
    
    async def check_users(user_id):
        urles = get_check_keyboard()
        user_channel_status = await bot.get_chat_member(chat_id='@naumov_glav', user_id=user_id)
        if user_channel_status.status != 'left':
            return True
        else:
            await bot.send_message(user_id, text='Для использования бота необходима подписка. Благодаря ей, Вы получаете неограниченный доступ к нашим функциям бота.', reply_markup=urles)
            return False

    @dp.message(CommandStart())
    async def command_start_handler(message: Message, state: FSMContext) -> None:
        user_id = message.from_user.id
        username = message.from_user.username
        async with conn.cursor() as cursor:
            start = await ensure_connection(conn)
            print("Good command")
            await cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            result = await cursor.fetchone()

            if result is None:
                await cursor.execute("INSERT INTO users (user_id, username) VALUES (%s, %s)", (user_id, username))
            await conn.commit()

            inline_key = get_start_keyboard()
            if await check_users(user_id):
                await message.reply("""
        <b>Добро пожаловать в мир беспрепятственной коммуникации с нашим умным ботом для перевода! 🚀</b>

1️⃣ <b>Автоматический перевод</b>: Отправьте любой текст, и бот моментально переведет его на выбранный вами язык.
2️⃣ <b>Поддержка множества языков</b>: Бот поддерживает широкий спектр языков, включая английский, испанский, французский, немецкий, русский и многие другие. Полный список доступных языков можно найти по ссылке ниже.
3️⃣ <b>Простой и удобный интерфейс</b>: Использование бота не требует специальных знаний — просто отправьте текст, и получите перевод в считанные секунды.
4️⃣ <b>Настройка языка по умолчанию</b>: Вы можете выбрать язык перевода по умолчанию, чтобы каждый раз не указывать его вручную.

Появились предложения по улучшению бота? Пиши администратору проекта. 
                """, reply_markup=inline_key, parse_mode='HTML')   
                await state.set_state(OrderFood.choosing_food_name)

    @dp.callback_query(lambda call: call.data.startswith("check"))
    async def callback_translate_handler(callback_query: CallbackQuery, state: FSMContext):
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        user_id = callback_query.message.chat.id
        username = callback_query.message.chat.username
        async with conn.cursor() as cursor:
            start = await ensure_connection(conn)
            print("Good command")
            await cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            result = await cursor.fetchone()

            if result is None:
                await cursor.execute("INSERT INTO users (user_id, username) VALUES (%s, %s)", (user_id, username))
            await conn.commit()

            if await check_users(user_id):
                inline_key = get_start_keyboard()
                await bot.send_message(user_id, text="""
        <b>Добро пожаловать в мир беспрепятственной коммуникации с нашим умным ботом для перевода! 🚀</b>

1️⃣ <b>Автоматический перевод</b>: Отправьте любой текст, и бот моментально переведет его на выбранный вами язык.
2️⃣ <b>Поддержка множества языков</b>: Бот поддерживает широкий спектр языков, включая английский, испанский, французский, немецкий, русский и многие другие. Полный список доступных языков можно найти по ссылке ниже.
3️⃣ <b>Простой и удобный интерфейс</b>: Использование бота не требует специальных знаний — просто отправьте текст, и получите перевод в считанные секунды.
4️⃣ <b>Настройка языка по умолчанию</b>: Вы можете выбрать язык перевода по умолчанию, чтобы каждый раз не указывать его вручную.
                """, reply_markup=inline_key, parse_mode='HTML')   
                await state.set_state(OrderFood.choosing_food_name)

    @dp.callback_query(lambda call: call.data.startswith("value_transalate"))
    async def callback_translate_handler(callback_query: CallbackQuery, state: FSMContext):
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        inline_key = get_language_keyboard()
        await bot.send_message(chat_id=callback_query.message.chat.id, text=f"""
Введи значение из списка ниже\nПример: en""", reply_markup=inline_key)
        await state.set_state(OrderFood.answering_user)

    @dp.message(F.text, OrderFood.answering_user)
    async def answer_user(message: Message, state: FSMContext):
        user_id = message.from_user.id
        new_value = message.text
        async with conn.cursor() as cursor:
            start = await ensure_connection(conn)
            print("Good command")
            await cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            result = await cursor.fetchone()
            if result:
                await cursor.execute("UPDATE users SET translate_value = %s WHERE user_id = %s", (new_value, user_id))
                await conn.commit()
                inline = get_new_language_keyboard()
                await bot.send_message(user_id, text=f"Вы успешно изменили язык перевода на: {new_value}", reply_markup=inline)
                await state.clear()

    @dp.message(F.text, OrderFood.choosing_food_name)
    async def choose_food_name(message: Message, state: FSMContext):
        food_name = message.text
        user_id = message.from_user.id
        if await check_users(user_id):
            async with conn.cursor() as cursor: 
                start = await ensure_connection(conn)
                print("Good command")
                await cursor.execute("SELECT translate_value FROM users WHERE user_id = %s", (message.from_user.id,))
                result = await cursor.fetchone()
                if result:
                    translate_value = result[0]  
                    try:
                        translated_text = await translate_text(food_name, dest_lang=translate_value)
                    except ValueError:
                        await message.reply("Не удалось перевести текст. Возможно, вы ввели неправильный язык.")
                        return
                    await message.reply(translated_text)


    @dp.message(lambda message: re.match(r'^@translatebo_bot\b', message.text))
    async def handle_mention_command(message: Message):
        command_text = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else ''
        
        chat_type = message.chat.type
        if chat_type == 'supergroup':
            user_id = message.from_user.id
            if await check_users(user_id):
                async with conn.cursor() as cursor: 
                    start = await ensure_connection(conn)
                    await cursor.execute("SELECT translate_value FROM users WHERE user_id = %s", (message.from_user.id,))
                    result = await cursor.fetchone()
                    if result:
                        translate_value = result[0]  
                        try:
                            translated_text = await translate_text(command_text, dest_lang=translate_value)
                        except ValueError:
                            await message.reply("Не удалось перевести текст. Возможно, вы ввели неправильный язык.")
                            return
                        await message.reply(translated_text)

    
        else:
            await message.answer(f"Данная команда работает лишь в групповом чате.")

    @dp.message()
    async def echo(message: Message):
        food_name = message.text
        user_id = message.from_user.id
        if await check_users(user_id):
            async with conn.cursor() as cursor: 
                start = await ensure_connection(conn)
                await cursor.execute("SELECT translate_value FROM users WHERE user_id = %s", (message.from_user.id,))
                result = await cursor.fetchone()
                if result:
                    translate_value = result[0]  
                    try:
                        translated_text = await translate_text(food_name, dest_lang=translate_value)
                    except ValueError:
                        await message.reply("Не удалось перевести текст. Возможно, вы ввели неправильный язык.")
                        return
                    await message.reply(translated_text)

    
