from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd


def make_distributions_graphs():
    return [
        html.H5("Distribution Graphs")
    ]


def make_distributions_panel():
    return [
        html.Label("Distributions option 1"),
        dcc.Dropdown(
            id="distributions-option-1",
            options=[],
        ),
    ]
