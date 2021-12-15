from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd


def make_map_graphs():
    return [
        html.H5("Map Graphs")
    ]


def make_map_panel():
    return [
        html.Label("Map option 1"),
        dcc.Dropdown(
            id="map-option-1",
            options=[],
        ),
    ]
