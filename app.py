import base64
import datetime
import io
from os import listdir
from os.path import isfile, join

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

from sklearn.externals import joblib
import plotly.graph_objs as go

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'MeCan'


app.layout = html.Div(children=[
    html.H1(children='Welcome to MeCan!'),
                                 
    html.Div(children='''
    Upload your gene expression profile and find out your personalized sensitivity to the common chemotheraputic drugs.
    ''', style={'fontSize': 24}),
                                 
    dcc.Upload(
        id='upload-data',
        children=html.Div([
                         'Drag and Drop or ',
                         html.A('Select Files')
                         ]),
        style={
        'width': '100%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin': '10px'
        },
        # Do not allow multiple files to be uploaded
        multiple=True
        ),
    html.Div(id='output-data-upload'),
    ])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), header=None)
        elif 'xls' in filename or 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
                     'There was an error processing this file.'
                     ])
    ic50s = []
    for model in models:
        ic50s.append(model.predict(df.T)[1])

    return html.Div([
                    html.H5("File name: " + filename),
                    html.H6("Last modified time: " + str(datetime.datetime.fromtimestamp(date))),
                     #html.H7("Prediction: " + str(ic50)),
                     
                    html.Div(', '.join([str(i) for i in ic50s])),
                     
                    dash_table.DataTable(
                                       data=df.to_dict('records'),
                                       columns=[{'name': i, 'id': i} for i in df.columns]
                                       ),

                    html.Hr(),  # horizontal line

                    # For debugging, display the raw contents provided by the web browser
                    #html.Div('Raw Content'),
                    #html.Pre(contents[0:200] + '...', style={
                    #       'whiteSpace': 'pre-wrap',
                    #      'wordBreak': 'break-all'
                    #      })
                    ])

@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [parse_contents(c, n, d) for c, n, d in
                    zip(list_of_contents, list_of_names, list_of_dates)]
        return children


def update_years_of_experience_input(years_of_experience):
    if years_of_experience is not None and years_of_experience is not '':
        try:
            salary = model.predict(float(years_of_experience))[0]
            return 'With {} years of experience you should earn a salary of ${:,.2f}'.                format(years_of_experience, salary, 2)
        except ValueError:
            return 'Unable to give years of experience'


if __name__ == '__main__':
    model_dir = './models/'
    model_paths = [join(model_dir, f) for f in listdir(model_dir) if isfile(join(model_dir, f))]
    models = [joblib.load(i) for i in model_paths]
    #model = joblib.load("./finalized_model.sav")
    app.run_server(debug=True)




