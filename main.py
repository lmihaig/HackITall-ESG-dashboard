import pandas as pd
import dash
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objects as go
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
                     dict(text=str(round(last_entry.factor, 2)), x=1.5, y=0, font_size=50, showarrow=False, font_color="white")])
    fig.update_layout(legend={'itemsizing': 'constant'})
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
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("ESG Grade", style={
                    "textAlign": "center"}),
                dbc.CardBody([
                    html.H1(id="gradeESG"),
                    html.H1(id="scoreESG"),
                    html.H1(id="changeESG"),
                    html.H1(id="year_changeESG")
                ], style={"textAlign": "center"})
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Stock Growth", style={
                    "textAlign": "center"}),
                dbc.CardBody([
                    dcc.Graph(id="stockGrowth", figure={})
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Events", style={
                    "textAlign": "center"}),
                dbc.CardBody([
                    html.H1(children="Add events")
                ])
            ])
        ], width=4),
    ])
], className="mt-2 mb-2")


@ app.callback(
    Output("scoreE", "figure"),
    Output("scoreS", "figure"),
    Output("scoreG", "figure"),
    Output("timelineESG", "figure"),
    Output("gradeESG", "children"),
    Output("scoreESG", "children"),
    Output("changeESG", "children"),
    Output("changeESG", "style"),
    Output("year_changeESG", "children"),
    Output("year_changeESG", "style"),
    Input(component_id='select_ticker', component_property='value')
)
def update_graph(ticker):
    if ticker is None:
        ticker = df.ticker.unique()[0]

    fig_E = get_Pie("Economic factor", data_process.get_E(ticker))
    fig_S = get_Pie("Social factor", data_process.get_S(ticker))
    fig_G = get_Pie("Governance factor", data_process.get_G(ticker))

    esg_df = data_process.get_ESG(ticker)
    fig_ESG = px.line(esg_df, x="date", y="ESG", markers=True,
                      title="ESG timeline")
    fig_ESG.update_traces(line_color="#00BC8C")
    fig_ESG.update_layout(font_color="white",
                          plot_bgcolor="rgba(0, 0, 0, 0)", paper_bgcolor="rgba(0, 0, 0, 0)", title_x=0.5, margin=dict(l=20, r=20, t=30, b=20),  yaxis_title="ESG score", xaxis_title="Financial Quarter")
    # fig_ESG.update_xaxes(visible=False)

    WINDOW = 20
    esg_df['sma'] = esg_df['ESG'].rolling(WINDOW).mean()
    esg_df['std'] = esg_df['ESG'].rolling(WINDOW).std(ddof=0)

    # Moving Average
    fig_ESG.add_trace(go.Scatter(x=esg_df['date'],
                                 y=esg_df['sma'],
                                 line_color='black',
                                 name='Simple Moving Average'),
                      row=1, col=1)

    # Upper Bound
    fig_ESG.add_trace(go.Scatter(x=esg_df['date'],
                                 y=esg_df['sma'] + (esg_df['std'] * 2),
                                 line_color='gray',
                                 line={'dash': 'dash'},
                                 name='Upper Bollinger Band',
                                 opacity=0.5),
                      row=1, col=1)

    # Lower Bound fill in between with parameter 'fill': 'tonexty'
    fig_ESG.add_trace(go.Scatter(x=esg_df['date'],
                                 y=esg_df['sma'] - (esg_df['std'] * 2),
                                 line_color='gray',
                                 line={'dash': 'dash'},
                                 fill='tonexty',
                                 name='Lower Bollinger Band',
                                 opacity=0.5),
                      row=1, col=1)
    fig_ESG.update_xaxes(visible=False)

    score = esg_df.ESG.iloc[-1]
    grade = ""
    match score:
        case num if 0 <= num < 1.429:
            grade = "CCC"
        case num if 1.429 <= num < 2.857:
            grade = "B"
        case num if 2.857 <= num < 4.286:
            grade = "BB"
        case num if 4.286 <= num < 5.714:
            grade = "BBB"
        case num if 5.714 <= num < 7.143:
            grade = "A"
        case num if 7.143 <= num < 8.571:
            grade = "AA"
        case num if 8.571 <= num <= 10:
            grade = "AAA"

    last_score = esg_df.ESG.iloc[-2]
    percentage = round(score/last_score - 1, 2)
    if percentage <= 0:
        colour = {"color": "red"}
    else:
        colour = {"color": "green"}

    lastyear_score = esg_df.ESG.iloc[-5]
    lastyear_percentage = round(score/lastyear_score - 1, 2)
    if lastyear_percentage <= 0:
        lastyear_colour = {"color": "red"}
    else:
        lastyear_colour = {"color": "green"}

    score = round(score, 2)
    percentage = "Last quarter: "+str(percentage)+"%"
    lastyear_percentage = "Last year: "+str(lastyear_percentage)+"%"
    return fig_E, fig_S, fig_G, fig_ESG, grade, score, percentage, colour, lastyear_percentage, lastyear_colour


if __name__ == "__main__":
    app.run_server(debug=True)
