import pandas as pd
import os

class Finder():
    def __init__(self, name: str, refind: bool=False) -> None:
        self.result = self.get_result()
        self.name = name
        self.__refind = refind
    
    def __convert_date (self, date) -> str:
        return f"{str(date)[:2]}.{str(date)[2:4]}.{str(date)[4:]}"
    def __convert_time (self, time) -> int:
        if str(time)[0] == '9': return 9
        else: return int(str(time)[:2])
 
    def __preprocess_file (self):
        current_dir_path = os.path.abspath(f'src/data/{self.name}/')
        
        data = pd.read_csv(current_dir_path+'/data.csv', sep=';')
        data['<DATE>'] = data['<DATE>'].apply(self.__convert_date)    
        data['<TIME>'] = data['<TIME>'].apply(self.__convert_time)
            
        return data
        
    def __find (self) -> dict:
        data = self.__preprocess_file()
        hours = {}
        for time in data['<TIME>'].unique():
            time_data = {}
            time_data['avg_volume'] = round(data.loc[data['<TIME>'] == time]['<VOL>'].mean(), 2)
            
            percentages = []
            range_price = []
            for time_values in data.loc[data['<TIME>'] == time].values:
                # столбцы 2 и 5 - open и close
                open_price, close_price = time_values[2], time_values[5]
                
                # столбцы 3 и 4 - high и low
                high, low = time_values[3], time_values[4]
                
                # расчет изменения в процентах
                if open_price > close_price:
                    percentages.append( abs(((close_price*100)/open_price)-100) )
                else:
                    percentages.append( abs(((open_price*100)/close_price)-100) )

                # расчет диапазона изменения цены
                range_price.append(high-low)
                    
            time_data['avg_percentages'] = round(sum(percentages)/len(percentages), 2)
            time_data['range_price'] = round(sum(range_price)/len(range_price)) 
            
            hours[time] = time_data
            
        return hours
            
    def get_result (self):
        ...
