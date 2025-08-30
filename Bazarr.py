import asyncio
import json
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

# === Загрузка переменных ===
load_dotenv()

# Функция загрузки конфигурации
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Проверь .env или переменные окружения.")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

# Главное меню
def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="☎ Контакты", callback_data="contacts")],
        [InlineKeyboardButton(text="💬 Наш чат", url=config["chat_url"])],
        [InlineKeyboardButton(text="📝 Оставить отзыв", url=config["review_url"])],
        [InlineKeyboardButton(text="📍 Как добраться", url=config["map_url"])]
    ])


# /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    file_path = os.path.join(os.path.dirname(__file__), config.get("welcome_image"))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Главное меню", callback_data="main_menu")]
    ])
    if file_path and os.path.exists(file_path):
        photo = FSInputFile(file_path)
        await message.answer_photo(photo, caption=config["welcome_text"], reply_markup=kb)
    else:
        await message.answer(config["welcome_text"], reply_markup=kb)

# Главное меню
@dp.callback_query(F.data == "main_menu")
async def main_menu(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Выберите раздел:", reply_markup=main_menu_kb())

# Каталог
@dp.callback_query(F.data == "catalog")
async def show_catalog(callback: types.CallbackQuery):
    await callback.message.delete()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="main_menu")]
    ])
    await callback.message.answer("🛠 Каталог в разработке. Скоро добавим товары!", reply_markup=kb)



# Контакты
@dp.callback_query(F.data == "contacts")
async def send_contacts(callback: types.CallbackQuery):
    await callback.message.delete()
    contacts_text = (
        f"📍 *Адрес*: {config['contacts']['address']}\n"
        f"☎ *Телефон*: {config['contacts']['phone']}\n"
        f"🕒 *Часы работы*: {config['contacts']['hours']}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="main_menu")]
    ])
    await callback.message.answer(contacts_text, reply_markup=kb)

# Перезагрузка config.json на лету
@dp.message(Command("reload_config"))
async def reload_config(message: types.Message):
    global config
    config = load_config()
    await message.answer("♻ Конфигурация успешно обновлена!")

# Запуск бота
async def main():
    print("✅ Бот запущен, ожидаю команды...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
