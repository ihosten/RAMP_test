import pandas as pd


def read_tendo_file(file_path):
    df_tendo = pd.read_csv(file_path)

    training_names = {
        'hyp LE 5 sets': 'LE_HYP_5x12',
        'hyp LE 8 sets': 'LE_HYP_8x12',
        'max LE': 'LE_MAX',
        'hyp LP': 'LP_HYP_5x12'
    }

    df_tendo['type_training'] = df_tendo['type_training'].replace(training_names)
    df_tendo= df_tendo.rename(columns={'type_training': 'training'})
    #df_tendo = df_tendo.drop(columns=['Unnamed: 0.2', 'Unnamed: 0.1', 'Unnamed: 0'])

    df_tendo['delta_v'] = df_tendo['velocity'].diff()

    starts_of_set = df_tendo[df_tendo['velocity']==0].index
    df_tendo.loc[starts_of_set, 'delta_v'] = 0


    df_tendo['delta_time'] = df_tendo['time'].diff()
    df_tendo['acc'] = df_tendo['delta_v']/ df_tendo['delta_time']
    df_tendo.loc[df_tendo['acc']<-10, ['acc', 'delta_v', 'delta_time']] = 0
    
    
    return df_tendo


def weight(group, athletes):
    match group['training'].iloc[1]:
        case 'LE_HYP_5x12':
            weight = athletes[str(group['pp'].iloc[1])]['hyp_LE']
        case 'LE_HYP_8x12':
            weight = athletes[str(group['pp'].iloc[1])]['hyp_LE']
        case 'LP_HYP_5x12':
            weight = athletes[str(group['pp'].iloc[1])]['hyp_LP']
        case 'LE_MAX':
            weight = athletes[str(group['pp'].iloc[1])]['max_LE']
        case _:
            raise KeyError(group['training'].iloc[1])
    
    return weight
    
    