import os
import dash
from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd

from viz_app.views.map import make_map_graphs, make_map_panel
from viz_app.views.distributions import make_distributions_graphs, make_distributions_panel
from viz_app.views.correlations import make_correlations_graphs, make_correlations_panel
from viz_app.views.trends import make_trends_graphs, make_trends_panel

app = dash.Dash(__name__)

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
            html.Label("General option 1"),
            dcc.Dropdown(
                id="general-option-1",
                options=[],
            ),
            html.Div(id='panel-content', className="control_card",
                     style={"textAlign": "float-left"}
                     ),
        ]
    ),
    html.Div(
        id="rightColumn",
        className="nine columns",
        children=[
            html.Div(id='graph-content'),
        ]
    ),
])

home_layout = []


@ app.callback(dash.dependencies.Output('graph-content', 'children'),
               [dash.dependencies.Input('url', 'pathname')])
def display_graph(pathname):
    if pathname == '/map':
        return make_map_graphs()
    elif pathname == '/correlations':
        return make_correlations_graphs()
    elif pathname == '/trends':
        return make_trends_graphs()
    elif pathname == '/distributions':
        return make_distributions_graphs()
    else:
        return home_layout
    # You could also return a 404 "URL not found" page here


@ app.callback(dash.dependencies.Output('panel-content', 'children'),
               [dash.dependencies.Input('url', 'pathname')])
def display_graph(pathname):
    if pathname == '/map':
        return make_map_panel()
    elif pathname == '/correlations':
        return make_correlations_panel()
    elif pathname == '/trends':
        return make_trends_panel()
    elif pathname == '/distributions':
        return make_distributions_panel()
    else:
        return home_layout
    # You could also return a 404 "URL not found" page here
