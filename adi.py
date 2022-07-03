import pandas as pd
import numpy as np 

import plotly.express as px


df = pd.read_csv('data/adi_pharma/hebrew_2022-03-06_15_18_adi_pharmcokintics_no_mm3_030622_m_calr.csv')

columns_names = {l.rsplit('_', 1)[0] for l in df.columns.to_list()}
numbers_canges = sorted({l.rsplit('_', 1)[1] for l in df.columns.to_list()}, key=int)
date_time_exp = pd.to_datetime(df['Date_Time_1'])
# kcal_hr cumulative 
kcal_hr = df[[f'kcal_hr_{i}' for i in numbers_canges]]
cumsum_kcal_hr = kcal_hr.cumsum().rename(columns={f'kcal_hr_{num}': num for num in numbers_canges}).set_index(date_time_exp)
cumsum_kcal_hr.to_csv('adi_pharma_cumulative_kcal_hr.csv')




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



