
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


df = pd.read_csv("datastore.csv")
df = df.groupby(['ticker', 'provider', 'date'])[['price']].mean()
df.reset_index(inplace=True)


def calculateEGS(df):
    return df


#  still deciding on DARKLY, SLATE, SUPERHERO #
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE], meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}])
server = app.server
app.title = "ESG Analyser"
app.layout = dbc.Container(fluid=True, children=[
    html.H1("ESG Analyser", style={'text-align': 'center'}),
    dbc.Row([
        dcc.Dropdown(id="select_ticker",
                     options=[{'label': i, 'value': i} for i in df.ticker.unique()],
                     placeholder='Select ticker',
                     multi=False,
                     style={'width': "40%"}
                     ),

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
    ], style={"height": "60vh"}),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id="timelineESG", figure={})
                ])
            ])
        ], width=12),
    ], style={"height": "40vh"},)
])


@ app.callback(
    Output("scoreE", "figure"),
    Output("scoreS", "figure"),
    Output("scoreG", "figure"),
    Output("timelineESG", "figure"),
    Input(component_id='select_ticker', component_property='value')
)
def update_graph(ticker):

    fig_E = px.pie(df, values="price",
                   names="ticker", title="Economic rating")
    fig_E.update_layout(font_color="white",
                        plot_bgcolor="rgba(0, 0, 0, 0)", paper_bgcolor="rgba(0, 0, 0, 0)", title_x=0.5, margin=dict(l=20, r=20, t=30, b=20))
    fig_E.update_xaxes(visible=False)
    fig_E.update_yaxes(visible=False)

    # Use `hole` to create a donut-like pie chart
    fig_E.update_traces(hole=.4, hoverinfo="label+percent+name")

    fig_E.update_layout(
        title_text="Global Emissions 1990-2011",
        # Add annotations in the center of the donut pies.
        annotations=[dict(text='E', x=0.5, y=0.5, font_size=60, showarrow=False, font_color="white")])

    fig_S = px.pie(df, values="price",
                   names="ticker", title="Economic rating")

    fig_S.update_layout(font_color="white",
                        plot_bgcolor="rgba(0, 0, 0, 0)", paper_bgcolor="rgba(0, 0, 0, 0)", title_x=0.5, margin=dict(l=20, r=20, t=30, b=20))
    fig_S.update_xaxes(visible=False)
    fig_S.update_yaxes(visible=False)

    # Use `hole` to create a donut-like pie chart
    fig_S.update_traces(hole=.4, hoverinfo="label+percent+name")

    fig_S.update_layout(
        title_text="Global Emissions 1990-2011",
        # Add annotations in the center of the donut pies.
        annotations=[dict(text='S', x=0.5, y=0.5, font_size=60, showarrow=False, font_color="white")])

    fig_G = px.pie(df, values="price",
                   names="ticker", title="Economic rating")

    fig_G.update_layout(font_color="white",
                        plot_bgcolor="rgba(0, 0, 0, 0)", paper_bgcolor="rgba(0, 0, 0, 0)", title_x=0.5, margin=dict(l=20, r=20, t=30, b=20))
    fig_G.update_xaxes(visible=False)
    fig_G.update_yaxes(visible=False)

    # Use `hole` to create a donut-like pie chart
    fig_G.update_traces(hole=.4, hoverinfo="label+percent+name")

    fig_G.update_layout(
        title_text="Global Emissions 1990-2011",
        # Add annotations in the center of the donut pies.
        annotations=[dict(text='G', x=0.5, y=0.5, font_size=60, showarrow=False, font_color="white")])

    return fig_E, fig_S, fig_G, 0


if __name__ == "__main__":
    app.run_server(debug=True)
