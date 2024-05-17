import os
import multiprocessing
import logging
import matplotlib as plt
import seaborn as sns
from emg_handler import Find_reps

trainings = {
    0: 0,
    'LE_HYP_5x12': 1,
    'LE_HYP_8x12' : 2,
    'LE_MAX_5x5': 3,
    'LP_HYP_5x12': 4   
}


path = './raw_emg_data/'

logging.basicConfig(filename='file_reader.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

for folder in [folder for folder in os.listdir(path) if folder not in ['ALL']]:
    participant = folder
    folder_path = f'./raw_emg_data/{participant}/'
    file_path_list = []
    df_list = []


    logging.info(f'programme started for {participant}')


    def process_calibration(calibration_file_name):
        file_path_calibration = os.path.join(folder_path, calibration_file_name)
        emg_handler_calibration = Find_reps(file_path_calibration, 0, calibration_file_name[0])
        df_calibration = emg_handler_calibration._rolling_window()
        max_value = df_calibration[df_calibration['Rolling_RMS_vl'] > 40]['Rolling_RMS_vl'].mean()
        
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.txt') and file_name != calibration_file_name:
                training_id = '_'.join(file_name.split('_')[1:4])
                if training_id == '_'.join(calibration_file_name.split('_')[1:4]):
                    file_path = os.path.join(folder_path, file_name)
                    set = file_name.split('.')[-2][-1]
                    emg_handler_file = Find_reps(file_path, training_id, file_name[0])
                    df, threshold = emg_handler_file.reps_rolling_avg(max_value)
                    if not df.empty:
                        plt.figure()
                        sns.lineplot(data=df, x='time' , y='Rolling_RMS_vl', hue='rep')
                        plt.axhline(threshold)
                        plt.savefig(f'./plots/{training_id}_{participant}_{set}')
                        plt.close()
                        df['set'] = set
                    df_list.append(df)
        
        df_calibration['training_id'] = trainings[training_id]
        df_calibration['rep'] = 0
        df_calibration['set'] = 0
        df_calibration['pp'] = file_name[0]
        df_list.append(df_calibration)

    # List calibration files
    calibration_files = [file_name for file_name in os.listdir(folder_path) if file_name.endswith('0.txt')]

    # Process calibration files concurrently
    pool = multiprocessing.Pool()
    pool.map(process_calibration, calibration_files)
    pool.close()
    pool.join()
