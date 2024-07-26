from aiogram import F, Bot, Dispatcher, Router, types
from aiogram.filters import Command
import asyncio
import os
import shutil
from src.core.finder import Finder
from config import decrypt, load_dotenv

# decrypt(filepath_in='.env.enc', filepath_out='.env')
# BOT_TOKEN = load_dotenv(filepath_env='.env')['BOT_TOKEN']
# os.remove(os.path.abspath('.env'))

# bot = Bot(BOT_TOKEN)

bot = Bot('7222661918:AAEF8_eUubcFl7SP1yswBD_KuFvb_HP_4zk')
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
        
@dp.message(F.content_type.in_([types.ContentType.DOCUMENT]))
async def start (message: types.Message):
    document = message.document
    file_id = document.file_id

    file_info = await bot.get_file(file_id)

    user_dir = os.path.abspath(f'src/data/{message.chat.id}')
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    
    fin_asset_dir = f'{user_dir}/{document.file_name.split(".")[0]}/'
    if not os.path.exists(fin_asset_dir):
        os.makedirs(fin_asset_dir)
    else:
        shutil.rmtree(fin_asset_dir)
        os.makedirs(fin_asset_dir)
    
    os.makedirs(f'{fin_asset_dir}/charts/')
    download_path = os.path.join(fin_asset_dir, 'data.csv')

    await bot.download_file(file_info.file_path, download_path)
    
    finder = Finder(document.file_name.split(".")[0], message.chat.id)
    analyz = finder.get_analysis()
    
    media = []
    for chart_photo in os.listdir(os.path.join(fin_asset_dir, 'charts/')):
        media.append(types.InputMediaPhoto(media=types.FSInputFile(f'{fin_asset_dir}/charts/{chart_photo}')))
    
    await bot.send_media_group(message.chat.id, media)
    await bot.send_message(message.chat.id, analyz, parse_mode='HTML')

async def main ():
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    asyncio.run(main())