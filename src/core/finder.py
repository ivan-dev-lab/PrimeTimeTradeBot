import pandas as pd
import os

class Finder():
    def __init__(self, name: str, refind: bool=False) -> None:
        self.result = ...
        self.name = name
        self.__refind = refind
    
    def __convert_date (self, date) -> str:
        return f"{str(date)[:2]}.{str(date)[2:4]}.{str(date)[4:]}"
    def __convert_time (self, time):
        if str(time)[0] == '9': return 9
        else: return int(str(time)[:2])
 
    def __preprocess_file (self):
        current_dir_path = os.path.abspath(f'src/data/{self.name}/')
        
        if os.path.exists(current_dir_path+'/result.txt') and self.__refind == False:
            result = ''
            with open(current_dir_path+'/result.txt', mode='r', encoding='utf8') as result_file:
                return result_file.read()
        else:
            data = pd.read_csv(current_dir_path+'/data.csv')
            data['<DATE>'] = data['<DATE>'].apply(self.__convert_date)    
            data['<TIME>'] = data['<TIME>'].apply(self.__convert_time)
            
            return data
