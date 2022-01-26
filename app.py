import os
from _plotly_utils.colors import get_colorscale
import dash
from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd
import datetime
import json
from dash.dependencies import Input, Output, MATCH, ALL, State

from viz_app.main import app
from viz_app.storage import Storage
from viz_app.views.map import make_map_panel, make_map_graphs
from viz_app.views.correlations import make_correlations_panel, make_correlations_graphs
from viz_app.views.trends import make_trends_panel, make_trends_graphs
import config
from config import ID_TO_LIGHT_CONDITIONS, ID_TO_JUNCTION_DETAIL, ID_TO_LOCAL_DISTRICT, ID_TO_REGION, ID_TO_SPECIAL_CONDITIONS_AT_SITE, CATEGORICAL_ATTRIBS, LOCATION_ATTRIBS, POPULATION_BY_REGION, QUANTITATIVE_ATTRIBS, \
                   MISSING_VALUE_TABLE, ID_TO_JUNCTION_CONTROL, ID_TO_ROAD_SURFACE_CONDITIONS, ID_TO_SPECIAL_CONDITIONS_AT_SITE, \
                   LIGHT_CONDITIONS, SPECIAL_CONDITIONS_AT_SITE, ROAD_SURFACE_CONDITIONS, \
                   JUNCTION_CONTROL, JUNCTION_DETAIL, ALL_ATTRIBUTES, SPEED_LIMIT



storage = Storage({})

# This function joins the module and built-in palette name (discrete), e.g. px.colors.qualitative.Reds
def get_disc_color(c):
    return getattr(px.colors.qualitative, c)

# This function joins the module and built-in palette name (sequential), e.g. px.colors.qualitative.Reds
def get_seq_cont_color(c):
    return getattr(px.colors.sequential, c)

# This function converts feature name into label names
def generate_dropdown_label(a):
    return a.replace("_", " ").title()

app.layout = html.Div(
    style={"width": "100%", "height": "100%"},
    children = [
    html.Div(id="placeholder", style={"visibility": "hidden", "position": "absolute"}),
    html.Div(
        className="topnav",
        children=[
            dcc.Link('Home', href='/'),
            dcc.Link('Map', href='/map'),
            dcc.Link('Correlations', href='/correlations'),
            dcc.Link('Trends', href='/trends'),
        ]
    ),
    dcc.Location(id='url', refresh=False),
    html.Div(
        id="home-page",
        className="ten columns",
        children=[
            html.H5("Visualization Tool by Group 26"),
            html.P("Use the navigation bar above to select a visualization. "
                   "You can choose from the following options:"),
            html.H6("Map", style={'text-decoration': 'underline'}),
            html.P("In this tab, you can locate the distributions of the accident count, fatality rate or accident "
                   "count per capita in specific regions of Great Britain or Great Britain as a whole. "
                   "The color of the regions on the map determines how severe the value of the chosen attribute is."),
            html.H6("Correlations", style={'text-decoration': 'underline'}),
            html.P("This tab allows you to explore the correlations between two attributes. "
                   "Depending on the type of the attributes, specific visualizations are created. For example, "
                   "choosing a categorical attribute on the x axis and a quantitative attribute on the y axis will"
                   " generate a scatterplot and histogram. This tab has multiple purposes as the histograms generated "
                   "allow the user to explore the distributions of a specific categorical attribute as well."),
            html.H6("Trends", style={'text-decoration': 'underline'}),
            html.P("This tab allows you to compare trends in the accident count or fatality rate "
                   "between any two years in the dataset. You can also simply just use it to see the trend "
                   "of any single year. The data of each of the years is shown as a line graph.")
        ]
    ),
    html.Div(
        id="leftColumn",
        className="two columns",
        children=[
            html.H5("Settings"),
            html.Div([
                html.Label("Dataset Year"),
                dcc.Dropdown(
                    id="dataset-year",
                    options=[{"label": i, "value": i} for i in range(1979, 2021)],
                    value=2020,
                    searchable=False,
                ),
            ]),
            html.Div(
                id='panel-content', className="control_card",
                children=make_correlations_panel(),
                style={"margin-top": "16px", "textAlign": "float-left"}
            ),                       
        ]
    ),
    html.Div(
        id="filter-panel",
        className="two columns wrapper",
        children=[
            html.H5("Filter"),
            html.Button(
                "New filter",
                className="button",
                id="btn-add-filter",
                n_clicks = 0
            ),
            html.Div(
                 style={
                    "display": "flex",
                    "flex-direction": "column",
                    "gap": "12px",
                }, 
                id="filter-section",
                children=[]
            ),
            html.Button(
                "Apply",
                className="button",
                id="btn-apply-filter",
                n_clicks = 0
            ),
        ]
    ),
    html.Div(
        id="rightColumn",
        className="eight columns",
        children=[
            html.Div(id='graph-content'),
        ]
    ),
])


@ app.callback(Output('home-page', 'style'),
    Output('filter-panel', 'style'), 
    Output('rightColumn', 'style'), 
    Output('leftColumn', 'style'), 
    Input('url', 'pathname'))
def show_hide_homepage(pathname):
    show = {'display': 'block'}
    hide = {'display': 'none'}
    if pathname in ['/map', '/correlations', '/trends']:
        return hide, show, show, show
    
    return show, hide, hide, hide

# Changing the left panel based on the url
@app.callback(Output('panel-content', 'children'),
              [Input('url', 'pathname')])
def display_options(pathname):
    if pathname == '/map':
        return make_map_panel()
    elif pathname == '/correlations':
        return make_correlations_panel()
    elif pathname == '/trends':
        return make_trends_panel()
    else:
        return []
    # You could also return a 404 "URL not found" page here

# This is a onClick handler for adding a filter option to a selected attribute
@app.callback(Output({"type": "filter-attribute-action", "index": MATCH}, "children"),
              Input({"type": "filter-attribute-dropdown", "index": MATCH}, "value"),
              State({"type": "filter-attribute-action", "index": MATCH}, 'id'),
              State("dataset-year", "value"))
def add_filter_option(attrib, id, year):
    # Dynamically create filter option based on the selected attribute type (i.e. Categorical)
    df = get_data(year)
    if (attrib in QUANTITATIVE_ATTRIBS):
        column = df[attrib]
        x = attrib
        if (attrib == "time"):
            column = df["time_index"]
            x = "time_index"

        val_min = column.min()
        val_max = column.max()
        fig = px.histogram(df, x=x)
        fig.update_layout(
            xaxis={'visible': False, 'showticklabels': False}, 
            yaxis={'visible': False, 'showticklabels': False},
            margin=dict(l=20, r=20, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
        )
        return [
            dcc.Graph(figure=fig, style={"margin-bottom": "8px"}),
            dcc.RangeSlider(className=attrib, id={"type": "filter-action-slider", \
            "index": id["index"]}, value=[val_min, val_max], min=val_min, max=val_max, \
            step=None, 
            marks={
                0: {'label': "00"},
                300: {'label': "03"},
                600: {'label': "06"},
                900: {'label': "09"},
                1200: {'label': "12"},
                1500: {'label': "15"},
                1800: {'label': "18"},
                2100: {'label': "21"},
                2359: {"label": "24"}
            }), html.Div(style={"display": "flex", "justify-content": "space-between"}, 
                children=[
                    html.Label(id={"type": "slider-label-start", "index": id["index"]} ,children = "00:00"),
                    html.Label(id={"type": "slider-label-end", "index": id["index"]} ,children = "23:59")
            ])]
    elif (attrib in CATEGORICAL_ATTRIBS or attrib in LOCATION_ATTRIBS):
        options = []
        if attrib == "light_conditions":
            options = [{'label': x, 'value': x} for x in LIGHT_CONDITIONS]
        if attrib == "special_conditions_at_site":
            options =  [{'label': x, 'value': x} for x in SPECIAL_CONDITIONS_AT_SITE]
        if attrib == "road_surface_conditions":
            options =  [{'label': x, 'value': x} for x in ROAD_SURFACE_CONDITIONS]
        if attrib == "junction_control":
            options = [{'label': x, 'value': x} for x in JUNCTION_CONTROL]
        if attrib == "junction_detail":
            options = [{'label': x, 'value': x} for x in JUNCTION_DETAIL]
        if attrib == "speed_limit":
            options = [{'label': x, 'value': x} for x in SPEED_LIMIT]
        if attrib == "region":
            options = [{'label': x[1], 'value': x[0]} for x in ID_TO_REGION.items()]
        if attrib == "local_district":
            options = [{'label': x[1], 'value': x[0]} for x in ID_TO_LOCAL_DISTRICT.items()]
        return dcc.Dropdown(className=attrib, id={"type": "filter-action-select", "index": id["index"]}, multi=True, options=options, value="")

# This is a onClick handler for creating new attribute filter
@app.callback(Output("filter-section", "children"), Input("btn-add-filter", "n_clicks"),
              State("filter-section", "children"))
def create_filter(n_clicks, filterSection):
    filterSection.append(
        html.Div(
            id={
                "type": "filter-group",
                "index": n_clicks
            },
            children=[
                html.Label("Filter {}".format(n_clicks + 1)),
                dcc.Dropdown(
                    style={"margin-bottom": "8px"},
                    id={
                        'type': "filter-attribute-dropdown",
                        'index': n_clicks,
                    },
                    options=[{'label': generate_dropdown_label(a), 'value': a} for a in (
                        ALL_ATTRIBUTES)],
                    searchable=False,
                ),
                html.Div(
                    id={
                        'type': "filter-attribute-action",
                        'index': n_clicks,
                    },
                    children=[]
                )
            ]
        )
    )
    return filterSection

@app.callback(
    Output({"type": "slider-label-start", "index": MATCH}, "children"),
    Output({"type": "slider-label-end", "index": MATCH}, "children"),
    Input({"type": "filter-action-slider", "index": MATCH}, "value"))
def display_slider_label(interval):
    temp_1 = interval[0]
    temp_2 = interval[1]
    start = ""
    end = ""
    if (temp_1 < 1000):
        start = "0{}:{}".format(str(temp_1)[0], str(temp_1)[1:])
        if (temp_1 == 0):
            start = "00:00"
    else:
        start = "{}:{}".format(str(temp_1)[0: 2], str(temp_1)[2:])

    if (temp_2 < 1000):
        if (temp_2 == 0):
            start = "00:00"
        end = "0{}:{}".format(str(temp_2)[0], str(temp_2)[1:])
    else:
        end = "{}:{}".format(str(temp_2)[0: 2], str(temp_2)[2:])
    return start, end


@app.callback(
    Output("placeholder", "children"),
    Input({"type": "filter-action-select", "index": ALL}, "value"),
    Input({"type": "filter-action-slider", "index": ALL}, "value"),
    State({"type": "filter-action-select", "index": ALL}, "className"),
    State({"type": "filter-action-slider", "index": ALL}, "className"))
def filter_by_attributes(list_filter_categorical, list_filter_quantitative, list_attribute_categorical, list_attrib_quantitative):
    filter_dict = {}
    list_filter = list_filter_categorical + list_filter_quantitative
    list_attrib = list_attribute_categorical + list_attrib_quantitative
    filter_dict = create_filter_dict(list_filter, list_attrib)
    return json.dumps(filter_dict)


# Changing the right panel based on the url
@app.callback(Output('graph-content', 'children'),
                [Input('url', 'pathname'),
                Input('dataset-year', 'value'),  
                # Map Options
                Input({'type': 'map-attrib', 'index': ALL}, 'value'),
                Input({'type': 'map-colorscale-seq', 'index': ALL}, 'value'),

                # Correlations Options
                Input({'type': 'correlations-attrib', 'index': ALL}, 'value'),
                Input({'type': 'correlations-colorscale-seq', 'index': ALL}, 'value'),
                Input({'type': 'correlations-colorscale-disc', 'index': ALL}, 'value'),
                Input({'type': 'correlations-sorting-order', 'index': ALL}, 'value'),
                Input({'type': 'correlations-kmeans', 'index': ALL}, 'value'),

                # Trends Options
                Input({'type': 'trends-attrib', 'index': ALL}, 'value'),
                Input({'type': 'trends-colorscale-disc', 'index': ALL}, 'value'),

                # Filter
                Input("btn-apply-filter", "n_clicks"),
                State("placeholder", "children")
            ])
def display_graphs(pathname, year, map_attribs, map_color_seq, corr_attribs,
                   corr_color_seq, corr_color_disc, corr_sort_order, k_means, trends_attribs, trends_color_disc, n_clicks, filter_json):
    df = get_data(year)
    df_filtered = df.copy()
    # Parse filter_dict in json format that is stored in "#placeholder"
    filter_dict = json.loads(filter_json)
    # If the apply button is clicked and the filter is not empty
    if (n_clicks != 0) and (len(filter_dict) != 0):
        # Filter dataset
        df_filtered = filter_dataset(df, filter_dict)
    if pathname == '/map':
        regions = []
        if 'region' in filter_dict:
            regions = filter_dict['region']
        return make_map_graphs(df_filtered, regions, map_attribs[0], get_seq_cont_color(map_color_seq[0]))
    elif pathname == '/correlations':
        temp_data = make_correlations_graphs(df_filtered, corr_attribs[0], corr_attribs[1],
                                             get_seq_cont_color(corr_color_seq[0]),
                                             get_disc_color(corr_color_disc[0]), corr_sort_order[0], k_means[0], k_means[1])
        if temp_data:
            storage.update(temp_data["dataframe"])
            return temp_data['children']
        return temp_data

    elif pathname == '/trends':
        return make_trends_graphs(df_filtered, trends_attribs[0], trends_attribs[1], get_disc_color(trends_color_disc[0]))
    else:
        return []
    # You could also return a 404 "URL not found" page here

@app.callback(
    Output({'type': 'correlations-graph', 'index': ALL}, 'figure'), 
        Input({'type': 'correlations-graph', 'index': ALL}, 'selectedData'),
    [
        State({'type': 'correlations-attrib', 'index': ALL}, 'value'),
        State({'type': 'correlations-colorscale-seq', 'index': ALL}, 'value'),
        State({'type': 'correlations-colorscale-disc', 'index': ALL}, 'value'),
    ])
def update_brushing(selected_data, corr_atrib, color_seq, color_disc):
    # If there are no two graphs, don't change anything.
    if len(selected_data) != 2:
        return dash.no_update
    
    #print(selected_data)

    # If the selected data changed for graph 0.
    if "\"index\":0" in dash.callback_context.triggered[0]['prop_id'] and selected_data[0] != None:
        # Update the second graph and leave the first the same.
        return [
            dash.no_update, 
            update_figure_histogram(storage.get(), corr_atrib[0], corr_atrib[1], selected_data[0], get_disc_color(color_disc[0]))
        ]
    elif "\"index\":1" in dash.callback_context.triggered[0]['prop_id'] and selected_data[1] != None:
        # Update the first graph and leave the second the same.
        return [
            update_figure_scatter(storage.get(), corr_atrib[0], corr_atrib[1], selected_data[1], color_seq[0]), 
            dash.no_update
        ]
    
    # Should never reach this, just in case.
    return dash.no_update


def update_figure_scatter(df, attrib1, attrib2, selectedpoints, corr_color_seq):
    fig = px.scatter(df, x=attrib1, y=attrib2, color='fatality_rate', height=800,
                     color_continuous_scale=corr_color_seq, labels={'fatality_rate': 'Fatality Rate(%)'})
    fig.update_layout(
        yaxis_zeroline=False,
        xaxis_zeroline=False,
        dragmode='select'
    )
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)

    # highlight points with selection other graph
    if selectedpoints is None:
        selected_index = df.index  # show all
    else:
        selected_index = [  # show only selected indices
            point['curveNumber']
            for point in selectedpoints['points']
        ]

    fig.update_traces(
        mode='markers',
        marker_size=20,
        #Selected indexes
        selectedpoints=selected_index,
        # color of selected points
        selected=dict(marker=dict(opacity=1.0)),
        # color of unselected pts
        unselected=dict(marker=dict(opacity=0.2))
    )


    # update axis titles
    fig.update_layout(
        xaxis_title=attrib1.replace("_", " ").title(),
        yaxis_title=attrib2.replace("_", " ").title(),
    )

    return fig


def update_figure_histogram(df, attrib1, attrib2, selectedpoints, corr_color_disc):
    fig = px.histogram(df, x=attrib1, y=attrib2, color='fatality_rate', height=800,
                       nbins=df.index.unique().size, color_discrete_sequence=corr_color_disc, labels=
                       {'fatality_rate': 'Fatality Rate(%)'})

    fig.update_layout(
        yaxis_zeroline=False,
        xaxis_zeroline=False,
        dragmode='select'
    )
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)

    # highlight points with selection other graph
    if selectedpoints is None:
        selected_index = df.index  # show all
    else:
        selected_index = [  # show only selected indices
            point['pointIndex']
            for point in selectedpoints['points']
        ]

    fig.update_traces(
        # color of selected points
        selected=dict(marker=dict(opacity=1.0)),
        # color of unselected pts
        unselected=dict(marker=dict(opacity=0.2))
    )

    current_indexes = [ x for x in range( len(fig.data) ) ]
    unselected_indexes = [x for x in current_indexes if x not in selected_index]

    for point in unselected_indexes:
        fig.data[point].update(
            selectedpoints=selected_index
        )

    # update axis titles
    fig.update_layout(
        xaxis_title=attrib1.replace("_", " ").title(),
        yaxis_title=attrib2.replace("_", " ").title(),
    )

    return fig


# Read and pre-process dta
def get_data(year):
    df = pd.read_csv(
        os.getcwd() + "/datasets/road_safety_" + str(year) + ".csv")
    df_valid = remove_missing_value(df)
    df = id_to_value(df_valid)
    # Add "time as integer" as a new column
    df['time_index'] = pd.to_numeric(df["time"].str.replace(':','')).astype("int")
    return df

# This is an auxillary method to create filter_dict from lists of attibutes and their selected options
def create_filter_dict(list_filter, list_attribute):
    filter_dict = {}
    for i in range(0, len(list_attribute)):
        attrib = list_attribute[i]
        try:
            filter_dict[attrib] = filter_dict[attrib] + list_filter[i]
        except:
            filter_dict[attrib] = list_filter[i]
    return filter_dict

# This is an auxillary method to filter a given dataset using a filter_dict
def filter_dataset(df, filter_dict):
    df_filtered = df.copy()
    # Iterate through each filter option
    for attrib in filter_dict:
        filter_options = filter_dict[attrib]
        if (len(filter_options) == 0):
            continue
        if (attrib == "time"): 
            start = filter_options[0]
            end = filter_options[1]
            df_filtered = df_filtered[(df_filtered["time_index"] >= start) & (df_filtered["time_index"] <= end)]
        else:
            df_filtered = df_filtered[df_filtered[attrib].isin(filter_options)]

    return df_filtered


# Remove rows with missing values for every target attribute
def remove_missing_value(df):
    columns = MISSING_VALUE_TABLE.keys()
    df_processed = df.copy()
    for attribute in columns:
        for missing_value in MISSING_VALUE_TABLE[attribute]:
            df_processed = df_processed[df_processed[attribute] != missing_value]
    return df_processed

# Map IDS to the corresponding value
def id_to_value(df):
    df_mapped = df.copy()
    return df_mapped.replace({'light_conditions': ID_TO_LIGHT_CONDITIONS, 'junction_detail': ID_TO_JUNCTION_DETAIL, \
                              'junction_control': ID_TO_JUNCTION_CONTROL,
                              'road_surface_conditions': ID_TO_ROAD_SURFACE_CONDITIONS, \
                              'special_conditions_at_site': ID_TO_SPECIAL_CONDITIONS_AT_SITE})

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

if __name__ == '__main__':
    app.run_server(debug=True)