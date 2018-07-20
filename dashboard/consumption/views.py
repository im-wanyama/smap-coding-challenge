# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Sum, Avg
from django.db.models.functions import TruncDate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from consumption.forms import Search
from consumption.models import User_data, Consumption

LAYOUT_HTML = 'consumption/layout.html'
SUMMARY_HTML = 'consumption/summary.html'
DETAIL_HTML = 'consumption/detail.html'


def front_page(request):
    return render(request, LAYOUT_HTML)


def detail(request):
    '''Template for the details tab of the app.'''
    form = Search()
    return render(request, DETAIL_HTML, {'form': form})


def summary(request):
    '''Creates tables summarising data in the db.'''
    tables = []
    queries = {
        'user_data_id': list(Consumption.objects.values('user_data_id')
                             .order_by('user_data_id')
                             .annotate(Average_consumption=Avg('consumption'),
                                       Total_consumption=Sum('consumption'))
                             # average and total consumption of all users
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
        if header == 'user_data_id':
            df.loc[len(df) + 1] = [
                'All',
                Consumption.objects.values('consumption')
                .aggregate(Avg('consumption'))['consumption__avg'],
                Consumption.objects.values('consumption')
                .aggregate(Sum('consumption'))['consumption__sum']
                ]
        df['Average_consumption'] = round(df['Average_consumption'], 2)
        df['Total_consumption'] = round(df['Total_consumption'], 2)
        df = df.rename(columns={'user_data_id': 'User ID',
                                'Average_consumption': 'Average Consumption',
                                'Total_consumption': 'Total Consumption',
                                'area': 'Area', 'tariff': 'Tariff'})
        tables.append(df.to_html(index=False, justify='left'))
        del df
    return render(request, SUMMARY_HTML, {'tables': tables})


def detail_search(request):
    '''Creates a table that shows all available data for a specific
       user id, this is inputted by the user via the web app.'''
    form = Search(request.GET)
    page = request.GET.get('page', 1)
    if form.is_valid():
        id_search = form.cleaned_data['id_search']
        data = list(User_data.objects.select_related('user_data_id')
                    .values('id', 'area', 'tariff',
                            'consumption__datetime',
                            'consumption__consumption')
                    .filter(id=id_search)
                    .order_by('consumption__datetime')
                    )
    if not data:
        return render(request, DETAIL_HTML,
                      {'form': form, 'no_id':
                       f'<p class="comments"> User id {id_search} is not'
                       ' present in our database.</p>'})
    df = pd.DataFrame(data)
    df['Month'] = pd.to_datetime(
        df['consumption__datetime']).dt.strftime('%b-%Y')
    df['consumption__datetime'] = pd.to_datetime(
        df['consumption__datetime']).dt.strftime('%d/%m/%Y, %T')
    user_data = df.to_dict(orient='records')
    paginator = Paginator(user_data, 200)
    try:
        user_rows = paginator.page(page)
    except PageNotAnInteger:
        user_rows = paginator.page(1)
    except EmptyPage:
        user_rows = paginator.page(paginator.num_pages)
    return render(request, DETAIL_HTML, {'user_rows': user_rows, 'form': form,
                                         'user_id': id_search})


def detail_search_api(request):
    '''Creates json data which is used to create JS graphs which show
       consumption over time (months) for a specific user.'''
    consumption_data = []
    sem = []
    data = []
    id_search = None
    form = Search(request.GET)
    if form.is_valid():
        id_search = form.cleaned_data['id_search']
        data = list(User_data.objects.select_related('user_data_id')
                    .values('id', 'consumption__datetime',
                            'consumption__consumption')
                    .filter(id=id_search)
                    .order_by('consumption__datetime')
                    )
    if not data:
        return JsonResponse({'error': f'User ID {id_search} is an'
                             ' invalid id.'})
    df = pd.DataFrame(data)
    df['month'] = pd.to_datetime(
        df['consumption__datetime']).dt.strftime('%b-%Y')
    for i in df['month'].unique():
        consumption_data.append(df['consumption__consumption'].where(
            df['month'] == i).mean().round(2))
        sem.append(df['consumption__consumption'].where(
            df['month'] == i).sem().round(2))
    response = JsonResponse([{'x_axis':  list(df['month'].unique()),
                             'y_axis': consumption_data, 'sem': sem}],
                            safe=False)
    return response


def summary_api(request):
    '''Creates json data which is used to create JS graphs to
       summarise data in the db.'''
    response = {
        'month_data': {'x_axis': [], 'y_axis': [], 'sem': []},
        'area_data': {'x_axis': [], 'y_axis': [], 'sem': []},
        'tariff_data': {'x_axis': [], 'y_axis': [], 'sem': []}
                }
    queries = {
        'month': list(Consumption.objects
                      .values('datetime', 'consumption')
                      .order_by('datetime')
                      # consumption for each date
                      ),
        'area': list(User_data.objects.select_related('user_data_id')
                     .values('area', 'consumption__consumption')
                     .order_by('area')
                     # consumption for each area
                     ),
        'tariff': list(User_data.objects.select_related('user_data_id')
                       .values('tariff', 'consumption__consumption')
                       .order_by('tariff')
                       # consumption for each tariff
                       )}
    for data_type, data in queries.items():
        df = pd.DataFrame(data)
        df = df.rename(columns={'consumption__consumption': 'consumption'})
        if 'datetime' in df.columns and len(df.columns) == 2:
            df['month'] = pd.to_datetime(
                df['datetime']).dt.strftime('%b-%Y')
        response[f'{data_type}_data']['x_axis'] = list(df[data_type].unique())
        for i in df[data_type].unique():
            response[f'{data_type}_data']['y_axis'].append(
                df['consumption'].where(df[data_type] == i)
                .mean().round(2))
            response[f'{data_type}_data']['sem'].append(
                df['consumption'].where(df[data_type] == i)
                .sem().round(2))
        del df
    response = JsonResponse([response['month_data'], response['area_data'],
                             response['tariff_data']], safe=False)
    return response
