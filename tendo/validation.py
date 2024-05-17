from settings import REPS_A_TRAINING, SETS_A_TRAINING



def tendo_validation(df, type='rep'):
    training_types = set(df['type_training'])
    wrong = list()
    for training_type in training_types:
        df = df[df['type_training'] == training_type]
        
        if type == 'rep':
            df_filter = (df['rep'] != REPS_A_TRAINING[training_type])
            wrong.append(df[df_filter].index)
            
        elif type == 'set':
            df_filter = (df['set'] != SETS_A_TRAINING[training_type])
            wrong.append(df[df_filter].index)
            
        else:
            raise KeyError(type)
        
    return wrong
        