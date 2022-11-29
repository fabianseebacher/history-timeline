from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_daq as daq
import pandas as pd
import numpy as np

# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
]

app = Dash(__name__, external_stylesheets=external_stylesheets)

events = pd.read_excel("Geschichte.xlsx")
# process columns
events['duration'] = events['end'] - events['start']
events['midpoint'] = events[['start', 'end']].mean(axis=1)
events['category'] = events['category'].fillna('n.d.')
events['label'] = events['start'].astype(str) + ' - ' + events['end'].astype(str) + '<br>' + events['comment'].replace(np.nan, '').astype(str)
events['label_bold'] = '<b>'+events.sort_values('start')['event']+'</b>'

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                    sorted(events['event'].unique()),
                    [],
                    placeholder="Select a historical event",
                    multi=True,
                    id='eve-dropdown'
                ),
        ], style={'margin': '1%'}),

        html.Div([
            html.Div([
                # html.Label(
                #     'Kategorie',
                #     id='cat-label'
                # ),
                dcc.Dropdown(
                    sorted(events['category'].unique()),
                    [],
                    placeholder="Select a category of event",
                    multi=True,
                    id='cat-dropdown'
                ),
            ], style={'width': '33%', 'display': 'inline-block'}),

            html.Div([
                # html.Label(
                #     'Kategorie',
                #     id='cat-label'
                # ),
                dcc.Dropdown(
                    sorted(events['continent'].unique()),
                    [],
                    placeholder="Select a continent",
                    multi=True,
                    id='cont-dropdown'
                ),
            ], style={'width': '34%', 'display': 'inline-block'}),

            html.Div([
                # html.Label(
                #     'Kontinent',
                #     id='cont-label'
                # ),
                dcc.Dropdown(
                    sorted(list(set([item for sublist in [i.split(';') for i in events['country'].dropna().unique()] for item in sublist]))),
                    [],
                    placeholder="Select a country",
                    multi=True,
                    id='country-dropdown'
                ),
            ], style={'width': '33%', 'display': 'inline-block'}),
        ], style={'margin': '1%'}),
            
        dcc.RangeSlider(-2700, 2022, value=[-2700, 2022],
                tooltip={"placement": "bottom", "always_visible": True},
                id='year-slider'),
        
        html.Div([
            daq.BooleanSwitch(id='group-switch', 
                on=False, 
                label="Toggle grouping",
                labelPosition="left"
                ),    
        ], style={'width': '25%', 'display': 'inline-block'}),
        
    ]),


    dcc.Graph(id='indicator-graphic'),

])


@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('eve-dropdown', 'value'),
    Input('cat-dropdown', 'value'),
    Input('cont-dropdown', 'value'),
    Input('country-dropdown', 'value'),
    Input('year-slider', 'value'),
    Input('group-switch', 'on'),
    )
def update_graph(eve, cat, cont, coun, year, group):
    events = pd.read_excel(r"C:\Users\fabia\dash\history\Geschichte.xlsx")
    events = events[(events['start'] >= year[0]) & (events['end'] <= year[1])]

    events['label_bold'] = '<b>'+events.sort_values('start')['event']+'</b>'
    
    # check if list and cast to list if input is str
    eve = [eve] if isinstance(eve, str) else eve
    cat = [cat] if isinstance(cat, str) else cat
    cont = [cont] if isinstance(cont, str) else cont
    coun = [coun] if isinstance(coun, str) else coun

    if eve == []:
        eve = events['event'].unique()
    if cat == []:
        cat = events['category'].unique()
    if cont == []:
        cont = events['continent'].unique()

    # apply filters
    events = events[(events['event'].isin(eve)) & (events['category'].isin(cat))& (events['continent'].isin(cont))]
    if coun != []:
        events = events[events['country'].str.contains('|'.join(coun), na=False)]
    # process columns
    events['duration'] = events['end'] - events['start']
    events['midpoint'] = events[['start', 'end']].mean(axis=1)
    events['category'] = events['category'].fillna('n.d.')
    events['label'] = events['start'].astype(str) + ' - ' + events['end'].astype(str) + '<br>' + events['comment'].replace(np.nan, '').astype(str)

    if group == True:
        fig = px.bar(events.sort_values('start'), 
                base = "start",
                x = "duration",
                #y = "event",
                y = "label_bold",
                #orientation = 'h',
                color = 'category',
                color_discrete_sequence=px.colors.qualitative.Pastel2,
                text = 'event',
                height=1000
        )
    else:
        fig = px.bar(events.sort_values('start'), 
                base = "start",
                x = "duration",
                #y = "event",
                y = "label_bold",
                #orientation = 'h',
                #color = 'category',
                color_discrete_sequence=["lightblue"],
                text = 'event',
                height=1000
        )

    fig.update_yaxes(autorange="reversed")
    #fig.update_layout(yaxis_categoryorder = 'total ascending')
    fig.update_layout(template='plotly_white')
    fig.update_traces(
            hovertemplate=None,
            hoverinfo='skip',
            textfont_size=12, 
            textangle=0, 
            textposition="outside", 
            cliponaxis=False
        )
    fig.update_layout(hovermode="x",
        #autosize=False,
        height=150+15*len(events),
        xaxis_title="Year", 
        yaxis_title="Event")
    fig.update_yaxes(tickmode='linear',showticklabels=False)
    fig.update_xaxes(side='top')
    
    fig.add_scatter(x = events.sort_values('start')['midpoint'],
                    #y = events.sort_values('start')['event'],
                    y = events.sort_values('start')['label_bold'],
                    mode = 'markers',
                    #color_discrete_sequence = ['darkgrey'],
                    line_color="darkgrey",
                    showlegend = False,
                    hovertext=events.sort_values('start')['label'],
                    # customdata = [events.sort_values('start')['start'], 
                    #             events.sort_values('start')['end'],
                    #             events.sort_values('start')['comment']
                    #             ]
                )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)