import dash
from dash import dcc
from dash import html
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash import callback
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
from data import db_info
from datetime import datetime as dt


dash.register_page(__name__, external_stylesheets=[dbc.themes.PULSE])

filters_lists = {'Designation': 'designation', 'Department': 'dept', 'Employee Type': 'emp_type',
                 'Nationality': 'nationality', 'Sex': 'sex', 'Maritial Status': 'maritial_state',
                 'Age Group': 'age_group', 'Service Period': 'service_period'}

row_one = dbc.Row(
    children=[
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dcc.Dropdown(
                            id='first-dpdw',
                            options=[{'label': v, 'value': k}
                                     for v, k in filters_lists.items()],
                            multi=False,
                            value='sex',
                        ),
                        dcc.Dropdown(
                            id='first-dpn-dpdw',
                            options=[],
                            multi=True,
                            clearable=True,
                            disabled=False,
                            placeholder='Please select an option',
                            className='mt-1',
                            value=['Male']
                        )
                    ], width=6
                ),
                dbc.Col(
                    children=[
                        dcc.Dropdown(
                            id='second-dpdw',
                            options=[],
                            clearable=False,
                            disabled=False,
                            value='nationality'
                        ),
                        dcc.Dropdown(
                            id='second-dpn-dpdw',
                            options=[],
                            clearable=True,
                            disabled=False,
                            multi=True,
                            placeholder='Please select an option',
                            className='mt-1',
                            value=['INDIAN']
                        )
                    ], width=6
                )
            ]
        ), dcc.Graph(id='hr-analytic', figure={})
    ]
)

row_two = dbc.Row(
    children=[
        html.H5('EMPLOYEE MOVEMENT FOR THE PERIOD',
                className='text-center text-primary mb-4'),
        html.Div(
            children=[], id='pl_results')
    ]
)

layout = html.Div(
    dcc.Loading(children=[row_one,
                          row_two],
                color='#119DFF',
                type='dot',
                fullscreen=True)
)

current_date = datetime.now()


def age_bracket(age):
    if age <= 30:
        return 'Below 30'
    elif age <= 40:
        return '30-40'
    elif age <= 50:
        return '40-50'
    else:
        return 'Above 50'


def service_bracket(age):
    if age <= 1:
        return 'Below 1 Year'
    elif age <= 2:
        return '1 - 2 Years'
    elif age <= 3:
        return '2 - 3 Years'
    elif age <= 4:
        return '3 - 4 Years'
    elif age <= 5:
        return '4 - 5 Years'
    else:
        return 'Above 5 Years'


@callback(
    [Output(component_id='first-dpn-dpdw', component_property='options'),
     Output(component_id='second-dpdw', component_property='options'),
     Output(component_id='second-dpn-dpdw', component_property='options'),
     Output(component_id='hr-analytic', component_property='figure')
     ],


    [Input(component_id='database', component_property='data'),
     Input(component_id='first-dpdw', component_property='value'),
     Input(component_id='second-dpdw', component_property='value'),
     Input(component_id='first-dpn-dpdw', component_property='value'),
     Input(component_id='second-dpn-dpdw', component_property='value'),
     Input(component_id='end-date', component_property='data')],
    prevent_initial_call=True
)
def my_func(database, first_dpdw, second_dpdw, first_dpn_dpdw, second_dpn_dpdw, end_date):
    engine = create_engine(
        f'postgresql://{db_info["USERNAME"]}:{db_info["PWD"]}@{db_info["HOSTNAME"]}:{db_info["PORT_ID"]}/{database}')

    df_dEmployee = pd.read_sql('dEmployee', engine, parse_dates=[
                               'dob', 'doj', 'confirmation_date', 'last_increment', 'last_rejoin', 'termination_date'])

    cy_end_date = dt.strptime(end_date, '%Y-%m-%d')

    df_dEmployee['age'] = df_dEmployee['dob'].apply(
        lambda x: relativedelta(current_date, x).years)
    df_dEmployee['age_group'] = df_dEmployee['age'].apply(age_bracket)
    df_dEmployee['service'] = df_dEmployee['doj'].apply(
        lambda x: relativedelta(current_date, x).years)
    df_dEmployee['service_period'] = df_dEmployee['service'].apply(
        service_bracket)
    existing_emp_filt = (~df_dEmployee['termination_date'].notna()) | (df_dEmployee['termination_date'] > cy_end_date)

    df_dEmployee = df_dEmployee.loc[existing_emp_filt]

    # create a subset from the df_dEmployees which has only two columns [first_dropdown and second dropdown]
    df_graph = df_dEmployee[[first_dpdw, second_dpdw]]
    filt = (df_graph[first_dpdw].isin(first_dpn_dpdw)) & (
        df_graph[second_dpdw].isin(second_dpn_dpdw))
    df_graph = df_graph.loc[filt]

    fig = px.bar(data_frame=df_graph,
                 x=first_dpdw,
                 color=second_dpdw,
                 barmode='stack'
                 )
    fig.update_layout(title=dict(text=f'{first_dpdw.title()} and {second_dpdw.title()}',
                                 font=dict(size=20,
                                           color='black',
                                           family='Arial'),
                                 x=0.5),
                      xaxis_title=first_dpdw.title(),
                      yaxis_title='No of Staff',
                      legend_title_text=second_dpdw.title())
    filtered_first = df_dEmployee.loc[df_dEmployee[first_dpdw].isin(
        first_dpn_dpdw)]

    return [
        [{'label': i.title(), 'value': i}
         for i in sorted(df_dEmployee[first_dpdw].unique())],
        [{'label': v, 'value': k}
            for v, k in filters_lists.items() if k != first_dpdw],
        [{'label': j.title(), 'value': j}
         for j in sorted(filtered_first[second_dpdw].unique())],
        fig
    ]
