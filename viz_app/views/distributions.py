from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd
from config import categorical_attribs, quantitive_attribs

def make_distributions_panel():
    return [
        html.Label("Categorical Attribute"),
        dcc.Dropdown(
            id={
                'type': "distributions-attrib",
                'index': 0,
            },
            options=[{'label': a, 'value': a} for a in categorical_attribs],
        ),
        html.Label("Quantative Attribute"),
        dcc.Dropdown(
            id={
                'type': "distributions-attrib",
                'index': 1,
            },
            options=[{'label': a, 'value': a} for a in quantitive_attribs],
        ),
    ]

def make_distributions_graphs(df, cat_attrib, quant_attrib):
    return [
        html.H5("Distribution Graphs")
    ]