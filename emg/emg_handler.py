import pandas as pd 
import numpy as np
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from emg_filter import butter_bandpass_filter

trainings = {
    0: 0,
    'LE_HYP_5x12': 1,
    'LE_HYP_8x12' : 2,
    'LE_MAX_5x5': 3,
    'LP_HYP_5x12': 4   
}

REPS_A_TRAINING = {
    
    1 : 12,
    2 : 12,
    3 : 4,
    4 : 12
}

COLUMNS = {
                'Time,s': 'time',
                'RT VLO,uV' : 'vl',
                'RT RECTUS FEM.,uV' : 'rf',
                'RT VMO,uV' : 'vm'
                
                }



class Find_reps:
    def __init__(self, file_path, training_id, pp):
        self.file_path = file_path
        self.df = self.__read_csv_file()
        self.training_id = trainings[training_id]
        self.pp = pp
        
        
    
    
    def __read_csv_file(self):
        df = pd.read_csv(self.file_path, delimiter='\t', skiprows=4)
        df.rename(columns=COLUMNS, inplace=True)
        
        
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df['rep'] = None
        list_of_names = [value for value in COLUMNS.values()]
        df = df.drop([column for column in df.columns if column.startswith('Mark') or column not in list_of_names], axis=1)
        return df
        
        
    def _rep_based_up(self, df, name='vl'):
        return df[f'Rolling_RMS_{name}']
    
    def _rolling_window(self, window_size='200ms'):
        df = self.df.copy()
        cols_to_abs = df.columns.difference(['time', 'rep'])
        abs_columns = [f'{column}_abs' for column in cols_to_abs]
        rolling_rms_columns = [f'Rolling_RMS_{column}' for column in cols_to_abs]
        filtered_columns = [f'Filtered_{column}' for column in cols_to_abs]        
        window_size_int = int(pd.Timedelta(window_size).total_seconds() * 1000)
        
        
        cols_filterd = df[cols_to_abs].apply(butter_bandpass_filter, lowcut=10, highcut=500, fs=1500)
        df[filtered_columns] = cols_filterd
        df[abs_columns] = df[filtered_columns].abs()
        
        rolling_rms_values = df[filtered_columns].rolling(window=window_size_int, min_periods=1, center=True) \
                                    .apply(lambda x: np.sqrt(np.mean(x**2)))
                                    
        df[rolling_rms_columns] = rolling_rms_values
        return df
    
    
    
    def reps_deritative(self):
        df_to_check = self._rolling_window()
        dx = df_to_check['time'].diff().dt.total_seconds()
        dy = self._rep_based_up(df_to_check).diff()
        df_to_check["f(x)'"] = dy/dx
        return df_to_check

    def reps_rolling_avg(self, threshold = 50, time_between_reps = 200, padding=600, threhold_muliplier=0.40, trail=1):
        """checking on reps based on the rolling average
        returns a dataframe with the reps"""
        logging.debug(f'tral: {trail}, thresholds: {threshold}, threshold_mulitplier: {threhold_muliplier}')
        threshold_raw = threshold
        threshold *= threhold_muliplier
        df_to_check = self._rolling_window(window_size='700ms')
            
        df_to_check['rep_busy'] = abs(self._rep_based_up(df_to_check)) > threshold
        print('*'*5, 'trail:', trail, '*'*5)
        
        rep = 0
        prev_row_same = True 
        for i ,row in df_to_check.iterrows():
            if i > 0 and df_to_check.loc[i-1, 'rep_busy'] == row['rep_busy']:
                prev_row_same = True 
            else:
                prev_row_same = False
            
            if row['rep_busy'] == False:
                df_to_check.at[i, 'rep'] = 0
                continue
            
            elif row['rep_busy'] == True and prev_row_same:
                df_to_check.at[i, 'rep'] = rep
                
            elif row['rep_busy'] == True and not prev_row_same:
                
                if rep>=1:
                    if (df_to_check['time'].iloc[i] - df_to_check['time'][df_to_check['rep'] == rep].iloc[-1]) < pd.Timedelta(f'{time_between_reps}ms'):
                        continue
                rep += 1
                df_to_check.at[i, 'rep'] = rep
                print(row['time'], rep)
            
            else:
                logging.error('fail kut')
                
        for i in range(1, rep+1):
            min_index, max_index = df_to_check[df_to_check['rep']==i].index.min(), df_to_check[df_to_check['rep']==i].index.max() 
            df_to_check.loc[min_index-padding:max_index+padding, 'rep'] = i
             
        df_to_check = df_to_check.dropna(subset=['time', 'Rolling_RMS_vl', 'rep'])   
        if df_to_check['rep'].max() != REPS_A_TRAINING[self.training_id] and trail < 70:
            df_to_check, threshold = self.reps_rolling_avg(threshold=threshold_raw, threhold_muliplier=threhold_muliplier+0.05, trail=trail+1)
            
            
            if df_to_check.empty or df_to_check['rep'].max() == REPS_A_TRAINING[self.training_id]:
                return df_to_check, threshold
        
        elif trail == 70:
            logging.critical(f'no reps where found in file: {self.file_path}')
            return pd.DataFrame(), threshold
           
        else:     
            self.df['rep'] = df_to_check['rep']
            df_to_check['pp'] = self.pp
            df_to_check['training_id'] = self.training_id
            
            logging.info(f'right amount of reps are found in {self.file_path} with threshold {threshold}')
            logging.debug(f'after else statement {rep} len of df: {len(df_to_check)}, trail: {trail}')
        
            return df_to_check, threshold
    

    



    