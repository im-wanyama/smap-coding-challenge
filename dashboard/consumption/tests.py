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
