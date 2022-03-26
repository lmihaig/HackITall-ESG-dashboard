import re
import pandas as pd
import dash
import plotly.express as px
import dash_bootstrap_components as dbc
import emoji
from base64 import b64decode
from dash.exceptions import PreventUpdate
from dash import dcc, html, dash_table
from dash.dependencies import Output, Input, State
from wordcloud import WordCloud


def clearchat(chat):
    # combines multi-line messages without a proper date-time in a single message#
    date_time_pattern = re.compile("^[0-3][0-9]\/[0-1][0-9]\/\d{4},")
    for i in range(len(chat)):
        if date_time_pattern.search(chat[i]) is None:
            chat[i-1] = chat[i-1] + " " + chat[i]
            chat[i] = "NotAValidEntry"

    for i in range(len(chat)):
        if chat[i].split(" ")[0] == "NotAValidEntry":
            chat[i] = "NotAValidEntry"

    while True:
        try:
            chat.remove("NotAValidEntry")
        except ValueError:
            break
    return chat


def build_df(chat):
    date_list = []
    time = []
    name = []
    content = []

    for text in chat:
        date_list.append(text.split(",")[0])
        time.append(text.split(",")[1].split("-")[0])
        name.append(text.split("-")[1].split(":")[0])
        try:
            content.append(text.split(":")[2])
        except IndexError:
            content.append(text.split("-")[1])
            name[-1] = "System Message"

    df = pd.DataFrame(list(zip(date_list, time, name, content)),
                      columns=["Date", "Time", "Name", "Content"])
    df = df[~df["Content"].str.contains("This message was deleted")]
    df = df[~df["Content"].str.contains("You deleted this message")]

    df_system = pd.DataFrame(columns=df.columns)
    cond = df["Name"] == "System Message"
    rows = df.loc[cond, :]
    df_system = df_system.append(rows, ignore_index=True)
    df.drop(rows.index, inplace=True)

    df_media = pd.DataFrame(columns=df.columns)
    cond = df["Content"] == " <Media omitted>"
    rows = df.loc[cond, :]
    df_media = df_media.append(rows, ignore_index=True)
    df.drop(rows.index, inplace=True)

    df_links = pd.DataFrame(columns=df.columns)
    #  sorry if someone was having a discussion about https or http #
    rows = df[df["Content"].astype(str).str.contains("https|http")]
    df_links = df_links.append(rows, ignore_index=True)
    df.drop(rows.index, inplace=True)

    df = df.reset_index()
    return df, df_system, df_media, df_links


#  still deciding on DARKLY, SLATE, SUPERHERO #
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}])
server = app.server
app.title = "WhatsApp Chat Analyser by lmihaig"
app.layout = dbc.Container(fluid=True, children=[
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.CardLink("WhatsApp Chat Analyser by lmihaig", target="_blank",
                                 href="https://github.com/lmihaig/whatsapp-analyser")
                ],  className="align-self-center")
            ])
        ], width=2),
        dbc.Col([

        ], width=1),
        dbc.Col([
            dcc.Upload([
                "Drag and Drop or ",
                html.A("Select a File")], className="align-items-center", id="upload-chat",
                style={
                "display": "inline-block",
                "text-align": "center",
                "font-size": "11px",
                "font-weight": "600",
                "line-height": "38px",
                "letter-spacing": ".1rem",
                "text-transform": "uppercase",
                "text-decoration": "none",
                "white-space": "nowrap",
                "background-color": "transparent",
                "border-radius": "4px",
                "border": "1px",
                "cursor": "pointer",
                "box-sizing": "border-box",
                "width": "95%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
            })])
    ], className="mt-2 mb-2"),
    dbc.Row([
        dbc.Col([
            dbc.Input(id="queryword", placeholder="Word to search for"),
        ]),
        dbc.Col([
            dbc.Button("Analyse", id="submit-val", n_clicks=0,
                       style={
                           "color":  "#00BC8C",
                           "border-style": "solid",
                           "border-width": "1px",
                           "border-color":  "#00BC8C",
                           "border-radius": "10px"
                       })
        ])
    ], className="mt-2 mb-2"),

    dcc.Store(id="dataframe"),
    html.Div([],
             id="query-results", style={"display": "none"}),
    html.Div([
        html.H2("Cards and Graphs"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("TOTAL MESSAGES", style={
                        "textAlign": "center"}),
                    dbc.CardBody([
                        html.H2(id="total-messages")
                    ], style={"textAlign": "center"})
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("TOTAL EMOJIS", style={
                        "textAlign": "center"}),
                    dbc.CardBody([
                        html.H2(id="total-emojis")
                    ], style={"textAlign": "center"})
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("TOTAL LINKS", style={
                        "textAlign": "center"}),
                    dbc.CardBody([
                        html.H2(id="total-links")
                    ], style={"textAlign": "center"})
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("TOTAL MEDIA", style={
                        "textAlign": "center"}),
                    dbc.CardBody([
                        html.H2(id="total-media")
                    ], style={"textAlign": "center"})
                ])
            ], width=3)
        ], className="mb-2"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("TOTAL CHATTERS", style={
                        "textAlign": "center"}),
                    dbc.CardBody([
                        html.H2(id="total-chatters")
                    ], style={"textAlign": "center"})
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("MOST USED EMOJI", style={
                        "textAlign": "center"}),
                    dbc.CardBody([
                        html.H2(id="most-used-emoji")
                    ], style={"textAlign": "center"})
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("PERSON WITH MOST MESSAGES", style={
                        "textAlign": "center"}),
                    dbc.CardBody([
                        html.H2(id="most-messages-person")
                    ], style={"textAlign": "center"})
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("DAY WITH MOST MESSAGES", style={
                        "textAlign": "center"}),
                    dbc.CardBody([
                        html.H2(id="most-messages-day")
                    ], style={"textAlign": "center"})
                ])
            ], width=3)
        ], className="mb-2"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id="line-chart", figure={})
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id="bar-chart", figure={})
                    ])
                ])
            ], width=6),
        ], className="mb-2"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id="pie-chart", figure={})
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id="word-cloud", figure={})
                    ])
                ])
            ], width=6),
        ], className="mb-2")
    ], id="cards-and-graphs", style={"display": "none"})

])

globalcontents = 0


@ app.callback(
    Output("cards-and-graphs", "style"),
    Output("total-messages", "children"),
    Output("total-emojis", "children"),
    Output("total-links", "children"),
    Output("total-media", "children"),
    Output("total-chatters", "children"),
    Output("most-used-emoji", "children"),
    Output("most-messages-person", "children"),
    Output("most-messages-day", "children"),
    Output("line-chart", "figure"),
    Output("pie-chart", "figure"),
    Output("bar-chart", "figure"),
    Output("word-cloud", "figure"),
    Output("dataframe", "data"),
    Input("submit-val", "n_clicks"),
    State("upload-chat", "contents"),
    State("upload-chat", "filename")
)
def update_cards(click, contents, filename):
    global globalcontents
    if contents == globalcontents:
        raise PreventUpdate
    else:
        globalcontents = contents
        content_type, content_string = contents.split(",")
        decoded_text = b64decode(content_string).decode("utf-8")
        try:
            if "txt" in filename:
                chat = decoded_text.splitlines()
                chat = clearchat(chat)
                df, df_system, df_media, df_links = build_df(chat)
        except Exception as e:
            print(e)
            return html.Div([
                "There was an error processing this file."
            ])

        #  total non-link non-media non-system messages #
        total_messages = len(df)

        #  all emojis sent #
        emojilist = df["Content"].str.extractall(
            emoji.get_emoji_regexp()).dropna()
        emojilist.reset_index(drop=True, inplace=True)

        #  total number of emojis sent #
        total_emojis = len(emojilist)

        # total messages with links#
        total_links = len(df_links)

        # total messages with media#
        total_media = len(df_media)

        # all the people that have ever sent a message in this chat #
        total_chatters = len(df["Name"].unique())

        #  most used emoji in texts #
        emojilist = emojilist.value_counts()
        most_used_emoji = emojilist.idxmax()
        emojilist = emojilist.reset_index(
            name="Value")
        emojilist = emojilist.rename(columns={emojilist.columns[0]: "Emoji"})
        emojilist = emojilist.head(15)

        #  person that sent the most messages #
        messages_per_chatter = df["Name"].value_counts()
        most_messages_person = messages_per_chatter.idxmax()
        messages_per_chatter = messages_per_chatter.rename_axis(
            "Name").reset_index(name="Messages")

        #  day that had most activity #
        messages_per_day = df["Date"].value_counts(sort=False)
        most_messages_day = messages_per_day.idxmax()

        #  line chart with total cumulative messages #
        df.index.rename("Messages")
        fig_linechart = px.line(df, x="Date", markers=True,
                                title="Daily progression of Messages")
        fig_linechart.update_traces(line_color="#00BC8C", fill='tozeroy')
        fig_linechart.update_layout(font_color="white",
                                    plot_bgcolor="rgba(0, 0, 0, 0)", paper_bgcolor="rgba(0, 0, 0, 0)", title_x=0.5, margin=dict(l=20, r=20, t=30, b=20),  yaxis_title="Messages")
        fig_linechart.update_xaxes(visible=False)

        #  pie chart with messages per sender #
        fig_piechart = px.pie(messages_per_chatter, values="Messages",
                              names="Name", title="Messages per Sender")
        fig_piechart.update_layout(font_color="white",
                                   plot_bgcolor="rgba(0, 0, 0, 0)", paper_bgcolor="rgba(0, 0, 0, 0)", title_x=0.5, margin=dict(l=20, r=20, t=30, b=20))
        fig_piechart.update_xaxes(visible=False)
        fig_piechart.update_yaxes(visible=False)

        #  barchart with most frequent emojis #
        fig_barchart = px.bar(emojilist, x="Emoji",
                              y="Value", title="Most used Emojis")
        fig_barchart.update_traces(marker_color="#00BC8C")
        fig_barchart.update_layout(font_color="white",
                                   plot_bgcolor="rgba(0, 0, 0, 0)", paper_bgcolor="rgba(0, 0, 0, 0)", title_x=0.5, margin=dict(l=20, r=20, t=30, b=20))

        #  wordcloud with messages #
        wordcloud = WordCloud(background_color="rgb(48,48,48)", min_word_length=4, width=800, height=400).generate(
            " ".join(df["Content"].astype(str)))
        fig_wordcloud = px.imshow(
            wordcloud, template="plotly_dark", title="Messages Wordcloud")
        fig_wordcloud.update_layout(
            plot_bgcolor="rgba(0, 0, 0, 0)", paper_bgcolor="rgba(0, 0, 0, 0)", title_x=0.5, margin=dict(l=20, r=20, t=30, b=20))
        fig_wordcloud.update_xaxes(visible=False)
        fig_wordcloud.update_yaxes(visible=False)

        visibility = {"display": "block"}
        df = df.to_json()

        return visibility, total_messages, total_emojis, total_links, total_media, total_chatters, most_used_emoji, most_messages_person, most_messages_day, fig_linechart, fig_piechart, fig_barchart, fig_wordcloud, df


@ app.callback(Output("query-results", "style"), Output("query-results", "children"),  Input("submit-val", "n_clicks"), State("queryword", "value"), State("dataframe", "data"))
def update_query(click, queryword, df):
    visibility = {"display": "none"}
    if (queryword is not None) and (queryword != ""):
        df = pd.read_json(df)
        df["Date"] = df["Date"].dt.strftime("%Y/%m/%d")
        df_query = pd.DataFrame(columns=df.columns)
        rows = df[df["Content"].astype(
            str).str.contains(queryword, case=False)]
        df_query = df_query.append(rows, ignore_index=True)
        visibility = {"display": "block"}
        table = [html.Hr(), html.H2("Query Results"),
                 dash_table.DataTable(
            id="table",
            columns=[{"name": i, "id": i} for i in df_query.columns],
            page_size=10,
            data=df_query.to_dict("records"),
            style_as_list_view=True,
            style_header={"backgroundColor": "rgb(30, 30, 30)"},
            style_cell={
                "backgroundColor": "rgb(50, 50, 50)",
                "color": "white",
                "textAlign": "left",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
                "maxWidth": "400px"
            },
            style_data={
                "whiteSpace": "normal",
                "height": "auto",
            }
        )]
        return visibility, table
    return visibility, 1


if __name__ == "__main__":
    app.run_server(debug=False)
