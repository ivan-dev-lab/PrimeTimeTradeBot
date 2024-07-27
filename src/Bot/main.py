from aiogram import F, Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import os
import shutil
import json
from src.core.finder import Finder
from config import decrypt, load_dotenv

decrypt(filepath_in='.env.enc', filepath_out='.env')
BOT_TOKEN = load_dotenv(filepath_env='.env')['BOT_TOKEN']
os.remove(os.path.abspath('.env'))

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def start (message: types.Message):
    text = 'Бот умеет анализировать отправленные вами данные по активу с сайта finam.ru\n\nДля начала работы:\n<b>/help</b> - бот вышлет инструкцию по загрузке данных\n<b>/menu</b> - переход в главное меню бота для просмотра анализа своих активов\n<b>/summary</b> - бот пришлет сводку с двумя лучшими часа для торговли по каждому из активов'
    await bot.send_message(message.chat.id, text, parse_mode='HTML')

@dp.message(Command('help'))
async def get_help (message: types.Message):
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
    text+='\nПосле получения <b>.csv</b> данных с правильным форматом, просто отправьте файл PrimeTimeTradeBot и вам будет прислан анализ'
    await bot.send_photo(message.chat.id, instruction_photo, caption=text, parse_mode='HTML')
        
@dp.message(F.content_type.in_([types.ContentType.DOCUMENT]))
async def upload_data (message: types.Message):
    document = message.document
    
    if document.mime_type == 'text/csv':

        file_id = document.file_id

        file_info = await bot.get_file(file_id)
    
        user_dir = os.path.abspath(f'data/{message.chat.id}')
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
    
        Finder(document.file_name.split(".")[0], message.chat.id).save_analysis()
    
        await bot.send_message(message.chat.id, 'Данные успешно обработаны. Ознакомиться с результатами вы можете в меню бота <b>/menu</b>', parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, '<b>Недопустимый формат файла. Необходим .csv</b>', parse_mode='HTML')
       
@dp.message(Command('menu'))
async def display_menu (message: types.Message):
    menu_text = 'Главное меню <b>PrimeTimeTradeBot</b>\n\n'
    
    try:
        assets_builder = InlineKeyboardBuilder()
        list_fin_assets = os.listdir(os.path.abspath(f'data/{message.chat.id}/'))
        
        menu_text+='Сохраненные активы:\n'
        for idx, fin_asset in enumerate(list_fin_assets, start=1):
            menu_text+=f'{idx}. <b>{fin_asset}</b>;\n'
            assets_builder.add(types.InlineKeyboardButton(text=fin_asset, callback_data=f'fin_asset-{fin_asset}'))
        assets_builder.adjust(4)
        menu_text+='\nЗапросить сводку по всем активам - <b>/summary</b>'
        menu_text+='\n\nИнструкция по загрузке данных - <b>/help</b>'
        menu_text+='\n\nЗапросить полный анализ по сохраненному активу - кнопки снизу ↘️'
       
        await bot.send_message(message.chat.id, menu_text, parse_mode='HTML', reply_markup=assets_builder.as_markup())
    except:
        menu_text+='Пока что вы не загрузили данные по активам.\nИнструкция как это сделать - <b>/help</b>\n'
        await bot.send_message(message.chat.id, menu_text, parse_mode='HTML')

@dp.callback_query(F.data.startswith('fin_asset'))    
async def get_analys (callback: types.CallbackQuery):
    fin_asset = callback.data.split('-')[1]
    fin_asset_dir = f'data/{callback.message.chat.id}/{fin_asset}/'
    with open(os.path.abspath(f'{fin_asset_dir}/result.txt'), mode='r', encoding='utf8') as result_file:
        result_text = result_file.read()
        result_text+='\n\nОбратно в меню - <b>/menu</b>'
        
        media = []
        for chart_photo in os.listdir(os.path.join(fin_asset_dir, 'charts/')):
            media.append(types.InputMediaPhoto(media=types.FSInputFile(f'{fin_asset_dir}/charts/{chart_photo}')))
        
        if media: await bot.send_media_group(callback.message.chat.id, media)

        await bot.send_message(callback.message.chat.id, result_text, parse_mode='HTML')

@dp.message(Command('summary'))
async def get_summary (message: types.Message):
    user_dir = os.path.abspath(f'data/{message.chat.id}/')
    summary_text = []
    start_summary_text = 'Сводка по вашим активам: '

    for idx, fin_asset in enumerate(os.listdir(user_dir)):
        fin_asset_json_path = f'{user_dir}/{fin_asset}/result.json'
        
        if idx != len(os.listdir(user_dir))-1: start_summary_text+=f'<b>{fin_asset}</b>, '
        else: start_summary_text+=f'<b>{fin_asset}</b>'
        
        
        with open(fin_asset_json_path, mode='r') as json_result_file:
            data = json.load(json_result_file)
            fin_asset_summary_text = f'Сводка по <b>{fin_asset}</b>:\n\n'
            fin_asset_summary_text+=f'<b>Топ 3 лучших часов для торговли {fin_asset} согласно индексам:</b>\n'
            
            for index_hour in data['indexes'][:3]:
                if len(str(index_hour[1])) < 4: index_hour_str = f'{index_hour[1]}0'
                else: index_hour_str = str(index_hour[1])                    
                if index_hour[0] == 9: 
                    fin_asset_summary_text+=f'0{index_hour[0]}:00 = {index_hour_str}\n'
                else:
                    fin_asset_summary_text+=f'{index_hour[0]}:00 = {index_hour_str}\n'    
                    
            fin_asset_summary_text+=f'\n<b>Лучшие часы для торговли {fin_asset} согласно показателям актива:</b>\n'
            fin_asset_summary_text+=f'Самый большой объем = <b>{data["best_hours_by"]["volume"][0]}:00 - {data["best_hours_by"]["volume"][1]}</b>\n'
            fin_asset_summary_text+=f'Самое большое изменение цены в процентах = <b>{data["best_hours_by"]["percentage_change"][0]}:00 - {data["best_hours_by"]["percentage_change"][1]}%</b>\n'
            fin_asset_summary_text+=f'Самый большой диапазон изменения цены = <b>{data["best_hours_by"]["range_price"][0]}:00 - {data["best_hours_by"]["range_price"][1]} пп.</b>\n'
            
            summary_text.append(fin_asset_summary_text)
            
    summary_text.append(start_summary_text)
    
    for text in reversed(summary_text):
        await bot.send_message(message.chat.id, text, parse_mode='HTML')
    
async def main ():
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    asyncio.run(main())