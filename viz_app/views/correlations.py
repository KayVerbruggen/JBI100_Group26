import os
from statistics import median
from dash import html
from dash import dcc
import datetime
import plotly.express as px
import pandas as pd
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
                                'type': "correlations-attrib",
                                'index': 0,
                            },
                            options=[{'label': generate_dropdown_label(a), 'value': a} for a in (
                                CATEGORICAL_ATTRIBS + QUANTITATIVE_ATTRIBS)],
                            searchable=False,
                        ),
                    ]),
                    html.Div([
                        html.Label("X-axis filter"),
                        dcc.Dropdown(
                            id={
                                'type': "correlations-attrib-filter",
                                'index': 0,
                            },
                            multi=True
                        ),
                    ]),
                    html.Div([
                        html.Label("Y-axis"),
                        dcc.Dropdown(
                            id={
                                'type': "correlations-attrib",
                                'index': 1,
                            },
                            options=[{'label':  generate_dropdown_label(a), 
                                    'value': a} for a in (
                                CATEGORICAL_ATTRIBS + QUANTITATIVE_ATTRIBS)],
                            searchable=False,
                        ),
                    ]),
                    html.Div([
                        html.Label("Y-axis filter"),
                        dcc.Dropdown(
                            id={
                                'type': "correlations-attrib-filter",
                                'index': 1,
                            },
                            multi=True
                        ),
                    ]),
                    html.Div([
                            html.Label("Graph Type"),
                            dcc.Dropdown(
                                id={'type': 'correlations-graph-type', 'index': 0}
                            ),
                    ]),
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
                    ])
                ]
            )
        ]

def make_correlations_graphs(df, graph_type, attrib1, attrib2, corr_color_seq, corr_color_disc, corr_sort_order, filterx, filtery):
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

        # depending on the combination of the attributes, filters are applied 
        if (filterx == '' and filtery == ''):        
            df_to_use = final_df
        if (filterx != '' and filtery == ''):
            final_df_filtered = final_df[(final_df[attrib1].isin(filterx))]
            df_to_use = final_df_filtered
        elif (filterx == '' and filtery != ''):
            final_df_filtered = final_df[(final_df[attrib2].isin(filtery))]
            df_to_use = final_df_filtered
        else:
            final_df_filtered = final_df[(final_df[attrib1].isin(filterx) & final_df[attrib2].isin(filtery))]
            df_to_use = final_df_filtered
        # Create parallel categories diagram
        fig = px.parallel_categories(df_to_use, dimensions=attributes_to_group, color='fatality', color_continuous_scale=corr_color_seq, height=800)
        fig.update_layout(
        margin=dict(l=270, r=250, t=20, b=20),
        )
        fig.layout['coloraxis']['colorbar']['x'] = 1.30
        return [
            html.H5("Parallel Categories Diagram"),
            dcc.Graph(figure=fig)
        ]
    if graph_type == 'scatter':

        df_fatal = calculate_fatality_rate(df_temp, attrib1).reset_index()     
        
        # depending on the combination of the attributes, filters are applied 
        # Only attrib1 is considered, since this one is the only categorical attribute
        if (filterx == '' and filtery == ''):        
            df_to_use = df_fatal
        elif (filterx != '' and filtery == ''):
            final_df_filtered = df_fatal[(df_fatal[attrib1].isin(filterx))]
            df_to_use = final_df_filtered
        # Create new plot
        fig = px.scatter(df_to_use , x=attrib1, y=attrib2, height=800,
            color="fatality_rate", color_continuous_scale=corr_color_seq)
        fig = add_sort_order(fig, corr_sort_order)


        fig.update_traces(marker=dict(size=10), selector=dict(mode='markers'))
        return [
            html.H5("Scatter Plot"),
            html.H6(attrib1 + " " + attrib2),
            dcc.Graph(figure=fig)
        ]
    
    if graph_type == 'histogram':

        df_fatal = calculate_fatality_rate(df_temp, attrib1).reset_index()
        # depending on the combination of the attributes, filters are applied 
        # Only attrib1 is considered, since this one is the only categorical attribute
        if (filterx == '' and filtery == ''):        
            df_to_use = df_fatal
        elif (filterx != '' and filtery == ''):
            final_df_filtered = df_fatal[(df_fatal[attrib1].isin(filterx))]
            df_to_use = final_df_filtered
        # Create the Histogram
        fig = px.histogram(df_to_use, x=attrib1, y=attrib2, height=800,
                         color="fatality_rate" ,nbins=df[attrib1].unique().size, color_discrete_sequence=corr_color_disc)
        fig.update_traces(marker=dict(size=10), selector=dict(mode='markers'))
        fig = add_sort_order(fig, corr_sort_order)
        return [
            html.H5("Histogram"),
            html.H6(attrib1 + " " + attrib2),
            dcc.Graph(figure=fig)
        ]

    return []

# Helper function to set sorting order on graph
def add_sort_order (fig, req_order) :
    if req_order == SORT_ORDER_OPTIONS[1]:
        fig.update_xaxes(categoryorder="total ascending")
    elif req_order == SORT_ORDER_OPTIONS[2]:
        fig.update_xaxes(categoryorder="total descending")
    elif req_order == SORT_ORDER_OPTIONS[0]:
        fig.update_xaxes(categoryorder="trace")
    return fig


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
    if (attrib1 in CATEGORICAL_ATTRIBS and attrib2 in CATEGORICAL_ATTRIBS):
        return [{'label': 'Parallel category diagram', 'value': 'parallel'}], 'parallel'

    # Both quantitive
    if (attrib1 in QUANTITATIVE_ATTRIBS and attrib2 in QUANTITATIVE_ATTRIBS):
        return [{'label': 'Scatter plot', 'value': 'scatter'}], 'scatter'

    # One of each
    if (attrib1 in QUANTITATIVE_ATTRIBS) != (attrib2 in QUANTITATIVE_ATTRIBS):
        return [
            {'label': 'Scatter plot', 'value': 'scatter'},
            {'label': 'Histogram', 'value': 'histogram'}
        ], 'scatter'

    return [], ""

# Changing X-axis filter dropdown based on attribute chosen for X-axis 
@app.callback([Output({'type': 'correlations-attrib-filter', 'index': 0}, 'options'),
                Output({'type': 'correlations-attrib-filter', 'index': 0}, 'value')],
              [Input({'type':'correlations-attrib', 'index': ALL}, 'value')])
def test(attribs):
    attrib1 = attribs[0]
    if attrib1 == "light_conditions":
        return [{'label': x, 'value': x} for x in LIGHT_CONDITIONS], ''
    if attrib1 == "special_conditions_at_site":
        return [{'label': x, 'value': x} for x in SPECIAL_CONDITIONS_AT_SITE], ''
    if attrib1 == "road_surface_conditions":
        return [{'label': x, 'value': x} for x in ROAD_SURFACE_CONDITIONS], ''
    if attrib1 == "junction_control":
        return [{'label': x, 'value': x} for x in JUNCTION_CONTROL], ''
    if attrib1 == "junction_detail":
        return [{'label': x, 'value': x} for x in JUNCTION_DETAIL], ''
    return [], ''

# Changing Y-axis filter dropdown based on attribute chosen for Y-axis 
@app.callback([Output({'type': 'correlations-attrib-filter', 'index': 1}, 'options'),
                Output({'type': 'correlations-attrib-filter', 'index': 1}, 'value')],
              [Input({'type':'correlations-attrib', 'index': ALL}, 'value')])
def test2(attribs):
    attrib2 = attribs[1]
    if attrib2 == "light_conditions":
        return [{'label': x, 'value': x} for x in LIGHT_CONDITIONS], ''
    if attrib2 == "special_conditions_at_site":
        return [{'label': x, 'value': x} for x in SPECIAL_CONDITIONS_AT_SITE], ''
    if attrib2 == "road_surface_conditions":
        return [{'label': x, 'value': x} for x in ROAD_SURFACE_CONDITIONS], ''
    if attrib2 == "junction_control":
        return [{'label': x, 'value': x} for x in JUNCTION_CONTROL], ''
    if attrib2 == "junction_detail":
        return [{'label': x, 'value': x} for x in JUNCTION_DETAIL], ''
    return [], ''


# @app.callback(
#     [Output("attrib2-slider", "min"),
#     Output("attrib2-slider", "max"),
#     Output("attrib2-slider", "step"),
#     Output("attrib2-slider", "value")],
#     [Input({'type': 'correlations-attrib', 'index': 1}, 'value')], Input("hidden-data", "children"))
# def callback_test(y_attribute, data_json):
#     # print(data_json
#     df = pd.read_json(data_json)
#     print(y_attribute)
#     # User has not select Y-axis yet
#     if (isinstance(y_attribute, type(None))):
#         return 0, 100, 1, 50

#     min_value = df[y_attribute].min()
#     max_value = df[y_attribute].max()
#     median_value = df[y_attribute].median()
#     print(min_value, max_value, median_value)
#     return min_value, max_value, 1, median_value


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

