from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd

from config import categorical_attribs, quantitive_attribs

def make_map_panel():
    return [
        html.Label("Attribute"),
        dcc.Dropdown(
            id={
                'type': "map-attrib",
                'index': 0,
            },
            options=[{'label': a, 'value': a} for a in quantitive_attribs],
        ),
    ]

def make_map_graphs(df, attrib):
    return [
        html.H5("Map Graph")
    ]