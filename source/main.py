# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from flask import request
import requests
import io
import datetime
from dash.dependencies import Input, Output
import dash  # (version 1.12.0)
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import traceback
from signalrcore.hub_connection_builder import HubConnectionBuilder
from signalrcore.protocol.messagepack_protocol import MessagepackProtocol


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

experiment_id = ""

def load_data():
    url = "https://telemetry-query-deloitte-eventinteractiondemo.platform.quix.ai/parameters/data"
    token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1qVTBRVE01TmtJNVJqSTNOVEpFUlVSRFF6WXdRVFF4TjBSRk56SkNNekpFUWpBNFFqazBSUSJ9.eyJodHRwczovL3F1aXguYWkvcm9sZXMiOiIiLCJodHRwczovL3F1aXguYWkvb3JnX2lkIjoiZGVsb2l0dGUiLCJpc3MiOiJodHRwczovL2xvZ2ljYWwtcGxhdGZvcm0uZXUuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfGU1OWQzZmQ1LWNjNTMtNGZmNi04MDEyLWU1ZDIxYjllMDhmYiIsImF1ZCI6WyJxdWl4IiwiaHR0cHM6Ly9sb2dpY2FsLXBsYXRmb3JtLmV1LmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE2MTcyODc2ODIsImV4cCI6MTYxOTg3OTY4MiwiYXpwIjoiMHptV2ZKZGtpdUdQaUpXeXBTQ0E4ckthVnZmUERLTEkiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwicGVybWlzc2lvbnMiOltdfQ.bEyV7OkZAljMZjie92TonnH3GVkpbMCeaCgu4RKyeHdMseq2CEtr0g9Czr_tAwAQIrUes-Ibuqhmvdx7wtMOHwOdDdA4u3uIyKfiJ2KPf4GY650jxeoX1mON2IiSTCR6JFxuBWnaayVjLL_hx4NUZpfBmcL9P7HX8kjrbtMnWzlB4VHHm8PhXeI006zupxu9alDws7pmO3gEWzIjtozUvS9V12f3r6ZHrkx_63iZTH7i6dv-gy0CkE_za9oNxgwdDV42wqalXf0I4ocFS1RHu2kYR9z_mGoWJrVHoaEn5iup6j9lmTDVOsasdFIseKlynUzldIAYqNJMxOdQwR0R_A"
    head = {'Authorization': 'Bearer {}'.format(token), 'Accept': "application/csv"}
    payload = {
        'from': 1617282074655142400,
        'to': 1617288750679790600,
        'numericParameters': [
            {
                'parameterName': 'word-count',
                'aggregationType': 'None'
            }
        ],
        'stringParameters': [],
        'streamIds': [
            'CocoaMQTT-816',
            'CocoaMQTT-816-words-counter'
        ],
        'groupBy': []
    }

    response = requests.post(url, headers=head, json=payload)

    panda_frame = pd.read_csv(io.StringIO(response.content.decode('utf-8')))

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(panda_frame)

    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    # print(panda_frame)
    if panda_frame.size > 0:
        print("Timestamp")
        panda_frame["Timestamp"] = panda_frame["Timestamp"].apply(lambda x: str(datetime.datetime.fromtimestamp(x / 1000000000)))
    return panda_frame


panda_frame = load_data()


app.layout = html.Div(children=[
    html.H1(children='Test dashboard'),
    html.Div(children='''
        Word count
    '''),
    dcc.Input(
            id="input",
            type="text"
    ),
    dcc.Graph(
        id='word-count',

    ),
    dcc.Interval(
        id='interval_component',
        interval=1000,
        n_intervals=0,
        
    ),
    html.Div(children='''
'''),
] + [html.Div(id="out-all-types")])


@app.callback(Output('word-count', 'figure'), [Input('interval_component', 'n_intervals')])
def update_data(n_intervals):
    try:
        data = load_data()

        scatter = go.Scatter(x=data["Timestamp"].to_numpy(), y=data["word-count"].to_numpy(), mode='lines+markers', name='lines+markers')

        # tuple is (dict of new data, target trace index, number of points to keep)
        fig = go.Figure(
            data=[scatter]
        )
        return fig

    except Exception:
        print(traceback.format_exc())


@app.callback(
    Output("out-all-types", "children"),
    [Input("input", "value")]
)
def cb_render(value):
    global experiment_id
    experiment_id = value
    return value

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=80)
