from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd

from config import categorical_attribs, quantitive_attribs

def make_trends_graphs(df, otherYear, attrib):
    return [
        html.H5("Trend Graphs")
    ]


def make_trends_panel():
    return [
        html.Label("Other Year"),
        dcc.Dropdown(
            id={
                'type': "trends-attrib",
                'index': 0,
            },
            options=[],
        ),
        html.Label("Attribute"),
        dcc.Dropdown(
            id={
                'type': "trends-attrib",
                'index': 1,
            },
            options=[{'label': a, 'value': a} for a in quantitive_attribs],
        ),
    ]
