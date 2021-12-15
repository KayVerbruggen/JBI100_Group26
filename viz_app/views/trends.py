from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd


def make_trends_graphs():
    return [
        html.H5("Trend Graphs")
    ]


def make_trends_panel():
    return [
        html.Label("Trends option 1"),
        dcc.Dropdown(
            id="trends-option-1",
            options=[],
        ),
    ]
