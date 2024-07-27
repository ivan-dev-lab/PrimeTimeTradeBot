import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json


class Finder():
    def __init__(self, name: str, chat_id: int, weights: tuple=(0.4, 0.3, 0.3)) -> None:
        self.name = name
        self.chat_id = chat_id
        self.vol_weight, self.percentage_change_weight, self.range_price_weight = weights
    
    def __convert_hour (self, hour) -> int:
        if str(hour)[0] == '9': return 9
        else: return int(str(hour)[:2])
    
    def __preprocess_file (self):
        current_dir_path = os.path.abspath(f'data/{self.chat_id}/{self.name}/')

        data = pd.read_csv(current_dir_path+'/data.csv', sep=';')

        try:
            if '<TIME>' in data.columns:
                data['<TIME>'] = data['<TIME>'].apply(self.__convert_hour)
                return data
            else:
                raise ValueError('Файл был загружен не с finam.ru')
        except ValueError as error_message:
            return str(error_message)  
    
    def __finder (self) -> dict:
        data = self.__preprocess_file()
        
        # это означает, что __preprocess_file() вернул не ошибку
        if type(data) != str:
            hours, avg_volume, avg_percentage_change, avg_range_price = [], [], [], []
        
            for hour in data['<TIME>'].unique():
                hours.append(int(hour))
                avg_volume.append(round(data.loc[data['<TIME>'] == hour]['<VOL>'].mean(), 2))
            
                percentages = []
                range_price = []
                for hour_values in data.loc[data['<TIME>'] == hour].values:
                    # столбцы 2 и 5 - open и close
                    open_price, close_price = hour_values[2], hour_values[5]
                
                    # столбцы 3 и 4 - high и low
                    high, low = hour_values[3], hour_values[4]
                
                    # расчет изменения в процентах
                    if open_price > close_price:
                        percentages.append( abs(((close_price*100)/open_price)-100) )
                    else:
                        percentages.append( abs(((open_price*100)/close_price)-100) )

                    # расчет диапазона изменения цены
                    range_price.append(high-low)

            
                avg_percentage_change.append(round(sum(percentages)/len(percentages), 2))
                avg_range_price.append(round(sum(range_price)/len(range_price), 2))
        
            return (hours, avg_volume, avg_percentage_change, avg_range_price)
        else: 
            return data
    
    def __normalize_minmax (self, data: list) -> float:
        max_val = np.max(data)
        min_val = np.min(data)
        
        if max_val == min_val:
            return [0.0 for _ in data]
        
        return [(x - min_val)/(max_val-min_val) for x in data]
    
    def __analyze (self) -> dict:
        response = self.__finder()
        if type(response) != str:
            hours, avg_volume, avg_percentage_change, avg_range_price = response

            norm_volume = self.__normalize_minmax(avg_volume)
            norm_percentages = self.__normalize_minmax(avg_percentage_change)
            norm_range_price = self.__normalize_minmax(avg_range_price)
        
            # расчёт индекса для каждого часа (макс. индекс = 1)
            index_hours = []
            for i in range(len(hours)):
                index = norm_volume[i]*self.vol_weight \
                        + norm_percentages[i]*self.percentage_change_weight \
                        + norm_range_price[i]*self.range_price_weight
                index_hours.append((hours[i], round(index, 2) ))
        
            best_hours_by = {}
            # поиск часа с самым высоким показателем
            max_avg_volume = max(avg_volume)
            index_max_avg_volume = avg_volume.index(max_avg_volume)
            best_hours_by['volume'] = (hours[index_max_avg_volume], max_avg_volume)
        
            max_avg_percentage_change = max(avg_percentage_change)
            index_max_avg_percentage_change = avg_percentage_change.index(max_avg_percentage_change)
            best_hours_by['percentage_change'] = (hours[index_max_avg_percentage_change], max_avg_percentage_change)
        
            max_avg_range_price = max(avg_range_price)
            index_max_avg_range_price = avg_range_price.index(max_avg_range_price)
            best_hours_by['range_price'] = (hours[index_max_avg_range_price], max_avg_range_price)

            # построение графиков
            # строится график с обычными данными и нормализованными

            # график объема от времени
            plt.rcParams['figure.figsize'] = [12, 6]
            sns.set_style('darkgrid')
        
            sns.lineplot(x=hours, y=avg_volume, color='b')
            plt.gca().set_xticks(hours)
        
            plt.title(f'График объема от времени {self.name}')
            plt.xlabel('Часы')
            plt.ylabel('Объём')
            plt.savefig(os.path.abspath(f'data/{self.chat_id}/{self.name}/charts/volume.png'))
            plt.clf()

            # график изменения цены в процентах от времени
            sns.lineplot(x=hours, y=avg_percentage_change, color='b')
            plt.gca().set_xticks(hours)
        
            plt.title(f'График изменения цены в процентах от времени {self.name}')
            plt.xlabel('Часы')
            plt.ylabel('Изменение цены в процентах')
            plt.savefig(os.path.abspath(f'data/{self.chat_id}/{self.name}/charts/percentage-change.png'))
            plt.clf()

            # график изменения диапазона цены от времени
            sns.lineplot(x=hours, y=avg_range_price, color='b')
            plt.gca().set_xticks(hours)
        
            plt.title(f'График диапазона цены от времени {self.name}')
            plt.xlabel('Часы')
            plt.ylabel('Изменение диапазона цены')
            plt.savefig(os.path.abspath(f'data/{self.chat_id}/{self.name}/charts/range-price.png'))
            plt.clf()

            return {'indexes': index_hours, 'best_hours_by': best_hours_by}
        else:
            return response
    def get_analysis (self) -> str:
        # функция предназначена для формирования анализа и отправки его в TG, поэтому уже в HTML разметке
        current_dir_path = os.path.abspath(f'data/{self.chat_id}/{self.name}/')
        
        response =  self.__analyze()
        if type(response) != str:
            indexes_hours, best_hours_by = response['indexes'], response['best_hours_by'] 
            result_text = f'<b>Анализ {self.name}</b>\n\n'
            
            result_text+=f'<b>Лучшие часы для торговли {self.name} согласно индексам:</b>\n'
            indexes_hours.sort(key = lambda x: x[1], reverse=True)
            
            for index_by_hour in indexes_hours:
                if len(str(index_by_hour[1])) < 4: index_hour_str = f'{index_by_hour[1]}0'
                else: index_hour_str = str(index_by_hour[1])                    
                if index_by_hour[0] == 9: 
                    result_text+=f'0{index_by_hour[0]}:00 = {index_hour_str}\n'
                else:
                    result_text+=f'{index_by_hour[0]}:00 = {index_hour_str}\n'
            
            result_text+=f'\n<b>Лучшие часы для торговли {self.name} согласно показателям актива:</b>\n'
            result_text+=f'Самый большой объем = <b>{best_hours_by["volume"][0]}:00 - {best_hours_by["volume"][1]}</b>\n'
            result_text+=f'Самое большое изменение цены в процентах = <b>{best_hours_by["percentage_change"][0]}:00 - {best_hours_by["percentage_change"][1]}%</b>\n'
            result_text+=f'Самый большой диапазон изменения цены = <b>{best_hours_by["range_price"][0]}:00 - {best_hours_by["range_price"][1]} пп.</b>\n'
            
            result_text+='\n<b>Время указано по МСК (UTC+3)</b>'

            with open(os.path.join(current_dir_path, 'result.txt'), mode='w+', encoding='utf8') as txt_result_file:
                txt_result_file.write(result_text)

            with open(os.path.join(current_dir_path, 'result.json'), mode='w') as json_result_file:
                json.dump(response, json_result_file, default=str)

            return result_text
        else:
            return response