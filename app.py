import base64
import datetime
import io
from os import listdir
from os.path import isfile, join
import json

import numpy as np
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

model_dir = 'models/'
model_paths = [join(model_dir, f) for f in listdir(model_dir) if isfile(join(model_dir, f))]
models = [joblib.load(i) for i in model_paths]
#models=[]
#for i in model_paths:
    #print(i)
#    models.append(joblib.load(i))
with open('conf/parms.json') as infile:
    params = json.load(infile)
opts = [{'label' : "patient {}".format(i), 'value' : "patient{}".format(i)} for i in range(1,4)]


app.layout = html.Div(children=[
                                html.H1(children='Welcome to Precision Chemotherapy Recommander!',
                                        style={'textAlign': 'center', 'backgroundColor':'#98C0B9'}),
                                 
    html.Div(children='''
    Find out your personalized sensitivity to the common chemotheraputic drugs.
    ''', style={'fontSize': 24, 'marginBottom': '1.5em'}),
                                
    html.Div(children='''Select to see an examples, or upload your gene expression file:''',
             style={'fontSize': 18}),

    html.Div([
              html.Div([
                  dcc.Dropdown(
                               id='example',
                               options=opts,
                               style={
                               'fontsize': '12px',
                               'height': '60px',
                               'lineHeight': '60px',
                               'borderWidth': '1px',
                               'textAlign': 'center',
                               'margin': '10px'
                               }
                               )
                        ],style={'width': '48%', 'display': 'inline-block'}),
              html.Div([
                  dcc.Upload(
                             id='upload-data',
                             children=html.Div([
                                                'Drag and Drop or ',
                                                html.A('Select Files')
                                                ]),
                             style={
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
                             )
                        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
              ]),
             
    html.Div(id='output-data-upload'),
    ])


@app.callback(Output('output-data-upload', 'children'),
              [Input('example', 'value'),
               Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(patient_num, list_of_contents, list_of_names):
    if patient_num is not None:
        filepath = 'examples/' + str(patient_num) + '.csv'
        df = pd.read_csv(filepath, header=None, index_col=0)

        return run_models(patient_num + '.csv', df)
    if list_of_contents is not None:
        children = [parse_contents(c, n) for c, n in
                    zip(list_of_contents, list_of_names)]
        return children


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), header=None, index_col=0)
        elif 'xls' in filename or 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
                         'There was an error processing this file.'
                         ])
    return run_models(filename, df)

def run_models(filename, df):
    ic50s = []
    genes = []
    drug_names = [i[7:-10] for i in model_paths]
    for i, model in enumerate(models):
        drug_name = drug_names[i]
        x = df.loc[params[drug_name]]
        x = x.fillna(0)
        ic50s.append(model.predict(x.T)[0])
        genes.append(', '.join(params[drug_name][-10:]))
    
    idx = np.array(ic50s).argsort()[:10]
    df1 = pd.DataFrame({'Rank': list(range(1,11)),
                       'Drug Name': [drug_names[i] for i in idx],
                       'IC50': [format(ic50s[i], '.2f') for i in idx],
                       'Ten Most Important Genes': [genes[i] for i in idx]
                       })

    return html.Div([
                     html.H3('The top 10 most sensitive chemotheraputic drugs', style={'textAlign': 'center'}),
                     
                     dash_table.DataTable(
                                          data=df1.to_dict('records'),
                                          columns=[{"name": i, "id": i} for i in df1.columns],
                                          style_cell = {'font_size': '16px', 'text_align': 'center'},
                                          style_data={'whiteSpace': 'normal'},
                                          style_cell_conditional=[
                                                                  {'if': {'column_id': 'Ten Most Important Genes'},
                                                                  'width': '60%'}
                                                                  ]
                                          ),
                     
                     html.H6('Input from: ' + filename),
                     html.Hr(),  # horizontal line
                     ])


if __name__ == '__main__':
    app.run_server(debug=True)




