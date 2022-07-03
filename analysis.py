from operator import le
import pandas as pd
import numpy as np 
import streamlit as st
from healpers import custome_days, incal_format, join_path, light_and_dark, remove_outliers_mixed_df
import plotly.express as px
import stumpy
# todo : units
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
    elif i == 'Late_TRF':
      return df_for_filter.index.isin(df_for_filter.between_time('16:00', '00:00').index)
    elif i == 'Early_TRF':
      return df_for_filter.index.isin(df_for_filter.between_time('00:00', '08:00').index)   
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
  # add here the data end in 20:00
  exp_df

  st.text('Fit Time To Time Expriment')


  exp_times = custome_days(exp_df.index.get_level_values('Date_Time_1'), 8)
  exp_dark_light = light_and_dark(exp_df.index.get_level_values('Date_Time_1'), '08:00', '16:00')
  series_times = pd.Series(exp_times, name='Expriments Times')
  series_dark_light = pd.Series(exp_dark_light, name='DarkLight')
  exp_df.set_index([series_times, series_dark_light], append=True, inplace=True)
  # export files - all data points
  # publish_results_all_data_points(exp_df)

  df_for_filter = exp_df.index.to_frame().reset_index(drop=True)[['Date_Time_1', 'Group']].set_index('Date_Time_1')
  exp_df.set_index([pd.Series(eat_or_restrict(df_for_filter), name='EatRestrict')], append=True, inplace=True)
  # export all data after marking
  exp_df.to_csv(join_path('data', 'exp_shani', 'modified', 'marks_for_analysis.csv'))
  # export all groups seperted
  # publish_results_groups_seperted(exp_df)


  st.text(
  '''
  TODO: agg all data to the mean or sum
  ''')
  col1, col2, col3, col4 = st.columns(4)
  with col1:
    option_freq = st.selectbox('Rolling Mean', ('H', '5min', 'D'))
  with col2:
    columns = exp_df.columns.to_list()
    temp = columns[0]
    columns[0] = columns[11]
    columns.append(temp)
    option_parms = st.selectbox('Parmeters', columns)
  with col3:
    option_radio = st.radio('remove 2std', ('no', 'yes'))
  with col4:
    option_not_in = st.multiselect('Remove Cages', (str(i) for i in exp_df.index.get_level_values(1).unique()))
  col1_1, col2_1, col3_1, col4_1 = st.columns(4)
  with col1_1:
    Group_Individual = st.selectbox('Parmeters', ('group', 'individual'))
  with col2_1:
    color_lines = st.selectbox('Color lines', ('Group', 'subjectsID', 'Expriments Times', 'DarkLight'))
  with col3_1:
    x_axis = st.selectbox('X axis', ('Date_Time_1', 'Expriments Times', 'DarkLight', 'Group', 'subjectsID'))


  if option_not_in:
    exp_df = exp_df[~exp_df.index.get_level_values(1).isin(option_not_in)]
  if option_radio == 'yes':
    exp_df = remove_outliers_mixed_df(exp_df)[option_parms]
  # todo - fix bugs
  if Group_Individual == 'individual': 
    data = exp_df[option_parms]
    if option_freq != '5min':
      group = pd.Grouper(level='Date_Time_1', freq=option_freq)
      data = data.groupby([group, exp_df.index.get_level_values(1)]).mean()
  elif Group_Individual == 'group':
    data = exp_df[option_parms].unstack([1, 2]).groupby([exp_df[option_parms].unstack([1, 2]).columns.get_level_values(1)], axis=1).mean()
    if option_freq != '5min':
      group = pd.Grouper(level='Date_Time_1', freq=option_freq)
      data = data.groupby([group]).mean().stack()
    else:
      data = data.stack()

  csv = convert_df(data)
  st.download_button(
    "Press to Download",
    csv,
    "file.csv",
    "text/csv",
    key='download-csv'
  )

  col1_2, col2_2 = st.columns(2) 


  d = data.reset_index()
  # d.loc[:2]

  fig = px.line(
    x=d[x_axis].values, 
    y=data, 
    color=d[color_lines], 
    markers=True, 
    labels={'y': option_parms, 'x': 'Date Time'}, 
    template="plotly_white"
    )
  
  st.plotly_chart(fig)
  d.shape
  time_diff = d[x_axis].iloc[-1] - d[x_axis].iloc[0]
  time_diff
  d.set_index('Expriments Times', inplace=True)
  for group in ['LowFat', 'HighFatAdLibitum', 'Early_TRF', 'Late_TRF']:
    new_d = d[d['Group'] == group]
    m = 4
    mp = stumpy.stump(new_d[0], m)
    mp



  # todo - add delta analysis

  # todo - add cumuletive columns

  # todo - add statistical analysis comper between 

  # add slice datetime with slider

  # use stumpy for analysis

  # find motif in time series data
  
if __name__ == '__main__':
  main()
