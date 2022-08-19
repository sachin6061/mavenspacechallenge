import json
from dash_iconify import DashIconify
import dash
from dash import html, dcc, Input, Output, callback, dash_table, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import base64
import component as cmp
import dash_leaflet as dl

df = pd.read_csv('final_data1.csv')
df["Date"] = pd.to_datetime(df['Date']).dt.date

app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])
server = app.server

canvas = dbc.Offcanvas(
    [html.H1('Menu ', style={'color': 'white', }),
     # html.H3('Space Challenge', style={'color': 'white', 'text-align': 'center', 'font-style': 'italic'}),
     html.Hr(style={'color': 'White', 'height': '3px'}),
     dbc.Nav([
         dbc.NavLink("Overall", href="/", active="exact", style={'color': 'white', 'width': '100vh'}),
         dbc.NavLink("Country Wise", href="/country_wise", active="exact",
                     style={'color': 'white', 'width': '100vh'}),
         dbc.NavLink("Year Wise", href="/year_wise", active="exact",
                     style={'color': 'white', 'width': '100vh'}),
         dbc.NavLink("Company wise", href="/company_wise", active="exact",
                     style={'color': 'white', 'width': '100vh'}),
         dbc.NavLink("Launch Pad", href="/launch_pad", active="exact",
                     style={'color': 'white', 'width': '100vh'}),
         dbc.NavLink("About Me", href="/about_me", active="exact",
                     style={'color': 'white', 'width': '100vh'})], )
     ],
    id="offcanvas",
    is_open=False,
    style={"background-color": "#000000"}
)

app.layout = dbc.Container([dcc.Location(id="url"),
                            canvas, html.Div(id="page-content"),

                            html.H1(html.Span(
                                [DashIconify(icon="twemoji:rocket", height=40), " Maven Space Challenge ",
                                 DashIconify(icon="twemoji:rocket", height=40)]),
                                style={'background-color': 'Black', "position": "fixed", "left": 0,
                                       "top": 0, 'color': 'white', 'text-align': 'center',
                                       'width': '100%', 'padding': '10px'}),
                            dbc.Button(
                                html.Span([DashIconify(icon="icon-park:hamburger-button", height=40)]),
                                id="open-offcanvas", n_clicks=0,
                                style={'background-color': 'white', "position": "fixed",
                                       "top": 9, 'width': '60px', }),
                            ],
                           fluid=True, style={'padding': '20px', 'margin-top': '63px', 'height': '100%',
                                              'background-color': '#d9d9d9'})


@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return dcc.Loading(world_data(), type='cube')
    elif pathname == "/country_wise":
        return dcc.Loading(coountry_wise(), type='cube')
    elif pathname == "/launch_pad":
        return dcc.Loading(launch_pad())
    elif pathname == "/year_wise":
        return dcc.Loading(year_wise(), type='cube')
    elif pathname == "/company_wise":
        return dcc.Loading(company_wise(), type='cube')
    elif pathname == "/about_me":
        return dcc.Loading(fnAboutMe(), type='cube')


def world_data():
    all_df = df.groupby(['MissionStatus']).agg(
        {'cost': 'sum', 'Rocket': 'count'}).reset_index()
    dis_pie = px.pie(all_df, values='Rocket', names='MissionStatus', template='plotly_dark', hole=.5,
                     title='Mission Status In Percentage')

    status_df = df.groupby(['RocketStatus']).agg(
        {'Rocket': 'count'}).reset_index()
    rocket_status = px.bar(status_df, x="Rocket", y='RocketStatus', title="Rocket Status as of 2022",
                           template='plotly_dark', color='RocketStatus', text_auto='.2s')
    rocket_status.update_layout(xaxis_title="Count", yaxis_title="Rocket Status")

    dis_fig = px.bar(all_df, x="MissionStatus", y='cost', title="Cost Depends on Mission Status",
                     template='plotly_dark', color='MissionStatus', text_auto='.2s')

    year_Wise_df = df.groupby(['year']).agg(
        {'cost': 'sum', 'Rocket': 'count'}).reset_index()
    year_Wise_df = year_Wise_df[year_Wise_df['year'] >= 2000]
    grp_chart = go.Figure(data=[
        go.Bar(name='cost', x=year_Wise_df['year'], y=year_Wise_df['cost'], text=year_Wise_df['cost']),
        go.Bar(name='total mission', x=year_Wise_df['year'], y=year_Wise_df['Rocket'],
               text=year_Wise_df['Rocket']),
    ])
    grp_chart.update_traces(texttemplate='%{text:.2s}', textposition='auto')
    grp_chart.update_layout(barmode='group', title='Cost and Count of Mission Per Year', template='plotly_dark',
                            xaxis_title="Years", yaxis_title="cost in $")

    rocket_cuntry = df.groupby(['country']).agg(
        {'cost': 'sum', 'Rocket': 'count'}).reset_index()
    top_countries = rocket_cuntry.nlargest(10, 'Rocket')
    top10_fig = px.bar(top_countries, x="Rocket", y='country', title="Top 10 Countries",
                       template='plotly_dark', color='country', text_auto='.2s')
    top_countries = rocket_cuntry.nlargest(10, 'cost')
    top10_cost_fig = px.bar(top_countries, x="cost", y='country', title="Top 10 Countries by cost",
                            template='plotly_dark', color='country', text_auto='.2s')

    countries_df = df.groupby(['country']).agg(
        {'cost': 'sum', 'Rocket': 'count'}).reset_index()
    countries_df = countries_df.nlargest(len(countries_df['country']), 'Rocket')
    tot_launch_fig = px.bar(countries_df, x="country", y='Rocket', title="Country With Total launch Mission",
                            template='plotly_dark', color='country', text_auto='.2s')
    return [dbc.Row([
        dbc.Col([html.H5(html.Span(['Total Missions ', DashIconify(icon="noto:rocket", height=40)]),
                         style={'text-align': 'center'}),
                 html.H4(df['Mission'].count(), style={'text-align': 'center'})], className='mx-1 p-3',
                style=cmp.card_style),
        dbc.Col(
            [html.H5(html.Span(['Total Countries ', DashIconify(icon="gis:search-country", height=40)]),
                     style={'text-align': 'center'}),
             html.H4(len(df['country'].unique()), id='ttl-sale-b', style={'text-align': 'center'})],
            className='mx-1 p-3',
            style=cmp.card_style
        ),
        dbc.Col([html.H5(html.Span(['Total Cost ', DashIconify(icon="ic:round-price-change", height=40)]),
                         style={'text-align': 'center'}),
                 html.H4(str(df['cost'].sum()) + ' M $', id='ttl-dis-b', style={'text-align': 'center'})],
                className='mx-1 p-3',
                style=cmp.card_style),
        dbc.Col([html.H5(
            html.Span(['Companies Involved ', DashIconify(icon="carbon:location-company-filled", height=40)]),
            style={'text-align': 'center'}),
            html.H4(len(df['Company'].unique()), id='ttl-dis-b', style={'text-align': 'center'})],
            className='mx-1 p-3',
            style=cmp.card_style),

    ], className='mx-auto'),
        dbc.Row(
            [dbc.Col(dcc.Graph(id='bar-chart-sale', figure=dis_fig), width=4, className='p-1 ',
                     style={'border-radius': '20px'}),
             dbc.Col(dcc.Graph(id='pie-chart-sale', figure=dis_pie), width=4, className='p-1'),
             dbc.Col(dcc.Graph(id='pie-chart-sale', figure=rocket_status), width=4, className='p-1')],
            className='my-2 mx-auto'),
        dbc.Row(
            dbc.Col(dcc.Graph(id='bar-chart-sale', figure=tot_launch_fig), width=12, className='p-1 ',
                    style={'border-radius': '20px'}
                    ), className='my-2 mx-auto'),
        dbc.Row(
            dbc.Col(dcc.Graph(id='bar-chart-sale', figure=grp_chart), width=12, className='p-1 ',
                    style={'border-radius': '20px'}
                    ), className='my-2 mx-auto'),
        dbc.Row(
            [dbc.Col(dcc.Graph(id='bar-chart-sale', figure=top10_fig), width=6, className='p-1 ',
                     style={'border-radius': '20px'}),
             dbc.Col(dcc.Graph(id='pie-chart-sale', figure=top10_cost_fig), width=6, className='p-1')],
            className='my-2 mx-auto'),
    ]


def coountry_wise():
    contries = df['country'].unique()
    contry_df = df[df['country'] == " India"]
    start_date = contry_df['Date'].min()
    table_data = contry_df.drop(["loc", "country", "year", "month_year", "cost", "lat", "lon"], axis=1)
    active_inactive = df.groupby(['RocketStatus'])['Rocket'].count().reset_index()
    active_inactive_fig = px.bar(active_inactive, x="RocketStatus", y='Rocket', title="Rocket Status as of 2022",
                                 template='plotly_dark', color='RocketStatus', text_auto='.2s')
    active_inactive_fig.update_layout(
        xaxis_title="Years", yaxis_title="cost in $")

    MissionStatus = df.groupby(['MissionStatus']).agg(
        {'cost': 'sum', 'Rocket': 'count'}).reset_index()

    cost_pie = px.pie(MissionStatus, names="MissionStatus", values='cost', title="Cost Based on Mission status",
                      template='plotly_dark')
    rocket_pie = px.pie(MissionStatus, values='Rocket', names='MissionStatus', template='plotly_dark', hole=.3,
                        title='Mission Status')

    year_Wise_df = contry_df.groupby(['year']).agg(
        {'cost': 'sum', 'Rocket': 'count'}).reset_index()
    # year_Wise_df = year_Wise_df[year_Wise_df['year'] >= 2000]
    grp_chart = go.Figure(data=[
        go.Bar(name='cost', x=year_Wise_df['year'], y=year_Wise_df['cost'], text=year_Wise_df['cost']),
        go.Bar(name='total mission', x=year_Wise_df['year'], y=year_Wise_df['Rocket'],
               text=year_Wise_df['Rocket']),
    ])
    grp_chart.update_traces(texttemplate='%{text:.2s}', textposition='auto')
    grp_chart.update_layout(barmode='group', title='Cost and Count of Mission Per Year', template='plotly_dark',
                            xaxis_title="Years", yaxis_title="cost in $")

    return [dbc.Row([
        dbc.Col(
            [dcc.Dropdown(contries, " India", id='selected_country', style={'color': 'black'}),
             html.H5(f'First Rocket Launch On {start_date}',
                     style={'text-align': 'center', 'margin': '5px','color': 'black'}, id='first_launch')], width=3,
            className='p-1'),
        dbc.Col([html.H5(html.Span(['Total Missions ', DashIconify(icon="noto:rocket", height=40)]),
                         style={'text-align': 'center'}),
                 html.H4(contry_df['Mission'].count(), style={'text-align': 'center'}, id='ttl_msn')],
                className='mx-1 p-3', style=cmp.card_style),
        dbc.Col([html.H5(html.Span(['Total Cost ', DashIconify(icon="ic:round-price-change", height=40)]),
                         style={'text-align': 'center'}),
                 html.H4('{:.2f} M $'.format(contry_df['cost'].sum()), id='ttl_cst', style={'text-align': 'center'})],
                className='mx-1 p-3',
                style=cmp.card_style),
        dbc.Col([html.H5(
            html.Span(['Companies Involved ', DashIconify(icon="carbon:location-company-filled", height=40)]),
            style={'text-align': 'center'}),
            html.H4(len(contry_df['Company'].unique()), id='ttl-cmp', style={'text-align': 'center'})],
            className='mx-1 p-3', style=cmp.card_style),
    ]),
        dbc.Row(
            [dbc.Col(dcc.Graph(id='rocket_pie', figure=rocket_pie), width=4, className='p-1 ',
                     style={'border-radius': '20px'}),
             dbc.Col(dcc.Graph(id='ac_in_bar', figure=active_inactive_fig), width=4, className='p-1 ',
                     style={'border-radius': '20px'}),
             dbc.Col(dcc.Graph(id='cost_pie', figure=cost_pie), width=4, className='p-1')],
            className='my-2 mx-auto'),

        dbc.Row(
            dbc.Col(dcc.Graph(id='country_m_count_bar', figure=grp_chart), width=12, className='p-1 ',
                    style={'border-radius': '20px'}
                    ), className='my-2 mx-auto'),
        dbc.Row(dbc.Col(dash_table.DataTable(
            id='result-table',
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'border': '1px solid grey',
            },
            data=table_data.to_dict('Records'),

            style_data_conditional=[
                {
                    'if': {
                        'filter_query': '{MissionStatus} != Success',
                        'column_id': 'MissionStatus'
                    },
                    'color': 'white',
                    'backgroundColor': 'red',

                },
                {
                    'if': {
                        'filter_query': '{MissionStatus} = Success',
                        'column_id': 'MissionStatus'
                    },
                    'color': 'white',
                    'backgroundColor': 'Green'
                }
            ],
            page_size=10,
            style_cell={'textAlign': 'center', 'background-color': 'white', 'color': 'black', 'height': 'auto', },
            style_header={'textAlign': 'center', 'background-color': 'black', "font-size": "1vw", 'color': 'white'},
            tooltip_delay=0,
            tooltip_duration=None, page_action='native',

        ), width=12, className='p-1 ', style={'background-color': 'black'}), className='my-2 mx-auto '),
    ]


@app.callback(
    [Output("result-table", "data"), Output('result-table', 'columns'), Output('first_launch', 'children'),
     Output('ttl_msn', 'children'), Output('ttl_cst', 'children'), Output('ttl-cmp', 'children'),
     Output('rocket_pie', 'figure'), Output('cost_pie', 'figure'), Output('ac_in_bar', 'figure'),
     Output('country_m_count_bar', 'figure')],
    [Input("selected_country", "value")], )
def update_countries_page(country):
    contry_df = df[df['country'] == country]
    table_data = contry_df.drop(["loc", "country", "year", "month_year", "cost", "lat", "lon"], axis=1)
    start_date = contry_df['Date'].min()
    txt = f'First Rocket Launch On {start_date}'
    ttl_msn = contry_df['Mission'].count()
    ttl_cst = '{:.2f} M $'.format(contry_df['cost'].sum())
    ttl_cmp = len(contry_df['Company'].unique())

    MissionStatus = contry_df.groupby(['MissionStatus']).agg(
        {'cost': 'sum', 'Rocket': 'count'}).reset_index()

    cost_pie = px.pie(MissionStatus, names="MissionStatus", values='cost', title="Cost Based on Mission status",
                      template='plotly_dark')
    rocket_pie = px.pie(MissionStatus, values='Rocket', names='MissionStatus', template='plotly_dark', hole=.3,
                        title='Mission Status')

    active_inactive = contry_df.groupby(['RocketStatus'])['Rocket'].count().reset_index()
    active_inactive_fig = px.bar(active_inactive, x="RocketStatus", y='Rocket', title="Rocket Status as of 2022",
                                 template='plotly_dark', color='RocketStatus', text_auto='.2s')

    year_Wise_df = contry_df.groupby(['year']).agg(
        {'cost': 'sum', 'Rocket': 'count'}).reset_index()
    # year_Wise_df = year_Wise_df[year_Wise_df['year'] >= 2000]
    year_Wise_df.dropna(inplace=True)
    grp_chart = go.Figure(data=[
        go.Bar(name='cost', x=year_Wise_df['year'], y=year_Wise_df['cost'], text=year_Wise_df['cost']),
        go.Bar(name='total mission', x=year_Wise_df['year'], y=year_Wise_df['Rocket'],
               text=year_Wise_df['Rocket']),
    ])
    grp_chart.update_traces(texttemplate='%{text:.2s}', textposition='auto')
    grp_chart.update_layout(barmode='group', title='Cost and Count of Mission Per Year', template='plotly_dark',
                            xaxis_title="Years", yaxis_title="cost in $")
    return table_data.to_dict('Records'), [{'name': i, 'id': i} for i in table_data.columns], \
           txt, ttl_msn, ttl_cst, ttl_cmp, rocket_pie, cost_pie, active_inactive_fig, grp_chart


def year_wise():
    geo_df = df.groupby(['lat', 'lon', 'year', 'country']).agg(
        {'Rocket': 'count'}).reset_index()
    geo_df.dropna(inplace=True)

    scatter_fig = px.scatter_geo(geo_df, lat=geo_df['lat'], lon=geo_df['lon'], color="Rocket",
                                 hover_name="country", size="Rocket",
                                 animation_frame="year",
                                 projection="natural earth", template='plotly_dark', )
    years = df['year'].unique()
    years_df = df[df['year'] == years[0]]

    all_df = years_df.groupby(['MissionStatus']).agg(
        {'cost': 'sum', 'Rocket': 'count'}).reset_index()
    dis_pie = px.pie(all_df, values='Rocket', names='MissionStatus', template='plotly_dark', hole=.5,
                     title='Mission Status In Percentage')
    dis_fig = px.bar(all_df, x="MissionStatus", y='cost', title="Cost Depends on Mission Status ",
                     template='plotly_dark', color='MissionStatus', text_auto='.2s')

    status_df = years_df.groupby(['RocketStatus']).agg(
        {'Rocket': 'count'}).reset_index()
    rocket_status = px.bar(status_df, x="Rocket", y='RocketStatus', title="Rocket Status as of 2022",
                           template='plotly_dark', color='RocketStatus', text_auto='.2s')
    rocket_status.update_layout(xaxis_title="Count", yaxis_title="Rocket Status")

    countries_df = years_df.groupby(['country']).agg(
        {'cost': 'sum', 'Rocket': 'count'}).reset_index()
    countries_df = countries_df.nlargest(len(countries_df['country']), 'Rocket')
    tot_launch_fig = px.bar(countries_df, x="country", y='Rocket', title="Country With Total launch Mission",
                            template='plotly_dark', color='country', text_auto='.2s')
    return [dbc.Row(
        dbc.Col(dcc.Graph(id='country_m_count_bar', figure=scatter_fig), width=12, className='p-1 ',
                style={'border-radius': '20px'}
                ), className='my-2 mx-auto'),
        dbc.Row([
            dbc.Col(
                [dcc.Dropdown(years, years[0], id='selected_year', style={'margin': '10px','color': 'black' })], width=3,
                className='p-1'),
            dbc.Col([html.H5(html.Span(['Total Missions ', DashIconify(icon="noto:rocket", height=40)]),
                             style={'text-align': 'center'}),
                     html.H4(years_df['Mission'].count(), style={'text-align': 'center'}, id='y_ttl_msn')],
                    className='mx-1 p-3',
                    style=cmp.card_style),
            dbc.Col([html.H5(html.Span(['Total Cost ', DashIconify(icon="ic:round-price-change", height=40)]),
                             style={'text-align': 'center'}),
                     html.H4('{:.2f} M $'.format(years_df['cost'].sum()), id='y_ttl_cst',
                             style={'text-align': 'center'})],
                    className='mx-1 p-3',
                    style=cmp.card_style),
            dbc.Col([html.H5(
                html.Span(['Companies Involved ', DashIconify(icon="carbon:location-company-filled", height=40)]),
                style={'text-align': 'center'}),
                html.H4(len(years_df['Company'].unique()), id='y_ttl-cmp', style={'text-align': 'center'})],
                className='mx-1 p-3',
                style=cmp.card_style),
        ]),
        dbc.Row(
            [dbc.Col(dcc.Graph(id='year_pie', figure=dis_pie), width=4, className='p-1 ',
                     style={'border-radius': '20px'}),
             dbc.Col(dcc.Graph(id='year_bar', figure=rocket_status), width=4, className='p-1'),
             dbc.Col(dcc.Graph(id='yearly_cost_pie', figure=dis_fig), width=4, className='p-1')],
            className='my-2 mx-auto'),
        dbc.Row(
            dbc.Col(dcc.Graph(id='yearly_countrywise', figure=tot_launch_fig), width=12, className='p-1 ',
                    style={'border-radius': '20px'}
                    ), className='my-2 mx-auto'),
    ]


@app.callback(
    [
        Output('y_ttl_msn', 'children'), Output('y_ttl_cst', 'children'), Output('y_ttl-cmp', 'children'),
        Output('year_pie', 'figure'), Output('year_bar', 'figure'), Output('yearly_cost_pie', 'figure'),
        Output('yearly_countrywise', 'figure')],
    [Input("selected_year", "value")], )
def select_year(year):
    years_df = df[df['year'] == year]
    ttl_msn = years_df['Mission'].count()
    ttl_cst = '{:.2f} M $'.format(years_df['cost'].sum())
    ttl_cmp = len(years_df['Company'].unique())

    all_df = years_df.groupby(['MissionStatus']).agg(
        {'cost': 'sum', 'Rocket': 'count'}).reset_index()
    dis_pie = px.pie(all_df, values='Rocket', names='MissionStatus', template='plotly_dark', hole=.5,
                     title='Mission Status In Percentage')
    dis_fig = px.bar(all_df, x="MissionStatus", y='cost', title="Cost Depends on Mission Status ",
                     template='plotly_dark', color='MissionStatus', text_auto='.2s')

    status_df = years_df.groupby(['RocketStatus']).agg(
        {'Rocket': 'count'}).reset_index()
    rocket_status = px.bar(status_df, x="Rocket", y='RocketStatus', title="Rocket Status as of 2022",
                           template='plotly_dark', color='RocketStatus', text_auto='.2s')
    rocket_status.update_layout(xaxis_title="Count", yaxis_title="Rocket Status")

    countries_df = years_df.groupby(['country']).agg(
        {'cost': 'sum', 'Rocket': 'count'}).reset_index()
    countries_df = countries_df.nlargest(len(countries_df['country']), 'Rocket')
    tot_launch_fig = px.bar(countries_df, x="country", y='Rocket', title="Country With Total launch Mission",
                            template='plotly_dark', color='country', text_auto='.2s')

    return ttl_msn, ttl_cst, ttl_cmp, dis_pie, rocket_status, dis_fig, tot_launch_fig


def company_wise():
    rocket_cuntry = df.groupby(['Company']).agg(
        {'cost': 'sum', 'Rocket': 'count'}).reset_index()
    top_countries = rocket_cuntry.nlargest(15, 'Rocket')
    top10_fig = px.bar(top_countries, x="Rocket", y='Company', title="Top 15 Companies",
                       template='plotly_dark', color='Company', text_auto='.2s')

    companies = df['Company'].unique()
    companies_df = df[df['Company'] == 'ISRO']

    all_df = companies_df.groupby(['MissionStatus']).agg(
        {'cost': 'sum', 'Rocket': 'count'}).reset_index()
    dis_pie = px.pie(all_df, values='Rocket', names='MissionStatus', template='plotly_dark', hole=.5,
                     title='Mission Status In Percentage')
    dis_fig = px.bar(all_df, x="MissionStatus", y='cost', title="Cost Depends on Mission Status ",
                     template='plotly_dark', color='MissionStatus', text_auto='.2s')

    status_df = companies_df.groupby(['RocketStatus']).agg(
        {'Rocket': 'count'}).reset_index()
    rocket_status = px.bar(status_df, x="Rocket", y='RocketStatus', title="Rocket Status as of 2022",
                           template='plotly_dark', color='RocketStatus', text_auto='.2s')
    rocket_status.update_layout(xaxis_title="Count", yaxis_title="Rocket Status")

    countries_df = companies_df.groupby(['year']).agg(
        {'Rocket': 'count'}).reset_index()
    tot_launch_fig = px.bar(countries_df, x="year", y='Rocket', title="Country With Total launch Mission",
                            template='plotly_dark', text_auto='.2s')

    rocket_cmp_status = companies_df.groupby(['year', 'MissionStatus']).agg(
        {'Rocket': 'count'}).reset_index()
    # rocket_status = rocket_status.nlargest(15, 'Rocket')

    fig = px.bar(rocket_cmp_status, x="year", y="Rocket", color="MissionStatus", title="Long-Form Input",
                 template='plotly_dark', color_discrete_map={
            'Success': 'Green', 'Failure': 'Red'})

    return [dbc.Row(
        dbc.Col(dcc.Graph(figure=top10_fig), width=12, className='p-1 ',
                style={'border-radius': '20px'}
                ), className='my-2 mx-auto'),
        dbc.Row([
            dbc.Col(
                [dcc.Dropdown(companies, 'ISRO', id='selected_company', style={'margin': '10px', })], width=3,
                className='p-1'),
            dbc.Col([html.H5(html.Span(['Total Missions ', DashIconify(icon="noto:rocket", height=40)]),
                             style={'text-align': 'center'}),
                     html.H4(companies_df['Mission'].count(), style={'text-align': 'center'}, id='c_ttl_msn')],
                    className='mx-1 p-3',
                    style=cmp.card_style),
            dbc.Col([html.H5(html.Span(['Total Cost ', DashIconify(icon="ic:round-price-change", height=40)]),
                             style={'text-align': 'center'}),
                     html.H4('{:.2f} M $'.format(companies_df['cost'].sum()), id='c_ttl_cst',
                             style={'text-align': 'center'})],
                    className='mx-1 p-3',
                    style=cmp.card_style),
        ]),
        dbc.Row(
            [dbc.Col(dcc.Graph(id='cmp_pie', figure=dis_pie), width=6, className='p-1 ',
                     style={'border-radius': '20px'}),
             dbc.Col(dcc.Graph(id='cmp_bar', figure=rocket_status), width=6, className='p-1'),
             ], className='my-2 mx-auto'),

        dbc.Row([
            dbc.Col(dcc.Graph(id='cmp_countrywise', figure=tot_launch_fig), width=8, className='p-1 ',
                    style={'border-radius': '20px'}
                    ),
            dbc.Col(dcc.Graph(id='cmp_cost_pie', figure=dis_fig), width=4, className='p-1')],
            className='my-2 mx-auto'),
        dbc.Row(
            dbc.Col(dcc.Graph(id='cmp_yearly', figure=fig), width=12, className='p-1 ',
                    style={'border-radius': '20px'}
                    ), className='my-2 mx-auto')

    ]


@app.callback(
    [
        Output('c_ttl_msn', 'children'), Output('c_ttl_cst', 'children'),
        Output('cmp_pie', 'figure'), Output('cmp_bar', 'figure'), Output('cmp_countrywise', 'figure'),
        Output('cmp_cost_pie', 'figure'),
        Output('cmp_yearly', 'figure')],
    [Input("selected_company", "value")], )
def selected_cmp(cmp):
    companies_df = df[df['Company'] == cmp]
    ttl_msn = companies_df['Mission'].count()
    ttl_cst = '{:.2f} M $'.format(companies_df['cost'].sum())

    all_df = companies_df.groupby(['MissionStatus']).agg(
        {'cost': 'sum', 'Rocket': 'count'}).reset_index()
    dis_pie = px.pie(all_df, values='Rocket', names='MissionStatus', template='plotly_dark', hole=.5,
                     title='Mission Status In Percentage', color_discrete_map={'Success': 'Green', 'Failure': 'Red'})
    dis_fig = px.bar(all_df, x="MissionStatus", y='cost', title="Cost Depends on Mission Status ",
                     template='plotly_dark', color='MissionStatus', text_auto='.2s',
                     color_discrete_map={'Success': 'Green', 'Failure': 'Red'})

    status_df = companies_df.groupby(['RocketStatus']).agg(
        {'Rocket': 'count'}).reset_index()
    rocket_status = px.bar(status_df, x="Rocket", y='RocketStatus', title="Rocket Status as of 2022",
                           template='plotly_dark', color='RocketStatus', text_auto='.2s')
    rocket_status.update_layout(xaxis_title="Count", yaxis_title="Rocket Status")

    countries_df = companies_df.groupby(['year']).agg(
        {'Rocket': 'count'}).reset_index()
    tot_launch_fig = px.bar(countries_df, x="year", y='Rocket', title="Total Mission Per Year",
                            template='plotly_dark', text_auto='.2s')

    rocket_cmp_status = companies_df.groupby(['year', 'MissionStatus']).agg(
        {'Rocket': 'count'}).reset_index()
    # rocket_status = rocket_status.nlargest(15, 'Rocket')

    fig = px.bar(rocket_cmp_status, x="year", y="Rocket", color="MissionStatus",
                 title="Mission Count Per Year Depends on Mission Status",
                 template='plotly_dark', color_discrete_map={'Success': 'Green', 'Failure': 'Red'})

    return ttl_msn, ttl_cst, dis_pie, rocket_status, tot_launch_fig, dis_fig, fig


def launch_pad():
    map_df = df.groupby(['loc', 'Location']).agg(
        {'Rocket': 'count'}).reset_index()
    maker = []
    for i, r in map_df.iterrows():
        lat = r['loc']
        pos = lat.replace('(', '')
        pos = pos.replace(')', '')
        pos = pos.split(',')
        maker.append(dl.Marker(id='source', position=[float(pos[0]), float(pos[1])],
                               children=dl.Tooltip(
                                   f"""{r['Location']} , No of Rocket launches {r['Rocket']}"""
                               )))
    return [
        dbc.Row(html.P('NOTE- Follow shows some rocket launch pad,for more details, you can zoom in and out .')),
        dbc.Row(
            dl.Map(id='atellite-streets-v9', style={'width': '100%', 'height': '85vh', 'margin': '0', 'padding': '0'},
                   zoom=2,
                   children=[dl.TileLayer(), dl.LayerGroup(id="layer", children=maker), ]
                   ), style={'margin': '0', 'padding': '0'})]


def fnAboutMe():
    encoded_image = base64.b64encode(open('asset/1657562494531.jpg', 'rb').read())
    return dbc.Row([
        dbc.Row(dbc.Col(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode("utf-8")),
                                 style={'height': '100%', 'width': '100%',
                                        'border-radius': '30px 30px 30px 30px',
                                        'box-shadow': 'rgb(38, 57, 77) 0px 20px 30px -10px'}),
                        width=4), justify='center', className='my-2'),
        dbc.Row(dbc.Col(html.H1('Sachin Halave', style={'text-align': 'center', 'color': 'Black'})),
                justify='center'),
        dbc.Row(dbc.Col(dbc.NavLink("sdhalave6061@gmail.com", href="sdhalave6061@gmail.com",
                                    style={'text-align': 'center', 'color': '#000066', 'height': '20px'})),
                justify='center'),
        dbc.Row(dbc.Col(dbc.NavLink("https://www.linkedin.com/in/sachin-halave-6061",
                                    href='https://www.linkedin.com/in/sachin-halave-6061',
                                    style={'text-align': 'center', 'color': '#000066', 'height': '20px'})),
                justify='center'),
        dbc.Row(dbc.Col(dbc.NavLink("https://github.com/sachin6061", href='https://github.com/sachin6061',
                                    style={'text-align': 'center', 'color': '#000066', 'height': '20px'})),
                justify='center'),
        html.Hr(style={'color': 'white', 'margin': '10px'}),
        dbc.Row(dbc.Col(html.H1('Python Developer', style={'text-align': 'center', 'color': '#800000'})))],
        style={'height': '100vh'})


if __name__ == "__main__":
    app.run_server(debug=False)
