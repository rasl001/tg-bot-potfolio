# Telegram Bot Portfolio 🤖✨

---

## English 🇬🇧

### Description 🌟
This project is a Telegram bot designed to showcase a portfolio. 
It enables users to view information, a photo album with thumbnails and pagination, and contact the author. 
The admin can manage content: edit the welcome message, info, contacts, and add or remove photos. 
The bot uses SQLite for data storage and logs all actions to `bot.log` for debugging.

### Features 🚀
- **Main Page** 🏠: Welcome message with a menu.
- **Information** ℹ️: Section with text info.
- **Photo Album** 📸: Displays thumbnails (9 per page) with pagination and full-size photo viewing.
- **Contacts** 📞: Contact the author.
- **Admin Panel** 🔧: For the admin — edit texts, add/remove photos.
- **Logging** 📜: All actions and errors are logged to `bot.log`.

### Installation ⚙️
1. Install the required package: pip install aiogram
2. Update BOT_TOKEN, and ADMIN_ID in telegram_bot_aiogram.py with your values.
3. Run the bot: python telegram_bot_aiogram.py

### Technologies 🛠️
- **Python 3** 🐍: Main programming language.
- **aiogram** 📡: Asynchronous library for Telegram API.
- **SQLite** 🗄️: Lightweight database for content storage.
- **tmux** 💻: For running the bot in the background on a server.

### License 📜
MIT License

---

## Русский 🇷🇺

### Описание 🌟
Telegram-бот, созданный для демонстрации портфолио. 
Он позволяет пользователям просматривать информацию, фотоальбом с миниатюрами и страницами, а также связываться с автором. 
Администратор может управлять контентом: изменять приветствие, информацию, контакты, добавлять и удалять фото. 
Бот использует SQLite для хранения данных и логирует все действия в файл `bot.log` для отладки.

### Функционал 🚀
- **Главная страница** 🏠: Приветственное сообщение с меню.
- **Информация** ℹ️: Раздел с текстовой информацией.
- **Фотоальбом** 📸: Отображение миниатюр (9 на страницу) с пагинацией и просмотром полноразмерных фото.
- **Контакты** 📞: Связь с автором.
- **Админка** 🔧: Для админа — редактирование текстов, добавление/удаление фото.
- **Логирование** 📜: Все действия и ошибки записываются в `bot.log`.

### Установка ⚙️
1. Установите необходимую библиотеку: pip install aiogram
2. Обновите BOT_TOKEN и ADMIN_ID в файле telegram_bot_aiogram.py своими значениями.
3. Запустите бота: python telegram_bot_aiogram.py

### Технологии 🛠️
- **Python 3** 🐍: Основной язык программирования.
- **aiogram** 📡: Асинхронная библиотека для работы с Telegram API.
- **SQLite** 🗄️: Лёгкая база данных для хранения контента.
- **tmux** 💻: Для фонового запуска бота на сервере.

### Лицензия 📜
Лицензия MIT
