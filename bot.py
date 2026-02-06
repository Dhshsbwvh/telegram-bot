import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup

# ===== Настройки =====
API_TOKEN = "8216116135:AAEsqunknYT3cSl2EM_EvTYBbhjZJOWfhOw"
ADMIN_ID = 7625893405 # твой Telegram ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ===== Логины =====
USER_LOGIN = "pronto"
USER_PASSWORD = "ZeMDZxwv"

ADMIN_LOGIN = "SuperAdm1nX"
ADMIN_PASSWORD = "7vZ#9qLp!2T"

# ===== Состояние =====
auth_stage = {} # user_id: "login" / "password_user" / "password_admin"

# ===== Клавиатуры =====
def user_kb():
kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add("📊 Balance")
kb.add("🟢 $75 [Circle]", "🌾 $500 [Agro Farm]", "🏭 $1000 [Farm]")
return kb

def admin_kb():
kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add("📋 Pending Deposits", "📬 User Requests")
return kb

# ===== START =====
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
uid = message.from_user.id
auth_stage[uid] = "login"
await message.answer("🔐 Enter login:")

# ===== AUTH =====
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
auth_stage.pop(uid)
await message.answer("✅ Logged in as user", reply_markup=user_kb())
else:
await message.answer("❌ Wrong password")
elif stage == "password_admin":
if uid == ADMIN_ID and text == ADMIN_PASSWORD:
auth_stage.pop(uid)
await message.answer("🛡 Admin panel", reply_markup=admin_kb())
else:
await message.answer("❌ Wrong admin password")

# ===== RUN =====
if __name__ == "__main__":
executor.start_polling(dp, skip_updates=True)
