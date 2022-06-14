# from aiogram import Bot, Dispatcher, types
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.utils import executor
#
# import config
#
#
# API_TOKEN = config.API_TG_BOT_TOKEN
#
#
# bot = Bot(token=API_TOKEN)
# storage = MemoryStorage()
# dp = Dispatcher(bot, storage=storage)
#
#
# class StartBot(StatesGroup):
#     language = State()
#     rules = State()
#
#
# @dp.message_handler(commands='start')
# async def cmd_start(message: types.Message):
#     await StartBot.language.set()
#     await message.answer('Hello! Choose language')
#
#
# @dp.message_handler(state=StartBot.language)
# async def process_name(message: types.Message, state: FSMContext):
#     await StartBot.next()
#     await message.answer("Here is rules")
#
#
# @dp.message_handler(state=StartBot.rules)
# async def process_name(message: types.Message, state: FSMContext):
#     await message.answer("DONE!")
#     await state.finish()
#
#
# if __name__ == '__main__':
#     executor.start_polling(dp, skip_updates=True)