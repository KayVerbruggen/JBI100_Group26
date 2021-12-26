import os
from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd

from config import categorical_attribs, quantitive_attribs
from viz_app.views.correlations import generate_dropdown_label

def make_trends_graphs(df, other_year, attrib):
    if other_year == None or attrib == None:
        return
    other_df = pd.read_csv(
        os.getcwd() + "/datasets/road_safety_" + str(other_year) + ".csv")

    df_year1 = df[['date', 'accident_year', 'accident_severity']]
    df_year2 = other_df[['date', 'accident_year', 'accident_severity']]
    processed_df = pd.concat([df_year1, df_year2], axis=0)
    # Look at only the month.
    processed_df['date'] = processed_df['date'].str[3:5] 

    # Look day by day (doesn't handle Feb 29 properly)
    #processed_df['date'] = processed_df['date'].str[3:6] + processed_df['date'].str[0:2]
    if attrib == 'fatality_rate':
        processed_df = (processed_df[processed_df['accident_severity']==1].groupby(['date', 'accident_year']).size() \
                        / processed_df.groupby(['date', 'accident_year']).size()).reset_index(name='fatality_rate')    
    else:
        processed_df = processed_df.groupby(['date', 'accident_year']).size().reset_index(name='accident_count')
    
    # Limits on Y axis are somewhat arbitray, but it looks fine for now.
    fig = px.line(processed_df, x='date', y=attrib, color='accident_year', 
                        markers=True, range_y=(0, processed_df[attrib].max()*1.1),
                        labels={'date': 'Date (MM/DD)'})
    return [
        html.H5("Trend Graph"),
        dcc.Graph(figure=fig),
    ]


def make_trends_panel():
    return [
        html.Label("Other Year"),
        dcc.Dropdown(
            id={
                'type': "trends-attrib",
                'index': 0,
            },
            options=[{"label": i, "value": i} for i in range(1979, 2021)],
            value=2019,
            searchable=False,
        ),
        html.Label("Attribute"),
        dcc.Dropdown(
            id={
                'type': "trends-attrib",
                'index': 1,
            },
            options=[{'label': generate_dropdown_label(a), 'value': a} for a in ['fatality_rate', 'accident_count']],
        ),
    ]
