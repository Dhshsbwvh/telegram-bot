import logging

from aiogram import Bot, Dispatcher, types, executor



# Telegram token прямо в коде для Paiza.IO

API_TOKEN = "8216116135:AAEsqunknYT3cSl2EM_EvTYBbhjZJOWfhOw"



logging.basicConfig(level=logging.INFO)



bot = Bot(token=API_TOKEN)

dp = Dispatcher(bot)



# ================== DATA ==================

USERS = {

    "pronto": {"password": "ZeMDZxwv", "balance": 0, "insurance": 0, "pending": 0, "chat_id": None}

}



ADMIN_LOGIN = "SuperAdm1nX"

ADMIN_PASSWORD = "7vZ#9qLp!2T"

ADMIN_CHAT_ID = None



SESSIONS = {}

# ==========================================



# ================== KEYBOARDS ==================

user_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

user_kb.add("📊 Balance")

user_kb.add("🟢 $75 [Circle]")   # <-- изменено с $50 на $75

user_kb.add("🌾 $500 [Agro Farm]")

user_kb.add("🏭 $1000 [Farm]")

user_kb.add("🔄 Update Info")



admin_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

admin_kb.add("📋 Pending Deposits")

# ==============================================



# ================== HELPERS ==================

async def admin_log(text):

    if ADMIN_CHAT_ID:

        await bot.send_message(ADMIN_CHAT_ID, f"📝 LOG\n{text}")



def get_user(chat_id):

    for u, d in USERS.items():

        if d["chat_id"] == chat_id:

            return u

    return None

# =============================================



# ================== START ====================

@dp.message_handler(commands=["start"])

async def start(msg: types.Message):

    SESSIONS[msg.chat.id] = {"step": "login"}

    await msg.answer("🔐 Enter login:")



# ================== AUTH =====================

@dp.message_handler()

async def auth(msg: types.Message):

    chat = msg.chat.id

    text = msg.text



    if chat not in SESSIONS:

        return



    step = SESSIONS[chat]["step"]



    if step == "login":

        SESSIONS[chat]["login"] = text

        SESSIONS[chat]["step"] = "password"

        await msg.answer("🔑 Enter password:")

        return



    if step == "password":

        login = SESSIONS[chat]["login"]



        global ADMIN_CHAT_ID

        if login == ADMIN_LOGIN and text == ADMIN_PASSWORD:

            ADMIN_CHAT_ID = chat

            SESSIONS.pop(chat)

            await msg.answer("✅ Admin panel", reply_markup=admin_kb)

            await admin_log("Admin logged in")

            return



        if login in USERS and USERS[login]["password"] == text:

            USERS[login]["chat_id"] = chat

            SESSIONS[chat]["user"] = login

            SESSIONS[chat]["step"] = "user"

            await msg.answer("✅ Access granted", reply_markup=user_kb)

            await admin_log(f"User logged in: {login}")

            return



        await msg.answer("❌ Access denied")

        SESSIONS.pop(chat)



# ================== USER =====================

@dp.message_handler(lambda m: m.text == "📊 Balance")

async def balance(msg: types.Message):

    user = get_user(msg.chat.id)

    if not user:

        return

    u = USERS[user]

    await msg.answer(f"📊 Account Info\nBalance: ${u['balance']}\nInsurance Deposit: ${u['insurance']}\nPending: ${u['pending']}")



@dp.message_handler(lambda m: m.text == "🟢 $75 [Circle]")   # <-- кнопка $75

async def dep75(msg: types.Message):

    await create_deposit(msg, 75)   # <-- сумма $75



@dp.message_handler(lambda m: m.text == "🌾 $500 [Agro Farm]")

async def dep500(msg: types.Message):

    await create_deposit(msg, 500)



@dp.message_handler(lambda m: m.text == "🏭 $1000 [Farm]")

async def dep1000(msg: types.Message):

    await create_deposit(msg, 1000)



async def create_deposit(msg, amount):

    user = get_user(msg.chat.id)

    if not user:

        return

    USERS[user]["pending"] = amount



    kb = types.InlineKeyboardMarkup()

    kb.add(

        types.InlineKeyboardButton("✅ Deposit Received", callback_data=f"ok:{user}"),

        types.InlineKeyboardButton("❌ Deposit Not Received", callback_data=f"no:{user}")

    )



    await admin_log(f"Deposit request\nUser: {user}\nAmount: ${amount}")



    if ADMIN_CHAT_ID:

        await bot.send_message(

            ADMIN_CHAT_ID,

            f"💰 New Insurance Deposit Request\nUser: {user}\nAmount: ${amount}",

            reply_markup=kb

        )



    await msg.answer("⏳ Waiting for admin confirmation...")



@dp.message_handler(lambda m: m.text == "🔄 Update Info")

async def inactive(msg: types.Message):

    await msg.answer("🔄 Update Info is currently unavailable.")



# ================== ADMIN =====================

@dp.message_handler(lambda m: m.text == "📋 Pending Deposits")

async def pending(msg: types.Message):

    if msg.chat.id != ADMIN_CHAT_ID:

        return

    text = "📋 Pending Deposits:\n\n"

    has = False

    for u, d in USERS.items():

        if d["pending"] > 0:

            text += f"👤 {u}: ${d['pending']}\n"

            has = True

    await msg.answer(text if has else "No pending deposits.")



@dp.callback_query_handler(lambda c: c.data.startswith(("ok", "no")))

async def decision(call: types.CallbackQuery):

    action, user = call.data.split(":")

    amount = USERS[user]["pending"]



    if action == "ok":

        USERS[user]["insurance"] += amount

        await bot.send_message(USERS[user]["chat_id"], f"✅ Insurance deposit of ${amount} RECEIVED.")

        await admin_log(f"Deposit CONFIRMED\nUser: {user}\nAmount: ${amount}")

    else:

        await bot.send_message(USERS[user]["chat_id"], f"❌ Insurance deposit of ${amount} NOT received.")

        await admin_log(f"Deposit REJECTED\nUser: {user}\nAmount: ${amount}")



    USERS[user]["pending"] = 0

    await call.message.edit_text("✔ Decision processed")

    await call.answer()



# ================== RUN =====================

if __name__ == "__main__":

    executor.start_polling(dp, skip_updates=True)
