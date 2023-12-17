import dash
from dash import dcc
from dash import html
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
                 'Nationality': 'nationality',
                 'Sex': 'sex', 'Maritial Status': 'maritial_state', 'Age Group': 'age_group',
                 'Service Period': 'service_period'}

current_date = dt.now()
start_date = dt.strptime(str(dt.now().year) + '-01-01', '%Y-%m-%d')

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
        html.H5(f'EMPLOYEE MOVEMENT FOR THE PERIOD FOR THE PERIOD FROM {start_date.date()} TO {current_date.date()}',
                className='text-center text-primary mb-4'),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dcc.Dropdown(
                            id='first-selection',
                            multi=False,
                            clearable=False,
                            value='sex',
                            options=[{'label': v, 'value': k}
                                     for v, k in filters_lists.items()],
                            className='mb-1'
                        )
                    ]
                ),
                dbc.Col(
                    children=[
                        dcc.Dropdown(
                            id='second-selection',
                            multi=True,
                            clearable=True,
                            value=[],
                            options=[],
                            className='mb-1'
                        )
                    ]
                )
            ]
        ),
        html.Div(
            children=[], id='staff-movement')
    ]
)

layout = html.Div(
    dcc.Loading(children=[row_one,
                          html.Hr(),
                          row_two,
                          html.Hr()],
                color='#119DFF',
                type='dot',
                fullscreen=True)
)


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
     Output(component_id='hr-analytic', component_property='figure'),
     Output(component_id='second-selection', component_property='options')
     ],

    [Input(component_id='database', component_property='data'),
     Input(component_id='first-dpdw', component_property='value'),
     Input(component_id='second-dpdw', component_property='value'),
     Input(component_id='first-dpn-dpdw', component_property='value'),
     Input(component_id='second-dpn-dpdw', component_property='value'),
     Input(component_id='first-selection', component_property='value')],
    prevent_initial_call=True
)
def my_func(database, first_dpdw, second_dpdw, first_dpn_dpdw, second_dpn_dpdw, first_selection):
    engine = create_engine(
        f'postgresql://{db_info["USERNAME"]}:{db_info["PWD"]}@{db_info["HOSTNAME"]}:{db_info["PORT_ID"]}/{database}')

    df_demployee = pd.read_sql('dEmployee', engine, parse_dates=[
        'dob', 'doj', 'confirmation_date', 'last_increment', 'last_rejoin', 'termination_date'])

    df_demployee['age'] = df_demployee['dob'].apply(
        lambda x: relativedelta(current_date, x).years)
    df_demployee['age_group'] = df_demployee['age'].apply(age_bracket)
    df_demployee['service'] = df_demployee['doj'].apply(
        lambda x: relativedelta(current_date, x).years)
    df_demployee['service_period'] = df_demployee['service'].apply(
        service_bracket)
    existing_emp_filt = (~df_demployee['termination_date'].notna()) | (df_demployee['termination_date'] > current_date)

    df_demployee = df_demployee.loc[existing_emp_filt]

    # create a subset from the df_dEmployees which has only two columns [first_dropdown and second dropdown]
    df_graph = df_demployee[[first_dpdw, second_dpdw]]
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
    filtered_first = df_demployee.loc[df_demployee[first_dpdw].isin(
        first_dpn_dpdw)]

    return [
        [{'label': i.title(), 'value': i}
         for i in sorted(df_demployee[first_dpdw].unique())],
        [{'label': v, 'value': k}
         for v, k in filters_lists.items() if k != first_dpdw],
        [{'label': j.title(), 'value': j}
         for j in sorted(filtered_first[second_dpdw].unique())],
        fig,
        [{'label': i.upper(), 'value': i}
         for i in sorted(df_demployee[first_selection].unique())]
    ]


@callback(
    Output(component_id='second-selection', component_property='value'),
    Input(component_id='second-selection', component_property='options')
)
def set_values(selection):
    return [x['value'] for x in selection]


@callback(
    Output(component_id='staff-movement', component_property='children'),
    [Input(component_id='database', component_property='data'),
     Input(component_id='first-selection', component_property='value'),
     Input(component_id='second-selection', component_property='value')]
)
def update_emp_table(database, primary, secondary):
    if len(secondary) == 0:
        return dash.no_update
    else:
        engine = create_engine(
            f'postgresql://{db_info["USERNAME"]}:{db_info["PWD"]}@{db_info["HOSTNAME"]}:{db_info["PORT_ID"]}/{database}')

        df_demployee = pd.read_sql('dEmployee', engine, parse_dates=[
            'dob', 'doj', 'confirmation_date', 'last_increment', 'last_rejoin', 'termination_date'])

        df_demployee['age'] = df_demployee['dob'].apply(
            lambda x: relativedelta(current_date, x).years)
        df_demployee['age_group'] = df_demployee['age'].apply(age_bracket)
        df_demployee['service'] = df_demployee['doj'].apply(
            lambda x: relativedelta(current_date, x).years)
        df_demployee['service_period'] = df_demployee['service'].apply(
            service_bracket)

        filt_emp_start = ((df_demployee['doj'] < start_date) & ((~df_demployee['termination_date'].notna()) |
                                                                (df_demployee['termination_date'] >= start_date)) &
                          (df_demployee[primary].isin(secondary)))

        emp_start: int = len(df_demployee.loc[filt_emp_start]['emp_id'].unique())

        filt_additions = (df_demployee['doj'] >= start_date) & (df_demployee['doj'] <= current_date) & (df_demployee[primary].isin(secondary))

        emp_additions: int = len(df_demployee.loc[filt_additions]['emp_id'].unique())

        filt_terminations = (df_demployee['termination_date'] >= start_date) & (
                df_demployee['termination_date'] <= current_date) & (df_demployee[primary].isin(secondary))

        emp_terminations: int = len(df_demployee.loc[filt_terminations]['emp_id'].unique())

        emp_movement_data = pd.DataFrame(
            {
                "Description": ['No of staff at the start', '[+] No of staff joined', '[-] No of staff resigned',
                                'No of staff at the end'],
                "# Staff": [emp_start, emp_additions, emp_terminations * -1,
                            (emp_start + emp_additions - emp_terminations)],
            }
        )

        emp_movement = dbc.Table.from_dataframe(emp_movement_data, striped=True, bordered=True, hover=True)

        return emp_movement
