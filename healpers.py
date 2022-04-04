import itertools
import os
import pandas as pd
import datetime as dt
import numpy as np
# marks
def custome_days(pd_DateTime64, hour=00, minute=00, sec=00):
    time_1 = dt.timedelta(hours=00, minutes=00, seconds=00)
    time_2 = dt.timedelta(hours=hour, minutes=minute, seconds=sec)
    return (pd_DateTime64 - (time_2 - time_1))

def light_and_dark(pd_index_datetime, start='08:30', end='16:30'):
    times = np.array([time.time() for time in pd_index_datetime])
    greater = pd.to_datetime(start).time() <= times
    stricly_less = pd.to_datetime(end).time() > times
    return np.where((greater & stricly_less), 'light', 'dark')

# format
def flat_list(d_list):
    '''
    dependencies: itertools
    '''
    return list(itertools.chain.from_iterable(d_list))


def incal_create_df_incal_format(df_data_experiment, df_design_expriment):
    df = df_data_experiment.copy()
    categories_groups = df_design_expriment.values[:, 0]
    categories_subjects = list(
        filter(lambda x: ~np.isnan(x),
               (flat_list(df_design_expriment.values[:, 1:]))))
    date_time_level = pd.Series((pd.DatetimeIndex(df['Date_Time_1'])),
                                name='Date_Time_1')
    subjects_level = pd.Series(pd.Categorical(df['subjectID'].astype('string'),
                                              categories=[str(n) for n in categories_subjects],
                                              ordered=True),
                                              name='subjectsID')
    group_level = pd.Series(pd.Categorical(df['Group'],
                                           categories=categories_groups,
                                           ordered=True),
                                           name='Group')

    df = df.drop(columns=['Date_Time_1', 'subjectID', 'Group'])

    multi_index_dataframe = pd.concat(
        [date_time_level, subjects_level, group_level], axis=1)
    

    return pd.DataFrame(df.values,
                        index=pd.MultiIndex.from_frame(multi_index_dataframe),
                        columns=df.columns.values.tolist()).sort_index(level=['Date_Time_1', 'subjectsID'])

def incal_format(path, experiment_design_path):
    df = pd.read_csv(path, parse_dates=['Date_Time_1'])
    exp_df = pd.read_csv(experiment_design_path)
    df = incal_create_df_incal_format(df, exp_df)
    df['locomotion'] = df['xbreak'].add(df['ybreak'])
    df = df.drop(columns=['vh2o', 'xbreak', 'ybreak'])
    return df


# os
def join_path(*args):
  __DIRNAME__ = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(__DIRNAME__, *args)







# remove outliears

# removing outliears
def sort_data_by_ids(df, column_name):
    return df.sort_values(column_name)


def flat_list(d_list):
    '''
    dependencies: itertools
    '''
    return list(itertools.chain.from_iterable(d_list))


def slice_df_for_floats_and_category(df, column_name):
    return df.select_dtypes(include=['float64']), df.select_dtypes(
        include=['category'])


def get_subject_ids(df, column_name):
    return df[column_name].unique()


def calc_mean_and_std_for_df_by_ids(df, ids_values):
    return df.groupby(ids_values).agg([np.mean, np.std])


def get_lims_upper_and_lower(df_means_and_stds,
                             number_of_ids,
                             number_featuers_columns,
                             by_sd_of=2):
    calcs_shape_values = df_means_and_stds.values.reshape(
        number_of_ids, number_featuers_columns, 2)
    means = calcs_shape_values[:, :, :1]
    stds = calcs_shape_values[:, :, 1:]
    upper_lims = means + stds * by_sd_of
    lower_lims = means - stds * by_sd_of
    return upper_lims, lower_lims


def reshpe_vlaues_3d_ndarray(ndarray, axis0_dimensions, axis1_columns,
                             axis2_rows):
    return ndarray.reshape(axis0_dimensions, axis1_columns, axis2_rows)


def select_and_replace_outliers(ndarry_of_features, ndarry_uppers_lims,
                                ndarry_lowers_lims):
    conditiones = [
        ndarry_of_features > ndarry_uppers_lims,
        ndarry_of_features < ndarry_lowers_lims
    ]
    choices = [np.nan, np.nan]
    return np.select(conditiones, choices, ndarry_of_features)


def back_to_2d_ndarray(ndarry_of_features, axis1, axis2):
    return ndarry_of_features.reshape(axis1, axis2)


def sort_data_by_index(df):
    return df.sort_index()


def get_categories_cals_names(df):
    return df.index.names[1:]


def incal_get_categories_col_from_multiindex(df):
    levels_names = get_categories_cals_names(df)
    get_values_values_from_index = df.reset_index(level=levels_names)
    return get_values_values_from_index[levels_names]


def remove_outliers_mixed_df(df):
    # sourcery skip: inline-immediately-returned-variable
    sorted_df = df.sort_index(level=1)
    fetuers, ids = df.values, df.index
    df_means_and_stds = calc_mean_and_std_for_df_by_ids(
        df,
        ids.get_level_values(1).astype('int32'))
    number_of_ids = len(ids.levels[1].categories.astype('int32'))
    fetuers_columns = df.columns
    number_featuers_columns = len(fetuers_columns)
    upper_lims, lower_lims = get_lims_upper_and_lower(df_means_and_stds,
                                                      number_of_ids,
                                                      number_featuers_columns)
    dimensions_by_numbers_of_ids_upper_lims = reshpe_vlaues_3d_ndarray(
        upper_lims, number_of_ids, 1, number_featuers_columns)
    dimensions_by_numbers_of_ids_lower_lims = reshpe_vlaues_3d_ndarray(
        lower_lims, number_of_ids, 1, number_featuers_columns)
    columns_of_each_id = fetuers.shape[0] // number_of_ids
    dimensions_by_numbers_of_ids_values = reshpe_vlaues_3d_ndarray(
        fetuers, number_of_ids, columns_of_each_id, number_featuers_columns)
    outliers_replaced_to_nan_values_ndarray = select_and_replace_outliers(
        dimensions_by_numbers_of_ids_values,
        dimensions_by_numbers_of_ids_upper_lims,
        dimensions_by_numbers_of_ids_lower_lims)
    combien_axis0_and_axis1 = number_of_ids * columns_of_each_id
    original_df_shape = back_to_2d_ndarray(
        outliers_replaced_to_nan_values_ndarray, combien_axis0_and_axis1,
        number_featuers_columns)
    df_fetuers_without_outliers = pd.DataFrame(original_df_shape,
                                               columns=fetuers_columns,
                                               index=ids)
    df_without_outliers = pd.concat([df_fetuers_without_outliers], axis=1)
    return df_without_outliers