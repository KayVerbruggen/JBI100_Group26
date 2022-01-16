from threading import local
from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, MATCH, ALL

from viz_app.main import app

from config import ID_TO_LOCAL_DISTRICT, ID_TO_POLICE_FORCE_AREA, POPULATION_BY_POLICE_FORCE_AREA, CATEGORICAL_ATTRIBS, QUANTITATIVE_ATTRIBS, SEQ_CONT_COL

from urllib.request import urlopen
import json

from viz_app.views.correlations import generate_dropdown_label
with urlopen('https://opendata.arcgis.com/datasets/2a1e3c23f1f24f15808275f52b8ae20d_0.geojson') as response:
    policeRegions = json.load(response)
with urlopen('https://opendata.arcgis.com/datasets/ac4ad96a586b4e4bab306dd59eb09401_0.geojson') as response:
    localRegions = json.load(response)



def make_map_panel():
    return [
        html.Div(
            style={
                "display": "flex",
                "flex-direction": "column",
                "gap": "16px",
            },
            children = [
                html.Div([
                    html.Label("Specific Region"),
                    dcc.Dropdown(
                        id={
                            'type': "map-attrib",
                            'index': 0,
                        },
                        options=[{'label': a, 'value': a} 
                            for a in ['None'] + list(POPULATION_BY_POLICE_FORCE_AREA)],
                        value='None'
                    )
                ]),
                html.Div([
                    html.Label("Attribute"),
                    dcc.Dropdown(
                        id={
                            'type': "map-attrib",
                            'index': 1,
                        },
                        options=[{'label': generate_dropdown_label(a), 'value': a} 
                            for a in ['accident_count_per_capita', 'accident_count', 'fatality_rate']],
                        value='accident_count_per_capita'
                    )
                ]),
                html.Div([
                    html.Label("Color Scale - Sequential"),
                    dcc.Dropdown(
                        id={
                            'type': "map-colorscale-seq",
                            'index': 0,
                        },
                        options=[{"value": x, "label": x} 
                            for x in SEQ_CONT_COL],
                        value='Reds'
                    )
                ])
            ]
        )]

# Changing the correlations panel
@app.callback([Output({'type': 'map-attrib', 'index': 1}, 'options'),
               Output({'type': 'map-attrib', 'index': 1}, 'value')],
              [Input({'type': 'map-attrib', 'index': 0}, 'value')])
def map_graph_options(region):
    # No specific region
    if region == "None":
        return [{'label': generate_dropdown_label(a), 'value': a} for a in ['accident_count_per_capita', 'accident_count', 'fatality_rate']], 'accident_count_per_capita'
    
    return [{'label': generate_dropdown_label(a), 'value': a} for a in ['accident_count', 'fatality_rate']], 'accident_count'

def make_map_graphs(df, region, attrib, map_color_seq):
    if attrib == None:
        return
        
    processed_df = df[df['police_force'] < 90][['police_force', 'accident_severity', 'local_authority_district']].copy()
    processed_df['police_force'] = [ID_TO_POLICE_FORCE_AREA[x] for x in processed_df['police_force']]

    region_map = policeRegions
    region_key = 'properties.PFA20NM'
    region_attrib = 'police_force'
    if region != "None":
        processed_df = processed_df[processed_df['police_force'] == region]
        processed_df['local_authority_district'] = [ID_TO_LOCAL_DISTRICT[x] for x in processed_df['local_authority_district']]
        region_map = localRegions
        region_key = 'properties.LAD21NM'
        region_attrib = 'local_authority_district'

    if attrib == 'fatality_rate':
        processed_df = (processed_df[processed_df['accident_severity']==1].groupby([region_attrib]).size() * 100 \
                        / processed_df.groupby([region_attrib]).size()).reset_index(name='fatality_rate')    
    elif attrib == 'accident_count':
        processed_df = processed_df.groupby([region_attrib]).size().reset_index(name='accident_count')
    elif attrib == 'accident_count_per_capita':
        processed_df = processed_df.groupby([region_attrib]).size().reset_index(name='accident_count')
        processed_df[attrib] = [processed_df[processed_df[region_attrib] == x]['accident_count'].values[0] / 
                                                POPULATION_BY_POLICE_FORCE_AREA[x] for x in processed_df[region_attrib]]
        
    fig = px.choropleth(processed_df, geojson=region_map, featureidkey=region_key,
                        locations=region_attrib, color=attrib,
                        range_color=(0, processed_df[attrib].max() * 1.1),
                        height=800,
                        labels={
                            'accident_count_per_capita':'Accident Count per Capita',
                            'accident_count': 'Accident Count',
                            'fatality_rate': 'Fatality Rate (%)'},
                        color_continuous_scale=map_color_seq
                        )
    fig.update_geos(fitbounds="locations", visible=False)
    return [
        html.H5("Map Graph"),
        dcc.Graph(figure=fig),
    ]