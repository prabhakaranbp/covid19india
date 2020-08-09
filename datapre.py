import pandas as pd
import numpy as np
import datetime
from datetime import date

dff = pd.read_csv('https://api.covid19india.org/csv/latest/districts.csv')

# Drop unwanted columns
df = dff[dff.columns[0:6]]

# Convert to date from string
# df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')

df['dist_in_state'] = df['District'].str.cat(df['State'], sep ="|") 

df_delta = df.sort_values(by=['State', 'District', 'Date'])

################################
## Daily Count                 #
################################
## District                    #
################################

def delta_districts():
  dist_delta_count = df_delta
  dist_delta_count['Delta_Confirmed'] = df_delta.groupby(['State', 'District'])['Confirmed'].diff().fillna(df_delta['Confirmed'])
  dist_delta_count['Delta_Recovered'] = df_delta.groupby(['State', 'District'])['Recovered'].diff().fillna(df_delta['Recovered'])
  dist_delta_count['Delta_Deceased'] =  df_delta.groupby(['State', 'District'])['Deceased'].diff().fillna(df_delta['Deceased'])
    
  dist_delta_count.reset_index(inplace = True, drop = True) 
  
  dist_delta_count = dist_delta_count.astype({'Delta_Confirmed': 'int64','Delta_Recovered': 'int64','Delta_Deceased': 'int64'})
  
  return(dist_delta_count)

################################
## State                       #
################################
def delta_states():
  st_delta_confirmed = pd.DataFrame(df_delta.groupby(['Date','State'])['Delta_Confirmed'].sum()) 
  st_delta_recovered = pd.DataFrame(df_delta.groupby(['Date','State'])['Delta_Recovered'].sum()) 
  st_delta_deceased  = pd.DataFrame(df_delta.groupby(['Date','State'])['Delta_Deceased'].sum())

  st_delta_confirmed['Delta_Confirmed'].astype('int64')
  st_delta_recovered['Delta_Recovered'].astype('int64')
  st_delta_deceased['Delta_Deceased'].astype('int64')

  state_concat = [st_delta_confirmed, st_delta_recovered, st_delta_deceased]
  state_delta_count = pd.concat(state_concat, join='outer', axis=1)

  state_delta_count = state_delta_count.sort_values(by=['State','Date'])
  state_delta_count.reset_index(inplace=True)

  state_delta_count = state_delta_count.astype({'Delta_Confirmed': 'int64','Delta_Recovered': 'int64','Delta_Deceased': 'int64'})

  return(state_delta_count)

################################
## Country                     #
################################

def delta_country():
  cntry_delta_confirmed = pd.DataFrame(df_delta.groupby(['Date'])['Delta_Confirmed'].sum())
  cntry_delta_recovered = pd.DataFrame(df_delta.groupby(['Date'])['Delta_Recovered'].sum())
  cntry_delta_deceased  = pd.DataFrame(df_delta.groupby(['Date'])['Delta_Deceased'].sum())

  cntry_concat = [cntry_delta_confirmed, cntry_delta_recovered, cntry_delta_deceased]
  cntry_delta_count = pd.concat(cntry_concat, join='outer', axis=1)

  cntry_delta_count = cntry_delta_count.sort_values(by=['Date'])
  cntry_delta_count.reset_index(inplace=True)

  cntry_delta_count = cntry_delta_count.astype({'Delta_Confirmed': 'int64','Delta_Recovered': 'int64','Delta_Deceased': 'int64'})

  return(cntry_delta_count)

################################
## Totals for Country          #
################################

def country_total():
  as_on_date = df['Date'].iloc[-1]
  tot_cntry_confirmed = pd.DataFrame(data=[df['Confirmed'][(df['Date']==as_on_date)].sum()],columns=['Total_Confirmed'])
  tot_cntry_recovered = pd.DataFrame(data=[df['Recovered'][(df['Date']==as_on_date)].sum()],columns=['Total_Recovered'])
  tot_cntry_deceased  = pd.DataFrame(data=[df['Deceased'][(df['Date']==as_on_date)].sum()],columns=['Total_Deceased'])

  cntry_concat = [tot_cntry_confirmed, tot_cntry_recovered, tot_cntry_deceased]
  country_totals = pd.concat(cntry_concat, join='outer', axis=1)


  country_totals.reset_index(level=0, inplace=True)
  country_totals.rename(columns={"index": "Country"},inplace=True)
  d = {0:'India'}
  country_totals = country_totals.replace(d)

  country_totals = country_totals.astype({'Total_Confirmed': 'int64','Total_Recovered': 'int64','Total_Deceased': 'int64'})

  return(country_totals)

# country_total['Total Active'] = country_total['Total Confirmed'] - country_total['Total Recovered'] - country_total['Total Deceased']
 
################################
## Totals for Districts        #
################################

def district_total():
  as_on_date = df['Date'].iloc[-1]
  district_totals = df[df['Date'] == as_on_date] 
  
  return(district_totals)

################################
## Totals for States           #
################################

def state_total():
  temp = district_total()
  df_state_total = temp.sort_values(by=['State'])

  state_total_confirmed = pd.DataFrame(df_state_total.groupby(['State'])['Confirmed'].sum())
  state_total_recovered = pd.DataFrame(df_state_total.groupby(['State'])['Recovered'].sum())
  state_total_deceased  = pd.DataFrame(df_state_total.groupby(['State'])['Deceased'].sum())

  state_concat = [state_total_confirmed, state_total_recovered, state_total_deceased]
  state_totals = pd.concat(state_concat, join='outer', axis=1)

  state_totals = state_totals.sort_values(by=['State'])
  state_totals.reset_index(inplace=True)

  state_totals = state_totals.astype({'Confirmed': 'int64','Recovered': 'int64','Deceased': 'int64'})

  return(state_totals)

def latest_date():
  as_on_date = df['Date'].iloc[-1]
  return(as_on_date)

