import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


class Finder():
    def __init__(self, name: str, refind: bool=False) -> None:
        self.name = name
        self.__refind = refind

    def __convert_date (self, date) -> str:
        return f"{str(date)[:2]}.{str(date)[2:4]}.{str(date)[4:]}"
    
    def __convert_hour (self, hour) -> int:
        if str(hour)[0] == '9': return 9
        else: return int(str(hour)[:2])
    
    def __preprocess_file (self):
        current_dir_path = os.path.abspath(f'src/data/{self.name}/')
        
        data = pd.read_csv(current_dir_path+'/data.csv', sep=';')
        data['<DATE>'] = data['<DATE>'].apply(self.__convert_date)    
        data['<TIME>'] = data['<TIME>'].apply(self.__convert_hour)
            
        return data
    
    def __finder (self) -> dict:
        data = self.__preprocess_file()
        hours, avg_volume, avg_percentage_change, avg_range_price = [], [], [], []
        
        for hour in data['<TIME>'].unique():
            hours.append(hour)
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
            avg_range_price.append(round(sum(range_price)/len(range_price)))
            
        
        return (hours, avg_volume, avg_percentage_change, avg_range_price)
    
    def __normalize_minmax (self, data: list) -> float:
        max_val = np.max(data)
        min_val = np.min(data)
        return [(x - min_val)/(max_val-min_val) for x in data]
    
    def analyzer (self, vol_weight: int=0.4, percentage_change_weight: int=0.3, range_price_weight: int=0.3) -> dict:
        hours, avg_volume, avg_percentage_change, avg_range_price = self.__finder()

        norm_volume = self.__normalize_minmax(avg_volume)
        norm_percentages = self.__normalize_minmax(avg_percentage_change)
        norm_range_price = self.__normalize_minmax(avg_range_price)
        
        # расчёт индекса для каждого часа (макс. индекс = 1)
        index_hours = []
        for i in range(len(hours)):
            index = norm_volume[i]*vol_weight \
                    + norm_percentages[i]*percentage_change_weight \
                    + norm_range_price[i]*range_price_weight
            index_hours.append((hours[i], index))
        
        best_hours_by = {}
        # поиск часа с самым высоким показателем
        max_avg_volume = max(avg_volume)
        index_max_avg_volume = avg_volume.index(max_avg_volume)
        best_hours_by['volume'] = (hours[index_max_avg_volume], max_avg_volume)
        
        max_avg_percentage_change = max(avg_percentage_change)
        index_max_avg_percentage_change = avg_percentage_change.index(max_avg_percentage_change)
        best_hours_by['percentage_change'] = (hours[index_max_avg_percentage_change], max_avg_volume)
        
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
        
        plt.title('График объема от времени')
        plt.xlabel('Часы')
        plt.ylabel('Объём')
        plt.savefig(os.path.abspath(f'src/data/{self.name}/charts/volume.png'))
        plt.clf()

        # график изменения цены в процентах от времени
        sns.lineplot(x=hours, y=avg_percentage_change, color='b')
        plt.gca().set_xticks(hours)
        
        plt.title('График изменения цены в процентах от времени')
        plt.xlabel('Часы')
        plt.ylabel('Изменение цены в процентах')
        plt.savefig(os.path.abspath(f'src/data/{self.name}/charts/percentage-change.png'))
        plt.clf()

        # график изменения диапазона цены от времени
        sns.lineplot(x=hours, y=avg_range_price, color='b')
        plt.gca().set_xticks(hours)
        
        plt.title('График диапазона цены от времени')
        plt.xlabel('Часы')
        plt.ylabel('Изменение диапазона цены')
        plt.savefig(os.path.abspath(f'src/data/{self.name}/charts/range-price.png'))
        plt.clf()

        return {'indexes': index_hours, 'best_hours_by': best_hours_by}
        
    def get_analysis (self) -> str:
        # функция предназначена для формирования анализа и отправки его в TG, поэтому уже в HTML разметке
        current_dir_path = os.path.abspath(f'src/data/{self.name}/')
        
        if os.path.exists(current_dir_path+'/result.txt') and self.__refind == False:
            with open(current_dir_path+'/result.txt', mode='r', encoding='utf8') as result_file:
                return result_file.read()
        else:
            ...
            