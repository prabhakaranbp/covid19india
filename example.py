import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.offline as pyo
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import os
import datapre
import datetime

##############################
# Daily count                #
##############################
dd = datapre.delta_districts()
ds= datapre.delta_states()
dc= datapre.delta_country()

##############################
# Totals                     #
##############################
ct= datapre.country_total()
dt= datapre.district_total()
st= datapre.state_total()

##############################
# Last collected data        #
##############################
as_on_date = datapre.latest_date()

##############################
# Create Components          #
##############################

def delta_plot(x_value,y1,y2,y3,loc):
  trace1 = go.Scatter(x=x_value,
                    y=y1,
                    mode = 'lines+markers',
                    name = 'Confirmed Cases',
                    line=dict(color='#76a8f5', width=2)
                    )
  trace2 = go.Scatter(x=x_value,
                    y=y2 ,
                    mode = 'lines+markers',
                    name = 'Recovered',
                    line=dict(color='#5df207', width=2)
                    )
  trace3 = go.Scatter(x=x_value,
                    y=y3,
                    mode = 'lines+markers',
                    name = 'Deceased',
                    line=dict(color='#ab321f', width=2)
                    )
  
  data = [trace1,trace2,trace3]
    
  location = 'Cases Reported in '+loc
  layout = go.Layout(title =  dict(text = location,
                               font =dict(family='Sherif',size=25,color = 'white')),
                     paper_bgcolor='rgba(0,0,0,0)',
                     plot_bgcolor='rgba(0,0,0,0)')

  fig = go.Figure(data= data, layout = layout)
  fig.update_yaxes(type="log",showline=True,mirror=True,color='crimson')
  fig.update_xaxes(showline=True,mirror=True,color='crimson')
  fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(color="white"),
        ),
    margin=dict(
        l=25,
        r=25,
        b=25,
        t=25,
        pad=2),
    yaxis_showgrid=False,
    xaxis = dict(
        title_text = "Date",
        title_font = {"size": 20},
        title_standoff = 25),
    yaxis = dict(
        title_text = "Count",
        title_standoff = 25)
   )
  return(fig)



app = dash.Dash(external_stylesheets=[dbc.themes.CYBORG])


inputs = dbc.FormGroup([
    html.H4("Select State"),
    dcc.Dropdown(id="state", options=[{"label":x,"value":x} for x in ds['State'].unique()], value="India")
]) 

input2 = dbc.FormGroup([
    html.H4("Select District"),
    dcc.Dropdown(id = "district_value",
                    value=[]
                )])

##############################
# Create the layout          #
##############################


app.layout = dbc.Container(
    [
        html.H1("Covid 19 Dashboard",style={"color":"#00cc99"}),
        html.Hr(),

               
        dbc.Row([
            dbc.Col(md=4, children=[
            inputs, 
            html.Br(),html.Br(),
            html.Div(id="output-panel")
            ]),
            dbc.Col(md=4, children=[
            input2,
            html.Br(),html.Br(),            
            html.Div(id="dist-panel")
            ])
        ]),

        dbc.Row(
            [
                dbc.Col(html.Div(id="card-panel"), width={"size": 3, "order": 1}),
                dbc.Col(dcc.Graph(id='delta_figure'),
                        width={"size": 9, "order": "last"})
                
            ],
            align="center",
        ),
    ],
    fluid=True,
)

##############################
# Callbacks                  #
##############################

@app.callback(Output('district_value', 'options'),[Input('state', 'value')])
def set_district_options(state):
 
    if state != 'India' or state != None:
        return [{'label': i, 'value': i} for i in sorted(set(dt[dt['State']==state]['District']))]


@app.callback(output=Output("delta_figure","figure"), inputs=[Input("state","value"),Input("district_value", "value")]) 
def plot_delta_figure(state,district_value):

  ## Check the values and set the defaults   
    if state == None:
        state = 'India'

    # Check if district belongs to that state
    dist_list = dt[dt['State']==state]['District']

    if len(dist_list[dist_list.isin([district_value])]) == 0:
        district_value = []

    if state == 'India' and (district_value == [] or district_value == None):
        cntry_dt_figure=delta_plot(dc['Date'],dc['Delta_Confirmed'],dc['Delta_Recovered'],dc['Delta_Deceased'],'India')
        return cntry_dt_figure
    elif len(state) > 0 and state != 'India' and (district_value == []  or district_value == None):
        state_dates = ds[ds['State']==state]['Date']
        state_dt_confirmed = ds[ds['State']==state]['Delta_Confirmed']
        state_dt_recovered = ds[ds['State']==state]['Delta_Recovered']
        state_dt_deceased  = ds[ds['State']==state]['Delta_Deceased']
        state_dt_figure=delta_plot(state_dates,state_dt_confirmed,state_dt_recovered,state_dt_deceased,state)
        return state_dt_figure
    else:
        district_dates = dd[dd['District']==district_value]['Date']
        district_dt_confirmed = dd[dd['District']==district_value]['Delta_Confirmed']
        district_dt_recovered = dd[dd['District']==district_value]['Delta_Recovered']
        district_dt_deceased  = dd[dd['District']==district_value]['Delta_Deceased']
        district_dt_figure=delta_plot(district_dates,district_dt_confirmed,district_dt_recovered,district_dt_deceased,district_value)
        return district_dt_figure

@app.callback(output=Output("card-panel","children"), inputs=[Input("state","value"),Input("district_value", "value")])
def print_panel(state,district_value):

    ## Check the values and set the defaults 
    if state == None:
        state = 'India'

    # Check if district belongs to that state
    dist_list = dt[dt['State']==state]['District']
    
    if len(dist_list[dist_list.isin([district_value])]) == 0:
        district_value = []

 
    if state == 'India' and (district_value == [] or district_value == None):
        Total_Confirmed = int(ct['Total_Confirmed'])
        Total_Recovered = int(ct['Total_Recovered'])
        Total_Deceased  = int(ct['Total_Deceased'])
        place = state
    elif len(state) > 0 and state != 'India' and (district_value == []  or district_value == None):
        Total_Confirmed = int(st[st['State']==state]['Confirmed'])
        Total_Recovered = int(st[st['State']==state]['Recovered'])
        Total_Deceased  = int(st[st['State']==state]['Deceased'])
        place = state
    else:
        Total_Confirmed = int(dt[dt['District']==district_value]['Confirmed'])
        Total_Recovered = int(dt[dt['District']==district_value]['Recovered'])
        Total_Deceased  = int(dt[dt['District']==district_value]['Deceased'])
        place = district_value

    card = html.Div([
        dbc.Card(
        [
            
            dbc.CardBody(
                [
                    html.H2(place, className="card-title"),
                    html.H6("*{}".format(as_on_date)),
                    html.Hr(),

                    html.H5("TOTAL CASES", style={"color":"#76a8f5"}),
                    html.H4("{:,.0f}".format(Total_Confirmed), style={"color":"#76a8f5"}),
                    html.Hr(),

                    html.H5("TOTAL RECOVERED ", style={"color":"#5df207"}),
                    html.H4("{:,.0f}".format(Total_Recovered), style={"color":"#5df207"}),
                    html.Hr(),

                    html.H5("TOTAL DECEASED ", style={"color":"#ab321f"}),
                    html.H4("{:,.0f}".format(Total_Deceased), style={"color":"#ab321f"}),

                ]
            ),
        ],style={"width": "18rem"},)
    ])
    return card




if __name__ == '__main__':
 app.run_server(debug=True)