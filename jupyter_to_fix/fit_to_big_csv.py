import fitparse
import pandas as pd
import os

def fit_to_df(fit_file):
    fitfile = fitparse.FitFile(fit_file)
    messages = fitfile.messages
    data = []

    for message in messages:
        if message.name == 'record':
            fields = message.fields
            message_data = {}
            for field in fields:
                if field.name == 'heart_rate':
                    message_data['heart_rate'] = field.value
                elif field.name == 'timestamp':
                    message_data['timestamp'] = field.value
            data.append(message_data)

    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df

folder_path = '../hr_data'
output_file = 'hr_output.csv'
list_df = []
training_types = {
        1:'LE_HYP_5x12',
        2:'LE_HYP_8x12',
        3:'LE_MAX',
        4:'LP_HYP_5x12'
    }

for fit_file in os.listdir(folder_path):
    if not fit_file.endswith('.fit'):
        print(f'{fit_file} was not a .fit file and not processed')
        continue
    
    file_path = os.path.join(folder_path, fit_file)
    id = int(input(f'pp id for {fit_file}: '))
    training = int(input(f'tye op training for file {fit_file}: '))
    training = training_types.get(training)
    print(id, training)
    
    df = fit_to_df(file_path)
    df['id'] = id
    df['training'] = training
    list_df.append(df)

df_final = pd.concat(list_df)
df_final['delta_time'] = df_final['timestamp'].diff()
df_final['delta_time'] = df_final['delta_time'].dt.total_seconds()
df_final.to_csv(output_file, index=False)
