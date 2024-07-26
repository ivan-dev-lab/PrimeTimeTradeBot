from aiogram import F, Bot, Dispatcher, Router, types
from aiogram.filters import Command
import asyncio
import os
import shutil
from src.core import finder
from config import decrypt, load_dotenv

decrypt(filepath_in='.env.enc', filepath_out='.env')
BOT_TOKEN = load_dotenv(filepath_env='.env')['BOT_TOKEN']
os.remove(os.path.abspath('.env'))

bot = Bot(BOT_TOKEN)
dp = Dispatcher()



@dp.message(Command('help'))
async def start (message: types.Message):
    instruction_photo = types.FSInputFile(os.path.abspath('src/Bot/instruction.jpg'))
    text = '<b>ИНСТРУКЦИЯ ПО ЗАГРУЗКЕ ДАННЫХ</b>\n\n'
    text+='Программа настроена на обработку данных <b>только с https://www.finam.ru/quote/moex/gdu4202309/export/</b>\n'
    text+='Для корректной обработки данных следует обратить внимание на следуюшие пункты:\n\n'
    text+='1) Периодичность - <b>1 час</b>\n'
    text+='2) Имя файла - сокращенное название актива/контракта (на примере - GDU4|GDU2024)\n'
    text+='3) Тип файла <b>.csv</b>\n'
    text+='4) Формат времени: обязательно первые два символа должны быть <b>чч</b>'
    text+='5) Время - <b>московское</b>\n'
    text+='6) Разделитель полей - <b>точка с запятой ;</b>\n'
    text+='7) Формат записи в файл - <b>DATE, TIME, OPEN, HIGH, LOW, CLOSE, VOL</b>\n'
    await bot.send_photo(message.chat.id, instruction_photo, caption=text, parse_mode='HTML')
        
    
    
    
async def main ():
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    asyncio.run(main())