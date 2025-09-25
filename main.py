import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import Command

API_TOKEN = "8033548959:AAEtHzV-TecfYAnpUBkkhKW8-ynnTPIk36k"  # токен от @BotFather
GROUP_CHAT_ID = -4905293305  # chat_id группы "Заявки с сайта"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# -------------------- SQLite --------------------
def init_db():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product TEXT,
        quantity TEXT,
        design TEXT,
        deadline TEXT,
        material TEXT,
        phone TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_order(user_id, product, quantity, design, deadline, material, phone):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO orders (user_id, product, quantity, design, deadline, material, phone)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, product, quantity, design, deadline, material, phone))
    conn.commit()
    conn.close()

# -------------------- Временное хранилище --------------------
user_data = {}

# -------------------- Хэндлеры --------------------
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🚀 Начать заявку")]],
        resize_keyboard=True
    )
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Вы можете быстро оформить заявку на печать за 1 минуту.\n"
        "Нажмите кнопку ниже, и мы всё подготовим для вас.\n⬇️ Начнем?",
        reply_markup=kb
    )

# Вопрос 1
@dp.message(F.text == "🚀 Начать заявку")
async def question_1(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📘 Буклеты"), KeyboardButton(text="📖 Журналы")],
            [KeyboardButton(text="📜 Лифлеты"), KeyboardButton(text="🎯 Флаеры")],
            [KeyboardButton(text="📢 Баннеры"), KeyboardButton(text="✍️ Другое")]
        ],
        resize_keyboard=True
    )
    await message.answer("Что вам нужно изготовить? Выберите вариант ниже 👇", reply_markup=kb)

# Вопрос 2
@dp.message(F.text.in_(["📘 Буклеты", "📖 Журналы", "📜 Лифлеты", "🎯 Флаеры", "📢 Баннеры", "✍️ Другое"]))
async def question_2(message: types.Message):
    user_data[message.from_user.id] = {"product": message.text}
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔹 До 500"), KeyboardButton(text="🔹 500–2000")],
            [KeyboardButton(text="🔹 2000+"), KeyboardButton(text="✍️ Другое")]
        ],
        resize_keyboard=True
    )
    await message.answer("Какой общий тираж вам нужен? (ориентировочно)", reply_markup=kb)

# Вопрос 3
@dp.message((F.text.startswith("🔹")) | (F.text == "✍️ Другое"))
async def question_3(message: types.Message):
    user_data.setdefault(message.from_user.id, {})["quantity"] = message.text
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет"), KeyboardButton(text="🎨 Нужна помощь")]
        ],
        resize_keyboard=True
    )
    await message.answer("У вас есть готовый дизайн макета?", reply_markup=kb)

# Вопрос 4
@dp.message(F.text.in_(["✅ Да", "❌ Нет", "🎨 Нужна помощь"]))
async def question_4(message: types.Message):
    user_data.setdefault(message.from_user.id, {})["design"] = message.text
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚡ Срочно (1–2 дня)"), KeyboardButton(text="📆 До недели")],
            [KeyboardButton(text="⏳ Более недели"), KeyboardButton(text="✍️ Другое")]
        ],
        resize_keyboard=True
    )
    await message.answer("Какие сроки для вас удобны?", reply_markup=kb)

# Вопрос 5
@dp.message(F.text.in_(["⚡ Срочно (1–2 дня)", "📆 До недели", "⏳ Более недели", "✍️ Другое"]))
async def question_5(message: types.Message):
    user_data.setdefault(message.from_user.id, {})["deadline"] = message.text
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📄 Обычная бумага"), KeyboardButton(text="📑 Плотная бумага")],
            [KeyboardButton(text="🏞 Баннерная ткань"), KeyboardButton(text="🏷 Самоклеящаяся пленка")],
            [KeyboardButton(text="✍️ Другое")]
        ],
        resize_keyboard=True
    )
    await message.answer("Какой материал предпочтителен?", reply_markup=kb)

# Вопрос 6
@dp.message(F.text.in_(["📄 Обычная бумага", "📑 Плотная бумага", "🏞 Баннерная ткань", "🏷 Самоклеящаяся пленка", "✍️ Другое"]))
async def question_6(message: types.Message):
    user_data.setdefault(message.from_user.id, {})["material"] = message.text
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📲 Отправить мой номер", request_contact=True)]],
        resize_keyboard=True
    )
    await message.answer(
        "Оставьте, пожалуйста, ваш номер телефона 📱, чтобы мы могли быстро рассчитать стоимость и отправить предложение.",
        reply_markup=kb
    )

# Финал
@dp.message(F.contact)
async def finish(message: types.Message):
    user_id = message.from_user.id
    phone = message.contact.phone_number
    data = user_data.get(user_id, {})

    # Сохраняем в базу
    save_order(
        user_id,
        data.get("product"),
        data.get("quantity"),
        data.get("design"),
        data.get("deadline"),
        data.get("material"),
        phone
    )

    # Сообщение клиенту
    await message.answer(
        "Спасибо! 🎉 Ваша заявка принята.\n\n"
        "Менеджер свяжется с вами в ближайшее время.\n"
        "✨ Мы ценим ваше время — расчёт вы получите максимально быстро!",
        reply_markup=ReplyKeyboardRemove()
    )

    # Сообщение в группу с inline-кнопками
    order_text = (
        f"📩 Новый заказ!\n\n"
        f"👤 User ID: {user_id}\n"
        f"📘 Продукт: {data.get('product')}\n"
        f"📦 Тираж: {data.get('quantity')}\n"
        f"🎨 Дизайн: {data.get('design')}\n"
        f"⏳ Сроки: {data.get('deadline')}\n"
        f"📑 Материал: {data.get('material')}\n"
        f"📱 Телефон: {phone}"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Взять в работу", callback_data=f"take_{user_id}")],
        [InlineKeyboardButton(text="✍️ Ответить клиенту", url=f"tg://user?id={user_id}")],
        [InlineKeyboardButton(text="📦 Завершить заказ", callback_data=f"done_{user_id}")]
    ])

    await bot.send_message(GROUP_CHAT_ID, order_text, reply_markup=kb)

# -------------------- Callback-хэндлеры --------------------
# Взять в работу
@dp.callback_query(F.data.startswith("take_"))
async def take_order(callback: types.CallbackQuery):
    manager = callback.from_user.full_name
    user_id = int(callback.data.split("_")[1])

    # обновляем сообщение в группе
    text = callback.message.text + f"\n\n🛠 В работе: {manager}"
    new_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Ответить клиенту", url=f"tg://user?id={user_id}")],
        [InlineKeyboardButton(text="📦 Завершить заказ", callback_data=f"done_{user_id}")],
        [InlineKeyboardButton(text="❌ Отклонить заказ", callback_data=f"decline_{user_id}")]
    ])
    await callback.message.edit_text(text, reply_markup=new_kb)
    await callback.answer("Ты взял заказ в работу ✅")

    # сообщение клиенту
    try:
        await bot.send_message(user_id, f"🛠 Ваш заказ взял в работу менеджер {manager}")
    except:
        pass  # если клиент закрыл ЛС

# Завершить
@dp.callback_query(F.data.startswith("done_"))
async def done_order(callback: types.CallbackQuery):
    manager = callback.from_user.full_name
    user_id = int(callback.data.split("_")[1])

    text = callback.message.text + f"\n\n✅ Завершил: {manager}"
    await callback.message.edit_text(text)
    await callback.answer("Заказ завершён ✅")

    # сообщение клиенту
    try:
        await bot.send_message(user_id, f"✅ Ваш заказ завершён\nМенеджер: {manager}")
    except:
        pass

# Отклонить
@dp.callback_query(F.data.startswith("decline_"))
async def decline_order(callback: types.CallbackQuery):
    manager = callback.from_user.full_name
    user_id = int(callback.data.split("_")[1])

    text = callback.message.text + f"\n\n❌ Отклонён: {manager}"
    await callback.message.edit_text(text)
    await callback.answer("Заказ отклонён ❌")

    # сообщение клиенту
    try:
        await bot.send_message(user_id, f"❌ К сожалению, ваш заказ отклонён\nМенеджер: {manager}")
    except:
        pass

# -------------------- main --------------------
async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
