import json
import math

from importlib import reload

import tendo_calculations
reload(tendo_calculations)

with open('athletes.json', 'r') as file:     
    athletes =  json.load(file) 

#---------------------------------------------------------------------
#------------------INTERNAL TRIMPS------------------------------------
#--------------------------------------------------------------------- 

def edwardsTRIMP(group) -> int:
    max_hr = athletes[str(group['id'].iloc[1])]['max_HR']
    EdwardTRIMP = []
    
    for Hr, td in zip(group["heart_rate"], group["delta_time"]):
        if td == None:
            pass
        elif 0.01 < Hr <= 0.6 * max_hr:
            EdwardTRIMP.append(td * 1)
        elif 0.6 * max_hr < Hr <= 0.7 * max_hr:
            EdwardTRIMP.append(td * 2)
        elif 0.7 * max_hr < Hr <= 0.8 * max_hr:
            EdwardTRIMP.append(td * 3)
        elif 0.8 * max_hr < Hr <= 0.9 * max_hr:
            EdwardTRIMP.append(td * 4)
        elif 0.9 * max_hr < Hr <= max_hr:
            EdwardTRIMP.append(td * 5)
    
    filtered_list = [x for x in EdwardTRIMP if not math.isnan(x)]
    sessionTRIMP = sum(filtered_list) 
          
    return sessionTRIMP



def luciaTRIMP(group)-> int:
    max_hr = athletes[str(group['id'].iloc[1])]['max_HR']
    hr_threshold_1 = athletes[str(group['id'].iloc[1])]['AeD_HR']
    hr_threshold_2 = athletes[str(group['id'].iloc[1])]['AnD_HR']
    
    
    luTRIMP_list = []

    for Hr, td in zip(group["heart_rate"],group["delta_time"]):
        if td == None:
            pass
        elif 0.01 < Hr <= hr_threshold_1:
            luTRIMP_list.append(td*1)
        elif hr_threshold_1 < Hr <= hr_threshold_2:
            luTRIMP_list.append(td*2)
        elif hr_threshold_2 < Hr <= max_hr:
            luTRIMP_list.append(td*3)
    filtered_list = [x for x in luTRIMP_list if not math.isnan(x)]
    sessionTRIMP = sum(filtered_list)
    
    return sessionTRIMP



def barnisterTRIMP(group)-> int:
    barnisterTRIMP_list = []
    max_hr = athletes[str(group['id'].iloc[1])]['max_HR']
    min_hr = athletes[str(group['id'].iloc[1])]['min_HR']
    
    for Hr, td in zip(group["heart_rate"],group["delta_time"]):
        if td == None:
            pass
        else:
            hr_scaled = (Hr - min_hr) / (max_hr - min_hr)
            y = 0.64 * math.exp(1.92 * hr_scaled)
            barnisterTRIMP_list.append(td* hr_scaled * y)
            
    filtered_list = [x for x in barnisterTRIMP_list if not math.isnan(x)]
    sessionTRIMP = sum(filtered_list)

    return sessionTRIMP


#---------------------------------------------------------------------
#------------------EXTERNAL TRIMPS------------------------------------
#---------------------------------------------------------------------    


def total_work_done(group, return_trimp = True)->int:
    mass = tendo_calculations.weight(group, athletes=athletes)
    group['work_done'] = mass* (group['acc']+9.81) * (group['displacement'].max()/1000)
    if return_trimp:
        return group['work_done'].sum()/1000
    else:
        group['force'] =  mass* (group['acc']+9.81)
        group['power'] = group['force'] * group['velocity']
        group['work_done'] = group['work_done']/1000
        return group

def total_work_done_exponational_weighted(group)->int:
    mass = tendo_calculations.weight(group, athletes=athletes)
    group['work_done'] = mass**3* (group['acc']+9.81) * (group['displacement'].max()/1000)
    return (group['work_done'].sum()/1000)*(group['rep'].max() / group['set'].max())

def tonnage(group)->int:
    mass = tendo_calculations.weight(group, athletes=athletes)
    return group['set'].max() * group['rep'].max() * mass

def impuls(group):
    mass = tendo_calculations.weight(group, athletes=athletes)
    group['impulse'] = group['delta_v']*mass
    return group['impulse'].sum()

    
    
    
            
            