import os
import calendar
from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd

from config import CATEGORICAL_ATTRIBS, QUANTITATIVE_ATTRIBS, DISCRETE_COL
from viz_app.views.correlations import generate_dropdown_label

def make_trends_graphs(df, other_df, attrib, trends_color_disc):
    if attrib == None:
        return

    df_year1 = df[['date', 'accident_year', 'accident_severity']]
    df_year2 = other_df[['date', 'accident_year', 'accident_severity']]
    processed_df = pd.concat([df_year1, df_year2], axis=0)
    # Look at only the month.
    #processed_df['date'] = processed_df['date'].str[3:5] 

    # Look day by day (doesn't handle Feb 29 properly)
    processed_df['date'] = processed_df['date'].str[3:6] + processed_df['date'].str[0:2]
    if attrib == 'fatality_rate':
        processed_df = (processed_df[processed_df['accident_severity']==1].groupby(['date', 'accident_year']).size() \
                        / processed_df.groupby(['date', 'accident_year']).size()).reset_index(name='fatality_rate')    
    else:
        processed_df = processed_df.groupby(['date', 'accident_year']).size().reset_index(name='accident_count')
    
    years = processed_df['accident_year'].unique()
    if calendar.isleap(years[0]) and not calendar.isleap(years[1]):
        processed_df = processed_df.append({
                'accident_year': years[1], 
                'date': '02/29', 
            }, 
            ignore_index=True)
    elif not calendar.isleap(years[0]) and calendar.isleap(years[1]):
        processed_df = processed_df.append({
                'accident_year': years[0], 
                'date': '02/29', 
            }, 
            ignore_index=True)

    processed_df.sort_values('date', inplace=True)

    # Limits on Y axis are somewhat arbitray, but it looks fine for now.
    fig = px.line(processed_df, x='date', y=attrib, color='accident_year', markers=True,
                  range_y=(0, processed_df[attrib].max()*1.1), labels={'date': 'Date (MM/DD)',
                  attrib: attrib.replace("_", " ").title(), 'accident_year':'Accident Year'},
                  color_discrete_sequence=trends_color_disc)
    return [
        html.H5("Trend Graph"),
        dcc.Graph(figure=fig),
    ]


def make_trends_panel():
    return [
        html.Div(
            style={
                "display": "flex",
                "flex-direction": "column",
                "gap": "16px",
            },
            children = [
                html.Div([
                    html.Label("Other Year"),
                    dcc.Dropdown(
                        id={
                            'type': "trends-attrib",
                            'index': 0,
                        },
                        options=[{"label": i, "value": i} for i in range(1979, 2021)],
                        value=2019,
                        searchable=False)
                ]),
                html.Div([
                    html.Label("Attribute"),
                    dcc.Dropdown(
                        id={
                            'type': "trends-attrib",
                            'index': 1,
                        },
                        options=[{'label': generate_dropdown_label(a), 'value': a} for a in ['fatality_rate', 'accident_count']],
                        value='accident_count',
                    )
                ]),
                html.Div([
                    html.Label("Color Scale - Discrete"),
                    dcc.Dropdown(
                        id={
                            'type': "trends-colorscale-disc",
                            'index': 0,
                        },
                        options=[{"value": x, "label": x} 
                            for x in DISCRETE_COL],
                        value='Pastel1'
                    )])
                ])
    ]
