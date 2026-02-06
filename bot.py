import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import (
ReplyKeyboardMarkup,
KeyboardButton,
InlineKeyboardMarkup,
InlineKeyboardButton
)

API_TOKEN = os.environ.get("API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ====== AUTH DATA ======
USER_LOGIN = "pronto"
USER_PASSWORD = "ZeMDZxwv"

ADMIN_LOGIN = "SuperAdm1nX"
ADMIN_PASSWORD = "7vZ#9qLp!2T"

ADMIN_ID = 7625893405 #

# ====== STORAGE ======
users = {} # user_id: {"balance": int}
pending = [] # {"user_id": int, "amount": int}
auth_stage = {} # user_id: stage

# ====== KEYBOARDS ======
def user_kb():
kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add("📊 Balance")
kb.add("🟢 $75 [Circle]")
kb.add("🌾 $500 [Agro Farm]")
kb.add("🏭 $1000 [Farm]")
kb.add("🔄 Update Info")
return kb

def admin_kb():
kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add("📋 Pending Deposits")
return kb

# ====== START ======
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
auth_stage[message.from_user.id] = "login"
await message.answer("🔐 Enter login:")

# ====== AUTH ======
@dp.message_handler()
async def auth(message: types.Message):
uid = message.from_user.id

if uid not in auth_stage:
return

stage = auth_stage[uid]

if stage == "login":
if message.text == USER_LOGIN:
auth_stage[uid] = "password_user"
await message.answer("🔑 Enter password:")
elif message.text == ADMIN_LOGIN:
auth_stage[uid] = "password_admin"
await message.answer("🔑 Enter admin password:")
else:
await message.answer("❌ Wrong login")

elif stage == "password_user":
if message.text == USER_PASSWORD:
users.setdefault(uid, {"balance": 0})
auth_stage.pop(uid)
await message.answer("✅ Logged in", reply_markup=user_kb())
else:
await message.answer("❌ Wrong password")

elif stage == "password_admin":
if message.text == ADMIN_PASSWORD and uid == ADMIN_ID:
auth_stage.pop(uid)
await message.answer("🛡 Admin panel", reply_markup=admin_kb())
else:
await message.answer("❌ Access denied")

# ====== USER BUTTONS ======
@dp.message_handler(text="📊 Balance")
async def balance(message: types.Message):
bal = users.get(message.from_user.id, {}).get("balance", 0)
await message.answer(f"💰 Your balance: ${bal}")

@dp.message_handler(text="🟢 $75 [Circle]")
async def dep_75(message: types.Message):
pending.append({"user_id": message.from_user.id, "amount": 75})
await message.answer("⏳ Insurance deposit $75 pending")

@dp.message_handler(text="🌾 $500 [Agro Farm]")
async def dep_500(message: types.Message):
pending.append({"user_id": message.from_user.id, "amount": 500})
await message.answer("⏳ Insurance deposit $500 pending")

@dp.message_handler(text="🏭 $1000 [Farm]")
async def dep_1000(message: types.Message):
pending.append({"user_id": message.from_user.id, "amount": 1000})
await message.answer("⏳ Insurance deposit $1000 pending")

@dp.message_handler(text="🔄 Update Info")
async def update_info(message: types.Message):
await message.answer("ℹ️ Update temporarily unavailable")

# ====== ADMIN ======
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
InlineKeyboardButton(
"✅ Received",
callback_data=f"ok_{dep['user_id']}_{dep['amount']}"
),
InlineKeyboardButton(
"❌ Not received",
callback_data=f"no_{dep['user_id']}_{dep['amount']}"
)
)
await message.answer(text, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("ok_"))
async def confirm(callback: types.CallbackQuery):
_, uid, amount = callback.data.split("_")
uid = int(uid)
amount = int(amount)

users.setdefault(uid, {"balance": 0})
users[uid]["balance"] += amount

pending[:] = [p for p in pending if not (p["user_id"] == uid and p["amount"] == amount)]

await bot.send_message(uid, f"✅ Deposit ${amount} received")
await callback.answer("Confirmed")

@dp.callback_query_handler(lambda c: c.data.startswith("no_"))
async def reject(callback: types.CallbackQuery):
_, uid, amount = callback.data.split("_")
uid = int(uid)
amount = int(amount)

pending[:] = [p for p in pending if not (p["user_id"] == uid and p["amount"] == amount)]

await bot.send_message(uid, f"❌ Deposit ${amount} not received")
await callback.answer("Rejected")

# ====== RUN ======
if __name__ == "__main__":
executor.start_polling(dp, skip_updates=True)
