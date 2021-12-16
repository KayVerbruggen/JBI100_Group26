import os
from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, MATCH, ALL

from viz_app.main import app
from config import categorical_attribs, quantitive_attribs

def generate_dropdown_label(a):
    return a.replace("_", " ") + \
        (' (Categorical)' if a in categorical_attribs else ' (Quantative)')

def make_correlations_panel():
    return [
        html.Label("Attribute 1"),
        dcc.Dropdown(
            id={
                'type': "correlations-attrib",
                'index': 0,
            },
            options=[{'label': generate_dropdown_label(a), 'value': a} for a in (
                categorical_attribs + quantitive_attribs)],
            searchable=False,
        ),
        html.Label("Attribute 2"),
        dcc.Dropdown(
            id={
                'type': "correlations-attrib",
                'index': 1,
            },
            options=[{'label':  generate_dropdown_label(a), 
                    'value': a} for a in (
                categorical_attribs + quantitive_attribs)],
            searchable=False,
        ),
        html.Label("Graph Type"),
        dcc.Dropdown(
            id={'type': 'correlations-graph-type', 'index': 0}
        ),
    ]

def make_correlations_graphs(df, type, attrib1, attrib2):
    # You can use: 
    # (attrib1 in categorical_attribs) and 
    # (attrib1 in quantitive_attribs)
    # To check the type of attribute.

    if type == 'parallel':
        return [
            html.H5("Parallel Category Diagram"),
            # html.H6(attrib1 + " " + attrib2),
            #dcc.Graph(figure=fig)
        ]
    
    if type == 'scatter':
        # Just a random hard coded example that I still had to test everything.
        df_junction = df[(df['junction_detail'] != -1) &
                     (df['junction_detail'] != 99)].copy()
        casualties_by_junction = df_junction[[
        'number_of_casualties', 'junction_detail']].groupby('junction_detail').sum()
        casualties_by_junction['fatality'] = df_junction[['accident_severity', 'junction_detail']
                                                     ][df_junction.accident_severity == 1].groupby('junction_detail').count()['accident_severity']
        casualties_by_junction['fatality'] = casualties_by_junction['fatality'] / \
        casualties_by_junction['number_of_casualties'] * 100
        fig = px.scatter(casualties_by_junction, 
            x='number_of_casualties', y='fatality', 
            color=casualties_by_junction.index, height=800)
        fig.update_traces(marker=dict(size=50,
                                           line=dict(width=2,
                                                     color='DarkSlateGrey')),
                               selector=dict(mode='markers'))
        return [
            html.H5("Scatter Plot"),
            #html.H6(attrib1 + " " + attrib2),
            dcc.Graph(figure=fig)
        ]
    
    if type == 'histogram':
        return [
            html.H5("Histogram"),
            # html.H6(attrib1 + " " + attrib2),
            # dcc.Graph(...)
        ]

    return []

# Changing the correlations panel
@app.callback([Output({'type': 'correlations-graph-type', 'index': 0}, 'options'),
               Output({'type': 'correlations-graph-type', 'index': 0}, 'value')],
              [Input({'type': 'correlations-attrib', 'index': ALL}, 'value')])
def correlation_graph_options(attribs):
    attrib1, attrib2 = attribs[0], attribs[1]
    # Both categorical
    if (attrib1 in categorical_attribs and attrib2 in categorical_attribs):
        return [{'label': 'Parallel category diagram', 'value': 'parallel'}], 'parallel'

    # Both quantitive
    if (attrib1 in quantitive_attribs and attrib2 in quantitive_attribs):
        return [{'label': 'Scatter plot', 'value': 'scatter'}], 'scatter'

    # One of each
    if (attrib1 in quantitive_attribs) != (attrib2 in quantitive_attribs):
        return [
            {'label': 'Scatter plot', 'value': 'scatter'},
            {'label': 'Histogram', 'value': 'histogram'}
        ], 'scatter'

    return [], ''