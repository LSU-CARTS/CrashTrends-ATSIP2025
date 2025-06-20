# Precipitation is gathered per NOAA station. There can be more than one per county.
# This script combines precipitation files and averages by county (across stations)

import pandas as pd

years = ['2018','2019','2020','2021','2022','2023','2024']

df = pd.DataFrame()

for year in years:
    FILE_NAME = f'your_state_daily_precip_{year}.csv'

    df_year = pd.read_csv(FILE_NAME)
    df = pd.concat([df,df_year])

df_agg = df.groupby(['county_name','date'])['value'].mean()

df_agg = df_agg.reset_index()
df_agg['date'] = pd.to_datetime(df_agg['date'])

df_agg.to_csv('counties_daily_precip_avg.csv',index=False)

