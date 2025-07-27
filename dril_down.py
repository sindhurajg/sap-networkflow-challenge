"""
To enable drill-down filtering by subscription, resource group, NSG, protocol, and time window.
"""

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import re
#from parser import load_and_merge_zipped_csvs

# Load NSG flow logs
df = pd.read_csv(r"C:\Users\Admin\Documents\NSG_Flow_Logs_1.csv")  # adjust date col
# folder = r"C:\Users\Admin\Downloads\NSG_Flow_Logs_files"
# df = load_and_merge_zipped_csvs(folder)
# print(f"Total records loaded: {len(df)}")
# print(df.head())

app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H2("NSG Flow Log Drill-Down Dashboard"),

    dcc.Dropdown(
        id='subscription-dropdown',
        options=[{'label': sub, 'value': sub} for sub in df['subscription'].dropna().unique()],
        placeholder='Select Subscription'
    ),

    dcc.Dropdown(id='resource-group-dropdown',
                 options=[{'label': p, 'value': p} for p in df['resource_group'].dropna().unique()],
                 placeholder='Select Resource Group'),
    dcc.Dropdown(id='nsg-dropdown', 
                 options=[{'label': p, 'value': p} for p in df['network_security_group'].dropna().unique()],
                 placeholder='Select NSG'),

    dcc.Dropdown(
        id='protocol-dropdown',
        options=[{'label': p, 'value': p} for p in df['ft_protocol'].dropna().unique()],
        placeholder='Select Protocol'
    ),

    dcc.DatePickerRange(
        id='date-range',
        start_date=df['ft_time'].min(),
        end_date=df['ft_time'].max()
    ),

    html.Br(),
    html.Div(id='filtered-results')
])

# Callbacks for Dropdown Chaining
@app.callback(
    Output('resource-group-dropdown', 'options'),
    Input('subscription-dropdown', 'value')
)
def update_resource_groups(subscription):
    if not subscription:
        return []
    filtered = df[df['subscription'] == subscription]
    return [{'label': rg, 'value': rg} for rg in filtered['resource_group'].dropna().unique()]

@app.callback(
    Output('nsg-dropdown', 'options'),
    [Input('subscription-dropdown', 'value'),
     Input('resource-group-dropdown', 'value')]
)
def update_nsgs(subscription, rg):
    if not (subscription and rg):
        return []
    filtered = df[(df['subscription'] == subscription) & (df['resource_group'] == rg)]
    return [{'label': nsg, 'value': nsg} for nsg in filtered['network_security_group'].dropna().unique()]

# Final Callback for Filtering and Charting
@app.callback(
    Output('filtered-results', 'children'),
    [Input('subscription-dropdown', 'value'),
     Input('resource-group-dropdown', 'value'),
     Input('nsg-dropdown', 'value'),
     Input('protocol-dropdown', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def filter_data(subscription, rg, nsg, protocol, start_date, end_date):
    dff = df.copy()
    if subscription:
        dff = dff[dff['subscription'] == subscription]
    if rg:
        dff = dff[dff['resource_group'] == rg]
    if nsg:
        dff = dff[dff['network_security_group'] == nsg]
    if protocol:
        dff = dff[dff['ft_protocol'] == protocol]
    if start_date and end_date:
        dff = dff[(dff['ft_time'] >= start_date) & (dff['ft_time'] <= end_date)]

    if dff.empty:
        return html.Div("⚠️ No records match the selected filters.")

    # Example chart: Number of flows over time
    fig = px.histogram(dff, x='ft_time', color='ft_protocol', nbins=50, title="Filtered NSG Flows Over Time")
    return dcc.Graph(figure=fig)


if __name__ == "__main__":
    app.run(debug=True)

