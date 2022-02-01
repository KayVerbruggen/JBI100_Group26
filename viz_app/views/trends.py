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

    # Take the relevant columns of both dataframes.
    df_year1 = df[['date', 'accident_year', 'accident_severity']]
    df_year2 = other_df[['date', 'accident_year', 'accident_severity']]

    # Join the two years together.
    processed_df = pd.concat([df_year1, df_year2], axis=0)

    # Convert the date to MM:DD instead of DD:MM, this way the ordering is easier.
    processed_df['date'] = processed_df['date'].str[3:6] + processed_df['date'].str[0:2]
    if attrib == 'fatality_rate':
        processed_df = (processed_df[processed_df['accident_severity']==1].groupby(['date', 'accident_year']).size() \
                        / processed_df.groupby(['date', 'accident_year']).size()).reset_index(name='fatality_rate')    
    else:
        processed_df = processed_df.groupby(['date', 'accident_year']).size().reset_index(name='accident_count')
    
    # Add empty rows to align data.
    years = processed_df['accident_year'].unique()
    for index, row in processed_df.iterrows():
        other_year = years[0]
        if row['accident_year'] == years[0]:
            other_year = years[1]
        
        # If there is no accident on this day for the other year, add an empty row.
        if row['date'] not in processed_df[processed_df['accident_year'] == other_year]['date'].unique():
            processed_df = processed_df.append({
                'accident_year': other_year, 
                'date': row['date'],
            }, 
            ignore_index=True)

    # Make sure it is still sorted after adding the empty rows.
    processed_df.sort_values('date', inplace=True)

    fig = px.line(processed_df, x='date', y=attrib, color='accident_year', markers=True,
                  range_y=(0, processed_df[attrib].max()*1.1), labels={'date': 'Date (MM/DD)',
                  attrib: attrib.replace("_", " ").title(), 'accident_year':'Accident Year'},
                  color_discrete_sequence=trends_color_disc)
    return [
        html.H5("Trend Graph"),
        dcc.Graph(figure=fig),
    ]

# The settings for the trends visualization.
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
                # A dropdown that allows the user to choose another discrete color palette. 
                # Discrete colors to distinguish the lines of the two plots. (the two years are discrete)
                # These color palettes are built-in from Plotly. See 
                # https://plotly.com/python/discrete-color/
                html.Div([
                    html.Label("Color Scale - Discrete"),
                    dcc.Dropdown(
                        id={
                            'type': "trends-colorscale-disc",
                            'index': 0,
                        },
                        options=[{"value": x, "label": x} 
                            for x in DISCRETE_COL],
                        # Default color palette Pastel1
                        value='Pastel1'
                    )])
                ])
    ]
