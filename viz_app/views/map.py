from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd

from config import ID_TO_POLICE_FORCE_AREA, POPULATION_BY_POLICE_FORCE_AREA, categorical_attribs, quantitive_attribs

from urllib.request import urlopen
import json

from viz_app.views.correlations import generate_dropdown_label
with urlopen('https://opendata.arcgis.com/datasets/61752cc924354e71846ffa044aa76669_0.geojson') as response:
    regions = json.load(response)

def make_map_panel():
    return [
        html.Label("Attribute"),
        dcc.Dropdown(
            id={
                'type': "map-attrib",
                'index': 0,
            },
            options=[{'label': generate_dropdown_label(a), 'value': a} for a in ['accident_count_per_capita', 'accident_count', 'fatality_rate']],
        ),
    ]

def make_map_graphs(df, attrib):
    if attrib == None:
        return
    processed_df = df[df['police_force'] < 90][['police_force', 'accident_severity']].copy()
    processed_df['police_force'] = [ID_TO_POLICE_FORCE_AREA[x] for x in processed_df['police_force']]
    
    if attrib == 'fatality_rate':
        processed_df = (processed_df[processed_df['accident_severity']==1].groupby(['police_force']).size() * 100 \
                        / processed_df.groupby(['police_force']).size()).reset_index(name='fatality_rate')    
    elif attrib == 'accident_count':
        processed_df = processed_df.groupby(['police_force']).size().reset_index(name='accident_count')
    elif attrib == 'accident_count_per_capita':
        processed_df = processed_df.groupby(['police_force']).size().reset_index(name='accident_count')
        processed_df[attrib] = [processed_df[processed_df['police_force'] == x]['accident_count'].values[0] / 
                                                POPULATION_BY_POLICE_FORCE_AREA[x] for x in processed_df['police_force']]
        
    fig = px.choropleth(processed_df, geojson=regions, featureidkey='properties.PFA20NM',
                        locations='police_force', color=attrib,
                        range_color=(0, processed_df[attrib].max() * 1.1),
                        height=800,
                        labels={
                            'accident_count_per_capita':'Accident Count per Capita',
                            'accident_count': 'Accident Count',
                            'fatality_rate': 'Fatality Rate (%)'}
                        )
    fig.update_geos(fitbounds="locations", visible=False)
    return [
        html.H5("Map Graph"),
        dcc.Graph(figure=fig),
    ]