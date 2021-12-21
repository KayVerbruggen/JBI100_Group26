import os
from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, MATCH, ALL

from viz_app.main import app
from config import categorical_attribs, quantitive_attribs

def generate_dropdown_label(a):
    return a.replace("_", " ").title() + \
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
        # Basic missing value filtering for any categorical variable

        # When attrib2 is empty, the plot is automatically updated to against the accident index
        if (attrib2 == None):
            return False
            
        df_temp = df.copy()
        df_fatal = df_temp[['accident_severity', attrib1]][df_temp["accident_severity"] == 1].groupby(attrib1).count()[['accident_severity']].reset_index()
        df_fatal["accident_count"] = df_temp.groupby(attrib1).count()["accident_index"]
        df_fatal["fatality_rate"] = df_fatal["accident_severity"] / df_fatal["accident_count"] * 100

        if (attrib2 == "accident_count"):
            df_temp = df_temp.groupby(by=attrib1).count()[["accident_index"]].rename(columns={"accident_index": "accident_count"}).reset_index()
            df_temp["fatality_rate"] = df_fatal["fatality_rate"]
        if (attrib2 == "fatality_rate"):
            df_temp = df_fatal
        
        # Create new plot
        fig = px.scatter(df_temp, x=attrib1, y=attrib2, height=800, color="fatality_rate")
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