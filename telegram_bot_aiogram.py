import os
import sqlite3
from datetime import datetime
import asyncio
import tempfile
import logging
import sys

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMediaPhoto, ReplyKeyboardMarkup, KeyboardButton, FSInputFile

# Настройка логирования
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация бота
TOKEN = 'token'
ADMIN_ID = 000000000

bot = Bot(token=TOKEN)
router = Router()
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
dp.include_router(router)

class AdminStates(StatesGroup):
    awaiting_welcome = State()
    awaiting_info = State()
    awaiting_contacts = State()
    awaiting_photo = State()
    awaiting_delete_confirm = State()

def init_db():
    try:
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        logger.info("Создание таблиц...")
        print("Создание таблиц...")
        c.execute('''CREATE TABLE IF NOT EXISTS welcome (id INTEGER PRIMARY KEY, content TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS info (id INTEGER PRIMARY KEY, content TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY, content TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS photos (id INTEGER PRIMARY KEY AUTOINCREMENT, file_id TEXT, thumb_file_id TEXT, timestamp TEXT)''')
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='photos'")
        if c.fetchone():
            logger.info("Таблица photos успешно создана или уже существует")
            print("Таблица photos успешно создана или уже существует")
        else:
            logger.error("Ошибка: таблица photos не создана")
            print("Ошибка: таблица photos не создана")
            raise Exception("Таблица photos не была создана")
        c.execute("SELECT COUNT(*) FROM welcome")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO welcome (id, content) VALUES (1, 'Добро пожаловать в бот!')")
            logger.info("Добавлены начальные данные в welcome")
            print("Добавлены начальные данные в welcome")
        c.execute("SELECT COUNT(*) FROM info")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO info (id, content) VALUES (1, 'Здесь будет ваша информация')")
            logger.info("Добавлены начальные данные в info")
            print("Добавлены начальные данные в info")
        c.execute("SELECT COUNT(*) FROM contacts")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO contacts (id, content) VALUES (1, 'Связаться со мной:\nTelegram: @YourUsername\nEmail: your@email.com')")
            logger.info("Добавлены начальные данные в contacts")
            print("Добавлены начальные данные в contacts")
        conn.commit()
        logger.info("База данных успешно инициализирована")
        print("База данных успешно инициализирована")
    except sqlite3.Error as e:
        logger.error(f"Ошибка SQLite при инициализации базы данных: {e}")
        print(f"Ошибка SQLite при инициализации базы данных: {e}")
    except Exception as e:
        logger.error(f"Общая ошибка при инициализации: {e}")
        print(f"Общая ошибка при инициализации: {e}")
    finally:
        conn.close()

def get_main_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Главная", callback_data='main')],
            [InlineKeyboardButton(text="Информация", callback_data='info')],
            [InlineKeyboardButton(text="Фотоальбом", callback_data='gallery_1')],
            [InlineKeyboardButton(text="Написать мне", callback_data='contacts')],
        ]
    )
    if ADMIN_ID:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="Админка", callback_data='admin')])
    return keyboard

def get_start_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="/start")]],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_admin_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Изменить приветствие", callback_data='edit_welcome')],
            [InlineKeyboardButton(text="Изменить инфо", callback_data='edit_info')],
            [InlineKeyboardButton(text="Изменить контакты", callback_data='edit_contacts')],
            [InlineKeyboardButton(text="Добавить фото", callback_data='add_photo')],
            [InlineKeyboardButton(text="Удалить фото", callback_data='delete_photo_menu_1')],
            [InlineKeyboardButton(text="Назад", callback_data='main')],
        ]
    )

@router.message(Command(commands=['start']))
async def start(message: types.Message):
    try:
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        c.execute("SELECT content FROM welcome WHERE id=1")
        welcome_text = c.fetchone()[0]
        conn.close()
        await message.answer(f"{welcome_text}\nВыберите раздел:", reply_markup=get_main_menu(),
                             reply_keyboard_markup=get_start_keyboard())
        logger.info(f"Пользователь {message.from_user.id} запустил бота")
    except Exception as e:
        logger.error(f"Ошибка в start: {e}")
        await message.answer("Произошла ошибка при запуске бота.")

@router.callback_query(lambda c: c.data in ['main', 'info', 'contacts', 'admin'])
async def process_menu_buttons(callback: types.CallbackQuery):
    try:
        await callback.answer()
        if callback.data == 'main':
            conn = sqlite3.connect('bot_data.db')
            c = conn.cursor()
            c.execute("SELECT content FROM welcome WHERE id=1")
            welcome_text = c.fetchone()[0]
            conn.close()
            # Проверяем, нужно ли редактировать сообщение
            current_text = callback.message.text
            current_markup = callback.message.reply_markup
            new_text = f"{welcome_text}\nВыберите раздел:"
            new_markup = get_main_menu()
            if current_text != new_text or str(current_markup) != str(new_markup):
                await callback.message.edit_text(new_text, reply_markup=new_markup)
            logger.info(f"Пользователь {callback.from_user.id} вернулся на главную")
        elif callback.data == 'info':
            conn = sqlite3.connect('bot_data.db')
            c = conn.cursor()
            c.execute("SELECT content FROM info WHERE id=1")
            info_text = c.fetchone()[0]
            conn.close()
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data='main')]])
            await callback.message.edit_text(info_text, reply_markup=keyboard)
            logger.info(f"Пользователь {callback.from_user.id} запросил информацию")
        elif callback.data == 'contacts':
            conn = sqlite3.connect('bot_data.db')
            c = conn.cursor()
            c.execute("SELECT content FROM contacts WHERE id=1")
            contacts_text = c.fetchone()[0]
            conn.close()
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data='main')]])
            await callback.message.edit_text(contacts_text, reply_markup=keyboard)
            logger.info(f"Пользователь {callback.from_user.id} запросил контакты")
        elif callback.data == 'admin' and callback.from_user.id == ADMIN_ID:
            await callback.message.edit_text("Добро пожаловать в админку!", reply_markup=get_admin_menu())
            logger.info(f"Админ {callback.from_user.id} открыл админку")
    except Exception as e:
        logger.error(f"Ошибка в process_menu_buttons ({callback.data}): {e}")
        await callback.message.edit_text("Произошла ошибка. Попробуйте позже.")

@router.callback_query(lambda c: c.data.startswith('gallery_'))
async def show_gallery(callback: types.CallbackQuery):
    try:
        await callback.answer()
        page = int(callback.data.split('_')[1])
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        c.execute("SELECT id, file_id, thumb_file_id FROM photos ORDER BY timestamp DESC")
        photos = c.fetchall()
        conn.close()
        logger.info(f"Фото из базы для галереи: {photos}")
        per_page = 9
        total_pages = (len(photos) + per_page - 1) // per_page if photos else 1
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        current_photos = photos[start_idx:end_idx]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[], row_width=3)
        if not photos:
            keyboard.inline_keyboard.append([InlineKeyboardButton(text="Назад", callback_data='main')])
            await callback.message.edit_text("Фотогалерея пуста", reply_markup=keyboard)
            return
        for i in range(0, len(current_photos), 3):
            row = [
                InlineKeyboardButton(text="🖼️", callback_data=f'photo_{current_photos[j][0]}_{page}')
                for j in range(i, min(i + 3, len(current_photos)))
            ]
            keyboard.inline_keyboard.append(row)
        nav_row = []
        if page > 1:
            nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=f'gallery_{page - 1}'))
        nav_row.append(InlineKeyboardButton(text="Назад", callback_data='main'))
        if page < total_pages:
            nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f'gallery_{page + 1}'))
        keyboard.inline_keyboard.append(nav_row)
        media = []
        for _, file_id, thumb_file_id in current_photos:
            media.append(InputMediaPhoto(media=thumb_file_id or file_id))
        await callback.message.delete()
        try:
            await bot.send_media_group(callback.message.chat.id, media=media)
            await bot.send_message(callback.message.chat.id, f"Фотогалерея (страница {page}/{total_pages})",
                                   reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Ошибка в галерее: {e}")
            await bot.send_message(callback.message.chat.id, "Ошибка при отображении галереи",
                                   reply_markup=keyboard)
        logger.info(f"Пользователь {callback.from_user.id} открыл галерею, страница {page}")
    except Exception as e:
        logger.error(f"Ошибка в show_gallery: {e}")
        await callback.message.edit_text("Произошла ошибка в галерее.")

@router.callback_query(lambda c: c.data.startswith('photo_'))
async def show_photo(callback: types.CallbackQuery):
    try:
        await callback.answer()
        parts = callback.data.split('_')
        photo_id = int(parts[1])
        page = int(parts[2])
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        c.execute("SELECT id, file_id FROM photos ORDER BY timestamp DESC")
        photos = c.fetchall()
        conn.close()
        if not photos or photo_id not in [p[0] for p in photos]:
            await callback.message.edit_text("Фото не найдено")
            return
        current_index = next(i for i, p in enumerate(photos) if p[0] == photo_id)
        file_id = photos[current_index][1]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        nav_row = []
        if current_index > 0:
            prev_id = photos[current_index - 1][0]
            nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=f'photo_{prev_id}_{page}'))
        nav_row.append(InlineKeyboardButton(text="Закрыть", callback_data=f'gallery_{page}'))
        if current_index < len(photos) - 1:
            next_id = photos[current_index + 1][0]
            nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f'photo_{next_id}_{page}'))
        keyboard.inline_keyboard.append(nav_row)
        await callback.message.delete()
        try:
            await bot.send_photo(callback.message.chat.id, file_id, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Ошибка при показе фото: {e}")
            await bot.send_message(callback.message.chat.id, "Ошибка при отображении фото",
                                   reply_markup=keyboard)
        logger.info(f"Пользователь {callback.from_user.id} просмотрел фото {photo_id}")
    except Exception as e:
        logger.error(f"Ошибка в show_photo: {e}")
        await callback.message.edit_text("Произошла ошибка при показе фото.")

@router.callback_query(lambda c: c.data in ['edit_welcome', 'edit_info', 'edit_contacts', 'add_photo'] or c.data.startswith('delete_photo_menu_'))
async def process_admin_buttons(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        if callback.from_user.id != ADMIN_ID:
            await callback.message.edit_text("У вас нет доступа к админке")
            return
        if callback.data == 'edit_welcome':
            await state.set_state(AdminStates.awaiting_welcome)
            await callback.message.edit_text("Введите новый приветственный текст")
            logger.info(f"Админ {callback.from_user.id} начал редактирование приветствия")
        elif callback.data == 'edit_info':
            await state.set_state(AdminStates.awaiting_info)
            await callback.message.edit_text("Введите новый текст для раздела Информация")
            logger.info(f"Админ {callback.from_user.id} начал редактирование информации")
        elif callback.data == 'edit_contacts':
            await state.set_state(AdminStates.awaiting_contacts)
            await callback.message.edit_text("Введите новый текст для раздела Написать мне")
            logger.info(f"Админ {callback.from_user.id} начал редактирование контактов")
        elif callback.data == 'add_photo':
            await state.set_state(AdminStates.awaiting_photo)
            await state.update_data(photos=[])
            await callback.message.edit_text("Отправьте одно или несколько фото для добавления. После завершения отправьте /done")
            logger.info(f"Админ {callback.from_user.id} начал добавление фото")
        elif callback.data.startswith('delete_photo_menu_'):
            page = int(callback.data.split('_')[3])
            await show_delete_photo_menu(callback, page, state)
    except Exception as e:
        logger.error(f"Ошибка в process_admin_buttons ({callback.data}): {e}")
        await callback.message.edit_text("Произошла ошибка в админке.")

async def show_delete_photo_menu(callback: types.CallbackQuery, page: int, state: FSMContext):
    try:
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        c.execute("SELECT id, file_id, thumb_file_id FROM photos ORDER BY timestamp DESC")
        photos = c.fetchall()
        conn.close()
        per_page = 9
        total_pages = (len(photos) + per_page - 1) // per_page if photos else 1
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        current_photos = photos[start_idx:end_idx]
        if not photos:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data='admin')]])
            await callback.message.edit_text("Фотогалерея пуста", reply_markup=keyboard)
            return
        media = []
        for _, file_id, thumb_file_id in current_photos:
            media.append(InputMediaPhoto(media=thumb_file_id or file_id))
        await callback.message.delete()
        message = await bot.send_media_group(callback.message.chat.id, media=media)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[], row_width=3)
        data = await state.get_data()
        selected_photos = data.get('selected_photos', [])
        for i in range(0, len(current_photos), 3):
            row = [
                InlineKeyboardButton(
                    text="✅" if current_photos[j][0] in selected_photos else "⬜",
                    callback_data=f'del_photo_{current_photos[j][0]}'
                )
                for j in range(i, min(i + 3, len(current_photos)))
            ]
            keyboard.inline_keyboard.append(row)
        nav_row = []
        if page > 1:
            nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=f'delete_photo_menu_{page - 1}'))
        nav_row.append(InlineKeyboardButton(text="Назад", callback_data='admin'))
        if page < total_pages:
            nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f'delete_photo_menu_{page + 1}'))
        keyboard.inline_keyboard.append(nav_row)
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="Подтвердить удаление", callback_data='confirm_delete')])
        await state.update_data(media_message_id=message[0].message_id)
        await bot.send_message(callback.message.chat.id, f"Выберите фото для удаления (страница {page}/{total_pages})",
                               reply_markup=keyboard)
        logger.info(f"Админ {callback.from_user.id} открыл меню удаления фото, страница {page}")
    except Exception as e:
        logger.error(f"Ошибка в show_delete_photo_menu: {e}")
        await callback.message.edit_text("Произошла ошибка при загрузке меню удаления.")

@router.callback_query(lambda c: c.data.startswith('del_photo_'))
async def select_photo_to_delete(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        photo_id = int(callback.data.split('_')[2])
        data = await state.get_data()
        selected_photos = data.get('selected_photos', [])
        if photo_id not in selected_photos:
            selected_photos.append(photo_id)
        else:
            selected_photos.remove(photo_id)
        await state.update_data(selected_photos=selected_photos)
        page = int(callback.message.reply_markup.inline_keyboard[-2][1].callback_data.split('_')[2])
        await show_delete_photo_menu(callback, page, state)
        logger.info(f"Админ {callback.from_user.id} выбрал/снял выбор фото {photo_id} для удаления")
    except Exception as e:
        logger.error(f"Ошибка в select_photo_to_delete: {e}")
        await callback.message.edit_text("Произошла ошибка при выборе фото.")

@router.callback_query(lambda c: c.data == 'confirm_delete')
async def confirm_delete(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        data = await state.get_data()
        selected_photos = data.get('selected_photos', [])
        if not selected_photos:
            await callback.message.edit_text("Вы не выбрали фото для удаления", reply_markup=get_admin_menu())
            await state.clear()
            return
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Да, удалить", callback_data='execute_delete')],
                [InlineKeyboardButton(text="Отмена", callback_data='admin')]
            ]
        )
        photo_count = len(selected_photos)
        text = "Вы уверены, что хотите удалить это изображение?" if photo_count == 1 else f"Вы уверены, что хотите удалить эти {photo_count} изображений?"
        await callback.message.edit_text(text, reply_markup=keyboard)
        logger.info(f"Админ {callback.from_user.id} запросил подтверждение удаления {photo_count} фото")
    except Exception as e:
        logger.error(f"Ошибка в confirm_delete: {e}")
        await callback.message.edit_text("Произошла ошибка при подтверждении удаления.")

@router.callback_query(lambda c: c.data == 'execute_delete')
async def execute_delete(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        data = await state.get_data()
        selected_photos = data.get('selected_photos', [])
        if not selected_photos:
            await callback.message.edit_text("Фото не выбраны", reply_markup=get_admin_menu())
            await state.clear()
            return
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        c.executemany("DELETE FROM photos WHERE id=?", [(photo_id,) for photo_id in selected_photos])
        conn.commit()
        conn.close()
        photo_count = len(selected_photos)
        text = "Изображение удалено" if photo_count == 1 else f"Изображения удалены ({photo_count})"
        await callback.message.edit_text(text, reply_markup=get_admin_menu())
        await state.clear()
        logger.info(f"Админ {callback.from_user.id} удалил {photo_count} фото")
    except Exception as e:
        logger.error(f"Ошибка в execute_delete: {e}")
        await callback.message.edit_text("Произошла ошибка при удалении фото.")

@router.message(StateFilter(AdminStates.awaiting_welcome))
async def process_welcome_input(message: types.Message, state: FSMContext):
    try:
        if message.from_user.id != ADMIN_ID:
            return
        if not message.text:
            await message.answer("Пожалуйста, отправьте текст!")
            return
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        c.execute("UPDATE welcome SET content=? WHERE id=1", (message.text,))
        conn.commit()
        conn.close()
        await state.clear()
        await message.answer("Информация обновлена", reply_markup=get_admin_menu())
        logger.info(f"Админ {message.from_user.id} обновил приветствие")
    except Exception as e:
        logger.error(f"Ошибка в process_welcome_input: {e}")
        await message.answer("Произошла ошибка при обновлении приветствия.")

@router.message(StateFilter(AdminStates.awaiting_info))
async def process_info_input(message: types.Message, state: FSMContext):
    try:
        if message.from_user.id != ADMIN_ID:
            return
        if not message.text:
            await message.answer("Пожалуйста, отправьте текст!")
            return
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        c.execute("UPDATE info SET content=? WHERE id=1", (message.text,))
        conn.commit()
        conn.close()
        await state.clear()
        await message.answer("Информация обновлена", reply_markup=get_admin_menu())
        logger.info(f"Админ {message.from_user.id} обновил информацию")
    except Exception as e:
        logger.error(f"Ошибка в process_info_input: {e}")
        await message.answer("Произошла ошибка при обновлении информации.")

@router.message(StateFilter(AdminStates.awaiting_contacts))
async def process_contacts_input(message: types.Message, state: FSMContext):
    try:
        if message.from_user.id != ADMIN_ID:
            return
        if not message.text:
            await message.answer("Пожалуйста, отправьте текст!")
            return
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        c.execute("UPDATE contacts SET content=? WHERE id=1", (message.text,))
        conn.commit()
        conn.close()
        await state.clear()
        await message.answer("Информация обновлена", reply_markup=get_admin_menu())
        logger.info(f"Админ {message.from_user.id} обновил контакты")
    except Exception as e:
        logger.error(f"Ошибка в process_contacts_input: {e}")
        await message.answer("Произошла ошибка при обновлении контактов.")

@router.message(StateFilter(AdminStates.awaiting_photo), lambda message: not message.text or message.text != '/done')
async def process_photo_input(message: types.Message, state: FSMContext):
    try:
        logger.info(f"Получено сообщение от user_id: {message.from_user.id}, фото: {message.photo}, документ: {message.document}")
        if message.from_user.id != ADMIN_ID:
            logger.info("Доступ запрещён: не админ")
            return

        file_id = None
        thumb_file_id = None

        if message.photo:
            file_id = message.photo[-1].file_id  # Самое большое разрешение
            thumb_file_id = message.photo[0].file_id  # Миниатюра
        elif message.document and message.document.mime_type.startswith('image/'):
            file_info = await bot.get_file(message.document.file_id)
            file_path = file_info.file_path
            downloaded_file = await bot.download_file(file_path)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(downloaded_file.read())
                temp_file_path = temp_file.name
            photo_msg = await bot.send_photo(message.chat.id, FSInputFile(temp_file_path))
            file_id = photo_msg.photo[-1].file_id
            thumb_file_id = photo_msg.photo[0].file_id
            await bot.delete_message(message.chat.id, photo_msg.message_id)
            os.unlink(temp_file_path)
        else:
            await message.answer("Пожалуйста, отправьте фото или завершите с помощью /done")
            return

        data = await state.get_data()
        photos = data.get('photos', [])
        photos.append((file_id, thumb_file_id))
        await state.update_data(photos=photos)
        await message.answer("Фото добавлено в очередь. Отправьте ещё или завершите с помощью /done")
        logger.info(f"Фото добавлено в очередь: {file_id}, thumb: {thumb_file_id}, список: {photos}")
    except Exception as e:
        logger.error(f"Ошибка при обработке фото: {e}")
        await message.answer("Ошибка при добавлении фото. Попробуйте ещё раз.")

@router.message(Command(commands=['done']), StateFilter(AdminStates.awaiting_photo))
async def process_photo_done(message: types.Message, state: FSMContext):
    try:
        logger.info(f"Получена команда /done от user_id: {message.from_user.id}")
        if message.from_user.id != ADMIN_ID:
            logger.info("Доступ запрещён: не админ")
            return

        data = await state.get_data()
        photos = data.get('photos', [])
        logger.info(f"Обработка /done, список фото: {photos}")

        if not photos:
            await message.answer("Вы не добавили ни одного фото", reply_markup=get_admin_menu())
            await state.clear()
            logger.info("Список фото пуст, состояние очищено")
            return

        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        for file_id, thumb_file_id in photos:
            c.execute("INSERT INTO photos (file_id, thumb_file_id, timestamp) VALUES (?, ?, ?)",
                      (file_id, thumb_file_id, datetime.now().isoformat()))
            logger.info(f"Добавлено в базу: file_id={file_id}, thumb_file_id={thumb_file_id}")
        conn.commit()
        conn.close()

        photo_count = len(photos)
        text = "Изображение добавлено" if photo_count == 1 else f"Изображения добавлены ({photo_count})"
        await message.answer(text, reply_markup=get_admin_menu())
        await state.clear()
        logger.info(f"Фото успешно добавлены, количество: {photo_count}, состояние очищено")
    except Exception as e:
        logger.error(f"Ошибка в process_photo_done: {e}")
        await message.answer("Ошибка при сохранении фото.")

async def main():
    init_db()
    logger.info("Бот запущен!")
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        logger.info("Старт программы...")
        print("Старт программы...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
        print("Бот остановлен")
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске: {e}")
        print(f"Критическая ошибка при запуске: {e}")