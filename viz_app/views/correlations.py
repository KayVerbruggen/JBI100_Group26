from gc import callbacks
import os
from statistics import median
from dash import html
from dash import dcc
import datetime
import plotly.express as px
import pandas as pd
from sklearn.cluster import KMeans
from dash.dependencies import Input, Output, MATCH, ALL

from viz_app.main import app
from config import CATEGORICAL_ATTRIBS, QUANTITATIVE_ATTRIBS, DISCRETE_COL, SEQ_CONT_COL, \
SORT_ORDER_OPTIONS, LIGHT_CONDITIONS, SPECIAL_CONDITIONS_AT_SITE, ROAD_SURFACE_CONDITIONS, \
JUNCTION_CONTROL, JUNCTION_DETAIL


def generate_dropdown_label(a):
    return a.replace("_", " ").title()


def make_correlations_panel():
    return [
            html.Div(
                className="wrapper",
                children=[
                    html.Div([
                        html.Label("X-axis"),
                        dcc.Dropdown(
                            id={
                                'type': "correlations-attrib-x",
                                'index': 0,
                            },
                            options=[{'label': generate_dropdown_label(a), 'value': a} for a in (
                                CATEGORICAL_ATTRIBS + ['time'])],
                            searchable=False,
                        ),
                    ]),
                    html.Div([
                        html.Label("Y-axis"),
                        dcc.Dropdown(
                            id={
                                'type': "correlations-attrib-y",
                                'index': 0,
                            },
                            options=[],
                            searchable=False,
                        ),
                    ]),
                    # A dropdown that allows the user to choose another sequential continuous color palette. 
                    # Sequential and Continuous color palettes only, because the fatality rate is 
                    # sequentially ordered. The color palettes are built-in from Plotly, see
                    # https://plotly.com/python/builtin-colorscales/ 
                    html.Div([
                        html.Label("Color Scale - Sequential"),
                        dcc.Dropdown(
                            id={
                                'type': "correlations-colorscale-seq",
                                'index': 0,
                            },
                            options=[{"value": x, "label": x}
                                for x in SEQ_CONT_COL],
                            value='Reds'
                            ),
                    ]),
                    # A dropdown that allows the user to choose another discrete color palette. 
                    # Discrete colors to distinguish the categorical variables for the
                    # bar chart. 
                    # These color palettes are built-in from Plotly. See 
                    # https://plotly.com/python/discrete-color/

                    html.Div([
                        html.Label("Color Scale - Discrete"),
                        dcc.Dropdown(
                            id={
                                'type': "correlations-colorscale-disc",
                                'index': 0,
                            },
                            options=[{"value": x, "label": x}
                                for x in DISCRETE_COL],
                            value='Pastel1'
                        ),   
                    ]),
                    html.Div([
                        html.Label("Sort"),
                        dcc.Dropdown(
                            id={
                                'type': "correlations-sorting-order",
                                'index': 0,
                            },
                            options=[{"value": x, "label": x}
                                     for x in SORT_ORDER_OPTIONS],
                            value='None'
                        ),
                    ]),
                    html.Div(
                        id='correlations-kmeans-settings', 
                        children = [
                        dcc.Checklist(
                            id={
                                'type': "correlations-kmeans",
                                'index': 0,
                            },
                            options = [{'value':'k_means', 'label':'Enable K-Means Clustering'}],
                            value = [],
                            labelStyle={'display': 'inline-block'},
                        ),
                        html.Label("Number of clusters:"),
                        dcc.Input(
                            id={
                                'type': "correlations-kmeans",
                                'index': 1,
                            },
                            type='number',
                            min=1,
                            value = 5,
                        ),
                    ]),
                ]
            )
        ]

@ app.callback([Output({'type': 'correlations-attrib-y', 'index': 0}, 'options'),
               Output({'type': 'correlations-attrib-y', 'index': 0}, 'value')],
               Input({'type': 'correlations-attrib-x', 'index': ALL}, 'value'))
def show_hide_homepage(attrib):
    possible_attribs = []
    quant_y = ['accident_count', 'fatality_rate']
    if attrib[0] in CATEGORICAL_ATTRIBS:
        possible_attribs = [a for a in CATEGORICAL_ATTRIBS if a != attrib[0]] + quant_y
    elif attrib[0] in QUANTITATIVE_ATTRIBS:
        possible_attribs = quant_y

    return [{'label': generate_dropdown_label(a), 'value': a} for a in possible_attribs], None 

def make_correlations_graphs(df, attrib1, attrib2, corr_color_seq, corr_color_disc, corr_sort_order, k_means, n_clusters):
    # You can use:
    # (attrib1 in categorical_attribs) and
    # (attrib1 in quantitive_attribs)

    # No plotting when an attribute is missing
    if (isinstance(attrib1, type(None)) or isinstance(attrib2, type(None))):
        return False

    df_temp = df.copy()
    # To check the type of attribute.
    if (attrib1 in CATEGORICAL_ATTRIBS and attrib2 in CATEGORICAL_ATTRIBS):
        attributes_to_group = []

        # if chosen attributes are the same, show only one
        if attrib1 == attrib2:
            attributes_to_group.append(attrib1)
        else:
            attributes_to_group.append(attrib1)
            attributes_to_group.append(attrib2)
        # Compute fatality rate of each combination of the two chosen attributes
        df_fatality = (
                    df_temp[df_temp['accident_severity'] == 1].groupby(attributes_to_group).count() / df_temp.groupby(
                attributes_to_group).count()).rename(columns={'accident_severity': 'fatality'})
        # Join df_temp and df_fatality on the chosen features
        final_df = pd.merge(df_temp, df_fatality, on=attributes_to_group)

        # Create parallel categories diagram
        # Add third attribute: fatality rate as color
        fig = px.parallel_categories(final_df, dimensions=attributes_to_group, color='fatality',
                                     color_continuous_scale=corr_color_seq, height=800, labels={attributes_to_group[0]:
                                     attributes_to_group[0].replace("_", " ").title(), attributes_to_group[1]:
                                     attributes_to_group[1].replace("_", " ").title(), 'fatality': 'Fatality Rate(%)'})
        fig.update_layout(
            margin=dict(l=270, r=250, t=20, b=20),
        )
        fig.layout['coloraxis']['colorbar']['x'] = 1.30

        return {
            "children" : [
                html.H5("Parallel Categories Diagram"),
                dcc.Graph(
                    id={
                        'type': "correlations-graph",
                        'index': 0,
                    }, 
                    figure=fig
                )
            ],
            "dataframe" : final_df
        }

    if (attrib1 in QUANTITATIVE_ATTRIBS) != (attrib2 in QUANTITATIVE_ATTRIBS):
        df_fatal = calculate_fatality_rate(df_temp, attrib1).reset_index()
        # depending on the combination of the attributes, filters are applied
        # Only attrib1 is considered, since this one is the only categorical attribute

        # Create new plot
        fig = px.scatter(df_fatal.reset_index() , x=attrib1, y=attrib2, height=800,
            color="fatality_rate", color_continuous_scale=corr_color_seq, labels=
                         {attrib1: attrib1.replace("_", " ").title(), attrib2: attrib2.replace("_", " ").title(),
                          'fatality_rate': 'Fatality Rate(%)'})
        fig = add_sort_order(fig, corr_sort_order)
        fig.update_traces(marker=dict(size=20), selector=dict(mode='markers'))

        # Create the Histogram
        fig2 = px.histogram(df_fatal.reset_index(), x=attrib1, y=attrib2, height=800, color=attrib1,
                    color_discrete_sequence=corr_color_disc,nbins=df[attrib1].unique().size,
                    labels={attrib1: attrib1.replace("_", " ").title(),
                    attrib2: attrib2.replace("_", " ").title()})
        # Configures sorting order type
        fig2 = add_sort_order(fig2, corr_sort_order)

        fig2.update_traces(marker=dict(size=10), selector=dict(mode='markers'))

        return {
            "children" : [
                html.H5("Scatter Plot and Histogram"),
                html.H6("{}(x) vs {}(y)".format(attrib1.replace("_", " ").title(), attrib2.replace("_", " ").title())),
                dcc.Graph(
                    id={
                        'type': "correlations-graph",
                        'index': 0,
                    }, 
                    figure=fig
                ),
                dcc.Graph(
                    id={
                        'type': "correlations-graph",
                        'index': 1,
                    }, 
                    figure=fig2
                )
            ],
            "dataframe" : df_fatal
        }

    if (attrib1 in QUANTITATIVE_ATTRIBS and attrib2 in QUANTITATIVE_ATTRIBS):
        df_fatal = calculate_fatality_rate(df_temp, attrib1)
        df_to_use = df_fatal
        color = "fatality_rate"
        colormap=corr_color_seq

        # If we are using k_means, do the clustering using scikit-learn.
        if 'k_means' in k_means:
            # Use a discrete colormap for the coloring of different clusters.
            colormap=corr_color_disc

            df_kmeans = df_to_use[[attrib2]].reset_index().copy()

            # We need time to be numerical, so we convert from HH:MM -> minutes passed
            df_kmeans['time'] = [int(x[0:2])*60 + int(x[3:5]) for x in df_kmeans['time']]
            
            kmeans = KMeans(n_clusters=n_clusters).fit(df_kmeans)

            color = kmeans.labels_
            
            # Convert back to HH:MM so we can plot it
            centroid_time = [min_to_time(x) for x in kmeans.cluster_centers_[:,0]]

            fig2 = px.scatter(x=centroid_time, y=kmeans.cluster_centers_[:,1],
                        color=range(0, n_clusters), color_continuous_scale=corr_color_disc,
                                    color_discrete_sequence=corr_color_disc)
            fig2.update_traces(marker=dict(size=20, symbol='x', opacity=1.0), selector=dict(mode='markers'))

        # Create new plot
        fig = px.scatter(df_fatal.reset_index(), x=attrib1, y=attrib2, height=800,
                        color=color, color_continuous_scale=colormap, labels={attrib1: attrib1.replace("_", " ").title(),
                                        attrib2: attrib2.replace("_", " ").title(), 'fatality_rate': 'Fatality Rate(%)'})

        fig = add_sort_order(fig, corr_sort_order)
        fig.update_traces(marker=dict(size=10), selector=dict(mode='markers'))

        # If we have k_means enabled: 
        #   - add the additional markers 
        #   - lower the opacity of the normal markers
        if 'k_means' in k_means:
            fig.update_traces(marker=dict(opacity=0.3), selector=dict(mode='markers'))
            fig.add_trace(fig2.data[0])
            fig.update_coloraxes(showscale=False)

        return  {
            "children" : [
                html.H5("Scatter Plot"),
                html.H6("{}(x) vs {}(y)".format(attrib1.replace("_", " ").title(), attrib2.replace("_", " ").title())),
                dcc.Graph(
                    id={
                        'type': "correlations-graph",
                        'index': 0,
                    }, 
                    figure=fig
                ),
            ],
            "dataframe" : df_to_use
        }

    return  {
            "children" : [],
            "dataframe" : []
        }

# Convert the number of minutes that have passed in a day to HH:MM
def min_to_time(mins):
    hours = int(mins/60)
    remainder_mins = int(mins%60)
    hours_string = str(hours)
    mins_string = str(remainder_mins)
    if hours < 10:
        hours_string = '0' + hours_string
    if remainder_mins < 10:
        mins_string = '0' + mins_string

    return hours_string + ':' + mins_string

# Helper function to set sorting order on graph
def add_sort_order(fig, req_order):
    if req_order == SORT_ORDER_OPTIONS[1]:
        fig.update_xaxes(categoryorder="total ascending")
    elif req_order == SORT_ORDER_OPTIONS[2]:
        fig.update_xaxes(categoryorder="total descending")
    elif req_order == SORT_ORDER_OPTIONS[0]:
        fig.update_xaxes(categoryorder="category ascending")
    return fig

# Helper function to add fatality rate attribute to df
def calculate_fatality_rate(df_temp, attrib1):
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

@ app.callback(Output('correlations-kmeans-settings', 'style'),
    Input({'type': 'correlations-attrib-x', 'index': ALL}, 'value'),
    Input({'type': 'correlations-attrib-y', 'index': ALL}, 'value'))
def show_hide_homepage(attrib_x, attrib_y):
    if attrib_x[0] in QUANTITATIVE_ATTRIBS and attrib_y[0] in QUANTITATIVE_ATTRIBS:
        return {'display': 'block'}
    
    return {'display': 'none'}

@app.callback(Output("indicator", "children"),
              Input('attrib2-slider', 'value'))
def display_value(value):
    return 'Linear Value: {}'.format(value)


# Method to generate list of time intervals for grouping accidents
def generate_list_intervals(interval_size):
    time_intervals = []
    start = "00:00"
    end = "23:59"
    delta = datetime.timedelta(minutes=interval_size)
    start = datetime.datetime.strptime(start, '%H:%M')
    end = datetime.datetime.strptime(end, '%H:%M')
    t = start
    while t <= end:
        time_intervals.append(int(datetime.datetime.strftime(t, '%H%M')))
        t += delta
    return time_intervals

# Auxillary method for finding the closest time interval for an accident
def find_closest_interval(row, intervals):
    abs_diff = lambda interval: abs(interval - row["time_index"])
    closest_interval = min(intervals, key=abs_diff)
    return closest_interval


