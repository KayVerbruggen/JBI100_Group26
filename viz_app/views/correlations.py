from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd


def make_correlations_graphs():
    return [
        html.H5("Correlation Graphs")
    ]


def make_correlations_panel():
    return [
        html.Label("Correlations option 1"),
        dcc.Dropdown(
            id="correlations-option-1",
            options=[],
        ),
    ]
