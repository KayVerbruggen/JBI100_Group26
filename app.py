import os
from _plotly_utils.colors import get_colorscale
import dash
from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd
import datetime
from dash.dependencies import Input, Output, MATCH, ALL

from viz_app.main import app
from viz_app.views.map import make_map_panel, make_map_graphs
from viz_app.views.correlations import make_correlations_panel, make_correlations_graphs
from viz_app.views.trends import make_trends_panel, make_trends_graphs
import config
from config import ID_TO_LIGHT_CONDITIONS, ID_TO_JUNCTION_DETAIL, ID_TO_SPECIAL_CONDITIONS_AT_SITE, \
                   MISSING_VALUE_TABLE, ID_TO_JUNCTION_CONTROL, ID_TO_ROAD_SURFACE_CONDITIONS, ID_TO_SPECIAL_CONDITIONS_AT_SITE, discrete_col, seq_cont_col

# This function joins the module and built-in palette name (discrete), e.g. px.colors.qualitative.Reds
def get_disc_color(c):
    return getattr(px.colors.qualitative, c)

# This function joins the module and built-in palette name (sequential), e.g. px.colors.qualitative.Reds
def get_seq_cont_color(c):
    return getattr(px.colors.sequential, c)

app.layout = html.Div([
    html.Div(
        className="topnav",
        children=[
            dcc.Link('Home', href='/'),
            dcc.Link('Map', href='/map'),
            dcc.Link('Correlations', href='/correlations'),
            dcc.Link('Trends', href='/trends'),
        ]
    ),
    dcc.Location(id='url', refresh=False),
    html.Div(
        id="leftColumn",
        className="three columns",
        children=[
            html.H5("Visualization Settings"),
            html.Label("Dataset Year"),
            dcc.Dropdown(
                id="dataset-year",
                options=[{"label": i, "value": i} for i in range(1979, 2021)],
                value=2020,
                searchable=False,
            ),
            html.Div(id='panel-content', className="control_card",
                     children=make_correlations_panel(),
                     style={"textAlign": "float-left"}
                     ),                       
        ]
    ),
    html.Div(
        id="rightColumn",
        className="nine columns",
        children=[
            html.Div(id='graph-content',),
        ]
    ),
])


# Changing the left panel based on the url
@ app.callback(dash.dependencies.Output('panel-content', 'children'),
               [dash.dependencies.Input('url', 'pathname')])
def display_options(pathname):
    if pathname == '/map':
        return make_map_panel()
    elif pathname == '/correlations':
        return make_correlations_panel()
    elif pathname == '/trends':
        return make_trends_panel()
    else:
        return []
    # You could also return a 404 "URL not found" page here

# Changing the right panel based on the url
@ app.callback(dash.dependencies.Output('graph-content', 'children'),
               [Input('url', 'pathname'),
                Input('dataset-year', 'value'),
                
                # Map Options
                Input({'type': 'map-attrib', 'index': ALL}, 'value'),
                Input({'type': 'map-colorscale-seq', 'index': ALL}, 'value'),

                # Correlations Options
                Input({'type': 'correlations-graph-type', 'index': ALL}, 'value'),
                Input({'type': 'correlations-attrib', 'index': ALL}, 'value'),
                Input({'type': 'correlations-colorscale-seq', 'index': ALL}, 'value'),
                Input({'type': 'correlations-colorscale-disc', 'index': ALL}, 'value'),

                # Trends Options
                Input({'type': 'trends-attrib', 'index': ALL}, 'value'),
                Input({'type': 'trends-colorscale-disc', 'index': ALL}, 'value'),
                ])
                
def display_graphs(pathname, year, map_attribs, map_color_seq, corr_type, corr_attribs, 
                    corr_color_seq, corr_color_disc, trends_attribs, trends_color_disc):
    df = pd.read_csv(
        os.getcwd() + "/datasets/road_safety_" + str(year) + ".csv")
    df_valid = remove_missing_value(df)
    df = id_to_value(df_valid)
    if pathname == '/map':
        return make_map_graphs(df, map_attribs[0], get_seq_cont_color(map_color_seq[0]))
    elif pathname == '/correlations':
        return make_correlations_graphs(df, corr_type[0], corr_attribs[0], corr_attribs[1], get_seq_cont_color(corr_color_seq[0]), get_disc_color(corr_color_disc[0]))
    elif pathname == '/trends':
        return make_trends_graphs(df, trends_attribs[0], trends_attribs[1], get_disc_color(trends_color_disc[0]))
    else:
        return []
    # You could also return a 404 "URL not found" page here

# Remove rows with missing values for every target attribute
def remove_missing_value(df):
    columns = MISSING_VALUE_TABLE.keys()
    df_processed = df.copy()
    for attribute in columns:
        for missing_value in MISSING_VALUE_TABLE[attribute]:
            df_processed = df_processed[df_processed[attribute] != missing_value]
    return df_processed

# Map IDS to the corresponding value
def id_to_value(df):
    df_mapped = df.copy()
    return df_mapped.replace({'light_conditions': ID_TO_LIGHT_CONDITIONS, 'junction_detail' : ID_TO_JUNCTION_DETAIL, \
    'junction_control' : ID_TO_JUNCTION_CONTROL, 'road_surface_conditions' : ID_TO_ROAD_SURFACE_CONDITIONS, \
    'special_conditions_at_site' : ID_TO_SPECIAL_CONDITIONS_AT_SITE})

# Method to generate list of time intervals for grouping accidents
def generate_list_intervals(interval_size):
    time_intervals = []
    start = "00:00"
    end = "23:59"
    delta = datetime.timedelta(minutes=interval_size)
    start = datetime.datetime.strptime(start, '%H:%M')
    end = datetime.datetime.strptime(end, '%H:%M' )
    t = start
    while t <= end :
        time_intervals.append(int(datetime.datetime.strftime(t, '%H%M')))
        t += delta
    return time_intervals

# Auxillary method for finding the closest time interval for an accident
def find_closest_interval(row, intervals):
    abs_diff = lambda interval: abs(interval - row["time_index"])
    closest_interval = min(intervals, key=abs_diff)
    return closest_interval


if __name__ == '__main__':
    app.run_server(debug=True)