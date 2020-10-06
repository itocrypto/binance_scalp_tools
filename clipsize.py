API=None
SECRET=None



clips_max=5
default_balance=10000


from binance.client import Client
exchange = Client(API, SECRET)
exchange_info = exchange.futures_exchange_info()
SYMBOLS = [s['symbol'] for s in exchange_info['symbols']]
SYMBOLS.sort()
quantity_precision = {item['symbol']:item['quantityPrecision'] for item in exchange_info['symbols']}

def get_last_price(symbol):
    result = exchange.futures_recent_trades(symbol=symbol, limit=1)
    return float(result[0]['price'])

def get_balance():
    if API is None or SECRET is None:
        return default_balance
    futures_account = exchange.futures_account()
    return float(futures_account['totalWalletBalance'])


import plotly.graph_objects as go
import dash
from dash.dependencies import Input, Output, State
import dash_table
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme
import dash_core_components as dcc
import dash_html_components as html
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

symbol_dropdown = dcc.Dropdown(id='symbols-dropdown',
    options=[{'label':symbol, 'value':symbol} for symbol in SYMBOLS],
    multi=True)  

clipsize_input = dcc.Input(
    id="clipsize-input", type="number", max=1, min=0, step=0.01, value=0.01,
    placeholder="clip size %",)

update_button = html.Button('Update', id='update-button', n_clicks=0)



def make_table(balance,clipsize,symbols_price):
    data = []

    for i in range(1,clips_max+1):
        row = {'clipsize':'{}x'.format(i)}
        for symbol, price in symbols_price.items():
            row[symbol] = clipsize*i*balance/price
            print(row)
        data.append(row)

    clip_table = dash_table.DataTable(
        columns=(
            [{'id': 'clipsize', 'name': 'Clip Size','type':'text'}]+
            [{'id': symbol, 'name': symbol,'type':'numeric','format':Format(precision=quantity_precision[symbol], scheme=Scheme.fixed)} for symbol in symbols_price.keys()]
        ),
        style_header={
            'backgroundColor': 'grey',
            'color' : 'black',
            'text-align': 'center',
            'font-family': 'HelveticaNeue',
            'font-size': '14px',        
            'fontWeight': 'bold'
        },
        style_cell={ 
            'backgroundColor': '#CFCFCF',
            'font-family': 'HelveticaNeue',
            'font-size': '12px',        
            'fontWeight': 'bold'
        },
        style_data={
        'color': 'black',
        'whiteSpace': 'normal',
        'textAlign': 'center'
        },    
        css=[
            {
            'selector': '.Select-menu-outer',
            'rule': '''--accent: black;'''
            },
            {
            'selector': '.Select-arrow',
            'rule': '''--accent: black;'''
            },              
            ],
        data=data,
        editable=False
    )
    return clip_table



app = dash.Dash(name="some_name", external_stylesheets=external_stylesheets)

app.layout = html.Div(
    children=[
        symbol_dropdown,
        clipsize_input,
        update_button,
        html.Div(id='clip-table'),])

@app.callback(
    Output('clip-table', 'children'),
    [Input('update-button', 'n_clicks')],
    [State('symbols-dropdown', 'value'), 
    State("clipsize-input",'value')])
def say_volume(n_clicks, symbols, clipsize):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]    

    output = ''
    if button_id=='update-button':
        symbol_price={}
        for symbol in symbols:
            symbol_price[symbol]=get_last_price(symbol)
        balance = get_balance()
    
        output = make_table(balance, clipsize, symbol_price)

    return output



if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port=8077, debug=True)


