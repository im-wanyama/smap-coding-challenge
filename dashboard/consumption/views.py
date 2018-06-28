# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from io import BytesIO
from base64 import b64encode
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from django.shortcuts import render
from django.db.models import Sum, Avg
from django.db.models.functions import TruncDate
from consumption.forms import Search
from consumption.models import User_data, Consumption

LAYOUT_HTML = 'consumption/layout.html'
SUMMARY_HTML = 'consumption/summary.html'
DETAIL_HTML = 'consumption/detail.html'


def mk_graph(df, x_axis, y_axis, graph_type):
    buf = BytesIO()
    if graph_type == 'point':
        plot = sns.pointplot(x=x_axis, y=y_axis, data=df)
        plot.figure.savefig(buf, format="png")
        plt.clf()
        return b64encode(buf.getvalue()).decode('ascii')
    elif graph_type == 'bar':
        plot = sns.barplot(x=x_axis, y=y_axis, data=df)
        plot.figure.savefig(buf, format="png")
        plt.clf()
        return b64encode(buf.getvalue()).decode('ascii')


def front_page(request):
    return render(request, LAYOUT_HTML)


def detail(request):
    '''Template for the details tab of the app.'''
    form = Search()
    return render(request, DETAIL_HTML, {'form': form})


def summary(request):
    '''Creates tables and graphs summarising data in the db.'''
    tables = []
    graphs = []
    queries = {
        'user_data_id': list(Consumption.objects.values('user_data_id')
                             .order_by('user_data_id')
                             .annotate(Average_consumption=Avg('consumption'),
                                       Total_consumption=Sum('consumption'))
                             # average and total consumption for each user
                             ),
        'Date': list(Consumption.objects.annotate(Date=TruncDate('datetime'))
                     .values('Date').order_by('Date')
                     .annotate(Average_consumption=Avg('consumption'),
                               Total_consumption=Sum('consumption'))
                     # average and total consumption for each date
                     ),
        'area': list(User_data.objects.select_related('user_data_id')
                     .values('area').order_by('area')
                     .annotate(
                         Average_consumption=Avg('consumption__consumption'),
                         Total_consumption=Sum('consumption__consumption'))
                     # average and total consumption for each area
                     ),
        'tariff': list(User_data.objects.select_related('user_data_id')
                       .values('tariff').order_by('tariff')
                       .annotate(
                           Average_consumption=Avg('consumption__consumption'),
                           Total_consumption=Sum('consumption__consumption'))
                       # average and total consumption for each tariff
                       )}

    for header, data in queries.items():
        df = pd.DataFrame(data)[[header, 'Average_consumption',
                                 'Total_consumption']]
        df['Average_consumption'] = round(df['Average_consumption'], 2)
        df['Total_consumption'] = round(df['Total_consumption'], 2)
        df = df.rename(columns={'user_data_id': 'User ID',
                                'Average_consumption': 'Average Consumption',
                                'Total_consumption': 'Total Consumption',
                                'area': 'Area', 'tariff': 'Tariff'})
        tables.append(df.to_html(index=False))
        if header == 'Date':
            x_axis = 'Month'
            graph_type = 'point'
            df['Month'] = pd.to_datetime(df['Date']).dt.strftime('%m-%Y')
        else:
            x_axis = header
            graph_type = 'bar'
        if header != 'user_data_id':
            graphs.append(mk_graph(df, df[x_axis.title()],
                                   df['Average Consumption'], graph_type)
                          )
        del df
    return render(request, SUMMARY_HTML, {'tables': tables, 'graphs': graphs})


def detail_search(request):
    '''Creates tables and graphs to show all available data for a specific
       user id, this is inputted by the user via the web app.'''
    tables = []
    graphs = []
    form = Search(request.GET)
    if form.is_valid():
        id_search = form.cleaned_data['id_search']
    df = pd.DataFrame(
        list(User_data.objects.select_related('user_data_id')
             .values('id', 'area', 'tariff', 'consumption__datetime',
                     'consumption__consumption')
             .filter(id=id_search)
             .order_by('consumption__datetime')
             )
                    )[['id', 'area', 'tariff', 'consumption__datetime',
                       'consumption__consumption']]
    df = df.rename(columns={'id': 'User ID', 'area': 'Area',
                            'tariff': 'Tariff',
                            'consumption__datetime': 'Timestamp',
                            'consumption__consumption': 'Consumption'})
    tables.append(df.to_html(index=False))
    df['Month'] = pd.to_datetime(df['Timestamp']).dt.strftime('%m-%Y')
    graphs.append(mk_graph(df, df['Month'], df['Consumption'], 'point'))
    del df
    return render(request, DETAIL_HTML,
                  {'tables': tables, 'graphs': graphs, 'form': form,
                   'user_id': f'User ID: {id_search}'})
