import asyncio

from aiogram import Bot, Dispatcher

from aiogram.types import Message



TOKEN = "8216116135:AAGTNq-_V89z6Lp_vWZ4ZTP1C1wsy-gtfiY"



async def main():

    bot = Bot(token=TOKEN)

    dp = Dispatcher()



    @dp.message(commands=["start"])

    async def start_handler(message: Message):

        await message.answer("✅ BOT IS ALIVE")



    await dp.start_polling(bot)



if __name__ == "__main__":

    asyncio.run(main())
