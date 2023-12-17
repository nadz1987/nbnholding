from datetime import datetime as dt
from datetime import timedelta
import dash
import dash_bootstrap_components as dbc
from data import time_series_data, db_info, fin_tiles_values, company_info, months
from dash import dcc, html, callback, Output, Input, dash_table, State
import pandas as pd
from sqlalchemy import create_engine, exc
import plotly.express as px
from dateutil.relativedelta import relativedelta


dash.register_page(__name__, external_stylesheets=[dbc.themes.PULSE])

row_one = dbc.Row(
    children=[
        dbc.Col(
            children=[
                html.H3('SELECT CUSTOMER',
                        className='text-center text-primary mb-4'),
            ], width={'size': 3}
        ),
        dbc.Col(
            children=[
                dcc.Dropdown(
                    id='cust-select',
                    multi=False,
                    placeholder='Please select a customer',
                    options=[],
                    clearable=False
                )
            ], width={'size': 6}
        )
    ]
)

row_two = html.Div(
    children=[
        dbc.Row(
            children=[
                dbc.Col(html.H6('Customer since:'), width=3),
                dbc.Col(html.H6(children=[], id='cus-since'), width=1),
                dbc.Col(html.H6('Highest Sales:'), width=3),
                dbc.Col(html.H6(children=[], id='highest-sales'), width=1),
                dbc.Col(html.H6('Highest GP:'), width=3),
                dbc.Col(html.H6(children=[], id='highest-gp'), width=1),
            ]
        ),
        dbc.Row(
            children=[
                dbc.Col(html.H6('Total GP Made:'), width=3),
                dbc.Col(html.H6(children=[], id='total-gp'), width=1),
                dbc.Tooltip('GP made from 2023 onward',
                            target='total-gp',
                            placement='top'),
                dbc.Col(html.H6('Total Sales Made:'), width=3),
                dbc.Col(html.H6(children=[], id='total-sales'), width=1),
                dbc.Col(html.H6('DSO:'), width=3),
                dbc.Col(html.H6(children=[], id='dso'), width=1),
            ]
        ),
        dbc.Row(
            children=[

                dbc.Col(html.H6('Sales Person(s):'), width=3),
                dbc.Col(html.H6(children=[], id='sales-person'), width=1),
                dbc.Col(html.H6('Closing Bal:'), width=3),
                dbc.Col(html.H6(children=[], id='clsoing-bal'), width=1),
            ]
        ),
        dbc.Row(
            children=[
                dbc.Col(html.H6('Last Invoice Value & Date:'), width=3),
                dbc.Col(html.H6(children=[], id='last-inv'), width=1),
                dbc.Col(html.H6('No of Pending Orders & Value:'), width=3),
                dbc.Col(html.H6(children=[],
                        id='pending-orders'), width=1),
                dbc.Col(html.H6('Last Payment Received:'), width=3),
                dbc.Col(html.H6(children=[],
                        id='last-payment'), width=1),
            ]
        )
    ]
)
modal_total_customers = html.Div(
    children=[
        dbc.Button("i", color="info",
                   className="me-1", size='sm', id='btn-total-customers-open'),
        dbc.Modal(
            children=[
                dbc.ModalHeader('Total Customers Served'),
                dbc.ModalBody(html.Div(
                    children=[], id='modal-total-customers-tbl'
                )),
                dbc.ModalFooter(
                    dbc.Button('Close', id='btn-total-customers-close',
                               className='ml-auto')
                )
            ],
            id='modal-total-customers',
            is_open=False,
            size='xl',
            backdrop=True,
            scrollable=True,
            centered=True,
            fade=True
        )
    ]
)

modal_new_customers = html.Div(
    children=[
        dbc.Button("i", color="info",
                   className="me-1", size='sm', id='btn-new-customers-open'),
        dbc.Modal(
            children=[
                dbc.ModalHeader('New Customers Added'),
                dbc.ModalBody(html.Div(
                    children=[], id='modal-new-customers-tbl'
                )),
                dbc.ModalFooter(
                    dbc.Button('Close', id='btn-new-customers-close',
                               className='ml-auto')
                )
            ],
            id='modal-new-customers',
            is_open=False,
            size='xl',
            backdrop=True,
            scrollable=True,
            centered=True,
            fade=True
        )
    ]
)

modal_inactive_customers = html.Div(
    children=[
        dbc.Button("i", color="info",
                   className="me-1", size='sm', id='btn-inactive-customers-open'),
        dbc.Modal(
            children=[
                dbc.ModalHeader('Inactive Customers'),
                dbc.ModalBody(html.Div(
                    children=[], id='modal-inactive-customers-tbl'
                )),
                dbc.ModalFooter(
                    dbc.Button('Close', id='btn-inactive-customers-close',
                               className='ml-auto')
                )
            ],
            id='modal-inactive-customers',
            is_open=False,
            size='xl',
            backdrop=True,
            scrollable=True,
            centered=True,
            fade=True
        )
    ]
)

row_three = dbc.Row(
    children=[
        dbc.Col(
            [
                dcc.Dropdown(
                    options=[
                        {'label': i, 'value': i} for i in time_series_data
                    ],
                    value='Current Month',
                    id='time-series',
                    className='mt-1',
                    optionHeight=35,
                    clearable=False
                ),
                html.Br(),
                html.Div(
                    children=[

                        html.H6(children=[], id='total-customers'),
                        modal_total_customers
                    ], className="d-flex mb-1"
                ),
                html.Div(
                    children=[

                        html.H6(children=[], id='new-customers'),
                        modal_new_customers
                    ], className="d-flex mb-1"
                ),
                html.Div(
                    children=[

                        html.H6(children=[], id='inactive-customers'),
                        modal_inactive_customers
                    ], className="d-flex mb-1"
                ),
            ], width={'size': 2}

        ),
        dbc.Col(
            children=[
                dbc.Card(
                    html.Div(children=[
                        html.H4('SALES'),
                        html.Hr(),
                        html.H4(children=[], id='period-sales'),
                        html.H5
                        (
                            children=[], className='', id='sales-pct-delta'
                        ),
                        html.H6(children=[], id='pre-period-sales')
                    ], className='', id='sales-tile'), className='text-center text-nowrap my-2 p-2'

                )
            ]
        ),
        dbc.Col(
            children=[
                dbc.Card(
                    html.Div(children=[
                        html.H4('GP'),
                        html.Hr(),
                        html.H4(children=[], id='period-gp'),
                        html.H5
                        (
                            children=[], className='', id='gp-pct-delta'
                        ),
                        html.H6(children=[], id='pre-period-gp')
                    ], className='', id='gp-tile'), className='text-center text-nowrap my-2 p-2'

                )
            ]
        ),
        dbc.Col(
            children=[
                dbc.Card(
                    html.Div(children=[
                        html.H4('COLLECTION'),
                        html.Hr(),
                        html.H4(children=[], id='period-col'),
                        html.H5
                        (
                            children=[], className='', id='pre-col-delta'
                        ),
                        html.H6(children=[], id='previous-col')
                    ], className='', id='collection-tile'), className='text-center text-nowrap my-2 p-2'

                )
            ]
        ),
        html.Hr()
    ]
)

row_four = dbc.Row(
    children=[
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        html.H5('TOP 5 CUSTOMERS',
                                className='text-center text-primary mb-4'),
                        html.Div(children=[], id='top-fivecust')
                    ], width=5
                ),
                dbc.Col(
                    children=[
                        html.H5('SALES PERSON ACHIEVMENT',
                                className='text-center text-primary mb-4'),
                        dcc.Graph(id='sales-achievement')
                    ], width=7
                )
            ]
        )
    ]
)

row_five = dbc.Row(
    children=[
        dbc.Col(
            children=[
                html.H5('REVENUE SALES PERSON WISE',
                        className='text-center text-primary mb-4'),
                dcc.Graph(id='rev-salesperson', figure={})
            ], width=8
        ),
        dbc.Col(
            children=[
                html.H5('YTD', className='text-center text-primary mb-4'),
                dcc.Graph(id='rev-salesperson-ytd', figure={})
            ], width=4
        )
    ]
)

row_six = dbc.Row(
    children=[
        dbc.Col(
            children=[
                html.H5('REVENUE NEW/EXISTING',
                        className='text-center text-primary mb-4'),
                dcc.Graph(id='rev-new-existing', figure={})
            ], width=8
        ),
        dbc.Col(
            children=[
                html.H5('NEW CUSTOMERS',
                        className='text-center text-primary mb-4'),
                dcc.Graph(id='rev-new-existing-ytd', figure={})
            ], width=4
        )
    ]
)

row_seven = dbc.Row(
    children=[
        dbc.Col(
            children=[
                html.H5('REVENUE INTERNAL/EXTERNAL',
                        className='text-center text-primary mb-4'),
                dcc.Graph(id='rev-internal-external', figure={})
            ], width=8
        ),
        dbc.Col(
            children=[
                html.H5('YTD', className='text-center text-primary mb-4'),
                dcc.Graph(id='rev-internal-external-ytd', figure={})
            ], width=4
        )
    ]
)

row_eight = dbc.Row(
    children=[
        dbc.Col(
            children=[
                html.H5('REVENUE GROSS/NET',
                        className='text-center text-primary mb-4'),
                dcc.Graph(id='rev-gross-net', figure={})
            ], width=8
        ),
        dbc.Col(
            children=[
                html.H5('YTD', className='text-center text-primary mb-4'),
                dcc.Graph(id='rev-gross-net-ytd', figure={})
            ], width=4
        )
    ], style={'display': 'block'}, id='row-eight'
)

row_nine = dbc.Row(
    children=[
        dbc.Col(
            children=[
                html.H5('COLLECTION INTERNAL/EXTENAL',
                        className='text-center text-primary mb-4'),
                dcc.Graph(id='col-internal-external', figure={})
            ], width=8
        ),
        dbc.Col(
            children=[
                html.H5('YTD', className='text-center text-primary mb-4'),
                dcc.Graph(id='col-int-ext-ytd', figure={})
            ], width=4
        )
    ]
)

row_ten = html.Div(
    children=[
        dcc.Dropdown(
            id='rev_type_select',
            multi=False,
            placeholder='Please select a report',
            options=[],
            clearable=False,
            value='Manpower Revenue'
        ),
        html.Hr(),
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        html.H5('ACTUAL VS BUDGETED REVENUE',
                                className='text-center text-primary mb-4 fw-bold'),
                        dcc.Graph(id='act-vs-bud-rev', figure={})
                    ], width=8
                ),
                dbc.Col(
                    children=[
                        html.H5(
                            'YTD', className='text-center text-primary mb-4'),
                        dcc.Graph(id='act-vs-bdt-ytd', figure={})
                    ], width=4
                )
            ]
        )
    ]
)


layout = html.Div(
    dcc.Loading(children=[row_one,
                          html.Hr(),
                          row_two,
                          html.Hr(),
                          row_three,
                          html.Hr(),
                          row_four,
                          html.Hr(),
                          row_five,
                          html.Hr(),
                          row_six,
                          html.Hr(),
                          row_seven,
                          html.Hr(),
                          row_eight,
                          html.Hr(),
                          row_nine,
                          html.Hr(),
                          row_ten], color='#119DFF', type='dot', fullscreen=True)
)


@callback(
    [Output(component_id='cust-select', component_property='options'),
     Output(component_id='cus-since', component_property='children'),
     Output(component_id='highest-sales', component_property='children'),
     Output(component_id='total-sales', component_property='children'),
     Output(component_id='clsoing-bal', component_property='children'),
     Output(component_id='last-inv', component_property='children'),
     Output(component_id='last-payment', component_property='children'),
     Output(component_id='pending-orders', component_property='children'),
     Output(component_id='total-customers', component_property='children'),
     Output(component_id='new-customers', component_property='children'),
     Output(component_id='inactive-customers', component_property='children'),
     Output(component_id='top-fivecust', component_property='children'),
     Output(component_id='rev-salesperson', component_property='figure'),
     Output(component_id='rev-salesperson-ytd', component_property='figure'),
     Output(component_id='rev-new-existing', component_property='figure'),
     Output(component_id='period-sales', component_property='children'),
     Output(component_id='period-col', component_property='children'),
     Output(component_id='pre-period-sales', component_property='children'),
     Output(component_id='sales-pct-delta', component_property='children'),
     Output(component_id='previous-col', component_property='children'),
     Output(component_id='pre-col-delta', component_property='children'),
     Output(component_id='rev-internal-external', component_property='figure'),
     Output(component_id='rev-internal-external-ytd',
            component_property='figure'),
     Output(component_id='row-eight', component_property='style'),
     Output(component_id='col-internal-external', component_property='figure'),
     Output(component_id='col-int-ext-ytd', component_property='figure'),
     Output(component_id='total-gp', component_property='children'),
     Output(component_id='period-gp', component_property='children'),
     Output(component_id='pre-period-gp', component_property='children'),
     Output(component_id='gp-pct-delta', component_property='children'),
     Output(component_id='sales-person', component_property='children'),
     Output(component_id='sales-pct-delta', component_property='className'),
     Output(component_id='sales-tile', component_property='className'),
     Output(component_id='modal-total-customers',
            component_property='is_open'),
     Output(component_id='modal-new-customers', component_property='is_open'),
     Output(component_id='modal-inactive-customers',
            component_property='is_open'),
     Output(component_id='pre-col-delta', component_property='className'),
     Output(component_id='collection-tile', component_property='className'),
     Output(component_id='gp-pct-delta', component_property='className'),
     Output(component_id='gp-tile', component_property='className'),
     Output(component_id='highest-gp', component_property='children'),
     Output(component_id='rev-new-existing-ytd', component_property='figure'),
     Output(component_id='rev_type_select', component_property='options')
     ],
    [
        Input(component_id='end-date', component_property='data'),
        Input(component_id='database', component_property='data'),
        Input(component_id='cust-select', component_property='value'),
        Input(component_id='time-series', component_property='value'),
        Input(component_id='btn-total-customers-open',
              component_property='n_clicks'),
        Input(component_id='btn-total-customers-close',
              component_property='n_clicks'),
        Input(component_id='btn-new-customers-open',
              component_property='n_clicks'),
        Input(component_id='btn-new-customers-close',
              component_property='n_clicks'),
        Input(component_id='btn-inactive-customers-open',
              component_property='n_clicks'),
        Input(component_id='btn-inactive-customers-close',
              component_property='n_clicks'),

    ],
    [State(component_id='modal-total-customers', component_property='is_open'),
     State(component_id='modal-new-customers', component_property='is_open'),
     State(component_id='modal-inactive-customers',
           component_property='is_open')
     ],
    prevent_initial_call=True
)
def data_output(end_date, database, cust_select, time_freq, b1, b2, is_open_1, b3, b4, is_open_2, b5, b6, is_open_3):

    engine = create_engine(
        f'postgresql://{db_info["USERNAME"]}:{db_info["PWD"]}@{db_info["HOSTNAME"]}:{db_info["PORT_ID"]}/{database}')
    try:
        df_dcoa_adler = pd.read_sql('dCoAAdler', engine)
        df_djobs = pd.read_sql('dJobs', engine)
        df_fGl = pd.read_sql('fGL', engine)
        df_dEmployee = pd.read_sql('dEmployee', engine)
        df_dCustomers = pd.read_sql('dCustomers', engine)
    except exc.ProgrammingError:
        pass

    # if any of above database are not avialable, then it will throw nameerror. need to fix !!!

    df_fGl['net'] = df_fGl['credit'] - df_fGl['debit']
    df_fGl['period'] = df_fGl['voucher_date'].dt.strftime(
        date_format='%m')  # return date as 01-12 i.e 2023-07-24 --> 07
    cy_end_date = dt.strptime(end_date, '%Y-%m-%d')  # 2023-08-31
    cy_m_begin_date = cy_end_date.replace(day=1)  # 2023-08-01
    cy_begin_date = cy_m_begin_date.replace(month=1)  # 2023-01-01
    cy_pm_end_date = cy_m_begin_date - timedelta(days=1)  # 2023-07-31 ok
    cy_pm_begin_date = cy_pm_end_date.replace(day=1)  # 2023-07-01 ok
    py_end_date = cy_end_date - relativedelta(years=1)  # 2022-08-31
    py_begin_date = cy_begin_date - relativedelta(years=1)  # 2022-01-01 ok
    py_m_begin_date = py_end_date.replace(day=1)  # 2022-08-01 ok
    inactive_end_date = cy_m_begin_date - timedelta(days=120)  # 2023-04-01 ok

    time_series = [
        {'freq': 'Current Month',
         'start_date': cy_m_begin_date,  # 2023-08-01
         'end_date': cy_end_date,  # 2023-08-31
         'comparative_start': cy_pm_begin_date,  # 2023-07-01 ok
         'comparative_end': cy_pm_end_date},  # 2023-07-31 ok
        {'freq': 'Previous Year Same Month',
         'start_date': py_m_begin_date,  # 2022-08-01 ok
         'end_date': py_end_date,  # 2022-08-31
         'comparative_start': cy_m_begin_date,  # 2023-08-01
         'comparative_end': cy_end_date},  # 2023-08-31
        {'freq': 'YTD Current Year',
         'start_date': cy_begin_date,  # 2023-01-01
         'end_date': cy_end_date,  # 2023-08-31
         'comparative_start': py_begin_date,  # 2022-01-01 ok
         'comparative_end': py_end_date}  # 2022-08-31
    ]

    start_date = [i['start_date']
                  for i in time_series if i['freq'] == time_freq][0]
    end_date = [i['end_date']
                for i in time_series if i['freq'] == time_freq][0]
    comparative_start = [i['comparative_start']
                         for i in time_series if i['freq'] == time_freq][0]
    comparative_end = [i['comparative_end']
                       for i in time_series if i['freq'] == time_freq][0]

    df_merged = pd.merge(left=df_fGl, right=df_dcoa_adler,
                         on='ledger_code', how='left')
    rev_types = ([i['filt']
                 for i in fin_tiles_values if i['value'] == 'Revenue'][0])  # get a list of revenue types
    # filter the dataset by the selected voucher type, so it will only include revenue related ledgers
    filt = df_merged['first_level'].isin(rev_types)
    df_merged = df_merged.loc[filt]
    v_types = list([i['data']['voucher_types'].keys()
                   for i in company_info if i['data']['database'] == database][0])  # get the list of voucher types. this will return list of voucher types

    def order_id(row):
        for v_type in v_types:
            split_pos = [i['data']['voucher_types'][v_type]
                         for i in company_info if i['data']['database'] == database][0]  # this will return job_id split position for each voucher type
            if row['transaction_type'] == v_type:
                try:
                    # return job_number from transaction_type column
                    return row['job_number'].split('-')[split_pos].strip()
                except AttributeError:
                    pass

    df_merged['job_number'] = df_merged.apply(order_id, axis=1)

    def extract_part(text):
        pattern = r'^(.*?)-Rev.*$'
        match = pd.Series(text).str.extract(pat=pattern, expand=False)
        return match[0] if match is not None and pd.notna(match[0]) else text

    df_djobs['job_number'] = df_djobs['job_number'].apply(extract_part)

    df_merged = pd.merge(left=df_merged[['bussiness_unit_name', 'cost_center', 'voucher_date', 'voucher_number', 'credit', 'debit',
                         'ledger_name', 'forth_level', 'third_level', 'second_level', 'first_level', 'job_number', 'net', 'period', 'transaction_type', 'ledger_code']],
                         right=df_djobs, on='job_number', how='left')
    df_merged = pd.merge(left=df_merged, right=df_dCustomers[[
                         'customer_code', 'cus_name']], on='customer_code', how='left')
    df_merged = pd.merge(left=df_merged, right=df_dEmployee[['emp_id', 'emp_name', 'leave_policy', 'travel_cost', 'ba', 'hra', 'tra', 'ma', 'oa', 'pda']],
                         on='emp_id', how='left')

    highest_sales = df_merged.loc[df_merged['customer_code'] == cust_select, [
        'voucher_number', 'net']]
    # to get the unique list of sales person for selected customer
    salesman_list: list = [i.split(' ')[0].title(
    ) for i in df_merged.loc[df_merged['customer_code'] == cust_select, 'emp_name'].unique() if isinstance(i, str)]

    salesman_list_formatted = ', '.join(map(str, salesman_list))

    highest_sales: float = highest_sales.groupby(by=['voucher_number'])[
        'net'].sum().max()
    total_sales: float = df_merged.loc[df_merged['customer_code']
                                       == cust_select, 'net'].sum()
    cust_ledger: list = list(
        df_dCustomers.loc[df_dCustomers['customer_code'] == cust_select, 'ledger_code'])  # list all the ledger account each customer_code has
    clsoing_bal: float = df_fGl.loc[df_fGl['ledger_code'].isin(
        cust_ledger), 'net'].sum() * -1

    last_col_date_filt = (df_fGl['transaction_type'] == 'Receipt') & (
        df_fGl['ledger_code'].isin(cust_ledger))  # create a filter which show receipts from a given customer for whole period
    col_filt = (df_fGl['transaction_type'] == 'Receipt') & (df_fGl['ledger_code'].isin(list(df_dCustomers['ledger_code']))) & (
        df_fGl['voucher_date'] >= cy_begin_date) & (df_fGl['voucher_date'] <= cy_end_date)  # for YTD period this list all the receips from customers
    # filter the df_fGl only for receipts from customers for YTD period
    col_report = df_fGl.loc[col_filt, ['ledger_code', 'net', 'period']]
    col_report = pd.merge(left=col_report, right=df_dcoa_adler[[
                          'ledger_code', 'second_level']], on='ledger_code', how='left')
    col_report.dropna(inplace=True)

    try:
        cus_since = df_merged.loc[df_merged['customer_code']
                                  == cust_select, 'voucher_date'].min().strftime("%Y-%m-%d")
        last_inv_date = df_merged.loc[df_merged['customer_code']
                                      == cust_select, 'voucher_date'].max().strftime("%Y-%m-%d")
        last_col_date = df_fGl.loc[last_col_date_filt,
                                   'voucher_date'].max().strftime("%Y-%m-%d")
    except:
        last_inv_date = 'Not Available'
        cus_since = 'Not Available'
        last_col_date = 'Not Available'

    # new_df created as otherwise AssertionError
    new_df = df_fGl.loc[last_col_date_filt]
    last_col_amt_filt = new_df['voucher_date'] == df_fGl.loc[last_col_date_filt,
                                                             'voucher_date'].max()

    last_col_amt: float = new_df.loc[last_col_amt_filt, 'net'].max()

    last_inv_amt_filt = (df_merged['customer_code'] == cust_select) & (
        df_merged['voucher_date'] == last_inv_date)

    try:
        last_inv_amt: float = df_merged.loc[last_inv_amt_filt, 'net'].max()
    except IndexError:
        pass

    pending_jobs = None
    highest_gp = None
    if database in ['elite_security', 'premium']:
        pending_jobs = 'Not Applicable'
        highest_gp = 'Not Applicable'
        visibility_state = {'display': 'none'}
        df_fGlJobs = pd.read_sql('fGlJob', engine)
        df_exp_allo = pd.read_sql('exp_allocation', engine)

    period_customers_filt = (df_merged['voucher_date'] >= start_date) & (
        df_merged['voucher_date'] <= end_date)
    period_customers = df_merged.loc[period_customers_filt,
                                     'customer_code'].unique().tolist()

    period_customers_number: int = sum(
        1 for i in period_customers if isinstance(i, str))

    total_customers_filt = (df_merged['voucher_date'] >= df_merged['voucher_date'].min()) & (
        df_merged['voucher_date'] <= cy_pm_end_date)

    total_customers = df_merged.loc[total_customers_filt,
                                    'customer_code'].unique().tolist()

    new_customers = len(
        [item for item in period_customers if item not in total_customers])

    four_months_customers = len(
        df_merged.loc[df_merged['voucher_date'] >= inactive_end_date, 'customer_code'].unique())
    one_year_customers = len(
        df_merged.loc[df_merged['voucher_date'] >= py_m_begin_date, 'customer_code'].unique())
    inactive_customers = one_year_customers - four_months_customers

    period_sales_filt = (df_merged['voucher_date'] >= start_date) & (
        df_merged['voucher_date'] <= end_date) & (df_merged['customer_code'] == cust_select)
    period_sales: float = df_merged.loc[period_sales_filt, 'net'].sum()

    previous_period_sales_filt = (df_merged['voucher_date'] >= comparative_start) & (
        df_merged['voucher_date'] <= comparative_end) & (df_merged['customer_code'] == cust_select)
    previous_period_sales: float = df_merged.loc[previous_period_sales_filt, 'net'].sum(
    )

    try:
        sales_pct_delta: float = (period_sales/previous_period_sales-1) * 100
        color_sales_pct_delta = "text-danger fw-bold" if sales_pct_delta < 0 else "text-success fw-bold"
        color_sales_border = "border-danger border-start border-5" if sales_pct_delta < 0 else "border-success border-start border-5"
    except ZeroDivisionError:
        sales_pct_delta = 0
        color_sales_pct_delta = "text-success"
        color_sales_border = "border-success border-start border-5"

    period_col_filt = (df_fGl['voucher_date'] >= start_date) & (df_fGl['voucher_date'] <= end_date) & (
        df_fGl['ledger_code'].isin(cust_ledger)) & (df_fGl['transaction_type'] == 'Receipt')
    period_col: float = df_fGl.loc[period_col_filt, 'net'].sum()

    previous_col_filt = (df_fGl['voucher_date'] >= comparative_start) & (df_fGl['voucher_date'] <= comparative_end) & (
        df_fGl['ledger_code'].isin(cust_ledger)) & (df_fGl['transaction_type'] == 'Receipt')
    previous_col: float = df_fGl.loc[previous_col_filt, 'net'].sum()

    try:
        col_pct_delta: float = (period_col / previous_col - 1) * 100
        color_col_pct_delta = "text-danger fw-bold" if col_pct_delta < 0 else "text-success fw-bold"
        color_col_border = "border-danger border-start border-5" if col_pct_delta < 0 else "border-success border-start border-5"
    except ZeroDivisionError:
        col_pct_delta = 0
        color_col_pct_delta = "text-success"
        color_col_border = "border-success border-start border-5"

    top_five_cust_df = df_merged.loc[period_customers_filt, [
        'cus_name', 'net']]
    top_five_cust = top_five_cust_df.groupby(by='cus_name')['net'].sum()
    top_five_cust = top_five_cust.sort_values(ascending=False).head(5)
    top_five_report = dash_table.DataTable(
        id='table',
        columns=[{'name': 'Customer Name', 'id': 'cus_name'},
                 {'name': 'Value', 'id': 'net'}],
        data=[
            {'cus_name': index, 'net': f'QAR :{value:,.0f}'} for index, value in top_five_cust.items()
        ],
        style_cell={'textAlign': 'left'},
        style_header={'backgroundColor': 'paleturquoise'},
        style_data={'backgroundColor': 'lavender'}
    )
    salesman_df_filt = (df_merged['voucher_date'] >= cy_begin_date) & (
        df_merged['voucher_date'] <= cy_end_date)
    salesman_df_final = df_merged.loc[salesman_df_filt]
    salesman_df_final = salesman_df_final.groupby(['emp_name', 'period'],
                                                  as_index=False)['net'].sum()

    bar_chart_rev_monthwise_salesman = px.bar(
        data_frame=salesman_df_final,
        x='period',
        y='net',
        barmode='stack',
        color='emp_name',
        labels={'period': 'Months', 'net': 'QAR Value',
                'emp_name': 'Employee Name'},
    )
    bar_chart_rev_monthwise_salesman.update_xaxes(labelalias=months)

    # to change the legend labels as per the 'graph_legends' dictionery
    bar_chart_rev_monthwise_salesman.for_each_trace(
        lambda t: t.update(name=t.name.split(' ')[0].title()))

    salesman_df_final = df_merged.groupby(by=['emp_name'],
                                          as_index=False)['net'].sum()
    pie_chart_rev_ytd_salesman = px.pie(
        data_frame=salesman_df_final,
        names=salesman_df_final['emp_name'],
        values=salesman_df_final['net'],
        hole=0.3
    )

    pie_chart_rev_ytd_salesman.update_traces(
        labels=[label.split(' ')[0].title() for label in pie_chart_rev_ytd_salesman.data[0]['labels']])

    df_merged['voucher_date'] = pd.to_datetime(df_merged['voucher_date'])
    df_merged['month_year'] = df_merged['voucher_date'].dt.to_period(
        freq='M')  # return 2021-01
    df_merged['customer_type'] = df_merged.groupby(
        'customer_code')['voucher_date'].transform('min')  # to get the minimum voucher_date for each customer_code group
    # Return true if voucher_date is equeal to minimum date (New Customer) other wise false (Existing )
    df_merged['customer_type'] = df_merged['voucher_date'] == df_merged['customer_type']
    df_merged['month_year'] = df_merged['month_year'].astype(str)
    result = df_merged.groupby(['month_year', 'customer_type'], as_index=False)[
        'net'].sum()
    bar_chart_rev_new_existing = px.bar(data_frame=result,
                                        x='month_year',
                                        y='net',
                                        color='customer_type',
                                        barmode='stack',
                                        labels={'month_year': 'Period', 'net': 'QAR Value', 'customer_type': 'Customer Type'})

    bar_chart_rev_new_existing.for_each_trace(
        lambda t: t.update(name={'False': 'Existing', 'True': 'New'}[t.name]))

    cy_cust_filt = (df_merged['voucher_date'] >= cy_begin_date) & (
        df_merged['voucher_date'] <= cy_end_date) & (df_merged['first_level'].isin(rev_types))

    cy_cust_list: list = df_merged.loc[cy_cust_filt]['customer_code'].unique(
    ).tolist()

    min_date = df_merged['voucher_date'].min()

    till_cy_cust_filt = (df_merged['voucher_date'] >= min_date) & (
        df_merged['voucher_date'] < cy_begin_date) & (df_merged['first_level'].isin(rev_types))

    till_cy_cust_list: list = df_merged.loc[till_cy_cust_filt]['customer_code'].unique(
    ).tolist()

    new_cy_cust = len([i for i in cy_cust_list if i not in till_cy_cust_list])

    cust_data = {'Category': ['New', 'Existing'],
                 'Count': [new_cy_cust, len(cy_cust_list)-new_cy_cust]}

    df_cust_data = pd.DataFrame(cust_data)

    fig_cust_data = px.pie(df_cust_data,
                           names='Category',
                           values='Count')
    # creating a new df for revenue source calculation
    source_cy_filt = (df_merged['voucher_date'] >= cy_begin_date) & (
        df_merged['voucher_date'] <= cy_end_date)
    sales_src_df = df_merged.loc[source_cy_filt]
    sales_src_df = pd.merge(left=sales_src_df[['net', 'period', 'customer_code']], right=df_dCustomers[[
                            'customer_code', 'ledger_code']], on='customer_code', how='left')
    sales_src_df = pd.merge(left=sales_src_df[['net', 'period', 'ledger_code']], right=df_dcoa_adler[[
                            'ledger_code', 'second_level']], on='ledger_code', how='left')  # to get the customer ledger code for a given customer code

    source_df_final = sales_src_df.groupby(['second_level', 'period'],
                                           as_index=False)['net'].sum()
    bar_chart_rev_monthwise_source = px.bar(
        data_frame=source_df_final,
        x='period',
        y='net',
        barmode='group',
        color='second_level',
        labels={'period': 'Period', 'net': 'QAR Value',
                'second_level': 'Source'}
    )

    bar_chart_rev_monthwise_source.update_xaxes(labelalias=months)

    bar_chart_rev_monthwise_source.for_each_trace(
        lambda t: t.update(name={'Due from Related Parties': 'In-House', 'Trade Receivables': 'Market'}[t.name]))

    source_df_final = sales_src_df.groupby(by=['second_level'],
                                           as_index=False)['net'].sum()
    pie_chart_rev_ytd_source = px.pie(
        data_frame=source_df_final,
        names=source_df_final['second_level'],
        values=source_df_final['net'],
        hole=0.3,
    )

    pie_chart_rev_ytd_source.update_traces(
        labels=[{'Due from Related Parties': 'In-House', 'Trade Receivables': 'Market'}[label] for label in pie_chart_rev_ytd_source.data[0]['labels']])

    col_period = col_report.groupby(['second_level', 'period'],
                                    as_index=False)['net'].sum()
    bar_chart_col_monthwise = px.bar(
        data_frame=col_period,
        x='period',
        y='net',
        barmode='group',
        color='second_level',
        labels={'period': 'Period', 'net': 'QAR Value',
                'second_level': 'Source'}
    )

    bar_chart_col_monthwise.update_xaxes(labelalias=months)
    bar_chart_col_monthwise.for_each_trace(
        lambda t: t.update(name={'Due from Related Parties': 'In-House', 'Trade Receivables': 'Market'}[t.name]))

    col_period = col_report.groupby(by=['second_level'],
                                    as_index=False)['net'].sum()
    pie_chart_col_ytd = px.pie(
        data_frame=col_period,
        names=col_period['second_level'],
        values=col_period['net'],
        hole=0.3,
    )

    pie_chart_col_ytd.update_traces(
        labels=[{'Due from Related Parties': 'In-House', 'Trade Receivables': 'Market'}[label] for label in pie_chart_col_ytd.data[0]['labels']])

    df_fGlJobs['job_number'] = df_fGlJobs.apply(order_id, axis=1)
    df_fGlJobs['net'] = df_fGlJobs['credit'] - df_fGlJobs['debit']
    df_GlJob_merged = pd.merge(left=df_fGlJobs[['ledger_code', 'voucher_date', 'net', 'job_number']], right=df_dcoa_adler[[
                               'ledger_code', 'first_level']], on='ledger_code', how='left')
    df_GlJob_merged = pd.merge(
        left=df_GlJob_merged, right=df_djobs, on='job_number', how='left')
    df_GlJob_merged = pd.merge(
        left=df_GlJob_merged, right=df_dCustomers[['customer_code', 'cus_name']], on='customer_code', how='left')

    # date is set to 2023-01-01 as expenses are available from that date onward
    rev_filt = (df_GlJob_merged['customer_code'] == cust_select) & (
        df_GlJob_merged['first_level'].isin(rev_types)) & (df_GlJob_merged['voucher_date'] >= dt(2023, 1, 1))

    job_revenue: float = df_GlJob_merged.loc[rev_filt, 'net'].sum()

    rev_filt_period = (df_GlJob_merged['customer_code'] == cust_select) & (df_GlJob_merged['voucher_date'] >= start_date) & (
        df_GlJob_merged['voucher_date'] <= end_date) & (df_GlJob_merged['first_level'].isin(rev_types))  # this will return a customer revenue for the selected period

    job_revenue_period: float = df_GlJob_merged.loc[rev_filt_period, 'net'].sum(
    )

    rev_filt_pre_period = (df_GlJob_merged['customer_code'] == cust_select) & (df_GlJob_merged['voucher_date'] >= comparative_start) & (
        df_GlJob_merged['voucher_date'] <= comparative_end) & (df_GlJob_merged['first_level'].isin(rev_types))  # this will return a customer revenue for the selected period

    job_revenue_pre_period: float = df_GlJob_merged.loc[rev_filt_pre_period, 'net'].sum(
    )

    df_exp_allo['net'] = df_exp_allo[['allocated', 'overtime',
                                      'fixed_bill', 'fixed_gen']].sum(axis=1)
    df_exp_allo.rename(columns={'job_id': 'job_number'}, inplace=True)
    df_exp_allo_merged = pd.merge(left=df_exp_allo[['job_number', 'cost_center', 'date', 'net']], right=df_djobs[[
                                  'job_number', 'customer_code', 'emp_id']], on='job_number', how='left')
    exp_filt = (df_exp_allo_merged['customer_code']
                == cust_select)  # This filter is wrong

    job_cost: float = df_exp_allo_merged.loc[exp_filt, 'net'].sum()

    exp_filt_period = (df_exp_allo_merged['customer_code'] == cust_select) & (
        df_exp_allo_merged['date'] >= start_date) & (df_exp_allo_merged['date'] <= end_date)

    job_cost_period: float = df_exp_allo_merged.loc[exp_filt_period, 'net'].sum(
    )

    exp_filt_pre_period = (df_exp_allo_merged['customer_code'] == cust_select) & (
        df_exp_allo_merged['date'] >= comparative_start) & (df_exp_allo_merged['date'] <= comparative_end)

    job_cost_pre_period: float = df_exp_allo_merged.loc[exp_filt_pre_period, 'net'].sum(
    )

    job_cost_period: float = df_exp_allo_merged.loc[exp_filt_period, 'net'].sum(
    )

    job_profit: float = job_revenue - job_cost

    job_profit_period: float = job_revenue_period - job_cost_period

    job__profit_pre_period: float = job_revenue_pre_period - job_cost_pre_period

    try:
        gp_pct_delta = (job_profit_period / job__profit_pre_period - 1) * 100
        color_gp_pct_delta = "text-danger fw-bold" if gp_pct_delta < 0 else "text-success fw-bold"
        color_gp_border = "border-danger border-start border-5" if gp_pct_delta < 0 else "border-success border-start border-5"
    except ZeroDivisionError:
        gp_pct_delta = 0
        color_gp_pct_delta = "text-success"
        color_gp_border = "border-success border-start border-5"

    if b1 or b2:
        is_open_1_state = not is_open_1
    else:
        is_open_1_state = is_open_1

    if b3 or b4:
        is_open_2_state = not is_open_2
    else:
        is_open_2_state = is_open_2

    if b5 or b6:
        is_open_3_state = not is_open_3
    else:
        is_open_3_state = is_open_3

    tbl_modal_total_customers = dash_table.DataTable(
        id='modal-total-customers-tbl',
        columns=[],
        data=[],
        style_cell={'textAlign': 'left'},
        style_header={'backgroundColor': 'paleturquoise'},
        style_data={'backgroundColor': 'lavender'}
    )

    tbl_modal_new_customers = dash_table.DataTable(
        id='modal-new-customers-tbl',
        columns=[],
        data=[],
        style_cell={'textAlign': 'left'},
        style_header={'backgroundColor': 'paleturquoise'},
        style_data={'backgroundColor': 'lavender'}
    )

    tbl_modal_inactive_customers = dash_table.DataTable(
        id='modal-inactive-customers-tbl',
        columns=[],
        data=[],
        style_cell={'textAlign': 'left'},
        style_header={'backgroundColor': 'paleturquoise'},
        style_data={'backgroundColor': 'lavender'}
    )

    new_gl_coa = pd.merge(left=df_fGl[['ledger_code', 'voucher_date']], right=df_dcoa_adler[[
                          'ledger_code', 'first_level']], on='ledger_code', how='inner')
    new_cust_list_filt = (new_gl_coa['first_level'].isin(rev_types)) & (
        new_gl_coa['voucher_date'] >= cy_begin_date) & (new_gl_coa['voucher_date'] <= cy_end_date)
    # to display the list of reports at actual vs budgeted graphs.
    new_cust_list = new_gl_coa.loc[new_cust_list_filt, 'first_level'].unique()

    return [[{'label': row['cus_name'], 'value': row['customer_code']} for index, row in df_dCustomers.iterrows()],
            cus_since,
            f'QAR {highest_sales:,.0f}',
            f'QAR {total_sales:,.0f}',
            f'QAR {clsoing_bal:,.0f}',
            f'QAR {last_inv_amt:,.0f} dt {last_inv_date}',
            f'QAR {last_col_amt:,.0f} dt {last_col_date}',
            pending_jobs,
            f'Total Customers Served : {period_customers_number} ',
            f'New Customers Added : {new_customers} ',
            f'Inactive Customers : {inactive_customers} ',
            top_five_report,
            bar_chart_rev_monthwise_salesman,
            pie_chart_rev_ytd_salesman,
            bar_chart_rev_new_existing,
            f'QAR {period_sales:,.0f}',
            f'QAR {period_col:,.0f}',
            f'QAR {previous_period_sales:,.0f}',
            f'{sales_pct_delta:,.0f} %',
            f'QAR {previous_col:,.0f}',
            f'{col_pct_delta:,.0f} %',
            bar_chart_rev_monthwise_source,
            pie_chart_rev_ytd_source,
            visibility_state,
            bar_chart_col_monthwise,
            pie_chart_col_ytd,
            f'QAR {job_profit:,.0f}',
            f'QAR {job_profit_period:,.0f}',
            f'QAR {job__profit_pre_period:,.0f}',
            f'{gp_pct_delta:,.0f} %',
            salesman_list_formatted,
            color_sales_pct_delta,
            color_sales_border,
            is_open_1_state,
            is_open_2_state,
            is_open_3_state,
            color_col_pct_delta,
            color_col_border,
            color_gp_pct_delta,
            color_gp_border,
            highest_gp,
            fig_cust_data,
            [{'label': x, 'value': x} for x in new_cust_list]
            ]


@callback(
    [Output(component_id='act-vs-bud-rev', component_property='figure'),
     Output(component_id='act-vs-bdt-ytd', component_property='figure')],
    [Input(component_id='end-date', component_property='data'),
        Input(component_id='database', component_property='data'),
        Input(component_id='rev_type_select', component_property='value')]
)
def budget_area(end_date, database, rev_type):
    engine = create_engine(
        f'postgresql://{db_info["USERNAME"]}:{db_info["PWD"]}@{db_info["HOSTNAME"]}:{db_info["PORT_ID"]}/{database}')

    df_dcoa_adler = pd.read_sql('dCoAAdler', engine)
    df_fGl = pd.read_sql('fGL', engine)
    df_budget = pd.read_sql('fBudget', engine)

    cy_end_date = dt.strptime(end_date, '%Y-%m-%d')  # 2023-08-31
    cy_begin_date = cy_end_date.replace(month=1, day=1)  # 2023-01-01

    rev_types = ([i['filt']
                 for i in fin_tiles_values if i['value'] == 'Revenue'][0])  # get a list of revenue types

    filtered_budget = df_budget.set_index(['ledger_code', 'fy'])
    filtered_budget = filtered_budget.stack().reset_index()
    filtered_budget.rename(
        columns={'level_2': 'month', 0: 'net'}, inplace=True)
    filtered_budget = pd.merge(right=filtered_budget, left=df_dcoa_adler[[
                               'ledger_code', 'forth_level']], on='ledger_code', how='inner')
    filtered_budget['net'] = filtered_budget.apply(
        lambda row: row['net'] * -1 if row['forth_level'] == 'Expenses' else row['net'], axis=1)
    filtered_budget['voucher_date'] = pd.to_datetime(
        filtered_budget['fy'].astype(str) + '-' + filtered_budget['month'] + '-01')
    filtered_budget['type'] = 'Budget'
    df_fGl['type'] = 'Actual'
    filtered_budget = filtered_budget[[
        'ledger_code', 'net', 'voucher_date', 'type']]
    df_fGl['net'] = df_fGl['credit'] - df_fGl['debit']
    filtered_budget = pd.concat(
        [filtered_budget, df_fGl[['ledger_code', 'voucher_date', 'net', 'type']]])
    budget_filter = (filtered_budget['voucher_date'] >= cy_begin_date) & (filtered_budget['net'] != 0) & (filtered_budget['voucher_date'] <= cy_end_date) & (
        filtered_budget['ledger_code'].isin(df_dcoa_adler.loc[df_dcoa_adler['first_level'].isin(rev_types)]['ledger_code'].tolist()))
    filtered_budget = filtered_budget.loc[budget_filter]
    filtered_budget['voucher_date'] = filtered_budget.apply(
        lambda row: row['voucher_date'] + relativedelta(day=31), axis=1)
    filtered_budget = filtered_budget.groupby(
        by=['ledger_code', 'voucher_date', 'type'], as_index=False)['net'].sum()
    filtered_budget = pd.merge(left=filtered_budget, right=df_dcoa_adler[[
                               'ledger_code', 'first_level']], on='ledger_code', how='inner')
    rev_typewise_filt = filtered_budget['first_level'] == rev_type
    rev_typewise_df = filtered_budget.loc[rev_typewise_filt]
    rev_typewise_df['period'] = rev_typewise_df['voucher_date'].dt.strftime(
        date_format='%m')

    act_vs_bud_bar = px.bar(
        data_frame=rev_typewise_df,
        x='period',
        y='net',
        barmode='group',
        color='type',
        template='simple_white',
        labels={'period': 'Period', 'net': 'QAR Value',
                'type': 'Type'}
    )
    act_vs_bud_bar.update_xaxes(labelalias=months)

    rev_typewise_ytd = filtered_budget.groupby(
        by=['type', 'first_level'], as_index=False)['net'].sum()

    act_vs_bud_ytd = px.bar(
        data_frame=rev_typewise_ytd,
        x='first_level',
        y='net',
        barmode='group',
        color='type',
        labels={'net': 'QAR Value', 'first_level': 'Type',
                'type': 'Type'}
    )
    act_vs_bud_ytd.update_xaxes(labelalias=months)

    return [act_vs_bud_bar,
            act_vs_bud_ytd]
    # rev_typewise_df.to_csv('my_file.csv',index=False)
