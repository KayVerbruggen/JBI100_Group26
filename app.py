import os
import dash
from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, MATCH, ALL

from viz_app.main import app
from viz_app.views.map import make_map_panel, make_map_graphs
from viz_app.views.distributions import make_distributions_panel, make_distributions_graphs
from viz_app.views.correlations import make_correlations_panel, make_correlations_graphs
from viz_app.views.trends import make_trends_panel, make_trends_graphs
import config

app.layout = html.Div([
    html.Div(
        className="topnav",
        children=[
            dcc.Link('Home', href='/'),
            dcc.Link('Map', href='/map'),
            dcc.Link('Correlations', href='/correlations'),
            dcc.Link('Trends', href='/trends'),
            dcc.Link('Distributions', href='/distributions'),
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
    elif pathname == '/distributions':
        return make_distributions_panel()
    else:
        return []
    # You could also return a 404 "URL not found" page here

# Changing the left panel based on the url
@ app.callback(dash.dependencies.Output('graph-content', 'children'),
               [Input('url', 'pathname'),
                Input('dataset-year', 'value'),
                
                # Map Options
                Input({'type': 'map-attrib', 'index': ALL}, 'value'),

                # Correlations Options
                Input({'type': 'correlations-graph-type', 'index': ALL}, 'value'),
                Input({'type': 'correlations-attrib', 'index': ALL}, 'value'),

                # Trends Options
                Input({'type': 'trends-attrib', 'index': ALL}, 'value'),

                # Distributions Options
                Input({'type': 'distributions-attrib', 'index': ALL}, 'value'),
                ])
def display_graphs(pathname, year, map_attribs, corr_type, corr_attribs, 
                    trends_attribs, dist_attribs):
    df = pd.read_csv(
        os.getcwd() + "/datasets/road_safety_" + str(year) + ".csv")

    if pathname == '/map':
        return make_map_graphs(df, map_attribs[0])
    elif pathname == '/correlations':
        return make_correlations_graphs(df, corr_type[0], corr_attribs[0], corr_attribs[1])
    elif pathname == '/trends':
        return make_trends_graphs(df, trends_attribs[0], trends_attribs[1])
    elif pathname == '/distributions':
        return make_distributions_graphs(df, dist_attribs[0], dist_attribs[1])
    else:
        return []
    # You could also return a 404 "URL not found" page here

if __name__ == '__main__':
    app.run_server(debug=True)