import dash
from dash import dcc, html, dash_table, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
#from parser import load_and_merge_zipped_csvs

# Load your CSV file
df = pd.read_csv(r"C:\Users\Admin\Documents\NSG_Flow_Logs_1.csv")
# folder = r"C:\Users\Admin\Downloads\NSG_Flow_Logs_files"
# df = load_and_merge_zipped_csvs(folder)
# print(f"Total records loaded: {len(df)}")
# print(df.head())

# Preprocess data
df['timestamp'] = pd.to_datetime(df['ft_time'])
df['hour'] = df['timestamp'].dt.floor('h')
df['pair'] = df['ft_src_ip'] + " → " + df['ft_dest_ip']

# Geo fields
df['src_country'] = df['ft_src_ip_geo'].apply(lambda x: json.loads(x)['country'] if pd.notna(x) else None)
df['src_lat'] = df['ft_src_ip_geo'].apply(lambda x: float(json.loads(x)['latitude']) if pd.notna(x) else None)
df['src_lon'] = df['ft_src_ip_geo'].apply(lambda x: float(json.loads(x)['longitude']) if pd.notna(x) else None)

# Summary stats
total_flows = len(df)
percent_denied = round((df['ft_decision'] == 'Denied').sum() / total_flows * 100, 2)

# App
app = dash.Dash(__name__)
app.title = "NSG Flow Log Explorer"

app.layout = html.Div([
    html.H1("🔍 NSG Flow Log Dashboard"),
    html.Div([
        html.Div([
            html.H4("Filter by Decision"),
            dcc.Dropdown(
                id='decision-filter',
                options=[{"label": d, "value": d} for d in df['ft_decision'].unique()],
                multi=True,
                value=[]
            ),
        ], style={'width': '30%', 'display': 'inline-block'}),

        html.Div([
            html.H4("Summary"),
            html.Div([
                html.Div(f"Total Flows: {total_flows}", style={'margin': '4px'}),
                html.Div(f"% Denied: {percent_denied}%", style={'margin': '4px'}),
            ])
        ], style={'width': '65%', 'display': 'inline-block', 'paddingLeft': '30px'})
    ]),

    dcc.Graph(id="top-src-bar"),
    dcc.Graph(id="top-dest-bar"),
    dcc.Graph(id="denied-pie"),
    dcc.Graph(id="flows-per-hour-line"),
    dcc.Graph(id="traffic-heatmap"),
    dcc.Graph(id="geo-map"),
    dcc.Graph(id="sankey"),
    html.H3("Top Talkers and Listeners"),
    dash_table.DataTable(
        id='talkers-table',
        columns=[{"name": i, "id": i} for i in ['ft_src_ip', 'ft_dest_ip', 'ft_packets_sent', 'ft_packets_received']],
        page_size=10,
        style_table={'overflowX': 'auto'},
    )
])

@app.callback(
    [
        Output("top-src-bar", "figure"),
        Output("top-dest-bar", "figure"),
        Output("denied-pie", "figure"),
        Output("flows-per-hour-line", "figure"),
        Output("traffic-heatmap", "figure"),
        Output("geo-map", "figure"),
        Output("sankey", "figure"),
        Output("talkers-table", "data")
    ],
    Input("decision-filter", "value")
)
def update_graphs(decisions):
    dff = df if not decisions else df[df['ft_decision'].isin(decisions)]

    top_src = dff['ft_src_ip'].value_counts().nlargest(10)
    top_dest = dff['ft_dest_ip'].value_counts().nlargest(10)
    top_denied = dff[dff['ft_decision'] == "Denied"]['ft_src_ip'].value_counts().nlargest(10)

    flows_hour = dff.groupby('hour').size().reset_index(name='flows')
    heatmap_data = dff.copy()
    heatmap_data['hour'] = heatmap_data['timestamp'].dt.hour
    heatmap_data['day'] = heatmap_data['timestamp'].dt.day_name()
    heatmap = heatmap_data.groupby(['day', 'hour']).size().reset_index(name='count')
    heatmap_pivot = heatmap.pivot(index='day', columns='hour', values='count').fillna(0)

    # Geo map
    geo_map = px.scatter_geo(dff.dropna(subset=['src_lat', 'src_lon']),
                             lat='src_lat', lon='src_lon',
                             color='ft_decision',
                             hover_name='ft_src_ip',
                             title="Source IP Geolocation Map")

    # Sankey
    sankey_df = dff.groupby(['ft_src_ip', 'ft_dest_ip']).size().reset_index(name='count')
    nodes = list(set(sankey_df['ft_src_ip']) | set(sankey_df['ft_dest_ip']))
    node_dict = {node: i for i, node in enumerate(nodes)}
    sankey_fig = go.Figure(go.Sankey(
        node=dict(label=nodes),
        link=dict(
            source=[node_dict[src] for src in sankey_df['ft_src_ip']],
            target=[node_dict[dst] for dst in sankey_df['ft_dest_ip']],
            value=sankey_df['count']
        )
    ))
    sankey_fig.update_layout(title_text="Conversation Flow (Sankey Diagram)", font_size=10)

    return (
        px.bar(x=top_src.index, y=top_src.values, title="Top 10 Source IPs"),
        px.bar(x=top_dest.index, y=top_dest.values, title="Top 10 Destination IPs"),
        px.pie(values=top_denied.values, names=top_denied.index, title="Top 10 Denied Flows"),
        px.line(flows_hour, x='hour', y='flows', title="Flows per Hour"),
        px.imshow(heatmap_pivot.values, labels=dict(x="Hour", y="Day", color="Count"),
                  x=heatmap_pivot.columns, y=heatmap_pivot.index,
                  title="Hourly Traffic Heatmap"),
        geo_map,
        sankey_fig,
        dff[['ft_src_ip', 'ft_dest_ip', 'ft_packets_sent', 'ft_packets_received']].head(10).to_dict('records')
    )

if __name__ == '__main__':
    app.run(debug=True)
