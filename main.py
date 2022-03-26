
from matplotlib import ticker
from matplotlib.pyplot import get
import pandas as pd
import dash
import plotly.express as px
import dash_bootstrap_components as dbc
from base64 import b64decode
from dash.exceptions import PreventUpdate
from dash import dcc, html, dash_table
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import data_process


df = pd.read_csv("datastore.csv")
df = df.groupby(['ticker', 'provider', 'date'])[['price']].mean()
df.reset_index(inplace=True)


def get_Pie(text, temp_df):
    last_entry = temp_df.iloc[-1]
    temp_df = data_process.get_index_percentage(last_entry)

    fig = px.pie(temp_df, values="value",
                 names="index", title=text)

    fig.update_layout(height=300, font_color="white",
                      plot_bgcolor="rgba(0, 0, 0, 0)", paper_bgcolor="rgba(0, 0, 0, 0)", title_x=0.5, margin=dict(l=20, r=20, t=30, b=20))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    # Use `hole` to create a donut-like pie chart
    fig.update_traces(hole=.4, hoverinfo="label+percent+name")

    fig.update_layout(
        title_text=text,
        # Add annotations in the center of the donut pies.
        annotations=[dict(text=text[0], x=0.5, y=0.5, font_size=50, showarrow=False, font_color="white"),
                     dict(text=str(round(last_entry.factor, 2)), x=0, y=0, font_size=50, showarrow=False, font_color="white")])
    return fig


#  still deciding on DARKLY, SLATE, SUPERHERO #
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE], meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}])
server = app.server
app.title = "ESG Analyser"
app.layout = dbc.Container(fluid=True, children=[
    # html.H1("ESG Analyser", style={'text-align': 'center'}),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id="select_ticker",
                         options=[{'label': i, 'value': i} for i in df.ticker.unique()],
                         placeholder='Select ticker',
                         multi=False,
                         #  style={'width': "40%"}
                         ),
        ], width=3),
        dbc.Col([
            html.H1("ESG Analyser", style={'text-align': 'center'})
        ], width=7)
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Economic Score", style={
                    "textAlign": "center"}),
                dbc.CardBody([
                    dcc.Graph(id="scoreE", figure={})
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Social Score", style={
                    "textAlign": "center"}),
                dbc.CardBody([
                    dcc.Graph(id="scoreS", figure={})
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Governance Score", style={
                    "textAlign": "center"}),
                dbc.CardBody([
                    dcc.Graph(id="scoreG", figure={})
                ])
            ])
        ], width=4),
    ], style={"height": "42vh"}),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="timelineESG", figure={})
                ])
            ])
        ], width=12),
    ], style={"height": "40vh"},)
], className="mt-2 mb-2")


@ app.callback(
    Output("scoreE", "figure"),
    Output("scoreS", "figure"),
    Output("scoreG", "figure"),
    Output("timelineESG", "figure"),
    Input(component_id='select_ticker', component_property='value')
)
def update_graph(ticker):
    if(ticker == None):
        ticker = df.ticker.unique()[0]

    fig_E = get_Pie("Economic factor", data_process.get_E(ticker))
    fig_S = get_Pie("Social factor", data_process.get_S(ticker))
    fig_G = get_Pie("Governance factor", data_process.get_G(ticker))

    return fig_E, fig_S, fig_G, 0


if __name__ == "__main__":
    app.run_server(debug=True)
