"""
This script adds the precipitation data pulled from NOAA to the county-level and statewide data
previously pulled from your database.

Ensure that you have already gathered the county-level and statewide crash data before running this script.
"""



import pandas as pd

# ========= Add Precipitation to County Data ===========

county_dict = {
    1:  "County_1",
    2:  "County_2",
    3:  "County_3",
    -1: "NOT REPORTED"
}

# add precipitation data to crash data.
prcp_df = pd.read_csv("counties_daily_precip_avg.csv")
prcp_df.rename({'value':'Rainfall'}, axis=1, inplace=True)

for c in county_dict.values():
    fp = f'{c}/{c}_all.csv'
    df = pd.read_csv(fp)
    if 'Rainfall' in df.columns:
        df.drop('Rainfall', axis=1, inplace=True)                               # Remove the rainfall field from previous runs
    county_prcp = prcp_df[prcp_df['county_name'] == c]                                # Filter prcp to current county
    df = df.merge(county_prcp, how='outer', left_on='CrashDate', right_on='date')     # right join to get precipitation even if there are no crashes
    df.CrashDate = df.CrashDate.fillna(df.date)                                       # Fill Crash dates from precipitation data
    df.drop(columns=['date','county_name'], inplace=True)
    df.fillna(0,inplace=True)                                                   # Fill all other crash count fields with 0
    df.to_csv(fp, index=False)

# ========== Add Precipitation to State Data ===========
df_counties_agg = (
    prcp_df
    .groupby('date', as_index=False)
    ['Rainfall']
    .mean()
)

state_fp = 'STATEWIDE/STATEWIDE_all.csv'

df_state = pd.read_csv(state_fp)
if 'date' in df_state.columns:
    df_state.drop('date', axis=1, inplace=True)
if 'Rainfall' in df_state.columns:
    df_state.drop('Rainfall', axis=1, inplace=True)

df_state = pd.merge(df_state, df_counties_agg, how='outer', left_on='CrashDate', right_on='date')
df_state.drop('date', axis=1, inplace=True)
df_state.to_csv(state_fp, index=False)
