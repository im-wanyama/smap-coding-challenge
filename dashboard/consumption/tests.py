# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import pandas as pd
from django.test import TestCase
from django.db.models import Sum, Avg
from django.db.models.functions import TruncDate
from consumption.models import User_data, Consumption


class SummaryTestCase(TestCase):
    '''This class contains methods to test the functionality of functions in
       views.py.'''

    def setUp(self):
        Consumption.objects.create(id=1, datetime='2016-10-22 20:00:00',
                                   consumption=1, user_data_id=1)
        Consumption.objects.create(id=2, datetime='2016-10-22 18:00:00',
                                   consumption=2, user_data_id=1)
        Consumption.objects.create(id=3, datetime='2016-10-22 10:00:00',
                                   consumption=3, user_data_id=1)
        User_data.objects.create(id=1, area='a1', tariff='t2')

    def test_user_id_table(self):
        '''Test that the table containing average and total consumption for
           each user is generated correctly.'''
        df = pd.DataFrame(
            list(Consumption.objects.values('user_data_id')
                 .order_by('user_data_id')
                 .annotate(Average_consumption=Avg('consumption'),
                           Total_consumption=Sum('consumption'))
                 )
                          )[['user_data_id', 'Average_consumption',
                             'Total_consumption']]
        df['Average_consumption'] = round(df['Average_consumption'], 2)
        df['Total_consumption'] = round(df['Total_consumption'], 2)
        self.assertEqual(df.at[0, 'user_data_id'], 1)
        self.assertEqual(df.at[0, 'Average_consumption'], 2.0)
        self.assertEqual(df.at[0, 'Total_consumption'], 6.0)

    def test_date_table(self):
        '''Test that the table containing average and total consumption for
           each date is generated correctly.'''
        df = pd.DataFrame(
            list(Consumption.objects.annotate(Date=TruncDate('datetime'))
                 .values('Date').order_by('Date')
                 .annotate(Average_consumption=Avg('consumption'),
                           Total_consumption=Sum('consumption'))
                 )
                         )[['Date', 'Average_consumption',
                            'Total_consumption']]
        df['Average_consumption'] = round(df['Average_consumption'], 2)
        df['Total_consumption'] = round(df['Total_consumption'], 2)
        self.assertEqual(df.at[0, 'Date'], datetime.date(2016, 10, 22))
        self.assertEqual(df.at[0, 'Average_consumption'], 2.0)
        self.assertEqual(df.at[0, 'Total_consumption'], 6.0)

    def test_area_table(self):
        '''Test that the table containing average and total consumption for
           each area is generated correctly.'''
        df = pd.DataFrame(
            list(User_data.objects.select_related('user_data_id')
                 .values('area').order_by('area')
                 .annotate(Average_consumption=Avg('consumption__consumption'),
                           Total_consumption=Sum('consumption__consumption'))
                 )
                         )[['area', 'Average_consumption',
                            'Total_consumption']]
        df['Average_consumption'] = round(df['Average_consumption'], 2)
        df['Total_consumption'] = round(df['Total_consumption'], 2)
        self.assertEqual(df.at[0, 'area'], 'a1')
        self.assertEqual(df.at[0, 'Average_consumption'], 2.0)
        self.assertEqual(df.at[0, 'Total_consumption'], 6.0)

    def test_tariff_table(self):
        '''Test that the table containing average and total consumption for
           each tariff is generated correctly.'''
        df = pd.DataFrame(
            list(User_data.objects.select_related('user_data_id')
                 .values('tariff').order_by('tariff')
                 .annotate(Average_consumption=Avg('consumption__consumption'),
                           Total_consumption=Sum('consumption__consumption'))
                 )
                         )[['tariff', 'Average_consumption',
                            'Total_consumption']]
        df['Average_consumption'] = round(df['Average_consumption'], 2)
        df['Total_consumption'] = round(df['Total_consumption'], 2)
        self.assertEqual(df.at[0, 'tariff'], 't2')
        self.assertEqual(df.at[0, 'Average_consumption'], 2.0)
        self.assertEqual(df.at[0, 'Total_consumption'], 6.0)

    def test_details_table(self):
        '''Test that the table contains all relevant details for
           each user with regards to consumption is generated correctly.'''
        df = pd.DataFrame(
            list(User_data.objects.select_related('user_data_id')
                 .values('id', 'area', 'tariff', 'consumption__datetime',
                         'consumption__consumption')
                 .filter(id=1)
                 .order_by('consumption__datetime')
                 )
                         )[['id', 'area', 'tariff', 'consumption__datetime',
                            'consumption__consumption']]
        df = df.rename(columns={'consumption__datetime': 'Datetime',
                                'consumption__consumption': 'Consumption'})
        self.assertEqual(df.at[0, 'id'], 1)
        self.assertEqual(df.at[0, 'area'], 'a1')
        self.assertEqual(df.at[0, 'tariff'], 't2')
        self.assertEqual(df.at[0, 'Datetime'],
                         pd.Timestamp('2016-10-22 10:00:00'))
        self.assertEqual(df.at[0, 'Consumption'], 3.0)

    def test_details_api(self):
        '''Tests that the correct json data is created for the details
           graphs.'''
        consumption_data = []
        sem = []
        id_search = 1
        data = list(User_data.objects.select_related('user_data_id')
                    .values('id', 'consumption__datetime',
                            'consumption__consumption')
                    .filter(id=id_search)
                    .order_by('consumption__datetime')
                    )
        df = pd.DataFrame(data)
        df['month'] = pd.to_datetime(
            df['consumption__datetime']).dt.strftime('%b-%Y')
        for i in df['month'].unique():
            consumption_data.append(df['consumption__consumption'].where(
                df['month'] == i).mean().round(2))
            sem.append(df['consumption__consumption'].where(
                df['month'] == i).sem().round(2))
        self.assertEqual(consumption_data[0], 2.0)
        self.assertEqual(sem[0], 0.58)

    def test_summary_api(self):
        '''Tests that the correct json data is created for the summary
           graphs.'''
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
            response[f'{data_type}_data']['x_axis'] = list(
                df[data_type].unique())
            for i in df[data_type].unique():
                response[f'{data_type}_data']['y_axis'].append(
                    df['consumption'].where(df[data_type] == i)
                    .mean().round(2))
                response[f'{data_type}_data']['sem'].append(
                    df['consumption'].where(df[data_type] == i)
                    .sem().round(2))
        for data, x_axis in {'month_data': 'Oct-2016', 'area_data': 'a1',
                             'tariff_data': 't2'}.items():
            self.assertEqual(response[data]['x_axis'], [x_axis])
            self.assertEqual(response[data]['y_axis'], [2.0])
            self.assertEqual(response[data]['sem'], [0.58])
