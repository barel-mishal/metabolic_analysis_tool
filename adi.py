import pandas as pd
import numpy as np 

import plotly.express as px


df = pd.read_csv('data/adi_pharma/hebrew_2022-03-06_15_18_adi_pharmcokintics_no_mm3_030622_m_calr.csv')

columns_names = {l.rsplit('_', 1)[0] for l in df.columns.to_list()}
numbers_canges = sorted({l.rsplit('_', 1)[1] for l in df.columns.to_list()}, key=int)
date_time_exp = pd.to_datetime(df['Date_Time_1'])
# kcal_hr cumulative 
kcal_hr = df[[f'kcal_hr_{i}' for i in numbers_canges]]

groups1 = {
  '1': 'CBD', 
  '2': 'CBD', 
  '3': 'THC', 
  '4': 'THC', 
  '5': 'VEHICLE', 
  '6': 'VEHICLE', 
  '7': 'VEHICLE', 
  '8': 'CBD', 
  '9': 'VEHICLE', 
  '10': 'VEHICLE', 
  '11': 'VEHICLE', 
  '12': 'VEHICLE', 
  '13': 'CBD', 
  '14': 'THC', 
  '15': 'THC'
}

groups2 = {
  'CBD': ['1', '2', '8', '13'],
  'THC': ['3', '4', '14', '15'],
  'VEHICLE': ['5', '6', '7', '9', '10', '11', '12']
}.items()


cumsum_kcal_hr = kcal_hr.cumsum().rename(columns={f'kcal_hr_{num}': num for num in numbers_canges}).set_index(date_time_exp)

stack_kcal_hr = cumsum_kcal_hr.stack()

def make_column_group(subjects, groups):
  cons = [subjects == sub for g, s in groups for sub in s]
  chos = [g for g, s in groups for sub in s]
  return np.select(cons, chos)
  
res = stack_kcal_hr.to_frame().set_index(make_column_group(stack_kcal_hr.index.get_level_values(1), groups2), append=True)
res.sort_index(level=[0, 2]).unstack([1, 2]).to_csv('data/adi_pharma/adi_pharma_cumulative_kcal_hr.csv')



# cumsum_kcal_hr.set_index(axis=1, append=True).to_csv('adi_pharma_cumulative_kcal_hr.csv')



###
# {
# 'vco2', 
# 'pedmeters', 
# 'kcal_hr', 
# 'vh2o', 
# 'foodupa', 
# 'envirolightlux', 
# 'envirotemp', 
# 'envirosound', 
# 'vo2', 
# 'envirorh', 
# 'rq', 
# 'waterupa', 
# 'Date_Time', 
# 'ybreak', 
# 'envirooccupancy', 
# 'allmeters', 
# 'xbreak'
# }



