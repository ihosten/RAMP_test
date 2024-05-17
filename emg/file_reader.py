from emg_handler import Find_reps
import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import logging

trainings = {
    0: 0,
    'LE_HYP_5x12': 1,
    'LE_HYP_8x12' : 2,
    'LE_MAX_5x5': 3,
    'LP_HYP_5x12': 4   
}

path = './raw_emg_data/'

logging.basicConfig(filename='file_reader.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
padding = 700


for folder in [folder for folder in os.listdir(path) if folder not in ['ALL']]:
    participant = folder
    folder_path = f'./raw_emg_data/{participant}/'
    df_list = []


    logging.info(f'programme started for {participant}')
    for file_name_calibration in os.listdir(folder_path):
        if file_name_calibration.endswith('0.txt'):
            training_id = '_'.join(file_name_calibration.split('_')[1:4])
            file_path_calibration = os.path.join(folder_path, file_name_calibration)
            emg_hanlder = Find_reps(file_path_calibration, 0, file_name_calibration[0])
            df_calibration = emg_hanlder._rolling_window()
            df_calibration['training_id'] = trainings[training_id]
            df_calibration['rep'] = 0
            df_calibration['set'] = 0
            df_calibration['pp'] = file_name_calibration[0]
            df_list.append(df_calibration)
            max = df_calibration[df_calibration['Rolling_RMS_vl']>40]['Rolling_RMS_vl'].mean()
            
            
            for file_name in os.listdir(folder_path):
                if file_name != file_name_calibration:
                    training_id = '_'.join(file_name.split('_')[1:4])
                    if training_id == '_'.join(file_name_calibration.split('_')[1:4]):
                        file_path = os.path.join(folder_path, file_name)
                        set = file_name.split('.')[-2][-1]
                        emg_handler_file = Find_reps(file_path, training_id, file_name[0])
                        df, threshold = emg_handler_file.reps_rolling_avg(max)
                        if not df.empty:
                            plt.figure()
                            sns.lineplot(data=df, x='time' , y='Rolling_RMS_vl', hue='rep')
                            plt.axhline(threshold)
                            plt.savefig(f'./plots/{training_id}_{participant}_{set}')
                            plt.close()
                            df['set'] = set
                        df_list.append(df)
                        
        else:
            continue


    result = pd.concat(df_list, ignore_index=True)
    result.to_csv(f'result_{participant}.csv')
    logging.info('file saved')

