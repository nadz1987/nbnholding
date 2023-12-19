import dash
import dash_bootstrap_components as dbc
from dash import dcc,html

dash.register_page(__name__,external_stylesheets=[dbc.themes.PULSE])

layout = html.Div(
    [
        dcc.Markdown('# This is Operations Page : COMING SOON!!')
    ]
)