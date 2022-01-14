import os
from dash import html
from dash import dcc
import datetime
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, MATCH, ALL

from viz_app.main import app
from config import categorical_attribs, quantitive_attribs, discrete_col, seq_cont_col
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
        html.Label("Color Scale - Sequential"),
        dcc.Dropdown(
            id={
                'type': "correlations-colorscale-seq",
                'index': 0,
            },
            options=[{"value": x, "label": x} 
                 for x in seq_cont_col],
            value='Reds'
            ),
        html.Label("Color Scale - Discrete"),
        dcc.Dropdown(
            id={
                'type': "correlations-colorscale-disc",
                'index': 0,
            },
            options=[{"value": x, "label": x} 
                 for x in discrete_col],
            value='Pastel1'
        ),   
    ]

def make_correlations_graphs(df, graph_type, attrib1, attrib2, corr_color_seq, corr_color_disc):
    # You can use: 
    # (attrib1 in categorical_attribs) and 
    # (attrib1 in quantitive_attribs)

    # No plotting when an attribute is missing
    if (isinstance(attrib1, type(None)) or isinstance(attrib2, type(None))):
        return False

    df_temp = df.copy()

    # To check the type of attribute.
    if graph_type == 'parallel':   
        attributes_to_group = []
       
        # if chosen attributes are the same, show only one
        if attrib1 == attrib2:
            attributes_to_group.append(attrib1)
        else:
            attributes_to_group.append(attrib1)
            attributes_to_group.append(attrib2)
        # Compute fatality rate of each combination of the two chosen attributes
        df_fatality = (df_temp[df_temp['accident_severity'] == 1].groupby(attributes_to_group).count() / df_temp.groupby(attributes_to_group).count()).rename(columns={'accident_severity': 'fatality'})
        # Join df_temp and df_fatality on the chosen features
        final_df = pd.merge(df_temp, df_fatality, on=attributes_to_group)

        # Create parallel categories diagram
        fig = px.parallel_categories(final_df, dimensions=attributes_to_group, color='fatality', color_continuous_scale=corr_color_seq, height=800)
        fig.update_layout(
        margin=dict(l=270, r=250, t=20, b=20),
        )
        fig.layout['coloraxis']['colorbar']['x'] = 1.30
        return [
            html.H5("Parallel Categories Diagram"),
            dcc.Graph(figure=fig)
        ]
    
    if graph_type == 'scatter':

        df_fatal = calculate_fatality_rate(df_temp, attrib1)

        # Create new plot
        fig = px.scatter(df_fatal.reset_index() , x=attrib1, y=attrib2, height=800,
            color="fatality_rate", color_continuous_scale=corr_color_seq)
        fig.update_traces(marker=dict(size=10), selector=dict(mode='markers'))
        return [
            html.H5("Scatter Plot"),
            html.H6(attrib1 + " " + attrib2),
            dcc.Graph(figure=fig)
        ]
    
    if graph_type == 'histogram':

        df_fatal = calculate_fatality_rate(df_temp, attrib1)
        # Create the Histogram
        fig = px.histogram(df_fatal.reset_index(), x=attrib1, y=attrib2, height=800,
                         color="fatality_rate" ,nbins=df[attrib1].unique().size, color_discrete_sequence=corr_color_disc)
        fig.update_traces(marker=dict(size=10), selector=dict(mode='markers'))
        return [
            html.H5("Histogram"),
            html.H6(attrib1 + " " + attrib2),
            dcc.Graph(figure=fig)
        ]

    return []

def calculate_fatality_rate(df_temp,attrib1):

    # Compute the number of fatal accidents in each category
    df_fatal = df_temp[['accident_severity', attrib1]][df_temp["accident_severity"] == 1].groupby(attrib1).count()[
        ['accident_severity']]
    # Rename column
    df_fatal.rename(columns={"accident_severity": "fatal_accident_count"}, inplace=True)
    # Compute total number of accidents in each category
    df_fatal["accident_count"] = df_temp.groupby(attrib1).count()["accident_index"]
    # Compute fatality rate of accidents in each category,
    # later used in color scale
    df_fatal["fatality_rate"] = round(df_fatal["fatal_accident_count"] / df_fatal["accident_count"] * 100, 2)

    return df_fatal

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

# Method to generate list of time intervals for grouping accidents
def generate_list_intervals(interval_size):
    time_intervals = []
    start = "00:00"
    end = "23:59"
    delta = datetime.timedelta(minutes=interval_size)
    start = datetime.datetime.strptime(start, '%H:%M')
    end = datetime.datetime.strptime(end, '%H:%M' )
    t = start
    while t <= end :
        time_intervals.append(int(datetime.datetime.strftime(t, '%H%M')))
        t += delta
    return time_intervals

# Auxillary method for finding the closest time interval for an accident
def find_closest_interval(row, intervals):
    abs_diff = lambda interval: abs(interval - row["time_index"])
    closest_interval = min(intervals, key=abs_diff)
    return closest_interval

