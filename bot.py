import asyncio

import logging

from aiogram import Bot, Dispatcher, F

from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton



# ================= НАСТРОЙКИ =================

TOKEN = "8216116135:AAGTNq-_V89z6Lp_vWZ4ZTP1C1wsy-gtfiY"

ADMIN_ID = 7625893405



USER_LOGIN = "pronto"

USER_PASSWORD = "ZeMDZxwv"



ADMIN_LOGIN = "SuperAdm1nX"

ADMIN_PASSWORD = "7vZ#9qLp!2T"

# ============================================



logging.basicConfig(level=logging.INFO)



bot = Bot(token=TOKEN)

dp = Dispatcher()



user_state = {}  # user_id: state

user_role = {}   # user_id: "user" / "admin"



# ================= КНОПКИ =================

user_keyboard = ReplyKeyboardMarkup(

    keyboard=[

        [KeyboardButton(text="💰 Balance")],

        [KeyboardButton(text="💵 75$"), KeyboardButton(text="💵 500$"), KeyboardButton(text="💵 1000$")]

    ],

    resize_keyboard=True

)



admin_keyboard = ReplyKeyboardMarkup(

    keyboard=[

        [KeyboardButton(text="📋 Pending Deposits")],

        [KeyboardButton(text="👤 Users")]

    ],

    resize_keyboard=True

)



# ================= /start =================

@dp.message(F.text == "/start")

async def start(message: Message):

    user_state[message.from_user.id] = "login"

    await message.answer("🔐 Enter login:")



# ================= АВТОРИЗАЦИЯ =================

@dp.message()

async def auth(message: Message):

    uid = message.from_user.id

    text = message.text

    state = user_state.get(uid)



    if state == "login":

        if text == USER_LOGIN:

            user_state[uid] = "user_password"

            await message.answer("🔑 Enter password:")

        elif text == ADMIN_LOGIN:

            user_state[uid] = "admin_password"

            await message.answer("🔑 Enter admin password:")

        else:

            await message.answer("❌ Wrong login")



    elif state == "user_password":

        if text == USER_PASSWORD:

            user_state.pop(uid)

            user_role[uid] = "user"

            await message.answer("✅ Logged in successfully", reply_markup=user_keyboard)

        else:

            await message.answer("❌ Wrong password")



    elif state == "admin_password":

        if uid == ADMIN_ID and text == ADMIN_PASSWORD:

            user_state.pop(uid)

            user_role[uid] = "admin"

            await message.answer("🛡 Admin panel", reply_markup=admin_keyboard)

        else:

            await message.answer("❌ Wrong admin password")



    # ================= МЕНЮ ПОЛЬЗОВАТЕЛЯ =================

    elif user_role.get(uid) == "user":

        if text == "💰 Balance":

            await message.answer(

                "💼 Your balances:\n\n"

                "• Working balance: 0$\n"

                "• Insurance deposit: 0$"

            )

        elif text in ["💵 75$", "💵 500$", "💵 1000$"]:

            await message.answer(

                "🧾 To activate your account, please send the insurance deposit\n\n"

                "💰 USDT (BEP20)\n"

                "📍 Address:\n"

                "`0xf3a329bf7e26fc7d2fd69762b2336805f378d07a`\n\n"

                "After payment, wait for admin confirmation ⏳",

                parse_mode="Markdown"

            )

            await bot.send_message(

                ADMIN_ID,

                f"📥 New deposit request from user {uid}\nAmount: {text}"

            )



    # ================= АДМИН =================

    elif user_role.get(uid) == "admin":

        if text == "📋 Pending Deposits":

            await message.answer("📋 Pending deposits list is empty (demo)")

        elif text == "👤 Users":

            await message.answer("👤 Users list is empty (demo)")



# ================= ЗАПУСК =================

async def main():

    await dp.start_polling(bot)



if __name__ == "__main__":

    asyncio.run(main()

                
