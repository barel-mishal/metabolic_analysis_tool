import pandas as pd
import numpy as np 
import streamlit as st
from healpers import custome_days, incal_format, join_path, light_and_dark, remove_outliers_mixed_df
import plotly.express as px

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

def main():
  path_design_exp = join_path('data', 'exp_shani', 'modified', 'InCal_format_your_Design_SHANI.csv')
  path_data_exp = join_path('data', 'exp_shani', 'modified', 'InCal_format_SHANI.csv')
  design_exp_df = pd.read_csv(path_design_exp)
  exp_df = incal_format(path_data_exp, path_design_exp).rename(columns=NAMES_COLUMNS)

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
    option_freq = st.selectbox('Parmeters', ('D', 'H', '5min'))
  with col2:
    option_parms = st.selectbox('Parmeters', tuple(exp_df.columns))
  with col3:
    option_radio = st.radio('remove 2std', ('yes', 'no'))
  with col4:
    option_not_in = st.multiselect('Parmeters', (str(i) for i in exp_df.index.get_level_values(1).unique()))
  

  exp_df = exp_df[~exp_df.index.get_level_values(1).isin(option_not_in)]
  

  if option_radio == 'yes':
    data = remove_outliers_mixed_df(exp_df)[option_parms]
  else: 
    data = exp_df[option_parms]
  if option_freq == '5min': 
    # make it possibale to see as a groups
    fig = px.line(x=data.index.get_level_values(0), y=data, color=data.index.get_level_values(1), markers=True, labels={'y': option_parms, 'x': 'Date Time'})
  else: 
    data = data.groupby([pd.Grouper(level=0, freq=option_freq), exp_df.index.get_level_values(2)]).mean()
    fig = px.line(x=data.index.get_level_values(0), y=data, color=data.index.get_level_values(1), markers=True, labels={'y': option_parms, 'x': 'Date Time'})

  csv = convert_df(data)

  st.download_button(
    "Press to Download",
    csv,
    "file.csv",
    "text/csv",
    key='download-csv'
  )
  
  
  st.plotly_chart(fig)
  st.text('''
  לעיל פלוט המציג ממוצע משקלי שעתי של קבוצות העכברים על ציר זמן
  

  עקב המשקל הנמוך של קבוצה שאכלה ארוחה עם כמות שומן נמוכה נבדוק אינדבדאולית כל אחד וניתן צבע לקבוצה
  ''')
  
  
  data = exp_df['BodyMass (gram)'].groupby([pd.Grouper(level=3, freq='H'), exp_df.index.get_level_values(1)]).mean()
  not_in = ['12']
  data = data[~data.index.get_level_values(1).isin(not_in)]
  data
  cond = [data.index.get_level_values(1).isin(design_exp_df.set_index('Unnamed: 0').loc[name].astype('string')) for name in design_exp_df['Unnamed: 0']]
  cond[0]
  choice = design_exp_df['Unnamed: 0'].to_list()
  groups = np.select(cond, choice)
  fig = px.line(x=data.index.get_level_values(0), y=data, color=data.index.get_level_values(1), markers=True, labels={'y': 'weight (gram)', 'x': 'Date Time'})
  st.plotly_chart(fig)
  st.text('''
  לעיל פלוט המציג ממוצע משקלי שעתי של העכברים על ציר זמן

  בקבוצה הכחולה ראינו שיש שונות המשקל של עכבר 12 לא עבד לכן נוריד אותו בכלל מהחישוב

  נבדוק עכשיו את הדלטה של כל קבוצות העכברים לראות מה ההבדל בין הקבוצות כאשר כולם מתחילם מאותו משקל
  ''')









if __name__ == '__main__':
  main()
