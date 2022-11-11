from operator import le
from pickle import TRUE
import pandas as pd
import numpy as np 
import streamlit as st
from healpers import custome_days, incal_format, join_path, light_and_dark, remove_outliers_mixed_df
import plotly.express as px
import stumpy
# todo : units
# to run file
# open venv/script/activate.ps1
# then streamlit run analysis.py
# todo : check late files
#  todo : order gorups numbers
# todo : agg data for each parmetr 


NAMES_COLUMNS = {
    'actual_allmeters': 'AllMeters (m)',
    'actual_foodupa': 'FoodUpa (gram)',
    'actual_foodupa_caloirs': 'FoodUpa (kcal)',
    'actual_pedmeters': 'Pedmeters (m)',
    'actual_waterupa': 'WaterUpa (gram)', 
    'bodymass': 'BodyMass (gram)', 
    'kcal_hr': 'Kcal_hr (kcal/hr)', 
    'rq': 'RER', 
    'vco2': 'Co2 ml/min', 
    'vo2': 'Vo2 ml/min',   
    'locomotion': 'Locomotion (brakes)'
  }

def publish_results_all_data_points(df):
  for name in df.columns: 
    st.text(name)
    file_name = name.split(' ')[0]
    df_to_csv = df[name].unstack([1, 2])
    df_to_csv.to_csv(join_path('data', 'exp_shani', 'analysis_all_group_together', f'{file_name}.csv'))

def publish_results_groups_seperted(df):
  low_and_high = df[df.index.get_level_values(2).isin(['LowFat', 'HighFatAdLibitum'])] 
  low_and_high.to_csv(join_path(
    'data', 
    'exp_shani', 
    'analysis_groups_seperted',
    'LowFatAndHighFatAdLibitum',
    'LowFat_HighFatAdLibitum_all_data.csv'))
  for name in low_and_high.columns: 
    st.text(name)
    df_to_csv = low_and_high[name].unstack([1, 2])
    file_name = name.split(' ')[0]
    df_to_csv.to_csv(join_path(
      'data', 
      'exp_shani', 
      'analysis_groups_seperted',
      'LowFatAndHighFatAdLibitum',
      f'{ file_name }.csv'))
  Late_TRF = df[df.index.get_level_values(2).isin(['Late_TRF'])]
  Late_TRF.to_csv(join_path(
    'data', 
    'exp_shani', 
    'analysis_groups_seperted',
    'Late_TRF',
    'Late_TRF.csv'))
  for name in Late_TRF.columns: 
    st.text(name)
    df_to_csv = Late_TRF[name].unstack([1, 2])
    file_name = name.split(' ')[0]
    df_to_csv.to_csv(join_path(
      'data', 
      'exp_shani', 
      'analysis_groups_seperted',
      'Late_TRF',
      f'{file_name}.csv'))
  Early_TRF = df[df.index.get_level_values(2).isin(['Early_TRF'])]
  Early_TRF.to_csv(join_path(
    'data', 
    'exp_shani', 
    'analysis_groups_seperted',
    'Early_TRF',
    'Early_TRF.csv'))
  for name in Early_TRF.columns: 
    st.text(name)
    df_to_csv = Early_TRF[name].unstack([1, 2])
    file_name = name.split(' ')[0]
    df_to_csv.to_csv(join_path(
      'data', 
      'exp_shani', 
      'analysis_groups_seperted',
      'Early_TRF',
      f'{file_name}.csv'))
    
def eat_or_restrict(df):
  def create_cond(i, df_for_filter):
    if i in ['LowFat', 'HighFatAdLibitum']:
      return i == df_for_filter.Group.values
    # eat 8 - 16 (zt === Expriments Times) 
    # 16 - 00 (CT === שעון אכילה Date_Time_1)
    # 16 17 18 19 20 21 22 23 
    elif i == 'Early_TRF':
      df1 = df_for_filter.Group.values == i
      df2 = df_for_filter.between_time('16:00', '00:00') 
      isdf2 = df_for_filter.index.isin(df2.index)
      filters = (df1) & (isdf2)
      return filters
    # eat 8 - 16 (zt === Expriments Times) 
    # 00 - 08 (CT === שעון אכילה Date_Time_1)
    elif i == 'Late_TRF':
      df1 = df_for_filter.Group.values == i
      df2 = df_for_filter.between_time('00:00', '08:00') 
      isdf2 = df_for_filter.index.isin(df2.index)
      filters = (df1) & (isdf2)  
      return filters
  conds = [create_cond(i, df) for i in df.Group.unique()]
  choices = ['Eat', 'Eat', 'Eat', 'Eat']
  return np.select(conds, choices, 'Restrict')

def convert_df(df):
   return df.to_csv().encode('utf-8')

def uploadFile():
  path_design_exp = join_path('data', 'exp_shani', 'modified', 'InCal_format_your_Design_SHANI.csv')
  path_data_exp = join_path('data', 'exp_shani', 'modified', 'InCal_format_SHANI.csv')
  design_exp_df = pd.read_csv(path_design_exp)
  exp_df = incal_format(path_data_exp, path_design_exp).rename(columns=NAMES_COLUMNS)
  return design_exp_df, exp_df

def main():
  # add for seperting somefunctionality 
  # connect to mongodb db to create and add file upload
  design_exp_df, exp_df = uploadFile()
  st.text('Design expriment:')
  design_exp_df
  st.text('Data')
  exp_df
  st.text('Fit Time To Time Expriment')
  exp_times = custome_days(exp_df.index.get_level_values('Date_Time_1'), 8)
  exp_dark_light = light_and_dark(exp_df.index.get_level_values('Date_Time_1'), '16:00', '00:00')
  series_times = pd.Series(exp_times, name='Expriments Times')
  series_dark_light = pd.Series(exp_dark_light, name='DarkLight')
  exp_df.set_index([series_times, series_dark_light], append=True, inplace=True)
  df_for_filter = exp_df.index.to_frame().reset_index(drop=True)[['Date_Time_1', 'Group']].set_index('Date_Time_1')
  exp_df.set_index([pd.Series(eat_or_restrict(df_for_filter), name='EatRestrict')], append=True, inplace=True)

  # csv = convert_df(exp_df)
  # st.download_button(
  #   "Press to Download",
  #   csv,
  #   "marks_for_analysis.csv",
  #   "text/csv",
  #   key='download-csv'
  # )

  publish_results_all_data_points(exp_df)
  publish_results_groups_seperted(exp_df)


  
if __name__ == '__main__':
  main()
